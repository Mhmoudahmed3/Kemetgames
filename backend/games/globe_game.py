"""Interactive Globe & World Map game engine with 4 modes across ~197 UN countries."""

from __future__ import annotations

import math
import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty
from backend.data.country_store import (
    CONNECTED_PAIRS_BY_BETWEEN,
    COUNTRIES_BANK,
    COUNTRY_BY_CODE,
    compass_bearing,
    distance_to_heat,
    get_sanitized_flag_data_uri,
    haversine_km,
    resolve_country,
    shortest_border_path,
)

GLOBE_MODES = ["name", "flag", "hint", "borders_between"]
MAX_LOCATE_GUESSES = 6
ATTEMPT_BASE_SCORES = [1000, 820, 680, 540, 420, 300, 220]
GLOBE_DIFFICULTY_PROFILES: dict[str, tuple[float, float, int, int | None]] = {
    "easy": (55.0, 35.0, 7, 70),
    "mid": (40.0, 25.0, 6, None),
    "hard": (25.0, 16.0, 4, None),
}


class GlobeGame(BaseGame):
    GAME_TYPE = "globe"
    TITLE = "GLOBE PROTOCOL"
    CATEGORY = "IQ & Trivia"
    DESCRIPTION = (
        "Interactive 3D Globe & 2D World Map challenge across 4 modes: Locate by Name, Flag Pinpoint, Hint Detective, and Minimum Nations Between."
    )
    MIN_PLAYERS = 1
    MAX_PLAYERS = 16
    SUPPORTS_SOLO = True
    SUPPORTS_BOTS = False
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"mode": "mix", "rounds": 8, "difficulty": "mid"}

    LOCATE_SECONDS = 40.0
    BORDERS_SECONDS = 25.0
    REVEAL_SECONDS = 5.5

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.locate_seconds: float = self.LOCATE_SECONDS
        self.borders_seconds: float = self.BORDERS_SECONDS
        self.max_locate_guesses: int = MAX_LOCATE_GUESSES
        self.rounds: list[dict[str, Any]] = []
        self.round_idx: int = 0
        self.subphase: str = "question"  # question | reveal
        self.phase_started_at: float = 0.0
        self.round_progress: dict[str, dict[str, Any]] = {}
        self._last_tick_sec: int = -1

    def _build_rounds(
        self, count: int, mode_pref: str, difficulty: str = "mid"
    ) -> list[dict[str, Any]]:
        selected_mode = mode_pref if mode_pref in GLOBE_MODES else "mix"
        _, _, _, top_n = GLOBE_DIFFICULTY_PROFILES[difficulty]
        if top_n is not None:
            ranked = sorted(COUNTRIES_BANK, key=lambda c: c.get("population", 0), reverse=True)
            all_countries = ranked[: min(top_n, len(ranked))]
            allowed_codes: set[str] | None = {c["code"] for c in all_countries}
        else:
            all_countries = list(COUNTRIES_BANK)
            allowed_codes = None

        def pairs_for_bucket(bucket_k: int) -> list[tuple[str, str]]:
            raw_pairs = CONNECTED_PAIRS_BY_BETWEEN.get(bucket_k, [])
            if allowed_codes is None:
                return raw_pairs
            return [p for p in raw_pairs if p[0] in allowed_codes and p[1] in allowed_codes]

        used_targets: set[str] = set()
        used_pairs: set[tuple[str, str]] = set()
        built: list[dict[str, Any]] = []

        if difficulty == "easy":
            between_weights = [2, 4, 4, 3, 1, 0, 0, 0]
            between_choices = [b for b in range(5) if pairs_for_bucket(b)]
        elif difficulty == "hard":
            between_weights = [0, 1, 2, 4, 4, 3, 3, 2]
            between_choices = [b for b in range(1, 8) if pairs_for_bucket(b)]
        else:
            between_weights = [1, 3, 4, 4, 3, 2, 2, 1]
            between_choices = [b for b in range(8) if pairs_for_bucket(b)]
        if not between_choices:
            between_choices = [b for b in range(8) if pairs_for_bucket(b)]
            between_weights = [1] * len(between_choices)

        for i in range(count):
            mode = GLOBE_MODES[i % len(GLOBE_MODES)] if selected_mode == "mix" else selected_mode

            if mode == "borders_between" and between_choices:
                weights = [between_weights[b] for b in between_choices]
                chosen_pair: tuple[str, str] | None = None
                for _ in range(25):
                    bucket_k = random.choices(between_choices, weights=weights, k=1)[0]
                    pair = random.choice(pairs_for_bucket(bucket_k))
                    canonical = tuple(sorted(pair))
                    if canonical not in used_pairs:
                        chosen_pair = pair if random.random() < 0.5 else (pair[1], pair[0])
                        used_pairs.add(canonical)
                        break
                if chosen_pair is None:
                    fallback_pool = pairs_for_bucket(1) or pairs_for_bucket(between_choices[0])
                    chosen_pair = random.choice(fallback_pool)

                c_a = COUNTRY_BY_CODE[chosen_pair[0]]
                c_b = COUNTRY_BY_CODE[chosen_pair[1]]
                path_codes = shortest_border_path(c_a["code"], c_b["code"]) or [c_a["code"], c_b["code"]]
                min_between = max(0, len(path_codes) - 2)
                built.append(
                    {
                        "mode": "borders_between",
                        "prompt": f"What is the minimum number of nations separating {c_a['name']} and {c_b['name']} by land borders?",
                        "country_a": c_a,
                        "country_b": c_b,
                        "path_codes": path_codes,
                        "min_between": min_between,
                    }
                )
                continue

            # Locate modes: name, flag, hint
            # Prefer recognizable & polygon countries primarily while allowing full 197-country variety
            fresh = [c for c in all_countries if c["code"] not in used_targets]
            if not fresh:
                fresh = all_countries
            target = random.choice(fresh)
            used_targets.add(target["code"])

            raw_clue = target["landmark_clue"]
            cap_marker = f" with capital {target['capital']}"
            if cap_marker in raw_clue:
                raw_clue = raw_clue.replace(cap_marker, "")

            hints = [
                f"Region: {target['continent']} ({target['subregion']})",
                raw_clue,
                f"Scale: Population ~{target['population_label']} (#{target['population_rank']}) · Area {target['area_label']} (#{target['area_rank']})",
                f"Identity: Capital {target['capital']} · Language {target['language']} · Currency {target['currency']}",
            ]

            prompt = {
                "name": f"Locate {target['name']} on the globe",
                "flag": "Identify this flag and pinpoint the country on the globe",
                "hint": "Use the clues below to pinpoint the mystery nation on the globe",
            }[mode]

            built.append(
                {
                    "mode": mode,
                    "prompt": prompt,
                    "target": target,
                    "hints": hints,
                }
            )

        return built

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = diff
        self.locate_seconds, self.borders_seconds, self.max_locate_guesses, _ = (
            GLOBE_DIFFICULTY_PROFILES[diff]
        )
        raw_rounds = self.settings.get("rounds", 8)
        if isinstance(raw_rounds, bool) or raw_rounds is None:
            parsed_rounds = 8
        else:
            try:
                parsed_rounds = int(raw_rounds)
            except (TypeError, ValueError):
                parsed_rounds = 8
        count = max(4, min(20, parsed_rounds))
        self.settings["rounds"] = count
        mode_pref = str(self.settings.get("mode", "mix")).lower()
        self.rounds = self._build_rounds(count, mode_pref, difficulty=diff)
        self.round_idx = 0
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        for p in self.players:
            p.score = 0
        self._begin_question(self.started_at)
        self.log_event(
            f"Globe Protocol started ({count} rounds, {diff.upper()}, mode: {mode_pref})."
        )

    def _begin_question(self, now: float) -> None:
        self.subphase = "question"
        self.phase_started_at = now
        self._last_tick_sec = -1
        self.round_progress = {
            p.id: {
                "guesses": [],
                "extra_hints": 0,
                "solved": False,
                "between_guess": None,
                "points": 0,
                "scored": False,
            }
            for p in self.players
        }

    def _begin_reveal(self, now: float) -> None:
        if self.subphase == "reveal":
            return
        self.subphase = "reveal"
        self.phase_started_at = now
        for pid, prog in self.round_progress.items():
            if not prog["scored"] and prog["points"] > 0:
                prog["scored"] = True
                player = self.get_player(pid)
                if player:
                    player.score += prog["points"]

    def _all_players_done_round(self, mode: str) -> bool:
        active_players = [p for p in self.players if p.connected]
        if not active_players:
            return False
        for p in active_players:
            prog = self.round_progress.get(p.id)
            if not prog:
                return False
            if mode == "borders_between":
                if prog["between_guess"] is None:
                    return False
            else:
                if not prog["solved"] and len(prog["guesses"]) < self.max_locate_guesses:
                    return False
        return True

    def on_player_disconnect(self, player_id: str) -> bool:
        changed = super().on_player_disconnect(player_id)
        if changed and self.phase == "playing" and self.subphase == "question" and self.rounds:
            mode = self.rounds[self.round_idx]["mode"]
            if self._all_players_done_round(mode):
                self._begin_reveal(time.time())
        return changed

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        player = self.get_player(player_id)
        if player is None:
            return False, "Unknown player."

        now = time.time()
        q = self.rounds[self.round_idx]
        mode = q["mode"]

        if action == "next" and self.subphase == "reveal":
            connected_count = sum(1 for p in self.players if p.connected)
            if player.is_host or connected_count <= 1:
                self._advance_round(now)
                return True, ""
            return False, "Only the host can advance early."

        if self.subphase != "question":
            return False, "Round submission window is closed."

        prog = self.round_progress.setdefault(
            player_id,
            {
                "guesses": [],
                "extra_hints": 0,
                "solved": False,
                "between_guess": None,
                "points": 0,
                "scored": False,
            },
        )
        duration = self.borders_seconds if mode == "borders_between" else self.locate_seconds
        elapsed = max(0.0, now - self.phase_started_at)
        remaining = max(0.0, duration - elapsed)

        if action == "reveal_hint":
            if mode != "hint":
                return False, "Hints are only available in Hint Detective mode."
            if prog["solved"]:
                return False, "You have already solved this round."
            if prog["extra_hints"] >= 2:
                return False, "All available hints are already unlocked."
            prog["extra_hints"] += 1
            return True, ""

        if action == "answer_between":
            if mode != "borders_between":
                return False, "Border count answers apply only to Border Bridge rounds."
            if prog["between_guess"] is not None:
                return False, "Answer already submitted for this round."
            try:
                guess_num = int(data.get("count", -1))
            except (TypeError, ValueError):
                return False, "Invalid country count."
            if guess_num < 0 or guess_num > 20:
                return False, "Enter a count between 0 and 20."

            target_num = int(q["min_between"])
            diff = abs(guess_num - target_num)
            if diff == 0:
                pts = 1000 + math.floor(300.0 * (remaining / duration))
            elif diff == 1:
                pts = 450
            elif diff == 2:
                pts = 200
            else:
                pts = 0

            prog["between_guess"] = guess_num
            prog["solved"] = diff == 0
            prog["points"] = pts

            if self._all_players_done_round(mode):
                self._begin_reveal(now)
            return True, ""

        if action == "guess":
            if mode == "borders_between":
                return False, "Submit the minimum intermediate nations count for this round."
            if prog["solved"]:
                return False, "You already located this country."
            if len(prog["guesses"]) >= self.max_locate_guesses:
                return False, "Maximum attempts used for this round."

            raw_code = str(data.get("code") or data.get("ccn3") or data.get("name") or "")
            guessed = resolve_country(raw_code)
            if guessed is None:
                return False, "Unknown territory — click a sovereign nation or pin."

            if any(g["code"] == guessed["code"] for g in prog["guesses"]):
                return False, f"Already guessed {guessed['name']}."

            target = q["target"]
            is_correct = guessed["code"] == target["code"]
            dist_km = 0 if is_correct else haversine_km(
                guessed["lat"], guessed["lng"], target["lat"], target["lng"]
            )
            bearing_code, bearing_arrow = ("OK", "★") if is_correct else compass_bearing(
                guessed["lat"], guessed["lng"], target["lat"], target["lng"]
            )
            heat = 1.0 if is_correct else distance_to_heat(dist_km)

            prog["guesses"].append(
                {
                    "code": guessed["code"],
                    "ccn3": guessed["ccn3"],
                    "name": guessed["name"],
                    "lat": guessed["lat"],
                    "lng": guessed["lng"],
                    "distance_km": dist_km,
                    "bearing": bearing_code,
                    "arrow": bearing_arrow,
                    "heat": heat,
                    "is_correct": is_correct,
                }
            )

            if is_correct:
                attempt_idx = len(prog["guesses"]) - 1
                base_pts = ATTEMPT_BASE_SCORES[min(attempt_idx, len(ATTEMPT_BASE_SCORES) - 1)]
                hint_penalty = prog["extra_hints"] * 75
                speed_bonus = math.floor(150.0 * (remaining / duration))
                prog["solved"] = True
                prog["points"] = max(150, base_pts - hint_penalty) + speed_bonus

            if self._all_players_done_round(mode):
                self._begin_reveal(now)
            return True, ""

        return False, f"Unsupported action: {action}"

    def _advance_round(self, now: float) -> None:
        if self.round_idx + 1 >= len(self.rounds):
            ranked = sorted(self.players, key=lambda p: p.score, reverse=True)
            top = ranked[0].score if ranked else 0
            winners = [p.id for p in ranked if p.score == top] if top > 0 else []
            names = ", ".join(p.name for p in ranked if p.id in winners)
            msg = (
                f"Globe Protocol complete! Winner: {names} ({top} pts)."
                if winners
                else "Globe Protocol complete."
            )
            self.finish_game(winners, msg)
        else:
            self.round_idx += 1
            self._begin_question(now)

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing" or not self.rounds:
            return False
        q = self.rounds[self.round_idx]
        duration = self.borders_seconds if q["mode"] == "borders_between" else self.locate_seconds
        elapsed = now - self.phase_started_at
        if self.subphase == "question" and elapsed >= duration:
            self._begin_reveal(now)
            return True
        if self.subphase == "reveal" and elapsed >= self.REVEAL_SECONDS:
            self._advance_round(now)
            return True
        limit = duration if self.subphase == "question" else self.REVEAL_SECONDS
        sec = int(max(0.0, limit - elapsed))
        if self._last_tick_sec != sec:
            self._last_tick_sec = sec
            return True
        return False

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        if not self.rounds or player_id not in self.round_progress:
            return {}
        q = self.rounds[self.round_idx]
        prog = self.round_progress[player_id]
        hints_visible: list[str] = []
        if q["mode"] == "hint":
            # Start with 2 starter clues; unlock up to all 4 clues on request
            hints_visible = q["hints"][: 2 + prog["extra_hints"]]
        return {
            "round_idx": self.round_idx,
            "guesses": prog["guesses"],
            "guesses_left": max(0, self.max_locate_guesses - len(prog["guesses"])),
            "solved": prog["solved"],
            "between_guess": prog["between_guess"],
            "extra_hints": prog["extra_hints"],
            "hints_visible": hints_visible,
            "points_earned": prog["points"],
        }

    def get_public_state(self) -> dict[str, Any]:
        if not self.rounds:
            return {
                "phase": self.phase,
                "subphase": self.subphase,
                "duration": self.locate_seconds,
                "time_remaining": 0.0,
                "question": {},
                "done_players": [],
                "round_results": {},
                "winner_ids": self.winner_ids,
                "win_reason": self.win_reason,
            }

        now = time.time()
        q = self.rounds[self.round_idx]
        mode = q["mode"]
        duration = self.borders_seconds if mode == "borders_between" else self.locate_seconds
        elapsed = max(0.0, now - self.phase_started_at)
        limit = duration if self.subphase == "question" else self.REVEAL_SECONDS
        remaining = max(0.0, limit - elapsed) if self.phase == "playing" else 0.0

        question: dict[str, Any] = {
            "index": self.round_idx + 1,
            "total": len(self.rounds),
            "mode": mode,
            "prompt": q["prompt"],
            "max_guesses": self.max_locate_guesses,
        }

        if mode == "name":
            question["target_name"] = q["target"]["name"]
        elif mode == "flag":
            if self.subphase == "reveal" or self.phase == "finished":
                question["flag_svg"] = q["target"]["flag_svg"]
                question["flag_code"] = q["target"]["code"]
            else:
                question["flag_svg"] = (
                    get_sanitized_flag_data_uri(q["target"]["code"])
                    or q["target"]["flag_svg"]
                )
            question["flag"] = q["target"]["flag"]
        elif mode == "hint":
            # Always include starter clues in public shape too for spectators cleanly
            question["starter_hints"] = q["hints"][:2]
            question["total_hints"] = len(q["hints"])
        elif mode == "borders_between":
            c_a = q["country_a"]
            c_b = q["country_b"]
            question["country_a"] = {
                "code": c_a["code"],
                "ccn3": c_a["ccn3"],
                "name": c_a["name"],
                "lat": c_a["lat"],
                "lng": c_a["lng"],
                "continent": c_a["continent"],
                "flag_svg": c_a["flag_svg"],
            }
            question["country_b"] = {
                "code": c_b["code"],
                "ccn3": c_b["ccn3"],
                "name": c_b["name"],
                "lat": c_b["lat"],
                "lng": c_b["lng"],
                "continent": c_b["continent"],
                "flag_svg": c_b["flag_svg"],
            }

        reveal: dict[str, Any] | None = None
        if self.subphase == "reveal" or self.phase == "finished":
            if mode == "borders_between":
                path_list = [
                    {
                        "code": COUNTRY_BY_CODE[c]["code"],
                        "ccn3": COUNTRY_BY_CODE[c]["ccn3"],
                        "name": COUNTRY_BY_CODE[c]["name"],
                        "lat": COUNTRY_BY_CODE[c]["lat"],
                        "lng": COUNTRY_BY_CODE[c]["lng"],
                        "flag_svg": COUNTRY_BY_CODE[c]["flag_svg"],
                    }
                    for c in q["path_codes"]
                    if c in COUNTRY_BY_CODE
                ]
                reveal = {
                    "min_between": q["min_between"],
                    "shortest_path": path_list,
                    "explanation": (
                        f"Minimum {q['min_between']} nation(s) between {q['country_a']['name']} and {q['country_b']['name']}: "
                        + " → ".join(item["name"] for item in path_list)
                    ),
                }
            else:
                t = q["target"]
                reveal = {
                    "target": {
                        "code": t["code"],
                        "ccn3": t["ccn3"],
                        "name": t["name"],
                        "capital": t["capital"],
                        "continent": t["continent"],
                        "subregion": t["subregion"],
                        "lat": t["lat"],
                        "lng": t["lng"],
                        "population_label": t["population_label"],
                        "population_rank": t["population_rank"],
                        "area_label": t["area_label"],
                        "area_rank": t["area_rank"],
                        "flag_svg": t["flag_svg"],
                        "landmark_clue": t["landmark_clue"],
                    },
                    "explanation": (
                        f"{t['name']} (Capital: {t['capital']}, {t['subregion']}) · Pop {t['population_label']} · {t['area_label']}."
                    ),
                }

        done_players = []
        for pid, prog in self.round_progress.items():
            if mode == "borders_between":
                if prog["between_guess"] is not None:
                    done_players.append(pid)
            elif prog["solved"] or len(prog["guesses"]) >= self.max_locate_guesses:
                done_players.append(pid)

        round_results = (
            {
                pid: {
                    "solved": prog["solved"],
                    "attempts": len(prog["guesses"]),
                    "between_guess": prog["between_guess"],
                    "points": prog["points"],
                }
                for pid, prog in self.round_progress.items()
            }
            if (self.subphase == "reveal" or self.phase == "finished")
            else {}
        )

        return {
            "phase": self.phase,
            "subphase": self.subphase,
            "duration": duration,
            "time_remaining": round(remaining, 1),
            "question": question,
            "reveal": reveal,
            "done_players": done_players,
            "round_results": round_results,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }
