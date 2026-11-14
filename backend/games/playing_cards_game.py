"""Server-authoritative Playing Cards game engine for Blackout Arcade.

Subclasses BaseGame to support four complete, high-fidelity subgames:
1. Blackjack (Player vs Dealer, Hit, Stand, Double Down, Split, Soft/Hard Ace scoring)
2. War (Click-to-flip, Auto-Battle, 3-card tiebreaker war piles, chained wars)
3. Memory / Concentration (3D flip grid 4x4 or 6x4, timer, move counter, bot recall)
4. High-Low (Higher/Lower guess, streak multiplier progression, push preservation, bank)
"""

from __future__ import annotations

import random
import time
from typing import Any, Sequence

from backend.base_game import BaseGame, PlayerSlot
from backend.games.playing_cards_deck import (
    Card,
    PlayingCardsDeck,
    calculate_blackjack_hand,
    compare_war_cards,
    create_deck,
    create_memory_grid,
    evaluate_high_low_guess,
)


def _get_hl_multiplier(streak: int) -> float:
    """Return streak multiplier ladder for High-Low."""
    ladder = [1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 12.0]
    if streak < len(ladder):
        return ladder[streak]
    return round(12.0 * (1.5 ** (streak - 6)), 1)


class PlayingCardsGame(BaseGame):
    GAME_TYPE = "playing_cards"
    TITLE = "Playing Cards"
    CATEGORY = "Cards"
    DESCRIPTION = (
        "Reusable 52-card deck featuring Blackjack (vs Dealer), War, "
        "Memory / Concentration, and High-Low streak multiplier."
    )
    MIN_PLAYERS = 1
    MAX_PLAYERS = 2
    SUPPORTS_SOLO = True
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    SUPPORTS_CUSTOM_DIFFICULTY = False
    IS_STUB = False

    DEFAULT_SETTINGS = {
        "difficulty": "mid",
        "mode": "blackjack",       # blackjack | war | memory | high_low
        "subgame": "blackjack",
        "grid_size": "4x4",
        "pairs_count": 8,
        "pass_and_play": False,
        "auto_battle": False,
    }

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.mode: str = "blackjack"
        self.rng: random.Random = random.Random()
        self.deck: PlayingCardsDeck = PlayingCardsDeck(decks_count=1, rng=self.rng)

        # Blackjack State
        self.player_hands: dict[str, list[Any]] = {}
        self.dealer_hand: list[Any] = []
        self.dealer_revealed: bool = False
        self.split_hands: dict[str, list[list[Any]]] = {}
        self.active_hand_indices: dict[str, int] = {}
        self.player_bets: dict[str, int] = {}
        self.player_chips: dict[str, int] = {}
        self.player_stood: dict[str, bool] = {}

        # War State
        self.war_pile: list[Any] = []
        self.in_war: bool = False
        self.current_cards: dict[str, Any] = {}
        self.auto_battle: bool = False
        self.last_battle_time: float = 0.0
        self.war_round_count: int = 0

        # Memory / Concentration State
        self.grid: list[dict[str, Any]] = []
        self.matched_indices: set[int] = set()
        self.flipped_indices: list[int] = []
        self.moves_count: int = 0
        self.pairs_count: int = 8
        self.mismatch_deadline: float | None = None
        self.bot_memory: dict[str, list[int]] = {}

        # High-Low State
        self.current_card: dict[str, Any] | None = None
        self.next_card: dict[str, Any] | None = None
        self.streak: int = 0
        self.max_streak: int = 0
        self.multiplier: float = 1.0
        self.banked_score: int = 0
        self.card_history: list[dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # Aliases for Contract & Test Compatibility
    # -------------------------------------------------------------------------

    @property
    def player_decks(self) -> dict[str, list[Any]]:
        """Alias for player_hands expected by War tests."""
        return self.player_hands

    @player_decks.setter
    def player_decks(self, value: dict[str, list[Any]]) -> None:
        self.player_hands = value

    @property
    def cards(self) -> list[dict[str, Any]]:
        """Alias for Memory grid expected by tests."""
        return self.grid

    @cards.setter
    def cards(self, value: list[dict[str, Any]]) -> None:
        self.grid = value

    @property
    def deck_count(self) -> int:
        return self.deck.count()

    @property
    def war_active(self) -> bool:
        return self.in_war

    # -------------------------------------------------------------------------
    # Game Initialization & Lifecycle
    # -------------------------------------------------------------------------

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )

        mode_req = self.settings.get("mode") or self.settings.get("subgame") or "blackjack"
        self.mode = str(mode_req).strip().lower()
        if self.mode not in ("blackjack", "war", "memory", "high_low"):
            self.mode = "blackjack"

        self.phase = "playing"
        self.started_at = time.time()
        self.turn_player_id = self.players[0].id if self.players else None

        self._init_subgame()
        self.log_event(f"{self.TITLE} match started ({self.mode}).", kind="info")

    def _init_subgame(self) -> None:
        """Initialize data structures specific to the active subgame."""
        p_ids = [p.id for p in self.players]
        if not p_ids:
            p_ids = ["p1"]

        if self.mode == "blackjack":
            self.deck = PlayingCardsDeck(decks_count=4, rng=self.rng)
            self.player_hands = {pid: [] for pid in p_ids}
            self.split_hands = {pid: [] for pid in p_ids}
            self.active_hand_indices = {pid: 0 for pid in p_ids}
            self.player_bets = {pid: self.player_bets.get(pid, 25) for pid in p_ids}
            self.player_chips = {pid: self.player_chips.get(pid, 1000) for pid in p_ids}
            self.player_stood = {pid: False for pid in p_ids}
            self.dealer_revealed = False

            # Deal 2 cards to each player and 2 to dealer
            for pid in p_ids:
                c1 = self.deck.draw_card()
                c2 = self.deck.draw_card()
                self.player_hands[pid] = [c1, c2]

            d1 = self.deck.draw_card()
            d2 = self.deck.draw_card()
            self.dealer_hand = [d1, d2]

        elif self.mode == "war":
            self.deck = PlayingCardsDeck(decks_count=1, rng=self.rng)
            self.war_pile = []
            self.in_war = False
            self.current_cards = {}
            self.war_round_count = 0
            self.auto_battle = bool(self.settings.get("auto_battle", False))

            p1 = p_ids[0]
            p2 = p_ids[1] if len(p_ids) > 1 else "p2"
            self.player_hands = {
                p1: [self.deck.draw_card() for _ in range(26)],
                p2: [self.deck.draw_card() for _ in range(26)],
            }

        elif self.mode == "memory":
            if self.settings.get("grid_size") == "6x4":
                self.pairs_count = 12
            elif "pairs_count" in self.settings:
                self.pairs_count = max(2, min(26, int(self.settings["pairs_count"])))
            else:
                self.pairs_count = 8

            self.grid = create_memory_grid(pairs_count=self.pairs_count, rng=self.rng)
            self.matched_indices = set()
            self.flipped_indices = []
            self.moves_count = 0
            self.mismatch_deadline = None
            self.bot_memory = {}

        elif self.mode == "high_low":
            self.deck = PlayingCardsDeck(decks_count=1, rng=self.rng)
            self.current_card = self.deck.draw_card()
            self.next_card = None
            self.streak = 0
            self.max_streak = 0
            self.multiplier = 1.0
            self.banked_score = 0
            self.card_history = [self.current_card] if self.current_card else []

    def reset_for_rematch(self) -> None:
        """Reset match cleanly between rounds without stale state."""
        super().reset_for_rematch()
        self.phase = "playing"
        self.started_at = time.time()
        self.turn_player_id = self.players[0].id if self.players else None
        self._init_subgame()

    # -------------------------------------------------------------------------
    # Action Handling
    # -------------------------------------------------------------------------

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Game is not in playing phase."

        act = action.strip().lower()
        if act in ("resign", "forfeit"):
            self.forfeit_player(player_id, f"{player_id} resigned.")
            return True, ""

        if act == "switch_mode":
            new_mode = str(data.get("mode", "")).strip().lower()
            if new_mode in ("blackjack", "war", "memory", "high_low"):
                self.mode = new_mode
                self._init_subgame()
                return True, f"Switched mode to {new_mode}"
            return False, f"Unknown mode: {new_mode}"

        if self.mode == "blackjack":
            return self._handle_blackjack_action(player_id, act, data)
        elif self.mode == "war":
            return self._handle_war_action(player_id, act, data)
        elif self.mode == "memory":
            return self._handle_memory_action(player_id, act, data)
        elif self.mode == "high_low":
            return self._handle_high_low_action(player_id, act, data)

        return False, f"Unsupported action '{action}' for mode '{self.mode}'."

    # -------------------------------------------------------------------------
    # Subgame 1: Blackjack Action Flow
    # -------------------------------------------------------------------------

    def _handle_blackjack_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        hand = self.player_hands.get(player_id)
        if hand is None:
            # Fallback for solo/first player
            player_id = self.players[0].id if self.players else player_id
            hand = self.player_hands.setdefault(player_id, [])

        if self.player_stood.get(player_id, False):
            return False, "Player has already stood."

        if action == "hit":
            score_res = calculate_blackjack_hand(hand)
            if score_res["is_bust"]:
                return False, "Hand is already busted."
            card = self.deck.draw_card()
            if card:
                hand.append(card)
            splits = self.split_hands.get(player_id, [])
            sub_idx = self.active_hand_indices.get(player_id, 0)
            if splits and sub_idx < len(splits):
                splits[sub_idx] = list(hand)
            return True, ""

        elif action == "stand":
            splits = self.split_hands.get(player_id, [])
            sub_idx = self.active_hand_indices.get(player_id, 0)
            if splits and sub_idx == 0 and len(splits) > 1:
                # Advance to second split hand
                self.active_hand_indices[player_id] = 1
                self.player_hands[player_id] = splits[1]
            else:
                self.player_stood[player_id] = True
                self._check_blackjack_completion()
            return True, ""

        elif action in ("double", "double_down"):
            if len(hand) != 2:
                return False, "Double down is only permitted on the initial 2-card hand."
            self.player_bets[player_id] = self.player_bets.get(player_id, 25) * 2
            card = self.deck.draw_card()
            if card:
                hand.append(card)
            splits = self.split_hands.get(player_id, [])
            sub_idx = self.active_hand_indices.get(player_id, 0)
            if splits and sub_idx < len(splits):
                splits[sub_idx] = list(hand)

            if splits and sub_idx == 0 and len(splits) > 1:
                self.active_hand_indices[player_id] = 1
                self.player_hands[player_id] = splits[1]
            else:
                self.player_stood[player_id] = True
                self._check_blackjack_completion()
            return True, ""

        elif action == "split":
            if len(hand) != 2:
                return False, "Can only split a hand with exactly 2 cards."
            r1 = hand[0].get("rank") if isinstance(hand[0], dict) else getattr(hand[0], "rank", None)
            r2 = hand[1].get("rank") if isinstance(hand[1], dict) else getattr(hand[1], "rank", None)
            if r1 != r2:
                return False, "Cannot split cards of different ranks."

            c1, c2 = hand[0], hand[1]
            hand0 = [c1, self.deck.draw_card()]
            hand1 = [c2, self.deck.draw_card()]
            self.split_hands[player_id] = [hand0, hand1]
            self.active_hand_indices[player_id] = 0
            self.player_hands[player_id] = hand0
            return True, ""

        return False, f"Unknown Blackjack action: {action}"

    def _check_blackjack_completion(self) -> None:
        """Resolve dealer draw and determine winner when all player hands have stood."""
        all_stood = all(self.player_stood.get(p.id, False) for p in self.players)
        if not all_stood:
            return

        # Dealer turn: reveal hole card and hit until total >= 17
        self.dealer_revealed = True
        dealer_res = calculate_blackjack_hand(self.dealer_hand)
        while dealer_res["score"] < 17:
            card = self.deck.draw_card()
            if not card:
                break
            self.dealer_hand.append(card)
            dealer_res = calculate_blackjack_hand(self.dealer_hand)

        d_score = dealer_res["score"]
        d_bust = dealer_res["is_bust"]

        winning_players: list[str] = []
        for p in self.players:
            pid = p.id
            hands_to_evaluate = self.split_hands.get(pid) or [self.player_hands.get(pid, [])]
            for h in hands_to_evaluate:
                p_res = calculate_blackjack_hand(h)
                if p_res["is_bust"]:
                    continue
                if d_bust or p_res["score"] > d_score:
                    winning_players.append(pid)
                    break

        if winning_players:
            for wid in winning_players:
                wp = self.get_player(wid)
                if wp:
                    wp.score += 1
            self.finish_game(winning_players, "Player wins against dealer!")
        else:
            # Dealer won or push
            # Check if any player pushed
            has_push = False
            for p in self.players:
                p_res = calculate_blackjack_hand(self.player_hands.get(p.id, []))
                if not p_res["is_bust"] and p_res["score"] == d_score:
                    has_push = True
                    break

            if has_push:
                self.finish_game([], "Push! Bets returned.")
            else:
                self.finish_game([], "Dealer wins.")

    # -------------------------------------------------------------------------
    # Subgame 2: War Action Flow
    # -------------------------------------------------------------------------

    def _handle_war_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if action == "auto_battle":
            self.auto_battle = not self.auto_battle
            return True, f"Auto-battle set to {self.auto_battle}"

        if action not in ("battle", "flip", "play"):
            return False, f"Unknown War action: {action}"

        p1 = self.players[0].id if self.players else "p1"
        p2 = self.players[1].id if len(self.players) > 1 else "p2"
        h1 = self.player_hands.setdefault(p1, [])
        h2 = self.player_hands.setdefault(p2, [])

        if not h1 or not h2:
            winner = p1 if h1 else p2
            wp = self.get_player(winner)
            if wp:
                wp.score += 1
            self.finish_game([winner], f"{winner} captured all cards!")
            return True, ""

        self.war_round_count += 1
        self.last_battle_time = time.time()

        if not self.in_war:
            # Standard battle round: each flips 1 card
            c1 = h1.pop(0)
            c2 = h2.pop(0)
            self.current_cards = {p1: c1, p2: c2}
            self.war_pile.extend([c1, c2])

            cmp_res = compare_war_cards(c1, c2)
            if cmp_res == 1:
                # P1 wins round
                h1.extend(self.war_pile)
                self.war_pile.clear()
                if not h2:
                    wp = self.get_player(p1)
                    if wp:
                        wp.score += 1
                    self.finish_game([p1], f"{p1} captured all cards!")
            elif cmp_res == -1:
                # P2 wins round
                h2.extend(self.war_pile)
                self.war_pile.clear()
                if not h1:
                    wp = self.get_player(p2)
                    if wp:
                        wp.score += 1
                    self.finish_game([p2], f"{p2} captured all cards!")
            else:
                # TIE -> WAR triggered!
                self.in_war = True
                # Check boundary: insufficient cards for war (< 4 cards)
                if len(h1) < 4 or len(h2) < 4:
                    if len(h1) == 0:
                        winner = p2
                    elif len(h2) == 0:
                        winner = p1
                    elif len(h1) < len(h2):
                        winner = p2
                    elif len(h2) < len(h1):
                        winner = p1
                    else:
                        # Equal count: tie-break by final available card
                        final_cmp = compare_war_cards(h1[-1], h2[-1])
                        winner = p1 if final_cmp >= 0 else p2
                    wp = self.get_player(winner)
                    if wp:
                        wp.score += 1
                    self.finish_game([winner], "Resolved War with insufficient cards.")
            return True, ""

        else:
            # We are inside an active War (tied)
            # Each places 3 down cards + 1 face-up card
            down_p1 = min(3, max(0, len(h1) - 1))
            down_p2 = min(3, max(0, len(h2) - 1))
            for _ in range(down_p1):
                self.war_pile.append(h1.pop(0))
            for _ in range(down_p2):
                self.war_pile.append(h2.pop(0))

            if not h1 or not h2:
                winner = p1 if h1 else p2
                wp = self.get_player(winner)
                if wp:
                    wp.score += 1
                self.finish_game([winner], f"{winner} won war by card exhaustion.")
                return True, ""

            up1 = h1.pop(0)
            up2 = h2.pop(0)
            self.current_cards = {p1: up1, p2: up2}
            self.war_pile.extend([up1, up2])

            cmp_res = compare_war_cards(up1, up2)
            if cmp_res == 1:
                # P1 wins entire war pile
                h1.extend(self.war_pile)
                self.war_pile.clear()
                self.in_war = False
                if not h2:
                    wp = self.get_player(p1)
                    if wp:
                        wp.score += 1
                    self.finish_game([p1], f"{p1} captured all cards!")
            elif cmp_res == -1:
                # P2 wins entire war pile
                h2.extend(self.war_pile)
                self.war_pile.clear()
                self.in_war = False
                if not h1:
                    wp = self.get_player(p2)
                    if wp:
                        wp.score += 1
                    self.finish_game([p2], f"{p2} captured all cards!")
            else:
                # Another tie -> chained war!
                self.in_war = True
                if len(h1) < 4 or len(h2) < 4:
                    winner = p1 if len(h1) >= len(h2) else p2
                    wp = self.get_player(winner)
                    if wp:
                        wp.score += 1
                    self.finish_game([winner], "Chained war resolved on card boundary.")
            return True, ""

    # -------------------------------------------------------------------------
    # Subgame 3: Memory / Concentration Action Flow
    # -------------------------------------------------------------------------

    def _handle_memory_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if action != "flip":
            return False, f"Unknown Memory action: {action}"

        idx = data.get("index") if "index" in data else data.get("card_index")
        if idx is None or not isinstance(idx, int):
            return False, "Invalid or missing card index."

        if idx < 0 or idx >= len(self.grid):
            return False, f"Index {idx} is out of bounds (0..{len(self.grid)-1})."

        if idx in self.matched_indices:
            return False, "Card is already matched."

        if idx in self.flipped_indices:
            return False, "Card is already flipped face-up."

        # If previous mismatch was still showing, auto-flip back before flipping new card
        if len(self.flipped_indices) == 2:
            self.flipped_indices.clear()
            self.mismatch_deadline = None

        self.flipped_indices.append(idx)

        # Record seen card in bot memory
        card = self.grid[idx]
        k = card.get("match_key") or card.get("rank") or str(idx)
        seen_list = self.bot_memory.setdefault(k, [])
        if idx not in seen_list:
            seen_list.append(idx)

        if len(self.flipped_indices) == 1:
            return True, ""

        if len(self.flipped_indices) == 2:
            self.moves_count += 1
            i1, i2 = self.flipped_indices[0], self.flipped_indices[1]
            c1, c2 = self.grid[i1], self.grid[i2]
            k1 = c1.get("match_key") or c1.get("rank")
            k2 = c2.get("match_key") or c2.get("rank")

            if k1 == k2:
                # Match found!
                self.matched_indices.add(i1)
                self.matched_indices.add(i2)
                self.flipped_indices.clear()
                p = self.get_player(player_id)
                if p:
                    p.score += 1

                # Check game completion
                if len(self.matched_indices) >= len(self.grid):
                    if len(self.players) == 1:
                        winners = [self.players[0].id]
                    else:
                        s0 = self.players[0].score
                        s1 = self.players[1].score
                        if s0 > s1:
                            winners = [self.players[0].id]
                        elif s1 > s0:
                            winners = [self.players[1].id]
                        else:
                            winners = [p.id for p in self.players]
                    self.finish_game(winners, "All pairs matched!")
            else:
                # Mismatch -> set deadline for auto-flip back
                self.mismatch_deadline = time.time() + 1.2
                if len(self.players) > 1:
                    # Switch turn in 2P mode on mismatch
                    self.turn_player_id = (
                        self.players[1].id
                        if self.turn_player_id == self.players[0].id
                        else self.players[0].id
                    )

            return True, ""

        return True, ""

    # -------------------------------------------------------------------------
    # Subgame 4: High-Low Action Flow
    # -------------------------------------------------------------------------

    def _handle_high_low_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if action in ("bank", "cash_out"):
            p = self.get_player(player_id)
            if p:
                p.score = self.banked_score
            self.finish_game([player_id], f"Banked {self.banked_score} points!")
            return True, ""

        guess: str = ""
        if action in ("higher", "lower"):
            guess = action
        elif action in ("guess", "choice", "play"):
            guess = str(data.get("guess", "")).strip().lower()

        if guess not in ("higher", "lower"):
            return False, f"Invalid High-Low guess: '{guess}'. Must be 'higher' or 'lower'."

        if self.deck.is_empty():
            self.deck.reshuffle_discards()
            if self.deck.is_empty():
                self.deck.reset_deck()

        next_card = self.deck.draw_card()
        if not next_card:
            return False, "Deck exhausted."

        self.next_card = next_card
        res = evaluate_high_low_guess(self.current_card or {}, next_card, guess)

        if res == "win":
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)
            self.multiplier = _get_hl_multiplier(self.streak)
            self.banked_score += int(100 * self.multiplier)
            self.current_card = next_card
            self.card_history.append(next_card)
            p = self.get_player(player_id)
            if p:
                p.score = self.banked_score
        elif res == "push":
            # Equal rank preserves streak and multiplier
            self.current_card = next_card
            self.card_history.append(next_card)
        else:
            # Loss breaks streak
            self.streak = 0
            self.multiplier = 1.0
            self.current_card = next_card
            self.card_history.append(next_card)

        return True, ""

    # -------------------------------------------------------------------------
    # Timers & Bot Logic
    # -------------------------------------------------------------------------

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing":
            return False

        changed = False

        if self.mode == "memory":
            if self.mismatch_deadline is not None and now >= self.mismatch_deadline:
                self.flipped_indices.clear()
                self.mismatch_deadline = None
                changed = True

        elif self.mode == "war":
            if self.auto_battle and (now - self.last_battle_time >= 0.8):
                ok, _ = self.handle_action("p1", "battle", {})
                if ok:
                    changed = True

        return changed

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing":
            return None

        if self.mode == "blackjack":
            if self.player_stood.get(bot_id, False):
                return None
            hand = self.player_hands.get(bot_id, [])
            res = calculate_blackjack_hand(hand)
            if res["score"] < 17:
                return ("hit", {})
            return ("stand", {})

        elif self.mode == "war":
            return ("battle", {})

        elif self.mode == "memory":
            # Bot memory recall
            diff = self.settings.get("difficulty", "mid")
            recall_rate = 0.3 if diff == "easy" else (0.7 if diff == "mid" else 1.0)

            # Check if bot knows a pair that is not yet matched
            known_pairs: list[tuple[int, int]] = []
            for k, indices in self.bot_memory.items():
                unmatched = [i for i in indices if i not in self.matched_indices]
                if len(unmatched) >= 2:
                    known_pairs.append((unmatched[0], unmatched[1]))

            if known_pairs and self.rng.random() < recall_rate:
                p_i1, p_i2 = known_pairs[0]
                if len(self.flipped_indices) == 0:
                    return ("flip", {"index": p_i1})
                elif len(self.flipped_indices) == 1:
                    target = p_i2 if self.flipped_indices[0] == p_i1 else p_i1
                    return ("flip", {"index": target})

            # Random unrevealed card
            unrevealed = [
                i for i in range(len(self.grid))
                if i not in self.matched_indices and i not in self.flipped_indices
            ]
            if unrevealed:
                return ("flip", {"index": self.rng.choice(unrevealed)})
            return None

        elif self.mode == "high_low":
            val = self.current_card.get("value", 8) if self.current_card else 8
            guess = "higher" if val <= 7 else "lower"
            return ("guess", {"guess": guess})

        return None

    # -------------------------------------------------------------------------
    # Public & Private State Serialization
    # -------------------------------------------------------------------------

    def get_public_state(self) -> dict[str, Any]:
        now = time.time()
        elapsed = round(now - (self.started_at or now), 1)

        base_state: dict[str, Any] = {
            "phase": self.phase,
            "mode": self.mode,
            "subgame": self.mode,
            "turn_player_id": self.turn_player_id,
            "deck_count": self.deck.count(),
            "cards_remaining": self.deck.count(),
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
            "elapsed_time": elapsed,
            "timer": elapsed,
            "time_elapsed": elapsed,
            "time_seconds": elapsed,
            "elapsed_seconds": int(elapsed),
        }

        if self.mode == "blackjack":
            # Dealer hand: hide hole card unless dealer is revealed
            if self.dealer_revealed:
                dealer_view = list(self.dealer_hand)
                d_calc = calculate_blackjack_hand(self.dealer_hand)
                dealer_score = d_calc["score"]
            else:
                upcard = self.dealer_hand[0] if self.dealer_hand else {}
                dealer_view = [upcard, {"hidden": True, "rank": "?", "suit": "back"}]
                dealer_score = calculate_blackjack_hand([upcard])["score"] if upcard else 0

            p1_id = self.players[0].id if self.players else "p1"
            p1_hand = self.player_hands.get(p1_id, [])

            base_state.update({
                "dealer_hand": dealer_view,
                "dealer_revealed": self.dealer_revealed,
                "dealer_score": dealer_score,
                "player_hand": p1_hand,
                "hands": {pid: list(self.player_hands.get(pid, [])) for pid in self.player_ids()},
                "split_hands": self.split_hands,
                "active_hand_indices": self.active_hand_indices,
                "bets": self.player_bets,
                "chips": self.player_chips,
            })

        elif self.mode == "war":
            p_counts = {pid: len(self.player_hands.get(pid, [])) for pid in self.player_ids()}
            base_state.update({
                "in_war": self.in_war,
                "war_active": self.in_war,
                "war_pile_count": len(self.war_pile),
                "war_pile": list(self.war_pile),
                "current_cards": self.current_cards,
                "card_counts": p_counts,
                "player_cards_count": p_counts,
                "auto_battle": self.auto_battle,
                "round_count": self.war_round_count,
            })

        elif self.mode == "memory":
            pub_grid = []
            for idx, c in enumerate(self.grid):
                is_matched = idx in self.matched_indices
                is_flipped = idx in self.flipped_indices
                if is_matched or is_flipped:
                    pub_grid.append({**c, "face_up": True, "matched": is_matched})
                else:
                    pub_grid.append({
                        "grid_index": idx,
                        "uid": c.get("uid", idx),
                        "face_up": False,
                        "matched": False,
                    })

            base_state.update({
                "grid": pub_grid,
                "cards": pub_grid,
                "matched_indices": list(self.matched_indices),
                "flipped_indices": list(self.flipped_indices),
                "moves": self.moves_count,
                "moves_count": self.moves_count,
                "flips": self.moves_count,
                "pairs_count": self.pairs_count,
                "matched_pairs": len(self.matched_indices) // 2,
            })

        elif self.mode == "high_low":
            base_state.update({
                "current_card": self.current_card,
                "next_card": self.next_card,
                "streak": self.streak,
                "max_streak": self.max_streak,
                "multiplier": self.multiplier,
                "banked_score": self.banked_score,
                "score": self.banked_score,
                "card_history": self.card_history[-10:],
            })

        return base_state

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        if self.mode == "blackjack":
            hand = self.player_hands.get(player_id, [])
            return {
                "hand": hand,
                "chips": self.player_chips.get(player_id, 1000),
                "bet": self.player_bets.get(player_id, 25),
                "splits": self.split_hands.get(player_id, []),
                "active_hand_index": self.active_hand_indices.get(player_id, 0),
            }
        elif self.mode == "war":
            return {
                "hand": self.player_hands.get(player_id, []),
                "count": len(self.player_hands.get(player_id, [])),
            }
        return {}

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        if self.phase not in ("pre_game", "playing"):
            return False
        remaining = [p for p in self.players if p.id != player_id]
        winner_id = remaining[0].id if remaining else player_id
        winner = self.get_player(winner_id)
        if winner:
            winner.score = 1
        msg = reason or f"{player_id} forfeited."
        self.finish_game([winner_id], msg)
        return True
