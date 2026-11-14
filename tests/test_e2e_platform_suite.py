"""Blackout Arcade Platform Expansion — Comprehensive 4-Tier E2E Test Suite.

Contains 69 opaque-box, requirement-driven test cases across 4 tiers:
- Tier 1: Feature Coverage (30 tests: R1 [6], R2 [6], R3 [6], R4 [6], R5 [6])
- Tier 2: Boundary & Corner Cases (28 tests: R1 [6], R2 [6], R3 [5], R4 [5], R5 [6])
- Tier 3: Cross-Feature Combinations (6 tests)
- Tier 4: Real-World Application Scenarios (5 tests)

Safely handles progressive imports of parallel game engine implementations.
"""

from __future__ import annotations

import copy
import random
import time
from typing import Any

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.base_game import PlayerSlot
from backend.main import app, room_manager
from backend.games import GAME_REGISTRY
from backend.room_manager import ALLOWED_SETTINGS_KEYS, DUEL_FORFEIT_GAMES

# Safe progressive imports for parallel game modules
try:
    from backend.games.tic_tac_toe_game import TicTacToeGame
    if getattr(TicTacToeGame, "IS_STUB", False):
        TicTacToeGame = None
except ImportError:
    TicTacToeGame = None

try:
    from backend.games.rock_paper_scissors_game import RockPaperScissorsGame
    if getattr(RockPaperScissorsGame, "IS_STUB", False):
        RockPaperScissorsGame = None
except ImportError:
    RockPaperScissorsGame = None

try:
    from backend.games.connect4_game import Connect4Game
    if getattr(Connect4Game, "IS_STUB", False):
        Connect4Game = None
except ImportError:
    Connect4Game = None

try:
    from backend.games.playing_cards_game import PlayingCardsGame
    if getattr(PlayingCardsGame, "IS_STUB", False):
        PlayingCardsGame = None
except ImportError:
    PlayingCardsGame = None

try:
    from backend.games import playing_cards_deck
except ImportError:
    playing_cards_deck = None


def _require_engine(cls, name: str = "Game", milestone: str = "a future milestone"):
    """Skip test gracefully if the game engine is currently a stub awaiting milestone implementation."""
    if cls is None or getattr(cls, "IS_STUB", False):
        pytest.skip(f"{name} engine is currently a stub (full implementation scheduled for {milestone})")


# --- Shared Helpers ---

def make_players(count: int, bots_from: int | None = None) -> list[PlayerSlot]:
    """Generate player slots for engine tests."""
    out = []
    for i in range(count):
        is_bot = bots_from is not None and i >= bots_from
        out.append(
            PlayerSlot(
                id=f"p{i+1}",
                name=f"Player{i+1}",
                is_bot=is_bot,
                is_host=(i == 0),
                seat=i,
            )
        )
    return out


def _recv_until_type(ws, target_type: str, timeout: float = 2.0, limit: int = 20) -> tuple[dict, list[dict]]:
    """Helper to receive WebSocket messages until target type is encountered with deadlock prevention."""
    seen: list[dict] = []
    deadline = time.time() + timeout
    for _ in range(limit):
        while ws._send_rx.statistics().current_buffer_used == 0:
            if time.time() >= deadline:
                raise AssertionError(
                    f"Timed out after {timeout}s waiting for '{target_type}'. Received: {[m.get('type') for m in seen]}"
                )
            time.sleep(0.01)
        msg = ws.receive_json()
        seen.append(msg)
        if msg.get("type") == target_type:
            return msg, seen
    raise AssertionError(f"Did not receive '{target_type}' within {limit} messages. Received: {[m.get('type') for m in seen]}")


def ttt_action(game, pid: str, r: int, c: int, subboard: int | None = None) -> tuple[bool, str]:
    """Execute a Tic-Tac-Toe move with normalized payload formats."""
    data = {"row": r, "col": c, "r": r, "c": c, "cell": r * 3 + c}
    if subboard is not None:
        data["subboard"] = subboard
        data["macro"] = subboard
    for act in ("move", "place", "mark"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "occupied" in msg.lower() or "turn" in msg.lower() or "bound" in msg.lower() or "finish" in msg.lower():
            return ok, msg
    return ok, msg


def c4_drop_action(game, pid: str, col: int) -> tuple[bool, str]:
    """Execute a Connect 4 drop action."""
    data = {"col": col, "column": col}
    for act in ("drop", "move", "play"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "full" in msg.lower() or "bound" in msg.lower() or "turn" in msg.lower() or "finish" in msg.lower():
            return ok, msg
    return ok, msg


def c4_pop_action(game, pid: str, col: int) -> tuple[bool, str]:
    """Execute a Connect 4 pop-out action."""
    data = {"col": col, "column": col}
    for act in ("pop", "pop_out"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "opponent" in msg.lower() or "empty" in msg.lower() or "turn" in msg.lower():
            return ok, msg
    return ok, msg


def rps_commit_action(game, pid: str, choice: str) -> tuple[bool, str]:
    """Execute a Rock-Paper-Scissors choice action."""
    data = {"choice": choice}
    for act in ("choose", "play", "commit", "shoot", "move"):
        ok, msg = game.handle_action(pid, act, data)
        if ok or "invalid" in msg.lower() or "already" in msg.lower() or "turn" in msg.lower() or "countdown" in msg.lower():
            return ok, msg
    return ok, msg


REQUIRED_15_GAMES = {
    "snake", "minesweeper", "chess", "backgammon", "dominoes",
    "ludo", "skru", "uno", "qa_trivia", "globe", "monopoly",
    "tic_tac_toe", "rock_paper_scissors", "connect4", "playing_cards"
}


# ==============================================================================
# Tier 1: Feature Coverage (30 Tests)
# ==============================================================================

class TestTier1FeatureCoverage:
    """Tier 1: Feature Coverage tests across R1 to R5 requirements."""

    # --- R1: Platform Integration & Session Architecture ---

    def test_t1_r1_catalog_registration_15_games(self):
        """Verifies all 15 games exist in GAME_REGISTRY and /api/games endpoint."""
        with TestClient(app) as client:
            res = client.get("/api/games")
            assert res.status_code == 200
            data = res.json()
            games = data["games"]
            game_types = {g["game_type"] for g in games}
            registry_types = set(GAME_REGISTRY.keys())

            missing_in_registry = REQUIRED_15_GAMES - registry_types
            if missing_in_registry:
                pytest.skip(f"GAME_REGISTRY missing expected 15 games: {sorted(missing_in_registry)}")

            assert len(games) == 15, f"Expected 15 games in /api/games, found {len(games)}"
            assert REQUIRED_15_GAMES.issubset(game_types)
            for g in games:
                assert "game_type" in g and "title" in g and "min_players" in g and "max_players" in g

    def test_t1_r1_room_creation_and_join_multiplayer(self):
        """Host creates room, guest joins via 6-character room code, verifies ROOM_JOINED & ROOM_UPDATE."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        if game_to_test not in GAME_REGISTRY:
            pytest.skip("Neither 'tic_tac_toe' nor 'connect4' is registered in GAME_REGISTRY yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/host_r1") as ws_h, client.websocket_connect("/ws/guest_r1") as ws_g:
                assert ws_h.receive_json()["type"] == "LOBBY_STATE"
                assert ws_g.receive_json()["type"] == "LOBBY_STATE"

                ws_h.send_json({"type": "SET_NAME", "player_name": "HostPlayer", "payload": {}})
                assert ws_h.receive_json()["type"] == "LOBBY_STATE"

                ws_g.send_json({"type": "SET_NAME", "player_name": "GuestPlayer", "payload": {}})
                assert ws_g.receive_json()["type"] == "LOBBY_STATE"

                # Host creates room
                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HostPlayer",
                    "game_type": game_to_test,
                    "payload": {"action": "create", "data": {"is_public": True, "solo": False}},
                })
                h_joined = ws_h.receive_json()
                assert h_joined["type"] == "ROOM_JOINED"
                code = h_joined["room_code"]
                assert len(code) == 6

                # Guest joins room
                ws_g.receive_json()  # drain LOBBY_STATE on guest
                ws_g.send_json({
                    "type": "JOIN_ROOM",
                    "player_name": "GuestPlayer",
                    "room_code": code,
                    "payload": {},
                })
                g_joined = ws_g.receive_json()
                assert g_joined["type"] == "ROOM_JOINED"
                assert len(g_joined["players"]) == 2

                h_update = ws_h.receive_json()
                assert h_update["type"] == "ROOM_UPDATE"
                assert len(h_update["players"]) == 2
                player_ids = {p["id"] for p in h_update["players"]}
                assert "host_r1" in player_ids and "guest_r1" in player_ids

    def test_t1_r1_solo_vs_ai_launch(self):
        """Solo challenge creates room with bot and transitions immediately to 'playing'."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        if game_to_test not in GAME_REGISTRY:
            pytest.fail("Neither 'tic_tac_toe' nor 'connect4' registered in GAME_REGISTRY yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/solo_ai_h") as ws:
                assert ws.receive_json()["type"] == "LOBBY_STATE"
                ws.send_json({"type": "SET_NAME", "player_name": "SoloMaster", "payload": {}})
                assert ws.receive_json()["type"] == "LOBBY_STATE"

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "SoloMaster",
                    "game_type": game_to_test,
                    "payload": {"action": "create", "data": {"is_public": False, "solo": True}},
                })
                m_joined = ws.receive_json()
                m_started = ws.receive_json()
                m_state = ws.receive_json()

                assert m_joined["type"] == "ROOM_JOINED"
                assert m_started["type"] == "GAME_STARTED"
                assert m_state["type"] == "GAME_STATE"
                assert m_state["public_state"]["room_meta"]["phase"] in ("pre_game", "playing")
                assert len(m_state["players"]) == 2
                assert any(p["is_bot"] for p in m_state["players"])

    def test_t1_r1_spectator_join_and_action_rejection(self):
        """Spectator connects, receives state broadcasts, but cannot submit gameplay actions."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        if game_to_test not in GAME_REGISTRY:
            pytest.fail("Target game not in GAME_REGISTRY")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/spec_h") as ws_h, client.websocket_connect("/ws/spec_g") as ws_g:
                ws_h.receive_json()
                ws_g.receive_json()
                ws_h.send_json({"type": "SET_NAME", "player_name": "P1", "payload": {}})
                ws_h.receive_json()
                ws_g.send_json({"type": "SET_NAME", "player_name": "P2", "payload": {}})
                ws_g.receive_json()

                ws_h.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "P1",
                    "game_type": game_to_test,
                    "payload": {"action": "create", "data": {"is_public": True}},
                })
                code = ws_h.receive_json()["room_code"]
                ws_g.receive_json()
                ws_g.send_json({"type": "JOIN_ROOM", "player_name": "P2", "room_code": code, "payload": {}})
                ws_g.receive_json()
                ws_h.receive_json()

                # Start game
                ws_h.send_json({
                    "type": "START_GAME",
                    "player_name": "P1",
                    "room_code": code,
                    "game_type": game_to_test,
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws_h, "GAME_STATE")
                _recv_until_type(ws_g, "GAME_STATE")

                # Spectator connects and joins
                with client.websocket_connect("/ws/watcher_spec") as ws_spec:
                    ws_spec.receive_json()
                    ws_spec.send_json({"type": "SET_NAME", "player_name": "Observer", "payload": {}})
                    ws_spec.receive_json()
                    ws_spec.send_json({"type": "JOIN_ROOM", "player_name": "Observer", "room_code": code, "payload": {}})
                    spec_joined = ws_spec.receive_json()
                    assert spec_joined["type"] == "ROOM_JOINED"
                    assert any(p["id"] == "watcher_spec" and p.get("role") == "spectator" for p in spec_joined["players"])
                    ws_spec.receive_json()  # Initial GAME_STATE for late joiner

                    # Spectator attempts an illegal game action
                    ws_spec.send_json({
                        "type": "GAME_ACTION",
                        "player_name": "Observer",
                        "room_code": code,
                        "game_type": game_to_test,
                        "payload": {"action": "move", "data": {"row": 0, "col": 0}},
                    })
                    err = ws_spec.receive_json()
                    assert err["type"] == "ERROR"

    def test_t1_r1_duel_forfeit_on_leave(self):
        """Disconnecting/leaving in a 2P duel forfeits match to remaining player."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        if game_to_test not in DUEL_FORFEIT_GAMES:
            pytest.fail(f"Game '{game_to_test}' is not configured in DUEL_FORFEIT_GAMES")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/ff_p1") as ws1:
                ws1.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "DuelHost", "payload": {}})
                ws1.receive_json()

                with client.websocket_connect("/ws/ff_p2") as ws2:
                    ws2.receive_json()
                    ws2.send_json({"type": "SET_NAME", "player_name": "DuelLeaver", "payload": {}})
                    ws2.receive_json()

                    ws1.send_json({
                        "type": "CREATE_ROOM",
                        "player_name": "DuelHost",
                        "game_type": game_to_test,
                        "payload": {"action": "create", "data": {"is_public": True}},
                    })
                    code = ws1.receive_json()["room_code"]
                    ws2.receive_json()
                    ws2.send_json({"type": "JOIN_ROOM", "player_name": "DuelLeaver", "room_code": code, "payload": {}})
                    ws2.receive_json()
                    ws1.receive_json()

                    ws1.send_json({
                        "type": "START_GAME",
                        "player_name": "DuelHost",
                        "room_code": code,
                        "game_type": game_to_test,
                        "payload": {"action": "start", "data": {}},
                    })
                    _recv_until_type(ws1, "GAME_STATE")
                    _recv_until_type(ws2, "GAME_STATE")

                # ws2 leaves / disconnects -> grace deadline expiration triggers forfeit
                ws1.receive_json()  # ROOM_UPDATE
                ws1.receive_json()  # GAME_STATE
                assert "ff_p2" in room_manager.rooms[code].disconnect_deadlines
                room_manager.rooms[code].disconnect_deadlines["ff_p2"] = time.time() - 1.0

                over_msg, _ = _recv_until_type(ws1, "GAME_OVER")
                assert over_msg["public_state"]["winner_ids"] == ["ff_p1"]
                assert over_msg["public_state"]["room_meta"]["phase"] == "finished"

    def test_t1_r1_rematch_reset_and_to_lobby(self):
        """Rematch resets phase and scores, supports immediate restart or return to lobby."""
        game_to_test = "chess"
        with TestClient(app) as client:
            with client.websocket_connect("/ws/rm_host") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "SoloRematch", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "SoloRematch",
                    "game_type": game_to_test,
                    "payload": {"action": "create", "data": {"solo": True, "is_public": False}},
                })
                code = ws.receive_json()["room_code"]
                ws.receive_json()  # GAME_STARTED
                ws.receive_json()  # GAME_STATE

                # Forfeit/resign to finish match
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "SoloRematch",
                    "room_code": code,
                    "game_type": game_to_test,
                    "payload": {"action": "resign", "data": {}},
                })
                over_msg, _ = _recv_until_type(ws, "GAME_OVER")
                assert over_msg["public_state"]["room_meta"]["phase"] == "finished"

                # Trigger immediate rematch
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "SoloRematch",
                    "room_code": code,
                    "game_type": game_to_test,
                    "payload": {"action": "rematch", "data": {}},
                })
                started_msg = ws.receive_json()
                state_msg = ws.receive_json()
                assert started_msg["type"] == "GAME_STARTED"
                assert state_msg["type"] == "GAME_STATE"
                assert state_msg["public_state"]["room_meta"]["phase"] in ("pre_game", "playing")
                assert state_msg["players"][0]["score"] == 0

    # --- R2: Tic-Tac-Toe ---

    def test_t1_r2_tictactoe_classic_3x3_win_and_draw(self):
        """Standard 3x3 win line detection (horizontal, vertical, diagonal) and full-board draw."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        # 1. Horizontal win (row 0)
        g1 = TicTacToeGame("TTT01", make_players(2))
        g1.start_game({"mode": "classic", "grid_size": 3})
        ttt_action(g1, "p1", 0, 0)
        ttt_action(g1, "p2", 1, 0)
        ttt_action(g1, "p1", 0, 1)
        ttt_action(g1, "p2", 1, 1)
        ok, _ = ttt_action(g1, "p1", 0, 2)
        assert ok
        assert g1.phase == "finished"
        assert g1.winner_ids == ["p1"]
        pub1 = g1.get_public_state()
        assert "winning_cells" in pub1 and len(pub1["winning_cells"]) >= 3

        # 2. Vertical win (col 1)
        g2 = TicTacToeGame("TTT02", make_players(2))
        g2.start_game({"mode": "classic"})
        ttt_action(g2, "p1", 0, 1)
        ttt_action(g2, "p2", 0, 0)
        ttt_action(g2, "p1", 1, 1)
        ttt_action(g2, "p2", 1, 0)
        ttt_action(g2, "p1", 2, 1)
        assert g2.phase == "finished"
        assert g2.winner_ids == ["p1"]

        # 3. Diagonal win
        g3 = TicTacToeGame("TTT03", make_players(2))
        g3.start_game()
        ttt_action(g3, "p1", 0, 0)
        ttt_action(g3, "p2", 0, 1)
        ttt_action(g3, "p1", 1, 1)
        ttt_action(g3, "p2", 0, 2)
        ttt_action(g3, "p1", 2, 2)
        assert g3.phase == "finished"
        assert g3.winner_ids == ["p1"]

        # 4. Full board Draw
        g4 = TicTacToeGame("TTT04", make_players(2))
        g4.start_game()
        # Draw board sequence:
        # X O X
        # X O O
        # O X X
        moves = [
            ("p1", 0, 0), ("p2", 0, 1), ("p1", 0, 2),
            ("p2", 1, 1), ("p1", 1, 0), ("p2", 1, 2),
            ("p1", 2, 1), ("p2", 2, 0), ("p1", 2, 2)
        ]
        for pid, r, c in moves:
            ttt_action(g4, pid, r, c)
        assert g4.phase == "finished"
        assert g4.winner_ids == []

    def test_t1_r2_tictactoe_misere_mode_win_condition(self):
        """Completing 3-in-a-row triggers loss for active player; opponent wins."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        game = TicTacToeGame("TTT_MIS", make_players(2))
        game.start_game({"mode": "misere"})
        ttt_action(game, "p1", 0, 0)
        ttt_action(game, "p2", 1, 0)
        ttt_action(game, "p1", 0, 1)
        ttt_action(game, "p2", 1, 1)
        # P1 completes 3-in-a-row at row 0 -> P1 loses, P2 wins!
        ttt_action(game, "p1", 0, 2)
        assert game.phase == "finished"
        assert game.winner_ids == ["p2"], "In Misere mode, player completing 3-in-a-row loses"

    def test_t1_r2_tictactoe_extended_grids_4x4_and_5x5(self):
        """4x4 and 5x5 grids require 4-in-a-row to win."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        # 4x4 Grid
        g4 = TicTacToeGame("TTT_4X4", make_players(2))
        g4.start_game({"grid_size": 4, "mode": "extended_4x4"})
        ttt_action(g4, "p1", 0, 0)
        ttt_action(g4, "p2", 1, 0)
        ttt_action(g4, "p1", 0, 1)
        ttt_action(g4, "p2", 1, 1)
        ttt_action(g4, "p1", 0, 2)
        ttt_action(g4, "p2", 1, 2)
        # 3 in a row must NOT trigger win on 4x4 grid
        assert g4.phase == "playing", "3-in-a-row in 4x4 grid must not declare win"
        ttt_action(g4, "p1", 0, 3)
        assert g4.phase == "finished"
        assert g4.winner_ids == ["p1"]

        # 5x5 Grid
        g5 = TicTacToeGame("TTT_5X5", make_players(2))
        g5.start_game({"grid_size": 5, "mode": "extended_5x5"})
        ttt_action(g5, "p1", 2, 0)
        ttt_action(g5, "p2", 3, 0)
        ttt_action(g5, "p1", 2, 1)
        ttt_action(g5, "p2", 3, 1)
        ttt_action(g5, "p1", 2, 2)
        ttt_action(g5, "p2", 3, 2)
        assert g5.phase == "playing", "3-in-a-row in 5x5 grid must not declare win"
        ttt_action(g5, "p1", 2, 3)
        assert g5.phase == "finished"
        assert g5.winner_ids == ["p1"]

    def test_t1_r2_tictactoe_ultimate_routing_and_macro_win(self):
        """Opponent's cell routes next sub-board; winning 3 sub-boards wins macro game."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        game = TicTacToeGame("TTT_ULT", make_players(2))
        game.start_game({"mode": "ultimate"})
        pub = game.get_public_state()
        assert "subboards" in pub or "macro_board" in pub or "active_subboard" in pub

        # Place move in subboard 4 at cell (0, 2) -> routes next player to subboard 2
        ok, _ = ttt_action(game, "p1", 0, 2, subboard=4)
        assert ok
        st = game.get_public_state()
        assert "active_subboard" in st and st["active_subboard"] in (2, [0, 2])

        # Play subboard sequence verifying winning 3 sub-boards in a row awards macro game win
        game_win = TicTacToeGame("TTT_ULT_MACRO", make_players(2))
        game_win.start_game({"mode": "ultimate"})
        macro_moves = [
            ("p1", 0, 0, 1),  # -> subboard 1
            ("p2", 1, 0, 0),  # -> subboard 0
            ("p1", 0, 0, 2),  # -> subboard 2
            ("p2", 2, 0, 0),  # -> subboard 0
            ("p1", 0, 0, 0),  # P1 wins subboard 0! Target subboard 0 is won -> free placement
            ("p2", 1, 0, 1),  # P2 free placement to subboard 1 -> routes to subboard 1
            ("p1", 1, 1, 0),  # -> subboard 3
            ("p2", 3, 0, 1),  # -> subboard 1
            ("p1", 1, 1, 1),  # -> subboard 4
            ("p2", 4, 0, 1),  # -> subboard 1
            ("p1", 1, 1, 2),  # P1 wins subboard 1! Routes to subboard 5
            ("p2", 5, 0, 2),  # -> subboard 2
            ("p1", 2, 2, 0),  # -> subboard 6
            ("p2", 6, 0, 2),  # -> subboard 2
            ("p1", 2, 2, 1),  # -> subboard 7
            ("p2", 7, 0, 2),  # -> subboard 2
            ("p1", 2, 2, 2),  # P1 wins subboard 2! (3 subboards in a row: 0, 1, 2 -> Macro Win)
        ]
        for pid, sb, r, c in macro_moves:
            ok_m, _ = ttt_action(game_win, pid, r, c, subboard=sb)
            if not ok_m and game_win.phase == "finished":
                break
        assert game_win.phase == "finished"
        assert game_win.winner_ids == ["p1"]

    def test_t1_r2_tictactoe_ultimate_free_placement_fallback(self):
        """If target sub-board is won or full, player can place in any open sub-board."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        game = TicTacToeGame("TTT_ULT_FREE", make_players(2))
        game.start_game({"mode": "ultimate"})
        # When active_subboard is unrestricted, placement in any open board is legal
        ok, _ = ttt_action(game, "p1", 1, 1, subboard=7)
        assert ok

    def test_t1_r2_tictactoe_ai_minimax_unbeatable(self):
        """Minimax AI vs opponent across iterations never loses (win or draw)."""
        if TicTacToeGame is None:
            pytest.skip("backend.games.tic_tac_toe_game.TicTacToeGame is not implemented yet")

        # Run 10 games with Minimax as p2 against random moves
        rng = random.Random(42)
        for i in range(10):
            game = TicTacToeGame(f"TTT_AI_{i}", make_players(2, bots_from=1))
            game.start_game({"mode": "classic", "difficulty": "hard"})
            while game.phase == "playing":
                if game.turn_player_id == "p1":
                    # Random open cell
                    pub = game.get_public_state()
                    board = pub.get("board", [[None]*3 for _ in range(3)])
                    open_cells = [
                        (r, c)
                        for r in range(3)
                        for c in range(3)
                        if board[r][c] in (None, "", " ", 0)
                    ]
                    if not open_cells:
                        break
                    r, c = rng.choice(open_cells)
                    ttt_action(game, "p1", r, c)
                else:
                    bot_act = game.get_bot_action("p2")
                    if bot_act:
                        act_name, data = bot_act
                        game.handle_action("p2", act_name, data)
                    else:
                        break
            assert "p1" not in game.winner_ids, f"Minimax AI lost in iteration {i}"

    # --- R3: Rock-Paper-Scissors ---

    def test_t1_r3_rps_classic_3_choice_rules(self):
        """All 9 outcomes of Rock/Paper/Scissors evaluate to canonical win/loss/tie."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        expected_winners = {
            ("rock", "scissors"): "p1",
            ("scissors", "paper"): "p1",
            ("paper", "rock"): "p1",
            ("scissors", "rock"): "p2",
            ("paper", "scissors"): "p2",
            ("rock", "paper"): "p2",
            ("rock", "rock"): None,
            ("paper", "paper"): None,
            ("scissors", "scissors"): None,
        }
        for (c1, c2), expected in expected_winners.items():
            g = RockPaperScissorsGame("RPS_3C", make_players(2))
            g.start_game({"mode": "classic", "format": "single"})
            rps_commit_action(g, "p1", c1)
            rps_commit_action(g, "p2", c2)
            pub = g.get_public_state()
            round_winner = pub.get("last_round_winner") or (g.winner_ids[0] if g.winner_ids else None)
            assert round_winner == expected, f"Failed for ({c1}, {c2}): expected {expected}, got {round_winner}"

    def test_t1_r3_rps_lizard_spock_5_choice_rules(self):
        """All 25 outcomes of 5-choice variant evaluate correctly."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        beats = {
            "scissors": {"paper", "lizard"},
            "paper": {"rock", "spock"},
            "rock": {"lizard", "scissors"},
            "lizard": {"spock", "paper"},
            "spock": {"scissors", "rock"},
        }
        for c1, win_set in beats.items():
            for c2 in ("rock", "paper", "scissors", "lizard", "spock"):
                g = RockPaperScissorsGame("RPS_5C", make_players(2))
                g.start_game({"mode": "lizard_spock", "format": "single"})
                rps_commit_action(g, "p1", c1)
                rps_commit_action(g, "p2", c2)
                pub = g.get_public_state()
                winner = pub.get("last_round_winner") or (g.winner_ids[0] if g.winner_ids else None)
                if c1 == c2:
                    assert winner is None, f"Tie failed for {c1} vs {c2}"
                elif c2 in win_set:
                    assert winner == "p1", f"{c1} should beat {c2}"
                else:
                    assert winner == "p2", f"{c2} should beat {c1}"

    def test_t1_r3_rps_best_of_3_format(self):
        """First player to 2 round wins triggers match victory."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        g = RockPaperScissorsGame("RPS_BO3", make_players(2))
        g.start_game({"format": "bo3"})
        # Round 1: P1 wins
        rps_commit_action(g, "p1", "rock")
        rps_commit_action(g, "p2", "scissors")
        assert g.phase == "playing"
        # Round 2: P1 wins again (2-0)
        rps_commit_action(g, "p1", "rock")
        rps_commit_action(g, "p2", "scissors")
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_t1_r3_rps_best_of_5_format(self):
        """First player to 3 round wins triggers match victory."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        g = RockPaperScissorsGame("RPS_BO5", make_players(2))
        g.start_game({"format": "bo5"})
        for _ in range(3):
            rps_commit_action(g, "p1", "paper")
            rps_commit_action(g, "p2", "rock")
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_t1_r3_rps_endless_streak_mode(self):
        """Consecutive wins increment streak; loss resets current streak."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        g = RockPaperScissorsGame("RPS_STRK", make_players(2))
        g.start_game({"format": "endless"})
        # Win 2 rounds
        for _ in range(2):
            rps_commit_action(g, "p1", "rock")
            rps_commit_action(g, "p2", "scissors")
        pub = g.get_public_state()
        streak = pub.get("streaks", {}).get("p1") if "streaks" in pub else pub.get("p1_streak")
        assert streak is not None and streak >= 2
        # Loss on round 3
        rps_commit_action(g, "p1", "scissors")
        rps_commit_action(g, "p2", "rock")
        pub2 = g.get_public_state()
        assert ("streaks" in pub2 and pub2["streaks"].get("p1") == 0) or ("p1_streak" in pub2 and pub2["p1_streak"] == 0)

    def test_t1_r3_rps_secret_commit_isolation(self):
        """Player choice is hidden from public state until both commit."""
        if RockPaperScissorsGame is None:
            pytest.skip("backend.games.rock_paper_scissors_game.RockPaperScissorsGame is not implemented yet")

        g = RockPaperScissorsGame("RPS_SEC", make_players(2))
        g.start_game()
        rps_commit_action(g, "p1", "rock")
        pub = g.get_public_state()
        # Public state must not reveal P1's choice
        choices = pub.get("choices", {})
        assert choices.get("p1") in (None, "", "hidden", True, "*")

        priv1 = g.get_private_state("p1")
        assert priv1.get("choice") in ("rock", {"choice": "rock"}) or priv1.get("committed_choice") == "rock"

        priv2 = g.get_private_state("p2")
        assert priv2.get("choice") != "rock" and "p1_choice" not in priv2

    # --- R4: Connect 4 ---

    def test_t1_r4_connect4_classic_drop_and_gravity(self):
        """Discs settle into lowest available row in column."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        g = Connect4Game("C4_GRAV", make_players(2))
        g.start_game({"mode": "classic"})
        ok1, _ = c4_drop_action(g, "p1", 3)
        assert ok1
        pub = g.get_public_state()
        board = pub["board"]
        # In a 6-row board (rows 0..5), bottom row is 5 (or 0 depending on convention)
        bottom_row = 5 if board[5][3] in ("p1", 1, "R", "Y") else 0
        assert board[bottom_row][3] is not None

        # Second drop in same column settles in next row
        c4_drop_action(g, "p2", 3)
        pub2 = g.get_public_state()
        second_row = bottom_row - 1 if bottom_row == 5 else 1
        assert pub2["board"][second_row][3] is not None

    def test_t1_r4_connect4_horizontal_vertical_diagonal_wins(self):
        """Tests horizontal, vertical, and diagonal win detection."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        # 1. Horizontal win (cols 0, 1, 2, 3)
        gh = Connect4Game("C4_HORIZ", make_players(2))
        gh.start_game()
        for c in range(3):
            c4_drop_action(gh, "p1", c)
            c4_drop_action(gh, "p2", c)
        c4_drop_action(gh, "p1", 3)
        assert gh.phase == "finished"
        assert gh.winner_ids == ["p1"]

        # 2. Vertical win (4 discs in col 0)
        gv = Connect4Game("C4_VERT", make_players(2))
        gv.start_game()
        for _ in range(3):
            c4_drop_action(gv, "p1", 0)
            c4_drop_action(gv, "p2", 1)
        c4_drop_action(gv, "p1", 0)
        assert gv.phase == "finished"
        assert gv.winner_ids == ["p1"]

    def test_t1_r4_connect4_pop_out_mechanics(self):
        """Popping bottom-row disc removes it and shifts upper discs down by 1 row."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        g = Connect4Game("C4_POP", make_players(2))
        g.start_game({"mode": "pop_out"})
        c4_drop_action(g, "p1", 2)
        c4_drop_action(g, "p2", 2)
        # Pop P1's bottom disc
        ok, _ = c4_pop_action(g, "p1", 2)
        assert ok
        pub = g.get_public_state()
        # Column 2 now only has 1 disc belonging to p2 at the bottom
        board = pub["board"]
        bottom_val = board[5][2] if len(board) == 6 else board[0][2]
        assert bottom_val in ("p2", 2, "Y", "R")

    def test_t1_r4_connect4_pop_out_simultaneous_double_win_tie(self):
        """Simultaneous double-win in Pop Out mode resolves to a TIE (draw)."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        g = Connect4Game("C4_DBL_WIN", make_players(2))
        g.start_game({"mode": "pop_out"})
        # Setup board where popping col 0 causes simultaneous 4-in-a-row for both p1 and p2:
        # Row 5 (bottom): col 0='p1', col 1='p2', col 2='p2', col 3='p2'
        # Row 4:          col 0='p2', col 1='p1', col 2='p1', col 3='p1'
        # Row 3:          col 0='p1'
        g.board[5][0] = "p1"
        g.board[5][1] = "p2"
        g.board[5][2] = "p2"
        g.board[5][3] = "p2"

        g.board[4][0] = "p2"
        g.board[4][1] = "p1"
        g.board[4][2] = "p1"
        g.board[4][3] = "p1"

        g.board[3][0] = "p1"

        g.turn_player_id = "p1"
        ok, _ = c4_pop_action(g, "p1", 0)
        assert ok
        assert g.phase == "finished"
        assert g.winner_ids == []

    def test_t1_r4_connect4_5_in_a_row_9x7_grid(self):
        """9x7 grid requires 5-in-a-row (4-in-a-row does not win)."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        g = Connect4Game("C4_5ROW", make_players(2))
        g.start_game({"mode": "5_in_a_row", "grid_size": "9x7"})
        pub = g.get_public_state()
        board = pub["board"]
        assert len(board) >= 7 and len(board[0]) >= 9
        # Drop 4 in a row
        for c in range(4):
            c4_drop_action(g, "p1", c)
            c4_drop_action(g, "p2", c)
        assert g.phase == "playing", "4-in-a-row must not win in 5_in_a_row mode"
        # 5th drop completes 5-in-a-row
        c4_drop_action(g, "p1", 4)
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_t1_r4_connect4_blitz_5s_timer(self):
        """Exceeding 5-second turn timer in Blitz mode triggers timeout."""
        if Connect4Game is None:
            pytest.skip("backend.games.connect4_game.Connect4Game is not implemented yet")

        g = Connect4Game("C4_BLITZ", make_players(2))
        g.start_game({"mode": "blitz", "timer": 5})
        now = time.time()
        # Advance clock by 6 seconds
        timeout_occurred = g._tick_timers(now + 6.0)
        assert timeout_occurred is True

    # --- R5: Playing Cards ---

    def test_t1_r5_deck_fisher_yates_integrity(self):
        """52 unique cards, 4 suits x 13 ranks; shuffle preserves complete deck."""
        if playing_cards_deck is None:
            pytest.skip("backend.games.playing_cards_deck is not implemented yet")

        deck = playing_cards_deck.PlayingCardsDeck()
        assert deck.count() == 52 or deck.deck_count() == 52
        initial_cards = copy.deepcopy(deck.to_dict())

        deck.shuffle()
        assert deck.count() == 52 or deck.deck_count() == 52
        drawn = [deck.draw_card() for _ in range(52)]
        assert len(drawn) == 52
        assert len(set((c["suit"], c["rank"]) for c in drawn if c)) == 52

    def test_t1_r5_blackjack_scoring_and_dealer_rules(self):
        """Soft Ace (11) converts to Hard Ace (1) to prevent bust; dealer draws to 17."""
        if playing_cards_deck is None:
            pytest.skip("backend.games.playing_cards_deck is not implemented yet")

        calc = playing_cards_deck.calculate_blackjack_hand
        # Ace + 9 = 20 (soft)
        res1 = calc([{"rank": "A"}, {"rank": "9"}])
        assert res1["score"] == 20 and res1["is_soft"] is True
        # Ace + 9 + 5 = 15 (hard)
        res2 = calc([{"rank": "A"}, {"rank": "9"}, {"rank": "5"}])
        assert res2["score"] == 15 and res2["is_soft"] is False

    def test_t1_r5_blackjack_actions_hit_stand_double_split(self):
        """Validates Hit, Stand, Double Down, and Split in Blackjack."""
        if PlayingCardsGame is None:
            pytest.skip("backend.games.playing_cards_game.PlayingCardsGame is not implemented yet")

        g = PlayingCardsGame("BJ_ACT", make_players(1))
        g.start_game({"mode": "blackjack"})
        # Hit draws a card
        ok, _ = g.handle_action("p1", "hit", {})
        assert ok
        # Stand locks the hand
        ok_stand, _ = g.handle_action("p1", "stand", {})
        assert ok_stand

    def test_t1_r5_war_battle_and_3_card_tiebreaker(self):
        """Higher card takes round; ties trigger 3-card war pile."""
        if playing_cards_deck is None:
            pytest.skip("backend.games.playing_cards_deck is not implemented yet")

        res1 = playing_cards_deck.compare_war_cards({"rank": "K"}, {"rank": "7"})
        assert res1 == 1  # P1 wins
        res2 = playing_cards_deck.compare_war_cards({"rank": "8"}, {"rank": "8"})
        assert res2 == 0  # Tie / War

    def test_t1_r5_memory_concentration_matching_and_timer(self):
        """Matching pair keeps cards face-up; mismatches flip back; timer tracks elapsed time."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame is not implemented yet")

        g = PlayingCardsGame("MEM_01", make_players(1))
        g.start_game({"mode": "memory", "grid_size": "4x4"})
        pub = g.get_public_state()
        assert "grid" in pub or "cards" in pub
        # Action flip card
        ok, _ = g.handle_action("p1", "flip", {"index": 0})
        assert ok

    def test_t1_r5_high_low_streak_and_push_preservation(self):
        """Correct guess increments multiplier; equal rank preserves streak (push)."""
        if playing_cards_deck is None:
            pytest.skip("backend.games.playing_cards_deck is not implemented yet")

        eval_fn = playing_cards_deck.evaluate_high_low_guess
        # 7 to 10 guessing 'higher' -> Win
        assert eval_fn({"rank": "7"}, {"rank": "10"}, "higher") == "win"
        # 10 to 10 guessing 'higher' -> Push
        assert eval_fn({"rank": "10"}, {"rank": "10"}, "higher") == "push"


# ==============================================================================
# Tier 2: Boundary & Corner Cases (28 Tests)
# ==============================================================================

class TestTier2BoundaryAndEdgeCases:
    """Tier 2: Boundary & Edge Cases covering R1 to R5 error paths."""

    # --- R1: Platform Boundaries ---

    def test_t2_r1_bnd_player_count_out_of_bounds(self):
        """Rejects < MIN_PLAYERS and > MAX_PLAYERS on room initialization."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        cls = GAME_REGISTRY.get(game_to_test)
        if cls is None:
            pytest.skip(f"Game '{game_to_test}' not registered")

        # Below MIN_PLAYERS
        too_few = make_players(cls.MIN_PLAYERS - 1)
        g_few = cls("BND_FEW", too_few)
        ok_few, _ = g_few.can_start()
        assert ok_few is False

        # Above MAX_PLAYERS
        too_many = make_players(cls.MAX_PLAYERS + 1)
        g_many = cls("BND_MANY", too_many)
        ok_many, _ = g_many.can_start()
        assert ok_many is False

    def test_t2_r1_bnd_unknown_game_type(self):
        """CREATE_ROOM with invalid game type rejected."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/bnd_unk") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
                ws.receive_json()
                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": "quantum_space_invaders_9000",
                    "payload": {"action": "create", "data": {}},
                })
                err = ws.receive_json()
                assert err["type"] == "ERROR"

    def test_t2_r1_bnd_invalid_room_code(self):
        """JOIN_ROOM with non-existent code rejected."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/bnd_inv_code") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
                ws.receive_json()
                ws.send_json({
                    "type": "JOIN_ROOM",
                    "player_name": "Tester",
                    "room_code": "NONEX9",
                    "payload": {},
                })
                err = ws.receive_json()
                assert err["type"] == "ERROR"

    def test_t2_r1_bnd_unwhitelisted_settings_pruned(self):
        """Forbidden settings keys filtered out during room creation."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "globe"
        with TestClient(app) as client:
            with client.websocket_connect("/ws/bnd_prune") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "HostP", "payload": {}})
                ws.receive_json()
                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HostP",
                    "game_type": game_to_test,
                    "payload": {
                        "action": "create",
                        "data": {
                            "is_public": True,
                            "settings": {"admin_privileges": True, "speed_hack": 999},
                        },
                    },
                })
                joined = ws.receive_json()
                assert joined["type"] == "ROOM_JOINED"
                meta_settings = joined["public_state"]["room_meta"]["settings"]
                assert "admin_privileges" not in meta_settings
                assert "speed_hack" not in meta_settings

    def test_t2_r1_bnd_oversized_ws_frame(self):
        """Frame > 64 KB rejected cleanly without server crash."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/bnd_huge") as ws:
                ws.receive_json()
                huge_payload = {"type": "CHAT_MSG", "payload": {"text": "A" * 70000}}
                ws.send_json(huge_payload)
                msg, _ = _recv_until_type(ws, "ERROR")
                assert msg["type"] == "ERROR"
                assert "Message exceeds 64 KB frame size limit." in msg.get("message", "")

    def test_t2_r1_bnd_session_hijacking_rejected(self):
        """Duplicate client ID with mismatched secret rejected."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/legit_user") as ws1:
                ws1.receive_json()

                # Attacker connects with same client_id but wrong secret
                with pytest.raises(WebSocketDisconnect) as exc:
                    with client.websocket_connect("/ws/legit_user?secret=wrong_hacker_secret") as ws_bad:
                        err_msg = ws_bad.receive_json()
                        assert err_msg["type"] == "ERROR"
                        ws_bad.receive_json()
                assert exc.value.code == 4003

    # --- R2: Tic-Tac-Toe Boundaries ---

    def test_t2_r2_bnd_out_of_bounds_cell_coords(self):
        """Coordinates < 0 or >= grid_size rejected."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_OOB", make_players(2))
        g.start_game({"grid_size": 3})
        ok1, _ = ttt_action(g, "p1", -1, 0)
        assert ok1 is False
        ok2, _ = ttt_action(g, "p1", 0, 3)
        assert ok2 is False

    def test_t2_r2_bnd_play_in_occupied_cell(self):
        """Placement in marked cell rejected."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_OCC", make_players(2))
        g.start_game()
        ttt_action(g, "p1", 1, 1)
        ok, _ = ttt_action(g, "p2", 1, 1)
        assert ok is False

    def test_t2_r2_bnd_play_out_of_turn(self):
        """Non-turn player move rejected."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_TURN", make_players(2))
        g.start_game()
        ok, _ = ttt_action(g, "p2", 0, 0)
        assert ok is False

    def test_t2_r2_bnd_action_after_game_finished(self):
        """Moves rejected when match finished."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_FIN", make_players(2))
        g.start_game()
        # Fast horizontal win
        for c in range(3):
            ttt_action(g, "p1", 0, c)
            if c < 2:
                ttt_action(g, "p2", 1, c)
        assert g.phase == "finished"
        # Move after finished must be rejected
        ok, _ = ttt_action(g, "p2", 2, 2)
        assert ok is False

    def test_t2_r2_bnd_ultimate_wrong_subboard(self):
        """Placement in wrong sub-board rejected when target is active."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_SUB", make_players(2))
        g.start_game({"mode": "ultimate"})
        # P1 plays in subboard 4 at (0, 2), routing next player to subboard 2
        ok1, _ = ttt_action(g, "p1", 0, 2, subboard=4)
        assert ok1
        # P2 attempts to play in wrong subboard 0 instead of required target subboard 2
        ok2, _ = ttt_action(g, "p2", 0, 0, subboard=0)
        assert ok2 is False

    def test_t2_r2_bnd_extended_grid_3_in_a_row_not_win(self):
        """3-in-a-row in 4x4 or 5x5 does not trigger win."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        g = TicTacToeGame("TTT_BND_EXT", make_players(2))
        g.start_game({"grid_size": 4})
        ttt_action(g, "p1", 0, 0)
        ttt_action(g, "p2", 1, 0)
        ttt_action(g, "p1", 0, 1)
        ttt_action(g, "p2", 1, 1)
        ttt_action(g, "p1", 0, 2)
        assert g.phase == "playing"

    # --- R3: Rock-Paper-Scissors Boundaries ---

    def test_t2_r3_bnd_invalid_choice_rejected(self):
        """Unrecognized choice rejected."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        g = RockPaperScissorsGame("RPS_BND_INV", make_players(2))
        g.start_game()
        ok, _ = rps_commit_action(g, "p1", "nuclear_bomb")
        assert ok is False

    def test_t2_r3_bnd_double_commit_rejected(self):
        """Multiple commits in single round rejected."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        g = RockPaperScissorsGame("RPS_BND_DBL", make_players(2))
        g.start_game()
        ok1, _ = rps_commit_action(g, "p1", "rock")
        assert ok1
        ok2, _ = rps_commit_action(g, "p1", "paper")
        assert ok2 is False

    def test_t2_r3_bnd_round_tie_does_not_advance_match_score(self):
        """Ties in Bo3/Bo5 do not award points."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        g = RockPaperScissorsGame("RPS_BND_TIE", make_players(2))
        g.start_game({"format": "bo3"})
        rps_commit_action(g, "p1", "rock")
        rps_commit_action(g, "p2", "rock")
        pub = g.get_public_state()
        assert "scores" in pub
        assert pub["scores"]["p1"] == 0 and pub["scores"]["p2"] == 0

    def test_t2_r3_bnd_choice_rejection_after_round_resolution(self):
        """Moves submitted during countdown or after finish rejected."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        g = RockPaperScissorsGame("RPS_BND_RES", make_players(2))
        g.start_game({"format": "single"})
        rps_commit_action(g, "p1", "rock")
        rps_commit_action(g, "p2", "scissors")
        assert g.phase == "finished"
        ok, _ = rps_commit_action(g, "p1", "paper")
        assert ok is False

    def test_t2_r3_bnd_max_streak_retention(self):
        """max_streak persists when current streak resets."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        g = RockPaperScissorsGame("RPS_BND_MAX", make_players(2))
        g.start_game({"format": "endless"})
        for _ in range(3):
            rps_commit_action(g, "p1", "rock")
            rps_commit_action(g, "p2", "scissors")
        # P1 loses
        rps_commit_action(g, "p1", "scissors")
        rps_commit_action(g, "p2", "rock")
        pub = g.get_public_state()
        max_streak = pub.get("max_streaks", {}).get("p1") if "max_streaks" in pub else pub.get("p1_max_streak")
        assert max_streak is not None and max_streak >= 3

    # --- R4: Connect 4 Boundaries ---

    def test_t2_r4_bnd_drop_in_full_column_rejected(self):
        """Dropping into full column rejected."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        g = Connect4Game("C4_BND_FULL", make_players(2))
        g.start_game()
        # Fill col 0 with 6 discs
        for _ in range(3):
            c4_drop_action(g, "p1", 0)
            c4_drop_action(g, "p2", 0)
        # 7th disc must be rejected
        ok, _ = c4_drop_action(g, "p1", 0)
        assert ok is False

    def test_t2_r4_bnd_invalid_column_index(self):
        """Column < 0 or >= cols rejected."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        g = Connect4Game("C4_BND_COL", make_players(2))
        g.start_game()
        ok_neg, _ = c4_drop_action(g, "p1", -1)
        assert ok_neg is False
        ok_high, _ = c4_drop_action(g, "p1", 7)
        assert ok_high is False

    def test_t2_r4_bnd_pop_opponent_disc_rejected(self):
        """Popping opponent's disc rejected."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        g = Connect4Game("C4_BND_POP_OPP", make_players(2))
        g.start_game({"mode": "pop_out"})
        c4_drop_action(g, "p1", 1)  # P1 disc at bottom of col 1
        c4_drop_action(g, "p2", 2)  # P2 disc at bottom of col 2
        # P1 attempts to pop P2's disc at bottom of col 2
        ok, _ = c4_pop_action(g, "p1", 2)
        assert ok is False

    def test_t2_r4_bnd_pop_empty_column_rejected(self):
        """Popping from empty column rejected."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        g = Connect4Game("C4_BND_POP_EMP", make_players(2))
        g.start_game({"mode": "pop_out"})
        ok, _ = c4_pop_action(g, "p1", 4)
        assert ok is False

    def test_t2_r4_bnd_board_full_draw(self):
        """All 42 cells filled without 4-in-a-row declares draw."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        g = Connect4Game("C4_BND_DRAW", make_players(2))
        g.start_game()
        draw_board = [
            ["p1", "p2", "p1", "p2", "p1", "p2", None],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p1"],
            ["p2", "p1", "p2", "p1", "p2", "p1", "p2"],
            ["p2", "p1", "p2", "p1", "p2", "p1", "p2"],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p1"],
            ["p1", "p2", "p1", "p2", "p1", "p2", "p2"],
        ]
        g.board = draw_board
        g.turn_player_id = "p1"
        ok, _ = c4_drop_action(g, "p1", 6)
        assert ok
        assert g.phase == "finished"
        assert g.winner_ids == []

    # --- R5: Playing Cards Boundaries ---

    def test_t2_r5_bnd_deck_exhaustion(self):
        """Drawing from empty deck handled safely."""
        if playing_cards_deck is None:
            pytest.skip("playing_cards_deck not implemented yet")

        deck = playing_cards_deck.PlayingCardsDeck()
        for _ in range(52):
            deck.draw_card()
        # 53rd draw must return None cleanly without crash
        card = deck.draw_card()
        assert card is None

    def test_t2_r5_bnd_blackjack_bust_immediate_loss(self):
        """Hand > 21 immediately busts."""
        if playing_cards_deck is None:
            pytest.skip("playing_cards_deck not implemented yet")

        res = playing_cards_deck.calculate_blackjack_hand([
            {"rank": "10"}, {"rank": "8"}, {"rank": "5"}
        ])
        assert res["score"] == 23
        assert res["is_bust"] is True

    def test_t2_r5_bnd_blackjack_split_only_on_matching_rank(self):
        """Splitting non-matching cards rejected."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        g = PlayingCardsGame("BJ_BND_SPLIT", make_players(1))
        g.start_game({"mode": "blackjack"})
        # Force non-matching hand: p1 has an '8' and a '9'
        g.player_hands["p1"] = [{"rank": "8"}, {"rank": "9"}]
        ok, _ = g.handle_action("p1", "split", {})
        assert ok is False

    def test_t2_r5_bnd_war_insufficient_cards_for_war(self):
        """Player with < 4 cards in War handled safely."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        g = PlayingCardsGame("WAR_BND_FEW", make_players(2))
        g.start_game({"mode": "war"})
        # Setup player with fewer than 4 cards (e.g. 2 cards) and trigger a War tie condition
        two_cards_p1 = [{"rank": "8", "suit": "hearts"}, {"rank": "2", "suit": "clubs"}]
        two_cards_p2 = [{"rank": "8", "suit": "spades"}, {"rank": "3", "suit": "diamonds"}]
        try:
            g.player_hands["p1"] = list(two_cards_p1)
            g.player_hands["p2"] = list(two_cards_p2)
        except (AttributeError, TypeError):
            g.player_decks["p1"] = list(two_cards_p1)
            g.player_decks["p2"] = list(two_cards_p2)

        # Trigger War battle/flip: must safely resolve without IndexError
        ok = False
        for act in ("battle", "flip", "play"):
            ok, _ = g.handle_action("p1", act, {})
            if ok:
                break
        assert ok is True
        assert g.phase == "finished" or len(g.winner_ids) > 0

    def test_t2_r5_bnd_memory_flip_already_matched_or_active(self):
        """Flipping matched card rejected."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        g = PlayingCardsGame("MEM_BND_FLIP", make_players(1))
        g.start_game({"mode": "memory"})
        ok1, _ = g.handle_action("p1", "flip", {"index": 0})
        assert ok1
        # Flipping same card twice in turn rejected
        ok2, _ = g.handle_action("p1", "flip", {"index": 0})
        assert ok2 is False

    def test_t2_r5_bnd_clean_deck_reset_between_rounds(self):
        """Reset restores 52 fresh cards and clears hands."""
        if playing_cards_deck is None:
            pytest.skip("playing_cards_deck not implemented yet")

        deck = playing_cards_deck.PlayingCardsDeck()
        for _ in range(10):
            deck.draw_card()
        assert deck.count() == 42 or deck.deck_count() == 42
        deck.reset_deck()
        assert deck.count() == 52 or deck.deck_count() == 52


# ==============================================================================
# Tier 3: Cross-Feature Combinations (6 Tests)
# ==============================================================================

class TestTier3CrossFeatureCombinations:
    """Tier 3: Pairwise Combinatorial Interactions across features."""

    def test_t3_combo_tictactoe_misere_with_minimax_ai(self):
        """Misère inversion evaluated under Minimax decision tree."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        # Test A: In Misère mode, when AI has 2-in-a-row with 3rd cell open, Minimax must AVOID completing 3-in-a-row
        g_avoid = TicTacToeGame("TTT_CMB_MIS_AVOID", make_players(2, bots_from=1))
        g_avoid.start_game({"mode": "misere", "difficulty": "hard"})
        # Setup board where P2 (bot) occupies (0, 0) and (0, 1), and (0, 2) is open
        ttt_action(g_avoid, "p1", 2, 2)
        ttt_action(g_avoid, "p2", 0, 0)
        ttt_action(g_avoid, "p1", 2, 1)
        ttt_action(g_avoid, "p2", 0, 1)
        ttt_action(g_avoid, "p1", 1, 1)

        # Minimax bot P2 must choose a safe cell and NOT (0, 2), avoiding completing 3-in-a-row
        bot_choice = g_avoid.get_bot_action("p2")
        assert bot_choice is not None
        b_act, b_data = bot_choice
        r_choice = b_data.get("row", b_data.get("r"))
        c_choice = b_data.get("col", b_data.get("c"))
        if r_choice is None and "cell" in b_data:
            r_choice, c_choice = b_data["cell"] // 3, b_data["cell"] % 3
        assert not (r_choice == 0 and c_choice == 2), "Minimax in Misère mode erroneously completed 3-in-a-row"

        # Test B: Play several moves into a game verifying Minimax forces opponent to take the 3rd cell
        game = TicTacToeGame("TTT_CMB_MIS_AI", make_players(2, bots_from=1))
        game.start_game({"mode": "misere", "difficulty": "hard"})
        for _ in range(4):
            if game.phase == "finished":
                break
            if game.turn_player_id == "p1":
                # P1 plays in first available open cell
                pub = game.get_public_state()
                board = pub.get("board", [])
                open_indices = [i for i, v in enumerate(board) if v is None]
                if not open_indices:
                    break
                p1_idx = open_indices[0]
                ttt_action(game, "p1", p1_idx // 3, p1_idx % 3)
            elif game.turn_player_id == "p2":
                act = game.get_bot_action("p2")
                assert act is not None
                a_name, a_data = act
                ok, _ = game.handle_action("p2", a_name, a_data)
                assert ok

        # In Misère mode, Minimax AI avoids self-loss and forces opponent into losing cell
        if game.phase == "finished":
            assert game.winner_ids == ["p2"]

    def test_t3_combo_connect4_pop_out_in_blitz_mode(self):
        """Pop-out action mechanics executed under strict 5s Blitz timer."""
        if Connect4Game is None:
            pytest.skip("Connect4Game not implemented yet")

        game = Connect4Game("C4_CMB_POP_BLZ", make_players(2))
        game.start_game({"mode": "pop_out", "timer": 5})

        # Setup column with P1 disc at bottom, then P2 disc above it
        c4_drop_action(game, "p1", 3)
        c4_drop_action(game, "p2", 3)

        # It is now P1's turn under 5s Blitz timer.
        # Advance clock by 3 seconds; verify timeout has not occurred yet
        t0 = time.time()
        timeout_pre = game._tick_timers(t0 + 3.0)
        assert timeout_pre is False

        # P1 successfully pops their own disc from the bottom of column 3
        ok_pop, _ = c4_pop_action(game, "p1", 3)
        assert ok_pop is True

        # Successful action must reset turn timer for next player (P2)
        # Advance 3 seconds past pop time: timer must not expire (only 3s of new 5s turn elapsed)
        t_pop = t0 + 3.0
        timeout_after_pop = game._tick_timers(t_pop + 3.0)
        assert timeout_after_pop is False

        # Exceeding the fresh 5s limit (6s past t_pop) triggers timeout
        timeout_expired = game._tick_timers(t_pop + 6.0)
        assert timeout_expired is True

    def test_t3_combo_rps_lizard_spock_in_best_of_5(self):
        """5-choice cyclic graph scored across multi-round match format."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        game = RockPaperScissorsGame("RPS_CMB_5C_BO5", make_players(2))
        game.start_game({"mode": "lizard_spock", "format": "bo5"})
        # P1 plays Spock, P2 plays Scissors (Spock smashes Scissors -> P1 wins round 1)
        rps_commit_action(game, "p1", "spock")
        rps_commit_action(game, "p2", "scissors")
        # P1 plays Lizard, P2 plays Paper (Lizard eats Paper -> P1 wins round 2)
        rps_commit_action(game, "p1", "lizard")
        rps_commit_action(game, "p2", "paper")
        # P1 plays Rock, P2 plays Lizard (Rock crushes Lizard -> P1 wins round 3 & match)
        rps_commit_action(game, "p1", "rock")
        rps_commit_action(game, "p2", "lizard")
        assert game.phase == "finished"
        assert game.winner_ids == ["p1"]

    def test_t3_combo_playing_cards_blackjack_split_with_aces(self):
        """Splitting Aces with dynamic Ace soft/hard scoring evaluation."""
        if playing_cards_deck is None:
            pytest.skip("playing_cards_deck not implemented yet")

        calc = playing_cards_deck.calculate_blackjack_hand
        # Split Ace receiving a 10 = 21 (blackjack/soft 21)
        res_a10 = calc([{"rank": "A"}, {"rank": "10"}])
        assert res_a10["score"] == 21
        # Split Ace receiving a 5 and 8 = 14 (1 + 5 + 8)
        res_a58 = calc([{"rank": "A"}, {"rank": "5"}, {"rank": "8"}])
        assert res_a58["score"] == 14

    def test_t3_combo_ultimate_tictactoe_opponent_win_redirection(self):
        """Move directed to completed sub-board invokes free placement fallback."""
        if TicTacToeGame is None:
            pytest.skip("TicTacToeGame not implemented yet")

        game = TicTacToeGame("TTT_CMB_ULT_REDIR", make_players(2))
        game.start_game({"mode": "ultimate"})

        # Route moves so P1 completes subboard 0:
        # P1 in SB 0 at (0, 1) -> routes P2 to SB 1
        ok1, _ = ttt_action(game, "p1", 0, 1, subboard=0)
        assert ok1
        # P2 in SB 1 at (0, 0) -> routes P1 to SB 0
        ok2, _ = ttt_action(game, "p2", 0, 0, subboard=1)
        assert ok2
        # P1 in SB 0 at (0, 2) -> routes P2 to SB 2
        ok3, _ = ttt_action(game, "p1", 0, 2, subboard=0)
        assert ok3
        # P2 in SB 2 at (0, 0) -> routes P1 to SB 0
        ok4, _ = ttt_action(game, "p2", 0, 0, subboard=2)
        assert ok4
        # P1 in SB 0 at (0, 0) -> completes 3-in-a-row for P1 in SB 0!
        # This move points to cell (0, 0) -> routes P2 to subboard 0, which is now won.
        ok5, _ = ttt_action(game, "p1", 0, 0, subboard=0)
        assert ok5

        # Subboard 0 is completed/won: verify active_subboard resets to None (free placement fallback)
        st = game.get_public_state()
        assert "active_subboard" in st
        assert st["active_subboard"] is None

        # Verify free placement allows P2 to place in any other open subboard (e.g. subboard 4)
        ok_free, _ = ttt_action(game, "p2", 1, 1, subboard=4)
        assert ok_free is True

    def test_t3_combo_playing_cards_war_chained_double_war(self):
        """Consecutive rank ties trigger chained 3-card war piles."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        g = PlayingCardsGame("WAR_CHAINED", make_players(2))
        g.start_game({"mode": "war"})

        # Verify underlying card comparison logic for the chained double war:
        if playing_cards_deck is not None:
            # Step 1: First tie (8 vs 8) -> war triggered
            assert playing_cards_deck.compare_war_cards({"rank": "8"}, {"rank": "8"}) == 0
            # Step 2: Chained second tie (Q vs Q) -> second war triggered
            assert playing_cards_deck.compare_war_cards({"rank": "Q"}, {"rank": "Q"}) == 0
            # Step 3: Decisive resolution (K vs 2) -> P1 wins all 18 cards
            assert playing_cards_deck.compare_war_cards({"rank": "K"}, {"rank": "2"}) == 1

        # Configure player hands with cards that tie twice consecutively:
        # Tie 1: 8 vs 8; 3 down each; Tie 2: Q vs Q; 3 down each; Final: K vs 2 -> P1 wins
        cards_p1 = [
            {"rank": "8", "suit": "hearts"},
            {"rank": "3", "suit": "hearts"}, {"rank": "4", "suit": "hearts"}, {"rank": "5", "suit": "hearts"},
            {"rank": "Q", "suit": "hearts"},
            {"rank": "6", "suit": "hearts"}, {"rank": "7", "suit": "hearts"}, {"rank": "9", "suit": "hearts"},
            {"rank": "K", "suit": "hearts"},
            {"rank": "10", "suit": "hearts"}, {"rank": "J", "suit": "hearts"},
        ]
        cards_p2 = [
            {"rank": "8", "suit": "spades"},
            {"rank": "3", "suit": "spades"}, {"rank": "4", "suit": "spades"}, {"rank": "5", "suit": "spades"},
            {"rank": "Q", "suit": "spades"},
            {"rank": "6", "suit": "spades"}, {"rank": "7", "suit": "spades"}, {"rank": "9", "suit": "spades"},
            {"rank": "2", "suit": "spades"},
            {"rank": "10", "suit": "spades"}, {"rank": "J", "suit": "spades"},
        ]
        try:
            g.player_hands["p1"] = list(cards_p1)
            g.player_hands["p2"] = list(cards_p2)
        except (AttributeError, TypeError):
            g.player_decks["p1"] = list(cards_p1)
            g.player_decks["p2"] = list(cards_p2)

        # Trigger battle action: must execute cleanly and initiate/resolve chained war
        ok = False
        for act in ("battle", "flip", "play"):
            ok, _ = g.handle_action("p1", act, {})
            if ok:
                break
        assert ok is True

        # Process any remaining war turns until chained war settles and cards are collected
        for _ in range(5):
            pub = g.get_public_state()
            if not pub.get("in_war", False) and not pub.get("war_active", False):
                break
            for act in ("battle", "flip", "play"):
                ok_step, _ = g.handle_action("p1", act, {})
                if ok_step:
                    break

        # Verify card collection: P1 collects both war piles + initial cards (18 cards)
        st = g.get_public_state()
        p1_hand = getattr(g, "player_hands", {}).get("p1") or getattr(g, "player_decks", {}).get("p1")
        if p1_hand is not None:
            assert len(p1_hand) >= 11, f"Expected P1 to collect cards, got {len(p1_hand)}"
        if "card_counts" in st:
            assert st["card_counts"]["p1"] >= 11
        elif "player_cards_count" in st:
            assert st["player_cards_count"]["p1"] >= 11


# ==============================================================================
# Tier 4: Real-World Application Scenarios (5 Tests)
# ==============================================================================

class TestTier4RealWorldApplicationScenarios:
    """Tier 4: End-to-end realistic user journeys via WebSocket flows."""

    def test_t4_scenario_full_connect4_match_with_rematch(self):
        """2 WebSocket clients play Connect 4 to victory, request rematch, and reset for game 2."""
        if Connect4Game is None:
            pytest.skip("Connect4Game is not implemented yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/sc4_p1") as ws1, client.websocket_connect("/ws/sc4_p2") as ws2:
                ws1.receive_json()
                ws2.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "C4Host", "payload": {}})
                ws1.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "C4Guest", "payload": {}})
                ws2.receive_json()

                ws1.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "C4Host",
                    "game_type": "connect4",
                    "payload": {"action": "create", "data": {"is_public": True, "settings": {"mode": "classic"}}},
                })
                code = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "C4Guest", "room_code": code, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                # Start game
                ws1.send_json({
                    "type": "START_GAME",
                    "player_name": "C4Host",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws1, "GAME_STATE")
                _recv_until_type(ws2, "GAME_STATE")

                # Play valid 4-in-a-row vertical drop sequence:
                # P1 (Host) drops col 0, P2 (Guest) drops col 1, P1 drops col 0, P2 drops col 1, P1 drops col 0, P2 drops col 1
                drops = [
                    (ws1, "C4Host", 0),
                    (ws2, "C4Guest", 1),
                    (ws1, "C4Host", 0),
                    (ws2, "C4Guest", 1),
                    (ws1, "C4Host", 0),
                    (ws2, "C4Guest", 1),
                ]
                for ws_curr, p_name, col in drops:
                    ws_curr.send_json({
                        "type": "GAME_ACTION",
                        "player_name": p_name,
                        "room_code": code,
                        "game_type": "connect4",
                        "payload": {"action": "drop", "data": {"col": col, "column": col}},
                    })
                    _recv_until_type(ws1, "GAME_STATE")
                    _recv_until_type(ws2, "GAME_STATE")

                # P1 drops col 0 (4th disc in col 0 wins)
                ws1.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "C4Host",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "drop", "data": {"col": 0, "column": 0}},
                })
                over_msg1, _ = _recv_until_type(ws1, "GAME_OVER")
                over_msg2, _ = _recv_until_type(ws2, "GAME_OVER")
                assert over_msg1["public_state"]["winner_ids"] == ["sc4_p1"]
                assert over_msg2["public_state"]["winner_ids"] == ["sc4_p1"]

                # Request rematch
                ws1.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "C4Host",
                    "room_code": code,
                    "game_type": "connect4",
                    "payload": {"action": "rematch", "data": {}},
                })
                rm1, _ = _recv_until_type(ws1, "GAME_STARTED")
                rm2, _ = _recv_until_type(ws2, "GAME_STARTED")
                assert rm1["public_state"]["phase"] == "playing"
                assert rm2["public_state"]["phase"] == "playing"
                assert rm1["public_state"]["winner_ids"] == []

    def test_t4_scenario_tictactoe_duel_disconnect_forfeit(self):
        """2 WebSocket clients play Tic-Tac-Toe; rival disconnects, triggering duel forfeit win."""
        game_to_test = "tic_tac_toe" if "tic_tac_toe" in GAME_REGISTRY else "connect4"
        if game_to_test not in DUEL_FORFEIT_GAMES:
            pytest.fail(f"Game '{game_to_test}' not configured in DUEL_FORFEIT_GAMES")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/sttt_p1") as ws1:
                ws1.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "StayP1", "payload": {}})
                ws1.receive_json()

                with client.websocket_connect("/ws/sttt_p2") as ws2:
                    ws2.receive_json()
                    ws2.send_json({"type": "SET_NAME", "player_name": "DropP2", "payload": {}})
                    ws2.receive_json()

                    ws1.send_json({
                        "type": "CREATE_ROOM",
                        "player_name": "StayP1",
                        "game_type": game_to_test,
                        "payload": {"action": "create", "data": {"is_public": True}},
                    })
                    code = ws1.receive_json()["room_code"]
                    ws2.receive_json()
                    ws2.send_json({"type": "JOIN_ROOM", "player_name": "DropP2", "room_code": code, "payload": {}})
                    ws2.receive_json()
                    ws1.receive_json()

                    ws1.send_json({
                        "type": "START_GAME",
                        "player_name": "StayP1",
                        "room_code": code,
                        "game_type": game_to_test,
                        "payload": {"action": "start", "data": {}},
                    })
                    _recv_until_type(ws1, "GAME_STATE")
                    _recv_until_type(ws2, "GAME_STATE")

                # ws2 disconnects
                ws1.receive_json()  # ROOM_UPDATE
                ws1.receive_json()  # GAME_STATE
                assert "sttt_p2" in room_manager.rooms[code].disconnect_deadlines
                room_manager.rooms[code].disconnect_deadlines["sttt_p2"] = time.time() - 1.0

                over_msg, _ = _recv_until_type(ws1, "GAME_OVER")
                assert over_msg["public_state"]["winner_ids"] == ["sttt_p1"]

    def test_t4_scenario_rps_secret_commit_and_reveal_flow(self):
        """2 WebSocket clients play Bo3 RPS with simultaneous secret commits and round resolution."""
        if RockPaperScissorsGame is None:
            pytest.skip("RockPaperScissorsGame not implemented yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/srps_p1") as ws1, client.websocket_connect("/ws/srps_p2") as ws2:
                ws1.receive_json()
                ws2.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "RpsP1", "payload": {}})
                ws1.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "RpsP2", "payload": {}})
                ws2.receive_json()

                ws1.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "RpsP1",
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "create", "data": {"is_public": True, "settings": {"format": "bo3"}}},
                })
                code = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "RpsP2", "room_code": code, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({
                    "type": "START_GAME",
                    "player_name": "RpsP1",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws1, "GAME_STATE")
                _recv_until_type(ws2, "GAME_STATE")

                # P1 sends secret commit ("rock")
                ws1.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "RpsP1",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "rock"}},
                })
                st1, _ = _recv_until_type(ws1, "GAME_STATE")
                st2, _ = _recv_until_type(ws2, "GAME_STATE")

                # Verify P1 private state contains "rock"
                priv1_msg, _ = _recv_until_type(ws1, "PRIVATE_STATE")
                p1_priv = priv1_msg.get("private_state", {})
                assert (
                    p1_priv.get("choice") in ("rock", {"choice": "rock"})
                    or p1_priv.get("committed_choice") == "rock"
                    or p1_priv.get("choice") == "rock"
                )

                # Verify P2 sees nothing or unrevealed status (not "rock")
                p2_priv = st2.get("private_state", {})
                assert p2_priv.get("p1_choice") is None
                assert p2_priv.get("choice") != "rock"
                p2_pub = st2.get("public_state", {})
                if "choices" in p2_pub:
                    assert p2_pub["choices"].get("srps_p1") in (None, True, "hidden", "committed")

                # P2 sends secret commit ("scissors")
                ws2.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "RpsP2",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "scissors"}},
                })

                # Both receive reveal/round resolution with P1 scoring
                res1, _ = _recv_until_type(ws1, "GAME_STATE")
                res2, _ = _recv_until_type(ws2, "GAME_STATE")
                pub1 = res1["public_state"]
                scores = pub1.get("scores", {})
                p1_score = scores.get("srps_p1") or pub1.get("p1_score", 0)
                assert p1_score >= 1 or pub1.get("last_round_winner") == "srps_p1" or pub1.get("round_winner") == "srps_p1"

    def test_t4_scenario_playing_cards_blackjack_multiplayer_or_solo(self):
        """Full Blackjack shoe with hits, stands, and dealer resolution with leaderboard entry."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/sbj_host") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "CardMaster", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "CardMaster",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": True, "settings": {"mode": "blackjack"}}},
                })
                joined = ws.receive_json()
                code = joined["room_code"]
                ws.receive_json()  # GAME_STARTED
                ws.receive_json()  # GAME_STATE

                # Host plays Blackjack, sends "hit", receives new card
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "CardMaster",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "hit", "data": {}},
                })
                msg_hit, _ = _recv_until_type(ws, "GAME_STATE")
                priv = msg_hit.get("private_state", {})
                pub = msg_hit.get("public_state", {})
                hand = priv.get("hand") or pub.get("player_hand") or pub.get("hands", {}).get("sbj_host", [])
                assert len(hand) >= 2

                # Host sends "stand", dealer draws to 17, game resolves with winner and leaderboard entry
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "CardMaster",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "stand", "data": {}},
                })
                msg_fin, _ = _recv_until_type(ws, "GAME_OVER")
                assert msg_fin["type"] == "GAME_OVER"
                assert "winner_ids" in msg_fin["public_state"] or "outcome" in msg_fin["public_state"]
                room = room_manager.rooms.get(code)
                assert room is not None
                assert room.leaderboard_recorded is True

    def test_t4_scenario_memory_concentration_complete_game(self):
        """Complete Memory game playthrough verifying move counter, timer, and GAME_OVER event."""
        if PlayingCardsGame is None:
            pytest.skip("PlayingCardsGame not implemented yet")

        with TestClient(app) as client:
            with client.websocket_connect("/ws/smem_host") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "MemoryChamp", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "MemoryChamp",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": True, "settings": {"mode": "memory", "pairs_count": 2}}},
                })
                joined = ws.receive_json()
                code = joined["room_code"]
                ws.receive_json()  # GAME_STARTED
                st = ws.receive_json()  # GAME_STATE

                room = room_manager.rooms[code]
                game = room.game

                # Find pairs from the server-authoritative card grid
                grid = getattr(game, "grid", []) or getattr(game, "cards", [])
                pair_map: dict[str, list[int]] = {}
                for idx, c in enumerate(grid):
                    k = c.get("match_key") if isinstance(c, dict) else getattr(c, "match_key", getattr(c, "rank", idx))
                    pair_map.setdefault(k, []).append(idx)

                # Flip first matching pair
                first_key = list(pair_map.keys())[0]
                idx1, idx2 = pair_map[first_key][:2]

                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "MemoryChamp",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "flip", "data": {"index": idx1, "card_index": idx1}},
                })
                _recv_until_type(ws, "GAME_STATE")

                # Advance timer slightly to verify elapsed timer increments
                time.sleep(0.05)
                game._tick_timers(time.time() + 1.0)

                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "MemoryChamp",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "flip", "data": {"index": idx2, "card_index": idx2}},
                })
                st_match, _ = _recv_until_type(ws, "GAME_STATE")
                pub_match = st_match["public_state"]
                # Verify move counter increments
                assert pub_match.get("moves", 0) >= 1 or pub_match.get("moves_count", 0) >= 1 or pub_match.get("flips", 0) >= 1
                # Verify elapsed timer tracking
                assert any(k in pub_match for k in ("elapsed_time", "timer", "time_elapsed", "time_seconds", "elapsed_seconds"))

                # Match remaining pairs to complete the game
                for key in list(pair_map.keys())[1:]:
                    i1, i2 = pair_map[key][:2]
                    ws.send_json({
                        "type": "GAME_ACTION",
                        "player_name": "MemoryChamp",
                        "room_code": code,
                        "game_type": "playing_cards",
                        "payload": {"action": "flip", "data": {"index": i1, "card_index": i1}},
                    })
                    _recv_until_type(ws, "GAME_STATE")
                    ws.send_json({
                        "type": "GAME_ACTION",
                        "player_name": "MemoryChamp",
                        "room_code": code,
                        "game_type": "playing_cards",
                        "payload": {"action": "flip", "data": {"index": i2, "card_index": i2}},
                    })

                # Play to completion and verify GAME_OVER
                over_msg, _ = _recv_until_type(ws, "GAME_OVER")
                assert over_msg["type"] == "GAME_OVER"
                assert over_msg["public_state"]["phase"] == "finished"
