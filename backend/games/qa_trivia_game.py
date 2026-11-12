"""Unified QA game engine merging World Atlas (197 nations) and Curated IQ & Trivia with selectable categories."""

from __future__ import annotations

import json
import math
from pathlib import Path
import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty
from backend.data.country_store import COUNTRIES_BANK, get_sanitized_flag_data_uri

ATLAS_MODES = ["flag", "capital", "borders", "mystery", "population_area", "characteristics"]

QA_CATEGORIES = [
    "All",
    "Atlas",
    "Flags",
    "War",
    "History",
    "Science",
    "Logic & Pattern IQ",
    "General Knowledge",
    "Tech & Pop Culture",
]

# (standard_seconds, mystery_seconds)
QA_DURATIONS: dict[str, tuple[float, float]] = {
    "easy": (20.0, 24.0),
    "mid": (15.0, 18.0),
    "hard": (10.0, 12.0),
}

QUESTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_questions.json"
with QUESTIONS_PATH.open("r", encoding="utf-8") as _fh:
    QUESTION_BANK: list[dict[str, Any]] = json.load(_fh)


def normalize_qa_category(raw: Any) -> str:
    """Normalize user or legacy category settings onto canonical QA_CATEGORIES."""
    text = str(raw or "").strip()
    if not text:
        return "All"
    low = text.lower()
    if low in ("countries", "atlas", "atlas qa", "geography", "world atlas"):
        return "Atlas"
    if low in ("flag", "flags"):
        return "Flags"
    if low in ("war", "wars", "military", "battles", "warfare"):
        return "War"
    if low in ("logic", "logic iq", "pattern", "iq", "logic & pattern iq"):
        return "Logic & Pattern IQ"
    if low in ("tech", "technology", "tech & pop culture", "pop culture"):
        return "Tech & Pop Culture"
    if low in ("general", "general knowledge"):
        return "General Knowledge"
    if low in ("history", "historical"):
        return "History"
    if low in ("science", "sci"):
        return "Science"
    for cat in QA_CATEGORIES:
        if cat.lower() == low:
            return cat
    return "All"


def _pick_distractors(
    target: dict[str, Any],
    pool: list[dict[str, Any]],
    field: str,
    difficulty: str,
) -> list[str]:
    if difficulty == "hard":
        same_cont = [
            c[field]
            for c in pool
            if c["name"] != target["name"] and c.get("continent") == target.get("continent")
        ]
        if len(same_cont) >= 3:
            return random.sample(same_cont, 3)
    others = [c[field] for c in pool if c["name"] != target["name"]]
    return random.sample(others, 3)


def _build_atlas_questions(
    count: int,
    difficulty: str = "mid",
    only_mode: str | None = None,
    category_label: str = "Atlas",
) -> list[dict[str, Any]]:
    """Build rich World Atlas quiz rounds (Flags, Capitals, Borders, 3-Clue Mystery, Pop/Area, Traits)."""
    ranked = sorted(COUNTRIES_BANK, key=lambda c: c.get("population", 0), reverse=True)
    base_pool = ranked[:65] if difficulty == "easy" else list(COUNTRIES_BANK)
    border_eligible = [c for c in base_pool if len(c.get("borders", [])) >= 3]
    if not border_eligible:
        border_eligible = [c for c in COUNTRIES_BANK if len(c.get("borders", [])) >= 3]
    all_countries = list(COUNTRIES_BANK)
    if len(all_countries) < 4:
        return []

    built: list[dict[str, Any]] = []
    used_targets: set[str] = set()

    for i in range(count):
        mode = only_mode or ATLAS_MODES[i % len(ATLAS_MODES)]
        pool = border_eligible if mode == "borders" else base_pool
        fresh = [c for c in pool if c["name"] not in used_targets]
        if not fresh:
            fresh = pool
        target = random.choice(fresh)
        used_targets.add(target["name"])

        if mode == "flag":
            distractors = _pick_distractors(target, all_countries, "name", difficulty)
            options = distractors + [target["name"]]
            random.shuffle(options)
            prompt = "Identify the country represented by this flag:"
            built.append(
                {
                    "category": category_label,
                    "mode": "flag",
                    "prompt": prompt,
                    "question": prompt,
                    "flag": target.get("flag"),
                    "flag_svg": target.get("flag_svg"),
                    "flag_code": target["code"],
                    "options": options,
                    "correct_index": options.index(target["name"]),
                    "country_stats": {
                        "name": target["name"],
                        "capital": target["capital"],
                        "subregion": target["subregion"],
                        "population": target["population_label"],
                        "area": target["area_label"],
                        "trait": target["landmark_clue"],
                    },
                    "explanation": (
                        f"{target['name']} — Capital: {target['capital']} ({target['subregion']}) · "
                        f"Pop: {target['population_label']} · Size: {target['area_label']}."
                    ),
                }
            )
        elif mode == "capital":
            ask_capital = (i // len(ATLAS_MODES)) % 2 == 0
            if ask_capital:
                distractors = _pick_distractors(target, all_countries, "capital", difficulty)
                options = distractors + [target["capital"]]
                random.shuffle(options)
                prompt = f"What is the capital city of {target['name']}?"
                correct_val = target["capital"]
            else:
                distractors = _pick_distractors(target, all_countries, "name", difficulty)
                options = distractors + [target["name"]]
                random.shuffle(options)
                prompt = f"{target['capital']} is the capital city of which country?"
                correct_val = target["name"]
            built.append(
                {
                    "category": category_label,
                    "mode": "capital",
                    "prompt": prompt,
                    "question": prompt,
                    "options": options,
                    "correct_index": options.index(correct_val),
                    "explanation": f"{target['capital']} is the capital of {target['name']} ({target['subregion']}).",
                }
            )
        elif mode == "borders":
            clues_borders = random.sample(target["borders"], 3)
            clue_set = set(clues_borders)
            valid_distractors = [
                c["name"]
                for c in all_countries
                if c["name"] != target["name"]
                and not clue_set.issubset(set(c.get("borders", [])))
                and c["name"] not in clue_set
            ]
            if len(valid_distractors) < 3:
                valid_distractors = [c["name"] for c in all_countries if c["name"] != target["name"]]
            distractors = random.sample(valid_distractors, 3)
            options = distractors + [target["name"]]
            random.shuffle(options)
            prompt = f"Which country shares land borders with {', '.join(clues_borders)}?"
            built.append(
                {
                    "category": category_label,
                    "mode": "borders",
                    "border_list": clues_borders,
                    "prompt": prompt,
                    "question": prompt,
                    "options": options,
                    "correct_index": options.index(target["name"]),
                    "explanation": f"{target['name']} borders {', '.join(target['borders'][:6])}.",
                }
            )
        elif mode == "population_area":
            metric_kind = random.choice(["pop_max", "area_max", "area_min"])
            key = "population" if metric_kind == "pop_max" else "area_km2"
            sample_four: list[dict[str, Any]] = []
            target_stat: dict[str, Any] = all_countries[0]
            for _ in range(30):
                cand = random.sample(all_countries, 4)
                ordered = sorted(cand, key=lambda x: x[key], reverse=(metric_kind != "area_min"))
                distinct = (
                    ordered[0][key] * 1.45 < ordered[1][key]
                    if metric_kind == "area_min"
                    else ordered[0][key] > ordered[1][key] * 1.45
                )
                if distinct:
                    sample_four = cand
                    target_stat = ordered[0]
                    break
            if not sample_four:
                sample_four = random.sample(all_countries, 4)
                target_stat = (
                    max(sample_four, key=lambda x: x[key])
                    if metric_kind != "area_min"
                    else min(sample_four, key=lambda x: x[key])
                )
            options = [c["name"] for c in sample_four]
            random.shuffle(options)
            if metric_kind == "pop_max":
                prompt = "Which of these countries has the LARGEST population?"
                exp_txt = f"{target_stat['name']} leads this group with ~{target_stat['population_label']} people (#{target_stat['population_rank']} globally)."
            elif metric_kind == "area_max":
                prompt = "Which of these countries covers the LARGEST land area?"
                exp_txt = f"{target_stat['name']} covers {target_stat['area_label']} (#{target_stat['area_rank']} globally)."
            else:
                prompt = "Which of these countries has the SMALLEST land area?"
                exp_txt = f"{target_stat['name']} covers {target_stat['area_label']} (#{target_stat['area_rank']} globally)."
            built.append(
                {
                    "category": category_label,
                    "mode": "population_area",
                    "prompt": prompt,
                    "question": prompt,
                    "options": options,
                    "correct_index": options.index(target_stat["name"]),
                    "explanation": exp_txt,
                }
            )
        elif mode == "characteristics":
            distractors = _pick_distractors(target, all_countries, "name", difficulty)
            options = distractors + [target["name"]]
            random.shuffle(options)
            geo_tag = "Landlocked" if target.get("landlocked") else f"{len(target.get('borders', []))} land borders"
            prompt = "Which country matches this profile & unique characteristic?"
            built.append(
                {
                    "category": category_label,
                    "mode": "characteristics",
                    "prompt": prompt,
                    "question": prompt,
                    "clues": [
                        f"Location: {target['subregion']} · Coordinates {abs(target['lat']):.1f}°{'N' if target['lat']>=0 else 'S'}, {abs(target['lng']):.1f}°{'E' if target['lng']>=0 else 'W'} ({geo_tag})",
                        f"Scale: Pop ~{target['population_label']} · Size {target['area_label']}",
                        f"Characteristic: {target['landmark_clue']}",
                    ],
                    "options": options,
                    "correct_index": options.index(target["name"]),
                    "explanation": f"{target['name']} (Capital: {target['capital']}) — {target['landmark_clue']}",
                }
            )
        else:  # mystery
            distractors = _pick_distractors(target, all_countries, "name", difficulty)
            options = distractors + [target["name"]]
            random.shuffle(options)
            prompt = "Solve the 3-Clue Mystery — lock in early for higher points!"
            built.append(
                {
                    "category": category_label,
                    "mode": "mystery",
                    "prompt": prompt,
                    "question": prompt,
                    "clues": [
                        f"Clue 1 (1000 pts): {target['subregion']} · Population ~{target['population_label']} · Area {target['area_label']}",
                        f"Clue 2 (600 pts): Currency {target['currency']} · Official Language: {target['language']}",
                        f"Clue 3 (300 pts): {target['landmark_clue']}",
                    ],
                    "options": options,
                    "correct_index": options.index(target["name"]),
                    "explanation": f"Target country: {target['name']} (Capital: {target['capital']}).",
                }
            )
    return built


class QaTriviaGame(BaseGame):
    GAME_TYPE = "qa_trivia"
    TITLE = "QA"
    CATEGORY = "IQ & Atlas"
    DESCRIPTION = (
        "Unified 1–16P QA quiz across World Atlas (SVG flags, capitals, borders, 3-clue mysteries & 197 nations), "
        "Logic IQ, Science, History, General Knowledge, and Tech."
    )
    MIN_PLAYERS = 1
    MAX_PLAYERS = 16
    SUPPORTS_SOLO = True
    SUPPORTS_BOTS = False
    SUPPORTS_SPECTATORS = False
    DEFAULT_SETTINGS = {"category": "All", "rounds": 10, "difficulty": "mid"}

    QUESTION_SECONDS = 15.0
    MYSTERY_SECONDS = 18.0
    REVEAL_SECONDS = 4.0

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.question_seconds: float = self.QUESTION_SECONDS
        self.mystery_seconds: float = self.MYSTERY_SECONDS
        self.questions: list[dict[str, Any]] = []
        self.round_idx: int = 0
        self.subphase: str = "question"  # question | reveal
        self.phase_started_at: float = 0.0
        self.answers: dict[str, dict[str, Any]] = {}
        self._last_tick_sec: int = -1

    def _round_duration(self, q: dict[str, Any]) -> float:
        return self.mystery_seconds if q.get("mode") == "mystery" else self.question_seconds

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        diff = self.normalize_difficulty(self.settings.get("difficulty", "mid"))
        self.settings["difficulty"] = diff
        self.question_seconds, self.mystery_seconds = QA_DURATIONS[diff]
        self._last_tick_sec = -1

        category = normalize_qa_category(self.settings.get("category", "All"))
        self.settings["category"] = category
        raw_rounds = self.settings.get("rounds", 10)
        if isinstance(raw_rounds, bool) or raw_rounds is None:
            parsed_rounds = 10
        else:
            try:
                parsed_rounds = int(raw_rounds)
            except (TypeError, ValueError):
                parsed_rounds = 10
        rounds = max(3, min(25, parsed_rounds))
        self.settings["rounds"] = rounds

        if category == "Atlas":
            pool = _build_atlas_questions(rounds, difficulty=diff, category_label="Atlas")
        elif category == "Flags":
            pool = _build_atlas_questions(
                rounds, difficulty=diff, only_mode="flag", category_label="Flags"
            )
        elif category == "All":
            diff_pool = [
                dict(q, mode="trivia", prompt=q["question"])
                for q in QUESTION_BANK
                if q.get("difficulty") == diff
            ]
            trivia_pool = diff_pool if len(diff_pool) >= rounds else [
                dict(q, mode="trivia", prompt=q["question"]) for q in QUESTION_BANK
            ]
            random.shuffle(trivia_pool)
            atlas_count = max(3, rounds // 2)
            atlas_pool = _build_atlas_questions(atlas_count, difficulty=diff, category_label="Atlas")
            trivia_picks = trivia_pool[: max(1, rounds - len(atlas_pool))]
            pool = trivia_picks + atlas_pool
            random.shuffle(pool)
        else:
            cat_pool = [q for q in QUESTION_BANK if q.get("category") == category]
            diff_pool = [q for q in cat_pool if q.get("difficulty") == diff]
            chosen = diff_pool if len(diff_pool) >= rounds else cat_pool
            pool = [dict(q, mode="trivia", prompt=q["question"]) for q in chosen]
            random.shuffle(pool)

        if not pool:
            pool = [dict(q, mode="trivia", prompt=q["question"]) for q in QUESTION_BANK]
            random.shuffle(pool)

        self.questions = pool[: min(rounds, len(pool))]
        self.round_idx = 0
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""
        self.started_at = time.time()
        for p in self.players:
            p.score = 0
        self._begin_question(self.started_at)
        self.log_event(
            f"QA started ({len(self.questions)} rounds, {diff.upper()}, category: {category})."
        )

    def _begin_question(self, now: float) -> None:
        self.subphase = "question"
        self.phase_started_at = now
        self.answers = {}

    def _begin_reveal(self, now: float) -> None:
        if self.subphase == "reveal":
            return
        self.subphase = "reveal"
        self.phase_started_at = now
        q = self.questions[self.round_idx]
        correct = int(q["correct_index"])
        for pid, ans in self.answers.items():
            if ans["choice"] == correct and not ans["scored"]:
                ans["scored"] = True
                pts = ans["points"]
                player = self.get_player(pid)
                if player:
                    player.score += pts

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."

        now = time.time()
        if action == "next" and self.subphase == "reveal":
            player = self.get_player(player_id)
            connected_count = sum(1 for p in self.players if p.connected)
            if player and (player.is_host or connected_count <= 1):
                self._advance_round(now)
                return True, ""
            return False, "Only the host can skip explanation."

        if action != "answer":
            return False, f"Unsupported action: {action}"
        if self.subphase != "question":
            return False, "Answer window has closed."
        if player_id in self.answers:
            return False, "You already locked in your answer."

        raw_choice = data.get("choice", -1)
        if isinstance(raw_choice, bool):
            return False, "Invalid answer choice."
        try:
            choice = int(raw_choice)
        except (TypeError, ValueError):
            return False, "Invalid answer choice."
        if not (0 <= choice < 4):
            return False, "Choice must be between 0 and 3."

        elapsed = max(0.0, now - self.phase_started_at)
        q = self.questions[self.round_idx]
        duration = self._round_duration(q)
        remaining = max(0.0, duration - elapsed)
        is_correct = choice == int(q["correct_index"])

        if q.get("mode") == "mystery":
            clue2_at = duration / 3.0
            clue3_at = (duration * 2.0) / 3.0
            if not is_correct:
                pts = 0
            elif elapsed < clue2_at:
                pts = 1000
            elif elapsed < clue3_at:
                pts = 600
            else:
                pts = 300
        else:
            pts = (
                500 + math.floor(500.0 * (remaining / duration))
                if is_correct
                else 0
            )

        self.answers[player_id] = {
            "choice": choice,
            "points": pts,
            "is_correct": is_correct,
            "time_remaining": round(remaining, 2),
            "scored": False,
        }

        connected_ids = [p.id for p in self.players if p.connected]
        if connected_ids and all(pid in self.answers for pid in connected_ids):
            self._begin_reveal(now)
        return True, ""

    def on_player_disconnect(self, player_id: str) -> bool:
        changed = super().on_player_disconnect(player_id)
        if changed and self.phase == "playing" and self.subphase == "question":
            connected_ids = [p.id for p in self.players if p.connected]
            if connected_ids and all(pid in self.answers for pid in connected_ids):
                self._begin_reveal(time.time())
        return changed

    def _advance_round(self, now: float) -> None:
        if self.round_idx + 1 >= len(self.questions):
            ranked = sorted(self.players, key=lambda p: p.score, reverse=True)
            top_score = ranked[0].score
            winners = [p.id for p in ranked if p.score == top_score] if top_score > 0 else []
            names = ", ".join(p.name for p in ranked if p.id in winners)
            msg = (
                f"QA complete! Winner: {names} ({top_score} pts)."
                if winners
                else "QA complete with 0 points."
            )
            self.finish_game(winners, msg)
        else:
            self.round_idx += 1
            self._begin_question(now)

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing" or not self.questions:
            return False
        q = self.questions[self.round_idx]
        duration = self._round_duration(q)
        elapsed = now - self.phase_started_at
        if self.subphase == "question" and elapsed >= duration:
            self._begin_reveal(now)
            return True
        if self.subphase == "reveal" and elapsed >= self.REVEAL_SECONDS:
            self._advance_round(now)
            return True
        limit = duration if self.subphase == "question" else self.REVEAL_SECONDS
        sec = int(max(0.0, limit - elapsed))
        if self._last_tick_sec != sec:
            self._last_tick_sec = sec
            return True
        return False

    def get_public_state(self) -> dict[str, Any]:
        if not self.questions:
            return {
                "phase": self.phase,
                "subphase": self.subphase,
                "duration": self.question_seconds,
                "question_duration": self.question_seconds,
                "time_remaining": 0.0,
                "question": {},
                "locked_players": [],
                "round_results": {},
                "winner_ids": self.winner_ids,
                "win_reason": self.win_reason,
            }

        now = time.time()
        q = self.questions[self.round_idx]
        duration = self._round_duration(q)
        elapsed = max(0.0, now - self.phase_started_at)
        limit = duration if self.subphase == "question" else self.REVEAL_SECONDS
        remaining = max(0.0, limit - elapsed) if self.phase == "playing" else 0.0

        revealed_clues: list[str] = list(q.get("clues", []))
        if q.get("mode") == "mystery":
            clues = q.get("clues", [])
            if self.subphase == "reveal" or self.phase == "finished":
                revealed_clues = clues
            elif clues:
                clue2_at = duration / 3.0
                clue3_at = (duration * 2.0) / 3.0
                revealed_clues = [clues[0]]
                if elapsed >= clue2_at and len(clues) > 1:
                    revealed_clues.append(clues[1])
                if elapsed >= clue3_at and len(clues) > 2:
                    revealed_clues.append(clues[2])

        is_revealed = self.subphase == "reveal" or self.phase == "finished"
        flag_svg_val = q.get("flag_svg")
        if q.get("mode") == "flag" and not is_revealed and q.get("flag_code"):
            flag_svg_val = get_sanitized_flag_data_uri(q["flag_code"]) or flag_svg_val

        question_payload: dict[str, Any] = {
            "index": self.round_idx + 1,
            "total": len(self.questions),
            "category": q.get("category", ""),
            "mode": q.get("mode", "trivia"),
            "question": q.get("question", q.get("prompt", "")),
            "prompt": q.get("prompt", q.get("question", "")),
            "options": q.get("options", []),
            "flag": q.get("flag"),
            "flag_svg": flag_svg_val,
            "clues": revealed_clues,
        }
        if is_revealed:
            if q.get("flag_code") is not None:
                question_payload["flag_code"] = q.get("flag_code")
            question_payload["correct_index"] = q.get("correct_index")
            question_payload["explanation"] = q.get("explanation", "")
            if q.get("country_stats"):
                question_payload["country_stats"] = q["country_stats"]

        return {
            "phase": self.phase,
            "subphase": self.subphase,
            "time_remaining": round(remaining, 1),
            "duration": duration,
            "question_duration": duration,
            "selected_category": self.settings.get("category", "All"),
            "question": question_payload,
            "locked_players": list(self.answers.keys()),
            "round_results": (
                {
                    pid: {
                        "choice": ans["choice"],
                        "points": ans["points"],
                        "is_correct": ans["is_correct"],
                    }
                    for pid, ans in self.answers.items()
                }
                if self.subphase == "reveal" or self.phase == "finished"
                else {}
            ),
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }
