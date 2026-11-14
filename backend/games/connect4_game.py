"""Server-authoritative Connect 4 engine supporting all 4 game modes and AI bots.

Modes:
- Classic (7x6, 4-in-a-row wins)
- Pop Out (7x6, drop or pop active player's bottom disc, gravity shift, simultaneous double-win resolves to draw)
- 5-in-a-Row (9x7, 5-in-a-row wins; 4-in-a-row does NOT win)
- Blitz (7x6, strict 5s turn countdown timer integrated into _tick_timers)

AI Bots:
- Easy: random legal move selection
- Medium: immediate win taking, opponent win blocking, suicide move filtering, center column heuristic
- Hard: Tactical lookahead Minimax with alpha-beta pruning and streak evaluation
"""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot


class Connect4Game(BaseGame):
    GAME_TYPE = "connect4"
    TITLE = "Connect 4"
    CATEGORY = "Strategy"
    DESCRIPTION = (
        "Vertical disc drops with Classic (7x6), Pop Out mode, 5-in-a-Row (9x7), and Blitz Mode with 5s countdown timer."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 2
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    SUPPORTS_CUSTOM_DIFFICULTY = False
    IS_STUB = False

    DEFAULT_SETTINGS = {
        "difficulty": "mid",
        "mode": "classic",  # classic | pop_out | five_in_a_row | blitz
        "blitz_time": 5,
        "pass_and_play": False,
    }

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.mode: str = "classic"
        self.cols: int = 7
        self.rows: int = 6
        self.target_streak: int = 4
        self.board: list[list[str | None]] = [[None] * self.cols for _ in range(self.rows)]
        self.winning_cells: list[list[int]] = []
        self.winning_line: list[list[int]] = []
        self.last_move: dict[str, Any] | None = None
        self.move_count: int = 0
        self.turn_time_limit: float | None = None
        self.turn_started_at: float | None = None
        self._last_tick_time: float | None = None

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )

        raw_mode = str(self.settings.get("mode", "classic")).lower().strip()
        grid_size = str(self.settings.get("grid_size", "")).lower().strip()

        if raw_mode in ("five_in_a_row", "5_in_a_row", "5_row") or grid_size in ("9x7", "9*7"):
            self.mode = "five_in_a_row"
            self.cols = 9
            self.rows = 7
            self.target_streak = 5
        elif raw_mode in ("pop_out", "popout", "pop"):
            self.mode = "pop_out"
            self.cols = 7
            self.rows = 6
            self.target_streak = 4
        elif raw_mode in ("blitz", "speed"):
            self.mode = "blitz"
            self.cols = 7
            self.rows = 6
            self.target_streak = 4
        else:
            self.mode = "classic"
            self.cols = 7
            self.rows = 6
            self.target_streak = 4

        # Timer setup
        if self.mode == "blitz":
            raw_t = self.settings.get("timer") or self.settings.get("blitz_time") or 5.0
            self.turn_time_limit = float(raw_t)
        elif "timer" in self.settings or "blitz_time" in self.settings:
            self.turn_time_limit = float(self.settings.get("timer") or self.settings.get("blitz_time"))
        else:
            self.turn_time_limit = None

        self.board = [[None] * self.cols for _ in range(self.rows)]
        self.winning_cells = []
        self.winning_line = []
        self.last_move = None
        self.move_count = 0
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        now = time.time()
        self.started_at = now
        self.turn_started_at = now
        self._last_tick_time = None
        self.turn_player_id = self.players[0].id if self.players else None
        self.log_event(f"{self.TITLE} match started ({self.mode}).", kind="info")

    def _switch_turn(self) -> None:
        other = [p for p in self.players if p.id != self.turn_player_id]
        self.turn_player_id = other[0].id if other else None
        now = (
            self._last_tick_time
            if (self._last_tick_time is not None and self._last_tick_time > time.time())
            else time.time()
        )
        self.turn_started_at = now

    def _tick_timers(self, now: float) -> bool:
        self._last_tick_time = now
        if self.phase != "playing":
            return False
        if self.turn_time_limit is None or self.turn_started_at is None:
            return False

        elapsed = now - self.turn_started_at
        if elapsed >= self.turn_time_limit:
            timed_out_id = self.turn_player_id
            timed_out_player = self.get_player(timed_out_id) if timed_out_id else None
            pname = timed_out_player.name if timed_out_player else (timed_out_id or "Player")
            other = [p for p in self.players if p.id != timed_out_id]
            winner_id = other[0].id if other else (timed_out_id or "")
            winner = self.get_player(winner_id)
            wname = winner.name if winner else winner_id
            if winner:
                winner.score = 1
            self.finish_game(
                [winner_id],
                f"{pname} timed out in Blitz mode ({int(self.turn_time_limit)}s turn limit) — {wname} wins!",
            )
            return True
        return False

    def _check_player_win(self, player_id: str) -> tuple[bool, list[list[int]]]:
        """Checks if player_id has achieved target_streak in any orientation."""
        winning_points: list[list[int]] = []
        streak = self.target_streak

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != player_id:
                    continue
                for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
                    end_r = r + (streak - 1) * dr
                    end_c = c + (streak - 1) * dc
                    if 0 <= end_r < self.rows and 0 <= end_c < self.cols:
                        if all(self.board[r + i * dr][c + i * dc] == player_id for i in range(streak)):
                            for i in range(streak):
                                pt = [r + i * dr, c + i * dc]
                                if pt not in winning_points:
                                    winning_points.append(pt)

        return (len(winning_points) > 0, winning_points)

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        act = str(action).lower().strip()

        if act in ("resign", "forfeit"):
            self.forfeit_player(player_id, f"{player_id} resigned.")
            return True, ""

        if act in ("rematch", "restart", "play_again"):
            if self.phase == "finished":
                self.reset_for_rematch()
                return True, "Match reset for rematch."
            return False, "Match is still in progress."

        if self.phase != "playing":
            return False, "Game is not in playing phase."

        is_pass_and_play = bool(self.settings.get("pass_and_play"))
        if not is_pass_and_play and player_id != self.turn_player_id:
            return False, "Not your turn."

        effective_pid = self.turn_player_id if is_pass_and_play else player_id

        # Extract column
        col_val = data.get("col") if data.get("col") is not None else data.get("column")
        if col_val is None:
            return False, "Missing column index."
        try:
            col = int(col_val)
        except (ValueError, TypeError):
            return False, "Invalid column index: not an integer."

        if col < 0 or col >= self.cols:
            return False, f"Column {col} is out of bounds (0-{self.cols - 1})."

        if act in ("drop", "move", "play"):
            return self._handle_drop_action(effective_pid, col)
        elif act in ("pop", "pop_out"):
            return self._handle_pop_action(effective_pid, col)
        else:
            return False, f"Unknown action: {action}"

    def _handle_drop_action(self, player_id: str, col: int) -> tuple[bool, str]:
        if self.board[0][col] is not None:
            return False, f"Column {col} is full."

        target_row = max(r for r in range(self.rows) if self.board[r][col] is None)
        self.board[target_row][col] = player_id
        self.move_count += 1
        self.last_move = {
            "player_id": player_id,
            "action": "drop",
            "row": target_row,
            "col": col,
        }

        won, cells = self._check_player_win(player_id)
        if won:
            self.winning_cells = cells
            self.winning_line = list(cells)
            p = self.get_player(player_id)
            if p:
                p.score = 1
            self.finish_game(
                [player_id],
                f"{p.name if p else player_id} won with {self.target_streak}-in-a-row!",
            )
            return True, ""

        # Check full board draw
        if all(self.board[0][c] is not None for c in range(self.cols)):
            self.winning_cells = []
            self.winning_line = []
            self.finish_game([], "Match ended in a draw — board is full.")
            return True, ""

        self._switch_turn()
        return True, ""

    def _handle_pop_action(self, player_id: str, col: int) -> tuple[bool, str]:
        if self.mode != "pop_out":
            return False, "Pop-out action is only allowed in Pop Out mode."

        bottom_row = self.rows - 1
        bottom_disc = self.board[bottom_row][col]
        if bottom_disc is None:
            return False, f"Column {col} is empty."
        if bottom_disc != player_id:
            return False, "Cannot pop opponent's disc."

        # Gravity shift
        for r in range(bottom_row, 0, -1):
            self.board[r][col] = self.board[r - 1][col]
        self.board[0][col] = None

        self.move_count += 1
        self.last_move = {
            "player_id": player_id,
            "action": "pop",
            "row": bottom_row,
            "col": col,
        }

        # Check wins for all players
        winners = []
        all_cells = []
        for p in self.players:
            won, cells = self._check_player_win(p.id)
            if won:
                winners.append(p.id)
                for pt in cells:
                    if pt not in all_cells:
                        all_cells.append(pt)

        if len(winners) > 1:
            self.winning_cells = all_cells
            self.winning_line = list(all_cells)
            self.finish_game([], "Simultaneous double-win tie in Pop Out mode!")
            return True, ""
        elif len(winners) == 1:
            w_id = winners[0]
            self.winning_cells = all_cells
            self.winning_line = list(all_cells)
            winner = self.get_player(w_id)
            if winner:
                winner.score = 1
            self.finish_game(
                [w_id],
                f"{winner.name if winner else w_id} won with {self.target_streak}-in-a-row!",
            )
            return True, ""
        else:
            self._switch_turn()
            return True, ""

    def get_public_state(self) -> dict[str, Any]:
        time_remaining = None
        if self.turn_time_limit is not None and self.turn_started_at is not None:
            now = self._last_tick_time if self._last_tick_time is not None else time.time()
            time_remaining = max(0.0, self.turn_time_limit - (now - self.turn_started_at))

        return {
            "phase": self.phase,
            "mode": self.mode,
            "rows": self.rows,
            "cols": self.cols,
            "board": self.board,
            "turn_player_id": self.turn_player_id,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
            "target_streak": self.target_streak,
            "winning_cells": self.winning_cells,
            "winning_line": self.winning_line,
            "last_move": self.last_move,
            "move_count": self.move_count,
            "turn_time_limit": self.turn_time_limit,
            "turn_started_at": self.turn_started_at,
            "time_remaining": time_remaining,
            "difficulty": self.get_difficulty(),
            "pass_and_play": bool(self.settings.get("pass_and_play")),
        }

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        if self.phase not in ("pre_game", "playing"):
            return False
        remaining = [p for p in self.players if p.id != player_id]
        winner_id = remaining[0].id if remaining else player_id
        winner = self.get_player(winner_id)
        if winner:
            winner.score = 1
        msg = reason or f"{player_id} forfeited."
        self.finish_game([winner_id], msg)
        return True

    def reset_for_rematch(self) -> None:
        """Resets the game state for a new round while preserving player slots and scores."""
        self.start_game()

    # -------------------------------------------------------------------------
    # AI Bot Implementation
    # -------------------------------------------------------------------------

    def get_active_bot_ids(self) -> list[str]:
        return [p.id for p in self.players if p.is_bot]

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or bot_id != self.turn_player_id:
            return None

        legal_drops = [c for c in range(self.cols) if self.board[0][c] is None]
        legal_pops = (
            [c for c in range(self.cols) if self.board[self.rows - 1][c] == bot_id]
            if self.mode == "pop_out"
            else []
        )

        if not legal_drops and not legal_pops:
            return None

        other = [p for p in self.players if p.id != bot_id]
        opp_id = other[0].id if other else None
        diff = self.get_difficulty()

        if diff == "easy":
            # Random choice preferring drops
            if legal_drops and (not legal_pops or random.random() < 0.85):
                c = random.choice(legal_drops)
                return "drop", {"col": c, "column": c}
            elif legal_pops:
                c = random.choice(legal_pops)
                return "pop", {"col": c, "column": c}
            elif legal_drops:
                c = random.choice(legal_drops)
                return "drop", {"col": c, "column": c}
            return None

        # 1. Immediate winning drop
        for c in legal_drops:
            r = max(row for row in range(self.rows) if self.board[row][c] is None)
            self.board[r][c] = bot_id
            won, _ = self._check_player_win(bot_id)
            self.board[r][c] = None
            if won:
                return "drop", {"col": c, "column": c}

        # 2. Immediate winning pop (in pop_out mode)
        if self.mode == "pop_out":
            bottom_row = self.rows - 1
            for c in legal_pops:
                col_copy = [self.board[r][c] for r in range(self.rows)]
                for r in range(bottom_row, 0, -1):
                    self.board[r][c] = self.board[r - 1][c]
                self.board[0][c] = None
                bot_won, _ = self._check_player_win(bot_id)
                opp_won = self._check_player_win(opp_id)[0] if opp_id else False
                for r in range(self.rows):
                    self.board[r][c] = col_copy[r]
                if bot_won and not opp_won:
                    return "pop", {"col": c, "column": c}

        # 3. Block opponent immediate winning drop
        if opp_id:
            for c in legal_drops:
                r = max(row for row in range(self.rows) if self.board[row][c] is None)
                self.board[r][c] = opp_id
                opp_won, _ = self._check_player_win(opp_id)
                self.board[r][c] = None
                if opp_won:
                    return "drop", {"col": c, "column": c}

        # 4. Hard Minimax Search for classic / 5-in-a-row / blitz
        if diff == "hard" and self.mode != "pop_out" and legal_drops:
            best_col = self._minimax_best_col(bot_id, opp_id, depth=3)
            if best_col is not None and best_col in legal_drops:
                return "drop", {"col": best_col, "column": best_col}

        # 5. Medium Heuristic: Filter suicide moves (don't give opponent winning drop directly above)
        safe_drops = []
        for c in legal_drops:
            r = max(row for row in range(self.rows) if self.board[row][c] is None)
            if r > 0 and opp_id:
                self.board[r][c] = bot_id
                self.board[r - 1][c] = opp_id
                opp_wins, _ = self._check_player_win(opp_id)
                self.board[r - 1][c] = None
                self.board[r][c] = None
                if not opp_wins:
                    safe_drops.append(c)
            else:
                safe_drops.append(c)

        candidate_drops = safe_drops if safe_drops else legal_drops
        # Sort candidates closest to center column
        center = self.cols // 2
        candidate_drops.sort(key=lambda col: abs(col - center))
        chosen = candidate_drops[0]
        return "drop", {"col": chosen, "column": chosen}

    def _minimax_best_col(self, bot_id: str, opp_id: str | None, depth: int) -> int | None:
        """Minimax with alpha-beta pruning returning the optimal column."""
        legal_drops = [c for c in range(self.cols) if self.board[0][c] is None]
        if not legal_drops:
            return None

        center = self.cols // 2
        legal_drops.sort(key=lambda col: abs(col - center))

        best_score = -float("inf")
        best_col = legal_drops[0]
        alpha = -float("inf")
        beta = float("inf")

        for c in legal_drops:
            r = max(row for row in range(self.rows) if self.board[row][c] is None)
            self.board[r][c] = bot_id
            won, _ = self._check_player_win(bot_id)
            if won:
                self.board[r][c] = None
                return c

            score = self._minimax_eval(depth - 1, False, bot_id, opp_id, alpha, beta)
            self.board[r][c] = None

            if score > best_score:
                best_score = score
                best_col = c
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_col

    def _minimax_eval(
        self,
        depth: int,
        is_max: bool,
        bot_id: str,
        opp_id: str | None,
        alpha: float,
        beta: float,
    ) -> float:
        if opp_id is None:
            return 0.0

        bot_won, _ = self._check_player_win(bot_id)
        if bot_won:
            return 10000.0 + depth

        opp_won, _ = self._check_player_win(opp_id)
        if opp_won:
            return -10000.0 - depth

        legal_drops = [c for c in range(self.cols) if self.board[0][c] is None]
        if not legal_drops or depth <= 0:
            return self._heuristic_board_score(bot_id, opp_id)

        center = self.cols // 2
        legal_drops.sort(key=lambda col: abs(col - center))

        if is_max:
            max_eval = -float("inf")
            for c in legal_drops:
                r = max(row for row in range(self.rows) if self.board[row][c] is None)
                self.board[r][c] = bot_id
                eval_score = self._minimax_eval(depth - 1, False, bot_id, opp_id, alpha, beta)
                self.board[r][c] = None
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for c in legal_drops:
                r = max(row for row in range(self.rows) if self.board[row][c] is None)
                self.board[r][c] = opp_id
                eval_score = self._minimax_eval(depth - 1, True, bot_id, opp_id, alpha, beta)
                self.board[r][c] = None
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _heuristic_board_score(self, bot_id: str, opp_id: str) -> float:
        score = 0.0
        center = self.cols // 2
        # Center column control bonus
        for r in range(self.rows):
            if self.board[r][center] == bot_id:
                score += 3.0
            elif self.board[r][center] == opp_id:
                score -= 3.0

        streak = self.target_streak
        # Sample horizontal windows
        for r in range(self.rows):
            for c in range(self.cols - streak + 1):
                window = [self.board[r][c + i] for i in range(streak)]
                score += self._eval_window(window, bot_id, opp_id)

        # Sample vertical windows
        for c in range(self.cols):
            for r in range(self.rows - streak + 1):
                window = [self.board[r + i][c] for i in range(streak)]
                score += self._eval_window(window, bot_id, opp_id)

        # Sample positive diagonal
        for r in range(self.rows - streak + 1):
            for c in range(self.cols - streak + 1):
                window = [self.board[r + i][c + i] for i in range(streak)]
                score += self._eval_window(window, bot_id, opp_id)

        # Sample negative diagonal
        for r in range(streak - 1, self.rows):
            for c in range(self.cols - streak + 1):
                window = [self.board[r - i][c + i] for i in range(streak)]
                score += self._eval_window(window, bot_id, opp_id)

        return score

    def _eval_window(self, window: list[str | None], bot_id: str, opp_id: str) -> float:
        b_cnt = window.count(bot_id)
        o_cnt = window.count(opp_id)
        n_cnt = window.count(None)

        if b_cnt > 0 and o_cnt > 0:
            return 0.0

        if b_cnt > 0:
            if b_cnt == self.target_streak:
                return 1000.0
            elif b_cnt == self.target_streak - 1:
                return 50.0
            elif b_cnt == self.target_streak - 2:
                return 10.0

        if o_cnt > 0:
            if o_cnt == self.target_streak:
                return -1000.0
            elif o_cnt == self.target_streak - 1:
                return -60.0
            elif o_cnt == self.target_streak - 2:
                return -12.0

        return 0.0
