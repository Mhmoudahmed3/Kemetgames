"""Solo Classic & Multiplayer Score-Race Snake engine."""

from __future__ import annotations

import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

SNAKE_PACE: dict[str, tuple[int, int]] = {
    "easy": (165, 10),
    "mid": (125, 10),
    "hard": (85, 15),
}


class SnakeGame(BaseGame):
    GAME_TYPE = "snake"
    TITLE = "SNAKE"
    CATEGORY = "Arcade"
    DESCRIPTION = (
        "The timeless arcade classic of our youth. Slither across the retro grid, hunt down food to grow longer, and master split-second reflex turns without biting your own tail."
    )
    MIN_PLAYERS = 1
    MAX_PLAYERS = 8
    SUPPORTS_SOLO = True
    SUPPORTS_BOTS = False
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"duration": 90, "difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.snakes: dict[str, dict[str, Any]] = {}
        self.duration: int = 90
        self.difficulty: str = "mid"
        self.step_ms: int = 125
        self.points_per_food: int = 10
        self.is_solo: bool = False
        self._last_tick_sec: int = -1

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        raw_dur = self.settings.get("duration", 90)
        if isinstance(raw_dur, bool) or raw_dur is None:
            parsed_dur = 90
        else:
            try:
                parsed_dur = int(raw_dur)
            except (TypeError, ValueError):
                parsed_dur = 90
        self.duration = max(15, min(600, parsed_dur))
        self.settings["duration"] = self.duration
        self.difficulty = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = self.difficulty
        self.step_ms, self.points_per_food = SNAKE_PACE[self.difficulty]
        self.is_solo = len(self.players) == 1
        self._last_tick_sec = -1
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        self.snakes = {}
        for p in self.players:
            p.score = 0
            self.snakes[p.id] = {
                "score": 0,
                "length": 3,
                "alive": True,
                "last_sync": self.started_at,
                "died_at": None,
            }
        mode = "Solo Classic" if self.is_solo else f"{self.duration}s Multiplayer Score Race"
        self.log_event(f"Snake started ({mode}, {self.difficulty.upper()} pace).")

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        state = self.snakes.get(player_id)
        if not state:
            return False, "Unknown player."
        if action != "sync":
            return False, f"Unsupported action: {action}"
        if not state["alive"]:
            return False, "Your snake has already crashed."

        raw_score = data.get("score", state["score"])
        raw_len = data.get("length", state["length"])
        if isinstance(raw_score, bool) or isinstance(raw_len, bool):
            return False, "Invalid snake telemetry."
        try:
            new_score = max(0, int(raw_score))
            new_len = max(3, int(raw_len))
        except (TypeError, ValueError):
            return False, "Invalid snake telemetry."

        now = time.time()
        alive = bool(data.get("alive", True))

        # Server-side sanity bound against forged score/length jumps using elapsed match time
        elapsed = max(0.0, now - (self.started_at or now))
        max_foods = int(elapsed * (1000.0 / self.step_ms) * 0.65) + 6
        max_score = max_foods * self.points_per_food
        max_len = 3 + max_foods

        new_score = max(state["score"], min(new_score, max_score))
        len_cap = min(max_len, 3 + (new_score // max(1, self.points_per_food)) + 2)
        new_len = max(state["length"], min(new_len, len_cap))

        state["score"] = new_score
        state["length"] = new_len
        state["last_sync"] = now

        player = self.get_player(player_id)
        if player:
            player.score = new_score

        if state["alive"] and not alive:
            state["alive"] = False
            state["died_at"] = now
            if player:
                self.log_event(f"{player.name} crashed at {new_score} pts.", kind="warn")

        self._check_race_end(now)
        return True, ""

    def on_player_disconnect(self, player_id: str) -> bool:
        changed = super().on_player_disconnect(player_id)
        if changed and self.phase == "playing" and player_id in self.snakes:
            if self.snakes[player_id]["alive"]:
                self.snakes[player_id]["alive"] = False
                self.snakes[player_id]["died_at"] = time.time()
            self._check_race_end(time.time())
        return changed

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing" or self.started_at is None:
            return False
        if self.is_solo:
            return False
        if now - self.started_at >= self.duration:
            self._check_race_end(now, force_timeout=True)
            return True
        sec = int(max(0.0, self.duration - (now - self.started_at)))
        if self._last_tick_sec != sec:
            self._last_tick_sec = sec
            return True
        return False

    def _check_race_end(self, now: float, force_timeout: bool = False) -> None:
        if self.phase != "playing":
            return

        if self.is_solo:
            p = self.players[0]
            if not self.snakes[p.id]["alive"]:
                if p.score > 0:
                    self.finish_game([p.id], f"{p.name} finished with {p.score} points.")
                else:
                    self.finish_game([], f"{p.name} crashed with 0 points.")
            return

        alive_ids = [pid for pid, s in self.snakes.items() if s["alive"]]
        timed_out = force_timeout or (
            self.started_at is not None and (now - self.started_at >= self.duration)
        )

        if len(alive_ids) == 1 and len(self.players) >= 2:
            winner_id = alive_ids[0]
            winner = self.get_player(winner_id)
            name = winner.name if winner else winner_id
            self.finish_game([winner_id], f"{name} is the last snake alive!")
            return

        if len(alive_ids) == 0 or timed_out:
            ranked = sorted(
                self.players,
                key=lambda p: (
                    1 if self.snakes[p.id]["alive"] else 0,
                    self.snakes[p.id]["score"],
                    self.snakes[p.id]["length"],
                ),
                reverse=True,
            )
            top = ranked[0]
            top_score = self.snakes[top.id]["score"]
            if not alive_ids and top_score <= 0:
                self.finish_game([], "All snakes crashed with 0 points.")
                return
            winners = [
                p.id
                for p in ranked
                if self.snakes[p.id]["score"] == top_score
                and self.snakes[p.id]["alive"] == self.snakes[top.id]["alive"]
            ]
            names = ", ".join(self.get_player(w).name for w in winners if self.get_player(w))
            prefix = "Time expired!" if timed_out else "All snakes crashed!"
            self.finish_game(winners, f"{prefix} Winner: {names} ({top_score} pts).")

    def get_public_state(self) -> dict[str, Any]:
        remaining = 0.0
        if not self.is_solo and self.started_at is not None and self.phase == "playing":
            remaining = max(0.0, self.duration - (time.time() - self.started_at))
        return {
            "phase": self.phase,
            "is_solo": self.is_solo,
            "duration": self.duration,
            "difficulty": self.difficulty,
            "step_ms": self.step_ms,
            "points_per_food": self.points_per_food,
            "time_remaining": round(remaining, 1),
            "snakes": {
                pid: {
                    "score": st["score"],
                    "length": st["length"],
                    "alive": st["alive"],
                }
                for pid, st in self.snakes.items()
            },
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }
