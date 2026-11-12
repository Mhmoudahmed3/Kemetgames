"""2-6P UNO card engine with official 108-card deck, Wild/Draw/+4 actions, UNO calls & catches, and Easy/Mid/Hard AI."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

UNO_COLORS: tuple[str, ...] = ("red", "blue", "green", "yellow")
COLOR_LABELS: dict[str, str] = {
    "red": "RED",
    "blue": "BLUE",
    "green": "GREEN",
    "yellow": "YELLOW",
}


def build_uno_deck() -> list[dict[str, Any]]:
    """Construct an authentic 108-card UNO deck."""
    deck: list[dict[str, Any]] = []
    cid = 1
    for color in UNO_COLORS:
        deck.append(
            {
                "id": cid,
                "color": color,
                "kind": "0",
                "label": "0",
                "points": 0,
            }
        )
        cid += 1
        for num in range(1, 10):
            for _ in range(2):
                deck.append(
                    {
                        "id": cid,
                        "color": color,
                        "kind": str(num),
                        "label": str(num),
                        "points": num,
                    }
                )
                cid += 1
        for kind, label in (("skip", "SKIP"), ("reverse", "REV"), ("draw2", "+2")):
            for _ in range(2):
                deck.append(
                    {
                        "id": cid,
                        "color": color,
                        "kind": kind,
                        "label": label,
                        "points": 20,
                    }
                )
                cid += 1

    for kind, label in (("wild", "WILD"), ("wild4", "+4")):
        for _ in range(4):
            deck.append(
                {
                    "id": cid,
                    "color": "wild",
                    "kind": kind,
                    "label": label,
                    "points": 50,
                }
            )
            cid += 1

    random.shuffle(deck)
    return deck


def can_play_card(
    card: dict[str, Any], top_card: dict[str, Any], active_color: str
) -> bool:
    """Return True if card can legally be played onto top_card with active_color."""
    if card["color"] == "wild":
        return True
    if card["color"] == active_color:
        return True
    return card["kind"] == top_card["kind"]


class UnoGame(BaseGame):
    GAME_TYPE = "uno"
    TITLE = "UNO PROTOCOL"
    CATEGORY = "Card & Party"
    DESCRIPTION = (
        "2-6 player UNO with official 108-card deck, Reverse/Skip/+2/+4 Wilds, live UNO! callouts, and adaptive AI bots."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 6
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    DEFAULT_SETTINGS = {"difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.deck: list[dict[str, Any]] = []
        self.discard_pile: list[dict[str, Any]] = []
        self.hands: dict[str, list[dict[str, Any]]] = {}
        self.active_color: str = "red"
        self.direction: int = 1  # 1 = clockwise, -1 = counter-clockwise
        self.turn_idx: int = 0
        self.drawn_playable_id: int | None = None
        self.uno_declared: dict[str, bool] = {}
        self.last_action_note: str = ""
        self.stalled_passes: int = 0

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = diff

        self.deck = build_uno_deck()
        self.hands = {}
        self.uno_declared = {}
        for p in self.players:
            p.score = 0
            self.hands[p.id] = [self.deck.pop() for _ in range(7)]
            self.uno_declared[p.id] = False

        # Start with a clean colored number card whenever available
        opener_idx = next(
            (
                i
                for i in range(len(self.deck) - 1, -1, -1)
                if self.deck[i]["color"] in UNO_COLORS and self.deck[i]["kind"].isdigit()
            ),
            len(self.deck) - 1,
        )
        opener = self.deck.pop(opener_idx)
        self.discard_pile = [opener]
        self.active_color = opener["color"] if opener["color"] in UNO_COLORS else random.choice(UNO_COLORS)
        self.direction = 1
        self.turn_idx = 0
        self.turn_player_id = self.players[0].id
        self.drawn_playable_id = None
        self.stalled_passes = 0
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        self.last_action_note = (
            f"Opening card: {COLOR_LABELS[self.active_color]} {opener['label']}."
        )
        self.log_event(
            f"UNO launched ({diff.upper()}, {len(self.players)} players). {self.players[0].name} leads."
        )

    def _draw_one(self) -> dict[str, Any] | None:
        if not self.deck:
            if len(self.discard_pile) <= 1:
                return None
            top = self.discard_pile.pop()
            self.deck = list(self.discard_pile)
            random.shuffle(self.deck)
            self.discard_pile = [top]
            self.log_event("Discard pile reshuffled back into draw deck.")
        return self.deck.pop() if self.deck else None

    def _draw_cards(self, target_id: str, count: int) -> int:
        drawn = 0
        for _ in range(count):
            card = self._draw_one()
            if card is None:
                break
            self.hands[target_id].append(card)
            drawn += 1
        if drawn > 0:
            self.uno_declared[target_id] = False
        return drawn

    def _seat_at(self, steps: int) -> PlayerSlot:
        idx = (self.turn_idx + steps * self.direction) % len(self.players)
        return self.players[idx]

    def _advance_turn(self, steps: int = 1) -> None:
        self.drawn_playable_id = None
        self.turn_idx = (self.turn_idx + steps * self.direction) % len(self.players)
        self.turn_player_id = self.players[self.turn_idx].id

    def _resolve_lowest_points_finish(self, reason_prefix: str) -> None:
        totals = {
            p.id: sum(c["points"] for c in self.hands[p.id]) for p in self.players
        }
        min_pts = min(totals.values())
        winners = [p.id for p in self.players if totals[p.id] == min_pts]
        for wid in winners:
            wp = self.get_player(wid)
            if wp:
                wp.score = sum(totals[pid] for pid in totals if pid != wid)
        names = ", ".join(self.get_player(w).name for w in winners if self.get_player(w))
        self.finish_game(winners, f"{reason_prefix} Lowest hand wins: {names} ({min_pts} pts left).")

    def _playable_indices(self, player_id: str) -> list[int]:
        hand = self.hands.get(player_id, [])
        if not self.discard_pile:
            return list(range(len(hand)))
        top = self.discard_pile[-1]
        if self.drawn_playable_id is not None:
            return [
                i
                for i, c in enumerate(hand)
                if c["id"] == self.drawn_playable_id and can_play_card(c, top, self.active_color)
            ]
        return [i for i, c in enumerate(hand) if can_play_card(c, top, self.active_color)]

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        player = self.get_player(player_id)
        if player is None:
            return False, "Unknown player."

        if action == "shout_uno":
            hand = self.hands[player_id]
            if len(hand) not in (1, 2):
                return False, "Call UNO only when you have 1 or 2 cards."
            if self.uno_declared.get(player_id):
                return True, ""
            self.uno_declared[player_id] = True
            self.last_action_note = f"{player.name} shouted UNO!"
            self.log_event(self.last_action_note, kind="info")
            return True, ""

        if action == "catch_uno":
            target_id = str(data.get("target_id", ""))
            if not target_id or target_id == player_id or target_id not in self.hands:
                return False, "Invalid catch target."
            if len(self.hands[target_id]) != 1 or self.uno_declared.get(target_id, False):
                return False, "That player is not vulnerable to UNO catch."
            if not self.deck and len(self.discard_pile) <= 1:
                return False, "No penalty cards remaining in deck."
            drawn = self._draw_cards(target_id, 2)
            target_p = self.get_player(target_id)
            tname = target_p.name if target_p else target_id
            self.last_action_note = f"{player.name} caught {tname} without UNO! +{drawn} penalty cards."
            self.log_event(self.last_action_note, kind="warn")
            return True, ""

        if player_id != self.turn_player_id:
            return False, "Not your turn."

        hand = self.hands[player_id]

        if action == "draw":
            if self.drawn_playable_id is not None:
                return False, "Play your drawn card or pass your turn."
            card = self._draw_one()
            if card is None:
                self.stalled_passes += 1
                self.last_action_note = f"{player.name} passed (deck empty)."
                self.log_event(self.last_action_note)
                if self.stalled_passes >= len(self.players):
                    self._resolve_lowest_points_finish("Deck exhausted.")
                    return True, ""
                self._advance_turn(1)
                return True, ""

            self.stalled_passes = 0
            hand.append(card)
            self.uno_declared[player_id] = False
            top = self.discard_pile[-1]
            if can_play_card(card, top, self.active_color):
                self.drawn_playable_id = card["id"]
                self.last_action_note = f"{player.name} drew a playable card."
                return True, ""

            self.last_action_note = f"{player.name} drew a card."
            self.log_event(f"{player.name} drew 1 card.")
            self._advance_turn(1)
            return True, ""

        if action == "pass_turn":
            if self.drawn_playable_id is None:
                return False, "Draw a card before passing."
            self.last_action_note = f"{player.name} kept drawn card."
            self.log_event(f"{player.name} kept the drawn card and ended turn.")
            self._advance_turn(1)
            return True, ""

        if action == "play":
            try:
                idx = int(data.get("index", -1))
            except (TypeError, ValueError):
                return False, "Invalid card index."
            if not (0 <= idx < len(hand)):
                return False, "Card slot out of bounds."

            card = hand[idx]
            if self.drawn_playable_id is not None and card["id"] != self.drawn_playable_id:
                return False, "You can only play the card you just drew, or pass."

            top = self.discard_pile[-1]
            if not can_play_card(card, top, self.active_color):
                return False, "Card does not match active color or symbol."

            next_color = card["color"]
            if card["color"] == "wild":
                chosen = str(data.get("color", "")).strip().lower()
                if chosen not in UNO_COLORS:
                    return False, "Choose a Wild color (red, blue, green, or yellow)."
                next_color = chosen

            hand.pop(idx)
            self.discard_pile.append(card)
            self.active_color = next_color
            self.drawn_playable_id = None
            self.stalled_passes = 0

            if len(hand) != 1:
                self.uno_declared[player_id] = False

            card_desc = (
                f"{COLOR_LABELS[next_color]} {card['label']}"
                if card["color"] != "wild"
                else f"{card['label']} → {COLOR_LABELS[next_color]}"
            )

            if len(hand) == 0:
                score_gain = sum(
                    c["points"]
                    for pid, h in self.hands.items()
                    if pid != player_id
                    for c in h
                )
                player.score = max(100, score_gain)
                self.last_action_note = f"{player.name} played {card_desc} and won UNO!"
                self.finish_game(
                    [player_id],
                    f"UNO Victory! {player.name} emptied their hand for {player.score} pts.",
                )
                return True, ""

            steps = 1
            extra_note = ""
            if card["kind"] == "skip":
                victim = self._seat_at(1)
                extra_note = f" · {victim.name} skipped!"
                steps = 2
            elif card["kind"] == "reverse":
                if len(self.players) == 2:
                    extra_note = f" · {player.name} plays again!"
                    steps = 2
                else:
                    self.direction *= -1
                    extra_note = " · Direction reversed!"
                    steps = 1
            elif card["kind"] == "draw2":
                victim = self._seat_at(1)
                drawn = self._draw_cards(victim.id, 2)
                extra_note = f" · {victim.name} draws +{drawn} & skips!"
                steps = 2
            elif card["kind"] == "wild4":
                victim = self._seat_at(1)
                drawn = self._draw_cards(victim.id, 4)
                extra_note = f" · {victim.name} draws +{drawn} & skips!"
                steps = 2

            self.last_action_note = f"{player.name} played {card_desc}{extra_note}"
            self.log_event(self.last_action_note)
            self._advance_turn(steps)
            return True, ""

        return False, f"Unsupported action: {action}"

    def _choose_wild_color(self, bot_id: str, diff: str) -> str:
        hand = self.hands[bot_id]
        counts = {c: 0 for c in UNO_COLORS}
        for card in hand:
            if card["color"] in counts:
                counts[card["color"]] += 1
        if diff == "easy":
            return random.choice(UNO_COLORS)
        best_count = max(counts.values())
        top_colors = [c for c, cnt in counts.items() if cnt == best_count]
        return random.choice(top_colors)

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.turn_player_id != bot_id:
            return None

        diff = self.get_difficulty()

        # Hard bots spot and catch unprotected 1-card rivals first (only if deck/discard can supply penalty cards)
        if diff == "hard" and (self.deck or len(self.discard_pile) > 1):
            for p in self.players:
                if (
                    p.id != bot_id
                    and len(self.hands.get(p.id, [])) == 1
                    and not self.uno_declared.get(p.id, False)
                ):
                    return "catch_uno", {"target_id": p.id}

        hand = self.hands[bot_id]
        playable = self._playable_indices(bot_id)
        if not playable:
            if self.drawn_playable_id is not None:
                return "pass_turn", {}
            return "draw", {}

        # Shout UNO before playing down to 1 card based on difficulty reliability
        if (
            len(hand) == 2
            and not self.uno_declared.get(bot_id, False)
            and self.drawn_playable_id is None
        ):
            call_prob = 0.45 if diff == "easy" else (0.85 if diff == "mid" else 1.0)
            if random.random() < call_prob:
                return "shout_uno", {}

        if diff == "easy":
            idx = random.choice(playable)
            card = hand[idx]
            payload: dict[str, Any] = {"index": idx}
            if card["color"] == "wild":
                payload["color"] = self._choose_wild_color(bot_id, diff)
            return "play", payload

        next_opp = self._seat_at(1)
        next_low = len(self.hands.get(next_opp.id, [])) <= 2

        def score_play(idx: int) -> float:
            c = hand[idx]
            sc = float(c["points"])
            if diff == "hard":
                if c["color"] == "wild":
                    # Save wilds unless urgent or forced
                    sc -= 18.0
                    if c["kind"] == "wild4" and next_low:
                        sc += 45.0
                elif c["kind"] in ("draw2", "skip", "reverse") and next_low:
                    sc += 40.0
                # Prefer playing color with more backup cards so we keep flow
                same_color_cnt = sum(1 for h in hand if h["color"] == c["color"])
                sc += same_color_cnt * 2.5
            else:
                if c["color"] == "wild":
                    sc -= 8.0
            return sc

        best_idx = max(playable, key=score_play)
        chosen = hand[best_idx]
        data: dict[str, Any] = {"index": best_idx}
        if chosen["color"] == "wild":
            data["color"] = self._choose_wild_color(bot_id, diff)
        return "play", data

    def get_public_state(self) -> dict[str, Any]:
        counts = {p.id: len(self.hands.get(p.id, [])) for p in self.players}
        uno_vulnerable = [
            p.id
            for p in self.players
            if counts.get(p.id, 0) == 1 and not self.uno_declared.get(p.id, False)
        ]
        return {
            "phase": self.phase,
            "difficulty": self.get_difficulty(),
            "turn_player_id": self.turn_player_id,
            "direction": self.direction,
            "active_color": self.active_color,
            "deck_count": len(self.deck),
            "discard_count": len(self.discard_pile),
            "discard_top": self.discard_pile[-1] if self.discard_pile else None,
            "card_counts": counts,
            "uno_declared": {pid: bool(v) for pid, v in self.uno_declared.items()},
            "uno_vulnerable_ids": uno_vulnerable,
            "drawn_playable_active": self.drawn_playable_id is not None,
            "last_action_note": self.last_action_note,
            "revealed_hands": self.hands if self.phase == "finished" else {},
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        if player_id not in self.hands:
            return {}
        playable = self._playable_indices(player_id) if player_id == self.turn_player_id else []
        return {
            "hand": list(self.hands[player_id]),
            "playable_indices": playable,
            "drawn_playable_id": (
                self.drawn_playable_id if player_id == self.turn_player_id else None
            ),
            "can_shout_uno": len(self.hands[player_id]) in (1, 2)
            and not self.uno_declared.get(player_id, False),
        }

