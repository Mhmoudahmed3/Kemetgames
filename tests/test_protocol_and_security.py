"""Integration tests for FastAPI HTTP endpoints, strict WebSocket JSON protocol, and PRIVATE_STATE isolation."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from backend.games import GAME_REGISTRY
from backend.main import app


def test_http_health_catalog_and_spa():
    with TestClient(app) as client:
        res_health = client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "ok"

        res_games = client.get("/api/games")
        assert res_games.status_code == 200
        games = res_games.json()["games"]
        assert len(games) == 11
        assert {g["game_type"] for g in games} == {
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
        }
        qa_meta = next(g for g in games if g["game_type"] == "qa_trivia")
        assert qa_meta["title"] == "QA"

        res_countries = client.get("/api/countries?continent=Africa&q=Cairo")
        assert res_countries.status_code == 200
        cdata = res_countries.json()
        assert cdata["count"] >= 1
        assert any(row["code"] == "EG" for row in cdata["countries"])

        res_all_countries = client.get("/api/countries")
        assert res_all_countries.status_code == 200
        assert res_all_countries.json()["count"] >= 195

        res_index = client.get("/")
        assert res_index.status_code == 200
        assert "BLACKOUT" in res_index.text


def test_websocket_multiplayer_room_chat_and_private_state_isolation():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/c1") as ws1, client.websocket_connect("/ws/c2") as ws2:
            # Initial lobby payloads
            assert ws1.receive_json()["type"] == "LOBBY_STATE"
            assert ws2.receive_json()["type"] == "LOBBY_STATE"

            ws1.send_json({"type": "SET_NAME", "player_name": "Alex", "payload": {}})
            assert ws1.receive_json()["type"] == "LOBBY_STATE"

            ws2.send_json({"type": "SET_NAME", "player_name": "Sam", "payload": {}})
            assert ws2.receive_json()["type"] == "LOBBY_STATE"

            # Create Skru room
            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Alex",
                    "game_type": "skru",
                    "payload": {"action": "create", "data": {"is_public": True}},
                }
            )
            joined1 = ws1.receive_json()
            assert joined1["type"] == "ROOM_JOINED"
            room_code = joined1["room_code"]
            assert len(room_code) == 6
            # Drain LOBBY_STATE broadcast on ws2
            assert ws2.receive_json()["type"] == "LOBBY_STATE"

            # Join room from client 2
            ws2.send_json(
                {
                    "type": "JOIN_ROOM",
                    "player_name": "Sam",
                    "room_code": room_code,
                    "payload": {},
                }
            )
            joined2 = ws2.receive_json()
            assert joined2["type"] == "ROOM_JOINED"
            assert len(joined2["players"]) == 2
            assert ws1.receive_json()["type"] == "ROOM_UPDATE"

            # Chat message
            ws1.send_json(
                {
                    "type": "CHAT_MSG",
                    "player_name": "Alex",
                    "room_code": room_code,
                    "payload": {"action": "chat", "data": {"text": "Ready?"}},
                }
            )
            chat1 = ws1.receive_json()
            chat2 = ws2.receive_json()
            assert chat1["type"] == "ROOM_UPDATE"
            assert chat2["public_state"]["room_meta"]["chat"][-1]["text"] == "Ready?"

            # Start game and verify PRIVATE_STATE isolation
            ws1.send_json(
                {
                    "type": "START_GAME",
                    "player_name": "Alex",
                    "room_code": room_code,
                    "game_type": "skru",
                    "payload": {"action": "start", "data": {}},
                }
            )
            msgs1 = [ws1.receive_json() for _ in range(3)]
            msgs2 = [ws2.receive_json() for _ in range(3)]

            types1 = [m["type"] for m in msgs1]
            types2 = [m["type"] for m in msgs2]
            assert types1 == ["GAME_STARTED", "GAME_STATE", "PRIVATE_STATE"]
            assert types2 == ["GAME_STARTED", "GAME_STATE", "PRIVATE_STATE"]

            pub_hands = msgs1[1]["public_state"]["hands"]
            assert all(slot == {"hidden": True} for slot in pub_hands["c1"])
            assert all(slot == {"hidden": True} for slot in pub_hands["c2"])

            priv1 = msgs1[2]["private_state"]
            priv2 = msgs2[2]["private_state"]
            assert "initial_bottom" in priv1 and len(priv1["initial_bottom"]) == 2
            assert "initial_bottom" in priv2 and len(priv2["initial_bottom"]) == 2
            assert priv1["initial_bottom"] != priv2["initial_bottom"]


def test_solo_vs_bot_instant_launch_and_chess_spectator():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/solo1") as ws:
            assert ws.receive_json()["type"] == "LOBBY_STATE"
            ws.send_json({"type": "SET_NAME", "player_name": "SoloHost", "payload": {}})
            assert ws.receive_json()["type"] == "LOBBY_STATE"

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "SoloHost",
                    "game_type": "chess",
                    "payload": {"action": "create", "data": {"solo": True, "is_public": True}},
                }
            )
            m_joined = ws.receive_json()
            m_started = ws.receive_json()
            m_state = ws.receive_json()
            assert m_joined["type"] == "ROOM_JOINED"
            assert m_started["type"] == "GAME_STARTED"
            assert m_state["type"] == "GAME_STATE"
            assert len(m_state["players"]) == 2
            assert any(p["is_bot"] for p in m_state["players"])

            room_code = m_joined["room_code"]
            with client.websocket_connect("/ws/spec1") as ws_spec:
                assert ws_spec.receive_json()["type"] == "LOBBY_STATE"
                ws_spec.send_json(
                    {
                        "type": "JOIN_ROOM",
                        "player_name": "Watcher",
                        "room_code": room_code,
                        "payload": {},
                    }
                )
                spec_joined = ws_spec.receive_json()
                assert spec_joined["type"] == "ROOM_JOINED"
                assert any(p["role"] == "spectator" for p in spec_joined["players"])


@pytest.mark.parametrize("game_type", list(GAME_REGISTRY.keys()))
def test_all_10_games_create_waiting_and_solo_launch_over_ws(game_type: str):
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/t_{game_type}") as ws:
            assert ws.receive_json()["type"] == "LOBBY_STATE"
            ws.send_json({"type": "SET_NAME", "player_name": "Tester", "payload": {}})
            assert ws.receive_json()["type"] == "LOBBY_STATE"

            # Waiting room creation
            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": game_type,
                    "payload": {"action": "create", "data": {"is_public": True, "solo": False}},
                }
            )
            joined = ws.receive_json()
            assert joined["type"] == "ROOM_JOINED"
            assert joined["public_state"]["room_meta"]["phase"] == "waiting"

            ws.send_json({"type": "LEAVE_ROOM", "player_name": "Tester", "payload": {}})
            assert ws.receive_json()["type"] == "LOBBY_STATE"

            # Instant solo / solo-vs-bot launch
            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Tester",
                    "game_type": game_type,
                    "payload": {"action": "create", "data": {"is_public": False, "solo": True}},
                }
            )
            j2 = ws.receive_json()
            s2 = ws.receive_json()
            g2 = ws.receive_json()
            assert j2["type"] == "ROOM_JOINED"
            assert s2["type"] == "GAME_STARTED"
            assert g2["type"] == "GAME_STATE"
            assert g2["public_state"]["room_meta"]["phase"] in ("pre_game", "playing")


def test_difficulty_in_open_rooms_and_update_settings():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/host_d") as ws_host, client.websocket_connect("/ws/join_d") as ws_join:
            assert ws_host.receive_json()["type"] == "LOBBY_STATE"
            assert ws_join.receive_json()["type"] == "LOBBY_STATE"

            ws_host.send_json({"type": "SET_NAME", "player_name": "HostD", "payload": {}})
            assert ws_host.receive_json()["type"] == "LOBBY_STATE"

            ws_join.send_json({"type": "SET_NAME", "player_name": "JoinD", "payload": {}})
            assert ws_join.receive_json()["type"] == "LOBBY_STATE"

            ws_host.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "HostD",
                    "game_type": "globe",
                    "payload": {
                        "action": "create",
                        "data": {"is_public": True, "solo": False, "settings": {"difficulty": "hard"}},
                    },
                }
            )
            joined = ws_host.receive_json()
            assert joined["type"] == "ROOM_JOINED"
            code = joined["room_code"]
            assert joined["public_state"]["room_meta"]["settings"]["difficulty"] == "hard"

            lobby_msg = ws_join.receive_json()
            assert lobby_msg["type"] == "LOBBY_STATE"
            rooms = lobby_msg["public_state"]["open_rooms"]
            match = next((r for r in rooms if r["room_code"] == code), None)
            assert match is not None
            assert match["difficulty"] == "hard"

            ws_host.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "HostD",
                    "room_code": code,
                    "game_type": "globe",
                    "payload": {"action": "update_settings", "data": {"difficulty": "easy"}},
                }
            )
            upd = ws_host.receive_json()
            assert upd["type"] == "ROOM_UPDATE"
            assert upd["public_state"]["room_meta"]["settings"]["difficulty"] == "easy"

            lobby_upd = ws_join.receive_json()
            assert lobby_upd["type"] == "LOBBY_STATE"
            match2 = next((r for r in lobby_upd["public_state"]["open_rooms"] if r["room_code"] == code), None)
            assert match2 is not None
            assert match2["difficulty"] == "easy"


def _recv_until_type(ws, target_type: str, limit: int = 12) -> tuple[dict, list[dict]]:
    seen: list[dict] = []
    for _ in range(limit):
        msg = ws.receive_json()
        seen.append(msg)
        if msg.get("type") == target_type:
            return msg, seen
    raise AssertionError(f"Did not receive {target_type}; got {[m.get('type') for m in seen]}")


def test_chat_msg_delivery_events_empty_ignored_and_truncated():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/ch1") as ws1, client.websocket_connect("/ws/ch2") as ws2:
            ws1.receive_json()
            ws2.receive_json()

            ws1.send_json({"type": "SET_NAME", "player_name": "Alex", "payload": {}})
            ws1.receive_json()
            ws2.send_json({"type": "SET_NAME", "player_name": "Sam", "payload": {}})
            ws2.receive_json()

            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Alex",
                    "game_type": "uno",
                    "payload": {"action": "create", "data": {"is_public": True}},
                }
            )
            code = ws1.receive_json()["room_code"]
            ws2.receive_json()  # LOBBY_STATE

            ws2.send_json({"type": "JOIN_ROOM", "player_name": "Sam", "room_code": code, "payload": {}})
            ws2.receive_json()  # ROOM_JOINED
            ws1.receive_json()  # ROOM_UPDATE

            # Valid chat message
            ws1.send_json(
                {
                    "type": "CHAT_MSG",
                    "player_name": "Alex",
                    "room_code": code,
                    "payload": {"action": "chat", "data": {"text": "  GLHF bunker!  "}},
                }
            )
            upd1 = ws1.receive_json()
            upd2 = ws2.receive_json()
            assert upd1["type"] == "ROOM_UPDATE"
            assert upd2["type"] == "ROOM_UPDATE"
            chat_entry = upd2["public_state"]["room_meta"]["chat"][-1]
            assert chat_entry["sender"] == "Alex"
            assert chat_entry["sender_id"] == "ch1"
            assert chat_entry["text"] == "GLHF bunker!"
            events = upd2["public_state"]["room_meta"]["events"]
            assert any("created room" in ev["text"] for ev in events)
            assert any("joined the room" in ev["text"] for ev in events)

            # Empty/whitespace chat is ignored, >280 chars is truncated to 280
            ws1.send_json(
                {
                    "type": "CHAT_MSG",
                    "player_name": "Alex",
                    "room_code": code,
                    "payload": {"action": "chat", "data": {"text": "    "}},
                }
            )
            ws2.send_json(
                {
                    "type": "CHAT_MSG",
                    "player_name": "Sam",
                    "room_code": code,
                    "payload": {"action": "chat", "data": {"text": "Z" * 350}},
                }
            )
            long_upd = ws1.receive_json()
            assert long_upd["type"] == "ROOM_UPDATE"
            assert len(long_upd["public_state"]["room_meta"]["chat"][-1]["text"]) == 280


def test_game_action_game_over_rematch_and_leaderboard_recording(isolate_room_manager_and_leaderboard):
    from backend.main import room_manager

    with TestClient(app) as client:
        # 1. Solo Snake GAME_ACTION -> GAME_OVER -> immediate rematch -> to_lobby rematch -> Leaderboard
        with client.websocket_connect("/ws/snk_host") as ws:
            ws.receive_json()
            ws.send_json({"type": "SET_NAME", "player_name": "Viper", "payload": {}})
            ws.receive_json()

            ws.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Viper",
                    "game_type": "snake",
                    "payload": {"action": "create", "data": {"solo": True, "is_public": False}},
                }
            )
            joined = ws.receive_json()
            assert joined["type"] == "ROOM_JOINED"
            code = joined["room_code"]
            assert ws.receive_json()["type"] == "GAME_STARTED"
            assert ws.receive_json()["type"] == "GAME_STATE"

            ws.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Viper",
                    "room_code": code,
                    "game_type": "snake",
                    "payload": {"action": "sync", "data": {"score": 30, "length": 6, "alive": True}},
                }
            )
            st = ws.receive_json()
            assert st["type"] == "GAME_STATE"
            assert st["public_state"]["snakes"]["snk_host"]["score"] == 30

            ws.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Viper",
                    "room_code": code,
                    "game_type": "snake",
                    "payload": {"action": "sync", "data": {"score": 30, "length": 6, "alive": False}},
                }
            )
            assert ws.receive_json()["type"] == "GAME_STATE"
            over = ws.receive_json()
            assert over["type"] == "GAME_OVER"
            assert over["public_state"]["winner_ids"] == ["snk_host"]
            assert over["public_state"]["room_meta"]["phase"] == "finished"

            lb = client.get("/api/leaderboard").json()["leaderboard"]
            assert lb["snake"][0]["name"] == "Viper"
            assert lb["snake"][0]["wins"] == 1
            assert lb["snake"][0]["best_score"] == 30

            # Immediate rematch
            ws.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Viper",
                    "room_code": code,
                    "game_type": "snake",
                    "payload": {"action": "rematch", "data": {}},
                }
            )
            rm_started = ws.receive_json()
            rm_state = ws.receive_json()
            assert rm_started["type"] == "GAME_STARTED"
            assert rm_state["type"] == "GAME_STATE"
            assert rm_state["players"][0]["score"] == 0
            assert rm_state["public_state"]["phase"] == "playing"

            # Finish rematch with higher score and test to_lobby rematch
            ws.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Viper",
                    "room_code": code,
                    "game_type": "snake",
                    "payload": {"action": "sync", "data": {"score": 50, "length": 8, "alive": False}},
                }
            )
            assert ws.receive_json()["type"] == "GAME_STATE"
            assert ws.receive_json()["type"] == "GAME_OVER"

            lb2 = client.get("/api/leaderboard").json()["leaderboard"]
            assert lb2["snake"][0]["wins"] == 2
            assert lb2["snake"][0]["best_score"] == 50

            ws.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Viper",
                    "room_code": code,
                    "game_type": "snake",
                    "payload": {"action": "rematch", "data": {"to_lobby": True}},
                }
            )
            lobby_rm = ws.receive_json()
            assert lobby_rm["type"] == "ROOM_UPDATE"
            assert lobby_rm["public_state"]["room_meta"]["phase"] == "waiting"
            assert lobby_rm["players"][0]["score"] == 0

        # 2. Move-0 Custom Chess immediate checkmate emits GAME_OVER right on launch!
        mate_board = [[None] * 8 for _ in range(8)]
        mate_board[0][7] = "k"
        mate_board[0][1] = "r"
        mate_board[6][1] = "q"
        mate_board[7][0] = "K"
        with client.websocket_connect("/ws/ch_m0") as ws_ch:
            ws_ch.receive_json()
            ws_ch.send_json({"type": "SET_NAME", "player_name": "CustomHost", "payload": {}})
            ws_ch.receive_json()
            ws_ch.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "CustomHost",
                    "game_type": "chess",
                    "payload": {
                        "action": "create",
                        "data": {
                            "solo": True,
                            "is_public": False,
                            "settings": {"custom_board": mate_board},
                        },
                    },
                }
            )
            assert ws_ch.receive_json()["type"] == "ROOM_JOINED"
            assert ws_ch.receive_json()["type"] == "GAME_STARTED"
            assert ws_ch.receive_json()["type"] == "GAME_STATE"
            over_m0 = ws_ch.receive_json()
            assert over_m0["type"] == "GAME_OVER"
            assert "Checkmate from starting setup" in over_m0["message"]
            assert len(over_m0["public_state"]["winner_ids"]) == 1

    # 3. Skru lowest-score leaderboard recording & ranking
    store = isolate_room_manager_and_leaderboard
    store.record_entries(
        [
            {"game_type": "skru", "name": "Alpha", "score": 18, "won": False},
            {"game_type": "skru", "name": "Beta", "score": 6, "won": True},
        ]
    )
    store.record_entries(
        [
            {"game_type": "skru", "name": "Alpha", "score": 3, "won": True},
            {"game_type": "skru", "name": "Beta", "score": 25, "won": False},
        ]
    )
    summary = room_manager.leaderboard.get_summary()["skru"]
    by_name = {r["name"]: r for r in summary}
    assert by_name["Alpha"]["best_score"] == 3
    assert by_name["Beta"]["best_score"] == 6
    assert summary[0]["name"] == "Alpha"  # Both 1 win; lowest best_score (3) ranks #1


def test_midgame_disconnect_host_transfer_spectator_cleanup_and_finished_reconnect():
    from backend.main import room_manager

    with TestClient(app) as client:
        # 1. Spectator disconnect cleans up spectators list and session.room_code
        with client.websocket_connect("/ws/sp_host") as ws_h:
            ws_h.receive_json()
            ws_h.send_json({"type": "SET_NAME", "player_name": "HostC", "payload": {}})
            ws_h.receive_json()
            ws_h.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "HostC",
                    "game_type": "chess",
                    "payload": {"action": "create", "data": {"solo": True, "is_public": True}},
                }
            )
            chess_code = ws_h.receive_json()["room_code"]
            ws_h.receive_json()
            ws_h.receive_json()

            with client.websocket_connect("/ws/sp_watch") as ws_s:
                ws_s.receive_json()
                ws_s.send_json({"type": "SET_NAME", "player_name": "Watcher", "payload": {}})
                ws_s.receive_json()
                ws_s.send_json(
                    {"type": "JOIN_ROOM", "player_name": "Watcher", "room_code": chess_code, "payload": {}}
                )
                assert ws_s.receive_json()["type"] == "ROOM_JOINED"
                assert ws_s.receive_json()["type"] == "GAME_STATE"
                ws_h.receive_json()  # ROOM_UPDATE
                ws_h.receive_json()  # GAME_STATE
                assert room_manager.clients["sp_watch"].room_code == chess_code
                assert any(s.id == "sp_watch" for s in room_manager.rooms[chess_code].game.spectators)

            # Exiting ws_s triggers disconnect()
            assert room_manager.clients["sp_watch"].room_code is None
            assert not any(s.id == "sp_watch" for s in room_manager.rooms[chess_code].game.spectators)

        # 2. Mid-game host disconnect transfers host & doesn't block QA Trivia round completion
        with client.websocket_connect("/ws/qa_g") as ws_g:
            ws_g.receive_json()
            ws_g.send_json({"type": "SET_NAME", "player_name": "GuestQ", "payload": {}})
            ws_g.receive_json()

            with client.websocket_connect("/ws/qa_h") as ws_qa_h:
                ws_qa_h.receive_json()
                ws_qa_h.send_json({"type": "SET_NAME", "player_name": "HostQ", "payload": {}})
                ws_qa_h.receive_json()
                ws_qa_h.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "HostQ",
                        "game_type": "qa_trivia",
                        "payload": {"action": "create", "data": {"is_public": True, "settings": {"rounds": 3}}},
                    }
                )
                qa_code = ws_qa_h.receive_json()["room_code"]
                ws_g.receive_json()  # LOBBY_STATE

                ws_g.send_json(
                    {"type": "JOIN_ROOM", "player_name": "GuestQ", "room_code": qa_code, "payload": {}}
                )
                ws_g.receive_json()  # ROOM_JOINED
                ws_qa_h.receive_json()  # ROOM_UPDATE

                ws_qa_h.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "HostQ",
                        "room_code": qa_code,
                        "game_type": "qa_trivia",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(2):
                    ws_qa_h.receive_json()
                    ws_g.receive_json()

            # Host disconnected -> guest receives ROOM_UPDATE + GAME_STATE with is_host == True
            upd = ws_g.receive_json()
            assert upd["type"] == "ROOM_UPDATE"
            g_slot = next(p for p in upd["players"] if p["id"] == "qa_g")
            h_slot = next(p for p in upd["players"] if p["id"] == "qa_h")
            assert g_slot["is_host"] is True
            assert h_slot["is_host"] is False
            assert h_slot["connected"] is False
            assert ws_g.receive_json()["type"] == "GAME_STATE"

            # Disconnected host must NOT block round progression when guest answers
            ws_g.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "GuestQ",
                    "room_code": qa_code,
                    "game_type": "qa_trivia",
                    "payload": {"action": "answer", "data": {"choice": 0}},
                }
            )
            st = ws_g.receive_json()
            assert st["type"] == "GAME_STATE"
            assert st["public_state"]["subphase"] == "reveal"

        # 3. Reconnect during finished match emits GAME_OVER
        with client.websocket_connect("/ws/fin_1") as ws1:
            ws1.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "P1", "payload": {}})
            ws1.receive_json()

            with client.websocket_connect("/ws/fin_2") as ws2:
                lobby2 = ws2.receive_json()
                secret2 = lobby2["private_state"]["session_secret"]
                ws2.send_json({"type": "SET_NAME", "player_name": "P2", "payload": {}})
                ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "P1",
                        "game_type": "chess",
                        "payload": {"action": "create", "data": {"is_public": True}},
                    }
                )
                fcode = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "P2", "room_code": fcode, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "P1",
                        "room_code": fcode,
                        "game_type": "chess",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(2):
                    ws1.receive_json()
                    ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "GAME_ACTION",
                        "player_name": "P1",
                        "room_code": fcode,
                        "game_type": "chess",
                        "payload": {"action": "resign", "data": {}},
                    }
                )
                assert ws1.receive_json()["type"] == "GAME_STATE"
                assert ws1.receive_json()["type"] == "GAME_OVER"
                assert ws2.receive_json()["type"] == "GAME_STATE"
                assert ws2.receive_json()["type"] == "GAME_OVER"

            # ws2 disconnected while phase == "finished"; drain ws1 ROOM_UPDATE
            assert ws1.receive_json()["type"] == "ROOM_UPDATE"

            with client.websocket_connect(f"/ws/fin_2?secret={secret2}") as ws2_rec:
                m1 = ws2_rec.receive_json()
                m2 = ws2_rec.receive_json()
                m3 = ws2_rec.receive_json()
                assert [m1["type"], m2["type"], m3["type"]] == ["ROOM_JOINED", "GAME_STATE", "GAME_OVER"]
                assert m3["public_state"]["winner_ids"] == ["fin_2"]


def test_midgame_leave_and_disconnect_grace_party_and_duel_games():
    import time
    from backend.main import room_manager

    with TestClient(app) as client:
        # 1. Party game (UNO): LEAVE_ROOM converts leaver to AI bot, WS disconnect expires into bot takeover
        with client.websocket_connect("/ws/uno_1") as ws1:
            ws1.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "One", "payload": {}})
            ws1.receive_json()

            with client.websocket_connect("/ws/uno_2") as ws2:
                ws2.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "Two", "payload": {}})
                ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "One",
                        "game_type": "uno",
                        "payload": {"action": "create", "data": {"is_public": True}},
                    }
                )
                ucode = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "Two", "room_code": ucode, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "One",
                        "room_code": ucode,
                        "game_type": "uno",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(3):
                    ws1.receive_json()
                    ws2.receive_json()

                ws2.send_json({"type": "LEAVE_ROOM", "player_name": "Two", "payload": {}})
                assert ws2.receive_json()["type"] == "LOBBY_STATE"
                upd1 = ws1.receive_json()
                assert upd1["type"] == "ROOM_UPDATE"
                bot_slot = next(p for p in upd1["players"] if p["id"] == "uno_2")
                assert bot_slot["is_bot"] is True
                assert bot_slot["name"].endswith("[AI]")

        # Party disconnect grace expiration via tick worker
        with client.websocket_connect("/ws/uno_g1") as ws1:
            ws1.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "HostU", "payload": {}})
            ws1.receive_json()

            with client.websocket_connect("/ws/uno_g2") as ws2:
                ws2.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "DropU", "payload": {}})
                ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "HostU",
                        "game_type": "uno",
                        "payload": {"action": "create", "data": {"is_public": True}},
                    }
                )
                ucode2 = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "DropU", "room_code": ucode2, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "HostU",
                        "room_code": ucode2,
                        "game_type": "uno",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(3):
                    ws1.receive_json()
                    ws2.receive_json()

            # DropU disconnected -> drain disconnect ROOM_UPDATE + GAME_STATE + PRIVATE_STATE, then expire deadline
            assert ws1.receive_json()["type"] == "ROOM_UPDATE"
            assert ws1.receive_json()["type"] == "GAME_STATE"
            assert ws1.receive_json()["type"] == "PRIVATE_STATE"
            assert "uno_g2" in room_manager.rooms[ucode2].disconnect_deadlines
            room_manager.rooms[ucode2].disconnect_deadlines["uno_g2"] = time.time() - 1.0
            st_takeover, _ = _recv_until_type(ws1, "GAME_STATE")
            assert any(p["id"] == "uno_g2" and p["is_bot"] for p in st_takeover["players"])

        # 2. Duel game (Chess): WS disconnect 20s grace expires -> forfeit GAME_OVER
        with client.websocket_connect("/ws/duel_1") as ws1:
            ws1.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "Duel1", "payload": {}})
            ws1.receive_json()

            with client.websocket_connect("/ws/duel_2") as ws2:
                ws2.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "Duel2", "payload": {}})
                ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "Duel1",
                        "game_type": "chess",
                        "payload": {"action": "create", "data": {"is_public": True}},
                    }
                )
                dcode = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "Duel2", "room_code": dcode, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "Duel1",
                        "room_code": dcode,
                        "game_type": "chess",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(2):
                    ws1.receive_json()
                    ws2.receive_json()

            assert ws1.receive_json()["type"] == "ROOM_UPDATE"
            assert ws1.receive_json()["type"] == "GAME_STATE"
            assert "duel_2" in room_manager.rooms[dcode].disconnect_deadlines
            room_manager.rooms[dcode].disconnect_deadlines["duel_2"] = time.time() - 1.0
            over_msg, _ = _recv_until_type(ws1, "GAME_OVER")
            assert over_msg["public_state"]["winner_ids"] == ["duel_1"]
            assert "forfeit" in over_msg["message"].lower()


def test_leave_room_midgame_stops_broadcasts_to_leaver():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/lv1") as ws1, client.websocket_connect("/ws/lv2") as ws2:
            ws1.receive_json()
            ws2.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "Stay", "payload": {}})
            ws1.receive_json()
            ws2.send_json({"type": "SET_NAME", "player_name": "Leave", "payload": {}})
            ws2.receive_json()

            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Stay",
                    "game_type": "qa_trivia",
                    "payload": {"action": "create", "data": {"is_public": True, "settings": {"rounds": 3}}},
                }
            )
            code = ws1.receive_json()["room_code"]
            ws2.receive_json()
            ws2.send_json({"type": "JOIN_ROOM", "player_name": "Leave", "room_code": code, "payload": {}})
            ws2.receive_json()
            ws1.receive_json()

            ws1.send_json(
                {
                    "type": "START_GAME",
                    "player_name": "Stay",
                    "room_code": code,
                    "game_type": "qa_trivia",
                    "payload": {"action": "start", "data": {}},
                }
            )
            for _ in range(2):
                ws1.receive_json()
                ws2.receive_json()

            # ws2 leaves to lobby; ws2 should ONLY get LOBBY_STATE (not ROOM_UPDATE / GAME_STATE for old room)
            ws2.send_json({"type": "LEAVE_ROOM", "player_name": "Leave", "payload": {}})
            first_after_leave = ws2.receive_json()
            assert first_after_leave["type"] == "LOBBY_STATE"
            assert ws1.receive_json()["type"] == "ROOM_UPDATE"
            assert ws1.receive_json()["type"] == "GAME_STATE"

            # Subsequent actions in old room must NOT leak GAME_STATE / GAME_OVER to ws2
            ws1.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "Stay",
                    "room_code": code,
                    "game_type": "qa_trivia",
                    "payload": {"action": "answer", "data": {"choice": 0}},
                }
            )
            assert ws1.receive_json()["type"] == "GAME_STATE"
            ws2.send_json({"type": "SET_NAME", "player_name": "Leave2", "payload": {}})
            next_on_ws2 = ws2.receive_json()
            assert next_on_ws2["type"] == "LOBBY_STATE"


def test_party_takeover_rematch_reconnect_returns_to_lobby():
    import time
    from backend.main import room_manager

    with TestClient(app) as client:
        with client.websocket_connect("/ws/tk_1") as ws1:
            ws1.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "HostT", "payload": {}})
            ws1.receive_json()

            with client.websocket_connect("/ws/tk_2") as ws2:
                lobby2 = ws2.receive_json()
                secret2 = lobby2["private_state"]["session_secret"]
                ws2.send_json({"type": "SET_NAME", "player_name": "DropT", "payload": {}})
                ws2.receive_json()

                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "HostT",
                        "game_type": "uno",
                        "payload": {"action": "create", "data": {"is_public": True}},
                    }
                )
                code = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "DropT", "room_code": code, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "type": "START_GAME",
                        "player_name": "HostT",
                        "room_code": code,
                        "game_type": "uno",
                        "payload": {"action": "start", "data": {}},
                    }
                )
                for _ in range(3):
                    ws1.receive_json()
                    ws2.receive_json()

            assert ws1.receive_json()["type"] == "ROOM_UPDATE"
            assert ws1.receive_json()["type"] == "GAME_STATE"
            assert ws1.receive_json()["type"] == "PRIVATE_STATE"
            room = room_manager.rooms[code]
            room.disconnect_deadlines["tk_2"] = time.time() - 1.0
            st_takeover, _ = _recv_until_type(ws1, "GAME_STATE")
            assert any(p["id"] == "tk_2" and p["is_bot"] for p in st_takeover["players"])

            # Finish match via last card play on ws1 and immediately rematch
            room.game.hands["tk_1"] = [
                {"id": 9999, "color": room.game.active_color, "kind": "9", "label": "9", "points": 9}
            ]
            room.game.turn_idx = 0
            room.game.turn_player_id = "tk_1"
            ws1.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "HostT",
                    "room_code": code,
                    "game_type": "uno",
                    "payload": {"action": "play", "data": {"index": 0}},
                }
            )
            _recv_until_type(ws1, "GAME_OVER")

            ws1.send_json(
                {
                    "type": "GAME_ACTION",
                    "player_name": "HostT",
                    "room_code": code,
                    "game_type": "uno",
                    "payload": {"action": "rematch", "data": {}},
                }
            )
            _recv_until_type(ws1, "GAME_STARTED")
            assert room_manager.clients["tk_2"].room_code is None

            # Reconnecting tk_2 after rematch must receive LOBBY_STATE, never stale ROOM_JOINED into bot seat
            with client.websocket_connect(f"/ws/tk_2?secret={secret2}") as ws2_back:
                msg = ws2_back.receive_json()
                assert msg["type"] == "LOBBY_STATE"


def test_malformed_json_null_name_invalid_ints_spectator_blocks_and_session_secret():
    from starlette.websockets import WebSocketDisconnect
    from backend.main import room_manager

    with TestClient(app) as client:
        with client.websocket_connect("/ws/sec1") as ws1:
            lobby = ws1.receive_json()
            secret1 = lobby["private_state"]["session_secret"]
            assert isinstance(secret1, str) and len(secret1) >= 16

            # 1. Malformed JSON & non-object JSON
            ws1.send_text("{not valid json")
            err1 = ws1.receive_json()
            assert err1["type"] == "ERROR"
            assert "Malformed" in err1["message"]

            ws1.send_json([1, 2, 3])
            err2 = ws1.receive_json()
            assert err2["type"] == "ERROR"

            # 2. JSON null player_name must not become "None"
            ws1.send_json({"type": "SET_NAME", "player_name": None, "payload": {}})
            err3 = ws1.receive_json()
            assert err3["type"] == "ERROR"
            assert room_manager.clients["sec1"].name == ""

            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": None,
                    "game_type": "snake",
                    "payload": {"action": "create", "data": {"solo": True}},
                }
            )
            err4 = ws1.receive_json()
            assert err4["type"] == "ERROR"

            ws1.send_json({"type": "SET_NAME", "player_name": "SecHost", "payload": {}})
            assert ws1.receive_json()["type"] == "LOBBY_STATE"

            # 3. Invalid bot_count inputs
            for bad_bots in ("abc", True, -2):
                ws1.send_json(
                    {
                        "type": "CREATE_ROOM",
                        "player_name": "SecHost",
                        "game_type": "chess",
                        "payload": {"action": "create", "data": {"bot_count": bad_bots}},
                    }
                )
                err_b = ws1.receive_json()
                assert err_b["type"] == "ERROR"

            # 4. Invalid solo launch must not leave room stored
            bad_chess = [[None] * 8 for _ in range(8)]
            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "SecHost",
                    "game_type": "chess",
                    "payload": {
                        "action": "create",
                        "data": {"solo": True, "settings": {"custom_board": bad_chess}},
                    },
                }
            )
            err_solo = ws1.receive_json()
            assert err_solo["type"] == "ERROR"
            assert room_manager.clients["sec1"].room_code is None
            assert len(room_manager.rooms) == 0

            # 5. Session secret protects active session hijacking & wrong secret reconnects
            with pytest.raises(WebSocketDisconnect) as exc_no_sec:
                with client.websocket_connect("/ws/sec1") as ws_hijack:
                    err_h = ws_hijack.receive_json()
                    assert err_h["type"] == "ERROR"
                    ws_hijack.receive_json()
            assert exc_no_sec.value.code == 4003

            with pytest.raises(WebSocketDisconnect) as exc_bad_sec:
                with client.websocket_connect("/ws/sec1?secret=wrong_secret") as ws_bad:
                    err_b = ws_bad.receive_json()
                    assert err_b["type"] == "ERROR"
                    ws_bad.receive_json()
            assert exc_bad_sec.value.code == 4003

            # Launch a Chess game & test mid-game SET_NAME spoof block + spectator action/rematch blocks
            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "SecHost",
                    "game_type": "chess",
                    "payload": {"action": "create", "data": {"solo": True, "is_public": True}},
                }
            )
            code = ws1.receive_json()["room_code"]
            ws1.receive_json()  # GAME_STARTED
            ws1.receive_json()  # GAME_STATE

            ws1.send_json({"type": "SET_NAME", "player_name": "Spoofer", "payload": {}})
            err_name = ws1.receive_json()
            assert err_name["type"] == "ERROR"

            with client.websocket_connect("/ws/sec_spec") as ws_sp:
                ws_sp.receive_json()
                ws_sp.send_json({"type": "SET_NAME", "player_name": "Spec", "payload": {}})
                ws_sp.receive_json()
                ws_sp.send_json({"type": "JOIN_ROOM", "player_name": "Spec", "room_code": code, "payload": {}})
                ws_sp.receive_json()  # ROOM_JOINED
                ws_sp.receive_json()  # GAME_STATE

                for act, d in (
                    ("move", {"from": "e2", "to": "e4"}),
                    ("resign", {}),
                    ("rematch", {}),
                    ("add_bot", {}),
                ):
                    ws_sp.send_json(
                        {
                            "type": "GAME_ACTION",
                            "player_name": "Spec",
                            "room_code": code,
                            "game_type": "chess",
                            "payload": {"action": act, "data": d},
                        }
                    )
                    err_sp = ws_sp.receive_json()
                    assert err_sp["type"] == "ERROR"

        # Valid secret reconnect after clean disconnect succeeds
        with client.websocket_connect(f"/ws/sec1?secret={secret1}") as ws1_back:
            msg = ws1_back.receive_json()
            assert msg["type"] == "LOBBY_STATE"


@pytest.mark.parametrize("game_type", ["skru", "minesweeper", "dominoes", "uno", "globe"])
def test_private_state_isolation_across_hidden_info_games(game_type: str):
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/{game_type}_p1") as ws1, client.websocket_connect(
            f"/ws/{game_type}_p2"
        ) as ws2:
            ws1.receive_json()
            ws2.receive_json()
            ws1.send_json({"type": "SET_NAME", "player_name": "Alice", "payload": {}})
            ws1.receive_json()
            ws2.send_json({"type": "SET_NAME", "player_name": "Bob", "payload": {}})
            ws2.receive_json()

            settings = {"mode": "flag", "rounds": 4} if game_type == "globe" else {"difficulty": "easy"}
            ws1.send_json(
                {
                    "type": "CREATE_ROOM",
                    "player_name": "Alice",
                    "game_type": game_type,
                    "payload": {"action": "create", "data": {"is_public": True, "settings": settings}},
                }
            )
            code = ws1.receive_json()["room_code"]
            ws2.receive_json()
            ws2.send_json({"type": "JOIN_ROOM", "player_name": "Bob", "room_code": code, "payload": {}})
            ws2.receive_json()
            ws1.receive_json()

            ws1.send_json(
                {
                    "type": "START_GAME",
                    "player_name": "Alice",
                    "room_code": code,
                    "game_type": game_type,
                    "payload": {"action": "start", "data": {}},
                }
            )
            s1, g1, p1 = ws1.receive_json(), ws1.receive_json(), ws1.receive_json()
            s2, g2, p2 = ws2.receive_json(), ws2.receive_json(), ws2.receive_json()
            assert [s1["type"], g1["type"], p1["type"]] == ["GAME_STARTED", "GAME_STATE", "PRIVATE_STATE"]
            assert [s2["type"], g2["type"], p2["type"]] == ["GAME_STARTED", "GAME_STATE", "PRIVATE_STATE"]
            assert s1["private_state"] == {} and g1["private_state"] == {}
            assert s2["private_state"] == {} and g2["private_state"] == {}

            priv1 = p1["private_state"]
            priv2 = p2["private_state"]
            pub1 = g1["public_state"]

            if game_type == "skru":
                assert len(priv1["initial_bottom"]) == 2
                assert len(priv2["initial_bottom"]) == 2
                assert priv1["initial_bottom"] != priv2["initial_bottom"]
            elif game_type == "minesweeper":
                assert "mines" not in pub1
                assert priv1["mines"] == []
                assert priv2["mines"] == []
                ws1.send_json(
                    {
                        "type": "GAME_ACTION",
                        "player_name": "Alice",
                        "room_code": code,
                        "game_type": "minesweeper",
                        "payload": {"action": "reveal", "data": {"r": 0, "c": 0}},
                    }
                )
                assert ws1.receive_json()["type"] == "GAME_STATE"
                ms_p1 = ws1.receive_json()
                assert ws2.receive_json()["type"] == "GAME_STATE"
                ms_p2 = ws2.receive_json()
                assert len(ms_p1["private_state"]["revealed"]) >= 1
                assert ms_p1["private_state"]["mines"] == []
                assert ms_p2["private_state"]["revealed"] == []
            elif game_type == "dominoes":
                assert "hands" not in pub1
                assert len(priv1["hand"]) == 7 and len(priv2["hand"]) == 7
                assert {tuple(t) for t in priv1["hand"]}.isdisjoint({tuple(t) for t in priv2["hand"]})
            elif game_type == "uno":
                assert "hands" not in pub1
                assert pub1["revealed_hands"] == {}
                assert len(priv1["hand"]) == 7 and len(priv2["hand"]) == 7
                assert {c["id"] for c in priv1["hand"]}.isdisjoint({c["id"] for c in priv2["hand"]})
            elif game_type == "globe":
                assert "flag_code" not in pub1["question"]
                assert pub1["question"]["flag_svg"].startswith("data:image/svg+xml;base64,")
                ws1.send_json(
                    {
                        "type": "GAME_ACTION",
                        "player_name": "Alice",
                        "room_code": code,
                        "game_type": "globe",
                        "payload": {"action": "guess", "data": {"code": "EG"}},
                    }
                )
                assert ws1.receive_json()["type"] == "GAME_STATE"
                gl_p1 = ws1.receive_json()
                assert ws2.receive_json()["type"] == "GAME_STATE"
                gl_p2 = ws2.receive_json()
                assert len(gl_p1["private_state"]["guesses"]) == 1
                assert gl_p2["private_state"]["guesses"] == []

