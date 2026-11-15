"""
Rock-Paper-Scissors & Lizard-Spock Game Logic
Supports classic 3-choice and 5-choice expanded variants with explanations.
"""
import random

# Win mapping for Classic 3-choice: (winner, loser) -> reason
CLASSIC_RULES = {
    ("rock", "scissors"): "Rock crushes scissors",
    ("scissors", "paper"): "Scissors cuts paper",
    ("paper", "rock"): "Paper covers rock",
}

# Win mapping for RPS-Lizard-Spock 5-choice
LIZARD_SPOCK_RULES = {
    ("scissors", "paper"): "Scissors cuts paper",
    ("paper", "rock"): "Paper covers rock",
    ("rock", "lizard"): "Rock crushes lizard",
    ("lizard", "spock"): "Lizard poisons Spock",
    ("spock", "scissors"): "Spock smashes scissors",
    ("scissors", "lizard"): "Scissors decapitates lizard",
    ("lizard", "paper"): "Lizard eats paper",
    ("paper", "spock"): "Paper disproves Spock",
    ("spock", "rock"): "Spock vaporizes rock",
    ("rock", "scissors"): "Rock crushes scissors",
}


def get_choices(mode="classic"):
    """Return available choices for the selected mode."""
    if mode == "lizard-spock":
        return ["rock", "paper", "scissors", "lizard", "spock"]
    return ["rock", "paper", "scissors"]


def play_round(player_choice, mode="classic"):
    """
    Play one round of Rock-Paper-Scissors.
    Returns:
        dict with player_choice, computer_choice, outcome ('win', 'loss', 'tie'), and message.
    """
    valid_choices = get_choices(mode)
    player_choice = player_choice.lower()

    if player_choice not in valid_choices:
        return {
            "error": f"Invalid choice. Choose from: {', '.join(valid_choices)}"
        }

    computer_choice = random.choice(valid_choices)

    if player_choice == computer_choice:
        return {
            "player": player_choice,
            "computer": computer_choice,
            "outcome": "tie",
            "message": f"Both chose {player_choice}. It's a tie!"
        }

    rules = LIZARD_SPOCK_RULES if mode == "lizard-spock" else CLASSIC_RULES

    if (player_choice, computer_choice) in rules:
        reason = rules[(player_choice, computer_choice)]
        return {
            "player": player_choice,
            "computer": computer_choice,
            "outcome": "win",
            "message": f"{reason} — You win!"
        }
    else:
        reason = rules.get((computer_choice, player_choice), "Opponent beat you")
        return {
            "player": player_choice,
            "computer": computer_choice,
            "outcome": "loss",
            "message": f"{reason} — Computer wins!"
        }
