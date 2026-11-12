"""2-4P Double-Six Dominoes engine with server-side boneyard, blocked-board scoring, and AI bot."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty


def create_double_six_set() -> list[tuple[int, int]]:
    return [(a, b) for a in range(7) for b in range(a, 7)]


class DominoesGame(BaseGame):
    GAME_TYPE = "dominoes"
    TITLE = "DOMINOES CHAIN"
    CATEGORY = "Tabletop"
    DESCRIPTION = (
        "2-4 player Double-Six Dominoes with hidden server boneyard, spinner doubles, and multi-round pip scoring."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 4
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"target_score": 100, "difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.hands: dict[str, list[tuple[int, int]]] = {}
        self.boneyard: list[tuple[int, int]] = []
        self.chain: list[tuple[int, int]] = []
        self.left_end: int | None = None
        self.right_end: int | None = None
        self.turn_idx: int = 0
        self.consecutive_passes: int = 0
        self.round_number: int = 1
        self.target_score: int = 100

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )
        raw_ts = self.settings.get("target_score", 100)
        if isinstance(raw_ts, bool) or raw_ts is None:
            ts = 100
        else:
            try:
                ts = int(raw_ts)
            except (TypeError, ValueError):
                ts = 100
        self.target_score = max(25, min(500, ts))
        self.settings["target_score"] = self.target_score
        self.round_number = 1
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        for p in self.players:
            p.score = 0
        self._deal_round()

    def _deal_round(self) -> None:
        deck = create_double_six_set()
        random.shuffle(deck)
        self.hands = {}
        for p in self.players:
            self.hands[p.id] = [deck.pop() for _ in range(7)]
        self.boneyard = deck
        self.chain = []
        self.left_end = None
        self.right_end = None
        self.consecutive_passes = 0

        # Player holding highest double (or highest pip sum tile) starts
        best_idx = 0
        best_rank = (-1, -1)
        for idx, p in enumerate(self.players):
            for a, b in self.hands[p.id]:
                rank = (1, a) if a == b else (0, a + b)
                if rank > best_rank:
                    best_rank = rank
                    best_idx = idx
        self.turn_idx = best_idx
        self.turn_player_id = self.players[best_idx].id
        self.log_event(
            f"Round {self.round_number} dealt. {self.players[best_idx].name} leads."
        )

    def _playable_tiles(self, hand: list[tuple[int, int]]) -> list[tuple[tuple[int, int], list[str]]]:
        if not self.chain:
            return [(t, ["left"]) for t in hand]
        playable: list[tuple[tuple[int, int], list[str]]] = []
        for t in hand:
            sides: list[str] = []
            if self.left_end in t:
                sides.append("left")
            if self.right_end in t and self.right_end != self.left_end:
                sides.append("right")
            if sides:
                playable.append((t, sides))
        return playable

    def _advance_turn(self) -> None:
        self.turn_idx = (self.turn_idx + 1) % len(self.players)
        self.turn_player_id = self.players[self.turn_idx].id

    def _resolve_round_end(self, winner: PlayerSlot | None, reason: str) -> None:
        if winner:
            pts = sum(
                sum(a + b for a, b in self.hands[p.id])
                for p in self.players
                if p.id != winner.id
            )
            winner.score += pts
            self.log_event(f"{reason} {winner.name} scores +{pts} pips (Total: {winner.score}).", kind="finish")
            if winner.score >= self.target_score:
                self.finish_game(
                    [winner.id],
                    f"{winner.name} reached {winner.score} points and won the Dominoes match!",
                )
                return
        else:
            self.log_event(f"{reason} Tied pip counts — 0 points awarded.", kind="warn")

        self.round_number += 1
        self._deal_round()

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        if player_id != self.turn_player_id:
            return False, "It is not your turn."

        hand = self.hands[player_id]
        player = self.get_player(player_id)

        if action == "play":
            raw_tile = data.get("tile")
            if not isinstance(raw_tile, (list, tuple)) or len(raw_tile) != 2:
                return False, "Invalid tile format."
            if isinstance(raw_tile[0], bool) or isinstance(raw_tile[1], bool):
                return False, "Invalid tile values."
            try:
                tile = (int(raw_tile[0]), int(raw_tile[1]))
            except (TypeError, ValueError):
                return False, "Invalid tile values."
            if tile not in hand:
                rev = (tile[1], tile[0])
                if rev in hand:
                    tile = rev
                else:
                    return False, "Tile not in your hand."

            side = str(data.get("side", "right")).lower()
            if not self.chain:
                hand.remove(tile)
                self.chain.append(tile)
                self.left_end = tile[0]
                self.right_end = tile[1]
            else:
                if side == "left":
                    if self.left_end not in tile:
                        return False, "Tile does not match left chain end."
                    oriented = (tile[0], tile[1]) if tile[1] == self.left_end else (tile[1], tile[0])
                    hand.remove(tile)
                    self.chain.insert(0, oriented)
                    self.left_end = oriented[0]
                elif side == "right":
                    if self.right_end not in tile:
                        return False, "Tile does not match right chain end."
                    oriented = (tile[0], tile[1]) if tile[0] == self.right_end else (tile[1], tile[0])
                    hand.remove(tile)
                    self.chain.append(oriented)
                    self.right_end = oriented[1]
                else:
                    return False, "Side must be 'left' or 'right'."

            self.consecutive_passes = 0
            if not hand:
                self._resolve_round_end(player, f"{player.name if player else player_id} dominoed!")
                return True, ""
            self._advance_turn()
            return True, ""

        if action == "draw":
            if self._playable_tiles(hand):
                return False, "You already have a playable tile."
            if not self.boneyard:
                return False, "Boneyard is empty — you must pass."
            drawn = self.boneyard.pop()
            hand.append(drawn)
            if player:
                self.log_event(f"{player.name} drew from the boneyard.")
            return True, ""

        if action == "pass":
            if self._playable_tiles(hand):
                return False, "You have a playable tile."
            if self.boneyard:
                return False, "Draw from the boneyard before passing."
            self.consecutive_passes += 1
            if player:
                self.log_event(f"{player.name} passed.", kind="warn")
            if self.consecutive_passes >= len(self.players):
                pip_totals = {
                    p.id: sum(a + b for a, b in self.hands[p.id]) for p in self.players
                }
                min_pips = min(pip_totals.values())
                leaders = [p for p in self.players if pip_totals[p.id] == min_pips]
                winner = leaders[0] if len(leaders) == 1 else None
                self._resolve_round_end(winner, f"Board blocked (lowest pips: {min_pips})!")
                return True, ""
            self._advance_turn()
            return True, ""

        return False, f"Unsupported action: {action}"

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.turn_player_id != bot_id:
            return None
        hand = self.hands[bot_id]
        playable = self._playable_tiles(hand)
        if playable:
            diff = self.get_difficulty()
            if diff == "easy":
                tile, sides = random.choice(playable)
                return "play", {"tile": list(tile), "side": random.choice(sides)}
            if diff == "hard":
                # Count suit frequencies in own remaining hand to maintain flexibility & shed high pips cleanly
                suit_counts = {n: 0 for n in range(7)}
                for a, b in hand:
                    suit_counts[a] += 1
                    if b != a:
                        suit_counts[b] += 1

                def eval_play(tile_item: tuple[tuple[int, int], list[str]]) -> tuple[float, str]:
                    t, side_opts = tile_item
                    rem_counts = dict(suit_counts)
                    rem_counts[t[0]] = max(0, rem_counts[t[0]] - 1)
                    if t[1] != t[0]:
                        rem_counts[t[1]] = max(0, rem_counts[t[1]] - 1)
                    double_bonus = 6.0 if t[0] == t[1] else 0.0
                    if not self.chain:
                        # Opening lead exposes both ends (t[0] and t[1])
                        flex = (
                            rem_counts.get(t[0], 0)
                            + (rem_counts.get(t[1], 0) if t[1] != t[0] else 0)
                        ) * 6.0
                        sc = (t[0] + t[1]) * 1.4 + flex + double_bonus
                        return sc, side_opts[0]
                    best_side = side_opts[0]
                    best_sc = -10**6
                    for s in side_opts:
                        new_end = (
                            t[1]
                            if t[0] == (self.left_end if s == "left" else self.right_end)
                            else t[0]
                        )
                        flex = rem_counts.get(new_end, 0) * 6.0
                        sc = (t[0] + t[1]) * 1.4 + flex + double_bonus
                        if sc > best_sc:
                            best_sc = sc
                            best_side = s
                    return best_sc, best_side

                chosen_tile, chosen_side = max(
                    ((item[0], eval_play(item)) for item in playable),
                    key=lambda x: x[1][0],
                )
                return "play", {"tile": list(chosen_tile), "side": chosen_side[1]}

            tile, sides = max(playable, key=lambda item: item[0][0] + item[0][1])
            return "play", {"tile": list(tile), "side": sides[0]}
        if self.boneyard:
            return "draw", {}
        return "pass", {}

    def get_public_state(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "round_number": self.round_number,
            "target_score": self.target_score,
            "turn_player_id": self.turn_player_id,
            "chain": [list(t) for t in self.chain],
            "left_end": self.left_end,
            "right_end": self.right_end,
            "boneyard_count": len(self.boneyard),
            "hand_counts": {pid: len(h) for pid, h in self.hands.items()},
            "consecutive_passes": self.consecutive_passes,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

    def get_private_state(self, player_id: str) -> dict[str, Any]:
        hand = self.hands.get(player_id, [])
        playable = self._playable_tiles(hand) if player_id == self.turn_player_id else []
        return {
            "hand": [list(t) for t in hand],
            "playable": [
                {"tile": list(t), "sides": sides} for t, sides in playable
            ],
        }

