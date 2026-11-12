"""2-6P Skru / Screw hidden-hand card engine with private peeks, Basra matching, SKRU call, and AI bot."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

PRE_GAME_PEEK_SECONDS = 10.0
SKRU_PEEK_SECONDS = {"easy": 12.0, "mid": 10.0, "hard": 7.0}


def build_skru_deck() -> list[dict[str, Any]]:
    deck: list[dict[str, Any]] = []
    cid = 1
    for num in range(1, 7):
        for _ in range(4):
            deck.append({"id": cid, "code": str(num), "label": str(num), "points": num, "power": None})
            cid += 1
    for num in (7, 8):
        for _ in range(4):
            deck.append({"id": cid, "code": str(num), "label": str(num), "points": num, "power": "peek_self"})
            cid += 1
    for num in (9, 10):
        for _ in range(4):
            deck.append({"id": cid, "code": str(num), "label": str(num), "points": num, "power": "peek_opp"})
            cid += 1
    for _ in range(4):
        deck.append({"id": cid, "code": "J", "label": "JACK", "points": 11, "power": "blind_swap"})
        cid += 1
    for _ in range(4):
        deck.append({"id": cid, "code": "K", "label": "KING", "points": 13, "power": "look_swap"})
        cid += 1
    for _ in range(2):
        deck.append({"id": cid, "code": "RED_SKRU", "label": "RED SKRU", "points": 0, "power": None})
        cid += 1
    for _ in range(2):
        deck.append({"id": cid, "code": "GREEN_SKRU", "label": "GREEN SKRU", "points": 25, "power": None})
        cid += 1
    for _ in range(2):
        deck.append({"id": cid, "code": "PLUS_20", "label": "+20", "points": 20, "power": None})
        cid += 1
    random.shuffle(deck)
    return deck


class SkruGame(BaseGame):
    GAME_TYPE = "skru"
    TITLE = "SKRU / SCREW"
    CATEGORY = "Card & Party"
    DESCRIPTION = (
        "2-6 player memory & bluffing card game. Peek bottom 2 cards, swap, deploy powers (7/8, 9/10, J, K), Basra toss, and call SKRU! Lowest score wins."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 6
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.peek_seconds: float = PRE_GAME_PEEK_SECONDS
        self.deck: list[dict[str, Any]] = []
        self.discard_pile: list[dict[str, Any]] = []
        self.hands: dict[str, list[dict[str, Any] | None]] = {}
        self.pre_game_started_at: float = 0.0
        self.ready_players: set[str] = set()
        self.turn_idx: int = 0
        self.turn_stage: str = "choose_source"
        self.drawn_card: dict[str, Any] | None = None
        self.skru_caller_id: str | None = None
        self.final_turns_left: int = 0
        self.private_peeks: dict[str, dict[str, Any]] = {}
        self.king_context: dict[str, Any] | None = None
        self.bot_memory: dict[str, dict[str, int]] = {}
        self._last_peek_sec: int = -1

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = diff
        self.peek_seconds = SKRU_PEEK_SECONDS[diff]
        self._last_peek_sec = -1
        self.deck = build_skru_deck()
        self.hands = {}
        self.private_peeks = {}
        self.bot_memory = {}
        for p in self.players:
            p.score = 0
            cards: list[dict[str, Any] | None] = [self.deck.pop() for _ in range(4)]
            self.hands[p.id] = cards
            # Pre-game peek: bottom 2 cards (slots 2 and 3)
            self.private_peeks[p.id] = {
                "initial_bottom": {
                    "2": cards[2],
                    "3": cards[3],
                },
                "last_peek": None,
            }
            if p.is_bot:
                if diff == "easy":
                    self.bot_memory[p.id] = {f"{p.id}:2": cards[2]["points"]}
                else:
                    self.bot_memory[p.id] = {
                        f"{p.id}:2": cards[2]["points"],
                        f"{p.id}:3": cards[3]["points"],
                    }

        self.discard_pile = [self.deck.pop()]
        self.phase = "pre_game"
        self.pre_game_started_at = time.time()
        self.started_at = self.pre_game_started_at
        self.ready_players = {p.id for p in self.players if p.is_bot}
        self.turn_idx = 0
        self.turn_player_id = None
        self.turn_stage = "choose_source"
        self.drawn_card = None
        self.skru_caller_id = None
        self.final_turns_left = 0
        self.king_context = None
        self.winner_ids = []
        self.win_reason = ""
        self.log_event(
            f"Skru dealt! Memorize your bottom 2 cards within {int(self.peek_seconds)} seconds."
        )

    def _begin_play(self) -> None:
        if self.phase != "pre_game":
            return
        self.phase = "playing"
        self.turn_idx = 0
        self.turn_player_id = self.players[0].id
        self.turn_stage = "choose_source"
        # Clear initial bottom peek once round starts
        for pid in self.private_peeks:
            self.private_peeks[pid]["initial_bottom"] = {}
        self.log_event(f"Play begins! {self.players[0].name}'s turn.")

    def _draw_from_deck(self) -> dict[str, Any] | None:
        if not self.deck:
            if len(self.discard_pile) <= 1:
                return None
            top = self.discard_pile.pop()
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [top]
            self.log_event("Draw deck reshuffled from discard pile.")
        return self.deck.pop() if self.deck else None

    @staticmethod
    def _safe_int(val: Any) -> int | None:
        if val is None or isinstance(val, bool):
            return None
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    def _invalidate_slot_knowledge(
        self, owner_id: str, slot: int, preserve_bot_id: str | None = None
    ) -> None:
        key = f"{owner_id}:{slot}"
        for bid, mem in self.bot_memory.items():
            if bid != preserve_bot_id:
                mem.pop(key, None)
        for pdata in self.private_peeks.values():
            lp = pdata.get("last_peek")
            if lp and lp.get("owner_id") == owner_id and lp.get("slot") == slot:
                pdata["last_peek"] = None

    def _swap_slot_knowledge(
        self, id_a: str, slot_a: int, id_b: str, slot_b: int
    ) -> None:
        key_a = f"{id_a}:{slot_a}"
        key_b = f"{id_b}:{slot_b}"
        for mem in self.bot_memory.values():
            val_a = mem.pop(key_a, None)
            val_b = mem.pop(key_b, None)
            if val_b is not None:
                mem[key_a] = val_b
            if val_a is not None:
                mem[key_b] = val_a
        for pdata in self.private_peeks.values():
            lp = pdata.get("last_peek")
            if lp and (
                (lp.get("owner_id") == id_a and lp.get("slot") == slot_a)
                or (lp.get("owner_id") == id_b and lp.get("slot") == slot_b)
            ):
                pdata["last_peek"] = None

    def on_bot_takeover(self, player_id: str) -> None:
        if player_id not in self.hands:
            return
        diff = self.get_difficulty()
        if player_id not in self.bot_memory:
            cards = self.hands[player_id]
            mem: dict[str, int] = {}
            if self.phase == "pre_game":
                if len(cards) > 2 and cards[2] is not None:
                    mem[f"{player_id}:2"] = cards[2]["points"]
                if diff != "easy" and len(cards) > 3 and cards[3] is not None:
                    mem[f"{player_id}:3"] = cards[3]["points"]
            self.bot_memory[player_id] = mem
        if self.phase == "pre_game":
            self.ready_players.add(player_id)
            if len(self.ready_players) >= len(self.players):
                self._begin_play()

    def _tick_timers(self, now: float) -> bool:
        if self.phase == "pre_game":
            if now - self.pre_game_started_at >= self.peek_seconds:
                self._begin_play()
                return True
            sec = int(max(0.0, self.peek_seconds - (now - self.pre_game_started_at)))
            if self._last_peek_sec != sec:
                self._last_peek_sec = sec
                return True
        return False

    def _end_turn(self) -> None:
        self.drawn_card = None
        self.king_context = None
        if self.skru_caller_id is not None:
            self.final_turns_left -= 1
            if self.final_turns_left <= 0:
                self._tally_and_finish()
                return

        self.turn_idx = (self.turn_idx + 1) % len(self.players)
        self.turn_player_id = self.players[self.turn_idx].id
        self.turn_stage = "choose_source"

    def _tally_and_finish(self) -> None:
        totals: dict[str, int] = {}
        for p in self.players:
            pts = sum(c["points"] for c in self.hands[p.id] if c is not None)
            p.score = pts
            totals[p.id] = pts
        min_pts = min(totals.values())
        winners = [p.id for p in self.players if totals[p.id] == min_pts]
        # Rule nuance: if caller tied, non-caller wins or shared? Standard: lowest score wins!
        names = ", ".join(p.name for p in self.players if p.id in winners)
        self.finish_game(
            winners,
            f"All cards revealed! Lowest score: {names} with {min_pts} points.",
        )

    def _is_target_locked(self, target_id: str) -> bool:
        return self.skru_caller_id is not None and target_id == self.skru_caller_id

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase == "pre_game":
            if player_id not in self.hands:
                return False, "Spectators cannot act."
            if action == "ready":
                self.ready_players.add(player_id)
                if len(self.ready_players) >= len(self.players):
                    self._begin_play()
                return True, ""
            return False, "Wait for pre-game peek to finish (or click READY)."

        if self.phase != "playing":
            return False, "Match is not active."
        if player_id != self.turn_player_id:
            return False, "It is not your turn."

        player = self.get_player(player_id)
        hand = self.hands[player_id]

        if self.turn_stage == "choose_source":
            if action == "skru":
                if self.skru_caller_id is not None:
                    return False, "SKRU has already been called."
                self.skru_caller_id = player_id
                self.final_turns_left = len(self.players)
                self.log_event(
                    f"{player.name} called SKRU! Everyone else gets 1 final turn.",
                    kind="finish",
                )
                self._end_turn()
                return True, ""

            if action == "draw_deck":
                card = self._draw_from_deck()
                if not card:
                    self._tally_and_finish()
                    return True, ""
                self.drawn_card = card
                self.turn_stage = "resolve_drawn"
                return True, ""

            if action == "take_discard":
                if not self.discard_pile:
                    return False, "Discard pile is empty."
                self.drawn_card = self.discard_pile.pop()
                self.turn_stage = "choose_swap_discard"
                return True, ""

            if action == "basra":
                if not self.discard_pile:
                    return False, "No top discard card to match."
                slot = self._safe_int(data.get("slot"))
                if slot is None or not (0 <= slot < len(hand)) or hand[slot] is None:
                    return False, "Selected slot is empty."
                top = self.discard_pile[-1]
                chosen = hand[slot]
                if chosen["code"] == top["code"]:
                    hand[slot] = None
                    self.discard_pile.append(chosen)
                    self._invalidate_slot_knowledge(player_id, slot)
                    self.log_event(f"{player.name} nailed a Basra toss ({chosen['label']})!")
                    if all(c is None for c in hand):
                        self._tally_and_finish()
                        return True, ""
                    self._end_turn()
                    return True, ""
                else:
                    penalty = self._draw_from_deck()
                    if penalty:
                        placed = False
                        for idx, c in enumerate(hand):
                            if c is None:
                                hand[idx] = penalty
                                self._invalidate_slot_knowledge(player_id, idx)
                                placed = True
                                break
                        if not placed:
                            hand.append(penalty)
                    self.log_event(
                        f"{player.name} missed Basra ({chosen['label']} ≠ {top['label']}) — +1 penalty card!",
                        kind="warn",
                    )
                    self._end_turn()
                    return True, ""

            return False, "Choose Draw Deck, Take Discard, Basra, or SKRU."

        if self.turn_stage in ("resolve_drawn", "choose_swap_discard"):
            if action == "swap_drawn":
                slot = self._safe_int(data.get("slot"))
                if slot is None or not (0 <= slot < len(hand)) or hand[slot] is None:
                    return False, "Must choose an occupied card slot."
                old = hand[slot]
                hand[slot] = self.drawn_card
                self.discard_pile.append(old)
                self._invalidate_slot_knowledge(player_id, slot, preserve_bot_id=player_id)
                if player_id in self.bot_memory:
                    self.bot_memory[player_id][f"{player_id}:{slot}"] = self.drawn_card["points"]
                self.log_event(f"{player.name} swapped a card and discarded {old['label']}.")
                self._end_turn()
                return True, ""

            if action == "discard_drawn" and self.turn_stage == "resolve_drawn":
                card = self.drawn_card
                self.discard_pile.append(card)
                self.drawn_card = None
                power = card.get("power")
                self.log_event(f"{player.name} discarded drawn {card['label']}.")

                if power == "peek_self":
                    self.turn_stage = "power_peek_self"
                    return True, ""
                if power == "peek_opp":
                    # Only proceed if at least one unlocked opponent has a card
                    if any(
                        p.id != player_id
                        and not self._is_target_locked(p.id)
                        and any(c is not None for c in self.hands[p.id])
                        for p in self.players
                    ):
                        self.turn_stage = "power_peek_opp"
                        return True, ""
                    self._end_turn()
                    return True, ""
                if power == "blind_swap":
                    if any(
                        p.id != player_id
                        and not self._is_target_locked(p.id)
                        and any(c is not None for c in self.hands[p.id])
                        for p in self.players
                    ) and any(c is not None for c in hand):
                        self.turn_stage = "power_blind_swap"
                        return True, ""
                    self._end_turn()
                    return True, ""
                if power == "look_swap":
                    if any(
                        p.id != player_id
                        and not self._is_target_locked(p.id)
                        and any(c is not None for c in self.hands[p.id])
                        for p in self.players
                    ) and any(c is not None for c in hand):
                        self.turn_stage = "power_king_peek"
                        return True, ""
                    self._end_turn()
                    return True, ""

                self._end_turn()
                return True, ""

            return False, "Choose a card slot to swap or discard."

        if self.turn_stage == "power_peek_self":
            if action != "peek":
                return False, "Select one of your own cards to peek."
            slot = self._safe_int(data.get("slot"))
            if slot is None or not (0 <= slot < len(hand)) or hand[slot] is None:
                return False, "Invalid card slot."
            self.private_peeks[player_id]["last_peek"] = {
                "owner_id": player_id,
                "slot": slot,
                "card": hand[slot],
            }
            if player_id in self.bot_memory:
                self.bot_memory[player_id][f"{player_id}:{slot}"] = hand[slot]["points"]
            self.log_event(f"{player.name} peeked at one of their own cards.")
            self._end_turn()
            return True, ""

        if self.turn_stage == "power_peek_opp":
            if action != "peek":
                return False, "Select an opponent's card to peek."
            target_id = str(data.get("target_id", ""))
            slot = self._safe_int(data.get("slot"))
            if target_id == player_id or target_id not in self.hands:
                return False, "Invalid opponent."
            if self._is_target_locked(target_id):
                return False, "SKRU caller's cards are locked."
            t_hand = self.hands[target_id]
            if slot is None or not (0 <= slot < len(t_hand)) or t_hand[slot] is None:
                return False, "Invalid target card slot."
            self.private_peeks[player_id]["last_peek"] = {
                "owner_id": target_id,
                "slot": slot,
                "card": t_hand[slot],
            }
            if player_id in self.bot_memory:
                self.bot_memory[player_id][f"{target_id}:{slot}"] = t_hand[slot]["points"]
            target_p = self.get_player(target_id)
            self.log_event(f"{player.name} peeked at {target_p.name if target_p else target_id}'s card.")
            self._end_turn()
            return True, ""

        if self.turn_stage == "power_blind_swap":
            if action != "swap":
                return False, "Select your slot and an opponent's slot to blind swap."
            my_slot = self._safe_int(data.get("my_slot"))
            target_id = str(data.get("target_id", ""))
            opp_slot = self._safe_int(data.get("opp_slot"))
            if target_id == player_id or target_id not in self.hands:
                return False, "Invalid opponent."
            if self._is_target_locked(target_id):
                return False, "SKRU caller's cards are locked."
            t_hand = self.hands[target_id]
            if my_slot is None or not (0 <= my_slot < len(hand)) or hand[my_slot] is None:
                return False, "Invalid own slot."
            if opp_slot is None or not (0 <= opp_slot < len(t_hand)) or t_hand[opp_slot] is None:
                return False, "Invalid opponent slot."
            hand[my_slot], t_hand[opp_slot] = t_hand[opp_slot], hand[my_slot]
            self._swap_slot_knowledge(player_id, my_slot, target_id, opp_slot)
            target_p = self.get_player(target_id)
            self.log_event(
                f"{player.name} blind-swapped a card with {target_p.name if target_p else target_id}."
            )
            self._end_turn()
            return True, ""

        if self.turn_stage == "power_king_peek":
            if action != "peek":
                return False, "Pick one of your cards and one opponent card to inspect."
            my_slot = self._safe_int(data.get("my_slot"))
            target_id = str(data.get("target_id", ""))
            opp_slot = self._safe_int(data.get("opp_slot"))
            if target_id == player_id or target_id not in self.hands:
                return False, "Invalid opponent."
            if self._is_target_locked(target_id):
                return False, "SKRU caller's cards are locked."
            t_hand = self.hands[target_id]
            if my_slot is None or not (0 <= my_slot < len(hand)) or hand[my_slot] is None:
                return False, "Invalid own slot."
            if opp_slot is None or not (0 <= opp_slot < len(t_hand)) or t_hand[opp_slot] is None:
                return False, "Invalid opponent slot."

            self.king_context = {
                "my_slot": my_slot,
                "target_id": target_id,
                "opp_slot": opp_slot,
                "my_card": hand[my_slot],
                "opp_card": t_hand[opp_slot],
            }
            if player_id in self.bot_memory:
                self.bot_memory[player_id][f"{player_id}:{my_slot}"] = hand[my_slot]["points"]
                self.bot_memory[player_id][f"{target_id}:{opp_slot}"] = t_hand[opp_slot]["points"]
            self.turn_stage = "power_king_decide"
            return True, ""

        if self.turn_stage == "power_king_decide":
            if action != "king_decide":
                return False, "Decide whether to swap or keep the peeked cards."
            do_swap = bool(data.get("swap", False))
            ctx = self.king_context or {}
            if do_swap and ctx:
                ms = ctx["my_slot"]
                tid = ctx["target_id"]
                oslot = ctx["opp_slot"]
                self.hands[player_id][ms], self.hands[tid][oslot] = (
                    self.hands[tid][oslot],
                    self.hands[player_id][ms],
                )
                self._swap_slot_knowledge(player_id, ms, tid, oslot)
                self.log_event(f"{player.name} used King power and swapped cards!")
            else:
                self.log_event(f"{player.name} used King power and declined to swap.")
            self._end_turn()
            return True, ""

        return False, "Invalid turn state."

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.turn_player_id != bot_id:
            return None
        hand = self.hands[bot_id]
        mem = self.bot_memory.setdefault(bot_id, {})
        occupied_slots = [i for i, c in enumerate(hand) if c is not None]
        unlocked_opps = [
            p.id
            for p in self.players
            if p.id != bot_id
            and not self._is_target_locked(p.id)
            and any(c is not None for c in self.hands[p.id])
        ]

        diff = self.get_difficulty()

        if self.turn_stage == "choose_source":
            known_vals = [mem.get(f"{bot_id}:{s}") for s in occupied_slots]
            skru_cap = 4 if diff == "easy" else (9 if diff == "hard" else 7)
            if (
                self.skru_caller_id is None
                and all(v is not None for v in known_vals)
                and sum(v for v in known_vals if v is not None) <= skru_cap
            ):
                return "skru", {}
            discard_cap = 1 if diff == "easy" else (4 if diff == "hard" else 3)
            if self.discard_pile and self.discard_pile[-1]["points"] <= discard_cap and occupied_slots:
                return "take_discard", {}
            return "draw_deck", {}

        if self.turn_stage in ("resolve_drawn", "choose_swap_discard"):
            card = self.drawn_card
            if not occupied_slots:
                return "discard_drawn", {}
            if diff == "easy" and random.random() < 0.35:
                slot = random.choice(occupied_slots)
                return ("swap_drawn", {"slot": slot}) if (card and card["points"] <= 5) else ("discard_drawn", {})
            # Find highest known card in own hand (Hard remembers unknown as ~8 risk)
            default_est = 8 if diff == "hard" else 7
            worst_slot = max(
                occupied_slots,
                key=lambda s: mem.get(f"{bot_id}:{s}", default_est),
            )
            worst_val = mem.get(f"{bot_id}:{worst_slot}", default_est)
            if card and (card["points"] < worst_val or self.turn_stage == "choose_swap_discard"):
                return "swap_drawn", {"slot": worst_slot}
            return "discard_drawn", {}

        if self.turn_stage == "power_peek_self":
            unknown = [s for s in occupied_slots if f"{bot_id}:{s}" not in mem]
            slot = unknown[0] if unknown else occupied_slots[0]
            return "peek", {"slot": slot}

        if self.turn_stage == "power_peek_opp" and unlocked_opps:
            tid = random.choice(unlocked_opps)
            opp_slots = [i for i, c in enumerate(self.hands[tid]) if c is not None]
            return "peek", {"target_id": tid, "slot": random.choice(opp_slots)}

        if self.turn_stage == "power_blind_swap" and unlocked_opps and occupied_slots:
            tid = random.choice(unlocked_opps)
            opp_slots = [i for i, c in enumerate(self.hands[tid]) if c is not None]
            worst_slot = max(occupied_slots, key=lambda s: mem.get(f"{bot_id}:{s}", 7))
            return "swap", {"my_slot": worst_slot, "target_id": tid, "opp_slot": random.choice(opp_slots)}

        if self.turn_stage == "power_king_peek" and unlocked_opps and occupied_slots:
            tid = random.choice(unlocked_opps)
            opp_slots = [i for i, c in enumerate(self.hands[tid]) if c is not None]
            worst_slot = max(occupied_slots, key=lambda s: mem.get(f"{bot_id}:{s}", 7))
            return "peek", {"my_slot": worst_slot, "target_id": tid, "opp_slot": random.choice(opp_slots)}

        if self.turn_stage == "power_king_decide":
            ctx = self.king_context or {}
            my_pts = ctx.get("my_card", {}).get("points", 10)
            opp_pts = ctx.get("opp_card", {}).get("points", 10)
            return "king_decide", {"swap": opp_pts < my_pts}

        return None

    def get_public_state(self) -> dict[str, Any]:
        now = time.time()
        peek_rem = (
            max(0.0, self.peek_seconds - (now - self.pre_game_started_at))
            if self.phase == "pre_game"
            else 0.0
        )
        hands_public: dict[str, list[dict[str, Any] | None]] = {}
        for pid, cards in self.hands.items():
            if self.phase == "finished":
                hands_public[pid] = list(cards)
            else:
                hands_public[pid] = [
                    {"hidden": True} if c is not None else None for c in cards
                ]
        return {
            "phase": self.phase,
            "pre_game_remaining": round(peek_rem, 1),
            "ready_players": sorted(self.ready_players),
            "turn_player_id": self.turn_player_id,
            "turn_stage": self.turn_stage,
            "deck_count": len(self.deck),
            "discard_top": self.discard_pile[-1] if self.discard_pile else None,
            "discard_count": len(self.discard_pile),
            "hands": hands_public,
            "skru_caller_id": self.skru_caller_id,
            "final_turns_left": self.final_turns_left,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        if player_id not in self.hands:
            return {}
        priv = self.private_peeks.get(player_id, {})
        king_view = None
        if player_id == self.turn_player_id and self.turn_stage == "power_king_decide" and self.king_context:
            king_view = {
                "my_slot": self.king_context["my_slot"],
                "target_id": self.king_context["target_id"],
                "opp_slot": self.king_context["opp_slot"],
                "my_card": self.king_context["my_card"],
                "opp_card": self.king_context["opp_card"],
            }
        return {
            "initial_bottom": priv.get("initial_bottom", {}),
            "last_peek": priv.get("last_peek"),
            "drawn_card": self.drawn_card if player_id == self.turn_player_id else None,
            "king_view": king_view,
        }
