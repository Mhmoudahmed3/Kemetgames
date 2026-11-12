"""Shared world country database loader, geodesic math, and BFS land-border graph."""

from __future__ import annotations

import base64
from collections import deque
import json
import math
from pathlib import Path
import re
from typing import Any

DATA_PATH = Path(__file__).resolve().parent / "countries_data.json"
FLAGS_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "flags"
with DATA_PATH.open("r", encoding="utf-8") as _fh:
    COUNTRIES_BANK: list[dict[str, Any]] = json.load(_fh)

COUNTRY_BY_CODE: dict[str, dict[str, Any]] = {
    row["code"].upper(): row for row in COUNTRIES_BANK if row.get("code")
}
COUNTRY_BY_CCN3: dict[str, dict[str, Any]] = {
    str(row["ccn3"]).zfill(3): row for row in COUNTRIES_BANK if row.get("ccn3")
}
COUNTRY_BY_NAME: dict[str, dict[str, Any]] = {
    row["name"].strip().lower(): row for row in COUNTRIES_BANK if row.get("name")
}
COUNTRY_BY_OFFICIAL_NAME: dict[str, dict[str, Any]] = {
    row["official_name"].strip().lower(): row
    for row in COUNTRIES_BANK
    if row.get("official_name")
}

# Build verified symmetric adjacency graph keyed by 2-letter ISO code
_adj: dict[str, set[str]] = {c: set() for c in COUNTRY_BY_CODE}
for _code, _row in COUNTRY_BY_CODE.items():
    for _bc in _row.get("border_codes", []):
        _u = str(_bc).upper()
        if _u in COUNTRY_BY_CODE and _u != _code:
            _adj[_code].add(_u)
            _adj[_u].add(_code)
BORDER_GRAPH: dict[str, list[str]] = {
    c: sorted(nbrs) for c, nbrs in _adj.items()
}

_FLAG_DATA_URI_CACHE: dict[str, str] = {}


def get_sanitized_flag_data_uri(code: str) -> str | None:
    """Return a sanitized data:image/svg+xml;base64 URI with ISO-2 identifiers stripped."""
    key = str(code or "").strip().upper()
    if not key:
        return None
    cached = _FLAG_DATA_URI_CACHE.get(key)
    if cached is not None:
        return cached
    svg_path = FLAGS_DIR / f"{key.lower()}.svg"
    if not svg_path.exists():
        return None
    raw_svg = svg_path.read_text(encoding="utf-8")
    cleaned = re.sub(
        r"<script\b[^>]*>.*?</script>", "", raw_svg, flags=re.IGNORECASE | re.DOTALL
    )
    cleaned = re.sub(
        r"\s+on[a-z]+\s*=\s*(\"[^\"]*\"|'[^']*')",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r'\s+id="flag-icons-[^"]+"', "", cleaned)
    found_ids: list[str] = []
    for match in re.finditer(r'\bid="([^"]+)"', cleaned):
        ident = match.group(1)
        if ident not in found_ids:
            found_ids.append(ident)
    if found_ids:
        id_map = {old_id: f"s{idx}" for idx, old_id in enumerate(found_ids)}
        pattern = "|".join(re.escape(k) for k in sorted(id_map, key=len, reverse=True))
        cleaned = re.sub(
            rf'(\bid=")({pattern})(")',
            lambda m: f"{m.group(1)}{id_map[m.group(2)]}{m.group(3)}",
            cleaned,
        )
        cleaned = re.sub(
            rf'(\bhref="#)({pattern})(")',
            lambda m: f"{m.group(1)}{id_map[m.group(2)]}{m.group(3)}",
            cleaned,
        )
        cleaned = re.sub(
            rf'(url\(#)({pattern})(\))',
            lambda m: f"{m.group(1)}{id_map[m.group(2)]}{m.group(3)}",
            cleaned,
        )
    encoded = base64.b64encode(cleaned.encode("utf-8")).decode("ascii")
    uri = f"data:image/svg+xml;base64,{encoded}"
    _FLAG_DATA_URI_CACHE[key] = uri
    return uri


def resolve_country(identifier: str) -> dict[str, Any] | None:
    """Look up a country by ISO-2 code, 3-digit ccn3, common name, or official name."""
    if not identifier:
        return None
    raw = str(identifier).strip()
    up = raw.upper()
    if up in COUNTRY_BY_CODE:
        return COUNTRY_BY_CODE[up]
    if raw.isdigit():
        padded = raw.zfill(3)
        if padded in COUNTRY_BY_CCN3:
            return COUNTRY_BY_CCN3[padded]
    low = raw.lower()
    return COUNTRY_BY_NAME.get(low) or COUNTRY_BY_OFFICIAL_NAME.get(low)


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    """Great-circle surface distance between two coordinates in kilometers."""
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return round(2.0 * r * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a))))


_COMPASS_8 = [
    ("N", "↑"),
    ("NE", "↗"),
    ("E", "→"),
    ("SE", "↘"),
    ("S", "↓"),
    ("SW", "↙"),
    ("W", "←"),
    ("NW", "↖"),
]


def compass_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> tuple[str, str]:
    """Return initial bearing compass code and Unicode arrow from (lat1, lng1) toward (lat2, lng2)."""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dl = math.radians(lng2 - lng1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
    idx = int((deg + 22.5) // 45.0) % 8
    return _COMPASS_8[idx]


def distance_to_heat(distance_km: float) -> float:
    """Normalize geodesic distance (0..16000 km) into heat scalar (1.0=match, 0.05=antipode)."""
    if distance_km <= 0:
        return 1.0
    # Exponential decay scaled around 3200 km gives crisp distinction on continents
    return round(max(0.06, min(0.98, math.exp(-distance_km / 3400.0))), 3)


def shortest_border_path(code_a: str, code_b: str) -> list[str] | None:
    """BFS shortest land-border sequence of ISO-2 codes [code_a, ..., code_b], or None if disjoint."""
    a = str(code_a).upper()
    b = str(code_b).upper()
    if a not in BORDER_GRAPH or b not in BORDER_GRAPH:
        return None
    if a == b:
        return [a]
    queue: deque[list[str]] = deque([[a]])
    visited: set[str] = {a}
    while queue:
        path = queue.popleft()
        cur = path[-1]
        for nxt in BORDER_GRAPH[cur]:
            if nxt == b:
                return path + [nxt]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])
    return None


def _build_connected_pairs() -> dict[int, list[tuple[str, str]]]:
    """Precompute connected land-border country pairs bucketed by intermediate count (0..7)."""
    buckets: dict[int, list[tuple[str, str]]] = {i: [] for i in range(8)}
    codes = sorted(c for c, nbrs in BORDER_GRAPH.items() if nbrs)
    for idx, src in enumerate(codes):
        dist: dict[str, int] = {src: 0}
        q: deque[str] = deque([src])
        while q:
            cur = q.popleft()
            d = dist[cur]
            if d >= 8:
                continue
            for nxt in BORDER_GRAPH[cur]:
                if nxt not in dist:
                    dist[nxt] = d + 1
                    q.append(nxt)
        for dst, edges in dist.items():
            if dst <= src:
                continue
            between = edges - 1
            if 0 <= between <= 7:
                buckets[between].append((src, dst))
    return buckets


CONNECTED_PAIRS_BY_BETWEEN: dict[int, list[tuple[str, str]]] = _build_connected_pairs()
