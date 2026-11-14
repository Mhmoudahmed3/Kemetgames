"""Server-authoritative Tic-Tac-Toe engine supporting all 5 game modes and AI bots.

Modes:
- Classic (3x3, 3-in-a-row wins)
- Misère (3x3, 3-in-a-row loses)
- Extended 4x4 (4x4, 4-in-a-row wins)
- Extended 5x5 (5x5, 4-in-a-row wins)
- Ultimate Tic-Tac-Toe (9 nested 3x3 boards with target sub-board routing and free placement fallback)

AI:
- Easy: random legal move selection
- Medium: immediate win taking, critical blocking, and positional heuristics
- Hard: Mathematically unbeatable Minimax (zero losses) for 3x3 Classic & Misère,
  plus deep tactical heuristics for Extended and Ultimate modes.
"""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot

# Winning 3-in-a-row lines on a 3x3 grid
LINES_3X3: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = [
    # Rows
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    # Columns
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    # Diagonals
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
]

MACRO_LINES_3X3: list[tuple[int, int, int]] = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def _check_3x3_board_winner(board: tuple[tuple[str | None, ...], ...]) -> tuple[str | None, list[tuple[int, int]] | None]:
    """Evaluates 3x3 grid for a winning line."""
    for line in LINES_3X3:
        p0 = board[line[0][0]][line[0][1]]
        if p0 and p0 == board[line[1][0]][line[1][1]] == board[line[2][0]][line[2][1]]:
            return p0, list(line)
    return None, None


def _minimax_eval_3x3(
    board: tuple[tuple[str | None, ...], ...],
    is_max: bool,
    my_mark: str,
    opp_mark: str,
    depth: int,
    is_misere: bool,
    memo: dict[tuple[tuple[tuple[str | None, ...], ...], bool], int],
) -> int:
    """Minimax recursive solver for 3x3 Classic and Misère with memoization."""
    key = (board, is_max)
    if key in memo:
        return memo[key]

    winner, _ = _check_3x3_board_winner(board)
    if winner is not None:
        if is_misere:
            # Misère rule: completing 3-in-a-row LOSES!
            if winner == my_mark:
                return depth - 10  # loss for me
            else:
                return 10 - depth  # win for me
        else:
            # Classic rule: completing 3-in-a-row WINS!
            if winner == my_mark:
                return 10 - depth  # win for me
            else:
                return depth - 10  # loss for me

    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]
    if not empty:
        return 0  # Draw

    if is_max:
        best = -999
        for r, c in empty:
            row_l = list(board[r])
            row_l[c] = my_mark
            next_b = list(board)
            next_b[r] = tuple(row_l)
            val = _minimax_eval_3x3(tuple(next_b), False, my_mark, opp_mark, depth + 1, is_misere, memo)
            if val > best:
                best = val
        memo[key] = best
        return best
    else:
        best = 999
        for r, c in empty:
            row_l = list(board[r])
            row_l[c] = opp_mark
            next_b = list(board)
            next_b[r] = tuple(row_l)
            val = _minimax_eval_3x3(tuple(next_b), True, my_mark, opp_mark, depth + 1, is_misere, memo)
            if val < best:
                best = val
        memo[key] = best
        return best


class TicTacToeGame(BaseGame):
    GAME_TYPE = "tic_tac_toe"
    TITLE = "Tic-Tac-Toe"
    CATEGORY = "Strategy"
    DESCRIPTION = (
        "Classic 3x3, Misère, Extended Grids (4x4 & 5x5), and Ultimate Tic-Tac-Toe with AI opponents."
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
        "mode": "classic",  # classic | misere | extended_4x4 | extended_5x5 | ultimate
        "grid_size": 3,
        "pass_and_play": False,
        "first_player": "x",
    }

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.mode: str = "classic"
        self.grid_size: int = 3
        self.target_streak: int = 3
        self.board: list[list[str | None]] = []
        self.move_count: int = 0
        self.winning_cells: list[list[int]] = []
        self.winning_line: list[list[int]] = []

        # Player mark associations
        self.player_symbols: dict[str, str] = {}
        self.symbol_players: dict[str, str] = {}

        # Ultimate mode structures
        self.subboards: list[list[list[str | None]]] = []
        self.macro_board: list[str | None] = [None] * 9
        self.active_subboard: int | None = None
        self.subboard_winning_cells: dict[int, list[list[int]]] = {}
        self.macro_winning_line: list[int] = []

        # Lines cache for grid modes
        self._winning_lines: list[list[tuple[int, int]]] = []

    def normalize_difficulty(self, diff: str) -> str:
        s = str(diff or "").strip().lower()
        if s in ("hard", "minimax", "expert", "heuristic"):
            return "hard"
        if s in ("easy", "casual", "beginner"):
            return "easy"
        return "mid"

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)

        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )

        raw_mode = str(self.settings.get("mode", "")).lower()
        grid_sz = self.settings.get("grid_size")
        if grid_sz is not None:
            try:
                grid_sz = int(grid_sz)
            except (ValueError, TypeError):
                grid_sz = None

        if raw_mode == "ultimate":
            self.mode = "ultimate"
            self.grid_size = 3
            self.target_streak = 3
        elif raw_mode == "misere":
            self.mode = "misere"
            self.grid_size = 3
            self.target_streak = 3
        elif raw_mode in ("4x4", "extended_4x4") or grid_sz == 4:
            self.mode = "extended_4x4"
            self.grid_size = 4
            self.target_streak = 4
        elif raw_mode in ("5x5", "extended_5x5") or grid_sz == 5:
            self.mode = "extended_5x5"
            self.grid_size = 5
            self.target_streak = 4
        elif raw_mode == "extended":
            if grid_sz == 5:
                self.mode = "extended_5x5"
                self.grid_size = 5
                self.target_streak = 4
            else:
                self.mode = "extended_4x4"
                self.grid_size = 4
                self.target_streak = 4
        else:
            self.mode = "classic"
            self.grid_size = 3
            self.target_streak = 3

        # Grid lines precomputation for grid modes
        if self.mode != "ultimate":
            self._winning_lines = self._generate_grid_lines(self.grid_size, self.target_streak)
            self.board = [[None] * self.grid_size for _ in range(self.grid_size)]
        else:
            self.subboards = [[[None] * 3 for _ in range(3)] for _ in range(9)]
            self.macro_board = [None] * 9
            self.active_subboard = None
            self.subboard_winning_cells = {}
            self.macro_winning_line = []
            self.board = []  # Keep public state clean

        self.move_count = 0
        self.winning_cells = []
        self.winning_line = []
        self.winner_ids = []
        self.win_reason = None
        self.phase = "playing"
        self.started_at = time.time()

        # Symbol & turn allocation
        fp = str(self.settings.get("first_player", "x")).lower()
        p1 = self.players[0] if len(self.players) > 0 else None
        p2 = self.players[1] if len(self.players) > 1 else None

        if p1 and p2:
            if fp == "o":
                self.player_symbols = {p1.id: "O", p2.id: "X"}
                self.symbol_players = {"O": p1.id, "X": p2.id}
                self.turn_player_id = p2.id  # X always moves first
            elif fp == "random":
                if random.random() < 0.5:
                    self.player_symbols = {p1.id: "X", p2.id: "O"}
                    self.symbol_players = {"X": p1.id, "O": p2.id}
                    self.turn_player_id = p1.id
                else:
                    self.player_symbols = {p1.id: "O", p2.id: "X"}
                    self.symbol_players = {"O": p1.id, "X": p2.id}
                    self.turn_player_id = p2.id
            else:
                self.player_symbols = {p1.id: "X", p2.id: "O"}
                self.symbol_players = {"X": p1.id, "O": p2.id}
                self.turn_player_id = p1.id
        elif p1:
            self.player_symbols = {p1.id: "X"}
            self.symbol_players = {"X": p1.id}
            self.turn_player_id = p1.id

        self.log_event(
            f"{self.TITLE} match started ({self.mode}, difficulty: {self.settings['difficulty']}).",
            kind="info",
        )

    def _generate_grid_lines(self, size: int, streak: int) -> list[list[tuple[int, int]]]:
        """Precomputes all winning straight lines of length `streak` on a `size x size` grid."""
        lines: list[list[tuple[int, int]]] = []

        # Horizontal
        for r in range(size):
            for c in range(size - streak + 1):
                lines.append([(r, c + i) for i in range(streak)])

        # Vertical
        for c in range(size):
            for r in range(size - streak + 1):
                lines.append([(r + i, c) for i in range(streak)])

        # Main diagonals (down-right)
        for r in range(size - streak + 1):
            for c in range(size - streak + 1):
                lines.append([(r + i, c + i) for i in range(streak)])

        # Anti-diagonals (down-left)
        for r in range(size - streak + 1):
            for c in range(streak - 1, size):
                lines.append([(r + i, c - i) for i in range(streak)])

        return lines

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        act = action.lower()
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

        if act not in ("place_mark", "place", "move", "mark", "play"):
            return False, f"Unknown action: {action}"

        # Turn validation (pass_and_play allows sequential local moves)
        is_pass_and_play = bool(self.settings.get("pass_and_play"))
        if not is_pass_and_play and player_id != self.turn_player_id:
            return False, "Not your turn."

        effective_pid = self.turn_player_id if is_pass_and_play else player_id
        mark = self.player_symbols.get(effective_pid, "X")

        if self.mode == "ultimate":
            return self._handle_ultimate_move(effective_pid, mark, data)
        else:
            return self._handle_grid_move(effective_pid, mark, data)

    def _extract_grid_coords(self, data: dict[str, Any], size: int) -> tuple[int | None, int | None]:
        r = data.get("row", data.get("r"))
        c = data.get("col", data.get("c"))
        if r is None or c is None:
            cell = data.get("cell", data.get("index"))
            if cell is not None:
                try:
                    c_int = int(cell)
                    r = c_int // size
                    c = c_int % size
                except (ValueError, TypeError):
                    pass
        try:
            return (int(r), int(c)) if (r is not None and c is not None) else (None, None)
        except (ValueError, TypeError):
            return None, None

    def _handle_grid_move(
        self, player_id: str, mark: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        r, c = self._extract_grid_coords(data, self.grid_size)
        if r is None or c is None:
            return False, "Missing or invalid grid coordinates (row/col)."

        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
            return False, f"Coordinates ({r}, {c}) are out of bounds."

        if self.board[r][c] is not None:
            return False, f"Cell ({r}, {c}) is already occupied."

        # Apply mark
        self.board[r][c] = mark
        self.move_count += 1

        # Check for completed lines
        winning_line_found: list[tuple[int, int]] | None = None
        for line in self._winning_lines:
            if all(self.board[lr][lc] == mark for lr, lc in line):
                winning_line_found = line
                break

        player = self.get_player(player_id)
        p_name = player.name if player else player_id
        other_players = [p for p in self.players if p.id != player_id]
        opp = other_players[0] if other_players else None
        opp_id = opp.id if opp else "opponent"
        opp_name = opp.name if opp else "Opponent"

        if winning_line_found is not None:
            line_coords = [[lr, lc] for lr, lc in winning_line_found]
            self.winning_cells = line_coords
            self.winning_line = line_coords

            if self.mode == "misere":
                # In Misère: Player completing 3-in-a-row LOSES; Opponent WINS!
                if opp:
                    opp.score += 1
                self.finish_game(
                    [opp_id],
                    f"{p_name} completed 3-in-a-row and loses (Misère rules). {opp_name} wins!",
                )
            else:
                if player:
                    player.score += 1
                self.finish_game(
                    [player_id],
                    f"{p_name} won by completing {self.target_streak}-in-a-row!",
                )
            return True, "Move processed."

        # Check for full board draw
        if self.move_count >= self.grid_size * self.grid_size:
            self.winning_cells = []
            self.winning_line = []
            self.finish_game([], "Match drawn — board full.")
            return True, "Match drawn."

        # Next turn
        if opp:
            self.turn_player_id = opp.id
        return True, "Move processed."

    def _extract_ultimate_coords(self, data: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
        sb = data.get("subboard", data.get("macro", data.get("board_index", data.get("board_idx"))))
        r = data.get("row", data.get("r", data.get("micro_r")))
        c = data.get("col", data.get("c", data.get("micro_c")))

        if sb is None:
            if "cell" in data:
                try:
                    cell_val = int(data["cell"])
                    if cell_val >= 9:
                        sb = cell_val // 9
                        rem = cell_val % 9
                        r = rem // 3
                        c = rem % 3
                    else:
                        r = cell_val // 3
                        c = cell_val % 3
                except (ValueError, TypeError):
                    pass
            elif "cell_idx" in data:
                try:
                    cell_idx = int(data["cell_idx"])
                    r = cell_idx // 3
                    c = cell_idx % 3
                except (ValueError, TypeError):
                    pass

        if sb is None and self.active_subboard is not None:
            sb = self.active_subboard

        try:
            return (int(sb), int(r), int(c)) if (sb is not None and r is not None and c is not None) else (None, None, None)
        except (ValueError, TypeError):
            return None, None, None

    def _handle_ultimate_move(
        self, player_id: str, mark: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        sb, r, c = self._extract_ultimate_coords(data)
        if sb is None or r is None or c is None:
            return False, "Missing sub-board or cell coordinates."

        if not (0 <= sb < 9 and 0 <= r < 3 and 0 <= c < 3):
            return False, f"Coordinates out of bounds: subboard={sb}, r={r}, c={c}."

        # Sub-board target routing rule
        if self.active_subboard is not None and sb != self.active_subboard:
            return False, f"Invalid sub-board {sb}. You must play in sub-board {self.active_subboard}."

        # Cannot play in an already decided or full sub-board
        if self.macro_board[sb] is not None:
            return False, f"Sub-board {sb} is already resolved ({self.macro_board[sb]})."

        if self.subboards[sb][r][c] is not None:
            return False, f"Cell ({r}, {c}) in sub-board {sb} is already occupied."

        # Apply mark
        self.subboards[sb][r][c] = mark
        self.move_count += 1

        # Check if local sub-board is won
        sub_grid = self.subboards[sb]
        for line in LINES_3X3:
            p0 = sub_grid[line[0][0]][line[0][1]]
            if p0 and p0 == sub_grid[line[1][0]][line[1][1]] == sub_grid[line[2][0]][line[2][1]]:
                self.macro_board[sb] = mark
                self.subboard_winning_cells[sb] = [[lr, lc] for lr, lc in line]
                break

        # If not won, check if sub-board is full (draw)
        if self.macro_board[sb] is None:
            if all(sub_grid[lr][lc] is not None for lr in range(3) for lc in range(3)):
                self.macro_board[sb] = "draw"

        player = self.get_player(player_id)
        p_name = player.name if player else player_id
        other_players = [p for p in self.players if p.id != player_id]
        opp = other_players[0] if other_players else None

        # Check macro board for 3 sub-boards in a row
        for m_line in MACRO_LINES_3X3:
            m0 = self.macro_board[m_line[0]]
            if m0 in ("X", "O") and m0 == self.macro_board[m_line[1]] == self.macro_board[m_line[2]]:
                if player:
                    player.score += 1
                self.macro_winning_line = list(m_line)
                self.finish_game(
                    [player_id],
                    f"{p_name} won Ultimate Tic-Tac-Toe by completing sub-boards {m_line}!",
                )
                return True, "Ultimate match won."

        # Check macro draw: all 9 subboards resolved or no open cells left anywhere
        has_any_open_cell = any(
            self.macro_board[i] is None
            and any(self.subboards[i][mr][mc] is None for mr in range(3) for mc in range(3))
            for i in range(9)
        )
        if not has_any_open_cell or all(s is not None for s in self.macro_board):
            self.finish_game([], "Ultimate Tic-Tac-Toe match drawn — all sub-boards resolved.")
            return True, "Ultimate match drawn."

        # Next target subboard routing (dictated by local cell r, c)
        next_target = r * 3 + c
        # If target subboard is won, drawn, or full -> Free placement fallback!
        target_resolved = self.macro_board[next_target] is not None
        target_full = all(
            self.subboards[next_target][mr][mc] is not None for mr in range(3) for mc in range(3)
        )
        if target_resolved or target_full:
            self.active_subboard = None  # Free placement across any open board
        else:
            self.active_subboard = next_target

        if opp:
            self.turn_player_id = opp.id
        return True, "Move processed."

    def get_public_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "phase": self.phase,
            "status": self.phase,
            "mode": self.mode,
            "grid_size": self.grid_size,
            "target_streak": self.target_streak,
            "turn_player_id": self.turn_player_id,
            "active_player": self.turn_player_id,
            "winner_ids": self.winner_ids,
            "winner": self.winner_ids[0] if self.winner_ids else None,
            "win_reason": self.win_reason,
            "player_symbols": self.player_symbols,
            "player_marks": self.player_symbols,
            "scores": {p.id: p.score for p in self.players},
            "move_count": self.move_count,
            "settings": self.settings,
        }

        if self.mode == "ultimate":
            state.update({
                "board": self.subboards,
                "subboards": self.subboards,
                "macro_board": self.macro_board,
                "active_subboard": self.active_subboard,
                "target_board": self.active_subboard,
                "sub_board_winners": self.macro_board,
                "subboard_winning_cells": self.subboard_winning_cells,
                "macro_winning_line": self.macro_winning_line,
            })
        else:
            state.update({
                "board": self.board,
                "winning_cells": self.winning_cells,
                "winning_line": self.winning_line,
            })

        return state

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
        if self.phase != "playing":
            return None

        mark = self.player_symbols.get(bot_id, "O")
        opp_mark = "O" if mark == "X" else "X"
        diff = self.settings.get("difficulty", "mid")

        if self.mode == "ultimate":
            return self._get_ultimate_bot_action(mark, opp_mark, diff)
        elif self.mode in ("classic", "misere"):
            return self._get_3x3_bot_action(mark, opp_mark, diff)
        else:
            return self._get_extended_bot_action(mark, opp_mark, diff)

    def _get_3x3_bot_action(self, my_mark: str, opp_mark: str, diff: str) -> tuple[str, dict[str, Any]] | None:
        open_cells = [
            (r, c)
            for r in range(3)
            for c in range(3)
            if self.board[r][c] is None
        ]
        if not open_cells:
            return None

        # Easy difficulty: purely random
        if diff == "easy":
            r, c = random.choice(open_cells)
            return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}

        is_misere = self.mode == "misere"

        # Hard difficulty: Unbeatable Minimax solver
        if diff == "hard":
            board_tuple = tuple(tuple(self.board[r][c] for c in range(3)) for r in range(3))
            best_val = -9999
            best_moves: list[tuple[int, int]] = []
            memo: dict[tuple[tuple[tuple[str | None, ...], ...], bool], int] = {}

            for r, c in open_cells:
                # Simulate move
                row_l = list(board_tuple[r])
                row_l[c] = my_mark
                next_b = list(board_tuple)
                next_b[r] = tuple(row_l)
                score = _minimax_eval_3x3(tuple(next_b), False, my_mark, opp_mark, 1, is_misere, memo)

                if score > best_val:
                    best_val = score
                    best_moves = [(r, c)]
                elif score == best_val:
                    best_moves.append((r, c))

            chosen_r, chosen_c = random.choice(best_moves) if best_moves else open_cells[0]
            return "place_mark", {
                "row": chosen_r,
                "col": chosen_c,
                "r": chosen_r,
                "c": chosen_c,
                "cell": chosen_r * 3 + chosen_c,
            }

        # Medium difficulty: Rule-based heuristics
        if is_misere:
            # Avoid moves that complete 3-in-a-row
            safe_moves = []
            for r, c in open_cells:
                self.board[r][c] = my_mark
                wins = any(all(self.board[lr][lc] == my_mark for lr, lc in line) for line in LINES_3X3)
                self.board[r][c] = None
                if not wins:
                    safe_moves.append((r, c))
            candidate_pool = safe_moves if safe_moves else open_cells
            # Prefer corners and center
            preferred = [(r, c) for r, c in candidate_pool if (r, c) in ((0, 0), (0, 2), (2, 0), (2, 2), (1, 1))]
            chosen_r, chosen_c = random.choice(preferred if preferred else candidate_pool)
            return "place_mark", {
                "row": chosen_r,
                "col": chosen_c,
                "r": chosen_r,
                "c": chosen_c,
                "cell": chosen_r * 3 + chosen_c,
            }

        # Medium Classic 3x3:
        # 1. Take immediate win
        for r, c in open_cells:
            self.board[r][c] = my_mark
            if any(all(self.board[lr][lc] == my_mark for lr, lc in line) for line in LINES_3X3):
                self.board[r][c] = None
                return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}
            self.board[r][c] = None

        # 2. Block immediate opponent win
        for r, c in open_cells:
            self.board[r][c] = opp_mark
            if any(all(self.board[lr][lc] == opp_mark for lr, lc in line) for line in LINES_3X3):
                self.board[r][c] = None
                return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}
            self.board[r][c] = None

        # 3. Take center if open
        if (1, 1) in open_cells:
            return "place_mark", {"row": 1, "col": 1, "r": 1, "c": 1, "cell": 4}

        # 4. Take corners
        corners = [(r, c) for r, c in open_cells if (r, c) in ((0, 0), (0, 2), (2, 0), (2, 2))]
        if corners:
            r, c = random.choice(corners)
            return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}

        r, c = random.choice(open_cells)
        return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}

    def _get_extended_bot_action(self, my_mark: str, opp_mark: str, diff: str) -> tuple[str, dict[str, Any]] | None:
        open_cells = [
            (r, c)
            for r in range(self.grid_size)
            for c in range(self.grid_size)
            if self.board[r][c] is None
        ]
        if not open_cells:
            return None

        if diff == "easy":
            r, c = random.choice(open_cells)
            return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * self.grid_size + c}

        # 1. Immediate win taking
        for r, c in open_cells:
            self.board[r][c] = my_mark
            if any(all(self.board[lr][lc] == my_mark for lr, lc in line) for line in self._winning_lines):
                self.board[r][c] = None
                return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * self.grid_size + c}
            self.board[r][c] = None

        # 2. Immediate opponent block
        for r, c in open_cells:
            self.board[r][c] = opp_mark
            if any(all(self.board[lr][lc] == opp_mark for lr, lc in line) for line in self._winning_lines):
                self.board[r][c] = None
                return "place_mark", {"row": r, "col": c, "r": r, "c": c, "cell": r * self.grid_size + c}
            self.board[r][c] = None

        # 3. Positional heuristic evaluation across lines
        best_score = -999999
        best_moves: list[tuple[int, int]] = []

        center_val = (self.grid_size - 1) / 2.0
        for r, c in open_cells:
            score = 0
            # Center proximity bonus
            dist = abs(r - center_val) + abs(c - center_val)
            score += int((self.grid_size - dist) * 15)

            # Evaluate lines containing (r, c)
            for line in self._winning_lines:
                if (r, c) in line:
                    my_count = sum(1 for lr, lc in line if self.board[lr][lc] == my_mark)
                    opp_count = sum(1 for lr, lc in line if self.board[lr][lc] == opp_mark)

                    if opp_count == 0:
                        if my_count == self.target_streak - 2:
                            score += 400
                        elif my_count == 1:
                            score += 50
                    elif my_count == 0:
                        if opp_count == self.target_streak - 2:
                            score += 350
                        elif opp_count == 1:
                            score += 40

            if score > best_score:
                best_score = score
                best_moves = [(r, c)]
            elif score == best_score:
                best_moves.append((r, c))

        chosen_r, chosen_c = random.choice(best_moves) if best_moves else random.choice(open_cells)
        return "place_mark", {
            "row": chosen_r,
            "col": chosen_c,
            "r": chosen_r,
            "c": chosen_c,
            "cell": chosen_r * self.grid_size + chosen_c,
        }

    def _get_ultimate_bot_action(self, my_mark: str, opp_mark: str, diff: str) -> tuple[str, dict[str, Any]] | None:
        # Determine accessible subboards
        if self.active_subboard is not None and self.macro_board[self.active_subboard] is None:
            active_sbs = [self.active_subboard]
        else:
            active_sbs = [i for i in range(9) if self.macro_board[i] is None]

        legal_moves: list[tuple[int, int, int]] = []
        for sb in active_sbs:
            for r in range(3):
                for c in range(3):
                    if self.subboards[sb][r][c] is None:
                        legal_moves.append((sb, r, c))

        if not legal_moves:
            return None

        if diff == "easy":
            sb, r, c = random.choice(legal_moves)
            return "place_mark", {
                "subboard": sb,
                "macro": sb,
                "board_idx": sb,
                "row": r,
                "col": c,
                "r": r,
                "c": c,
                "cell": r * 3 + c,
            }

        # Medium / Hard tactical scoring
        best_score = -999999
        best_moves: list[tuple[int, int, int]] = []

        for sb, r, c in legal_moves:
            score = 0
            grid = self.subboards[sb]

            # 1. Does this move win the subboard?
            grid[r][c] = my_mark
            sub_win = any(all(grid[lr][lc] == my_mark for lr, lc in line) for line in LINES_3X3)
            grid[r][c] = None

            if sub_win:
                score += 5000
                # Does winning this subboard win the whole macro game?
                self.macro_board[sb] = my_mark
                macro_win = any(
                    self.macro_board[m[0]] == self.macro_board[m[1]] == self.macro_board[m[2]] == my_mark
                    for m in MACRO_LINES_3X3
                )
                self.macro_board[sb] = None
                if macro_win:
                    score += 100000

            # 2. Does this move block the opponent from winning this subboard?
            grid[r][c] = opp_mark
            opp_sub_win = any(all(grid[lr][lc] == opp_mark for lr, lc in line) for line in LINES_3X3)
            grid[r][c] = None
            if opp_sub_win:
                score += 2500

            # 3. Target destination routing evaluation
            dest_sb = r * 3 + c
            if self.macro_board[dest_sb] is not None:
                # Directs opponent to resolved subboard -> unlocks free placement for them!
                score -= 800
            else:
                # Check if opponent could win dest_sb immediately on next turn
                dest_grid = self.subboards[dest_sb]
                threat = False
                for dr in range(3):
                    for dc in range(3):
                        if dest_grid[dr][dc] is None:
                            dest_grid[dr][dc] = opp_mark
                            if any(all(dest_grid[lr][lc] == opp_mark for lr, lc in line) for line in LINES_3X3):
                                threat = True
                            dest_grid[dr][dc] = None
                            if threat:
                                break
                    if threat:
                        break
                if threat:
                    score -= 1500

            # 4. Micro-cell preferences (center > corners > edges)
            if (r, c) == (1, 1):
                score += 50
            elif (r, c) in ((0, 0), (0, 2), (2, 0), (2, 2)):
                score += 25

            # 5. Macro-board positional preferences (center macro subboard 4)
            if sb == 4:
                score += 100
            elif sb in (0, 2, 6, 8):
                score += 40

            if score > best_score:
                best_score = score
                best_moves = [(sb, r, c)]
            elif score == best_score:
                best_moves.append((sb, r, c))

        chosen_sb, chosen_r, chosen_c = random.choice(best_moves) if best_moves else random.choice(legal_moves)
        return "place_mark", {
            "subboard": chosen_sb,
            "macro": chosen_sb,
            "board_idx": chosen_sb,
            "row": chosen_r,
            "col": chosen_c,
            "r": chosen_r,
            "c": chosen_c,
            "cell": chosen_r * 3 + chosen_c,
        }
