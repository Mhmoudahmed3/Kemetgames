"""2-6P Monopoly engine with 40 tiles, 15s live auctions, color monopolies, houses/hotels, jail, trades, mortgages & bankruptcy."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

MONOPOLY_START_CASH = {"easy": 1800, "mid": 1500, "hard": 1200}

BOARD_TILES: list[dict[str, Any]] = [
    {"id": 0, "name": "GO", "kind": "go"},
    {"id": 1, "name": "Mediterranean Ave", "kind": "prop", "group": "brown", "price": 60, "rent": [2, 10, 30, 90, 160, 250], "house_cost": 50},
    {"id": 2, "name": "Community Chest", "kind": "chest"},
    {"id": 3, "name": "Baltic Ave", "kind": "prop", "group": "brown", "price": 60, "rent": [4, 20, 60, 180, 320, 450], "house_cost": 50},
    {"id": 4, "name": "Income Tax", "kind": "tax", "amount": 200},
    {"id": 5, "name": "Reading Railroad", "kind": "railroad", "price": 200},
    {"id": 6, "name": "Oriental Ave", "kind": "prop", "group": "light_blue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50},
    {"id": 7, "name": "Chance", "kind": "chance"},
    {"id": 8, "name": "Vermont Ave", "kind": "prop", "group": "light_blue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50},
    {"id": 9, "name": "Connecticut Ave", "kind": "prop", "group": "light_blue", "price": 120, "rent": [8, 40, 100, 300, 450, 600], "house_cost": 50},
    {"id": 10, "name": "Jail / Visiting", "kind": "jail"},
    {"id": 11, "name": "St. Charles Place", "kind": "prop", "group": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100},
    {"id": 12, "name": "Electric Company", "kind": "utility", "price": 150},
    {"id": 13, "name": "States Ave", "kind": "prop", "group": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100},
    {"id": 14, "name": "Virginia Ave", "kind": "prop", "group": "pink", "price": 160, "rent": [12, 60, 180, 500, 700, 900], "house_cost": 100},
    {"id": 15, "name": "Pennsylvania RR", "kind": "railroad", "price": 200},
    {"id": 16, "name": "St. James Place", "kind": "prop", "group": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100},
    {"id": 17, "name": "Community Chest", "kind": "chest"},
    {"id": 18, "name": "Tennessee Ave", "kind": "prop", "group": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100},
    {"id": 19, "name": "New York Ave", "kind": "prop", "group": "orange", "price": 200, "rent": [16, 80, 220, 600, 800, 1000], "house_cost": 100},
    {"id": 20, "name": "Free Parking", "kind": "parking"},
    {"id": 21, "name": "Kentucky Ave", "kind": "prop", "group": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150},
    {"id": 22, "name": "Chance", "kind": "chance"},
    {"id": 23, "name": "Indiana Ave", "kind": "prop", "group": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150},
    {"id": 24, "name": "Illinois Ave", "kind": "prop", "group": "red", "price": 240, "rent": [20, 100, 300, 750, 925, 1100], "house_cost": 150},
    {"id": 25, "name": "B. & O. Railroad", "kind": "railroad", "price": 200},
    {"id": 26, "name": "Atlantic Ave", "kind": "prop", "group": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150},
    {"id": 27, "name": "Ventnor Ave", "kind": "prop", "group": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150},
    {"id": 28, "name": "Water Works", "kind": "utility", "price": 150},
    {"id": 29, "name": "Marvin Gardens", "kind": "prop", "group": "yellow", "price": 280, "rent": [24, 120, 360, 850, 1025, 1200], "house_cost": 150},
    {"id": 30, "name": "Go To Jail", "kind": "go_jail"},
    {"id": 31, "name": "Pacific Ave", "kind": "prop", "group": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200},
    {"id": 32, "name": "North Carolina", "kind": "prop", "group": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200},
    {"id": 33, "name": "Community Chest", "kind": "chest"},
    {"id": 34, "name": "Pennsylvania Ave", "kind": "prop", "group": "green", "price": 320, "rent": [28, 150, 450, 1000, 1200, 1400], "house_cost": 200},
    {"id": 35, "name": "Short Line RR", "kind": "railroad", "price": 200},
    {"id": 36, "name": "Chance", "kind": "chance"},
    {"id": 37, "name": "Park Place", "kind": "prop", "group": "dark_blue", "price": 350, "rent": [35, 175, 500, 1100, 1300, 1500], "house_cost": 200},
    {"id": 38, "name": "Luxury Tax", "kind": "tax", "amount": 100},
    {"id": 39, "name": "Boardwalk", "kind": "prop", "group": "dark_blue", "price": 400, "rent": [50, 200, 600, 1400, 1700, 2000], "house_cost": 200},
]

COLOR_GROUPS: dict[str, list[int]] = {}
for _t in BOARD_TILES:
    if _t["kind"] == "prop":
        COLOR_GROUPS.setdefault(_t["group"], []).append(_t["id"])

CHANCE_CARDS = [
    {"text": "Advance to GO (Collect $200)", "effect": "move", "target": 0},
    {"text": "Advance to Illinois Ave", "effect": "move", "target": 24},
    {"text": "Advance to Boardwalk", "effect": "move", "target": 39},
    {"text": "Bank pays dividend of $50", "effect": "cash", "amount": 50},
    {"text": "Speeding fine — Pay $15", "effect": "cash", "amount": -15},
    {"text": "Your building loan matures — Collect $150", "effect": "cash", "amount": 150},
    {"text": "Get Out of Jail Free", "effect": "goojf"},
    {"text": "Go directly to Jail!", "effect": "jail"},
]

CHEST_CARDS = [
    {"text": "Advance to GO (Collect $200)", "effect": "move", "target": 0},
    {"text": "Bank error in your favor — Collect $200", "effect": "cash", "amount": 200},
    {"text": "Doctor's fee — Pay $50", "effect": "cash", "amount": -50},
    {"text": "From sale of stock you get $50", "effect": "cash", "amount": 50},
    {"text": "Holiday fund matures — Collect $100", "effect": "cash", "amount": 100},
    {"text": "Hospital fees — Pay $100", "effect": "cash", "amount": -100},
    {"text": "Get Out of Jail Free", "effect": "goojf"},
    {"text": "Go directly to Jail!", "effect": "jail"},
]


class MonopolyGame(BaseGame):
    GAME_TYPE = "monopoly"
    TITLE = "BLACKOUT MONOPOLY"
    CATEGORY = "Tabletop"
    DESCRIPTION = (
        "2-6 player 40-tile Monopoly economy: live 15s auctions, color-set houses/hotels, railroads, utilities, jail, mortgages, and live trades."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 6
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"difficulty": "mid"}

    AUCTION_SECONDS = 15.0

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.p_state: dict[str, dict[str, Any]] = {}
        self.ownership: dict[int, str] = {}
        self.houses: dict[int, int] = {}
        self.mortgaged: set[int] = set()
        self.turn_idx: int = 0
        self.subphase: str = "roll"  # roll | buy_or_auction | auction | end_turn | resolve_debt
        self.last_dice: list[int] = []
        self.doubles_count: int = 0
        self.extra_turn_pending: bool = False
        self.auction: dict[str, Any] | None = None
        self.pending_debt: dict[str, Any] | None = None
        self.pending_trade: dict[str, Any] | None = None
        self.last_card_text: str = ""

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = diff
        start_cash = MONOPOLY_START_CASH[diff]
        self.p_state = {}
        for p in self.players:
            p.score = start_cash
            self.p_state[p.id] = {
                "cash": start_cash,
                "pos": 0,
                "in_jail": False,
                "jail_turns": 0,
                "goojf": 0,
                "bankrupt": False,
            }
        self.ownership = {}
        self.houses = {}
        self.mortgaged = set()
        self.turn_idx = 0
        self.turn_player_id = self.players[0].id
        self.subphase = "roll"
        self.last_dice = []
        self.doubles_count = 0
        self.extra_turn_pending = False
        self.auction = None
        self.pending_debt = None
        self.pending_trade = None
        self.last_card_text = ""
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        self.log_event(f"Monopoly launched ({diff.upper()})! Each player starts with ${start_cash}.")

    def _recompute_net_worth(self) -> None:
        for p in self.players:
            st = self.p_state[p.id]
            if st["bankrupt"]:
                p.score = 0
                continue
            worth = st["cash"]
            for tid, owner in self.ownership.items():
                if owner == p.id:
                    tile = BOARD_TILES[tid]
                    worth += tile["price"] // 2 if tid in self.mortgaged else tile["price"]
                    worth += self.houses.get(tid, 0) * tile.get("house_cost", 0)
            p.score = worth

    def _has_monopoly(self, player_id: str, group: str) -> bool:
        tids = COLOR_GROUPS.get(group, [])
        return bool(tids) and all(
            self.ownership.get(tid) == player_id and tid not in self.mortgaged
            for tid in tids
        )

    def _liquidation_value(self, player_id: str) -> int:
        total = self.p_state[player_id]["cash"]
        for tid, owner in self.ownership.items():
            if owner == player_id:
                tile = BOARD_TILES[tid]
                total += self.houses.get(tid, 0) * (tile.get("house_cost", 0) // 2)
                if tid not in self.mortgaged:
                    total += tile["price"] // 2
        return total

    def _charge_player(
        self, player_id: str, amount: int, creditor_id: str | None, reason: str
    ) -> None:
        st = self.p_state[player_id]
        if st["cash"] >= amount:
            st["cash"] -= amount
            if creditor_id and creditor_id in self.p_state:
                self.p_state[creditor_id]["cash"] += amount
            return

        if self._liquidation_value(player_id) < amount:
            self._bankrupt_player(player_id, creditor_id, reason)
            return

        self.pending_debt = {
            "debtor_id": player_id,
            "creditor_id": creditor_id,
            "amount": amount,
            "reason": reason,
        }
        self.subphase = "resolve_debt"
        p = self.get_player(player_id)
        self.log_event(
            f"{p.name if p else player_id} owes ${amount} ({reason}) — mortgage or sell houses to pay!",
            kind="warn",
        )

    def _bankrupt_player(
        self, player_id: str, creditor_id: str | None, reason: str
    ) -> None:
        st = self.p_state[player_id]
        st["bankrupt"] = True
        remaining_cash = max(0, st["cash"])
        st["cash"] = 0

        if creditor_id and creditor_id in self.p_state and not self.p_state[creditor_id]["bankrupt"]:
            self.p_state[creditor_id]["cash"] += remaining_cash
            self.p_state[creditor_id]["goojf"] += st["goojf"]
            for tid, owner in list(self.ownership.items()):
                if owner == player_id:
                    self.ownership[tid] = creditor_id
                    self.houses[tid] = 0
        else:
            for tid, owner in list(self.ownership.items()):
                if owner == player_id:
                    del self.ownership[tid]
                    self.houses.pop(tid, None)
                    self.mortgaged.discard(tid)

        st["goojf"] = 0
        p = self.get_player(player_id)
        self.log_event(f"{p.name if p else player_id} declared BANKRUPTCY ({reason})!", kind="warn")
        self.pending_debt = None
        self.pending_trade = None
        self._recompute_net_worth()

        solvent = [pl for pl in self.players if not self.p_state[pl.id]["bankrupt"]]
        if len(solvent) <= 1:
            winner = solvent[0] if solvent else self.players[0]
            self.finish_game([winner.id], f"{winner.name} bankrupted all rivals and won Monopoly!")
            return
        self._advance_turn()

    def _advance_turn(self) -> None:
        if self.phase != "playing":
            return
        if self.extra_turn_pending and not self.p_state[self.turn_player_id]["in_jail"] and not self.p_state[self.turn_player_id]["bankrupt"]:
            self.extra_turn_pending = False
            self.subphase = "roll"
            return

        self.extra_turn_pending = False
        self.doubles_count = 0
        for _ in range(len(self.players)):
            self.turn_idx = (self.turn_idx + 1) % len(self.players)
            pid = self.players[self.turn_idx].id
            if not self.p_state[pid]["bankrupt"]:
                self.turn_player_id = pid
                self.subphase = "roll"
                return

    def _send_to_jail(self, player_id: str) -> None:
        st = self.p_state[player_id]
        st["pos"] = 10
        st["in_jail"] = True
        st["jail_turns"] = 0
        self.extra_turn_pending = False
        self.doubles_count = 0
        p = self.get_player(player_id)
        self.log_event(f"{p.name if p else player_id} was sent to Jail!", kind="warn")
        self.subphase = "end_turn"

    def _move_and_resolve(self, player_id: str, steps: int, dice_sum: int) -> None:
        st = self.p_state[player_id]
        old_pos = st["pos"]
        new_pos = (old_pos + steps) % 40
        if new_pos < old_pos and steps > 0:
            st["cash"] += 200
            p = self.get_player(player_id)
            self.log_event(f"{p.name if p else player_id} passed GO and collected $200.")
        st["pos"] = new_pos
        self._resolve_landing(player_id, new_pos, dice_sum)

    def _resolve_landing(self, player_id: str, pos: int, dice_sum: int) -> None:
        tile = BOARD_TILES[pos]
        kind = tile["kind"]
        p = self.get_player(player_id)
        pname = p.name if p else player_id

        if kind in ("go", "jail", "parking"):
            self.subphase = "end_turn"
            return

        if kind == "go_jail":
            self._send_to_jail(player_id)
            return

        if kind == "tax":
            amt = tile["amount"]
            self.log_event(f"{pname} landed on {tile['name']} (-${amt}).")
            self.subphase = "end_turn"
            self._charge_player(player_id, amt, None, tile["name"])
            return

        if kind in ("chance", "chest"):
            card = random.choice(CHANCE_CARDS if kind == "chance" else CHEST_CARDS)
            self.last_card_text = f"{tile['name']}: {card['text']}"
            self.log_event(f"{pname} drew {self.last_card_text}")
            eff = card["effect"]
            if eff == "cash":
                amt = card["amount"]
                if amt >= 0:
                    self.p_state[player_id]["cash"] += amt
                    self.subphase = "end_turn"
                else:
                    self.subphase = "end_turn"
                    self._charge_player(player_id, -amt, None, card["text"])
            elif eff == "goojf":
                self.p_state[player_id]["goojf"] += 1
                self.subphase = "end_turn"
            elif eff == "jail":
                self._send_to_jail(player_id)
            elif eff == "move":
                target = card["target"]
                if target < pos:
                    self.p_state[player_id]["cash"] += 200
                self.p_state[player_id]["pos"] = target
                self._resolve_landing(player_id, target, dice_sum)
            return

        if kind in ("prop", "railroad", "utility"):
            owner = self.ownership.get(pos)
            if owner is None:
                self.subphase = "buy_or_auction"
                return
            if owner == player_id or pos in self.mortgaged or self.p_state[owner]["bankrupt"]:
                self.subphase = "end_turn"
                return

            rent = self._compute_rent(pos, owner, dice_sum)
            owner_p = self.get_player(owner)
            self.log_event(
                f"{pname} paid ${rent} rent to {owner_p.name if owner_p else owner} for {tile['name']}."
            )
            self.subphase = "end_turn"
            self._charge_player(player_id, rent, owner, f"Rent on {tile['name']}")

    def _compute_rent(self, tile_id: int, owner_id: str, dice_sum: int) -> int:
        tile = BOARD_TILES[tile_id]
        kind = tile["kind"]
        if kind == "prop":
            houses = self.houses.get(tile_id, 0)
            base = tile["rent"][houses]
            if houses == 0 and self._has_monopoly(owner_id, tile["group"]):
                return base * 2
            return base
        if kind == "railroad":
            rr_count = sum(
                1
                for tid, own in self.ownership.items()
                if own == owner_id and BOARD_TILES[tid]["kind"] == "railroad" and tid not in self.mortgaged
            )
            return 25 * (2 ** max(0, rr_count - 1))
        if kind == "utility":
            util_count = sum(
                1
                for tid, own in self.ownership.items()
                if own == owner_id and BOARD_TILES[tid]["kind"] == "utility" and tid not in self.mortgaged
            )
            mult = 10 if util_count >= 2 else 4
            return mult * max(2, dice_sum)
        return 0

    def _start_auction(self, tile_id: int) -> None:
        self.subphase = "auction"
        self.auction = {
            "tile_id": tile_id,
            "highest_bid": 0,
            "highest_bidder": None,
            "ends_at": time.time() + self.AUCTION_SECONDS,
            "passed": [],
        }
        self.log_event(
            f"15s Auction started for {BOARD_TILES[tile_id]['name']}!", kind="warn"
        )

    def _finalize_auction(self) -> None:
        auc = self.auction
        if not auc:
            return
        tid = auc["tile_id"]
        bid = auc["highest_bid"]
        bidder = auc["highest_bidder"]
        if bidder and bid > 0 and self.p_state[bidder]["cash"] >= bid:
            self.p_state[bidder]["cash"] -= bid
            self.ownership[tid] = bidder
            bp = self.get_player(bidder)
            self.log_event(
                f"{bp.name if bp else bidder} won {BOARD_TILES[tid]['name']} at auction for ${bid}!",
                kind="finish",
            )
        else:
            self.log_event(f"No bids placed for {BOARD_TILES[tid]['name']}. Remains unowned.")
        self.auction = None
        self.subphase = "end_turn"
        self._recompute_net_worth()

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing":
            return False
        if self.subphase == "auction" and self.auction:
            if now >= self.auction["ends_at"]:
                self._finalize_auction()
                return True
            sec_left = int(max(0.0, self.auction["ends_at"] - now))
            if self.auction.get("last_sec") != sec_left:
                self.auction["last_sec"] = sec_left
                return True
        return False

    def get_active_bot_ids(self) -> list[str]:
        if self.phase != "playing":
            return []
        if self.pending_trade:
            target = self.get_player(self.pending_trade["to_id"])
            if target and target.is_bot:
                return [target.id]
        if self.subphase == "auction" and self.auction:
            return [
                p.id
                for p in self.players
                if p.is_bot
                and not self.p_state[p.id]["bankrupt"]
                and p.id not in self.auction["passed"]
                and self.auction["highest_bidder"] != p.id
            ]
        return super().get_active_bot_ids()

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        diff = self.get_difficulty()
        if self.pending_trade and self.pending_trade["to_id"] == bot_id:
            t = self.pending_trade
            min_edge = 0 if diff == "easy" else (150 if diff == "hard" else 50)
            accept = t["offer_cash"] >= t["request_cash"] + min_edge and not t["request_props"]
            return ("accept_trade" if accept else "reject_trade"), {}

        if self.subphase == "auction" and self.auction:
            tid = self.auction["tile_id"]
            list_price = BOARD_TILES[tid]["price"]
            next_bid = max(10, self.auction["highest_bid"] + 10)
            bid_mult = 0.80 if diff == "easy" else (1.35 if diff == "hard" else 1.10)
            bid_buf = 250 if diff == "easy" else (80 if diff == "hard" else 150)
            if next_bid <= int(list_price * bid_mult) and self.p_state[bot_id]["cash"] >= next_bid + bid_buf:
                return "bid", {"amount": next_bid}
            return "pass_auction", {}

        if bot_id != self.turn_player_id:
            return None

        st = self.p_state[bot_id]
        if self.subphase == "roll":
            if st["in_jail"]:
                if st["goojf"] > 0:
                    return "use_goojf", {}
                if st["cash"] >= 200:
                    return "pay_jail", {}
            return "roll", {}

        if self.subphase == "buy_or_auction":
            price = BOARD_TILES[st["pos"]]["price"]
            buy_buf = 250 if diff == "easy" else (40 if diff == "hard" else 100)
            if st["cash"] >= price + buy_buf:
                return "buy", {}
            return "pass_buy", {}

        if self.subphase == "resolve_debt":
            improved = [
                tid
                for tid, owner in self.ownership.items()
                if owner == bot_id and self.houses.get(tid, 0) > 0
            ]
            if improved:
                # Sell from the property with highest house count so the even-selling rule is satisfied
                best_tid = max(improved, key=lambda t: self.houses.get(t, 0))
                return "sell_house", {"tile_id": best_tid}
            for tid, owner in self.ownership.items():
                if owner == bot_id and tid not in self.mortgaged and self.houses.get(tid, 0) == 0:
                    return "mortgage", {"tile_id": tid}
            if self.pending_debt and st["cash"] >= self.pending_debt["amount"]:
                return "pay_debt", {}
            return "declare_bankrupt", {}

        if self.subphase == "end_turn":
            house_buf = 500 if diff == "easy" else (200 if diff == "hard" else 350)
            for group, tids in COLOR_GROUPS.items():
                if self._has_monopoly(bot_id, group):
                    min_h = min(self.houses.get(t, 0) for t in tids)
                    if min_h < 5:
                        cand = next(t for t in tids if self.houses.get(t, 0) == min_h)
                        cost = BOARD_TILES[cand]["house_cost"]
                        if st["cash"] >= cost + house_buf:
                            return "build_house", {"tile_id": cand}
            return "end_turn", {}

        return None

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        if player_id not in self.p_state or self.p_state[player_id]["bankrupt"]:
            return False, "Bankrupt players cannot act."

        st = self.p_state[player_id]
        player = self.get_player(player_id)

        # Auction bidding (any non-bankrupt player)
        if action in ("bid", "pass_auction"):
            if self.subphase != "auction" or not self.auction:
                return False, "No auction in progress."
            if action == "pass_auction":
                if player_id not in self.auction["passed"]:
                    self.auction["passed"].append(player_id)
                active_bidders = [
                    p.id
                    for p in self.players
                    if not self.p_state[p.id]["bankrupt"] and p.id not in self.auction["passed"]
                ]
                if len(active_bidders) == 0 or (
                    len(active_bidders) == 1 and self.auction["highest_bidder"] == active_bidders[0]
                ):
                    self._finalize_auction()
                return True, ""

            try:
                amount = int(data.get("amount", 0))
            except (TypeError, ValueError):
                return False, "Invalid bid amount."
            if amount <= self.auction["highest_bid"]:
                return False, "Bid must exceed current highest bid."
            if amount > st["cash"]:
                return False, "Insufficient cash for bid."
            self.auction["highest_bid"] = amount
            self.auction["highest_bidder"] = player_id
            if player_id in self.auction["passed"]:
                self.auction["passed"].remove(player_id)
            if self.auction["ends_at"] - time.time() < 4.0:
                self.auction["ends_at"] = time.time() + 4.0
            self.log_event(f"{player.name} bid ${amount}.")
            active_bidders = [
                p.id
                for p in self.players
                if not self.p_state[p.id]["bankrupt"] and p.id not in self.auction["passed"]
            ]
            if len(active_bidders) == 1 and active_bidders[0] == player_id:
                self._finalize_auction()
            return True, ""

        # Trade actions (forbidden during auction or debt resolution)
        if action == "propose_trade":
            if self.subphase in ("auction", "resolve_debt"):
                return False, "Cannot propose trades during an auction or debt resolution."
            if self.pending_trade:
                return False, "Another trade proposal is already pending."
            to_id = str(data.get("to_id", ""))
            if to_id == player_id or to_id not in self.p_state or self.p_state[to_id]["bankrupt"]:
                return False, "Invalid trade partner."
            raw_oc = data.get("offer_cash", 0) or 0
            raw_rc = data.get("request_cash", 0) or 0
            raw_op = data.get("offer_props", [])
            raw_rp = data.get("request_props", [])
            if (
                isinstance(raw_oc, bool)
                or isinstance(raw_rc, bool)
                or not isinstance(raw_op, list)
                or not isinstance(raw_rp, list)
            ):
                return False, "Invalid trade payload."
            try:
                offer_cash = int(raw_oc)
                request_cash = int(raw_rc)
                offer_props = []
                for t in raw_op:
                    if isinstance(t, bool):
                        return False, "Invalid property ID in trade."
                    offer_props.append(int(t))
                request_props = []
                for t in raw_rp:
                    if isinstance(t, bool):
                        return False, "Invalid property ID in trade."
                    request_props.append(int(t))
            except (TypeError, ValueError):
                return False, "Invalid numeric value in trade."

            if offer_cash < 0 or request_cash < 0:
                return False, "Trade cash cannot be negative."
            offer_props = list(dict.fromkeys(offer_props))
            request_props = list(dict.fromkeys(request_props))
            if any(t not in range(40) for t in offer_props + request_props):
                return False, "Invalid property ID in trade."

            if offer_cash > st["cash"] or request_cash > self.p_state[to_id]["cash"]:
                return False, "Insufficient cash for proposed trade."

            def _prop_tradeable(tid: int, owner_id: str) -> bool:
                if self.ownership.get(tid) != owner_id or self.houses.get(tid, 0) > 0:
                    return False
                tile = BOARD_TILES[tid]
                if tile["kind"] == "prop":
                    if any(self.houses.get(x, 0) > 0 for x in COLOR_GROUPS[tile["group"]]):
                        return False
                return True

            if any(not _prop_tradeable(t, player_id) for t in offer_props):
                return False, "You can only trade unimproved properties you own."
            if any(not _prop_tradeable(t, to_id) for t in request_props):
                return False, "Partner does not own requested unimproved properties."
            self.pending_trade = {
                "from_id": player_id,
                "to_id": to_id,
                "offer_cash": offer_cash,
                "request_cash": request_cash,
                "offer_props": offer_props,
                "request_props": request_props,
            }
            tp = self.get_player(to_id)
            self.log_event(f"{player.name} proposed a trade to {tp.name if tp else to_id}.")
            return True, ""

        if action == "accept_trade":
            if self.subphase in ("auction", "resolve_debt"):
                return False, "Cannot accept trades during an auction or debt resolution."
            t = self.pending_trade
            if not t or t["to_id"] != player_id:
                return False, "No trade waiting for your approval."
            from_id = t["from_id"]
            to_id = t["to_id"]
            f_st = self.p_state.get(from_id)
            t_st = self.p_state.get(to_id)
            if not f_st or not t_st or f_st["bankrupt"] or t_st["bankrupt"]:
                self.pending_trade = None
                return False, "A trade participant is bankrupt; trade invalidated."
            if f_st["cash"] < t["offer_cash"] or t_st["cash"] < t["request_cash"]:
                self.pending_trade = None
                return False, "Cash changed; trade invalidated."

            def _still_tradeable(tid: int, owner_id: str) -> bool:
                if self.ownership.get(tid) != owner_id or self.houses.get(tid, 0) > 0:
                    return False
                tile = BOARD_TILES[tid]
                if tile["kind"] == "prop":
                    if any(self.houses.get(x, 0) > 0 for x in COLOR_GROUPS[tile["group"]]):
                        return False
                return True

            if any(not _still_tradeable(tid, from_id) for tid in t["offer_props"]) or any(
                not _still_tradeable(tid, to_id) for tid in t["request_props"]
            ):
                self.pending_trade = None
                return False, "Property ownership or houses changed; trade invalidated."

            f_st["cash"] = f_st["cash"] - t["offer_cash"] + t["request_cash"]
            t_st["cash"] = t_st["cash"] - t["request_cash"] + t["offer_cash"]
            for tid in t["offer_props"]:
                self.ownership[tid] = to_id
            for tid in t["request_props"]:
                self.ownership[tid] = from_id
            self.pending_trade = None
            self._recompute_net_worth()
            self.log_event("Trade executed!")
            return True, ""

        if action == "reject_trade":
            t = self.pending_trade
            if not t or (t["to_id"] != player_id and t["from_id"] != player_id):
                return False, "No trade to cancel/reject."
            self.pending_trade = None
            self.log_event("Trade declined.")
            return True, ""

        # Property management (allowed on own turn or during debt resolution)
        if action in ("build_house", "sell_house", "mortgage", "unmortgage"):
            if player_id != self.turn_player_id and not (
                self.subphase == "resolve_debt" and self.pending_debt and self.pending_debt["debtor_id"] == player_id
            ):
                return False, "Can only manage properties on your turn."
            raw_tid = data.get("tile_id", -1)
            if isinstance(raw_tid, bool):
                return False, "Invalid property tile."
            try:
                tid = int(raw_tid)
            except (TypeError, ValueError):
                return False, "Invalid property tile."
            if tid not in range(40) or self.ownership.get(tid) != player_id:
                return False, "You do not own this property."
            tile = BOARD_TILES[tid]

            if action == "build_house":
                if tile["kind"] != "prop":
                    return False, "Only colored properties can hold houses."
                group = tile["group"]
                if not self._has_monopoly(player_id, group):
                    return False, "Must own all unmortgaged properties in the color set."
                g_tids = COLOR_GROUPS[group]
                cur = self.houses.get(tid, 0)
                if cur >= 5:
                    return False, "Hotel already built."
                if cur > min(self.houses.get(x, 0) for x in g_tids):
                    return False, "Must build evenly across the color set."
                cost = tile["house_cost"]
                if st["cash"] < cost:
                    return False, "Insufficient cash."
                st["cash"] -= cost
                self.houses[tid] = cur + 1
                self._recompute_net_worth()
                self.log_event(f"{player.name} built on {tile['name']}.")
                return True, ""

            if action == "sell_house":
                if tile["kind"] != "prop":
                    return False, "No houses here."
                g_tids = COLOR_GROUPS[tile["group"]]
                cur = self.houses.get(tid, 0)
                if cur <= 0:
                    return False, "No houses to sell."
                if cur < max(self.houses.get(x, 0) for x in g_tids):
                    return False, "Must sell houses evenly across the color set."
                self.houses[tid] = cur - 1
                st["cash"] += tile["house_cost"] // 2
                self._recompute_net_worth()
                return True, ""

            if action == "mortgage":
                if tid in self.mortgaged:
                    return False, "Already mortgaged."
                if tile["kind"] == "prop" and any(self.houses.get(x, 0) > 0 for x in COLOR_GROUPS[tile["group"]]):
                    return False, "Sell all houses in color set before mortgaging."
                self.mortgaged.add(tid)
                st["cash"] += tile["price"] // 2
                self._recompute_net_worth()
                return True, ""

            if action == "unmortgage":
                if tid not in self.mortgaged:
                    return False, "Property is not mortgaged."
                fee = int(tile["price"] * 0.55)
                if st["cash"] < fee:
                    return False, f"Need ${fee} to unmortgage."
                st["cash"] -= fee
                self.mortgaged.remove(tid)
                self._recompute_net_worth()
                return True, ""

        # Debt resolution
        if self.subphase == "resolve_debt":
            if not self.pending_debt or self.pending_debt["debtor_id"] != player_id:
                return False, "Waiting on debt resolution."
            if action == "pay_debt":
                amt = self.pending_debt["amount"]
                if st["cash"] < amt:
                    return False, f"Still short ${amt - st['cash']}."
                cred = self.pending_debt["creditor_id"]
                post_steps = self.pending_debt.get("post_move_steps")
                st["cash"] -= amt
                if cred and cred in self.p_state:
                    self.p_state[cred]["cash"] += amt
                self.pending_debt = None
                self.log_event(f"{player.name} settled ${amt} debt.")
                if post_steps:
                    self._move_and_resolve(player_id, post_steps, post_steps)
                else:
                    self.subphase = "end_turn"
                self._recompute_net_worth()
                return True, ""
            if action == "declare_bankrupt":
                self._bankrupt_player(
                    player_id,
                    self.pending_debt["creditor_id"],
                    self.pending_debt["reason"],
                )
                return True, ""
            return False, "Liquidate assets and click Pay Debt."

        if player_id != self.turn_player_id:
            return False, "It is not your turn."

        if action in ("pay_jail", "use_goojf"):
            if self.subphase != "roll" or not st["in_jail"]:
                return False, "Not currently in Jail."
            if action == "pay_jail":
                if st["cash"] < 50:
                    return False, "Need $50 to post bail."
                st["cash"] -= 50
            else:
                if st["goojf"] <= 0:
                    return False, "No Get Out of Jail Free card."
                st["goojf"] -= 1
            st["in_jail"] = False
            st["jail_turns"] = 0
            self.log_event(f"{player.name} exited Jail.")
            self._recompute_net_worth()
            return True, ""

        if action == "roll":
            if self.subphase != "roll":
                return False, "Already rolled this turn."
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            self.last_dice = [d1, d2]
            is_doubles = d1 == d2
            total = d1 + d2
            self.log_event(f"{player.name} rolled [{d1}, {d2}].")

            if st["in_jail"]:
                if is_doubles:
                    st["in_jail"] = False
                    st["jail_turns"] = 0
                    self.log_event(f"{player.name} rolled doubles and escaped Jail!")
                    self._move_and_resolve(player_id, total, total)
                else:
                    st["jail_turns"] += 1
                    if st["jail_turns"] >= 3:
                        st["in_jail"] = False
                        st["jail_turns"] = 0
                        self.log_event(f"{player.name} forced to pay $50 bail after 3rd Jail turn.")
                        if st["cash"] >= 50:
                            st["cash"] -= 50
                            self._move_and_resolve(player_id, total, total)
                        else:
                            self._charge_player(player_id, 50, None, "Mandatory Jail Bail")
                            if (
                                self.phase == "playing"
                                and self.subphase == "resolve_debt"
                                and self.pending_debt
                            ):
                                self.pending_debt["post_move_steps"] = total
                    else:
                        self.subphase = "end_turn"
                self._recompute_net_worth()
                return True, ""

            if is_doubles:
                self.doubles_count += 1
                if self.doubles_count >= 3:
                    self.log_event(f"{player.name} rolled 3 doubles in a row!", kind="warn")
                    self._send_to_jail(player_id)
                    self._recompute_net_worth()
                    return True, ""
                self.extra_turn_pending = True
            else:
                self.extra_turn_pending = False

            self._move_and_resolve(player_id, total, total)
            self._recompute_net_worth()
            return True, ""

        if action == "buy":
            if self.subphase != "buy_or_auction":
                return False, "Nothing available to purchase."
            pos = st["pos"]
            tile = BOARD_TILES[pos]
            if self.ownership.get(pos) is not None:
                return False, "Already owned."
            if st["cash"] < tile["price"]:
                return False, "Insufficient cash — trigger Auction instead."
            st["cash"] -= tile["price"]
            self.ownership[pos] = player_id
            self.subphase = "end_turn"
            self._recompute_net_worth()
            self.log_event(f"{player.name} bought {tile['name']} for ${tile['price']}.")
            return True, ""

        if action == "pass_buy":
            if self.subphase != "buy_or_auction":
                return False, "Not in purchase phase."
            self._start_auction(st["pos"])
            return True, ""

        if action == "end_turn":
            if self.subphase != "end_turn":
                return False, "Finish current turn step before ending turn."
            self._advance_turn()
            self._recompute_net_worth()
            return True, ""

        return False, f"Unsupported action: {action}"

    def get_public_state(self) -> dict[str, Any]:
        auc_pub = None
        if self.auction:
            auc_pub = {
                "tile_id": self.auction["tile_id"],
                "tile_name": BOARD_TILES[self.auction["tile_id"]]["name"],
                "highest_bid": self.auction["highest_bid"],
                "highest_bidder": self.auction["highest_bidder"],
                "time_remaining": round(max(0.0, self.auction["ends_at"] - time.time()), 1),
                "passed": self.auction["passed"],
            }
        return {
            "phase": self.phase,
            "board": BOARD_TILES,
            "turn_player_id": self.turn_player_id,
            "subphase": self.subphase,
            "last_dice": self.last_dice,
            "last_card_text": self.last_card_text,
            "players_state": self.p_state,
            "ownership": {str(k): v for k, v in self.ownership.items()},
            "houses": {str(k): v for k, v in self.houses.items()},
            "mortgaged": sorted(self.mortgaged),
            "auction": auc_pub,
            "pending_debt": self.pending_debt,
            "pending_trade": self.pending_trade,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }
