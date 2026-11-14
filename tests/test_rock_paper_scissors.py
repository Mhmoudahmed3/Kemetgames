"""Comprehensive server-authoritative unit tests for Rock-Paper-Scissors (Milestone 3)."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from backend.base_game import PlayerSlot
from backend.games.rock_paper_scissors_game import (
    CLASSIC_BEATS,
    CLASSIC_CHOICES,
    LIZARD_SPOCK_BEATS,
    LIZARD_SPOCK_CHOICES,
    WIN_REASONS,
    RockPaperScissorsGame,
)
from backend.main import app
from backend.room_manager import ClientSession, RoomManager


def make_players(count: int = 2) -> list[PlayerSlot]:
    return [
        PlayerSlot(
            id=f"p{i}",
            name=f"Player {i}",
            is_bot=False,
            is_host=(i == 1),
            connected=True,
            seat=i - 1,
        )
        for i in range(1, count + 1)
    ]


def commit_moves(game: RockPaperScissorsGame, c1: str, c2: str) -> None:
    ok1, msg1 = game.handle_action("p1", "choose", {"choice": c1})
    assert ok1, f"p1 commit failed: {msg1}"
    ok2, msg2 = game.handle_action("p2", "choose", {"choice": c2})
    assert ok2, f"p2 commit failed: {msg2}"


def _recv_until_type(ws, target_type: str, max_msgs: int = 20) -> tuple[dict, list[dict]]:
    received: list[dict] = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        received.append(msg)
        if msg.get("type") == target_type:
            return msg, received
    raise AssertionError(f"Did not receive message type {target_type} within {max_msgs} messages.")


# =============================================================================
# 1. TestRockPaperScissorsRules (Cyclic Graph Verification)
# =============================================================================


class TestRockPaperScissorsRules:
    @pytest.mark.parametrize(
        "c1,c2,expected_winner",
        [
            ("rock", "scissors", "p1"),
            ("scissors", "paper", "p1"),
            ("paper", "rock", "p1"),
            ("scissors", "rock", "p2"),
            ("paper", "scissors", "p2"),
            ("rock", "paper", "p2"),
            ("rock", "rock", None),
            ("paper", "paper", None),
            ("scissors", "scissors", None),
        ],
    )
    def test_classic_3_choice_all_9_combinations(
        self, c1: str, c2: str, expected_winner: str | None
    ):
        g = RockPaperScissorsGame("RPS_TEST_3C", make_players(2))
        g.start_game({"mode": "classic", "format": "single"})
        commit_moves(g, c1, c2)
        pub = g.get_public_state()
        round_winner = pub.get("last_round_winner")
        assert round_winner == expected_winner, (
            f"Expected {expected_winner} for {c1} vs {c2}, got {round_winner}"
        )

    def test_lizard_spock_5_choice_all_25_combinations(self):
        choices = LIZARD_SPOCK_CHOICES
        beats = LIZARD_SPOCK_BEATS
        for c1 in choices:
            for c2 in choices:
                g = RockPaperScissorsGame("RPS_TEST_5C", make_players(2))
                g.start_game({"mode": "lizard_spock", "format": "single"})
                commit_moves(g, c1, c2)
                pub = g.get_public_state()
                winner = pub.get("last_round_winner")
                if c1 == c2:
                    assert winner is None, f"Tie failed for {c1} vs {c2}"
                elif c2 in beats[c1]:
                    assert winner == "p1", f"{c1} should beat {c2}"
                else:
                    assert winner == "p2", f"{c2} should beat {c1}"

    def test_tie_handling_both_modes(self):
        # Classic tie
        g1 = RockPaperScissorsGame("RPS_TIE_CLS", make_players(2))
        g1.start_game({"mode": "classic", "format": "bo3"})
        commit_moves(g1, "rock", "rock")
        pub1 = g1.get_public_state()
        assert pub1["last_round_winner"] is None
        assert "Tie" in pub1["last_round_reason"]
        assert pub1["scores"]["p1"] == 0 and pub1["scores"]["p2"] == 0

        # Lizard-Spock tie
        g2 = RockPaperScissorsGame("RPS_TIE_LS", make_players(2))
        g2.start_game({"mode": "lizard_spock", "format": "bo3"})
        commit_moves(g2, "spock", "spock")
        pub2 = g2.get_public_state()
        assert pub2["last_round_winner"] is None
        assert "Tie" in pub2["last_round_reason"]
        assert pub2["scores"]["p1"] == 0 and pub2["scores"]["p2"] == 0

    def test_descriptive_win_reasons(self):
        for (w, l), expected_sub in WIN_REASONS.items():
            g = RockPaperScissorsGame("RPS_REASON", make_players(2))
            g.start_game({"mode": "lizard_spock", "format": "single"})
            commit_moves(g, w, l)
            pub = g.get_public_state()
            assert expected_sub in pub["last_round_reason"], (
                f"Missing '{expected_sub}' in '{pub['last_round_reason']}'"
            )


# =============================================================================
# 2. TestRockPaperScissorsMatchFormats (Format & Streak Mechanics)
# =============================================================================


class TestRockPaperScissorsMatchFormats:
    def test_single_round_format(self):
        g = RockPaperScissorsGame("RPS_SINGLE", make_players(2))
        g.start_game({"format": "single"})
        commit_moves(g, "rock", "scissors")
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]
        assert g.players[0].score == 1

    def test_best_of_3_format(self):
        g = RockPaperScissorsGame("RPS_BO3", make_players(2))
        g.start_game({"format": "bo3"})
        # Round 1: P1 wins (1-0)
        commit_moves(g, "rock", "scissors")
        assert g.phase == "playing"
        assert g.round == 2
        # Round 2: P2 wins (1-1)
        commit_moves(g, "paper", "scissors")
        assert g.phase == "playing"
        assert g.round == 3
        # Round 3: P1 wins (2-1) -> Match finish
        commit_moves(g, "scissors", "paper")
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]
        assert g.players[0].score == 2
        assert g.players[1].score == 1

    def test_best_of_5_format(self):
        g = RockPaperScissorsGame("RPS_BO5", make_players(2))
        g.start_game({"format": "bo5"})
        # P2 wins 3 rounds in a row
        for _ in range(3):
            commit_moves(g, "rock", "paper")
        assert g.phase == "finished"
        assert g.winner_ids == ["p2"]
        assert g.players[1].score == 3
        assert g.players[0].score == 0

    def test_ties_do_not_advance_match_score(self):
        g = RockPaperScissorsGame("RPS_TIE_SCORE", make_players(2))
        g.start_game({"format": "bo3"})
        commit_moves(g, "paper", "paper")
        pub = g.get_public_state()
        assert pub["scores"]["p1"] == 0
        assert pub["scores"]["p2"] == 0
        assert g.round == 2
        assert g.phase == "playing"

    def test_endless_streak_progression(self):
        g = RockPaperScissorsGame("RPS_ENDLESS", make_players(2))
        g.start_game({"format": "endless"})
        for i in range(1, 5):
            commit_moves(g, "rock", "scissors")
            pub = g.get_public_state()
            assert pub["streaks"]["p1"] == i
            assert pub["max_streaks"]["p1"] == i
            assert pub["streaks"]["p2"] == 0
            assert g.phase == "playing"

    def test_endless_streak_reset_on_loss(self):
        g = RockPaperScissorsGame("RPS_STRK_RESET", make_players(2))
        g.start_game({"format": "endless"})
        # P1 wins 2 rounds
        for _ in range(2):
            commit_moves(g, "rock", "scissors")
        assert g.streaks["p1"] == 2
        # P1 loses round 3
        commit_moves(g, "scissors", "rock")
        pub = g.get_public_state()
        assert pub["streaks"]["p1"] == 0
        assert pub["streaks"]["p2"] == 1
        assert pub["max_streaks"]["p1"] == 2

    def test_endless_max_streak_retention(self):
        g = RockPaperScissorsGame("RPS_MAX_RET", make_players(2))
        g.start_game({"format": "endless"})
        # P1 gets streak of 4
        for _ in range(4):
            commit_moves(g, "paper", "rock")
        assert g.max_streaks["p1"] == 4
        # P1 loses
        commit_moves(g, "paper", "scissors")
        assert g.streaks["p1"] == 0
        assert g.max_streaks["p1"] == 4
        # P1 wins 1
        commit_moves(g, "paper", "rock")
        assert g.streaks["p1"] == 1
        assert g.max_streaks["p1"] == 4

    def test_endless_ties_preserve_streak(self):
        g = RockPaperScissorsGame("RPS_TIE_PRESERVE", make_players(2))
        g.start_game({"format": "endless"})
        # P1 wins 2
        for _ in range(2):
            commit_moves(g, "rock", "scissors")
        assert g.streaks["p1"] == 2
        # Round 3 tie
        commit_moves(g, "spock", "spock") if g.mode == "lizard_spock" else commit_moves(g, "rock", "rock")
        pub = g.get_public_state()
        assert pub["streaks"]["p1"] == 2
        assert pub["max_streaks"]["p1"] == 2


# =============================================================================
# 3. TestSecretCommitIsolationAndInputValidation (Boundaries & Edge Cases)
# =============================================================================


class TestSecretCommitIsolationAndInputValidation:
    def test_initial_state_and_settings(self):
        g = RockPaperScissorsGame("RPS_INIT", make_players(2))
        assert g.phase == "waiting"
        g.start_game({"mode": "classic", "format": "bo3"})
        pub = g.get_public_state()
        assert pub["phase"] == "playing"
        assert pub["mode"] == "classic"
        assert pub["format"] == "bo3"
        assert pub["round"] == 1
        assert pub["target_wins"] == 2
        assert pub["scores"] == {"p1": 0, "p2": 0}

    def test_secret_commit_isolation(self):
        g = RockPaperScissorsGame("RPS_ISOLATION", make_players(2))
        g.start_game()
        ok, msg = g.handle_action("p1", "choose", {"choice": "rock"})
        assert ok

        # Public state: P1 is committed (True), choice hidden
        pub = g.get_public_state()
        assert pub["choices"]["p1"] in (None, True, "hidden", "committed")
        assert pub["choices"]["p2"] is None
        assert pub["choices_committed"]["p1"] is True
        assert pub["choices_committed"]["p2"] is False

        # P1 private state: choice is revealed
        priv1 = g.get_private_state("p1")
        assert priv1["choice"] == "rock"
        assert priv1["committed"] is True

        # P2 private state: no knowledge of P1 choice
        priv2 = g.get_private_state("p2")
        assert priv2["choice"] is None
        assert "p1_choice" not in priv2

    def test_double_commit_rejection(self):
        g = RockPaperScissorsGame("RPS_DOUBLE", make_players(2))
        g.start_game()
        ok1, _ = g.handle_action("p1", "choose", {"choice": "rock"})
        assert ok1
        ok2, msg2 = g.handle_action("p1", "choose", {"choice": "paper"})
        assert not ok2
        assert "already" in msg2.lower()

    def test_invalid_choice_rejected(self):
        g = RockPaperScissorsGame("RPS_INVALID", make_players(2))
        g.start_game()
        ok, msg = g.handle_action("p1", "choose", {"choice": "laser_gun"})
        assert not ok
        assert "invalid choice" in msg.lower()

    def test_cross_mode_choice_rejection(self):
        g = RockPaperScissorsGame("RPS_CROSS", make_players(2))
        g.start_game({"mode": "classic"})
        ok_lizard, _ = g.handle_action("p1", "choose", {"choice": "lizard"})
        assert not ok_lizard
        ok_spock, _ = g.handle_action("p1", "choose", {"choice": "spock"})
        assert not ok_spock

    def test_action_after_game_finished_rejected(self):
        g = RockPaperScissorsGame("RPS_FINISHED", make_players(2))
        g.start_game({"format": "single"})
        commit_moves(g, "rock", "scissors")
        assert g.phase == "finished"
        ok, msg = g.handle_action("p1", "choose", {"choice": "paper"})
        assert not ok
        assert "playing" in msg.lower()

    def test_spectator_action_rejected(self):
        g = RockPaperScissorsGame("RPS_SPECTATOR", make_players(2))
        g.start_game()
        ok, msg = g.handle_action("spectator_99", "choose", {"choice": "rock"})
        assert not ok
        assert "not found" in msg.lower()


# =============================================================================
# 4. TestRockPaperScissorsBot (AI Logic & Simulation)
# =============================================================================


class TestRockPaperScissorsBot:
    def test_bot_action_generation_classic(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_BOT_CLS", players)
        g.start_game({"mode": "classic"})
        act = g.get_bot_action("bot1")
        assert act is not None
        action_name, payload = act
        assert action_name == "choose"
        assert payload["choice"] in CLASSIC_CHOICES

    def test_bot_action_generation_lizard_spock(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_BOT_LS", players)
        g.start_game({"mode": "lizard_spock"})
        act = g.get_bot_action("bot1")
        assert act is not None
        action_name, payload = act
        assert action_name == "choose"
        assert payload["choice"] in LIZARD_SPOCK_CHOICES

    def test_bot_easy_randomness(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_BOT_RND", players)
        g.start_game({"mode": "classic", "difficulty": "easy"})
        moves = {g.get_bot_action("bot1")[1]["choice"] for _ in range(60)}
        assert len(moves) == 3, "Easy bot should sample all 3 classic choices across 60 trials"

    def test_bot_mid_frequency_counter(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_BOT_MID", players)
        g.start_game({"mode": "classic", "difficulty": "mid"})
        # Feed history where Human won with "rock"
        g.handle_action("p1", "choose", {"choice": "rock"})
        g.handle_action("bot1", "choose", {"choice": "scissors"})
        # Bot should tend to pick paper to beat anticipated rock repeat
        counter_choices = [g.get_bot_action("bot1")[1]["choice"] for _ in range(50)]
        paper_count = counter_choices.count("paper")
        assert paper_count > 15, "Mid bot should bias toward countering repeated winning move"

    def test_bot_hard_markov_predictor(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_BOT_HRD", players)
        g.start_game({"mode": "classic", "format": "endless", "difficulty": "hard"})
        # Feed alternating sequence rock -> paper -> rock -> paper
        for _ in range(5):
            g.handle_action("p1", "choose", {"choice": "rock"})
            g.handle_action("bot1", "choose", {"choice": "rock"})
            g.handle_action("p1", "choose", {"choice": "paper"})
            g.handle_action("bot1", "choose", {"choice": "rock"})
        # Last was paper, next predicted is rock -> bot should play paper to counter rock
        picks = [g.get_bot_action("bot1")[1]["choice"] for _ in range(50)]
        paper_count = picks.count("paper")
        assert paper_count > 20, "Hard bot should detect transition pattern and counter"

    def test_bot_active_ids_simultaneous(self):
        players = [
            PlayerSlot(id="p1", name="Human", is_bot=False),
            PlayerSlot(id="bot1", name="Bot", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_ACTIVE_BOTS", players)
        g.start_game()
        # Bot hasn't committed -> active
        assert g.get_active_bot_ids() == ["bot1"]
        # Bot commits -> not active
        g.handle_action("bot1", "choose", {"choice": "rock"})
        assert g.get_active_bot_ids() == []

    def test_bot_vs_bot_simulation(self):
        players = [
            PlayerSlot(id="b1", name="Bot 1", is_bot=True),
            PlayerSlot(id="b2", name="Bot 2", is_bot=True),
        ]
        g = RockPaperScissorsGame("RPS_SIM", players)
        g.start_game({"mode": "lizard_spock", "format": "endless", "difficulty": "hard"})
        for _ in range(50):
            act1 = g.get_bot_action("b1")
            act2 = g.get_bot_action("b2")
            assert act1 and act2
            ok1, _ = g.handle_action("b1", act1[0], act1[1])
            ok2, _ = g.handle_action("b2", act2[0], act2[1])
            assert ok1 and ok2
        assert g.round == 51
        assert len(g.rounds_history) == 50


# =============================================================================
# 5. TestRoomManagerAndSessionIntegration (Integration & Lifecycle)
# =============================================================================


class TestRoomManagerAndSessionIntegration:
    def test_room_create_and_join_multiplayer(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/rps_u1") as ws1, client.websocket_connect("/ws/rps_u2") as ws2:
                ws1.receive_json()
                ws2.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "Alice", "payload": {}})
                ws1.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "Bob", "payload": {}})
                ws2.receive_json()

                ws1.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "Alice",
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "create", "data": {"settings": {"format": "bo3"}}},
                })
                code = ws1.receive_json()["room_code"]
                ws2.receive_json()
                ws2.send_json({"type": "JOIN_ROOM", "player_name": "Bob", "room_code": code, "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({
                    "type": "START_GAME",
                    "player_name": "Alice",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws1, "GAME_STATE")
                _recv_until_type(ws2, "GAME_STATE")

                # Both play round 1
                ws1.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "Alice",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "rock"}},
                })
                _recv_until_type(ws1, "GAME_STATE")
                _recv_until_type(ws2, "GAME_STATE")

                ws2.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "Bob",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "scissors"}},
                })
                st1, _ = _recv_until_type(ws1, "GAME_STATE")
                st2, _ = _recv_until_type(ws2, "GAME_STATE")
                pub = st1["public_state"]
                assert pub["scores"]["rps_u1"] == 1
                assert pub["last_round_winner"] == "rps_u1"

    def test_pass_and_play_local_moves(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/pnp_rps") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "SoloPlayer", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "SoloPlayer",
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "create", "data": {"settings": {"pass_and_play": True, "format": "single"}}},
                })
                create_msg = ws.receive_json()
                code = create_msg["room_code"]

                ws.send_json({
                    "type": "START_GAME",
                    "player_name": "SoloPlayer",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "start", "data": {}},
                })
                _recv_until_type(ws, "GAME_STATE")

                # Commit for Player 1
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "SoloPlayer",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "paper", "player_id": "pnp_rps"}},
                })
                _recv_until_type(ws, "GAME_STATE")

                # Commit for Player 2
                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "SoloPlayer",
                    "room_code": code,
                    "game_type": "rock_paper_scissors",
                    "payload": {"action": "choose", "data": {"choice": "rock", "player_id": "pnp_rps_p2"}},
                })
                final_st, _ = _recv_until_type(ws, "GAME_STATE")
                pub = final_st["public_state"]
                assert pub["phase"] == "finished"
                assert pub["last_round_winner"] == "pnp_rps"

    def test_rematch_reset_lifecycle(self):
        g = RockPaperScissorsGame("RPS_REMATCH", make_players(2))
        g.start_game({"format": "single"})
        commit_moves(g, "rock", "scissors")
        assert g.phase == "finished"
        assert g.players[0].score == 1

        g.reset_for_rematch()
        assert g.phase == "playing"
        assert g.round == 1
        assert g.players[0].score == 0
        assert g.players[1].score == 0
        assert g.winner_ids == []

    def test_duel_forfeit_awards_win(self):
        players = make_players(2)
        g = RockPaperScissorsGame("RPS_FORFEIT", players)
        g.start_game()
        ok = g.forfeit_player("p1", "Resigned")
        assert ok is True
        assert g.phase == "finished"
        assert g.winner_ids == ["p2"]
        assert g.players[1].score >= 1
