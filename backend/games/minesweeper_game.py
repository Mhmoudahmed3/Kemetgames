"""Seeded Minesweeper board generator and time-attack race engine."""

from __future__ import annotations

from collections import deque
import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

DIFFICULTIES: dict[str, tuple[int, int, int]] = {
    "easy": (9, 9, 10),
    "mid": (16, 16, 40),
    "hard": (16, 30, 99),
    "beginner": (9, 9, 10),
    "intermediate": (16, 16, 40),
    "expert": (16, 30, 99),
    "custom": (16, 16, 40),
}


class MinesweeperGame(BaseGame):
    GAME_TYPE = "minesweeper"
    TITLE = "MINEFIELD SWEEP"
    CATEGORY = "Arcade"
    DESCRIPTION = (
        "Seeded Minesweeper time-attack. First click guarantees a zero-mine clearing. Supports chording and live progress."
    )
    MIN_PLAYERS = 1
    MAX_PLAYERS = 8
    SUPPORTS_SOLO = True
    SUPPORTS_BOTS = False
    SUPPORTS_SPECTATORS = False
    SUPPORTS_CUSTOM_DIFFICULTY = True
    DEFAULT_SETTINGS = {"difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.difficulty: str = "mid"
        self.rows: int = 16
        self.cols: int = 16
        self.total_mines: int = 40
        self.seed: int = 0
        self.boards: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _safe_int(val: Any, default: int) -> int:
        if val is None or isinstance(val, bool):
            return default
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        custom_keys = ("rows", "cols", "mines", "width", "height", "booms")
        if settings:
            if "difficulty" in settings:
                req_diff = self.normalize_difficulty(settings["difficulty"])
                if req_diff != "custom" and not any(k in settings for k in custom_keys):
                    for k in custom_keys:
                        self.settings.pop(k, None)
            self.settings.update(settings)

        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        has_manual = any(k in self.settings for k in custom_keys)

        if diff == "custom" or has_manual:
            raw_r = self.settings["rows"] if "rows" in self.settings else self.settings.get("height")
            raw_c = self.settings["cols"] if "cols" in self.settings else self.settings.get("width")
            raw_m = self.settings["mines"] if "mines" in self.settings else self.settings.get("booms")
            r = max(8, min(30, self._safe_int(raw_r, 16)))
            c = max(8, min(36, self._safe_int(raw_c, 16)))
            max_mines = (r * c) - 9  # guarantees a 3x3 first-click safe area
            m = max(1, min(max_mines, self._safe_int(raw_m, 40)))
            self.rows = r
            self.cols = c
            self.total_mines = m
            self.difficulty = "custom"
            self.settings["difficulty"] = "custom"
            self.settings["rows"] = r
            self.settings["cols"] = c
            self.settings["mines"] = m
        else:
            self.difficulty = diff
            self.settings["difficulty"] = diff
            self.rows, self.cols, self.total_mines = DIFFICULTIES[diff]
        self.seed = random.randint(100_000, 999_999)
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        self.boards = {}
        total_safe = self.rows * self.cols - self.total_mines

        for p in self.players:
            p.score = 0
            self.boards[p.id] = {
                "generated": False,
                "mines": set(),
                "numbers": {},
                "revealed": {},  # (r, c) -> int
                "flagged": set(),
                "status": "playing",  # playing | cleared | exploded
                "finished_at": None,
                "total_safe": total_safe,
            }
        self.log_event(
            f"Minesweeper started ({diff.title()}: {self.cols}x{self.rows}, {self.total_mines} mines)."
        )

    def _neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    out.append((nr, nc))
        return out

    def _generate_mines_for_player(
        self, player_id: str, safe_r: int, safe_c: int
    ) -> None:
        board = self.boards[player_id]
        excluded = {(safe_r, safe_c), *self._neighbors(safe_r, safe_c)}
        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in excluded
        ]
        rng = random.Random(f"{self.seed}:{player_id}")
        mines = set(rng.sample(candidates, min(self.total_mines, len(candidates))))
        numbers: dict[tuple[int, int], int] = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in mines:
                    numbers[(r, c)] = sum(
                        1 for n in self._neighbors(r, c) if n in mines
                    )
        board["mines"] = mines
        board["numbers"] = numbers
        board["generated"] = True

    def _flood_reveal(self, board: dict[str, Any], start_r: int, start_c: int) -> None:
        queue = deque([(start_r, start_c)])
        visited = set(board["revealed"].keys())
        while queue:
            r, c = queue.popleft()
            if (r, c) in visited or (r, c) in board["flagged"]:
                continue
            if (r, c) in board["mines"]:
                continue
            visited.add((r, c))
            num = board["numbers"][(r, c)]
            board["revealed"][(r, c)] = num
            if num == 0:
                for nr, nc in self._neighbors(r, c):
                    if (nr, nc) not in visited and (nr, nc) not in board["flagged"]:
                        queue.append((nr, nc))

    def _reveal_cell(self, player_id: str, r: int, c: int) -> None:
        board = self.boards[player_id]
        if (r, c) in board["flagged"] or (r, c) in board["revealed"]:
            return
        if not board["generated"]:
            self._generate_mines_for_player(player_id, r, c)

        if (r, c) in board["mines"]:
            board["status"] = "exploded"
            board["finished_at"] = time.time()
            player = self.get_player(player_id)
            if player:
                self.log_event(f"{player.name} detonated a mine!", kind="warn")
            return

        self._flood_reveal(board, r, c)
        revealed_count = len(board["revealed"])
        total_safe = board["total_safe"]
        player = self.get_player(player_id)
        if player:
            player.score = int((revealed_count / max(1, total_safe)) * 1000)

        if revealed_count >= total_safe:
            board["status"] = "cleared"
            board["finished_at"] = time.time()
            if player:
                elapsed = max(0.1, board["finished_at"] - (self.started_at or board["finished_at"]))
                player.score = 1000 + max(0, int(1000 - elapsed * 4))
                self.log_event(
                    f"{player.name} cleared the minefield in {elapsed:.1f}s!", kind="finish"
                )

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        board = self.boards.get(player_id)
        if not board:
            return False, "Unknown player."
        if board["status"] != "playing":
            return False, "Your board is already finished."

        try:
            raw_r = data.get("r", -1)
            raw_c = data.get("c", -1)
            if isinstance(raw_r, bool) or isinstance(raw_c, bool):
                return False, "Invalid cell coordinates."
            r = int(raw_r)
            c = int(raw_c)
        except (TypeError, ValueError):
            return False, "Invalid cell coordinates."

        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False, "Coordinates out of bounds."

        if action == "reveal":
            self._reveal_cell(player_id, r, c)
        elif action == "flag":
            if (r, c) in board["revealed"]:
                return False, "Cannot flag an already revealed cell."
            if (r, c) in board["flagged"]:
                board["flagged"].remove((r, c))
            else:
                board["flagged"].add((r, c))
        elif action == "chord":
            if (r, c) not in board["revealed"]:
                return False, "Can only chord a revealed number."
            val = board["revealed"][(r, c)]
            if val <= 0:
                return False, "Empty cell cannot be chorded."
            neighbors = self._neighbors(r, c)
            flag_count = sum(1 for n in neighbors if n in board["flagged"])
            if flag_count != val:
                return False, "Adjacent flags do not match cell number."
            for nr, nc in neighbors:
                if (nr, nc) not in board["flagged"] and (nr, nc) not in board["revealed"]:
                    if board["status"] == "playing":
                        self._reveal_cell(player_id, nr, nc)
        else:
            return False, f"Unknown action: {action}"

        self._check_match_end()
        return True, ""

    def on_player_disconnect(self, player_id: str) -> bool:
        changed = super().on_player_disconnect(player_id)
        if changed and self.phase == "playing":
            self._check_match_end()
        return changed

    def _check_match_end(self) -> None:
        cleared = [pid for pid, b in self.boards.items() if b["status"] == "cleared"]
        if cleared:
            winner = self.get_player(cleared[0])
            name = winner.name if winner else cleared[0]
            self.finish_game([cleared[0]], f"{name} swept every safe tile!")
            return

        still_playing = [
            p.id
            for p in self.players
            if p.connected and self.boards.get(p.id, {}).get("status") == "playing"
        ]
        if not still_playing:
            if len(self.players) == 1:
                p = self.players[0]
                self.finish_game([], f"{p.name} hit a mine.")
                return
            ranked = sorted(
                self.players,
                key=lambda p: len(self.boards[p.id]["revealed"]),
                reverse=True,
            )
            top_rev = len(self.boards[ranked[0].id]["revealed"])
            winners = (
                [p.id for p in ranked if len(self.boards[p.id]["revealed"]) == top_rev]
                if top_rev > 0
                else []
            )
            self.finish_game(
                winners,
                "All active players finished! Highest board progress takes the match.",
            )

    def get_public_state(self) -> dict[str, Any]:
        now = time.time()
        progress: dict[str, dict[str, Any]] = {}
        for pid, b in self.boards.items():
            total_safe = max(1, b["total_safe"])
            rev = len(b["revealed"])
            end_t = b["finished_at"] or now
            elapsed = max(0.0, end_t - (self.started_at or end_t))
            progress[pid] = {
                "progress_pct": round((rev / total_safe) * 100, 1),
                "revealed_count": rev,
                "total_safe": total_safe,
                "flags_used": len(b["flagged"]),
                "status": b["status"],
                "elapsed": round(elapsed, 1),
            }
        return {
            "phase": self.phase,
            "difficulty": self.difficulty,
            "rows": self.rows,
            "cols": self.cols,
            "total_mines": self.total_mines,
            "progress": progress,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        board = self.boards.get(player_id)
        if not board:
            return {}
        reveal_list = [
            [r, c, val] for (r, c), val in board["revealed"].items()
        ]
        flag_list = [[r, c] for (r, c) in board["flagged"]]
        # Strictly withhold mine positions until player has cleared or exploded!
        mines_list = (
            [[r, c] for (r, c) in board["mines"]]
            if board["status"] in ("exploded", "cleared")
            else []
        )
        return {
            "status": board["status"],
            "revealed": reveal_list,
            "flagged": flag_list,
            "mines": mines_list,
        }

