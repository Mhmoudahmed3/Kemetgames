"""Server-authoritative Rock-Paper-Scissors engine supporting Classic & Lizard-Spock."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot

CLASSIC_CHOICES: tuple[str, ...] = ("rock", "paper", "scissors")
LIZARD_SPOCK_CHOICES: tuple[str, ...] = ("rock", "paper", "scissors", "lizard", "spock")

CLASSIC_BEATS: dict[str, set[str]] = {
    "rock": {"scissors"},
    "scissors": {"paper"},
    "paper": {"rock"},
}

LIZARD_SPOCK_BEATS: dict[str, set[str]] = {
    "scissors": {"paper", "lizard"},
    "paper": {"rock", "spock"},
    "rock": {"lizard", "scissors"},
    "lizard": {"spock", "paper"},
    "spock": {"scissors", "rock"},
}

WIN_REASONS: dict[tuple[str, str], str] = {
    ("scissors", "paper"): "Scissors cuts Paper",
    ("paper", "rock"): "Paper covers Rock",
    ("rock", "lizard"): "Rock crushes Lizard",
    ("lizard", "spock"): "Lizard poisons Spock",
    ("spock", "scissors"): "Spock smashes Scissors",
    ("scissors", "lizard"): "Scissors decapitates Lizard",
    ("lizard", "paper"): "Lizard eats Paper",
    ("paper", "spock"): "Paper disproves Spock",
    ("spock", "rock"): "Spock vaporizes Rock",
    ("rock", "scissors"): "Rock crushes Scissors",
}


class RockPaperScissorsGame(BaseGame):
    GAME_TYPE = "rock_paper_scissors"
    TITLE = "Rock Paper Scissors"
    CATEGORY = "Casual"
    DESCRIPTION = (
        "Classic 3-Choice and RPS-Lizard-Spock across Best-of-3, Best-of-5, and Endless Streak formats."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 2
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    SUPPORTS_CUSTOM_DIFFICULTY = False
    IS_STUB = False
    DEFAULT_SETTINGS = {
        "difficulty": "mid",
        "mode": "classic",  # classic | lizard_spock
        "format": "bo3",    # bo3 | bo5 | endless | single
        "pass_and_play": False,
    }

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.mode: str = "classic"
        self.format: str = "bo3"
        self.target_wins: int | None = 2
        self.round: int = 1
        self._commits: dict[str, str] = {}
        self.last_choices: dict[str, str] = {}
        self.last_round_winner: str | None = None
        self.last_round_reason: str = ""
        self.rounds_history: list[dict[str, Any]] = []
        self.streaks: dict[str, int] = {}
        self.max_streaks: dict[str, int] = {}
        self.stats: dict[str, dict[str, int]] = {}
        self._opponent_history: list[str] = []
        self._init_player_stats()

    def _init_player_stats(self) -> None:
        for p in self.players:
            self.streaks.setdefault(p.id, 0)
            self.max_streaks.setdefault(p.id, 0)
            self.stats.setdefault(
                p.id,
                {"wins": 0, "losses": 0, "ties": 0, "current_streak": 0, "max_streak": 0},
            )

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )

        raw_mode = str(self.settings.get("mode", "classic")).strip().lower()
        if raw_mode in ("lizard_spock", "rpsls", "5_choice", "5choice"):
            self.mode = "lizard_spock"
        else:
            self.mode = "classic"

        raw_fmt = str(self.settings.get("format", "bo3")).strip().lower()
        if raw_fmt in ("bo5", "best_of_5"):
            self.format = "bo5"
            self.target_wins = 3
        elif raw_fmt in ("endless", "streak"):
            self.format = "endless"
            self.target_wins = None
        elif raw_fmt in ("single", "1", "bo1", "best_of_1"):
            self.format = "single"
            self.target_wins = 1
        else:
            self.format = "bo3"
            self.target_wins = 2

        self.phase = "playing"
        self.started_at = time.time()
        self.turn_player_id = None
        self.winner_ids = []
        self.win_reason = ""
        self.round = 1
        self._commits.clear()
        self.last_choices.clear()
        self.last_round_winner = None
        self.last_round_reason = ""
        self.rounds_history.clear()
        self._opponent_history.clear()

        for p in self.players:
            p.score = 0
            self.streaks[p.id] = 0
            self.max_streaks.setdefault(p.id, 0)
            self.stats.setdefault(
                p.id,
                {"wins": 0, "losses": 0, "ties": 0, "current_streak": 0, "max_streak": 0},
            )
            self.stats[p.id]["current_streak"] = 0

        self.log_event(
            f"{self.TITLE} match started ({self.mode}, {self.format}, difficulty: {self.settings['difficulty']}).",
            kind="info",
        )

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if action in ("resign", "forfeit"):
            self.forfeit_player(player_id, f"{player_id} resigned.")
            return True, "Player resigned."

        if action in ("rematch", "restart"):
            self.reset_for_rematch()
            return True, "Rematch initiated."

        if self.phase != "playing":
            return False, "Game is not in playing phase."

        valid_actions = ("choose", "play", "commit", "shoot", "move")
        if action not in valid_actions:
            return False, f"Unknown action: {action}."

        acting_id = player_id
        if self.settings.get("pass_and_play") and data.get("player_id"):
            acting_id = str(data.get("player_id"))

        player = self.get_player(acting_id)
        if not player:
            return False, f"Player {acting_id} not found."

        raw_choice = data.get("choice") or data.get("move") or data.get("value")
        if not raw_choice or not isinstance(raw_choice, str):
            return False, "Missing or invalid choice."

        choice = raw_choice.strip().lower()
        allowed = LIZARD_SPOCK_CHOICES if self.mode == "lizard_spock" else CLASSIC_CHOICES
        if choice not in allowed:
            return False, f"Invalid choice '{choice}'. Allowed choices for {self.mode}: {', '.join(allowed)}."

        if acting_id in self._commits:
            return False, "You have already committed a choice for this round."

        self._commits[acting_id] = choice
        self.log_event(f"{player.name} committed a choice.", kind="info")

        # Resolve when all active players have committed
        active_ids = self.player_ids()
        if len(active_ids) >= 2 and all(pid in self._commits for pid in active_ids):
            self._resolve_round()

        return True, "Choice committed."

    def _resolve_round(self) -> None:
        if len(self.players) < 2:
            return
        p1 = self.players[0]
        p2 = self.players[1]
        c1 = self._commits.get(p1.id)
        c2 = self._commits.get(p2.id)
        if not c1 or not c2:
            return

        self.last_choices = {p1.id: c1, p2.id: c2}
        beats = LIZARD_SPOCK_BEATS if self.mode == "lizard_spock" else CLASSIC_BEATS

        if not p1.is_bot:
            self._opponent_history.append(c1)
        if not p2.is_bot:
            self._opponent_history.append(c2)

        if c1 == c2:
            round_winner = None
            reason = f"Tie! Both players picked {c1}."
            self.stats[p1.id]["ties"] += 1
            self.stats[p2.id]["ties"] += 1
        elif c2 in beats.get(c1, set()):
            round_winner = p1.id
            p1.score += 1
            action_desc = WIN_REASONS.get((c1, c2), f"{c1.capitalize()} beats {c2}")
            reason = f"{action_desc}. {p1.name} wins round {self.round}!"
            self.streaks[p1.id] += 1
            self.max_streaks[p1.id] = max(self.max_streaks[p1.id], self.streaks[p1.id])
            self.streaks[p2.id] = 0
            self.stats[p1.id]["wins"] += 1
            self.stats[p2.id]["losses"] += 1
        else:
            round_winner = p2.id
            p2.score += 1
            action_desc = WIN_REASONS.get((c2, c1), f"{c2.capitalize()} beats {c1}")
            reason = f"{action_desc}. {p2.name} wins round {self.round}!"
            self.streaks[p2.id] += 1
            self.max_streaks[p2.id] = max(self.max_streaks[p2.id], self.streaks[p2.id])
            self.streaks[p1.id] = 0
            self.stats[p2.id]["wins"] += 1
            self.stats[p1.id]["losses"] += 1

        for pid in (p1.id, p2.id):
            self.stats[pid]["current_streak"] = self.streaks[pid]
            self.stats[pid]["max_streak"] = self.max_streaks[pid]

        self.last_round_winner = round_winner
        self.last_round_reason = reason
        self.rounds_history.append({
            "round": self.round,
            "choices": dict(self.last_choices),
            "winner": round_winner,
            "reason": reason,
        })
        self.log_event(reason, kind="info" if round_winner else "warn")
        self._commits.clear()

        # Check match win condition
        if self.format == "single":
            if round_winner is not None:
                winner_slot = self.get_player(round_winner)
                w_name = winner_slot.name if winner_slot else round_winner
                self.finish_game([round_winner], f"{w_name} won the match!")
                return
        elif self.format in ("bo3", "bo5", "best_of_3", "best_of_5") and self.target_wins:
            if p1.score >= self.target_wins:
                self.finish_game(
                    [p1.id],
                    f"{p1.name} won the Best-of-{3 if self.format in ('bo3', 'best_of_3') else 5} match ({p1.score}-{p2.score})!",
                )
                return
            elif p2.score >= self.target_wins:
                self.finish_game(
                    [p2.id],
                    f"{p2.name} won the Best-of-{3 if self.format in ('bo3', 'best_of_3') else 5} match ({p2.score}-{p1.score})!",
                )
                return

        self.round += 1

    def get_public_state(self) -> dict[str, Any]:
        p1 = self.players[0] if len(self.players) > 0 else None
        p2 = self.players[1] if len(self.players) > 1 else None

        if self._commits:
            pub_choices = {p.id: (True if p.id in self._commits else None) for p in self.players}
        elif self.last_choices:
            pub_choices = dict(self.last_choices)
        else:
            pub_choices = {p.id: None for p in self.players}

        return {
            "phase": self.phase,
            "status": self.phase,
            "mode": self.mode,
            "format": self.format,
            "round": self.round,
            "target_wins": self.target_wins,
            "target_score": self.target_wins,
            "turn_player_id": self.turn_player_id,
            "winner_ids": list(self.winner_ids),
            "winner": self.winner_ids[0] if self.winner_ids else None,
            "win_reason": self.win_reason,
            "choices_committed": {p.id: (p.id in self._commits) for p in self.players},
            "choices": pub_choices,
            "last_choices": dict(self.last_choices),
            "last_round_choices": dict(self.last_choices),
            "revealed_choices": dict(self.last_choices),
            "last_round_winner": self.last_round_winner,
            "round_winner": self.last_round_winner,
            "last_round_reason": self.last_round_reason,
            "last_round_result": self.last_round_reason,
            "scores": {p.id: p.score for p in self.players},
            "p1_score": p1.score if p1 else 0,
            "p2_score": p2.score if p2 else 0,
            "streaks": dict(self.streaks),
            "p1_streak": self.streaks.get(p1.id, 0) if p1 else 0,
            "p2_streak": self.streaks.get(p2.id, 0) if p2 else 0,
            "max_streaks": dict(self.max_streaks),
            "p1_max_streak": self.max_streaks.get(p1.id, 0) if p1 else 0,
            "p2_max_streak": self.max_streaks.get(p2.id, 0) if p2 else 0,
            "stats": dict(self.stats),
            "rounds_history": list(self.rounds_history),
            "settings": dict(self.settings),
            "events": list(self.events),
        }

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        choice = self._commits.get(player_id)
        return {
            "choice": choice,
            "committed_choice": choice,
            "committed": choice is not None,
            "has_committed": choice is not None,
            "round": self.round,
        }

    def get_active_bot_ids(self) -> list[str]:
        if self.phase != "playing":
            return []
        return [p.id for p in self.players if p.is_bot and p.id not in self._commits]

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or bot_id in self._commits:
            return None

        allowed = LIZARD_SPOCK_CHOICES if self.mode == "lizard_spock" else CLASSIC_CHOICES
        beats = LIZARD_SPOCK_BEATS if self.mode == "lizard_spock" else CLASSIC_BEATS
        diff = self.get_difficulty()

        if diff == "easy" or not self.rounds_history:
            chosen = random.choice(allowed)
        elif diff == "mid":
            # Win-Stay, Lose-Shift prediction heuristic
            last_round = self.rounds_history[-1]
            last_winner = last_round.get("winner")
            last_choices = last_round.get("choices", {})
            opp_id = [pid for pid in self.player_ids() if pid != bot_id]
            opp_choice = last_choices.get(opp_id[0]) if opp_id else None

            if opp_choice and random.random() < 0.65:
                if last_winner == opp_id[0]:
                    # Opponent won with opp_choice; expect repeat -> pick what beats opp_choice
                    candidates = [c for c, defeats in beats.items() if opp_choice in defeats]
                    chosen = random.choice(candidates) if candidates else random.choice(allowed)
                else:
                    # Opponent lost; expect shift -> counter their likely shift
                    bot_last = last_choices.get(bot_id)
                    expected_shift = [c for c, defeats in beats.items() if bot_last in defeats]
                    if expected_shift:
                        shift_choice = random.choice(expected_shift)
                        counter_shift = [c for c, defeats in beats.items() if shift_choice in defeats]
                        chosen = random.choice(counter_shift) if counter_shift else random.choice(allowed)
                    else:
                        chosen = random.choice(allowed)
            else:
                chosen = random.choice(allowed)
        else:
            # Hard: 1st-order Markov transition matrix + Entropy
            if len(self._opponent_history) >= 2 and random.random() < 0.80:
                prev = self._opponent_history[-1]
                transitions: dict[str, int] = {}
                for idx in range(len(self._opponent_history) - 1):
                    if self._opponent_history[idx] == prev:
                        next_c = self._opponent_history[idx + 1]
                        transitions[next_c] = transitions.get(next_c, 0) + 1
                if transitions:
                    predicted_opp = max(transitions, key=transitions.get)
                    candidates = [c for c, defeats in beats.items() if predicted_opp in defeats]
                    chosen = random.choice(candidates) if candidates else random.choice(allowed)
                else:
                    chosen = random.choice(allowed)
            else:
                chosen = random.choice(allowed)

        return "choose", {"choice": chosen}

    def reset_for_rematch(self) -> None:
        self.start_game()

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        if self.phase not in ("pre_game", "playing"):
            return False
        remaining = [p for p in self.players if p.id != player_id]
        winner_id = remaining[0].id if remaining else player_id
        winner = self.get_player(winner_id)
        if winner:
            winner.score = max(winner.score, self.target_wins or 1)
        msg = reason or f"{player_id} forfeited."
        self.finish_game([winner_id], msg)
        return True
