"""Milestone 1 foundation tests: engine stubs, card deck, pass-and-play, and settings."""

from __future__ import annotations

import random
import pytest

from backend.base_game import PlayerSlot
from backend.games import GAME_REGISTRY
from backend.games.connect4_game import Connect4Game
from backend.games.playing_cards_deck import (
    Card,
    PlayingCardsDeck,
    calculate_blackjack_hand,
    compare_high_low,
    compare_war_cards,
    create_memory_grid,
    evaluate_high_low_guess,
    fisher_yates_shuffle,
)
from backend.games.playing_cards_game import PlayingCardsGame
from backend.games.rock_paper_scissors_game import RockPaperScissorsGame
from backend.games.tic_tac_toe_game import TicTacToeGame
from backend.room_manager import (
    ALLOWED_SETTINGS_KEYS,
    DUEL_FORFEIT_GAMES,
    ClientSession,
    RoomManager,
)


def make_slots(count: int) -> list[PlayerSlot]:
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


# ---------------------------------------------------------------------------
# 1. Server-authoritative Stubs Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "game_cls,expected_type,min_p,max_p,supports_solo,supports_bots",
    [
        (TicTacToeGame, "tic_tac_toe", 2, 2, False, True),
        (RockPaperScissorsGame, "rock_paper_scissors", 2, 2, False, True),
        (Connect4Game, "connect4", 2, 2, False, True),
        (PlayingCardsGame, "playing_cards", 1, 2, True, True),
    ],
)
def test_stub_class_attributes_and_registration(
    game_cls, expected_type, min_p, max_p, supports_solo, supports_bots
):
    assert game_cls.GAME_TYPE == expected_type
    assert game_cls.MIN_PLAYERS == min_p
    assert game_cls.MAX_PLAYERS == max_p
    assert game_cls.SUPPORTS_SOLO == supports_solo
    assert game_cls.SUPPORTS_BOTS == supports_bots
    assert game_cls.SUPPORTS_SPECTATORS is True
    assert game_cls.SUPPORTS_CUSTOM_DIFFICULTY is False
    assert expected_type in GAME_REGISTRY
    assert GAME_REGISTRY[expected_type] is game_cls


@pytest.mark.parametrize(
    "game_cls", [TicTacToeGame, RockPaperScissorsGame, Connect4Game, PlayingCardsGame]
)
def test_stub_lifecycle_start_and_forfeit(game_cls):
    players = make_slots(game_cls.MIN_PLAYERS)
    game = game_cls("ROOM101", players)
    assert game.phase == "waiting"

    game.start_game({"difficulty": "hard"})
    assert game.phase == "playing"
    assert game.get_difficulty() == "hard"

    state = game.get_public_state()
    assert isinstance(state, dict)
    assert state["phase"] == "playing"

    # Test forfeit
    p1_id = players[0].id
    ok = game.forfeit_player(p1_id, "User conceded")
    assert ok is True
    assert game.phase == "finished"
    assert len(game.winner_ids) == 1
    if len(players) > 1:
        assert game.winner_ids[0] == players[1].id


def test_connect4_grid_sizes():
    c4 = Connect4Game("C4R1", make_slots(2))
    c4.start_game({"mode": "classic"})
    assert c4.cols == 7 and c4.rows == 6

    c4_5inrow = Connect4Game("C4R2", make_slots(2))
    c4_5inrow.start_game({"mode": "five_in_a_row"})
    assert c4_5inrow.cols == 9 and c4_5inrow.rows == 7


# ---------------------------------------------------------------------------
# 2. PlayingCardsDeck and Utilities Tests
# ---------------------------------------------------------------------------

def test_playing_cards_deck_standard_capacity_and_draw():
    deck = PlayingCardsDeck(decks_count=1, shuffle_on_init=False)
    assert deck.count() == 52
    assert deck.deck_count() == 52
    assert deck.remaining() == 52
    assert deck.total_cards() == 52
    assert not deck.is_empty()

    drawn_cards = deck.draw(5)
    assert len(drawn_cards) == 5
    assert deck.count() == 47

    one = deck.draw_one()
    assert isinstance(one, Card)
    assert deck.count() == 46

    one_dict = deck.draw_card()
    assert isinstance(one_dict, dict)
    assert "rank" in one_dict and "suit" in one_dict
    assert deck.count() == 45

    # Test peek
    peeked = deck.peek(3)
    assert len(peeked) == 3
    assert deck.count() == 45


def test_card_dataclass_methods():
    c = Card(
        id="hearts_A_0",
        suit="hearts",
        rank="A",
        value=14,
        color="red",
        symbol="♥",
        label="A♥",
    )
    d = c.to_dict()
    assert d["id"] == "hearts_A_0"
    assert d["suit"] == "hearts"
    assert d["rank"] == "A"
    assert c.blackjack_value() == 11

    reconstructed = Card.from_dict(d)
    assert reconstructed == c


def test_fisher_yates_shuffle_and_discards():
    rng = random.Random(42)
    deck = PlayingCardsDeck(decks_count=1, rng=rng)
    initial_top = deck.cards[-1]

    drawn = deck.draw(10)
    assert deck.count() == 42

    deck.discard(drawn)
    recycled = deck.reshuffle_discards()
    assert recycled == 10
    assert deck.count() == 52
    assert len(deck.discards) == 0


def test_calculate_blackjack_hand():
    # 2-card 21 (Natural Blackjack)
    hand1 = [
        {"suit": "spades", "rank": "A"},
        {"suit": "clubs", "rank": "K"},
    ]
    res1 = calculate_blackjack_hand(hand1)
    assert res1["score"] == 21
    assert res1["is_blackjack"] is True
    assert res1["is_soft"] is True
    assert res1["is_bust"] is False

    # Soft Ace demotion: A + 9 + 5 = 15 (not 25)
    hand2 = [
        {"suit": "hearts", "rank": "A"},
        {"suit": "diamonds", "rank": "9"},
        {"suit": "clubs", "rank": "5"},
    ]
    res2 = calculate_blackjack_hand(hand2)
    assert res2["score"] == 15
    assert res2["is_soft"] is False
    assert res2["is_bust"] is False

    # Bust: 10 + 8 + 5 = 23
    hand3 = [
        {"suit": "hearts", "rank": "10"},
        {"suit": "diamonds", "rank": "8"},
        {"suit": "clubs", "rank": "5"},
    ]
    res3 = calculate_blackjack_hand(hand3)
    assert res3["score"] == 23
    assert res3["is_bust"] is True


def test_compare_war_cards():
    c_ace = Card("s_A", "spades", "A", 14, "black", "♠", "A♠")
    c_king = Card("h_K", "hearts", "K", 13, "red", "♥", "K♥")
    c_king2 = Card("d_K", "diamonds", "K", 13, "red", "♦", "K♦")

    assert compare_war_cards(c_ace, c_king) == 1
    assert compare_war_cards(c_king, c_ace) == -1
    assert compare_war_cards(c_king, c_king2) == 0


def test_high_low_and_memory_grid():
    c_seven = Card("s_7", "spades", "7", 7, "black", "♠", "7♠")
    c_nine = Card("h_9", "hearts", "9", 9, "red", "♥", "9♥")
    c_seven_dup = Card("c_7", "clubs", "7", 7, "black", "♣", "7♣")

    assert compare_high_low(c_seven, c_nine) == "higher"
    assert compare_high_low(c_nine, c_seven) == "lower"
    assert compare_high_low(c_seven, c_seven_dup) == "equal"

    ok, rel = evaluate_high_low_guess(c_seven, c_nine, "higher")
    assert ok is True and rel == "higher"

    ok, rel = evaluate_high_low_guess(c_seven, c_nine, "lower")
    assert ok is False and rel == "higher"

    ok, rel = evaluate_high_low_guess(c_seven, c_seven_dup, "lower")
    assert ok is True and rel == "push"

    grid = create_memory_grid(pairs_count=8, rng=random.Random(123))
    assert len(grid) == 16
    for item in grid:
        assert "grid_index" in item
        assert "match_key" in item


# ---------------------------------------------------------------------------
# 3. RoomManager Integration Tests (Pass-and-Play & Settings)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_room_manager_settings_sanitization():
    rm = RoomManager()

    # TicTacToe
    s_ttt = rm._sanitize_settings(
        TicTacToeGame,
        "tic_tac_toe",
        {"difficulty": "hard", "mode": "extended_4x4", "grid_size": 4, "pass_and_play": True, "invalid": 123},
    )
    assert s_ttt == {
        "difficulty": "hard",
        "mode": "extended_4x4",
        "grid_size": 4,
        "pass_and_play": True,
    }

    # RockPaperScissors
    s_rps = rm._sanitize_settings(
        RockPaperScissorsGame,
        "rock_paper_scissors",
        {"mode": "lizard_spock", "format": "bo5", "rounds": 5, "pass_and_play": True},
    )
    assert s_rps["mode"] == "lizard_spock"
    assert s_rps["format"] == "bo5"
    assert s_rps["rounds"] == 5
    assert s_rps["pass_and_play"] is True

    # Connect4
    s_c4 = rm._sanitize_settings(
        Connect4Game,
        "connect4",
        {"mode": "blitz", "blitz_time": 5, "pass_and_play": True},
    )
    assert s_c4["mode"] == "blitz"
    assert s_c4["blitz_time"] == 5
    assert s_c4["pass_and_play"] is True

    # Duel forfeit inclusion
    for g in ("tic_tac_toe", "rock_paper_scissors", "connect4", "playing_cards"):
        assert g in DUEL_FORFEIT_GAMES
        assert g in ALLOWED_SETTINGS_KEYS


@pytest.mark.anyio
async def test_room_manager_pass_and_play_flow():
    rm = RoomManager()
    session = ClientSession(client_id="client_host_01")
    session.name = "HostAlice"

    # Create Pass-and-Play TicTacToe room
    await rm._on_create_room(
        session=session,
        player_name="HostAlice",
        game_type="tic_tac_toe",
        data={
            "solo": True,
            "pass_and_play": True,
            "player2_name": "LocalBob",
            "settings": {"mode": "classic", "pass_and_play": True},
        },
    )

    room = rm.rooms.get(session.room_code)
    assert room is not None
    assert room.game.phase == "playing"
    assert len(room.game.players) == 2
    assert room.game.players[0].id == "client_host_01"
    assert room.game.players[1].id == "client_host_01_p2"
    assert room.game.players[1].name == "LocalBob"
    assert room.game.settings.get("pass_and_play") is True

    # Pass-and-play action proxy
    await rm._on_game_action(
        session=session,
        action="move",
        data={"player_id": "client_host_01_p2", "cell": 4},
    )
    # The action was dispatched without "Spectators cannot perform actions" error
