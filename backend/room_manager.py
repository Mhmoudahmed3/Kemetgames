"""Room lifecycle, WebSocket connection routing, leaderboard persistence, and tick scheduling."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import random
import secrets
import time
from typing import Any
from fastapi import WebSocket

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

ROOM_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
DATA_DIR = Path(__file__).resolve().parent / "data"
LEADERBOARD_PATH = DATA_DIR / "leaderboard.json"

LOWER_IS_BETTER_GAMES = {"skru"}
DUEL_FORFEIT_GAMES = {
    "chess",
    "backgammon",
    "tic_tac_toe",
    "rock_paper_scissors",
    "connect4",
    "playing_cards",
}
PARTY_BOT_TAKEOVER_GAMES = {"dominoes", "ludo", "skru", "uno", "monopoly"}
DUEL_DISCONNECT_GRACE_SECONDS = 20.0
PARTY_DISCONNECT_GRACE_SECONDS = 10.0

ALLOWED_SETTINGS_KEYS: dict[str, set[str]] = {
    "snake": {"difficulty", "duration"},
    "minesweeper": {"difficulty", "rows", "cols", "mines", "width", "height", "booms"},
    "chess": {"difficulty", "time_control", "custom_board", "custom_fen"},
    "backgammon": {"difficulty", "mode"},
    "dominoes": {"difficulty", "target_score"},
    "ludo": {"difficulty"},
    "skru": {"difficulty"},
    "uno": {"difficulty"},
    "qa_trivia": {"difficulty", "category", "rounds"},
    "globe": {"difficulty", "mode", "rounds"},
    "monopoly": {"difficulty"},
    "tic_tac_toe": {"difficulty", "mode", "grid_size", "pass_and_play", "first_player"},
    "rock_paper_scissors": {"difficulty", "mode", "format", "rounds", "pass_and_play"},
    "connect4": {"difficulty", "mode", "blitz_time", "pass_and_play"},
    "playing_cards": {"difficulty", "mode", "subgame", "rounds", "rows", "cols", "pass_and_play", "pairs_count", "grid_size"},
}

BOT_NAMES = [
    "SIREN-01",
    "FALLOUT-02",
    "RADAR-03",
    "BUNKER-04",
    "ASH-05",
    "VECTOR-06",
]


class LeaderboardStore:
    """Thread/loop-safe JSON leaderboard store for persistent player wins & scores."""

    def __init__(self, path: Path = LEADERBOARD_PATH) -> None:
        self.path = path
        self.data: dict[str, dict[str, dict[str, int]]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self.data = raw
        except Exception:
            self.data = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        os.replace(tmp_path, self.path)

    def record_entries(self, entries: list[dict[str, Any]]) -> None:
        if not entries:
            return
        for row in entries:
            game_type = str(row.get("game_type") or "")
            name = str(row.get("name") or "").strip()
            try:
                score = int(row.get("score", 0))
            except (TypeError, ValueError):
                score = 0
            won = bool(row.get("won", False))
            if not game_type or not name:
                continue
            game_board = self.data.setdefault(game_type, {})
            is_first = name not in game_board or game_board[name].get("games", 0) == 0
            stats = game_board.setdefault(
                name, {"wins": 0, "best_score": score if game_type in LOWER_IS_BETTER_GAMES else 0, "games": 0}
            )
            stats["games"] += 1
            if won:
                stats["wins"] += 1
            if game_type in LOWER_IS_BETTER_GAMES:
                if is_first or score < stats["best_score"]:
                    stats["best_score"] = score
            else:
                if score > stats["best_score"]:
                    stats["best_score"] = score
        self._save()

    def get_summary(self, limit_per_game: int = 10) -> dict[str, list[dict[str, Any]]]:
        summary: dict[str, list[dict[str, Any]]] = {}
        for game_type, players in self.data.items():
            ranked = [
                {
                    "name": name,
                    "wins": stats.get("wins", 0),
                    "best_score": stats.get("best_score", 0),
                    "games": stats.get("games", 0),
                }
                for name, stats in players.items()
            ]
            if game_type in LOWER_IS_BETTER_GAMES:
                ranked.sort(key=lambda r: (-r["wins"], r["best_score"], r["name"]))
            else:
                ranked.sort(key=lambda r: (-r["wins"], -r["best_score"], r["name"]))
            summary[game_type] = ranked[:limit_per_game]
        return summary


@dataclass
class ClientSession:
    """Represents a connected or recently disconnected WebSocket player."""

    client_id: str
    name: str = ""
    room_code: str | None = None
    websocket: WebSocket | None = None
    last_seen: float = field(default_factory=time.time)
    session_secret: str = field(default_factory=lambda: secrets.token_urlsafe(24))


@dataclass
class Room:
    """Active multiplayer or solo room wrapping a BaseGame instance."""

    room_code: str
    game_type: str
    is_public: bool
    game: BaseGame
    target_players: int | None = None
    chat: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    leaderboard_recorded: bool = False
    bot_counter: int = 0
    disconnect_deadlines: dict[str, float] = field(default_factory=dict)
    takeover_original_names: dict[str, str] = field(default_factory=dict)
    _last_grace_sec: dict[str, int] = field(default_factory=dict)


def get_game_registry() -> dict[str, type[BaseGame]]:
    """Return all registered game classes keyed by game_type."""
    from backend.games import GAME_REGISTRY

    return GAME_REGISTRY


class RoomManager:
    """Coordinates client sessions, matchmaking rooms, WebSocket broadcasts, and game ticks."""

    def __init__(self, leaderboard: LeaderboardStore | None = None) -> None:
        self.clients: dict[str, ClientSession] = {}
        self.rooms: dict[str, Room] = {}
        self.leaderboard = leaderboard or LeaderboardStore()
        self._disconnecting: set[str] = set()

    @staticmethod
    def _sanitize_name(raw: Any) -> str:
        if raw is None or isinstance(raw, (bool, dict, list)):
            return ""
        text = "".join(ch for ch in str(raw) if ch.isprintable())
        return " ".join(text.split())[:20]

    @staticmethod
    def _safe_int(val: Any, default: int | None = None) -> int | None:
        if val is None or isinstance(val, bool):
            return default
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    def _sanitize_settings(
        self,
        game_cls_or_inst: type[BaseGame] | BaseGame,
        game_type: str,
        raw: Any,
    ) -> dict[str, Any]:
        if not isinstance(raw, dict):
            return {}
        allowed = ALLOWED_SETTINGS_KEYS.get(game_type, {"difficulty"})
        cleaned: dict[str, Any] = {}
        for k, v in raw.items():
            if k not in allowed:
                continue
            if k == "difficulty":
                cleaned["difficulty"] = normalize_difficulty(
                    v, allow_custom=game_cls_or_inst.SUPPORTS_CUSTOM_DIFFICULTY
                )
            elif k in (
                "duration", "target_score", "rounds", "rows", "cols",
                "mines", "width", "height", "booms", "blitz_time"
            ):
                parsed = self._safe_int(v)
                if parsed is not None:
                    cleaned[k] = parsed
            elif k == "pairs_count":
                parsed = self._safe_int(v)
                if parsed is not None and parsed > 0:
                    cleaned["pairs_count"] = parsed
            elif k == "grid_size":
                if isinstance(v, str) and v.strip() in ("3x3", "4x4", "5x5", "6x4"):
                    cleaned["grid_size"] = v.strip()
                else:
                    parsed = self._safe_int(v)
                    if parsed is not None:
                        cleaned["grid_size"] = parsed
            elif k == "mode":
                m_val = str(v or "").strip().lower()
                if game_type == "backgammon" and m_val in ("classic", "tawla_31", "mahbosa"):
                    cleaned["mode"] = m_val
                elif game_type == "globe" and m_val in ("mix", "name", "flag", "hint", "borders_between"):
                    cleaned["mode"] = m_val
                elif game_type == "tic_tac_toe" and m_val in ("classic", "misere", "extended_4x4", "extended_5x5", "4x4", "5x5", "extended", "ultimate"):
                    cleaned["mode"] = m_val
                elif game_type == "rock_paper_scissors" and m_val in ("classic", "lizard_spock", "rpsls"):
                    cleaned["mode"] = m_val
                elif game_type == "connect4" and m_val in ("classic", "pop_out", "five_in_a_row", "5_in_a_row", "blitz"):
                    cleaned["mode"] = m_val
                elif game_type == "playing_cards" and m_val in ("blackjack", "war", "memory", "high_low"):
                    cleaned["mode"] = m_val
            elif k == "subgame":
                sg_val = str(v or "").strip().lower()
                if game_type == "playing_cards" and sg_val in ("blackjack", "war", "memory", "high_low"):
                    cleaned["subgame"] = sg_val
            elif k == "format":
                f_val = str(v or "").strip().lower()
                if game_type == "rock_paper_scissors" and f_val in ("bo3", "bo5", "endless", "best_of_3", "best_of_5", "single"):
                    cleaned["format"] = f_val
            elif k in ("pass_and_play", "local"):
                cleaned["pass_and_play"] = bool(v)
            elif k == "time_control":
                tc = str(v or "").strip()
                if tc in ("3+2", "5+0", "10+0"):
                    cleaned["time_control"] = tc
            elif k == "category":
                from backend.games.qa_trivia_game import normalize_qa_category
                cleaned["category"] = normalize_qa_category(v)
            elif k == "first_player":
                fp = str(v or "").strip().lower()
                if fp in ("x", "o", "random"):
                    cleaned["first_player"] = fp
            elif k == "custom_board" and isinstance(v, list):
                cleaned["custom_board"] = v
            elif k == "custom_fen" and isinstance(v, str):
                cleaned["custom_fen"] = v[:200]
        return cleaned

    def _apply_settings_update(self, room: Room, cleaned: dict[str, Any]) -> None:
        if not cleaned:
            return
        if (
            room.game_type == "minesweeper"
            and "difficulty" in cleaned
            and cleaned["difficulty"] != "custom"
            and not any(
                k in cleaned
                for k in ("rows", "cols", "mines", "width", "height", "booms")
            )
        ):
            for stale in ("rows", "cols", "mines", "width", "height", "booms"):
                room.game.settings.pop(stale, None)
        room.game.settings.update(cleaned)

    def get_catalog(self) -> list[dict[str, Any]]:
        registry = get_game_registry()
        return [
            {
                "game_type": cls.GAME_TYPE,
                "title": cls.TITLE,
                "category": cls.CATEGORY,
                "description": cls.DESCRIPTION,
                "min_players": cls.MIN_PLAYERS,
                "max_players": cls.MAX_PLAYERS,
                "supports_solo": cls.SUPPORTS_SOLO,
                "supports_bots": cls.SUPPORTS_BOTS,
                "supports_spectators": cls.SUPPORTS_SPECTATORS,
                "supports_custom_difficulty": cls.SUPPORTS_CUSTOM_DIFFICULTY,
                "default_settings": cls.DEFAULT_SETTINGS,
            }
            for cls in registry.values()
        ]

    def _generate_room_code(self) -> str:
        while True:
            code = "".join(random.choices(ROOM_CODE_ALPHABET, k=6))
            if code not in self.rooms:
                return code

    async def connect(
        self, client_id: str, websocket: WebSocket, secret: str | None = None
    ) -> bool:
        if not client_id or len(client_id) > 64:
            await websocket.close(code=4000, reason="Invalid client ID.")
            return False

        existing = self.clients.get(client_id)
        if existing:
            if secret is not None:
                if not secrets.compare_digest(secret, existing.session_secret):
                    await websocket.accept()
                    await websocket.send_json(
                        {
                            "type": "ERROR",
                            "room_code": "",
                            "game_type": "",
                            "public_state": {},
                            "private_state": {},
                            "players": [],
                            "message": "Invalid session secret.",
                        }
                    )
                    await websocket.close(code=4003, reason="Invalid session secret.")
                    return False
            elif existing.websocket is not None:
                await websocket.accept()
                await websocket.send_json(
                    {
                        "type": "ERROR",
                        "room_code": "",
                        "game_type": "",
                        "public_state": {},
                        "private_state": {},
                        "players": [],
                        "message": "Session is already active; valid session secret required.",
                    }
                )
                await websocket.close(code=4003, reason="Session already active.")
                return False

            await websocket.accept()
            old_ws = existing.websocket
            existing.websocket = websocket
            existing.last_seen = time.time()
            if old_ws is not None and old_ws is not websocket:
                try:
                    await old_ws.close(code=1000, reason="Session reconnected elsewhere.")
                except Exception:
                    pass

            if existing.room_code and existing.room_code not in self.rooms:
                existing.room_code = None

            if existing.room_code and existing.room_code in self.rooms:
                room = self.rooms[existing.room_code]
                slot = room.game.get_player(client_id)
                is_spec = any(s.id == client_id for s in room.game.spectators)
                reclaimable = client_id in room.takeover_original_names
                if (slot is None and not is_spec) or (
                    slot is not None and slot.is_bot and not reclaimable
                ):
                    existing.room_code = None
                    room.takeover_original_names.pop(client_id, None)
                else:
                    room.disconnect_deadlines.pop(client_id, None)
                    room._last_grace_sec.pop(client_id, None)
                    if reclaimable:
                        orig_name = room.takeover_original_names.pop(client_id)
                        if slot:
                            slot.is_bot = False
                            slot.name = orig_name
                            slot.connected = True
                            room.game.log_event(
                                f"{orig_name} reconnected and resumed control from AI.",
                                kind="info",
                            )
                    room.game.on_player_reconnect(client_id)
                    await self._send_room_joined(existing, room)
                    await self._broadcast_room_update(room, exclude_id=client_id)
                    if room.game.phase in ("pre_game", "playing", "finished"):
                        await self._send_game_sync(room)
                    if room.game.phase == "finished":
                        await self._send_game_over_to_client(client_id, room)
                    return True
        else:
            await websocket.accept()
            self.clients[client_id] = ClientSession(
                client_id=client_id, websocket=websocket
            )
        await self.send_lobby_state(client_id)
        return True

    async def disconnect(
        self, client_id: str, websocket: WebSocket | None = None
    ) -> None:
        session = self.clients.get(client_id)
        if not session:
            return
        if (
            websocket is not None
            and session.websocket is not None
            and session.websocket is not websocket
        ):
            return
        if client_id in self._disconnecting:
            return
        self._disconnecting.add(client_id)
        try:
            session.websocket = None
            session.last_seen = time.time()
            if session.room_code and session.room_code in self.rooms:
                room = self.rooms[session.room_code]
                if room.game.phase == "waiting":
                    await self._remove_from_room(client_id, room)
                    return

                was_finished = room.game.phase == "finished"
                was_spec = any(s.id == client_id for s in room.game.spectators)
                changed = False
                if was_spec:
                    room.game.spectators = [
                        s for s in room.game.spectators if s.id != client_id
                    ]
                    session.room_code = None
                    changed = True
                else:
                    changed = room.game.on_player_disconnect(client_id)

                human_connected = [
                    p for p in room.game.players if not p.is_bot and p.connected
                ]
                any_human_connected = bool(human_connected) or any(
                    s.connected for s in room.game.spectators
                )
                if not any_human_connected:
                    self._cleanup_room(room.room_code)
                    await self.broadcast_lobby_state()
                    return

                player = room.game.get_player(client_id)
                if player and player.is_host and human_connected:
                    player.is_host = False
                    human_connected[0].is_host = True
                    changed = True

                if (
                    player
                    and not was_spec
                    and room.game.phase in ("pre_game", "playing")
                    and human_connected
                ):
                    if room.game_type in DUEL_FORFEIT_GAMES:
                        room.disconnect_deadlines[client_id] = (
                            time.time() + DUEL_DISCONNECT_GRACE_SECONDS
                        )
                        room.game.log_event(
                            f"{player.name} disconnected — {int(DUEL_DISCONNECT_GRACE_SECONDS)}s to reconnect before forfeit.",
                            kind="warn",
                        )
                        changed = True
                    elif room.game_type in PARTY_BOT_TAKEOVER_GAMES:
                        room.disconnect_deadlines[client_id] = (
                            time.time() + PARTY_DISCONNECT_GRACE_SECONDS
                        )
                        room.game.log_event(
                            f"{player.name} disconnected — AI bot takeover in {int(PARTY_DISCONNECT_GRACE_SECONDS)}s unless reconnected.",
                            kind="warn",
                        )
                        changed = True

                if changed:
                    await self._broadcast_room_update(room)
                    if not was_finished and room.game.phase == "finished":
                        await self._handle_game_finished(room)
                    elif room.game.phase in ("pre_game", "playing", "finished"):
                        await self._send_game_sync(room)
        finally:
            self._disconnecting.discard(client_id)

    async def handle_message(self, client_id: str, raw_text: str) -> None:
        try:
            msg = json.loads(raw_text)
        except json.JSONDecodeError:
            await self._send_error(client_id, "Malformed JSON payload.")
            return

        if not isinstance(msg, dict):
            await self._send_error(client_id, "Payload must be a JSON object.")
            return

        msg_type = str(msg.get("type") or "").strip().upper()
        player_name = self._sanitize_name(msg.get("player_name"))
        room_code = str(msg.get("room_code") or "").strip().upper()
        game_type = str(msg.get("game_type") or "").strip().lower()
        payload = msg.get("payload") if isinstance(msg.get("payload"), dict) else {}
        action = str(payload.get("action") or "").strip().lower()
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}

        session = self.clients.get(client_id)
        if not session:
            await self._send_error(client_id, "Unknown client session.")
            return
        session.last_seen = time.time()

        if msg_type == "SET_NAME":
            await self._on_set_name(session, player_name)
        elif msg_type == "CREATE_ROOM":
            await self._on_create_room(session, player_name, game_type, data)
        elif msg_type == "JOIN_ROOM":
            await self._on_join_room(session, player_name, room_code)
        elif msg_type == "LEAVE_ROOM":
            await self._on_leave_room(session)
        elif msg_type == "START_GAME":
            await self._on_start_game(session, data)
        elif msg_type == "GAME_ACTION":
            await self._on_game_action(session, action, data)
        elif msg_type == "CHAT_MSG":
            await self._on_chat_msg(session, data)
        else:
            await self._send_error(client_id, f"Unsupported message type: {msg_type}")

    async def _on_set_name(self, session: ClientSession, player_name: str) -> None:
        clean = self._sanitize_name(player_name)
        if not clean:
            await self._send_error(session.client_id, "Display name cannot be empty.")
            return

        if session.room_code and session.room_code in self.rooms:
            room = self.rooms[session.room_code]
            if room.game.phase in ("pre_game", "playing"):
                if clean == session.name:
                    return
                await self._send_error(
                    session.client_id,
                    "Cannot change display name while a match is in progress.",
                )
                return

        session.name = clean
        if session.room_code and session.room_code in self.rooms:
            room = self.rooms[session.room_code]
            player = room.game.get_player(session.client_id)
            if player:
                player.name = clean
            for spec in room.game.spectators:
                if spec.id == session.client_id:
                    spec.name = clean
            await self._broadcast_room_update(room)
        await self.send_lobby_state(session.client_id)

    async def _on_create_room(
        self,
        session: ClientSession,
        player_name: str,
        game_type: str,
        data: dict[str, Any],
    ) -> None:
        if not session.name and player_name:
            session.name = self._sanitize_name(player_name)
        if not session.name:
            await self._send_error(session.client_id, "Enter your player name first.")
            return

        registry = get_game_registry()
        if game_type not in registry:
            await self._send_error(session.client_id, f"Unknown game type: {game_type}")
            return

        raw_bots = data.get("bot_count", 0)
        if raw_bots is None or raw_bots == "":
            requested_bots = 0
        elif isinstance(raw_bots, bool):
            await self._send_error(session.client_id, "Invalid bot count.")
            return
        else:
            try:
                requested_bots = int(raw_bots)
            except (TypeError, ValueError):
                await self._send_error(session.client_id, "Invalid bot count.")
                return
        if requested_bots < 0:
            await self._send_error(session.client_id, "Bot count cannot be negative.")
            return

        game_cls = registry[game_type]

        raw_player_count = data.get("player_count")
        if raw_player_count is not None and raw_player_count != "":
            if isinstance(raw_player_count, bool):
                await self._send_error(session.client_id, "Invalid player count.")
                return
            try:
                pc = int(raw_player_count)
            except (TypeError, ValueError):
                await self._send_error(session.client_id, "Invalid player count.")
                return
            if pc < game_cls.MIN_PLAYERS:
                await self._send_error(
                    session.client_id, f"Need at least {game_cls.MIN_PLAYERS} player(s) to launch."
                )
                return
            if pc > game_cls.MAX_PLAYERS:
                await self._send_error(
                    session.client_id, f"Maximum {game_cls.MAX_PLAYERS} players allowed."
                )
                return
        else:
            pc = None

        code = self._generate_room_code()
        solo = bool(data.get("solo", False))
        settings = self._sanitize_settings(game_cls, game_type, data.get("settings"))
        is_pass_and_play = bool(
            data.get("pass_and_play", False) or settings.get("pass_and_play", False)
        )
        if is_pass_and_play:
            settings["pass_and_play"] = True
        is_public = bool(data.get("is_public", not solo and not is_pass_and_play))

        host_slot = PlayerSlot(
            id=session.client_id,
            name=session.name,
            is_bot=False,
            is_host=True,
            connected=True,
            seat=0,
        )
        game = game_cls(room_code=code, players=[host_slot], settings=settings)
        room = Room(
            room_code=code,
            game_type=game_type,
            is_public=is_public,
            game=game,
            target_players=pc,
        )

        if is_pass_and_play:
            # 2-Player Pass-and-Play: allocate local Player 2 human slot
            p2_slot = PlayerSlot(
                id=f"{session.client_id}_p2",
                name=data.get("player2_name") or "Player 2",
                is_bot=False,
                is_host=False,
                connected=True,
                seat=1,
            )
            game.players.append(p2_slot)

        if solo and not is_pass_and_play and not game.SUPPORTS_SOLO and game.SUPPORTS_BOTS and requested_bots == 0:
            if pc is not None:
                requested_bots = max(1, pc - 1)
            else:
                requested_bots = max(1, game.MIN_PLAYERS - 1)
        if requested_bots > 0 and game.SUPPORTS_BOTS and not is_pass_and_play:
            max_bots = game.MAX_PLAYERS - len(game.players)
            for _ in range(min(requested_bots, max_bots)):
                self._add_bot_slot(room)

        if solo or is_pass_and_play:
            ok, err = game.can_start()
            if not ok:
                await self._send_error(session.client_id, err)
                return

        if session.room_code and session.room_code in self.rooms:
            await self._remove_from_room(session.client_id, self.rooms[session.room_code])

        self.rooms[code] = room
        session.room_code = code
        room.game.log_event(f"{session.name} created room {code}.")

        await self._send_room_joined(session, room)

        if solo or is_pass_and_play:
            await self._start_room_game(room, settings)
        await self.broadcast_lobby_state()

    async def _on_join_room(
        self, session: ClientSession, player_name: str, room_code: str
    ) -> None:
        if not session.name and player_name:
            session.name = self._sanitize_name(player_name)
        if not session.name:
            await self._send_error(session.client_id, "Enter your player name first.")
            return
        if not room_code or room_code not in self.rooms:
            await self._send_error(
                session.client_id, f"Room {room_code or '------'} not found."
            )
            return

        room = self.rooms[room_code]
        if session.room_code == room_code:
            player = room.game.get_player(session.client_id)
            is_spec = any(s.id == session.client_id for s in room.game.spectators)
            reclaimable = session.client_id in room.takeover_original_names
            if (player is None and not is_spec) or (
                player is not None and player.is_bot and not reclaimable
            ):
                session.room_code = None
                await self.send_lobby_state(session.client_id)
                return
            room.disconnect_deadlines.pop(session.client_id, None)
            room._last_grace_sec.pop(session.client_id, None)
            if reclaimable:
                orig_name = room.takeover_original_names.pop(session.client_id)
                if player:
                    player.is_bot = False
                    player.name = orig_name
                    player.connected = True
            if player:
                room.game.on_player_reconnect(session.client_id)
            await self._send_room_joined(session, room)
            if room.game.phase != "waiting":
                await self._send_game_sync(room)
            if room.game.phase == "finished":
                await self._send_game_over_to_client(session.client_id, room)
            return

        # Validate joinability BEFORE removing from current room
        existing_slot = room.game.get_player(session.client_id)
        if (
            existing_slot is not None
            and existing_slot.is_bot
            and session.client_id not in room.takeover_original_names
        ):
            await self._send_error(
                session.client_id,
                "Your previous seat in this room was permanently converted to an AI bot.",
            )
            return
        can_join_waiting = (
            room.game.phase == "waiting"
            and len(room.game.players) < room.game.MAX_PLAYERS
        )
        can_spectate = (
            room.game.SUPPORTS_SPECTATORS and room.game.phase != "finished"
        )
        if not (existing_slot or can_join_waiting or can_spectate):
            await self._send_error(
                session.client_id, "Room is full or match already in progress."
            )
            return

        if session.room_code and session.room_code in self.rooms:
            await self._remove_from_room(session.client_id, self.rooms[session.room_code])

        # Reconnect check by same client_id
        if existing_slot:
            room.disconnect_deadlines.pop(session.client_id, None)
            room._last_grace_sec.pop(session.client_id, None)
            if session.client_id in room.takeover_original_names:
                orig_name = room.takeover_original_names.pop(session.client_id)
                existing_slot.is_bot = False
                existing_slot.name = orig_name
            elif room.game.phase == "waiting":
                existing_slot.name = session.name
            existing_slot.connected = True
            session.room_code = room_code
            room.game.on_player_reconnect(session.client_id)
            await self._send_room_joined(session, room)
            await self._broadcast_room_update(room, exclude_id=session.client_id)
            if room.game.phase != "waiting":
                await self._send_game_sync(room)
            if room.game.phase == "finished":
                await self._send_game_over_to_client(session.client_id, room)
            return

        if can_join_waiting:
            slot = PlayerSlot(
                id=session.client_id,
                name=session.name,
                is_bot=False,
                is_host=False,
                connected=True,
                seat=len(room.game.players),
            )
            room.game.players.append(slot)
            session.room_code = room_code
            room.game.log_event(f"{session.name} joined the room.")
            await self._send_room_joined(session, room)
            await self._broadcast_room_update(room, exclude_id=session.client_id)
            await self.broadcast_lobby_state()
            return

        if can_spectate:
            spec_slot = PlayerSlot(
                id=session.client_id,
                name=session.name,
                is_bot=False,
                is_host=False,
                connected=True,
                seat=-1,
                role="spectator",
            )
            room.game.spectators.append(spec_slot)
            session.room_code = room_code
            room.game.log_event(f"{session.name} joined as spectator.")
            await self._send_room_joined(session, room)
            await self._broadcast_room_update(room, exclude_id=session.client_id)
            if room.game.phase != "waiting":
                await self._send_game_sync(room)
            return

    async def _on_leave_room(self, session: ClientSession) -> None:
        if session.room_code and session.room_code in self.rooms:
            room = self.rooms[session.room_code]
            await self._remove_from_room(session.client_id, room)
        session.room_code = None
        await self.send_lobby_state(session.client_id)

    def _convert_to_bot_takeover(
        self, room: Room, player: PlayerSlot, save_original: bool = False
    ) -> None:
        if save_original and player.id not in room.takeover_original_names:
            room.takeover_original_names[player.id] = player.name
        elif not save_original:
            room.takeover_original_names.pop(player.id, None)
            sess = self.clients.get(player.id)
            if sess and sess.room_code == room.room_code:
                sess.room_code = None
        player.is_bot = True
        player.connected = True
        player.is_host = False
        if not player.name.endswith(" [AI]"):
            player.name = f"{player.name} [AI]"
        room.game.on_bot_takeover(player.id)

    async def _remove_from_room(self, client_id: str, room: Room) -> None:
        session = self.clients.get(client_id)
        if session:
            session.room_code = None
        room.disconnect_deadlines.pop(client_id, None)
        room._last_grace_sec.pop(client_id, None)
        room.takeover_original_names.pop(client_id, None)

        # Spectator leave
        was_spec = any(s.id == client_id for s in room.game.spectators)
        if was_spec:
            room.game.spectators = [s for s in room.game.spectators if s.id != client_id]
            any_human_connected = any(
                not p.is_bot and p.connected for p in room.game.players
            ) or any(s.connected for s in room.game.spectators)
            if not any_human_connected:
                self._cleanup_room(room.room_code)
                await self.broadcast_lobby_state(exclude_id=client_id)
            else:
                await self._broadcast_room_update(room)
            return

        leaving_player = room.game.get_player(client_id)
        if not leaving_player:
            return

        if room.game.phase == "waiting":
            room.game.players = [p for p in room.game.players if p.id != client_id]
            for idx, p in enumerate(room.game.players):
                p.seat = idx
            human_players = [p for p in room.game.players if not p.is_bot]
            if not human_players:
                self._cleanup_room(room.room_code)
                await self.broadcast_lobby_state(exclude_id=client_id)
                return
            if leaving_player.is_host:
                human_players[0].is_host = True
            room.game.log_event(f"{leaving_player.name} left the room.")
            await self._broadcast_room_update(room)
            await self.broadcast_lobby_state(exclude_id=client_id)
        else:
            was_finished = room.game.phase == "finished"
            human_connected = [
                p
                for p in room.game.players
                if not p.is_bot and p.connected and p.id != client_id
            ]
            if not human_connected:
                self._cleanup_room(room.room_code)
                await self.broadcast_lobby_state(exclude_id=client_id)
                return

            if leaving_player.is_host:
                leaving_player.is_host = False
                human_connected[0].is_host = True

            if room.game.phase in ("pre_game", "playing"):
                if room.game_type in DUEL_FORFEIT_GAMES:
                    leaving_player.connected = False
                    room.game.forfeit_player(
                        client_id,
                        f"{leaving_player.name} left the match — {human_connected[0].name} wins by forfeit!",
                    )
                elif room.game_type in PARTY_BOT_TAKEOVER_GAMES:
                    orig_name = leaving_player.name
                    self._convert_to_bot_takeover(room, leaving_player, save_original=False)
                    room.game.log_event(
                        f"{orig_name} left the match — {leaving_player.name} took over.",
                        kind="warn",
                    )
                else:
                    room.game.on_player_disconnect(client_id)
            else:
                leaving_player.connected = False

            await self._broadcast_room_update(room)
            if not was_finished and room.game.phase == "finished":
                await self._handle_game_finished(room, exclude_lobby_id=client_id)
            else:
                await self._send_game_sync(room)

    def _cleanup_room(self, room_code: str) -> None:
        room = self.rooms.pop(room_code, None)
        if not room:
            return
        room.disconnect_deadlines.clear()
        room._last_grace_sec.clear()
        room.takeover_original_names.clear()
        for session in self.clients.values():
            if session.room_code == room_code:
                session.room_code = None

    def _clear_takeovers(self, room: Room) -> None:
        """Clear reclaimable AI takeovers and release stale room bindings for bot seats."""
        for pid in list(room.takeover_original_names):
            sess = self.clients.get(pid)
            if sess and sess.room_code == room.room_code:
                sess.room_code = None
        room.takeover_original_names.clear()
        for p in room.game.players:
            if p.is_bot:
                sess = self.clients.get(p.id)
                if sess and sess.room_code == room.room_code:
                    sess.room_code = None

    def _prune_disconnected_humans_for_waiting(self, room: Room) -> None:
        kept: list[PlayerSlot] = []
        for p in room.game.players:
            if p.is_bot or p.connected:
                kept.append(p)
            else:
                sess = self.clients.get(p.id)
                if sess and sess.room_code == room.room_code:
                    sess.room_code = None
        room.game.players = kept
        for idx, p in enumerate(room.game.players):
            p.seat = idx
        humans = [p for p in room.game.players if not p.is_bot]
        if humans and not any(p.is_host for p in humans):
            humans[0].is_host = True

    def _add_bot_slot(self, room: Room) -> PlayerSlot:
        room.bot_counter += 1
        bot_name = BOT_NAMES[(room.bot_counter - 1) % len(BOT_NAMES)]
        slot = PlayerSlot(
            id=f"bot_{room.room_code}_{room.bot_counter}",
            name=f"{bot_name} [AI]",
            is_bot=True,
            is_host=False,
            connected=True,
            seat=len(room.game.players),
        )
        room.game.players.append(slot)
        return slot

    async def _on_start_game(
        self, session: ClientSession, data: dict[str, Any]
    ) -> None:
        if not session.room_code or session.room_code not in self.rooms:
            await self._send_error(session.client_id, "You are not inside a room.")
            return
        room = self.rooms[session.room_code]
        player = room.game.get_player(session.client_id)
        if player and player.is_bot:
            await self._send_error(
                session.client_id, "AI-controlled seats cannot perform manual actions."
            )
            return
        if not player or not player.is_host:
            await self._send_error(session.client_id, "Only the room host can start.")
            return
        if room.game.phase not in ("waiting", "finished"):
            await self._send_error(session.client_id, "Game is already running.")
            return

        if room.game.phase == "finished":
            self._clear_takeovers(room)
            self._prune_disconnected_humans_for_waiting(room)
            room.game.reset_for_rematch()
            room.leaderboard_recorded = False

        raw_settings = data.get("settings")
        settings = (
            self._sanitize_settings(room.game, room.game_type, raw_settings)
            if isinstance(raw_settings, dict)
            else None
        )
        prev_settings = dict(room.game.settings)
        if settings:
            self._apply_settings_update(room, settings)

        ok, err = room.game.can_start()
        if not ok:
            if settings:
                room.game.settings = prev_settings
            await self._send_error(session.client_id, err)
            return

        await self._start_room_game(room, settings)
        await self.broadcast_lobby_state()

    async def _start_room_game(
        self, room: Room, settings: dict[str, Any] | None = None
    ) -> None:
        room.leaderboard_recorded = False
        room.disconnect_deadlines.clear()
        room._last_grace_sec.clear()
        self._clear_takeovers(room)
        room.game.start_game(settings)
        await self._broadcast_to_room(
            room,
            {
                "type": "GAME_STARTED",
                "room_code": room.room_code,
                "game_type": room.game_type,
                "public_state": room.game.get_public_state(),
                "private_state": {},
                "players": self._room_players_payload(room),
                "message": f"{room.game.TITLE} started.",
            },
        )
        await self._send_game_sync(room)
        if room.game.phase == "finished":
            await self._handle_game_finished(room)

    async def _on_game_action(
        self, session: ClientSession, action: str, data: dict[str, Any]
    ) -> None:
        if not session.room_code or session.room_code not in self.rooms:
            await self._send_error(session.client_id, "Not currently in a room.")
            return
        room = self.rooms[session.room_code]
        player = room.game.get_player(session.client_id)
        if player and player.is_bot:
            await self._send_error(
                session.client_id, "AI-controlled seats cannot perform manual actions."
            )
            return

        # Pre-game room management actions within waiting room
        if action == "add_bot":
            if not player or not player.is_host:
                await self._send_error(session.client_id, "Only the host can add bots.")
                return
            if room.game.phase != "waiting":
                await self._send_error(session.client_id, "Cannot add bots mid-game.")
                return
            if not room.game.SUPPORTS_BOTS:
                await self._send_error(session.client_id, "This game does not use bots.")
                return
            if len(room.game.players) >= room.game.MAX_PLAYERS:
                await self._send_error(session.client_id, "Room is already full.")
                return
            bot = self._add_bot_slot(room)
            room.game.log_event(f"{bot.name} entered the bunker.")
            await self._broadcast_room_update(room)
            await self.broadcast_lobby_state()
            return

        if action == "remove_bot":
            if not player or not player.is_host:
                await self._send_error(session.client_id, "Only the host can remove bots.")
                return
            if room.game.phase != "waiting":
                await self._send_error(session.client_id, "Cannot remove bots mid-game.")
                return
            raw_bot_id = data.get("bot_id")
            bot_id = raw_bot_id.strip() if isinstance(raw_bot_id, str) else ""
            before = len(room.game.players)
            room.game.players = (
                [
                    p
                    for p in room.game.players
                    if not (p.is_bot and p.id == bot_id)
                ]
                if bot_id
                else self._pop_last_bot(room.game.players)
            )
            if len(room.game.players) != before:
                for idx, p in enumerate(room.game.players):
                    p.seat = idx
                await self._broadcast_room_update(room)
                await self.broadcast_lobby_state()
            return

        if action == "update_settings":
            if not player or not player.is_host:
                await self._send_error(session.client_id, "Only the host can change settings.")
                return
            if room.game.phase != "waiting":
                await self._send_error(session.client_id, "Cannot update settings mid-game.")
                return
            updated = self._sanitize_settings(room.game, room.game_type, data)
            if not updated:
                await self._send_error(session.client_id, "No valid settings provided.")
                return
            self._apply_settings_update(room, updated)
            await self._broadcast_room_update(room)
            await self.broadcast_lobby_state()
            return

        if action == "rematch":
            connected_humans = [
                p for p in room.game.players if not p.is_bot and p.connected
            ]
            if not player or (not player.is_host and len(connected_humans) > 1):
                await self._send_error(session.client_id, "Only the host can trigger rematch.")
                return
            if room.game.phase != "finished":
                await self._send_error(session.client_id, "Match has not finished yet.")
                return
            room.disconnect_deadlines.clear()
            room._last_grace_sec.clear()
            self._clear_takeovers(room)
            self._prune_disconnected_humans_for_waiting(room)
            room.game.reset_for_rematch()
            room.leaderboard_recorded = False
            if data.get("to_lobby"):
                room.game.log_event("Returned to match staging.")
                await self._broadcast_room_update(room)
                await self.broadcast_lobby_state()
            else:
                ok, err = room.game.can_start()
                if ok:
                    await self._start_room_game(room, room.game.settings)
                else:
                    await self._broadcast_room_update(room)
                    await self.broadcast_lobby_state()
                    await self._send_error(session.client_id, err)
            return

        if not player:
            await self._send_error(session.client_id, "Spectators cannot perform actions.")
            return

        acting_id = session.client_id
        if room.game.settings.get("pass_and_play"):
            acting_id = data.get("player_id") or room.game.turn_player_id or session.client_id

        ok, err = room.game.handle_action(acting_id, action, data)
        if not ok:
            await self._send_error(session.client_id, err or "Illegal move.")
            return

        await self._send_game_sync(room)
        if room.game.phase == "finished":
            await self._handle_game_finished(room)

    @staticmethod
    def _pop_last_bot(players: list[PlayerSlot]) -> list[PlayerSlot]:
        for idx in range(len(players) - 1, -1, -1):
            if players[idx].is_bot:
                return players[:idx] + players[idx + 1 :]
        return players

    async def _on_chat_msg(
        self, session: ClientSession, data: dict[str, Any]
    ) -> None:
        if not session.room_code or session.room_code not in self.rooms:
            await self._send_error(session.client_id, "Join a room to chat.")
            return
        raw_text = data.get("text")
        text = raw_text.strip() if isinstance(raw_text, str) else ""
        if not text:
            return
        text = text[:280]
        room = self.rooms[session.room_code]
        entry = {
            "sender": session.name or "Anonymous",
            "sender_id": session.client_id,
            "text": text,
            "ts": round(time.time(), 2),
        }
        room.chat.append(entry)
        if len(room.chat) > 50:
            room.chat = room.chat[-50:]
        await self._broadcast_room_update(room, message=f"{entry['sender']}: {text}")

    async def tick_all_rooms(self) -> None:
        """Advance timers, disconnect grace deadlines, and bot moves across all active rooms."""
        now = time.time()
        for room in list(self.rooms.values()):
            if room.game.phase not in ("pre_game", "playing"):
                continue
            changed = False

            if room.disconnect_deadlines:
                human_connected = [
                    p for p in room.game.players if not p.is_bot and p.connected
                ]
                for pid, deadline in list(room.disconnect_deadlines.items()):
                    slot = room.game.get_player(pid)
                    if not slot or slot.connected:
                        room.disconnect_deadlines.pop(pid, None)
                        room._last_grace_sec.pop(pid, None)
                        continue
                    rem_sec = int(max(0.0, deadline - now))
                    if now >= deadline:
                        room.disconnect_deadlines.pop(pid, None)
                        room._last_grace_sec.pop(pid, None)
                        if not human_connected:
                            self._cleanup_room(room.room_code)
                            await self.broadcast_lobby_state()
                            break
                        if room.game_type in DUEL_FORFEIT_GAMES:
                            if room.game.forfeit_player(
                                pid,
                                f"{slot.name} failed to reconnect within {int(DUEL_DISCONNECT_GRACE_SECONDS)}s — {human_connected[0].name} wins by forfeit!",
                            ):
                                changed = True
                        elif room.game_type in PARTY_BOT_TAKEOVER_GAMES:
                            orig_name = slot.name
                            self._convert_to_bot_takeover(room, slot, save_original=True)
                            room.game.log_event(
                                f"{orig_name} timed out — {slot.name} took over the seat.",
                                kind="warn",
                            )
                            changed = True
                    elif room._last_grace_sec.get(pid) != rem_sec:
                        room._last_grace_sec[pid] = rem_sec
                        changed = True

                if room.room_code not in self.rooms:
                    continue

            if room.game.phase in ("pre_game", "playing"):
                try:
                    if room.game.tick(now):
                        changed = True
                except Exception as exc:
                    room.game.log_event(f"Engine tick warning: {exc}", kind="warn")

            if changed:
                await self._send_game_sync(room)
                if room.game.phase == "finished":
                    await self._handle_game_finished(room)

    async def _handle_game_finished(
        self, room: Room, exclude_lobby_id: str | None = None
    ) -> None:
        room.disconnect_deadlines.clear()
        room._last_grace_sec.clear()
        if not room.leaderboard_recorded:
            room.leaderboard_recorded = True
            self.leaderboard.record_entries(room.game.get_leaderboard_entries())
        await self._broadcast_to_room(
            room,
            {
                "type": "GAME_OVER",
                "room_code": room.room_code,
                "game_type": room.game_type,
                "public_state": {
                    **room.game.get_public_state(),
                    "room_meta": self._room_meta_state(room),
                },
                "private_state": {},
                "players": self._room_players_payload(room),
                "message": room.game.win_reason or "Match complete.",
            },
        )
        await self.broadcast_lobby_state(exclude_id=exclude_lobby_id)

    async def _send_game_over_to_client(self, client_id: str, room: Room) -> None:
        await self._send_json(
            client_id,
            {
                "type": "GAME_OVER",
                "room_code": room.room_code,
                "game_type": room.game_type,
                "public_state": {
                    **room.game.get_public_state(),
                    "room_meta": self._room_meta_state(room),
                },
                "private_state": {},
                "players": self._room_players_payload(room),
                "message": room.game.win_reason or "Match complete.",
            },
        )

    def _room_players_payload(self, room: Room) -> list[dict[str, Any]]:
        return [p.to_dict() for p in room.game.players] + [
            s.to_dict() for s in room.game.spectators
        ]

    def _room_meta_state(self, room: Room) -> dict[str, Any]:
        now = time.time()
        return {
            "room_code": room.room_code,
            "game_type": room.game_type,
            "title": room.game.TITLE,
            "phase": room.game.phase,
            "is_public": room.is_public,
            "min_players": room.game.MIN_PLAYERS,
            "max_players": room.game.MAX_PLAYERS,
            "target_players": room.target_players,
            "supports_bots": room.game.SUPPORTS_BOTS,
            "supports_spectators": room.game.SUPPORTS_SPECTATORS,
            "supports_custom_difficulty": room.game.SUPPORTS_CUSTOM_DIFFICULTY,
            "settings": room.game.settings,
            "disconnect_grace": {
                pid: round(max(0.0, deadline - now), 1)
                for pid, deadline in room.disconnect_deadlines.items()
            },
            "bot_takeovers": sorted(room.takeover_original_names.keys()),
            "chat": room.chat[-30:],
            "events": room.game.events[-30:],
        }

    async def _send_room_joined(self, session: ClientSession, room: Room) -> None:
        public_state = {
            **room.game.get_public_state(),
            "room_meta": self._room_meta_state(room),
        }
        await self._send_json(
            session.client_id,
            {
                "type": "ROOM_JOINED",
                "room_code": room.room_code,
                "game_type": room.game_type,
                "public_state": public_state,
                "private_state": room.game.get_private_state(session.client_id),
                "players": self._room_players_payload(room),
                "message": f"Connected to room {room.room_code}.",
            },
        )

    async def _broadcast_room_update(
        self, room: Room, message: str = "", exclude_id: str | None = None
    ) -> None:
        public_state = {
            **room.game.get_public_state(),
            "room_meta": self._room_meta_state(room),
        }
        await self._broadcast_to_room(
            room,
            {
                "type": "ROOM_UPDATE",
                "room_code": room.room_code,
                "game_type": room.game_type,
                "public_state": public_state,
                "private_state": {},
                "players": self._room_players_payload(room),
                "message": message,
            },
            exclude_id=exclude_id,
        )

    async def _send_game_sync(self, room: Room) -> None:
        public_state = {
            **room.game.get_public_state(),
            "room_meta": self._room_meta_state(room),
        }
        players_payload = self._room_players_payload(room)
        # Send strictly isolated GAME_STATE to each player (private_state remains empty in GAME_STATE; private_state dispatched via PRIVATE_STATE)
        for p in room.game.players:
            if not self._is_active_room_recipient(room, p):
                continue
            priv = room.game.get_private_state(p.id) or {}
            await self._send_json(
                p.id,
                {
                    "type": "GAME_STATE",
                    "room_code": room.room_code,
                    "game_type": room.game_type,
                    "public_state": public_state,
                    "private_state": {},
                    "players": players_payload,
                    "message": "",
                },
            )
            if priv:
                await self._send_json(
                    p.id,
                    {
                        "type": "PRIVATE_STATE",
                        "room_code": room.room_code,
                        "game_type": room.game_type,
                        "public_state": {},
                        "private_state": priv,
                        "players": players_payload,
                        "message": "",
                    },
                )
        for s in room.game.spectators:
            if not self._is_active_room_recipient(room, s):
                continue
            await self._send_json(
                s.id,
                {
                    "type": "GAME_STATE",
                    "room_code": room.room_code,
                    "game_type": room.game_type,
                    "public_state": public_state,
                    "private_state": {},
                    "players": players_payload,
                    "message": "",
                },
            )

    def _open_public_rooms_payload(self) -> list[dict[str, Any]]:
        open_rooms: list[dict[str, Any]] = []
        for room in self.rooms.values():
            if not room.is_public:
                continue
            joinable = room.game.phase == "waiting" and len(room.game.players) < room.game.MAX_PLAYERS
            spectatable = room.game.phase in ("pre_game", "playing") and room.game.SUPPORTS_SPECTATORS
            if not (joinable or spectatable):
                continue
            host = next((p.name for p in room.game.players if p.is_host), "Host")
            open_rooms.append(
                {
                    "room_code": room.room_code,
                    "game_type": room.game_type,
                    "title": room.game.TITLE,
                    "host": host,
                    "player_count": len(room.game.players),
                    "max_players": room.game.MAX_PLAYERS,
                    "phase": room.game.phase,
                    "spectatable": spectatable and not joinable,
                    "difficulty": room.game.get_difficulty(),
                }
            )
        open_rooms.sort(key=lambda r: (r["phase"] != "waiting", -r["player_count"]))
        return open_rooms

    async def send_lobby_state(self, client_id: str) -> None:
        session = self.clients.get(client_id)
        if not session:
            return
        await self._send_json(
            client_id,
            {
                "type": "LOBBY_STATE",
                "room_code": "",
                "game_type": "",
                "public_state": {
                    "open_rooms": self._open_public_rooms_payload(),
                    "games": self.get_catalog(),
                    "leaderboard": self.leaderboard.get_summary(limit_per_game=8),
                },
                "private_state": {
                    "client_id": session.client_id,
                    "player_name": session.name,
                    "session_secret": session.session_secret,
                },
                "players": [],
                "message": "",
            },
        )

    async def broadcast_lobby_state(self, exclude_id: str | None = None) -> None:
        for cid, session in list(self.clients.items()):
            if exclude_id and cid == exclude_id:
                continue
            if session.websocket is not None and session.room_code is None:
                await self.send_lobby_state(cid)

    def _is_active_room_recipient(self, room: Room, slot: PlayerSlot) -> bool:
        """Return True iff slot is a connected human still assigned to room."""
        if slot.is_bot or not slot.connected:
            return False
        sess = self.clients.get(slot.id)
        return sess is not None and sess.room_code == room.room_code

    async def _broadcast_to_room(
        self, room: Room, payload: dict[str, Any], exclude_id: str | None = None
    ) -> None:
        recipients = [
            p.id
            for p in room.game.players
            if self._is_active_room_recipient(room, p)
        ] + [
            s.id
            for s in room.game.spectators
            if self._is_active_room_recipient(room, s)
        ]
        for cid in recipients:
            if exclude_id and cid == exclude_id:
                continue
            await self._send_json(cid, payload)

    async def send_error(self, client_id: str, message: str) -> None:
        await self._send_error(client_id, message)

    async def _send_error(self, client_id: str, message: str) -> None:
        session = self.clients.get(client_id)
        room_code = session.room_code or "" if session else ""
        game_type = (
            self.rooms[room_code].game_type
            if room_code and room_code in self.rooms
            else ""
        )
        await self._send_json(
            client_id,
            {
                "type": "ERROR",
                "room_code": room_code,
                "game_type": game_type,
                "public_state": {},
                "private_state": {},
                "players": [],
                "message": message,
            },
        )

    async def _send_json(self, client_id: str, payload: dict[str, Any]) -> None:
        session = self.clients.get(client_id)
        if not session or session.websocket is None:
            return
        ws = session.websocket
        try:
            await ws.send_json(payload)
        except Exception:
            if session.websocket is ws and client_id not in self._disconnecting:
                await self.disconnect(client_id, websocket=ws)
