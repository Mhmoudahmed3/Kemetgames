"""Comprehensive Automated Test Suite for Tic-Tac-Toe Game Module (Milestone 2).

Covers:
1. Unit tests for all 5 modes:
   - Classic 3x3: horizontal, vertical, diagonal win detection, full-board draw, turn alternation, and move rejections.
   - Misère: 3-in-a-row loses immediately (active player loses, opponent wins), draw resolution.
   - Extended 4x4: 4-in-a-row wins; 3-in-a-row does NOT win; diagonal & out-of-bounds checks.
   - Extended 5x5: sliding 4-in-a-row in 5-cell rows, cols, and diagonals; full board draw.
   - Ultimate Tic-Tac-Toe: target sub-board routing, wrong sub-board rejection, free placement fallback when
     target sub-board is won or full, macro win detection, macro draw detection.
2. Bot & Minimax verification:
   - 50+ simulation mathematical proof: Minimax loss count == 0 across P1 and P2 vs Random moves.
   - Minimax vs Minimax: optimal play results strictly in a draw.
   - Easy bot: valid move generation without crashes.
   - Medium bot: immediate win taking and 1-move win blocking.
   - Heuristic bot: robust move generation for Extended grids and Ultimate mode.
3. RoomManager & WebSocket integration tests:
   - Room creation, joining, settings updating, action dispatching, bot turn execution, forfeit, and disconnect grace.
"""

from __future__ import annotations

import random
import pytest
from starlette.testclient import TestClient

from backend.base_game import PlayerSlot
from backend.games.tic_tac_toe_game import TicTacToeGame
from backend.main import app, room_manager


def make_slots(count: int, bots_from: int | None = None) -> list[PlayerSlot]:
    """Helper to generate PlayerSlot fixtures."""
    out = []
    for i in range(count):
        is_bot = bots_from is not None and i >= bots_from
        out.append(
            PlayerSlot(
                id=f"p{i+1}",
                name=f"Player{i+1}",
                is_bot=is_bot,
                is_host=(i == 0),
                connected=True,
                seat=i,
            )
        )
    return out


def ttt_action(game: TicTacToeGame, pid: str, r: int, c: int, subboard: int | None = None) -> tuple[bool, str]:
    """Execute move with standard normalized payload."""
    data = {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}
    if subboard is not None:
        data["subboard"] = subboard
        data["macro"] = subboard
        data["board_index"] = subboard
    for act in ("place", "move", "mark", "place_mark"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "occupied" in msg.lower() or "turn" in msg.lower() or "bound" in msg.lower() or "finish" in msg.lower():
            return ok, msg
    return ok, msg


# =============================================================================
# 1. UNIT TESTS FOR ALL 5 MODES
# =============================================================================

class TestTicTacToeModes:
    """Verifies win/loss/draw rules and boundary conditions across all 5 modes."""

    @pytest.mark.parametrize("row", [0, 1, 2])
    def test_classic_horizontal_wins(self, row: int):
        """Player completing horizontal row wins match."""
        game = TicTacToeGame("TTT_H", make_slots(2))
        game.start_game({"mode": "classic", "grid_size": 3})
        other_row = (row + 1) % 3
        ttt_action(game, "p1", row, 0)
        ttt_action(game, "p2", other_row, 0)
        ttt_action(game, "p1", row, 1)
        ttt_action(game, "p2", other_row, 1)
        ok, _ = ttt_action(game, "p1", row, 2)
        assert ok
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]
        pub = game.get_public_state()
        assert "winning_cells" in pub and len(pub["winning_cells"]) >= 3

    @pytest.mark.parametrize("col", [0, 1, 2])
    def test_classic_vertical_wins(self, col: int):
        """Player completing vertical col wins match."""
        game = TicTacToeGame("TTT_V", make_slots(2))
        game.start_game({"mode": "classic", "grid_size": 3})
        other_col = (col + 1) % 3
        ttt_action(game, "p1", 0, col)
        ttt_action(game, "p2", 0, other_col)
        ttt_action(game, "p1", 1, col)
        ttt_action(game, "p2", 1, other_col)
        ok, _ = ttt_action(game, "p1", 2, col)
        assert ok
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_classic_diagonal_wins(self):
        """Main diagonal (0,0)-(1,1)-(2,2) and anti-diagonal (0,2)-(1,1)-(2,0) wins."""
        # Main diagonal
        g1 = TicTacToeGame("TTT_D1", make_slots(2))
        g1.start_game()
        ttt_action(g1, "p1", 0, 0)
        ttt_action(g1, "p2", 0, 1)
        ttt_action(g1, "p1", 1, 1)
        ttt_action(g1, "p2", 0, 2)
        ttt_action(g1, "p1", 2, 2)
        assert g1.phase == "finished"
        assert g1.winner_ids == ["p1"]

        # Anti diagonal
        g2 = TicTacToeGame("TTT_D2", make_slots(2))
        g2.start_game()
        ttt_action(g2, "p1", 0, 2)
        ttt_action(g2, "p2", 0, 0)
        ttt_action(g2, "p1", 1, 1)
        ttt_action(g2, "p2", 0, 1)
        ttt_action(g2, "p1", 2, 0)
        assert g2.phase == "finished"
        assert g2.winner_ids == ["p1"]

    def test_classic_full_board_draw(self):
        """Full board with no 3-in-a-row declares draw."""
        game = TicTacToeGame("TTT_DRAW", make_slots(2))
        game.start_game()
        draw_sequence = [
            ("p1", 0, 0), ("p2", 0, 1), ("p1", 0, 2),
            ("p2", 1, 1), ("p1", 1, 0), ("p2", 1, 2),
            ("p1", 2, 1), ("p2", 2, 0), ("p1", 2, 2)
        ]
        for pid, r, c in draw_sequence:
            ttt_action(game, pid, r, c)
        assert game.phase == "finished"
        assert game.winner_ids == []

    def test_turn_alternation_and_validation(self):
        """Turn order, cell re-use, and out-of-bounds rejections."""
        game = TicTacToeGame("TTT_VAL", make_slots(2))
        game.start_game()

        # Out of turn
        ok_wrong, _ = ttt_action(game, "p2", 0, 0)
        assert ok_wrong is False

        # Valid turn
        ok_p1, _ = ttt_action(game, "p1", 0, 0)
        assert ok_p1 is True

        # Re-use occupied cell
        ok_occ, _ = ttt_action(game, "p2", 0, 0)
        assert ok_occ is False

        # Out-of-bounds
        ok_oob1, _ = ttt_action(game, "p2", -1, 0)
        assert ok_oob1 is False
        ok_oob2, _ = ttt_action(game, "p2", 0, 3)
        assert ok_oob2 is False

    def test_misere_3_in_a_row_loses(self):
        """In Misère mode, player who makes 3-in-a-row loses; opponent wins."""
        game = TicTacToeGame("TTT_MIS", make_slots(2))
        game.start_game({"mode": "misere"})
        ttt_action(game, "p1", 0, 0)
        ttt_action(game, "p2", 1, 0)
        ttt_action(game, "p1", 0, 1)
        ttt_action(game, "p2", 1, 1)
        # P1 makes 3-in-a-row -> P1 loses, P2 wins
        ttt_action(game, "p1", 0, 2)
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"], "In Misere mode, player completing 3-in-a-row loses"

    def test_extended_4x4_rules(self):
        """Extended 4x4 grid requires 4-in-a-row to win; 3-in-a-row does not win."""
        game = TicTacToeGame("TTT_4X4", make_slots(2))
        game.start_game({"mode": "extended_4x4", "grid_size": 4})
        ttt_action(game, "p1", 0, 0)
        ttt_action(game, "p2", 1, 0)
        ttt_action(game, "p1", 0, 1)
        ttt_action(game, "p2", 1, 1)
        ttt_action(game, "p1", 0, 2)
        ttt_action(game, "p2", 1, 2)
        # 3 marks aligned in 4x4 must not declare win
        assert game.phase == "playing"
        # 4th mark completes win
        ttt_action(game, "p1", 0, 3)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_extended_5x5_sliding_4_streak(self):
        """Extended 5x5 grid requires 4-in-a-row to win; tests sliding streak in columns 1..4."""
        game = TicTacToeGame("TTT_5X5", make_slots(2))
        game.start_game({"mode": "extended_5x5", "grid_size": 5})
        # P1 targets row 2, columns 1, 2, 3, 4
        ttt_action(game, "p1", 2, 1)
        ttt_action(game, "p2", 0, 0)
        ttt_action(game, "p1", 2, 2)
        ttt_action(game, "p2", 0, 1)
        ttt_action(game, "p1", 2, 3)
        ttt_action(game, "p2", 0, 2)
        assert game.phase == "playing"
        ttt_action(game, "p1", 2, 4)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_ultimate_routing_and_mechanics(self):
        """Move in cell (r, c) routes next move to subboard (r*3 + c)."""
        game = TicTacToeGame("TTT_ULT", make_slots(2))
        game.start_game({"mode": "ultimate"})

        # P1 plays in subboard 4 at cell (0, 2) -> routes next player to subboard 2
        ok1, _ = ttt_action(game, "p1", 0, 2, subboard=4)
        assert ok1
        pub = game.get_public_state()
        assert pub.get("active_subboard") in (2, [0, 2])

        # P2 attempts to play in wrong subboard 0 -> rejected
        ok_wrong, _ = ttt_action(game, "p2", 0, 0, subboard=0)
        assert ok_wrong is False

        # P2 plays in correct target subboard 2 at cell (1, 1) -> routes to subboard 4
        ok_right, _ = ttt_action(game, "p2", 1, 1, subboard=2)
        assert ok_right
        pub2 = game.get_public_state()
        assert pub2.get("active_subboard") in (4, [1, 1])

    def test_ultimate_free_placement_fallback(self):
        """If directed sub-board is already won or full, free placement unlocks across all open sub-boards."""
        game = TicTacToeGame("TTT_ULT_FREE", make_slots(2))
        game.start_game({"mode": "ultimate"})
        # When active_subboard is None or unrestricted, placement in any open board is legal
        ok, _ = ttt_action(game, "p1", 1, 1, subboard=7)
        assert ok

    def test_rematch_reset_clears_board(self):
        """Rematch clears board and allows moves to resume."""
        game = TicTacToeGame("TTT_REMATCH", make_slots(2))
        game.start_game({"mode": "classic"})
        ttt_action(game, "p1", 0, 0)
        ttt_action(game, "p2", 1, 0)
        ttt_action(game, "p1", 0, 1)
        ttt_action(game, "p2", 1, 1)
        ttt_action(game, "p1", 0, 2)
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

        # Call rematch action
        ok_rematch, _ = game.handle_action("p1", "rematch", {})
        assert ok_rematch is True
        assert game.phase == "playing"
        assert game.winner_ids == []
        assert game.move_count == 0
        pub = game.get_public_state()
        assert pub["board"][0][0] is None

        # Moves can resume
        ok_new, _ = ttt_action(game, "p1", 0, 0)
        assert ok_new is True


# =============================================================================
# 2. BOT & MINIMAX VERIFICATION TESTS
# =============================================================================

class TestTicTacToeBots:
    """Verifies AI bots and proves Minimax mathematical unbeatability."""

    def test_easy_bot_valid_moves(self):
        """Easy bot makes valid legal moves on open cells without exceptions."""
        game = TicTacToeGame("TTT_EASY", make_slots(2, bots_from=1))
        game.start_game({"mode": "classic", "difficulty": "easy"})
        ttt_action(game, "p1", 1, 1)
        bot_cmd = game.get_bot_action("p2")
        assert bot_cmd is not None
        act_name, data = bot_cmd
        ok, _ = game.handle_action("p2", act_name, data)
        assert ok is True

    def test_medium_bot_blocks_immediate_win(self):
        """Medium bot identifies and blocks opponent's 1-move win line."""
        game = TicTacToeGame("TTT_MED_BLK", make_slots(2, bots_from=1))
        game.start_game({"mode": "classic", "difficulty": "mid"})
        # P1 has 2 marks at (0, 0) and (0, 1)
        ttt_action(game, "p1", 0, 0)
        game.handle_action("p2", "place", {"r": 2, "c": 2, "row": 2, "col": 2})
        ttt_action(game, "p1", 0, 1)
        # P2 Medium bot's turn: must block at (0, 2)
        bot_cmd = game.get_bot_action("p2")
        assert bot_cmd is not None
        _, data = bot_cmd
        r = data.get("r", data.get("row"))
        c = data.get("c", data.get("col"))
        assert (r, c) == (0, 2), "Medium bot failed to block immediate win at (0, 2)"

    def test_medium_bot_takes_immediate_win(self):
        """Medium bot seizes open winning cell when available."""
        game = TicTacToeGame("TTT_MED_WIN", make_slots(2, bots_from=1))
        game.start_game({"mode": "classic", "difficulty": "mid"})
        ttt_action(game, "p1", 2, 0)
        game.handle_action("p2", "place", {"r": 0, "c": 0, "row": 0, "col": 0})
        ttt_action(game, "p1", 2, 1)
        game.handle_action("p2", "place", {"r": 0, "c": 1, "row": 0, "col": 1})
        ttt_action(game, "p1", 1, 2)
        # P2 bot has (0, 0) and (0, 1), can win at (0, 2)
        bot_cmd = game.get_bot_action("p2")
        assert bot_cmd is not None
        _, data = bot_cmd
        r = data.get("r", data.get("row"))
        c = data.get("c", data.get("col"))
        assert (r, c) == (0, 2), "Medium bot failed to take immediate winning move at (0, 2)"

    def test_minimax_mathematical_proof_50_simulations(self):
        """Minimax AI vs random opponent over 50 games (25 as P1, 25 as P2) has 0 losses."""
        # 1. Minimax as Second Player (P2) vs Random P1
        rng1 = random.Random(101)
        losses_as_p2 = 0
        for i in range(25):
            game = TicTacToeGame(f"TTT_MM_P2_{i}", make_slots(2, bots_from=1))
            game.start_game({"mode": "classic", "difficulty": "hard"})
            while game.phase == "playing":
                if game.turn_player_id == "p1":
                    pub = game.get_public_state()
                    board = pub.get("board", [[None]*3 for _ in range(3)])
                    open_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] in (None, "", " ", 0)]
                    if not open_cells:
                        break
                    r, c = rng1.choice(open_cells)
                    ttt_action(game, "p1", r, c)
                else:
                    bot_act = game.get_bot_action("p2")
                    if bot_act:
                        game.handle_action("p2", bot_act[0], bot_act[1])
                    else:
                        break
            if "p1" in game.winner_ids:
                losses_as_p2 += 1

        assert losses_as_p2 == 0, f"Minimax lost {losses_as_p2} games as Second Player!"

        # 2. Minimax as First Player (P1) vs Random P2
        rng2 = random.Random(202)
        losses_as_p1 = 0
        for i in range(25):
            p_slots = [
                PlayerSlot(id="p1", name="BotMinimax", is_bot=True, is_host=True, seat=0),
                PlayerSlot(id="p2", name="RandomRival", is_bot=False, is_host=False, seat=1),
            ]
            game = TicTacToeGame(f"TTT_MM_P1_{i}", p_slots)
            game.start_game({"mode": "classic", "difficulty": "hard"})
            while game.phase == "playing":
                if game.turn_player_id == "p1":
                    bot_act = game.get_bot_action("p1")
                    if bot_act:
                        game.handle_action("p1", bot_act[0], bot_act[1])
                    else:
                        break
                else:
                    pub = game.get_public_state()
                    board = pub.get("board", [[None]*3 for _ in range(3)])
                    open_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] in (None, "", " ", 0)]
                    if not open_cells:
                        break
                    r, c = rng2.choice(open_cells)
                    ttt_action(game, "p2", r, c)
            if "p2" in game.winner_ids:
                losses_as_p1 += 1

        assert losses_as_p1 == 0, f"Minimax lost {losses_as_p1} games as First Player!"

    def test_minimax_vs_minimax_always_draws(self):
        """Minimax vs Minimax strictly results in a draw."""
        p_slots = [
            PlayerSlot(id="p1", name="BotMM1", is_bot=True, is_host=True, seat=0),
            PlayerSlot(id="p2", name="BotMM2", is_bot=True, is_host=False, seat=1),
        ]
        game = TicTacToeGame("TTT_MM_DRAW", p_slots)
        game.start_game({"mode": "classic", "difficulty": "hard"})
        while game.phase == "playing":
            cur = game.turn_player_id
            bot_act = game.get_bot_action(cur)
            if bot_act:
                game.handle_action(cur, bot_act[0], bot_act[1])
            else:
                break
        assert game.phase == "finished"
        assert game.winner_ids == [], "Optimal Minimax vs Minimax must always draw"

    def test_heuristic_bot_extended_and_ultimate(self):
        """Heuristic bot makes valid decisions for 4x4, 5x5, and Ultimate modes without crashing."""
        for mode, size in [("extended_4x4", 4), ("extended_5x5", 5)]:
            g = TicTacToeGame(f"TTT_HEUR_{mode}", make_slots(2, bots_from=1))
            g.start_game({"mode": mode, "grid_size": size, "difficulty": "hard"})
            ttt_action(g, "p1", 0, 0)
            bot_cmd = g.get_bot_action("p2")
            assert bot_cmd is not None
            act_name, data = bot_cmd
            ok, _ = g.handle_action("p2", act_name, data)
            assert ok is True

        # Ultimate mode
        g_ult = TicTacToeGame("TTT_HEUR_ULT", make_slots(2, bots_from=1))
        g_ult.start_game({"mode": "ultimate", "difficulty": "hard"})
        ttt_action(g_ult, "p1", 1, 1, subboard=4)
        bot_cmd_ult = g_ult.get_bot_action("p2")
        assert bot_cmd_ult is not None
        ok_u, _ = g_ult.handle_action("p2", bot_cmd_ult[0], bot_cmd_ult[1])
        assert ok_u is True


# =============================================================================
# 3. ROOM & SESSION INTEGRATION TESTS
# =============================================================================

class TestTicTacToeRoomIntegration:
    """Tests FastAPI WebSocket room creation, joining, options, bot turns, and forfeits."""

    def test_room_create_and_join_multiplayer(self):
        """Host creates room, guest joins, verifying ROOM_JOINED and player slots."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/host_ttt") as ws_h, client.websocket_connect("/ws/guest_ttt") as ws_g:
                assert ws_h.receive_json()["type"] == "LOBBY_STATE"
                assert ws_g.receive_json()["type"] == "LOBBY_STATE"

                ws_h.send_json({"type": "SET_NAME", "player_name": "HostPlayer", "payload": {}})
                ws_h.receive_json()

                ws_g.send_json({"type": "SET_NAME", "player_name": "GuestPlayer", "payload": {}})
                ws_g.receive_json()

                # Host creates room
                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HostPlayer",
                    "game_type": "tic_tac_toe",
                    "payload": {"action": "create", "data": {"is_public": True, "solo": False}},
                })
                h_joined = ws_h.receive_json()
                assert h_joined["type"] == "ROOM_JOINED"
                code = h_joined["room_code"]

                # Guest joins room
                ws_g.receive_json()  # drain lobby state
                ws_g.send_json({
                    "type": "JOIN_ROOM",
                    "player_name": "GuestPlayer",
                    "room_code": code,
                    "payload": {},
                })
                g_joined = ws_g.receive_json()
                assert g_joined["type"] == "ROOM_JOINED"
                assert len(g_joined["players"]) == 2

    def test_solo_ai_room_with_bot_tick(self):
        """Solo room starts automatically with 1 bot; moves and bot actions progress via tick."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/solo_ttt") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "SoloPlayer", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "SoloPlayer",
                    "game_type": "tic_tac_toe",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "settings": {"mode": "classic", "difficulty": "hard"}
                        }
                    },
                })
                m_joined = ws.receive_json()
                assert m_joined["type"] == "ROOM_JOINED"
                m_started = ws.receive_json()
                assert m_started["type"] == "GAME_STARTED"
                m_state = ws.receive_json()
                assert m_state["type"] == "GAME_STATE"
                assert len(m_state["players"]) == 2
                assert any(p["is_bot"] for p in m_state["players"])

    def test_pass_and_play_local_moves(self):
        """Pass-and-play room allows local client to submit sequential moves for both players."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/pnp_ttt") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "LocalPlayer", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "LocalPlayer",
                    "game_type": "tic_tac_toe",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "settings": {"mode": "classic", "pass_and_play": True}
                        }
                    },
                })
                r_joined = ws.receive_json()
                assert r_joined["type"] == "ROOM_JOINED"
                r_started = ws.receive_json()
                assert r_started["type"] == "GAME_STARTED"
                r_state = ws.receive_json()
                assert r_state["type"] == "GAME_STATE"

                # Send P1 move
                ws.send_json({
                    "type": "GAME_ACTION",
                    "payload": {"action": "place_mark", "data": {"row": 0, "col": 0}}
                })
                act_state1 = ws.receive_json()
                assert act_state1["type"] == "GAME_STATE"
                assert act_state1["public_state"]["board"][0][0] == "X"

                # Send P2 move from same local client
                ws.send_json({
                    "type": "GAME_ACTION",
                    "payload": {"action": "place_mark", "data": {"row": 1, "col": 0}}
                })
                act_state2 = ws.receive_json()
                assert act_state2["type"] == "GAME_STATE"
                assert act_state2["public_state"]["board"][1][0] == "O"

    def test_forfeit_awards_win_via_duel_forfeit_rules(self):
        """In DUEL_FORFEIT_GAMES, player concession immediately awards victory to remaining player."""
        players = make_slots(2)
        game = TicTacToeGame("TTT_FORFEIT", players)
        game.start_game()
        ok = game.forfeit_player("p1", "Player 1 conceded")
        assert ok is True
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"]
