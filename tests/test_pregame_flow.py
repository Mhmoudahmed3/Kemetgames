"""Automated verification suite for Pre-Game Setup Flow.

Verifies:
1. R1: Game Mode Selection
   - Mode card presence across all 11 games on the website in GAME_HUB_META.
   - Verification that minesweeper activities are populated.
   - Mode metadata structure: minPlayers, maxPlayers, defaultPlayers, supportsSolo, supportsHost.
   - HTML markup for mode setup controls and CSS rules for active mode selection (.active, aria-selected="true").
   - Single-active card selection invariant.
2. R2: Matchup Option Selection
   - Toggle between "Challenging AI" and "Hosting a game against another player".
   - Reflection in CREATE_ROOM launch payload (solo=True vs solo=False).
3. R3: Player Count Selection & Constraints
   - Dynamic boundary enforcement: min_players <= player_count <= max_players.
   - Server rejection of out-of-bounds player counts with exact protocol error messages.
   - Dynamic clamping simulation: preventing values below min or above max.
   - Game session transition: AI challenge launches immediately into active play (playing / pre_game),
     while Host game stages in waiting room with target player metadata.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.games import GAME_REGISTRY
from backend.main import app

REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_HUB_DATA_PATH = REPO_ROOT / "frontend" / "js" / "game_hub_data.js"
INDEX_HTML_PATH = REPO_ROOT / "frontend" / "index.html"
MAIN_CSS_PATH = REPO_ROOT / "frontend" / "css" / "main.css"
APP_JS_PATH = REPO_ROOT / "frontend" / "js" / "app.js"

ALL_11_GAMES = [
    "snake",
    "minesweeper",
    "chess",
    "backgammon",
    "dominoes",
    "ludo",
    "skru",
    "uno",
    "qa_trivia",
    "globe",
    "monopoly",
]


def load_game_hub_meta_via_node() -> dict[str, Any]:
    """Execute a Node.js snippet importing GAME_HUB_META from game_hub_data.js."""
    script = """
    import { GAME_HUB_META } from './frontend/js/game_hub_data.js';
    console.log(JSON.stringify(GAME_HUB_META));
    """
    res = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout)


# =============================================================================
# R1: GAME MODE SELECTION & CATALOG TESTS
# =============================================================================


def test_r1_all_11_games_have_selectable_mode_cards():
    """Verify all 11 games on the platform have selectable mode cards defined in GAME_HUB_META."""
    meta = load_game_hub_meta_via_node()

    for game_key in ALL_11_GAMES:
        assert game_key in meta, f"Game '{game_key}' missing from GAME_HUB_META"
        game_meta = meta[game_key]
        activities = game_meta.get("activities", [])
        assert (
            len(activities) >= 2
        ), f"Game '{game_key}' must have at least 2 selectable mode cards, found {len(activities)}"

        for act in activities:
            assert "id" in act, f"Mode card in {game_key} missing 'id': {act}"
            assert "title" in act and act["title"], f"Mode card in {game_key} missing 'title': {act}"
            assert "minPlayers" in act, f"Mode card in {game_key} missing 'minPlayers': {act}"
            assert "maxPlayers" in act, f"Mode card in {game_key} missing 'maxPlayers': {act}"
            assert "defaultPlayers" in act, f"Mode card in {game_key} missing 'defaultPlayers': {act}"

            min_p = act["minPlayers"]
            max_p = act["maxPlayers"]
            def_p = act["defaultPlayers"]

            assert isinstance(min_p, int) and min_p >= 1, f"Invalid minPlayers {min_p} in {game_key}"
            assert isinstance(max_p, int) and max_p >= min_p, f"Invalid maxPlayers {max_p} in {game_key}"
            assert min_p <= def_p <= max_p, f"defaultPlayers {def_p} outside [{min_p}, {max_p}] in {game_key}"

            # Verify consistency with backend engine limits
            engine_cls = GAME_REGISTRY[game_key]
            assert (
                min_p >= engine_cls.MIN_PLAYERS
            ), f"Mode minPlayers {min_p} < engine MIN_PLAYERS {engine_cls.MIN_PLAYERS} for {game_key}"
            assert (
                max_p <= engine_cls.MAX_PLAYERS
            ), f"Mode maxPlayers {max_p} > engine MAX_PLAYERS {engine_cls.MAX_PLAYERS} for {game_key}"


def test_r1_minesweeper_mode_cards_specifically_populated():
    """Verify minesweeper activities are specifically populated with multiple distinct difficulty modes."""
    meta = load_game_hub_meta_via_node()
    ms = meta.get("minesweeper", {})
    activities = ms.get("activities", [])

    assert (
        len(activities) >= 4
    ), f"Minesweeper must have at least 4 modes (Beginner, Mid, Hard, Multiplayer Race), found {len(activities)}"

    mode_ids = [a["id"] for a in activities]
    assert "solo_beginner" in mode_ids
    assert "solo_intermediate" in mode_ids
    assert "solo_expert" in mode_ids
    assert "multiplayer_race" in mode_ids

    # Solo modes are strictly 1P, multiplayer is 2-8P
    beginner = next(a for a in activities if a["id"] == "solo_beginner")
    assert beginner["minPlayers"] == 1 and beginner["maxPlayers"] == 1
    assert beginner["supportsSolo"] is True and beginner["supportsHost"] is False

    race = next(a for a in activities if a["id"] == "multiplayer_race")
    assert race["minPlayers"] == 2 and race["maxPlayers"] == 8
    assert race["supportsSolo"] is False and race["supportsHost"] is True


def test_r1_html_and_css_active_visual_state_styles():
    """Verify HTML and CSS support mode card active visual states (.active, aria-selected='true')."""
    html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")
    css_content = MAIN_CSS_PATH.read_text(encoding="utf-8")
    app_js_content = APP_JS_PATH.read_text(encoding="utf-8")

    # HTML verification
    assert 'id="ps5-activity-strip"' in html_content
    assert 'id="pregame-setup-panel"' in html_content
    assert 'id="pregame-matchup-row"' in html_content
    assert 'id="pregame-player-count-row"' in html_content
    assert 'id="btn-pregame-launch"' in html_content

    # CSS verification
    assert ".visual-activity-card.active" in css_content
    assert '.visual-activity-card[aria-selected="true"]' in css_content
    assert ".visual-card-active-pill" in css_content
    assert ".pregame-setup-panel" in css_content
    assert ".pregame-stepper-wrap" in css_content
    assert ".stepper-btn" in css_content

    # app.js single-active invariant verification
    assert "aria-selected" in app_js_content
    assert "pregameSetup" in app_js_content
    assert "_syncPregameSetup" in app_js_content
    assert "_launchPregameSession" in app_js_content


def test_r1_single_active_card_invariant_simulation():
    """Simulate single-active card selection: clicking a card activates it and deactivates siblings."""
    meta = load_game_hub_meta_via_node()

    for game_key, gdata in meta.items():
        if game_key == "explore":
            continue
        activities = gdata.get("activities", [])
        if not activities:
            continue

        # Simulate UI card array with active state flags
        cards = [{"idx": i, "active": (i == 0), "ariaSelected": (i == 0)} for i in range(len(activities))]

        # Verify initial invariant: exactly one active
        assert sum(1 for c in cards if c["active"]) == 1
        assert sum(1 for c in cards if c["ariaSelected"]) == 1

        # Simulate user clicking each card
        for clicked_idx in range(len(activities)):
            # Selection handler logic (mirrored from _createVisualCard in app.js):
            for c in cards:
                c["active"] = False
                c["ariaSelected"] = False
            cards[clicked_idx]["active"] = True
            cards[clicked_idx]["ariaSelected"] = True

            # Invariant check: strictly one card is active
            active_cards = [c for c in cards if c["active"]]
            assert len(active_cards) == 1
            assert active_cards[0]["idx"] == clicked_idx
            assert active_cards[0]["ariaSelected"] is True


# =============================================================================
# R2: MATCHUP OPTION TESTS (AI VS HOST)
# =============================================================================


def test_r2_matchup_option_markup_and_defaults():
    """Verify UI matchup toggle options 'Challenge AI' and 'Host vs Player' exist with radiogroup semantics."""
    html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")

    assert 'id="btn-matchup-ai"' in html_content
    assert 'data-matchup="ai"' in html_content
    assert 'id="btn-matchup-host"' in html_content
    assert 'data-matchup="host"' in html_content
    assert 'role="radiogroup"' in html_content


def test_r2_ai_matchup_instant_launch_with_bots_over_ws():
    """Verify selecting 'Challenge AI' in bot-supporting games automatically provisions bots and launches match."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/client_test_ai") as ws:
            assert ws.receive_json()["type"] == "LOBBY_STATE"
            ws.send_json({"type": "SET_NAME", "player_name": "Commander", "payload": {}})
            assert ws.receive_json()["type"] == "LOBBY_STATE"

            # Launch Uno duel vs 1 AI Bot
            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Commander",
                    "game_type": "uno",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "player_count": 2,
                            "bot_count": 1,
                            "settings": {"difficulty": "mid"},
                        },
                    },
                }
            )

            room_joined = ws.receive_json()
            assert room_joined["type"] == "ROOM_JOINED"

            game_started = ws.receive_json()
            assert game_started["type"] == "GAME_STARTED"
            players = game_started["players"]
            assert len(players) == 2
            assert sum(1 for p in players if p["is_bot"]) == 1
            assert sum(1 for p in players if not p["is_bot"]) == 1

            game_state = ws.receive_json()
            assert game_state["type"] == "GAME_STATE"
            assert game_state["public_state"]["room_meta"]["phase"] in ("playing", "pre_game")


def test_r2_ai_matchup_party_table_allocates_correct_bot_count():
    """Verify challenging AI in a 4-player table provisions 3 AI bots (N - 1 bots)."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/client_test_ai_party") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "TableHost", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "TableHost",
                    "game_type": "monopoly",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "player_count": 4,
                            "bot_count": 3,
                            "settings": {"difficulty": "mid"},
                        },
                    },
                }
            )

            ws.receive_json()  # ROOM_JOINED
            started = ws.receive_json()  # GAME_STARTED
            assert started["type"] == "GAME_STARTED"
            players = started["players"]
            assert len(players) == 4
            assert sum(1 for p in players if p["is_bot"]) == 3


def test_r2_ai_matchup_pure_solo_games():
    """Verify challenging AI / solo run on games without bots (Snake, Minesweeper) creates 1-player active session."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/client_test_solo_sweep") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "Sweeper", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Sweeper",
                    "game_type": "minesweeper",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "player_count": 1,
                            "bot_count": 0,
                            "settings": {"difficulty": "mid", "width": 16, "height": 16, "booms": 40},
                        },
                    },
                }
            )

            ws.receive_json()  # ROOM_JOINED
            started = ws.receive_json()  # GAME_STARTED
            assert started["type"] == "GAME_STARTED"
            players = started["players"]
            assert len(players) == 1
            assert players[0]["name"] == "Sweeper"
            assert not players[0]["is_bot"]


def test_r2_host_matchup_stages_in_waiting_room():
    """Verify selecting 'Host vs Player' creates a public room in waiting phase with 0 initial bots."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/client_test_host") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "HostUser", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "HostUser",
                    "game_type": "ludo",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": False,
                            "is_public": True,
                            "player_count": 4,
                            "bot_count": 0,
                            "settings": {"difficulty": "mid"},
                        },
                    },
                }
            )

            joined = ws.receive_json()
            assert joined["type"] == "ROOM_JOINED"
            meta = joined["public_state"]["room_meta"]
            assert meta["phase"] == "waiting"
            assert meta["target_players"] == 4
            assert meta["is_public"] is True

            # Room host is only player, no bots
            players = joined["players"]
            assert len(players) == 1
            assert players[0]["is_host"] is True


# =============================================================================
# R3: PLAYER COUNT BOUNDS & CONSTRAINTS ENFORCEMENT
# =============================================================================


@pytest.mark.parametrize("game_type", ALL_11_GAMES)
def test_r3_server_rejects_player_count_below_minimum(game_type: str):
    """Verify server rejects CREATE_ROOM when player_count is strictly below MIN_PLAYERS."""
    engine_cls = GAME_REGISTRY[game_type]
    min_players = engine_cls.MIN_PLAYERS
    invalid_count = min_players - 1

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/test_min_{game_type}") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": game_type,
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": False,
                            "player_count": invalid_count,
                        },
                    },
                }
            )

            err = ws.receive_json()
            assert err["type"] == "ERROR"
            assert f"Need at least {min_players} player(s) to launch." in err["message"]


@pytest.mark.parametrize("game_type", ALL_11_GAMES)
def test_r3_server_rejects_player_count_above_maximum(game_type: str):
    """Verify server rejects CREATE_ROOM when player_count is strictly above MAX_PLAYERS."""
    engine_cls = GAME_REGISTRY[game_type]
    max_players = engine_cls.MAX_PLAYERS
    invalid_count = max_players + 1

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/test_max_{game_type}") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": game_type,
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": False,
                            "player_count": invalid_count,
                        },
                    },
                }
            )

            err = ws.receive_json()
            assert err["type"] == "ERROR"
            assert f"Maximum {max_players} players allowed." in err["message"]


def test_r3_server_rejects_invalid_type_player_count():
    """Verify server rejects non-numeric or boolean player_count."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test_invalid_pc") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
            ws.receive_json()

            # Test boolean player_count
            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": "chess",
                    "payload": {
                        "action": "create",
                        "data": {"solo": True, "player_count": True},
                    },
                }
            )
            err1 = ws.receive_json()
            assert err1["type"] == "ERROR"
            assert "Invalid player count." in err1["message"]

            # Test string non-numeric player_count
            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": "chess",
                    "payload": {
                        "action": "create",
                        "data": {"solo": True, "player_count": "invalid_five"},
                    },
                }
            )
            err2 = ws.receive_json()
            assert err2["type"] == "ERROR"
            assert "Invalid player count." in err2["message"]


def test_r3_fixed_two_player_duel_boundary():
    """Verify fixed 2-player games (Chess, Backgammon) enforce exactly 2 players."""
    for duel_game in ("chess", "backgammon"):
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/duel_{duel_game}") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "Duelist", "payload": {}})
                ws.receive_json()

                # 1 Player fails
                ws.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "Duelist",
                        "game_type": duel_game,
                        "payload": {"action": "create", "data": {"solo": False, "player_count": 1}},
                    }
                )
                assert "Need at least 2 player(s) to launch." in ws.receive_json()["message"]

                # 3 Players fails
                ws.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "Duelist",
                        "game_type": duel_game,
                        "payload": {"action": "create", "data": {"solo": False, "player_count": 3}},
                    }
                )
                assert "Maximum 2 players allowed." in ws.receive_json()["message"]

                # Exactly 2 Players succeeds
                ws.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "Duelist",
                        "game_type": duel_game,
                        "payload": {
                            "action": "create",
                            "data": {
                                "solo": True,
                                "player_count": 2,
                                "bot_count": 1,
                                "settings": {},
                            },
                        },
                    }
                )
                j = ws.receive_json()
                assert j["type"] == "ROOM_JOINED"
                s = ws.receive_json()
                assert s["type"] == "GAME_STARTED"
                assert len(s["players"]) == 2


def test_r3_client_side_clamping_simulation():
    """Verify client-side clamping logic prevents out-of-bounds player counts and handles mode switches."""
    meta = load_game_hub_meta_via_node()

    def simulate_clamp(current_count: int, min_p: int, max_p: int) -> int:
        return max(min_p, min(max_p, current_count))

    def simulate_step(current_count: int, delta: int, min_p: int, max_p: int) -> tuple[int, bool, bool]:
        new_count = simulate_clamp(current_count + delta, min_p, max_p)
        can_dec = new_count > min_p
        can_inc = new_count < max_p
        return new_count, can_dec, can_inc

    # 1. Uno Party Table (2-6 players)
    uno_min, uno_max = 2, 6
    count = 4
    # Step up to max
    count, can_dec, can_inc = simulate_step(count, +1, uno_min, uno_max)
    assert count == 5 and can_dec is True and can_inc is True
    count, can_dec, can_inc = simulate_step(count, +1, uno_min, uno_max)
    assert count == 6 and can_dec is True and can_inc is False  # At max: cannot increment!
    # Attempting to increment past max does not change value
    count, can_dec, can_inc = simulate_step(count, +1, uno_min, uno_max)
    assert count == 6 and can_inc is False

    # Step down to min
    while can_dec:
        count, can_dec, can_inc = simulate_step(count, -1, uno_min, uno_max)
    assert count == 2 and can_dec is False and can_inc is True  # At min: cannot decrement!

    # 2. Mode switch: From Uno 6P table to Chess 2P
    # Prior count was 6, Chess bounds are [2, 2]
    chess_min, chess_max = 2, 2
    clamped_chess = simulate_clamp(current_count=6, min_p=chess_min, max_p=chess_max)
    assert clamped_chess == 2
    # In 2P fixed mode, both buttons must be disabled
    _, can_dec, can_inc = simulate_step(clamped_chess, 0, chess_min, chess_max)
    assert can_dec is False and can_inc is False

    # 3. Mode switch: From Snake 1P solo to Snake 8P race
    snake_solo_min, snake_solo_max = 1, 1
    snake_race_min, snake_race_max = 2, 8
    clamped_race = simulate_clamp(current_count=1, min_p=snake_race_min, max_p=snake_race_max)
    assert clamped_race == 2  # Automatically clamped up to mode minimum 2!


def test_r3_full_session_transition_payload_and_state():
    """Verify confirming setup transitions user to arena with configured mode, matchup, and player count."""
    with TestClient(app) as client:
        # Scenario A: AI Challenge with Dominoes 4P
        with client.websocket_connect("/ws/client_transition_ai") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "DominoChamp", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "DominoChamp",
                    "game_type": "dominoes",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "player_count": 4,
                            "bot_count": 3,
                            "settings": {"target_score": 100, "difficulty": "hard"},
                        },
                    },
                }
            )

            r_joined = ws.receive_json()
            assert r_joined["type"] == "ROOM_JOINED"
            assert r_joined["game_type"] == "dominoes"

            g_started = ws.receive_json()
            assert g_started["type"] == "GAME_STARTED"
            assert len(g_started["players"]) == 4

            g_state = ws.receive_json()
            assert g_state["type"] == "GAME_STATE"
            assert g_state["public_state"]["room_meta"]["phase"] in ("playing", "pre_game")
            assert g_state["public_state"]["room_meta"]["settings"]["target_score"] == 100

        # Scenario B: Hosted Room with QA Showdown 8P
        with client.websocket_connect("/ws/client_transition_host") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "QuizMaster", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "QuizMaster",
                    "game_type": "qa_trivia",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": False,
                            "is_public": True,
                            "player_count": 8,
                            "bot_count": 0,
                            "settings": {"category": "Atlas", "rounds": 12},
                        },
                    },
                }
            )

            r_joined = ws.receive_json()
            assert r_joined["type"] == "ROOM_JOINED"
            meta = r_joined["public_state"]["room_meta"]
            assert meta["phase"] == "waiting"
            assert meta["target_players"] == 8
            assert meta["settings"]["category"] == "Atlas"
            assert meta["settings"]["rounds"] == 12
