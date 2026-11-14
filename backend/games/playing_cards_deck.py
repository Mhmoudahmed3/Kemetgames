"""Reusable, server-authoritative 52-card playing deck module and game scoring utilities."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Sequence

# Canonical suit names in consistent standard order
SUITS: tuple[str, ...] = ("hearts", "diamonds", "clubs", "spades")

# Standard 13 card ranks from low to high
RANKS: tuple[str, ...] = (
    "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "J", "Q", "K", "A"
)

# Visual suit symbols and colors for frontend SVG/CSS rendering
SUIT_SYMBOLS: dict[str, str] = {
    "hearts": "♥",
    "diamonds": "♦",
    "clubs": "♣",
    "spades": "♠",
}

SUIT_COLORS: dict[str, str] = {
    "hearts": "red",
    "diamonds": "red",
    "clubs": "black",
    "spades": "black",
}

# Standard card values (Ace high = 14)
RANK_VALUES: dict[str, int] = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14,
}

# Blackjack values (Ace default = 11, face cards = 10)
BLACKJACK_VALUES: dict[str, int] = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}


@dataclass(frozen=True)
class Card:
    """Immutable representation of a standard playing card."""

    id: str           # Unique identifier, e.g. "hearts_A_0"
    suit: str         # "hearts" | "diamonds" | "clubs" | "spades"
    rank: str         # "2".."10", "J", "Q", "K", "A"
    value: int        # Base rank value (2..14)
    color: str        # "red" | "black"
    symbol: str       # "♥" | "♦" | "♣" | "♠"
    label: str        # Formatted string, e.g. "A♥" or "10♠"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return {
            "id": self.id,
            "suit": self.suit,
            "rank": self.rank,
            "value": self.value,
            "color": self.color,
            "symbol": self.symbol,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Card:
        """Construct a Card instance from a dictionary."""
        rank = str(data["rank"])
        suit = str(data.get("suit", "spades"))
        return cls(
            id=str(data.get("id", f"{suit}_{rank}_0")),
            suit=suit,
            rank=rank,
            value=int(data.get("value", RANK_VALUES.get(rank, 0))),
            color=str(data.get("color", SUIT_COLORS.get(suit, "black"))),
            symbol=str(data.get("symbol", SUIT_SYMBOLS.get(suit, ""))),
            label=str(data.get("label", f"{rank}{SUIT_SYMBOLS.get(suit, '')}")),
        )

    def blackjack_value(self) -> int:
        """Return the standard Blackjack point value (Ace=11, face=10)."""
        return BLACKJACK_VALUES.get(self.rank, self.value)


def fisher_yates_shuffle(deck: list[Any], rng: random.Random | None = None) -> list[Any]:
    """In-place Fisher-Yates (Knuth) unbiased shuffle algorithm.

    Guarantees that all n! permutations are equally likely with probability 1 / n!.
    Iterates backward from index n - 1 down to 1. At step i, selects a uniform random
    integer j such that 0 <= j <= i, and swaps deck[i] with deck[j].

    Time Complexity: O(n)
    Space Complexity: O(1) in-place
    """
    rand = rng if rng is not None else random
    n = len(deck)
    for i in range(n - 1, 0, -1):
        j = rand.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]
    return deck


def build_standard_deck(deck_index: int = 0) -> list[Card]:
    """Construct an authentic standard 52-card deck ordered deterministically."""
    cards: list[Card] = []
    for suit in SUITS:
        symbol = SUIT_SYMBOLS[suit]
        color = SUIT_COLORS[suit]
        for rank in RANKS:
            value = RANK_VALUES[rank]
            cid = f"{suit}_{rank}_{deck_index}"
            label = f"{rank}{symbol}"
            cards.append(
                Card(
                    id=cid,
                    suit=suit,
                    rank=rank,
                    value=value,
                    color=color,
                    symbol=symbol,
                    label=label,
                )
            )
    return cards


def create_deck(deck_index: int = 0) -> list[dict[str, Any]]:
    """Contract compatibility function: return standard 52-card deck as list of dicts."""
    return [c.to_dict() for c in build_standard_deck(deck_index)]


class PlayingCardsDeck:
    """Reusable, server-authoritative 52-card standard deck (and multi-deck shoe)."""

    def __init__(
        self,
        decks_count: int = 1,
        shuffle_on_init: bool = True,
        rng: random.Random | None = None,
    ) -> None:
        self.decks_count: int = max(1, decks_count)
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.cards: list[Card] = []
        self.discards: list[Card] = []
        self.reset(shuffle=shuffle_on_init)

    def reset(self, shuffle: bool = True) -> None:
        """Reset the deck to full capacity (52 * decks_count) and clear discards."""
        self.cards.clear()
        self.discards.clear()
        for d_idx in range(self.decks_count):
            self.cards.extend(build_standard_deck(d_idx))
        if shuffle:
            self.shuffle()

    def reset_deck(self) -> None:
        """Contract compatibility alias for reset(shuffle=True)."""
        self.reset(shuffle=True)

    def shuffle(self) -> None:
        """In-place Fisher-Yates shuffle on all remaining cards in draw pile."""
        fisher_yates_shuffle(self.cards, self.rng)

    def draw(self, count: int = 1) -> list[Card]:
        """Draw up to `count` cards from the top of the deck (popping from list tail)."""
        drawn: list[Card] = []
        for _ in range(count):
            if not self.cards:
                break
            drawn.append(self.cards.pop())
        return drawn

    def draw_card(self) -> dict[str, Any] | None:
        """Contract compatibility method: draw 1 card and return its dict (or None)."""
        if not self.cards:
            return None
        return self.cards.pop().to_dict()

    def draw_one(self) -> Card | None:
        """Draw a single Card object, or None if deck is empty."""
        return self.cards.pop() if self.cards else None

    def discard(self, cards: Sequence[Card | dict[str, Any]]) -> None:
        """Add one or more cards to the discard pile."""
        for c in cards:
            if isinstance(c, Card):
                self.discards.append(c)
            elif isinstance(c, dict):
                self.discards.append(Card.from_dict(c))

    def reshuffle_discards(self) -> int:
        """Recycle discard pile back into draw deck and shuffle. Returns recycled count."""
        recycled_count = len(self.discards)
        if recycled_count > 0:
            self.cards.extend(self.discards)
            self.discards.clear()
            self.shuffle()
        return recycled_count

    def count(self) -> int:
        """Return the count of cards remaining in the draw pile."""
        return len(self.cards)

    def deck_count(self) -> int:
        """Contract compatibility alias for count()."""
        return len(self.cards)

    def remaining(self) -> int:
        """Alias for count()."""
        return len(self.cards)

    def is_empty(self) -> bool:
        """Return True if draw deck is empty."""
        return len(self.cards) == 0

    def total_cards(self) -> int:
        """Return maximum capacity of the deck shoe (52 * decks_count)."""
        return 52 * self.decks_count

    def peek(self, count: int = 1) -> list[Card]:
        """View next `count` cards from top of deck without removing them."""
        if count <= 0:
            return []
        return list(reversed(self.cards[-count:]))

    def to_dict(self, include_cards: bool = False) -> dict[str, Any]:
        """Return a public JSON-serializable dictionary representation."""
        payload: dict[str, Any] = {
            "remaining": len(self.cards),
            "discards_count": len(self.discards),
            "total_capacity": self.total_cards(),
            "decks_count": self.decks_count,
            "is_empty": self.is_empty(),
        }
        if include_cards:
            payload["cards"] = [c.to_dict() for c in reversed(self.cards)]
        return payload


# ---------------------------------------------------------------------------
# Downstream Card Game Scoring & Comparison Helpers
# ---------------------------------------------------------------------------

class BlackjackHandResult(dict):
    """Dictionary containing blackjack metrics that also unpacks as (score, is_soft)."""

    def __iter__(self):
        return iter((self["score"], self["is_soft"]))


def calculate_blackjack_hand(hand: Sequence[Card | dict[str, Any]]) -> BlackjackHandResult:
    """Calculate standard Blackjack score, handling soft/hard Ace values."""
    card_objs = [c if isinstance(c, Card) else Card.from_dict(c) for c in hand]
    total = 0
    aces = 0
    for card in card_objs:
        if card.rank == "A":
            aces += 1
            total += 11
        else:
            total += card.blackjack_value()

    # Demote Aces from 11 down to 1 as needed to prevent bust
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    is_soft = (aces > 0)
    is_bust = (total > 21)
    is_blackjack = (len(card_objs) == 2 and total == 21)
    return BlackjackHandResult({
        "score": total,
        "is_soft": is_soft,
        "is_bust": is_bust,
        "is_blackjack": is_blackjack,
    })


def compare_war_cards(card_a: Card | dict[str, Any], card_b: Card | dict[str, Any]) -> int:
    """Compare two cards for War rules (Ace high = 14).

    Returns:
        1 if card_a wins, -1 if card_b wins, 0 if tie (War trigger).
    """
    ca = card_a if isinstance(card_a, Card) else Card.from_dict(card_a)
    cb = card_b if isinstance(card_b, Card) else Card.from_dict(card_b)
    if ca.value > cb.value:
        return 1
    elif ca.value < cb.value:
        return -1
    return 0


def compare_high_low(
    current_card: Card | dict[str, Any],
    next_card: Card | dict[str, Any],
) -> str:
    """Determine relationship of next_card relative to current_card ('higher' | 'lower' | 'equal')."""
    ca = current_card if isinstance(current_card, Card) else Card.from_dict(current_card)
    cb = next_card if isinstance(next_card, Card) else Card.from_dict(next_card)
    if cb.value > ca.value:
        return "higher"
    elif cb.value < ca.value:
        return "lower"
    return "equal"


class HighLowResult(str):
    """String result ('win' | 'loss' | 'push') that also supports unpacking as (is_ok, relation)."""

    def __new__(cls, outcome: str, is_ok: bool, relation: str) -> HighLowResult:
        obj = str.__new__(cls, outcome)
        obj.is_ok = is_ok
        obj.relation = relation
        return obj

    def __iter__(self):
        return iter((self.is_ok, self.relation))


def evaluate_high_low_guess(
    current_card: Card | dict[str, Any],
    next_card: Card | dict[str, Any],
    guess: str,
) -> HighLowResult:
    """Evaluate a player's higher/lower guess.

    Equal cards (push) preserve streak and count as successful pass.
    Returns HighLowResult which acts as outcome string ("win", "loss", "push")
    and can also be unpacked as (is_correct: bool, actual_relation: str).
    """
    actual = compare_high_low(current_card, next_card)
    if actual == "equal":
        return HighLowResult("push", True, "push")
    is_correct = (guess.strip().lower() == actual)
    outcome = "win" if is_correct else "loss"
    return HighLowResult(outcome, is_correct, actual)


def create_memory_grid(
    pairs_count: int = 8, rng: random.Random | None = None
) -> list[dict[str, Any]]:
    """Generate a shuffled matched-pair grid for Memory/Concentration game.

    Selects `pairs_count` ranks from standard deck, creates 2 matching cards for each,
    shuffles the grid with Fisher-Yates, and attaches a 0-indexed `grid_index`.
    """
    rand = rng if rng is not None else random
    chosen_ranks = rand.sample(RANKS, min(pairs_count, len(RANKS)))
    grid_cards: list[dict[str, Any]] = []
    card_uid = 1
    for rank in chosen_ranks:
        # Create pair: red suit (hearts) and black suit (spades) for contrast
        for suit in ("hearts", "spades"):
            grid_cards.append(
                {
                    "uid": card_uid,
                    "suit": suit,
                    "rank": rank,
                    "color": SUIT_COLORS[suit],
                    "symbol": SUIT_SYMBOLS[suit],
                    "label": f"{rank}{SUIT_SYMBOLS[suit]}",
                    "match_key": rank,
                }
            )
            card_uid += 1

    fisher_yates_shuffle(grid_cards, rng=rand)
    for idx, card_dict in enumerate(grid_cards):
        card_dict["grid_index"] = idx
    return grid_cards
