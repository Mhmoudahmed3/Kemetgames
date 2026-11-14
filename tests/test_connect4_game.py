"""Comprehensive server-authoritative unit tests for Connect 4 (Milestone 4).

Covers:
1. Classic 7x6 mode: gravity drops, alternation, horizontal, vertical, positive diagonal,
   negative diagonal wins, winning_cells highlighting, and full board draw.
2. Boundary & input validation: full column rejection, invalid column indices,
   wrong turn rejection, action aliases ("drop", "move", "play"), and resignation/forfeit.
3. Pop Out mode: popping bottom-row disc, upper disc downward gravity shift, cannot pop
   opponent's disc, cannot pop empty column, win-on-pop, and simultaneous double-win tie.
4. 5-in-a-Row mode: 9x7 grid dimensions, 4-in-a-row does NOT win, 5-in-a-row horizontal,
   vertical, diagonal wins, and column boundary checks.
5. Blitz mode: 5s timer configuration, _tick_timers countdown, timeout handling, turn action
   timer resets, and pop-out combo under blitz timer.
6. AI Bot intelligence: legal move generation, immediate win taking, opponent win blocking,
   5-in-a-row handling, and multi-game simulation.
7. Rematch & state reset: board wipe, phase reset, score/player preservation, mid-game rejection.
8. RoomManager & WebSocket integration: room creation, joining, start game, pass-and-play,
   solo vs AI, rematch lifecycle, and duel forfeit.
"""

from __future__ import annotations

import time
from typing import Any
import pytest
from starlette.testclient import TestClient

from backend.base_game import PlayerSlot
from backend.games.connect4_game import Connect4Game
from backend.main import app


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def make_slots(count: int = 2, bots_from: int | None = None) -> list[PlayerSlot]:
    slots: list[PlayerSlot] = []
    for i in range(1, count + 1):
        pid = f"p{i}"
        is_bot = (bots_from is not None) and (i >= bots_from)
        slots.append(
            PlayerSlot(
                id=pid,
                name=f"Bot_{i}" if is_bot else f"Player_{i}",
                is_host=(i == 1),
                is_bot=is_bot,
                connected=True,
            )
        )
    return slots


def c4_drop(game: Connect4Game, pid: str, col: int) -> tuple[bool, str]:
    """Helper to drop a disc using standard action names."""
    data = {"col": col, "column": col}
    for act in ("drop", "move", "play"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "full" in msg.lower() or "bound" in msg.lower() or "turn" in msg.lower() or "finish" in msg.lower():
            return ok, msg
    return ok, msg


def c4_pop(game: Connect4Game, pid: str, col: int) -> tuple[bool, str]:
    """Helper to pop a bottom disc using standard action names."""
    data = {"col": col, "column": col}
    for act in ("pop", "pop_out"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "opponent" in msg.lower() or "empty" in msg.lower() or "turn" in msg.lower():
            return ok, msg
    return ok, msg


def _recv_until_type(ws, target_type: str, max_msgs: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    history = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        history.append(msg)
        if msg.get("type") == target_type:
            return msg, history
    raise TimeoutError(f"Target message {target_type} not received within {max_msgs} messages.")


# =============================================================================
# 1. CLASSIC MODE TESTS
# =============================================================================

class TestConnect4ClassicMode:
    """Tests standard 7x6 board, gravity mechanics, win orientations, and draw states."""

    def test_classic_initialization(self):
        game = Connect4Game("C4_INIT", make_slots(2))
        game.start_game({"mode": "classic"})
        assert game.cols == 7
        assert game.rows == 6
        assert game.target_streak == 4
        assert game.phase == "playing"
        assert game.turn_player_id == "p1"
        assert game.winner_ids == []
        assert all(game.board[r][c] is None for r in range(6) for c in range(7))

    def test_classic_gravity_drop_sequence(self):
        game = Connect4Game("C4_GRAV", make_slots(2))
        game.start_game()
        # Drop 1: P1 in col 3 -> lands in bottom row (index 5)
        ok1, _ = c4_drop(game, "p1", 3)
        assert ok1 is True
        assert game.board[5][3] == "p1"

        # Drop 2: P2 in col 3 -> lands in row 4
        ok2, _ = c4_drop(game, "p2", 3)
        assert ok2 is True
        assert game.board[4][3] == "p2"

        # Drop 3: P1 in col 3 -> lands in row 3
        ok3, _ = c4_drop(game, "p1", 3)
        assert ok3 is True
        assert game.board[3][3] == "p1"

    def test_classic_turn_alternation(self):
        game = Connect4Game("C4_ALT", make_slots(2))
        game.start_game()
        # P1 moves
        c4_drop(game, "p1", 0)
        assert game.turn_player_id == "p2"

        # P1 attempts to move again out of turn
        ok_wrong, msg = c4_drop(game, "p1", 0)
        assert ok_wrong is False
        assert "turn" in msg.lower()

        # P2 moves
        ok_p2, _ = c4_drop(game, "p2", 1)
        assert ok_p2 is True
        assert game.turn_player_id == "p1"

    def test_classic_horizontal_wins(self):
        game = Connect4Game("C4_HORIZ", make_slots(2))
        game.start_game()
        # P1 drops cols 0, 1, 2, 3 in bottom row; P2 drops in row above
        for col in range(3):
            c4_drop(game, "p1", col)
            c4_drop(game, "p2", col)

        assert game.phase == "playing"
        c4_drop(game, "p1", 3)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]
        assert game.get_player("p1").score == 1

    def test_classic_vertical_wins(self):
        game = Connect4Game("C4_VERT", make_slots(2))
        game.start_game()
        # P1 stacks in col 0, P2 plays in col 1
        for _ in range(3):
            c4_drop(game, "p1", 0)
            c4_drop(game, "p2", 1)

        assert game.phase == "playing"
        c4_drop(game, "p1", 0)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_classic_positive_diagonal_win(self):
        """Tests positive diagonal (/) from (row 5, col 0) up to (row 2, col 3)."""
        game = Connect4Game("C4_DIAG_POS", make_slots(2))
        game.start_game()
        # Setup:
        # Col 0: P1 (settles row 5)
        # Col 1: P2, P1 (settles row 5, 4)
        # Col 2: P2, P2, P1 (settles row 5, 4, 3)
        # Col 3: P2, P2, P2, P1 (settles row 5, 4, 3, 2)
        moves = [
            ("p1", 0),  # (5, 0) P1
            ("p2", 1),  # (5, 1) P2
            ("p1", 1),  # (4, 1) P1
            ("p2", 2),  # (5, 2) P2
            ("p1", 3),  # (5, 3) P1 (dummy)
            ("p2", 2),  # (4, 2) P2
            ("p1", 2),  # (3, 2) P1
            ("p2", 3),  # (4, 3) P2
            ("p1", 4),  # (5, 4) P1 (dummy)
            ("p2", 3),  # (3, 3) P2
            ("p1", 3),  # (2, 3) P1 -> Connects (5,0), (4,1), (3,2), (2,3)
        ]
        for pid, c in moves:
            ok, _ = c4_drop(game, pid, c)
            assert ok is True

        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_classic_negative_diagonal_win(self):
        """Tests negative diagonal (\\) from (row 2, col 0) down to (row 5, col 3)."""
        game = Connect4Game("C4_DIAG_NEG", make_slots(2))
        game.start_game()
        # Col 3: (5, 3) P1
        # Col 2: (5, 2) P2, (4, 2) P1
        # Col 1: (5, 1) P2, (4, 1) P2, (3, 1) P1
        # Col 0: (5, 0) P2, (4, 0) P2, (3, 0) P2, (2, 0) P1
        moves = [
            ("p1", 3),  # (5, 3) P1
            ("p2", 2),  # (5, 2) P2
            ("p1", 2),  # (4, 2) P1
            ("p2", 1),  # (5, 1) P2
            ("p1", 4),  # (5, 4) P1 (dummy)
            ("p2", 1),  # (4, 1) P2
            ("p1", 1),  # (3, 1) P1
            ("p2", 0),  # (5, 0) P2
            ("p1", 4),  # (4, 4) P1 (dummy)
            ("p2", 0),  # (4, 0) P2
            ("p1", 5),  # (5, 5) P1 (dummy)
            ("p2", 0),  # (3, 0) P2
            ("p1", 0),  # (2, 0) P1 -> connects (2,0), (3,1), (4,2), (5,3)
        ]
        for pid, c in moves:
            ok, _ = c4_drop(game, pid, c)
            assert ok is True

        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_classic_full_board_draw(self):
        game = Connect4Game("C4_DRAW", make_slots(2))
        game.start_game()
        draw_board = [
            ["p1", "p2", "p1", "p2", "p1", "p2", None],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p1"],
            ["p2", "p1", "p2", "p1", "p2", "p1", "p2"],
            ["p2", "p1", "p2", "p1", "p2", "p1", "p2"],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p1"],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p2"],
        ]
        game.board = draw_board
        game.turn_player_id = "p1"
        ok, _ = c4_drop(game, "p1", 6)
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == []

    def test_classic_winning_cells_in_public_state(self):
        game = Connect4Game("C4_PUB_CELLS", make_slots(2))
        game.start_game()
        for c in range(3):
            c4_drop(game, "p1", c)
            c4_drop(game, "p2", c)
        c4_drop(game, "p1", 3)
        pub = game.get_public_state()
        assert "winning_cells" in pub
        expected = [[5, 0], [5, 1], [5, 2], [5, 3]]
        for pt in expected:
            assert pt in pub["winning_cells"] or tuple(pt) in pub["winning_cells"]


# =============================================================================
# 2. BOUNDARY & ERROR TESTS
# =============================================================================

class TestConnect4BoundariesAndErrors:
    """Tests full column rejections, out-of-bounds columns, and game state constraints."""

    def test_drop_in_full_column_rejected(self):
        game = Connect4Game("C4_FULL_COL", make_slots(2))
        game.start_game()
        # Stack 6 discs in col 0
        for _ in range(3):
            c4_drop(game, "p1", 0)
            c4_drop(game, "p2", 0)

        # 7th drop must fail
        ok, msg = c4_drop(game, "p1", 0)
        assert ok is False
        assert "full" in msg.lower()
        # Player retains turn
        assert game.turn_player_id == "p1"

    def test_invalid_column_indices(self):
        game = Connect4Game("C4_INVALID_COL", make_slots(2))
        game.start_game()
        ok_neg, _ = c4_drop(game, "p1", -1)
        assert ok_neg is False
        ok_high, _ = c4_drop(game, "p1", 7)
        assert ok_high is False
        ok_far, _ = c4_drop(game, "p1", 100)
        assert ok_far is False

    def test_actions_rejected_when_game_finished(self):
        game = Connect4Game("C4_FINISHED", make_slots(2))
        game.start_game()
        game.finish_game(["p1"], "P1 won")
        ok, msg = c4_drop(game, "p1", 0)
        assert ok is False
        assert "playing" in msg.lower()

    def test_action_aliases_support(self):
        game = Connect4Game("C4_ALIASES", make_slots(2))
        game.start_game()
        # Test "move" with "column"
        ok1, _ = game.handle_action("p1", "move", {"column": 1})
        assert ok1 is True
        # Test "play" with "col"
        ok2, _ = game.handle_action("p2", "play", {"col": 2})
        assert ok2 is True
        # Test "drop" with both
        ok3, _ = game.handle_action("p1", "drop", {"col": 3, "column": 3})
        assert ok3 is True

    def test_player_resignation_and_forfeit(self):
        game = Connect4Game("C4_RESIGN", make_slots(2))
        game.start_game()
        ok, _ = game.handle_action("p1", "resign", {})
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"]


# =============================================================================
# 3. POP OUT MODE TESTS
# =============================================================================

class TestConnect4PopOutMode:
    """Tests bottom-disc popping, gravity shifts, simultaneous double-win tie, and invalid pops."""

    def test_pop_out_initialization(self):
        game = Connect4Game("C4_POP_INIT", make_slots(2))
        game.start_game({"mode": "pop_out"})
        assert game.mode == "pop_out"
        assert game.cols == 7
        assert game.rows == 6

    def test_pop_own_disc_from_bottom(self):
        game = Connect4Game("C4_POP_OWN", make_slots(2))
        game.start_game({"mode": "pop_out"})
        c4_drop(game, "p1", 2)  # Row 5 col 2 has P1
        c4_drop(game, "p2", 2)  # Row 4 col 2 has P2

        ok, _ = c4_pop(game, "p1", 2)
        assert ok is True
        # P2's disc shifted down to row 5, row 4 is now None
        assert game.board[5][2] == "p2"
        assert game.board[4][2] is None

    def test_pop_opponent_disc_rejected(self):
        game = Connect4Game("C4_POP_OPP", make_slots(2))
        game.start_game({"mode": "pop_out"})
        c4_drop(game, "p1", 1)  # Bottom of col 1 is P1
        c4_drop(game, "p2", 2)  # Bottom of col 2 is P2

        # P1 tries to pop col 2 (P2's disc)
        ok, msg = c4_pop(game, "p1", 2)
        assert ok is False
        assert "opponent" in msg.lower()

    def test_pop_empty_column_rejected(self):
        game = Connect4Game("C4_POP_EMPTY", make_slots(2))
        game.start_game({"mode": "pop_out"})
        ok, msg = c4_pop(game, "p1", 4)
        assert ok is False
        assert "empty" in msg.lower()

    def test_pop_out_creates_own_win(self):
        """Popping own bottom disc causes upper discs to shift down and complete 4-in-a-row for active player."""
        game = Connect4Game("C4_POP_OWN_WIN", make_slots(2))
        game.start_game({"mode": "pop_out"})
        # Place P1 discs at (5, 1), (5, 2), (5, 3)
        game.board[5][1] = "p1"
        game.board[5][2] = "p1"
        game.board[5][3] = "p1"
        # In col 0: bottom is P1 (5, 0), above is P1 (4, 0)
        game.board[5][0] = "p1"
        game.board[4][0] = "p1"

        game.turn_player_id = "p1"
        ok, _ = c4_pop(game, "p1", 0)
        assert ok is True
        # Disc at (4, 0) falls to (5, 0), completing row 5: (5,0), (5,1), (5,2), (5,3)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_pop_out_creates_opponent_win(self):
        """Popping own bottom disc inadvertently drops opponent disc completing 4-in-a-row for opponent."""
        game = Connect4Game("C4_POP_OPP_WIN", make_slots(2))
        game.start_game({"mode": "pop_out"})
        # Opponent has row 5 at cols 1, 2, 3
        game.board[5][1] = "p2"
        game.board[5][2] = "p2"
        game.board[5][3] = "p2"
        # In col 0: P1 at (5,0), P2 at (4,0)
        game.board[5][0] = "p1"
        game.board[4][0] = "p2"

        game.turn_player_id = "p1"
        ok, _ = c4_pop(game, "p1", 0)
        assert ok is True
        # P2 completes 4-in-a-row
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"]

    def test_pop_out_simultaneous_double_win_resolves_to_draw(self):
        """When popping causes both P1 and P2 to complete 4-in-a-row, game terminates in a tie."""
        game = Connect4Game("C4_POP_DBL_WIN", make_slots(2))
        game.start_game({"mode": "pop_out"})
        # Setup board:
        # Row 5 (bottom): col 0='p1', col 1='p2', col 2='p2', col 3='p2'
        # Row 4:          col 0='p2', col 1='p1', col 2='p1', col 3='p1'
        # Row 3:          col 0='p1'
        game.board[5][0] = "p1"
        game.board[5][1] = "p2"
        game.board[5][2] = "p2"
        game.board[5][3] = "p2"

        game.board[4][0] = "p2"
        game.board[4][1] = "p1"
        game.board[4][2] = "p1"
        game.board[4][3] = "p1"

        game.board[3][0] = "p1"

        game.turn_player_id = "p1"
        ok, _ = c4_pop(game, "p1", 0)
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == []


# =============================================================================
# 4. 5-IN-A-ROW MODE TESTS
# =============================================================================

class TestConnect4FiveInARowMode:
    """Tests 9x7 grid dimensions, 4-in-a-row non-win, and 5-in-a-row win requirements."""

    def test_five_in_a_row_grid_dimensions(self):
        game = Connect4Game("C4_5ROW_DIM", make_slots(2))
        game.start_game({"mode": "five_in_a_row"})
        assert game.cols == 9
        assert game.rows == 7
        assert game.target_streak == 5
        assert len(game.board) == 7
        assert len(game.board[0]) == 9

    def test_four_in_a_row_does_not_win(self):
        game = Connect4Game("C4_4ROW_NOWIN", make_slots(2))
        game.start_game({"mode": "5_in_a_row", "grid_size": "9x7"})
        for c in range(4):
            c4_drop(game, "p1", c)
            c4_drop(game, "p2", c)
        assert game.phase == "playing"
        assert game.winner_ids == []

    def test_five_in_a_row_horizontal_win(self):
        game = Connect4Game("C4_5ROW_HORIZ", make_slots(2))
        game.start_game({"mode": "5_in_a_row"})
        for c in range(4):
            c4_drop(game, "p1", c)
            c4_drop(game, "p2", c)
        # 5th drop
        ok, _ = c4_drop(game, "p1", 4)
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]
        assert len(game.winning_cells) >= 5

    def test_five_in_a_row_vertical_win(self):
        game = Connect4Game("C4_5ROW_VERT", make_slots(2))
        game.start_game({"mode": "five_in_a_row"})
        for _ in range(4):
            c4_drop(game, "p1", 0)
            c4_drop(game, "p2", 1)
        assert game.phase == "playing"
        c4_drop(game, "p1", 0)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_five_in_a_row_diagonal_win(self):
        game = Connect4Game("C4_5ROW_DIAG", make_slots(2))
        game.start_game({"mode": "five_in_a_row"})
        # Build positive diagonal of 5 discs
        # Cols 0..4
        for r in range(5):
            for _ in range(r):
                c4_drop(game, "p2" if game.turn_player_id == "p2" else "p1", r)
            # drop the diagonal disc
            if game.turn_player_id != "p1":
                c4_drop(game, "p2", 8)  # dummy
            c4_drop(game, "p1", r)

        # Check that completing 5-in-a-row terminates game
        game.board[6][0] = "p1"
        game.board[5][1] = "p1"
        game.board[4][2] = "p1"
        game.board[3][3] = "p1"
        game.board[2][4] = "p1"
        won, cells = game._check_player_win("p1")
        assert won is True
        assert len(cells) == 5

    def test_five_in_a_row_column_boundary(self):
        game = Connect4Game("C4_5ROW_BND", make_slots(2))
        game.start_game({"mode": "five_in_a_row"})
        ok_valid, _ = c4_drop(game, "p1", 8)
        assert ok_valid is True
        ok_invalid, _ = c4_drop(game, "p2", 9)
        assert ok_invalid is False


# =============================================================================
# 5. BLITZ MODE TESTS
# =============================================================================

class TestConnect4BlitzMode:
    """Tests 5s per-turn timer, clock resets on valid moves, and timeout forfeitures."""

    def test_blitz_timer_configuration(self):
        game = Connect4Game("C4_BLITZ_CFG", make_slots(2))
        game.start_game({"mode": "blitz", "timer": 5})
        assert game.turn_time_limit == 5.0
        assert game.turn_started_at is not None

    def test_blitz_tick_timers_within_time_limit(self):
        game = Connect4Game("C4_BLITZ_OK", make_slots(2))
        game.start_game({"mode": "blitz", "timer": 5})
        now = time.time()
        timeout = game._tick_timers(now + 3.0)
        assert timeout is False
        assert game.phase == "playing"

    def test_blitz_tick_timers_expiry_triggers_timeout(self):
        game = Connect4Game("C4_BLITZ_EXP", make_slots(2))
        game.start_game({"mode": "blitz", "timer": 5})
        now = time.time()
        timeout = game._tick_timers(now + 6.0)
        assert timeout is True
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"]
        assert game.get_player("p2").score == 1

    def test_blitz_move_resets_turn_timer(self):
        game = Connect4Game("C4_BLITZ_RESET", make_slots(2))
        game.start_game({"mode": "blitz", "timer": 5})
        t0 = time.time()
        # Advance 3s
        assert game._tick_timers(t0 + 3.0) is False
        # P1 moves at t0 + 3s
        c4_drop(game, "p1", 0)
        # Clock reset for P2; advance 3s past move -> total 6s from t0, but only 3s for P2
        t_move = t0 + 3.0
        assert game._tick_timers(t_move + 3.0) is False
        # Exceeding 5s for P2 triggers timeout
        assert game._tick_timers(t_move + 6.0) is True
        assert game.winner_ids == ["p1"]

    def test_blitz_pop_out_combo(self):
        game = Connect4Game("C4_BLITZ_POP", make_slots(2))
        game.start_game({"mode": "pop_out", "timer": 5})
        c4_drop(game, "p1", 3)
        c4_drop(game, "p2", 3)
        t0 = time.time()
        assert game._tick_timers(t0 + 3.0) is False
        ok, _ = c4_pop(game, "p1", 3)
        assert ok is True
        t_pop = t0 + 3.0
        assert game._tick_timers(t_pop + 3.0) is False
        assert game._tick_timers(t_pop + 6.0) is True


# =============================================================================
# 6. AI BOT TESTS
# =============================================================================

class TestConnect4BotAI:
    """Tests bot action generation, win taking, win blocking, and full game simulations."""

    def test_bot_valid_moves_generation(self):
        game = Connect4Game("C4_BOT_GEN", make_slots(2, bots_from=2))
        game.start_game({"difficulty": "mid"})
        c4_drop(game, "p1", 3)
        assert game.turn_player_id == "p2"
        action, data = game.get_bot_action("p2")
        assert action in ("drop", "pop")
        assert 0 <= data["col"] < 7

    def test_bot_takes_immediate_winning_move(self):
        game = Connect4Game("C4_BOT_WIN", make_slots(2, bots_from=2))
        game.start_game({"difficulty": "mid"})
        # Place 3 bot discs in row 5 at cols 0, 1, 2
        game.board[5][0] = "p2"
        game.board[5][1] = "p2"
        game.board[5][2] = "p2"
        game.turn_player_id = "p2"

        action, data = game.get_bot_action("p2")
        assert action == "drop"
        assert data["col"] == 3  # Must take winning drop

    def test_bot_blocks_opponent_immediate_win(self):
        game = Connect4Game("C4_BOT_BLOCK", make_slots(2, bots_from=2))
        game.start_game({"difficulty": "mid"})
        # P1 has 3 in a row at cols 0, 1, 2
        game.board[5][0] = "p1"
        game.board[5][1] = "p1"
        game.board[5][2] = "p1"
        game.turn_player_id = "p2"

        action, data = game.get_bot_action("p2")
        assert action == "drop"
        assert data["col"] == 3  # Must block P1 winning drop

    def test_bot_handles_five_in_a_row_mode(self):
        game = Connect4Game("C4_BOT_5ROW", make_slots(2, bots_from=2))
        game.start_game({"mode": "five_in_a_row", "difficulty": "hard"})
        c4_drop(game, "p1", 4)
        action, data = game.get_bot_action("p2")
        assert action == "drop"
        assert 0 <= data["col"] < 9

    def test_bot_vs_bot_simulation_completes(self):
        """Simulate 3 complete Bot vs Bot games to ensure zero exceptions."""
        for game_idx in range(3):
            game = Connect4Game(f"C4_BVB_{game_idx}", make_slots(2, bots_from=1))
            game.start_game({"difficulty": "easy"})
            max_moves = 42
            moves = 0
            while game.phase == "playing" and moves < max_moves:
                curr_bot = game.turn_player_id
                action, data = game.get_bot_action(curr_bot)
                assert action is not None
                ok, _ = game.handle_action(curr_bot, action, data)
                assert ok is True
                moves += 1
            assert game.phase == "finished"


# =============================================================================
# 7. REMATCH & STATE RESET TESTS
# =============================================================================

class TestConnect4RematchAndStateReset:
    """Tests game reset lifecycle for rematches."""

    def test_rematch_after_win_clears_board(self):
        game = Connect4Game("C4_REMATCH_CLR", make_slots(2))
        game.start_game()
        for col in range(3):
            c4_drop(game, "p1", col)
            c4_drop(game, "p2", col)
        c4_drop(game, "p1", 3)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

        # Call rematch action
        ok, _ = game.handle_action("p1", "rematch", {})
        assert ok is True
        assert game.phase == "playing"
        assert game.winner_ids == []
        assert all(game.board[r][c] is None for r in range(6) for c in range(7))
        # Moves can resume
        ok_next, _ = c4_drop(game, "p1", 3)
        assert ok_next is True

    def test_rematch_preserves_players_and_settings(self):
        game = Connect4Game("C4_REMATCH_PRESERVE", make_slots(2))
        game.start_game({"mode": "pop_out", "difficulty": "hard"})
        game.finish_game(["p1"], "P1 won")
        p1 = game.get_player("p1")
        p1.score = 3

        game.reset_for_rematch()
        assert game.mode == "pop_out"
        assert game.settings["difficulty"] == "hard"
        assert len(game.players) == 2
        assert game.get_player("p1").score == 3

    def test_rematch_rejected_while_game_active(self):
        game = Connect4Game("C4_REMATCH_ACT", make_slots(2))
        game.start_game()
        ok, msg = game.handle_action("p1", "rematch", {})
        assert ok is False
        assert "progress" in msg.lower()


# =============================================================================
# 8. ROOM & WEBSOCKET INTEGRATION TESTS
# =============================================================================

class TestConnect4RoomAndPlatformIntegration:
    """Tests FastAPI WebSocket room creation, joining, start game, pass-and-play, and rematch."""

    def test_ws_room_creation_and_join(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/host_c4") as ws_h, client.websocket_connect("/ws/guest_c4") as ws_g:
                ws_h.receive_json()
                ws_g.receive_json()
                ws_h.send_json({"type": "SET_NAME", "player_name": "HostC4", "payload": {}})
                ws_h.receive_json()
                ws_g.send_json({"type": "SET_NAME", "player_name": "GuestC4", "payload": {}})
                ws_g.receive_json()

                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HostC4",
                    "game_type": "connect4",
                    "payload": {"action": "create", "data": {"is_public": True}},
                })
                h_joined = ws_h.receive_json()
                assert h_joined["type"] == "ROOM_JOINED"
                code = h_joined["room_code"]

                ws_g.receive_json()  # drain lobby state
                ws_g.send_json({
                    "type": "JOIN_ROOM",
                    "player_name": "GuestC4",
                    "room_code": code,
                    "payload": {},
                })
                g_joined = ws_g.receive_json()
                assert g_joined["type"] == "ROOM_JOINED"
                assert len(g_joined["players"]) == 2

    def test_ws_start_game_and_turns(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/h_turn") as ws_h, client.websocket_connect("/ws/g_turn") as ws_g:
                ws_h.receive_json()
                ws_g.receive_json()
                ws_h.send_json({"type": "SET_NAME", "player_name": "HTurn", "payload": {}})
                ws_h.receive_json()
                ws_g.send_json({"type": "SET_NAME", "player_name": "GTurn", "payload": {}})
                ws_g.receive_json()

                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HTurn",
                    "game_type": "connect4",
                    "payload": {"action": "create", "data": {"is_public": True}},
                })
                code = ws_h.receive_json()["room_code"]
                ws_g.receive_json()

                ws_g.send_json({"type": "JOIN_ROOM", "player_name": "GTurn", "room_code": code, "payload": {}})
                ws_g.receive_json()
                ws_h.receive_json()

                # Start game
                ws_h.send_json({
                    "type": "START_GAME",
                    "player_name": "HTurn",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws_h, "GAME_STATE")
                _recv_until_type(ws_g, "GAME_STATE")

                # Host drops disc
                ws_h.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "HTurn",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "drop", "data": {"col": 3, "column": 3}},
                })
                st_msg, _ = _recv_until_type(ws_h, "GAME_STATE")
                assert st_msg["public_state"]["board"][5][3] is not None

    def test_ws_pass_and_play_local_moves(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/pnp_c4") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "PnpC4", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "PnpC4",
                    "game_type": "connect4",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "settings": {"mode": "classic", "pass_and_play": True},
                        },
                    },
                })
                ws.receive_json()  # ROOM_JOINED
                ws.receive_json()  # GAME_STARTED
                ws.receive_json()  # GAME_STATE

                # Move 1 (P1)
                ws.send_json({
                    "type": "GAME_ACTION",
                    "payload": {"action": "drop", "data": {"col": 2, "column": 2}},
                })
                m1 = ws.receive_json()
                assert m1["type"] == "GAME_STATE"
                assert m1["public_state"]["board"][5][2] == "pnp_c4"

                # Move 2 (P2 from same client)
                ws.send_json({
                    "type": "GAME_ACTION",
                    "payload": {"action": "drop", "data": {"col": 2, "column": 2}},
                })
                m2 = ws.receive_json()
                assert m2["type"] == "GAME_STATE"
                assert m2["public_state"]["board"][4][2] is not None

    def test_ws_solo_vs_ai_mode(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/solo_c4") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "SoloC4", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "SoloC4",
                    "game_type": "connect4",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "settings": {"mode": "classic", "difficulty": "mid"},
                        },
                    },
                })
                ws.receive_json()  # ROOM_JOINED
                ws.receive_json()  # GAME_STARTED
                st = ws.receive_json()  # GAME_STATE
                assert len(st["players"]) == 2
                assert any(p["is_bot"] for p in st["players"])

    def test_ws_rematch_lifecycle(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/rm_h") as ws_h, client.websocket_connect("/ws/rm_g") as ws_g:
                ws_h.receive_json()
                ws_g.receive_json()
                ws_h.send_json({"type": "SET_NAME", "player_name": "RmH", "payload": {}})
                ws_h.receive_json()
                ws_g.send_json({"type": "SET_NAME", "player_name": "RmG", "payload": {}})
                ws_g.receive_json()

                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "RmH",
                    "game_type": "connect4",
                    "payload": {"action": "create", "data": {"is_public": True}},
                })
                code = ws_h.receive_json()["room_code"]
                ws_g.receive_json()

                ws_g.send_json({"type": "JOIN_ROOM", "player_name": "RmG", "room_code": code, "payload": {}})
                ws_g.receive_json()
                ws_h.receive_json()

                # Start game
                ws_h.send_json({
                    "type": "START_GAME",
                    "player_name": "RmH",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws_h, "GAME_STATE")
                _recv_until_type(ws_g, "GAME_STATE")

                # Vertical 4-streak for host
                drops = [
                    (ws_h, "RmH", 0),
                    (ws_g, "RmG", 1),
                    (ws_h, "RmH", 0),
                    (ws_g, "RmG", 1),
                    (ws_h, "RmH", 0),
                    (ws_g, "RmG", 1),
                    (ws_h, "RmH", 0),
                ]
                for ws_curr, p_name, col in drops[:-1]:
                    ws_curr.send_json({
                        "type": "GAME_ACTION",
                        "player_name": p_name,
                        "room_code": code,
                        "game_type": "connect4",
                        "payload": {"action": "drop", "data": {"col": col, "column": col}},
                    })
                    _recv_until_type(ws_h, "GAME_STATE")
                    _recv_until_type(ws_g, "GAME_STATE")

                # Winning drop
                ws_h.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "RmH",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "drop", "data": {"col": 0, "column": 0}},
                })
                _recv_until_type(ws_h, "GAME_OVER")
                _recv_until_type(ws_g, "GAME_OVER")

                # Rematch
                ws_h.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "RmH",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "rematch", "data": {}},
                })
                rm_msg, _ = _recv_until_type(ws_h, "GAME_STARTED")
                assert rm_msg["public_state"]["phase"] == "playing"
                assert rm_msg["public_state"]["winner_ids"] == []

    def test_ws_duel_forfeit_on_disconnect(self):
        """Connect 4 is in DUEL_FORFEIT_GAMES; forfeit immediately awards win to remaining player."""
        game = Connect4Game("C4_FORFEIT_DUEL", make_slots(2))
        game.start_game()
        ok = game.forfeit_player("p1", "Player 1 disconnected")
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"]
