"""2-4P Ludo engine with 52-square outer track, safe stars, 3-six forfeit, captures, and AI bot."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

COLOR_NAMES = ["RED", "GREEN", "YELLOW", "BLUE"]

# Continuous 52-square clockwise outer track (r, c) on a 15x15 grid
OUTER_TRACK: list[tuple[int, int]] = [
    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
    (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6),
    (0, 7),
    (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8),
    (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14),
    (7, 14),
    (8, 14), (8, 13), (8, 12), (8, 11), (8, 10), (8, 9),
    (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8),
    (14, 7),
    (14, 6), (13, 6), (12, 6), (11, 6), (10, 6), (9, 6),
    (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (8, 0),
    (7, 0), (6, 0),
]

SAFE_TRACK_INDICES = {0, 8, 13, 21, 26, 34, 39, 47}

HOME_LANES: dict[int, list[tuple[int, int]]] = {
    0: [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)],
    1: [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)],
    2: [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)],
    3: [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)],
}

YARD_COORDS: dict[int, list[tuple[int, int]]] = {
    0: [(2, 2), (2, 3), (3, 2), (3, 3)],
    1: [(2, 11), (2, 12), (3, 11), (3, 12)],
    2: [(11, 11), (11, 12), (12, 11), (12, 12)],
    3: [(11, 2), (11, 3), (12, 2), (12, 3)],
}


class LudoGame(BaseGame):
    GAME_TYPE = "ludo"
    TITLE = "LUDO BUNKER RACE"
    CATEGORY = "Tabletop"
    DESCRIPTION = (
        "2-4 player 15x15 Ludo. Roll 6 to deploy, capture rival tokens, use starred safe squares, and beware triple 6s."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 4
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
        self.seat_colors: dict[str, int] = {}
        self.tokens: dict[str, list[int]] = {}  # -1 = yard, 0..50 = track, 51..55 = home lane, 56 = finish
        self.turn_idx: int = 0
        self.subphase: str = "roll"  # roll | move
        self.dice_value: int | None = None
        self.last_dice: int | None = None
        self.consecutive_sixes: int = 0
        self.last_hop_path: list[list[int]] = []

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )
        color_layout = [0, 2] if len(self.players) == 2 else list(range(len(self.players)))
        self.seat_colors = {}
        self.tokens = {}
        for idx, p in enumerate(self.players):
            p.score = 0
            self.seat_colors[p.id] = color_layout[idx]
            self.tokens[p.id] = [-1, -1, -1, -1]
        self.turn_idx = 0
        self.turn_player_id = self.players[0].id
        self.subphase = "roll"
        self.dice_value = None
        self.last_dice = None
        self.consecutive_sixes = 0
        self.last_hop_path = []
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        self.log_event("Ludo race launched!")

    def _track_index(self, player_id: str, rel_pos: int) -> int | None:
        if 0 <= rel_pos <= 50:
            c_idx = self.seat_colors[player_id]
            return (c_idx * 13 + rel_pos) % 52
        return None

    def _coord_for(self, player_id: str, token_idx: int, rel_pos: int) -> tuple[int, int]:
        c_idx = self.seat_colors[player_id]
        if rel_pos == -1:
            return YARD_COORDS[c_idx][token_idx]
        if 0 <= rel_pos <= 50:
            return OUTER_TRACK[self._track_index(player_id, rel_pos)]
        return HOME_LANES[c_idx][min(5, rel_pos - 51)]

    def _movable_tokens(self, player_id: str, die: int) -> list[int]:
        movable: list[int] = []
        for idx, pos in enumerate(self.tokens[player_id]):
            if pos == -1:
                if die == 6:
                    movable.append(idx)
            elif pos < 56 and pos + die <= 56:
                movable.append(idx)
        return movable

    def _advance_turn(self) -> None:
        self.turn_idx = (self.turn_idx + 1) % len(self.players)
        self.turn_player_id = self.players[self.turn_idx].id
        self.subphase = "roll"
        self.dice_value = None
        self.consecutive_sixes = 0

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        if player_id != self.turn_player_id:
            return False, "It is not your turn."

        player = self.get_player(player_id)

        if action == "roll":
            if self.subphase != "roll":
                return False, "Already rolled."
            die = random.randint(1, 6)
            self.dice_value = die
            self.last_dice = die
            self.last_hop_path = []

            if die == 6:
                self.consecutive_sixes += 1
                if self.consecutive_sixes >= 3:
                    self.log_event(
                        f"{player.name} rolled three consecutive 6s — turn forfeited!",
                        kind="warn",
                    )
                    self._advance_turn()
                    return True, ""
            else:
                self.consecutive_sixes = 0

            movable = self._movable_tokens(player_id, die)
            if not movable:
                self.log_event(f"{player.name} rolled {die} — no movable tokens.")
                self._advance_turn()
                return True, ""

            self.subphase = "move"
            self.log_event(f"{player.name} rolled {die}.")
            return True, ""

        if action == "move":
            if self.subphase != "move" or self.dice_value is None:
                return False, "Roll the die first."
            try:
                t_idx = int(data.get("token", -1))
            except (TypeError, ValueError):
                return False, "Invalid token index."
            movable = self._movable_tokens(player_id, self.dice_value)
            if t_idx not in movable:
                return False, "Token cannot legally move with this roll."

            old_pos = self.tokens[player_id][t_idx]
            new_pos = 0 if old_pos == -1 else old_pos + self.dice_value

            # Record animated path steps
            if old_pos == -1:
                self.last_hop_path = [list(self._coord_for(player_id, t_idx, 0))]
            else:
                self.last_hop_path = [
                    list(self._coord_for(player_id, t_idx, p))
                    for p in range(old_pos + 1, new_pos + 1)
                ]

            self.tokens[player_id][t_idx] = new_pos
            captured = False
            reached_home = new_pos == 56

            dest_track = self._track_index(player_id, new_pos)
            if dest_track is not None and dest_track not in SAFE_TRACK_INDICES:
                for opp in self.players:
                    if opp.id == player_id:
                        continue
                    for o_idx, o_pos in enumerate(self.tokens[opp.id]):
                        if self._track_index(opp.id, o_pos) == dest_track:
                            self.tokens[opp.id][o_idx] = -1
                            captured = True
                            self.log_event(
                                f"{player.name} captured {opp.name}'s token!",
                                kind="warn",
                            )

            if player:
                player.score = sum(1 for p in self.tokens[player_id] if p == 56)

            if all(p == 56 for p in self.tokens[player_id]):
                self.finish_game(
                    [player_id],
                    f"{player.name} brought all 4 tokens home and won Ludo!",
                )
                return True, ""

            if self.dice_value == 6 or captured or reached_home:
                self.subphase = "roll"
                if captured or reached_home:
                    self.consecutive_sixes = 0
            else:
                self._advance_turn()
            return True, ""

        return False, f"Unsupported action: {action}"

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.turn_player_id != bot_id:
            return None
        if self.subphase == "roll":
            return "roll", {}
        if self.dice_value is None:
            return None
        movable = self._movable_tokens(bot_id, self.dice_value)
        if not movable:
            return None

        diff = self.get_difficulty()
        if diff == "easy" and len(movable) > 1 and random.random() < 0.45:
            return "move", {"token": random.choice(movable)}

        def eval_token(idx: int) -> float:
            pos = self.tokens[bot_id][idx]
            nxt = 0 if pos == -1 else pos + self.dice_value
            sc = float(nxt)
            if pos == -1:
                sc += 65.0
            if nxt == 56:
                sc += 100.0
            dest_track = self._track_index(bot_id, nxt)
            if dest_track is not None:
                if dest_track in SAFE_TRACK_INDICES:
                    sc += 35.0 if diff == "hard" else 25.0
                else:
                    for opp in self.players:
                        if opp.id == bot_id:
                            continue
                        for op in self.tokens[opp.id]:
                            opp_track = self._track_index(opp.id, op)
                            if opp_track is None:
                                continue
                            if opp_track == dest_track:
                                sc += 95.0 if diff == "hard" else 90.0
                            elif diff == "hard" and 1 <= ((dest_track - opp_track) % 52) <= 6:
                                # Penalize stopping within 1-6 steps ahead of an opponent token
                                sc -= 32.0
            elif diff == "hard" and nxt >= 51:
                # Safe home stretch away from capture risk
                sc += 30.0
            return sc

        best = max(movable, key=eval_token)
        return "move", {"token": best}

    def get_public_state(self) -> dict[str, Any]:
        movable = (
            self._movable_tokens(self.turn_player_id, self.dice_value)
            if self.phase == "playing" and self.subphase == "move" and self.dice_value
            else []
        )
        token_coords: dict[str, list[dict[str, Any]]] = {}
        for p in self.players:
            if p.id not in self.tokens or p.id not in self.seat_colors:
                token_coords[p.id] = []
                continue
            token_coords[p.id] = [
                {
                    "rel": pos,
                    "coord": list(self._coord_for(p.id, idx, pos)),
                }
                for idx, pos in enumerate(self.tokens[p.id])
            ]
        return {
            "phase": self.phase,
            "turn_player_id": self.turn_player_id,
            "subphase": self.subphase,
            "dice_value": self.dice_value,
            "last_dice": self.last_dice,
            "consecutive_sixes": self.consecutive_sixes,
            "seat_colors": self.seat_colors,
            "tokens": token_coords,
            "movable_tokens": movable,
            "last_hop_path": self.last_hop_path,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }
