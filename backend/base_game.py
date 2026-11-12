"""Abstract base game contract and shared player/event state utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time
from typing import Any

DIFFICULTY_LEVELS: tuple[str, ...] = ("easy", "mid", "hard", "custom")

_DIFFICULTY_ALIASES: dict[str, str] = {
    "easy": "easy",
    "beginner": "easy",
    "mid": "mid",
    "medium": "mid",
    "intermediate": "mid",
    "normal": "mid",
    "hard": "hard",
    "expert": "hard",
    "custom": "custom",
    "custem": "custom",
    "manual": "custom",
}


def normalize_difficulty(
    value: Any, default: str = "mid", allow_custom: bool = True
) -> str:
    """Normalize difficulty presets and legacy aliases into 'easy' | 'mid' | 'hard' (or 'custom' if allowed)."""
    key = str(value or "").strip().lower()
    normalized = _DIFFICULTY_ALIASES.get(key, default)
    if normalized == "custom" and not allow_custom:
        return default
    return normalized


@dataclass
class PlayerSlot:
    """Represents a human or AI participant (or spectator) in a game room."""

    id: str
    name: str
    is_bot: bool = False
    is_host: bool = False
    connected: bool = True
    score: int = 0
    seat: int = 0
    role: str = "player"  # "player" | "spectator"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "is_host": self.is_host,
            "connected": self.connected,
            "is_bot": self.is_bot,
            "seat": self.seat,
            "role": self.role,
        }


class BaseGame(ABC):
    """Abstract base class enforced across all 11 server-authoritative engines."""

    GAME_TYPE: str = ""
    TITLE: str = ""
    CATEGORY: str = ""
    DESCRIPTION: str = ""
    MIN_PLAYERS: int = 1
    MAX_PLAYERS: int = 4
    SUPPORTS_SOLO: bool = False
    SUPPORTS_BOTS: bool = False
    SUPPORTS_SPECTATORS: bool = False
    SUPPORTS_CUSTOM_DIFFICULTY: bool = False
    DEFAULT_SETTINGS: dict[str, Any] = {"difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        self.room_code: str = room_code
        self.players: list[PlayerSlot] = list(players or [])
        self.spectators: list[PlayerSlot] = []
        merged = {**self.DEFAULT_SETTINGS, **(settings or {})}
        merged["difficulty"] = self.normalize_difficulty(merged.get("difficulty", "mid"))
        self.settings: dict[str, Any] = merged
        self.phase: str = "waiting"  # waiting | pre_game | playing | finished
        self.turn_player_id: str | None = None
        self.winner_ids: list[str] = []
        self.win_reason: str = ""
        self.events: list[dict[str, Any]] = []
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self.bot_delay: float = 0.70
        self._last_bot_tick: float = 0.0

    def normalize_difficulty(self, value: Any, default: str = "mid") -> str:
        """Normalize difficulty for this engine, clamping unsupported 'custom' to default."""
        return normalize_difficulty(
            value, default=default, allow_custom=self.SUPPORTS_CUSTOM_DIFFICULTY
        )

    def get_difficulty(self) -> str:
        """Return normalized match difficulty ('easy' | 'mid' | 'hard', or 'custom' if supported)."""
        return self.normalize_difficulty(self.settings.get("difficulty", "mid"))

    def log_event(self, text: str, kind: str = "info") -> None:
        """Append a bounded event entry to the room's live event feed."""
        self.events.append(
            {
                "text": text,
                "kind": kind,
                "ts": round(time.time(), 2),
            }
        )
        if len(self.events) > 60:
            self.events = self.events[-60:]

    def get_player(self, player_id: str) -> PlayerSlot | None:
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def player_ids(self) -> list[str]:
        return [p.id for p in self.players]

    def reset_for_rematch(self) -> None:
        """Restore common turn/phase fields before re-starting a match."""
        self.phase = "waiting"
        self.turn_player_id = None
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = None
        self.finished_at = None
        for p in self.players:
            p.score = 0

    def finish_game(self, winner_ids: list[str], reason: str) -> None:
        """Mark the match as finished and log the authoritative result."""
        if self.phase == "finished":
            return
        self.phase = "finished"
        self.winner_ids = list(winner_ids)
        self.win_reason = reason
        self.finished_at = time.time()
        self.turn_player_id = None
        self.log_event(reason, kind="finish")

    def on_player_disconnect(self, player_id: str) -> bool:
        """Hook called when a human player disconnects; return True if state changed."""
        player = self.get_player(player_id)
        if player is None:
            return False
        player.connected = False
        self.log_event(f"{player.name} disconnected.", kind="warn")
        return True

    def on_player_reconnect(self, player_id: str) -> None:
        player = self.get_player(player_id)
        if player is not None:
            player.connected = True
            self.log_event(f"{player.name} reconnected.", kind="info")

    def on_bot_takeover(self, player_id: str) -> None:
        """Optional hook called when an AI bot takes over a disconnected/left player slot."""
        return None

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        """Optional hook for 2P duel forfeit on explicit leave or disconnect timeout."""
        return False

    def can_start(self) -> tuple[bool, str]:
        count = len(self.players)
        if count < self.MIN_PLAYERS:
            return False, f"Need at least {self.MIN_PLAYERS} player(s) to launch."
        if count > self.MAX_PLAYERS:
            return False, f"Maximum {self.MAX_PLAYERS} players allowed."
        return True, ""

    @abstractmethod
    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        """Initialize the game board, decks, clocks, and initial turn state."""

    @abstractmethod
    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate and apply an action from player_id. Returns (ok, error_msg)."""

    @abstractmethod
    def get_public_state(self) -> dict[str, Any]:
        """Return public shared state safe to broadcast to all room members."""

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        """Return player-specific hidden data (hands, unrevealed mines, etc.)."""
        return {}

    def _tick_timers(self, now: float) -> bool:
        """Override in timer-driven games; return True if public/private state changed."""
        return False

    def get_active_bot_ids(self) -> list[str]:
        """Return bot IDs eligible to act right now (turn-based by default)."""
        if not self.turn_player_id:
            return []
        player = self.get_player(self.turn_player_id)
        if player and player.is_bot:
            return [player.id]
        return []

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        """Override in bot-capable games to return (action, data) for bot_id."""
        return None

    def tick(self, now: float | None = None) -> bool:
        """Advance timers and step at most one AI bot decision per cadence interval."""
        ts = time.time() if now is None else now
        changed = False
        if self.phase in ("pre_game", "playing"):
            if self._tick_timers(ts):
                changed = True

        if self.phase in ("pre_game", "playing") and ts - self._last_bot_tick >= self.bot_delay:
            bot_ids = self.get_active_bot_ids()
            for bot_id in bot_ids:
                bot_cmd = self.get_bot_action(bot_id)
                if bot_cmd is not None:
                    action, data = bot_cmd
                    ok, _ = self.handle_action(bot_id, action, data)
                    if ok:
                        self._last_bot_tick = ts
                        changed = True
                        break
        return changed

    def get_leaderboard_entries(self) -> list[dict[str, Any]]:
        """Return human player result rows for persistent leaderboard tracking."""
        if self.phase != "finished":
            return []
        winner_set = set(self.winner_ids)
        return [
            {
                "name": p.name,
                "score": p.score,
                "won": p.id in winner_set,
                "game_type": self.GAME_TYPE,
            }
            for p in self.players
            if not p.is_bot
        ]

