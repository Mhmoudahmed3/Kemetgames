"""Server-authoritative Tawla / Backgammon engine with full legal move tree validation and AI bot."""

from __future__ import annotations

import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty


VALID_BACKGAMMON_MODES: tuple[str, ...] = ("classic", "tawla_31", "mahbosa")


def normalize_backgammon_mode(raw: Any) -> str:
    mode = str(raw or "classic").strip().lower()
    return mode if mode in VALID_BACKGAMMON_MODES else "classic"


def initial_points(mode: str = "classic") -> list[int]:
    pts = [0] * 24
    if mode in ("tawla_31", "mahbosa"):
        # In both Tawla 31 and Mahbosa, all 15 checkers start on the opponent's 1-point:
        # Player 0 (White) starts all 15 on point 23 (moves 23 -> 0)
        # Player 1 (Black) starts all 15 on point 0 (moves 0 -> 23)
        pts[23] = 15
        pts[0] = -15
        return pts
    # Classic Backgammon / Franjieh
    pts[23] = 2
    pts[12] = 5
    pts[7] = 3
    pts[5] = 5
    pts[0] = -2
    pts[11] = -5
    pts[16] = -3
    pts[18] = -5
    return pts


class BackgammonGame(BaseGame):
    GAME_TYPE = "backgammon"
    TITLE = "TAWLA / BACKGAMMON"
    CATEGORY = "Strategy"
    DESCRIPTION = (
        "24-point Backgammon with server-rolled 2d6 dice, doubles x4, Bar hitting & re-entry, and bearing-off rules."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 2
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    DEFAULT_SETTINGS = {"difficulty": "mid", "mode": "classic"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.mode: str = normalize_backgammon_mode(self.settings.get("mode", "classic"))
        self.settings["mode"] = self.mode
        self.points: list[int] = initial_points(self.mode)
        self.pinned: list[int] = [0] * 24
        self.bar: dict[int, int] = {0: 0, 1: 0}
        self.off: dict[int, int] = {0: 0, 1: 0}
        self.turn_idx: int = 0
        self.subphase: str = "roll"  # roll | move
        self.dice: list[int] = []
        self.last_dice: list[int] = []
        self.remaining_dice: list[int] = []
        self.last_roll_note: str = ""

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )
        self.mode = normalize_backgammon_mode(self.settings.get("mode", "classic"))
        self.settings["mode"] = self.mode
        self.points = initial_points(self.mode)
        self.pinned = [0] * 24
        self.bar = {0: 0, 1: 0}
        self.off = {0: 0, 1: 0}
        self.turn_idx = 0
        self.subphase = "roll"
        self.dice = []
        self.last_dice = []
        self.remaining_dice = []
        self.last_roll_note = ""
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        for p in self.players:
            p.score = 0
        self.turn_player_id = self.players[0].id
        mode_label = (
            "Tawla 31"
            if self.mode == "tawla_31"
            else "Mahbosa"
            if self.mode == "mahbosa"
            else "Classic Backgammon"
        )
        self.log_event(
            f"{mode_label} started: {self.players[0].name} (Cream) vs {self.players[1].name} (Red)."
        )

    @staticmethod
    def _can_bear_off(
        points: list[int],
        bar: dict[int, int],
        p_idx: int,
        pinned: list[int] | None = None,
        mode: str = "classic",
    ) -> bool:
        if mode == "classic" and bar[p_idx] > 0:
            return False
        if mode == "mahbosa" and pinned:
            # Cannot bear off if any of your checkers are pinned/jailed anywhere
            target_pin = 1 if p_idx == 0 else -1
            if any(p == target_pin for p in pinned):
                return False
        if p_idx == 0:
            # All White checkers must be on points 0..5
            return all(points[i] <= 0 for i in range(6, 24))
        return all(points[i] >= 0 for i in range(0, 18))

    @staticmethod
    def _highest_home_point(points: list[int], p_idx: int) -> int | None:
        if p_idx == 0:
            for i in range(5, -1, -1):
                if points[i] > 0:
                    return i
        else:
            for i in range(18, 24):
                if points[i] < 0:
                    return i
        return None

    def _single_die_moves(
        self,
        points: list[int],
        bar: dict[int, int],
        p_idx: int,
        die: int,
        pinned: list[int] | None = None,
        mode: str = "classic",
    ) -> list[dict[str, Any]]:
        moves: list[dict[str, Any]] = []
        sign = 1 if p_idx == 0 else -1
        cur_pinned = pinned or [0] * 24

        def can_land(dest: int) -> bool:
            val = points[dest]
            if mode == "tawla_31":
                # In 31, single checker holds the point; no hitting allowed
                if p_idx == 0:
                    return val >= 0
                return val <= 0
            elif mode == "mahbosa":
                # In Mahbosa, empty or own checkers are legal.
                # If opponent has a single lone checker (val == -1 for P0, val == 1 for P1) AND no pin exists there,
                # you can land and pin it!
                if p_idx == 0:
                    if val >= 0:
                        return True
                    return val == -1 and cur_pinned[dest] == 0
                else:
                    if val <= 0:
                        return True
                    return val == 1 and cur_pinned[dest] == 0
            else:
                # Classic Backgammon / Franjieh
                if p_idx == 0:
                    return val >= -1
                return val <= 1

        if mode == "classic" and bar[p_idx] > 0:
            dest = (24 - die) if p_idx == 0 else (die - 1)
            if 0 <= dest < 24 and can_land(dest):
                moves.append({"from": "bar", "to": dest, "die": die})
            return moves

        can_off = self._can_bear_off(points, bar, p_idx, cur_pinned, mode)
        highest = self._highest_home_point(points, p_idx) if can_off else None

        for idx in range(24):
            has_checker = points[idx] > 0 if p_idx == 0 else points[idx] < 0
            if not has_checker:
                continue
            dest = idx - die if p_idx == 0 else idx + die
            if 0 <= dest < 24:
                if can_land(dest):
                    moves.append({"from": idx, "to": dest, "die": die})
            elif can_off:
                exact = (dest == -1) if p_idx == 0 else (dest == 24)
                over_valid = (
                    (dest < -1 and idx == highest)
                    if p_idx == 0
                    else (dest > 24 and idx == highest)
                )
                if exact or over_valid:
                    moves.append({"from": idx, "to": "off", "die": die})
        return moves

    @staticmethod
    def _apply_step(
        points: list[int],
        bar: dict[int, int],
        off: dict[int, int],
        p_idx: int,
        move: dict[str, Any],
        pinned: list[int] | None = None,
        mode: str = "classic",
    ) -> tuple[list[int], dict[int, int], dict[int, int], list[int], bool]:
        np = list(points)
        nbar = dict(bar)
        noff = dict(off)
        npinned = list(pinned) if pinned else [0] * 24
        opp = 1 - p_idx
        sign = 1 if p_idx == 0 else -1
        hit = False

        src = move["from"]
        if src == "bar":
            nbar[p_idx] -= 1
        else:
            s = int(src)
            np[s] -= sign
            # In Mahbosa: if the last pinning checker moves away, the pinned checker is liberated!
            if mode == "mahbosa" and np[s] == 0 and npinned[s] != 0:
                freed = npinned[s]
                npinned[s] = 0
                np[s] = freed

        dst = move["to"]
        if dst == "off":
            noff[p_idx] += 1
        else:
            d = int(dst)
            if mode == "mahbosa":
                if p_idx == 0 and np[d] == -1 and npinned[d] == 0:
                    # White lands on lone Black checker: PIN IT!
                    npinned[d] = -1
                    np[d] = 1
                    hit = True
                elif p_idx == 1 and np[d] == 1 and npinned[d] == 0:
                    # Black lands on lone White checker: PIN IT!
                    npinned[d] = 1
                    np[d] = -1
                    hit = True
                else:
                    np[d] += sign
            elif mode == "tawla_31":
                np[d] += sign
            else:
                if (p_idx == 0 and np[d] == -1) or (p_idx == 1 and np[d] == 1):
                    np[d] = 0
                    nbar[opp] += 1
                    hit = True
                np[d] += sign

        return np, nbar, noff, npinned, hit

    def _max_dice_usage(
        self,
        points: list[int],
        bar: dict[int, int],
        off: dict[int, int],
        p_idx: int,
        rem_dice: list[int],
        pinned: list[int] | None = None,
        mode: str = "classic",
    ) -> int:
        if not rem_dice or off[p_idx] >= 15:
            return 0
        best = 0
        cur_pinned = pinned or [0] * 24
        for die in set(rem_dice):
            steps = self._single_die_moves(points, bar, p_idx, die, cur_pinned, mode)
            if not steps:
                continue
            next_dice = list(rem_dice)
            next_dice.remove(die)
            for st in steps:
                np, nbar, noff, npinned, _ = self._apply_step(
                    points, bar, off, p_idx, st, cur_pinned, mode
                )
                used = 1 + self._max_dice_usage(np, nbar, noff, p_idx, next_dice, npinned, mode)
                if used > best:
                    best = used
                    if best == len(rem_dice):
                        return best
        return best

    def _legal_first_moves(self) -> list[dict[str, Any]]:
        if self.phase != "playing" or self.subphase != "move" or not self.remaining_dice:
            return []
        max_use = self._max_dice_usage(
            self.points, self.bar, self.off, self.turn_idx, self.remaining_dice, self.pinned, self.mode
        )
        if max_use == 0:
            return []

        candidates: list[dict[str, Any]] = []
        for die in sorted(set(self.remaining_dice), reverse=True):
            steps = self._single_die_moves(
                self.points, self.bar, self.turn_idx, die, self.pinned, self.mode
            )
            next_dice = list(self.remaining_dice)
            next_dice.remove(die)
            for st in steps:
                np, nbar, noff, npinned, _ = self._apply_step(
                    self.points, self.bar, self.off, self.turn_idx, st, self.pinned, self.mode
                )
                if (
                    1 + self._max_dice_usage(np, nbar, noff, self.turn_idx, next_dice, npinned, self.mode)
                    == max_use
                ):
                    candidates.append(st)

        # If max_use == 1 with two distinct remaining dice and both are playable individually, must use larger die
        if max_use == 1 and len(set(self.remaining_dice)) > 1:
            max_die = max(m["die"] for m in candidates)
            candidates = [m for m in candidates if m["die"] == max_die]

        return candidates

    def _has_any_possible_move(self, p_idx: int) -> bool:
        for die in range(1, 7):
            if self._single_die_moves(
                self.points, self.bar, p_idx, die, self.pinned, self.mode
            ):
                return True
        return False

    def _check_mahbosa_deadlock(self) -> bool:
        if self.mode != "mahbosa" or self.phase != "playing":
            return False
        if self._has_any_possible_move(0) or self._has_any_possible_move(1):
            return False
        pip0 = sum((i + 1) * max(0, self.points[i]) for i in range(24)) + sum(
            (i + 1) for i in range(24) if self.pinned[i] == 1
        )
        pip1 = sum((24 - i) * max(0, -self.points[i]) for i in range(24)) + sum(
            (24 - i) for i in range(24) if self.pinned[i] == -1
        )
        if self.off[0] > self.off[1] or (self.off[0] == self.off[1] and pip0 < pip1):
            w = self.players[0]
            self.finish_game(
                [w.id],
                f"Mutual Mahbosa pin deadlock — {w.name} wins on pip count ({pip0} vs {pip1})!",
            )
        elif self.off[1] > self.off[0] or (self.off[0] == self.off[1] and pip1 < pip0):
            w = self.players[1]
            self.finish_game(
                [w.id],
                f"Mutual Mahbosa pin deadlock — {w.name} wins on pip count ({pip1} vs {pip0})!",
            )
        else:
            self.finish_game([], f"Mutual Mahbosa pin deadlock — match drawn ({pip0} pips each)!")
        return True

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        if self.phase not in ("pre_game", "playing"):
            return False
        leaver = self.get_player(player_id)
        rival = next((p for p in self.players if p.id != player_id), None)
        if not leaver or not rival:
            return False
        rival.score = max(15, rival.score)
        msg = reason or f"{leaver.name} forfeited. {rival.name} wins!"
        self.finish_game([rival.id], msg)
        return True

    def _advance_turn(self) -> None:
        self.turn_idx = 1 - self.turn_idx
        self.turn_player_id = self.players[self.turn_idx].id
        self.subphase = "roll"
        self.dice = []
        self.remaining_dice = []

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        if player_id != self.turn_player_id:
            return False, "It is not your turn."

        if action == "roll":
            if self.subphase != "roll":
                return False, "Dice already rolled this turn."
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            self.dice = [d1, d2]
            self.last_dice = [d1, d2]
            self.remaining_dice = [d1] * 4 if d1 == d2 else [d1, d2]
            self.subphase = "move"
            player = self.players[self.turn_idx]
            legal = self._legal_first_moves()
            if not legal:
                self.last_roll_note = f"{player.name} rolled [{d1}, {d2}] — no legal moves!"
                self.log_event(self.last_roll_note, kind="warn")
                if not self._check_mahbosa_deadlock():
                    self._advance_turn()
            else:
                self.last_roll_note = f"{player.name} rolled [{d1}, {d2}]."
                self.log_event(self.last_roll_note)
            return True, ""

        if action == "move":
            if self.subphase != "move":
                return False, "Roll the dice first."
            src = data.get("from")
            dst = data.get("to")
            if src != "bar":
                if isinstance(src, bool):
                    return False, "Invalid source point."
                try:
                    src = int(src)
                except (TypeError, ValueError):
                    return False, "Invalid source point."
            if dst != "off":
                if isinstance(dst, bool):
                    return False, "Invalid target point."
                try:
                    dst = int(dst)
                except (TypeError, ValueError):
                    return False, "Invalid target point."

            legal = self._legal_first_moves()
            matches = [m for m in legal if m["from"] == src and m["to"] == dst]
            if not matches:
                return False, "Illegal Backgammon move."
            req_die = data.get("die")
            if req_die is not None:
                if isinstance(req_die, bool):
                    return False, "Invalid die value."
                try:
                    req_die_int = int(req_die)
                except (TypeError, ValueError):
                    return False, "Invalid die value."
                die_matches = [m for m in matches if m["die"] == req_die_int]
                if not die_matches:
                    return False, "Requested die cannot perform that move."
                chosen = die_matches[0]
            else:
                chosen = matches[0]
            self.points, self.bar, self.off, self.pinned, hit = self._apply_step(
                self.points, self.bar, self.off, self.turn_idx, chosen, self.pinned, self.mode
            )
            self.remaining_dice.remove(chosen["die"])

            player = self.players[self.turn_idx]
            player.score = self.off[self.turn_idx]
            if hit:
                if self.mode == "mahbosa":
                    self.log_event(f"{player.name} pinned an opponent checker in jail!", kind="warn")
                else:
                    self.log_event(f"{player.name} hit an opponent blot to the Bar!", kind="warn")

            if self.off[self.turn_idx] >= 15:
                self.finish_game(
                    [player.id],
                    f"{player.name} bore off all 15 checkers and won!",
                )
                return True, ""

            if not self.remaining_dice or not self._legal_first_moves():
                if self.remaining_dice:
                    self.log_event(f"{player.name} has no remaining legal moves.", kind="info")
                if not self._check_mahbosa_deadlock():
                    self._advance_turn()
            return True, ""

        return False, f"Unsupported action: {action}"

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.turn_player_id != bot_id:
            return None
        if self.subphase == "roll":
            return "roll", {}
        legal = self._legal_first_moves()
        if not legal:
            return None

        p_idx = self.turn_idx
        sign = 1 if p_idx == 0 else -1
        diff = self.get_difficulty()

        if diff == "easy" and len(legal) > 1 and random.random() < 0.45:
            pick = random.choice(legal)
            return "move", {"from": pick["from"], "to": pick["to"], "die": pick["die"]}

        def score_move(mv: dict[str, Any]) -> float:
            np, _, noff, npinned, hit = self._apply_step(
                self.points, self.bar, self.off, p_idx, mv, self.pinned, self.mode
            )
            sc = 0.0
            hit_w = 55.0 if diff == "hard" else 35.0
            off_w = 60.0 if diff == "hard" else 45.0
            make_w = 28.0 if diff == "hard" else 18.0
            blot_pen = 24.0 if diff == "hard" else 14.0
            if hit:
                sc += hit_w
            if mv["to"] == "off":
                sc += off_w
            else:
                d = int(mv["to"])
                if np[d] * sign >= 2:
                    sc += make_w
                    if diff == "hard":
                        if (d > 0 and np[d - 1] * sign >= 2) or (d < 23 and np[d + 1] * sign >= 2):
                            sc += 10.0
                if np[d] * sign == 1:
                    sc -= blot_pen
            if mv["from"] != "bar":
                s = int(mv["from"])
                if np[s] * sign == 1:
                    sc -= (20.0 if diff == "hard" else 12.0)
            pip_sum = sum(
                (i + 1 if p_idx == 0 else 24 - i) * abs(np[i])
                for i in range(24)
                if (np[i] > 0 if p_idx == 0 else np[i] < 0)
            )
            return sc - pip_sum * 0.25 + noff[p_idx] * 10

        best = max(legal, key=score_move)
        return "move", {"from": best["from"], "to": best["to"], "die": best["die"]}

    def get_public_state(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "mode": self.mode,
            "points": self.points,
            "pinned": self.pinned,
            "bar": {str(k): v for k, v in self.bar.items()},
            "off": {str(k): v for k, v in self.off.items()},
            "turn_idx": self.turn_idx,
            "turn_player_id": self.turn_player_id,
            "subphase": self.subphase,
            "dice": self.dice,
            "last_dice": self.last_dice,
            "remaining_dice": self.remaining_dice,
            "last_roll_note": self.last_roll_note,
            "legal_moves": self._legal_first_moves(),
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

