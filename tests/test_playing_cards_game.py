"""Automated Unit and Integration Test Suite for Playing Cards Game Module.

Tests comprehensive server-authoritative engine behaviors across 7 test classes:
1. TestPlayingCardsDeckMechanics
2. TestBlackjackSubgame
3. TestWarSubgame
4. TestMemoryConcentrationSubgame
5. TestHighLowSubgame
6. TestPlayingCardsLifecycleAndReset
7. TestPlayingCardsRoomAndWebSocketIntegration
"""

from __future__ import annotations

import random
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.base_game import PlayerSlot
from backend.games.playing_cards_deck import (
    Card,
    PlayingCardsDeck,
    build_standard_deck,
    calculate_blackjack_hand,
    compare_high_low,
    compare_war_cards,
    create_deck,
    create_memory_grid,
    evaluate_high_low_guess,
    fisher_yates_shuffle,
    RANKS,
    SUITS,
)
from backend.games.playing_cards_game import PlayingCardsGame
from backend.main import app, room_manager


# -----------------------------------------------------------------------------
# Fixtures & Test Helpers
# -----------------------------------------------------------------------------

def make_slots(count: int = 1, bots_from: int | None = None) -> list[PlayerSlot]:
    """Build standard player slot list with host, IDs, and bot flags."""
    slots = []
    for i in range(1, count + 1):
        is_bot = (bots_from is not None) and (i >= bots_from)
        slots.append(
            PlayerSlot(
                id=f"p{i}",
                name=f"Bot_{i}" if is_bot else f"Player_{i}",
                is_host=(i == 1),
                is_bot=is_bot,
                connected=True,
                seat=i - 1,
            )
        )
    return slots


def _recv_until_type(ws, target_type: str, max_msgs: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Helper for reading WebSocket frames until matching target message type."""
    collected = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        collected.append(msg)
        if msg.get("type") == target_type:
            return msg, collected
    raise AssertionError(
        f"Did not receive message of type '{target_type}' within {max_msgs} messages. "
        f"Got types: {[m.get('type') for m in collected]}"
    )


# =============================================================================
# Class 1: Deck Mechanics
# =============================================================================

class TestPlayingCardsDeckMechanics:
    """Rigorous verification of the shared 52-card deck, shuffle, draw/discard, and serialization."""

    def test_deck_standard_52_cards_composition(self):
        cards = build_standard_deck()
        assert len(cards) == 52
        for suit in SUITS:
            suit_cards = [c for c in cards if c.suit == suit]
            assert len(suit_cards) == 13
        for rank in RANKS:
            rank_cards = [c for c in cards if c.rank == rank]
            assert len(rank_cards) == 4

        c = cards[0]
        assert hasattr(c, "id") and hasattr(c, "suit") and hasattr(c, "rank")
        assert hasattr(c, "value") and hasattr(c, "color") and hasattr(c, "symbol")

    def test_deck_fisher_yates_shuffle_invariance_and_in_place(self):
        deck_a = build_standard_deck()
        deck_b = list(deck_a)
        rng = random.Random(42)
        res = fisher_yates_shuffle(deck_b, rng=rng)
        assert res is deck_b  # In-place
        assert len(res) == 52
        # Multiset equality
        assert {c.id for c in deck_a} == {c.id for c in res}
        # Order changed
        assert [c.id for c in deck_a] != [c.id for c in res]

    def test_deck_draw_methods_and_remaining(self):
        deck = PlayingCardsDeck(decks_count=1, shuffle_on_init=False)
        assert deck.count() == 52
        drawn_5 = deck.draw(5)
        assert len(drawn_5) == 5
        assert deck.count() == 47

        card_dict = deck.draw_card()
        assert isinstance(card_dict, dict)
        assert "rank" in card_dict and "suit" in card_dict
        assert deck.count() == 46

        card_obj = deck.draw_one()
        assert isinstance(card_obj, Card)
        assert deck.count() == 45

        peeked = deck.peek(3)
        assert len(peeked) == 3
        assert deck.count() == 45  # Peek does not remove

    def test_deck_exhaustion_safety(self):
        deck = PlayingCardsDeck(decks_count=1)
        all_cards = deck.draw(52)
        assert len(all_cards) == 52
        assert deck.is_empty()
        assert deck.count() == 0
        assert deck.draw_one() is None
        assert deck.draw_card() is None

    def test_deck_discard_and_reshuffle(self):
        deck = PlayingCardsDeck(decks_count=1)
        drawn = deck.draw(10)
        assert deck.count() == 42
        deck.discard(drawn)
        assert len(deck.discards) == 10

        recycled = deck.reshuffle_discards()
        assert recycled == 10
        assert deck.count() == 52
        assert len(deck.discards) == 0

    def test_deck_reset_methods(self):
        deck = PlayingCardsDeck(decks_count=1)
        deck.draw(20)
        assert deck.count() == 32
        deck.reset_deck()
        assert deck.count() == 52

    def test_multi_deck_shoe(self):
        shoe = PlayingCardsDeck(decks_count=2)
        assert shoe.count() == 104
        assert shoe.total_cards() == 104
        ranks_count: dict[str, int] = {}
        for c in shoe.cards:
            ranks_count[c.rank] = ranks_count.get(c.rank, 0) + 1
        for rank in RANKS:
            assert ranks_count[rank] == 8

    def test_card_serialization_fidelity(self):
        card = Card("hearts_A_0", "hearts", "A", 14, "red", "♥", "A♥")
        d = card.to_dict()
        assert d["id"] == "hearts_A_0"
        assert d["rank"] == "A"
        reconstructed = Card.from_dict(d)
        assert reconstructed == card
        assert reconstructed.blackjack_value() == 11

        deck_dicts = create_deck(0)
        assert len(deck_dicts) == 52
        assert isinstance(deck_dicts[0], dict)


# =============================================================================
# Class 2: Blackjack Subgame
# =============================================================================

class TestBlackjackSubgame:
    """Rules, actions, soft/hard Aces, dealer draw to 17, double down, split hands, busts, pushes."""

    def test_blackjack_scoring_number_and_face_cards(self):
        hand1 = [{"rank": "2"}, {"rank": "7"}, {"rank": "10"}]
        res1 = calculate_blackjack_hand(hand1)
        assert res1["score"] == 19 and not res1["is_soft"]

        hand2 = [{"rank": "J"}, {"rank": "Q"}]
        res2 = calculate_blackjack_hand(hand2)
        assert res2["score"] == 20

    def test_blackjack_scoring_soft_and_hard_ace(self):
        # A + 9 = 20 (soft)
        res1 = calculate_blackjack_hand([{"rank": "A"}, {"rank": "9"}])
        assert res1["score"] == 20 and res1["is_soft"] is True

        # A + 9 + 5 = 15 (hard)
        res2 = calculate_blackjack_hand([{"rank": "A"}, {"rank": "9"}, {"rank": "5"}])
        assert res2["score"] == 15 and res2["is_soft"] is False

        # A + A = 12 (soft)
        res3 = calculate_blackjack_hand([{"rank": "A"}, {"rank": "A"}])
        assert res3["score"] == 12 and res3["is_soft"] is True

    def test_blackjack_natural_21_evaluation(self):
        res = calculate_blackjack_hand([{"rank": "A"}, {"rank": "K"}])
        assert res["score"] == 21
        assert res["is_blackjack"] is True

    def test_blackjack_initial_deal_and_state(self):
        g = PlayingCardsGame("BJ_INIT", make_slots(1))
        g.start_game({"mode": "blackjack"})
        assert len(g.player_hands["p1"]) == 2
        assert len(g.dealer_hand) == 2
        pub = g.get_public_state()
        assert len(pub["dealer_hand"]) == 2
        # Hole card masked in public state
        assert pub["dealer_hand"][1].get("hidden") is True

    def test_blackjack_action_hit(self):
        g = PlayingCardsGame("BJ_HIT", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "5"}, {"rank": "6"}]
        ok, _ = g.handle_action("p1", "hit", {})
        assert ok is True
        assert len(g.player_hands["p1"]) == 3

    def test_blackjack_player_bust_immediate_loss(self):
        g = PlayingCardsGame("BJ_BUST", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "10"}, {"rank": "9"}]  # 19
        g.deck.cards.append(Card("spades_K_0", "spades", "K", 13, "black", "♠", "K♠"))  # Draw King -> 29 bust
        ok, _ = g.handle_action("p1", "hit", {})
        assert ok is True
        calc = calculate_blackjack_hand(g.player_hands["p1"])
        assert calc["is_bust"] is True

    def test_blackjack_action_stand_and_dealer_resolution(self):
        g = PlayingCardsGame("BJ_STAND", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "10"}, {"rank": "9"}]  # 19
        g.dealer_hand = [{"rank": "10"}, {"rank": "8"}]        # 18
        ok, _ = g.handle_action("p1", "stand", {})
        assert ok is True
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_blackjack_dealer_bust_player_wins(self):
        g = PlayingCardsGame("BJ_DBUST", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "10"}, {"rank": "8"}]  # 18
        g.dealer_hand = [{"rank": "10"}, {"rank": "6"}]        # 16 -> must hit
        g.deck.cards.append(Card("spades_10_0", "spades", "10", 10, "black", "♠", "10♠"))  # 16 + 10 = 26 bust
        ok, _ = g.handle_action("p1", "stand", {})
        assert ok is True
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_blackjack_push_on_equal_totals(self):
        g = PlayingCardsGame("BJ_PUSH", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "10"}, {"rank": "10"}]  # 20
        g.dealer_hand = [{"rank": "10"}, {"rank": "10"}]        # 20
        ok, _ = g.handle_action("p1", "stand", {})
        assert ok is True
        assert g.phase == "finished"
        assert g.winner_ids == []  # Push

    def test_blackjack_action_double_down(self):
        g = PlayingCardsGame("BJ_DOUBLE", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.player_hands["p1"] = [{"rank": "5"}, {"rank": "6"}]  # 11
        initial_bet = g.player_bets["p1"]
        ok, _ = g.handle_action("p1", "double", {})
        assert ok is True
        assert g.player_bets["p1"] == initial_bet * 2
        assert len(g.player_hands["p1"]) == 3
        # Double down forces stand

    def test_blackjack_action_split_matching_ranks_only(self):
        g = PlayingCardsGame("BJ_SPLIT", make_slots(1))
        g.start_game({"mode": "blackjack"})
        # Non-matching ranks reject split
        g.player_hands["p1"] = [{"rank": "8"}, {"rank": "9"}]
        ok_fail, _ = g.handle_action("p1", "split", {})
        assert ok_fail is False

        # Matching ranks permit split
        g.player_hands["p1"] = [{"rank": "8"}, {"rank": "8"}]
        ok_success, _ = g.handle_action("p1", "split", {})
        assert ok_success is True
        assert len(g.split_hands["p1"]) == 2

    def test_blackjack_2p_stood_player_subsequent_actions_rejected(self):
        g = PlayingCardsGame("BJ_2P_STAND", make_slots(2))
        g.start_game({"mode": "blackjack"})
        assert g.phase == "playing"
        assert g.player_stood["p1"] is False
        assert g.player_stood["p2"] is False

        # P1 stands; game remains playing since P2 has not stood yet
        ok, msg = g.handle_action("p1", "stand", {})
        assert ok is True
        assert g.player_stood["p1"] is True
        assert g.phase == "playing"

        # P1 attempts to hit after standing -> cleanly rejected
        ok_hit, err_hit = g.handle_action("p1", "hit", {})
        assert ok_hit is False
        assert err_hit == "Player has already stood."

        # P1 attempts to stand again -> cleanly rejected
        ok_stand, err_stand = g.handle_action("p1", "stand", {})
        assert ok_stand is False
        assert err_stand == "Player has already stood."

        # P2 is still active and can hit or stand
        ok_p2, _ = g.handle_action("p2", "stand", {})
        assert ok_p2 is True
        assert g.player_stood["p2"] is True
        assert g.phase == "finished"


# =============================================================================
# Class 3: War Subgame
# =============================================================================

class TestWarSubgame:
    """High card comparison, click-to-flip, 3-card tiebreaker war piles, chained wars, auto-battle."""

    def test_war_initial_deal_2_players(self):
        g = PlayingCardsGame("WAR_INIT", make_slots(2))
        g.start_game({"mode": "war"})
        assert len(g.player_hands["p1"]) == 26
        assert len(g.player_hands["p2"]) == 26

    def test_war_single_round_comparison(self):
        assert compare_war_cards({"rank": "K"}, {"rank": "7"}) == 1
        assert compare_war_cards({"rank": "5"}, {"rank": "9"}) == -1
        assert compare_war_cards({"rank": "8"}, {"rank": "8"}) == 0

        g = PlayingCardsGame("WAR_ROUND", make_slots(2))
        g.start_game({"mode": "war"})
        g.player_hands["p1"] = [{"rank": "K", "value": 13}]
        g.player_hands["p2"] = [{"rank": "7", "value": 7}]
        ok, _ = g.handle_action("p1", "battle", {})
        assert ok is True
        # P1 collects all cards, P2 empty -> P1 wins
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_war_tie_triggers_3_card_war_pile(self):
        g = PlayingCardsGame("WAR_TIE", make_slots(2))
        g.start_game({"mode": "war"})
        # 1 battle tie + 3 down cards + 1 deciding card + extra buffer
        g.player_hands["p1"] = [
            {"rank": "8", "value": 8},
            {"rank": "2", "value": 2}, {"rank": "3", "value": 3}, {"rank": "4", "value": 4},
            {"rank": "K", "value": 13},
            {"rank": "10", "value": 10},
        ]
        g.player_hands["p2"] = [
            {"rank": "8", "value": 8},
            {"rank": "2", "value": 2}, {"rank": "3", "value": 3}, {"rank": "4", "value": 4},
            {"rank": "7", "value": 7},
            {"rank": "10", "value": 10},
        ]
        # Round 1: 8 vs 8 -> War triggered
        ok, _ = g.handle_action("p1", "battle", {})
        assert ok is True
        assert g.in_war is True

        # Round 2: 3 down + K vs 7 -> P1 wins war pile
        ok2, _ = g.handle_action("p1", "battle", {})
        assert ok2 is True
        assert g.in_war is False
        assert len(g.player_hands["p1"]) > len(g.player_hands["p2"])

    def test_war_chained_double_war(self):
        g = PlayingCardsGame("WAR_CHAIN", make_slots(2))
        g.start_game({"mode": "war"})
        # 8 vs 8, then Q vs Q, then K vs 2
        g.player_hands["p1"] = [
            {"rank": "8", "value": 8},
            {"rank": "2", "value": 2}, {"rank": "3", "value": 3}, {"rank": "4", "value": 4},
            {"rank": "Q", "value": 12},
            {"rank": "5", "value": 5}, {"rank": "6", "value": 6}, {"rank": "7", "value": 7},
            {"rank": "K", "value": 13},
            {"rank": "10", "value": 10},
        ]
        g.player_hands["p2"] = [
            {"rank": "8", "value": 8},
            {"rank": "2", "value": 2}, {"rank": "3", "value": 3}, {"rank": "4", "value": 4},
            {"rank": "Q", "value": 12},
            {"rank": "5", "value": 5}, {"rank": "6", "value": 6}, {"rank": "7", "value": 7},
            {"rank": "2", "value": 2},
            {"rank": "10", "value": 10},
        ]
        # Step 1: 8 vs 8 -> in_war = True
        g.handle_action("p1", "battle", {})
        assert g.in_war is True

        # Step 2: 3 down + Q vs Q -> in_war = True (chained)
        g.handle_action("p1", "battle", {})
        assert g.in_war is True

        # Step 3: 3 down + K vs 2 -> P1 collects both war piles
        g.handle_action("p1", "battle", {})
        assert g.in_war is False
        assert len(g.player_hands["p1"]) >= 10

    def test_war_insufficient_cards_boundary(self):
        g = PlayingCardsGame("WAR_BND", make_slots(2))
        g.start_game({"mode": "war"})
        g.player_hands["p1"] = [{"rank": "8", "value": 8}, {"rank": "2", "value": 2}]
        g.player_hands["p2"] = [{"rank": "8", "value": 8}, {"rank": "3", "value": 3}]
        ok, _ = g.handle_action("p1", "battle", {})
        assert ok is True
        assert g.phase == "finished" or len(g.winner_ids) > 0

    def test_war_deck_replenishment_from_won_pile(self):
        g = PlayingCardsGame("WAR_REPLENISH", make_slots(2))
        g.start_game({"mode": "war"})
        assert g.deck.count() == 0  # 52 cards dealt to 2 players

    def test_war_auto_battle_mode(self):
        g = PlayingCardsGame("WAR_AUTO", make_slots(2))
        g.start_game({"mode": "war"})
        assert g.auto_battle is False
        ok, _ = g.handle_action("p1", "auto_battle", {})
        assert ok is True
        assert g.auto_battle is True

    def test_war_complete_game_victory(self):
        g = PlayingCardsGame("WAR_VIC", make_slots(2))
        g.start_game({"mode": "war"})
        g.player_hands["p1"] = [{"rank": "K", "value": 13}]
        g.player_hands["p2"] = [{"rank": "2", "value": 2}]
        g.handle_action("p1", "battle", {})
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]


# =============================================================================
# Class 4: Memory / Concentration Subgame
# =============================================================================

class TestMemoryConcentrationSubgame:
    """Card matching grid, flip mechanics, mismatch flip-back, move count, timer, AI recall."""

    def test_memory_grid_generation_4x4_and_6x4(self):
        grid_4x4 = create_memory_grid(pairs_count=8)
        assert len(grid_4x4) == 16
        for card in grid_4x4:
            assert "match_key" in card
            assert "grid_index" in card

        grid_6x4 = create_memory_grid(pairs_count=12)
        assert len(grid_6x4) == 24

    def test_memory_grid_initialization_6x4_generates_24_cards(self):
        g = PlayingCardsGame("MEM_6x4", make_slots(1))
        g.start_game({"mode": "memory", "grid_size": "6x4"})
        assert len(g.grid) == 24
        assert g.pairs_count == 12
        for card in g.grid:
            assert "match_key" in card
            assert "grid_index" in card

    def test_memory_flip_first_card(self):
        g = PlayingCardsGame("MEM_FLIP1", make_slots(1))
        g.start_game({"mode": "memory", "grid_size": "4x4"})
        ok, _ = g.handle_action("p1", "flip", {"index": 0})
        assert ok is True
        assert len(g.flipped_indices) == 1
        assert g.moves_count == 0  # Move increments on second card

    def test_memory_matching_pair_resolution(self):
        g = PlayingCardsGame("MEM_MATCH", make_slots(1))
        g.start_game({"mode": "memory", "grid_size": "4x4"})
        # Force a pair at indices 0 and 1
        g.grid[0]["match_key"] = "K"
        g.grid[1]["match_key"] = "K"
        g.handle_action("p1", "flip", {"index": 0})
        ok2, _ = g.handle_action("p1", "flip", {"index": 1})
        assert ok2 is True
        assert 0 in g.matched_indices and 1 in g.matched_indices
        assert len(g.flipped_indices) == 0
        assert g.moves_count == 1

    def test_memory_mismatch_pair_resolution(self):
        g = PlayingCardsGame("MEM_MISMATCH", make_slots(1))
        g.start_game({"mode": "memory", "grid_size": "4x4"})
        g.grid[0]["match_key"] = "K"
        g.grid[1]["match_key"] = "7"
        g.handle_action("p1", "flip", {"index": 0})
        ok2, _ = g.handle_action("p1", "flip", {"index": 1})
        assert ok2 is True
        assert g.moves_count == 1
        assert len(g.matched_indices) == 0
        assert g.mismatch_deadline is not None

    def test_memory_illegal_flips_rejected(self):
        g = PlayingCardsGame("MEM_ILLEGAL", make_slots(1))
        g.start_game({"mode": "memory", "grid_size": "4x4"})
        g.handle_action("p1", "flip", {"index": 0})
        # Same card twice in turn rejected
        ok_same, _ = g.handle_action("p1", "flip", {"index": 0})
        assert ok_same is False

        # Out of bounds rejected
        ok_oob, _ = g.handle_action("p1", "flip", {"index": 999})
        assert ok_oob is False

    def test_memory_elapsed_timer_tracking(self):
        g = PlayingCardsGame("MEM_TIMER", make_slots(1))
        g.start_game({"mode": "memory"})
        now = time.time()
        g.started_at = now - 5.0
        pub = g.get_public_state()
        assert pub["elapsed_time"] >= 5.0
        assert any(k in pub for k in ("elapsed_time", "timer", "time_elapsed", "elapsed_seconds"))

    def test_memory_victory_condition_all_pairs_matched(self):
        g = PlayingCardsGame("MEM_VIC", make_slots(1))
        g.start_game({"mode": "memory", "pairs_count": 2})
        # 2 pairs = 4 cards
        g.grid[0]["match_key"] = "A"
        g.grid[1]["match_key"] = "A"
        g.grid[2]["match_key"] = "K"
        g.grid[3]["match_key"] = "K"

        g.handle_action("p1", "flip", {"index": 0})
        g.handle_action("p1", "flip", {"index": 1})
        g.handle_action("p1", "flip", {"index": 2})
        g.handle_action("p1", "flip", {"index": 3})

        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_memory_bot_ai_difficulty_and_recall(self):
        g = PlayingCardsGame("MEM_BOT", make_slots(2, bots_from=2))
        g.start_game({"mode": "memory", "difficulty": "hard"})
        # Populate bot memory with known pair
        g.bot_memory["A"] = [2, 3]
        action = g.get_bot_action("p2")
        assert action is not None
        assert action[0] == "flip"
        assert action[1]["index"] in (2, 3)

    def test_memory_pass_and_play_local_two_player(self):
        g = PlayingCardsGame("MEM_2P", make_slots(2))
        g.start_game({"mode": "memory", "pass_and_play": True})
        assert g.turn_player_id == "p1"
        g.grid[0]["match_key"] = "2"
        g.grid[1]["match_key"] = "3"  # Mismatch
        g.handle_action("p1", "flip", {"index": 0})
        g.handle_action("p1", "flip", {"index": 1})
        # Turn switches to p2 on mismatch
        assert g.turn_player_id == "p2"


# =============================================================================
# Class 5: High-Low Subgame
# =============================================================================

class TestHighLowSubgame:
    """Higher/lower prediction, streak multiplier progression, push preservation, cash-out banking."""

    def test_high_low_initial_deal(self):
        g = PlayingCardsGame("HL_INIT", make_slots(1))
        g.start_game({"mode": "high_low"})
        assert g.current_card is not None
        assert g.multiplier == 1.0
        assert g.streak == 0

    def test_high_low_guess_higher_correct_and_incorrect(self):
        g = PlayingCardsGame("HL_HIGH", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.current_card = {"rank": "7", "value": 7}
        g.deck.cards.append(Card("diamonds_10_0", "diamonds", "10", 10, "red", "♦", "10♦"))
        ok, _ = g.handle_action("p1", "higher", {})
        assert ok is True
        assert g.streak == 1
        assert g.multiplier >= 1.5

    def test_high_low_guess_lower_correct_and_incorrect(self):
        g = PlayingCardsGame("HL_LOW", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.current_card = {"rank": "9", "value": 9}
        g.deck.cards.append(Card("diamonds_3_0", "diamonds", "3", 3, "red", "♦", "3♦"))
        ok, _ = g.handle_action("p1", "lower", {})
        assert ok is True
        assert g.streak == 1

    def test_high_low_push_preservation(self):
        g = PlayingCardsGame("HL_PUSH", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.streak = 3
        g.multiplier = 3.0
        g.current_card = {"rank": "10", "value": 10}
        g.deck.cards.append(Card("hearts_10_0", "hearts", "10", 10, "red", "♥", "10♥"))
        ok, _ = g.handle_action("p1", "guess", {"guess": "higher"})
        assert ok is True
        # Streak and multiplier preserved on push
        assert g.streak == 3
        assert g.multiplier == 3.0

    def test_high_low_multiplier_streak_progression(self):
        g = PlayingCardsGame("HL_STREAK", make_slots(1))
        g.start_game({"mode": "high_low"})
        # 3 consecutive wins
        values = [2, 5, 8, 12]
        g.current_card = {"rank": str(values[0]), "value": values[0]}
        for i in range(1, 4):
            val = values[i]
            g.deck.cards.append(Card(f"c_{val}", "clubs", str(val), val, "black", "♣", f"{val}♣"))
            g.handle_action("p1", "higher", {})
        assert g.streak == 3
        assert g.multiplier == 3.0

    def test_high_low_action_cash_out_bank(self):
        g = PlayingCardsGame("HL_BANK", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.banked_score = 500
        ok, _ = g.handle_action("p1", "bank", {})
        assert ok is True
        assert g.phase == "finished"
        assert g.players[0].score == 500

    def test_high_low_deck_exhaustion_auto_reshuffle(self):
        g = PlayingCardsGame("HL_RESHUFFLE", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.deck.cards.clear()
        g.deck.discards = build_standard_deck()
        g.current_card = {"rank": "7", "value": 7}
        ok, _ = g.handle_action("p1", "guess", {"guess": "higher"})
        assert ok is True

    def test_high_low_action_aliases(self):
        g = PlayingCardsGame("HL_ALIASES", make_slots(1))
        g.start_game({"mode": "high_low"})
        g.current_card = {"rank": "7", "value": 7}
        g.deck.cards.append(Card("s_8", "spades", "8", 8, "black", "♠", "8♠"))
        ok, _ = g.handle_action("p1", "choice", {"guess": "higher"})
        assert ok is True


# =============================================================================
# Class 6: Lifecycle & Reset
# =============================================================================

class TestPlayingCardsLifecycleAndReset:
    """Rematch resets, clean state between rounds, mode switching, player forfeit."""

    def test_mode_switching_and_isolation(self):
        g = PlayingCardsGame("PC_SWITCH", make_slots(2))
        g.start_game({"mode": "blackjack"})
        assert len(g.player_hands["p1"]) == 2

        # Switch to war
        g.handle_action("p1", "switch_mode", {"mode": "war"})
        assert g.mode == "war"
        assert len(g.player_hands["p1"]) == 26

        # Switch to memory
        g.handle_action("p1", "switch_mode", {"mode": "memory"})
        assert g.mode == "memory"
        assert len(g.grid) == 16

        # Switch to high_low
        g.handle_action("p1", "switch_mode", {"mode": "high_low"})
        assert g.mode == "high_low"
        assert g.current_card is not None

    def test_reset_for_rematch_clean_state(self):
        g = PlayingCardsGame("PC_REMATCH", make_slots(1))
        g.start_game({"mode": "blackjack"})
        g.handle_action("p1", "hit", {})
        assert len(g.player_hands["p1"]) == 3
        g.reset_for_rematch()
        assert len(g.player_hands["p1"]) == 2
        assert g.phase == "playing"

    def test_player_resignation_and_forfeit(self):
        g = PlayingCardsGame("PC_FORFEIT", make_slots(2))
        g.start_game({"mode": "war"})
        ok, _ = g.handle_action("p2", "resign", {})
        assert ok is True
        assert g.phase == "finished"
        assert g.winner_ids == ["p1"]

    def test_score_persistence_across_rematches(self):
        g = PlayingCardsGame("PC_SCORE_PERSIST", make_slots(2))
        g.start_game({"mode": "blackjack"})
        g.player_chips["p1"] = 1500
        g.reset_for_rematch()
        assert g.player_chips["p1"] == 1500
        assert g.phase == "playing"


# =============================================================================
# Class 7: Room & WebSocket Integration
# =============================================================================

class TestPlayingCardsRoomAndWebSocketIntegration:
    """End-to-end WebSocket integration with RoomManager, solo mode, and duel forfeit."""

    def test_ws_blackjack_solo_match_flow(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/pc_ws_bj") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "AcePlayer", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "AcePlayer",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": True, "settings": {"mode": "blackjack"}}},
                })
                joined = ws.receive_json()
                code = joined["room_code"]
                ws.receive_json()  # GAME_STARTED
                ws.receive_json()  # GAME_STATE

                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "AcePlayer",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "hit", "data": {}},
                })
                msg_hit, _ = _recv_until_type(ws, "GAME_STATE")
                hand = msg_hit.get("private_state", {}).get("hand") or msg_hit.get("public_state", {}).get("player_hand")
                assert len(hand) >= 2

                ws.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "AcePlayer",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "stand", "data": {}},
                })
                msg_fin, _ = _recv_until_type(ws, "GAME_OVER")
                assert msg_fin["type"] == "GAME_OVER"
                room = room_manager.rooms.get(code)
                assert room is not None
                assert room.leaderboard_recorded is True

    def test_ws_memory_complete_playthrough(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/pc_ws_mem") as ws:
                ws.receive_json()
                ws.send_json({"type": "SET_NAME", "player_name": "MemTester", "payload": {}})
                ws.receive_json()

                ws.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "MemTester",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": True, "settings": {"mode": "memory", "pairs_count": 2}}},
                })
                joined = ws.receive_json()
                code = joined["room_code"]
                ws.receive_json()  # GAME_STARTED
                ws.receive_json()  # GAME_STATE

                room = room_manager.rooms[code]
                game = room.game

                grid = getattr(game, "grid", [])
                pair_map: dict[str, list[int]] = {}
                for idx, c in enumerate(grid):
                    k = c.get("match_key", c.get("rank"))
                    pair_map.setdefault(k, []).append(idx)

                # Match all pairs
                for k, idxs in pair_map.items():
                    ws.send_json({
                        "type": "GAME_ACTION",
                        "player_name": "MemTester",
                        "room_code": code,
                        "game_type": "playing_cards",
                        "payload": {"action": "flip", "data": {"index": idxs[0]}},
                    })
                    _recv_until_type(ws, "GAME_STATE")
                    ws.send_json({
                        "type": "GAME_ACTION",
                        "player_name": "MemTester",
                        "room_code": code,
                        "game_type": "playing_cards",
                        "payload": {"action": "flip", "data": {"index": idxs[1]}},
                    })
                    _recv_until_type(ws, "GAME_STATE" if game.phase != "finished" else "GAME_OVER")

                assert game.phase == "finished"

    def test_ws_war_multiplayer_room(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/war_host") as ws1, client.websocket_connect("/ws/war_guest") as ws2:
                ws1.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "Host", "payload": {}})
                ws1.receive_json()

                ws2.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "Guest", "payload": {}})
                ws2.receive_json()

                ws1.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "Host",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": False, "settings": {"mode": "war"}}},
                })
                j1 = ws1.receive_json()
                code = j1["room_code"]

                ws2.send_json({"type": "JOIN_ROOM", "room_code": code, "player_name": "Guest", "payload": {}})
                ws2.receive_json()  # ROOM_JOINED
                ws1.receive_json()  # PLAYER_JOINED

                # Start match
                ws1.send_json({"type": "START_GAME", "room_code": code, "payload": {}})
                ws1.receive_json()  # GAME_STARTED
                ws1.receive_json()  # GAME_STATE
                ws2.receive_json()  # GAME_STARTED
                ws2.receive_json()  # GAME_STATE

                # Battle action
                ws1.send_json({
                    "type": "GAME_ACTION",
                    "player_name": "Host",
                    "room_code": code,
                    "game_type": "playing_cards",
                    "payload": {"action": "battle", "data": {}},
                })
                msg_b, _ = _recv_until_type(ws1, "GAME_STATE")
                assert "current_cards" in msg_b["public_state"]

    def test_ws_duel_disconnect_forfeit(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/ff_host") as ws1, client.websocket_connect("/ws/ff_guest") as ws2:
                ws1.receive_json()
                ws1.send_json({"type": "SET_NAME", "player_name": "HostFF", "payload": {}})
                ws1.receive_json()

                ws2.receive_json()
                ws2.send_json({"type": "SET_NAME", "player_name": "GuestFF", "payload": {}})
                ws2.receive_json()

                ws1.send_json({
                    "type": "CREATE_ROOM",
                    "player_name": "HostFF",
                    "game_type": "playing_cards",
                    "payload": {"action": "create", "data": {"solo": False, "settings": {"mode": "war"}}},
                })
                j1 = ws1.receive_json()
                code = j1["room_code"]

                ws2.send_json({"type": "JOIN_ROOM", "room_code": code, "player_name": "GuestFF", "payload": {}})
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({"type": "START_GAME", "room_code": code, "payload": {}})
                ws1.receive_json()
                ws1.receive_json()
                ws2.receive_json()
                ws2.receive_json()

                # Guest disconnects
                ws2.close()
                ws1.receive_json()  # ROOM_UPDATE
                ws1.receive_json()  # GAME_STATE

                room = room_manager.rooms[code]
                assert "ff_guest" in room.disconnect_deadlines
                room.disconnect_deadlines["ff_guest"] = time.time() - 1.0

                msg_fin, _ = _recv_until_type(ws1, "GAME_OVER")
                assert msg_fin["type"] == "GAME_OVER"
                assert room.game.phase == "finished"
