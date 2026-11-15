"""
Playing Cards Module
Includes a standard 52-card deck, High-Low guessing, and classic Blackjack.
"""
import random

SUITS = [
    {"name": "hearts", "symbol": "♥", "color": "red"},
    {"name": "diamonds", "symbol": "♦", "color": "red"},
    {"name": "clubs", "symbol": "♣", "color": "black"},
    {"name": "spades", "symbol": "♠", "color": "black"},
]

RANKS = [
    {"name": "2", "bj_val": 2, "hl_val": 2},
    {"name": "3", "bj_val": 3, "hl_val": 3},
    {"name": "4", "bj_val": 4, "hl_val": 4},
    {"name": "5", "bj_val": 5, "hl_val": 5},
    {"name": "6", "bj_val": 6, "hl_val": 6},
    {"name": "7", "bj_val": 7, "hl_val": 7},
    {"name": "8", "bj_val": 8, "hl_val": 8},
    {"name": "9", "bj_val": 9, "hl_val": 9},
    {"name": "10", "bj_val": 10, "hl_val": 10},
    {"name": "J", "bj_val": 10, "hl_val": 11},
    {"name": "Q", "bj_val": 10, "hl_val": 12},
    {"name": "K", "bj_val": 10, "hl_val": 13},
    {"name": "A", "bj_val": 11, "hl_val": 14},  # Ace high in High-Low, 11/1 in Blackjack
]


def create_deck():
    """Create and shuffle a standard 52-card deck."""
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({
                "rank": rank["name"],
                "suit": suit["symbol"],
                "suit_name": suit["name"],
                "color": suit["color"],
                "bj_val": rank["bj_val"],
                "hl_val": rank["hl_val"]
            })
    random.shuffle(deck)
    return deck


# ----------------------------------------------------
# High-Low Game Logic
# ----------------------------------------------------

def high_low_new_game():
    """Start a new High-Low game with a shuffled deck and the first card revealed."""
    deck = create_deck()
    current_card = deck.pop()
    return {
        "deck": deck,
        "current_card": current_card,
        "streak": 0,
        "game_over": False,
        "message": "Game started! Guess if the next card will be Higher or Lower."
    }


def high_low_guess(deck, current_card, guess, streak):
    """
    Check the player's guess ('higher' or 'lower').
    Returns updated game state.
    """
    if not deck:
        deck = create_deck()

    next_card = deck.pop()

    # Compare rank values
    if next_card["hl_val"] == current_card["hl_val"]:
        # Tie keeps the streak alive
        return {
            "current_card": next_card,
            "streak": streak,
            "game_over": False,
            "outcome": "tie",
            "message": f"Equal value ({next_card['rank']})! Streak continues at {streak}."
        }

    is_higher = next_card["hl_val"] > current_card["hl_val"]
    correct = (guess == "higher" and is_higher) or (guess == "lower" and not is_higher)

    if correct:
        new_streak = streak + 1
        return {
            "current_card": next_card,
            "streak": new_streak,
            "game_over": False,
            "outcome": "correct",
            "message": f"Correct! It was {next_card['rank']}{next_card['suit']}. Streak is now {new_streak}!"
        }
    else:
        return {
            "current_card": next_card,
            "streak": streak,
            "game_over": True,
            "outcome": "wrong",
            "message": f"Wrong guess! It was {next_card['rank']}{next_card['suit']}. Final streak: {streak}."
        }


# ----------------------------------------------------
# Blackjack Game Logic
# ----------------------------------------------------

def calculate_hand_value(hand):
    """
    Calculate the total value of a Blackjack hand.
    Handles Aces as 11 or 1 to prevent busting.
    """
    value = 0
    aces = 0

    for card in hand:
        value += card["bj_val"]
        if card["rank"] == "A":
            aces += 1

    # If bust and we have aces counted as 11, reduce them to 1
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def blackjack_new_game():
    """Deal initial 2 cards to player and dealer."""
    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    player_score = calculate_hand_value(player_hand)
    # Dealer shows only first card initially

    is_natural_blackjack = (player_score == 21)

    return {
        "deck": deck,
        "player_hand": player_hand,
        "dealer_hand": dealer_hand,
        "player_score": player_score,
        "dealer_score": calculate_hand_value(dealer_hand),
        "game_over": is_natural_blackjack,
        "message": "Blackjack! You win!" if is_natural_blackjack else "Choose Hit or Stand."
    }


def blackjack_hit(deck, player_hand):
    """Draw one card for player and recalculate score."""
    if not deck:
        deck = create_deck()

    player_hand.append(deck.pop())
    score = calculate_hand_value(player_hand)

    if score > 21:
        return {
            "player_hand": player_hand,
            "player_score": score,
            "game_over": True,
            "outcome": "bust",
            "message": f"Bust! You scored {score}."
        }

    return {
        "player_hand": player_hand,
        "player_score": score,
        "game_over": False,
        "outcome": "continue",
        "message": f"Card dealt. Current score: {score}."
    }


def blackjack_stand(deck, player_hand, dealer_hand):
    """
    Player stands; dealer draws until reaching at least 17.
    Returns final outcome.
    """
    player_score = calculate_hand_value(player_hand)

    # Dealer draws until reaching 17 or higher
    while calculate_hand_value(dealer_hand) < 17:
        if not deck:
            deck = create_deck()
        dealer_hand.append(deck.pop())

    dealer_score = calculate_hand_value(dealer_hand)

    if dealer_score > 21:
        outcome = "win"
        message = f"Dealer busts with {dealer_score}! You win!"
    elif player_score > dealer_score:
        outcome = "win"
        message = f"You win ({player_score} vs {dealer_score})!"
    elif player_score < dealer_score:
        outcome = "loss"
        message = f"Dealer wins ({dealer_score} vs {player_score})."
    else:
        outcome = "push"
        message = f"Push (tie) at {player_score}."

    return {
        "dealer_hand": dealer_hand,
        "dealer_score": dealer_score,
        "player_score": player_score,
        "game_over": True,
        "outcome": outcome,
        "message": message
    }
