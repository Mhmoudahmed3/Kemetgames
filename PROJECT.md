# Project: Blackout Arcade — 4 New Game Modules & Platform Expansion

## Architecture
- **Backend**: Python 3.14+, FastAPI, Uvicorn, WebSockets. Server-authoritative game state governed by `BaseGame` abstraction (`backend/base_game.py`). Rooms and lifecycle managed by `RoomManager` (`backend/room_manager.py`) with 5 Hz tick worker (`backend/main.py`).
- **Frontend**: Vanilla ES6+ modules with dynamic import `mount(container, context) -> { update, destroy }` in `frontend/js/app.js`. Zero bundler / zero build step. Dimension Liquid Glass styling in `frontend/css/main.css` and scoped `.game-board-scope` in `frontend/css/games.css`.
- **Navigation & Staging**: Dynamic PS5 game rail, hero SVG art, and activity mode cards in `frontend/js/game_hub_data.js`. Waiting Bunker handles AI bots and multiplayer room staging.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Platform & Session Registration | Register 4 games in GAME_REGISTRY, ALLOWED_SETTINGS_KEYS, DUEL_FORFEIT_GAMES, navigation rail, and pytest.ini | M1 | R1, R6 |
| 2 | Local Pass-and-Play & Room Multiplayer Support | Ensure local 2P and online room sessions operate cleanly across all modes without layout breakage | M1 | R1 |
| 3 | Tic-Tac-Toe Classic 3x3 & Misère | 3x3 standard and Misère (3-in-a-row loses) with win/draw detection | M2 | R2 |
| 4 | Tic-Tac-Toe Extended Grids | 4x4 and 5x5 grids requiring 4-in-a-row to win | M2 | R2 |
| 5 | Tic-Tac-Toe Ultimate Mode | 9 nested 3x3 boards, opponent-dictated target sub-board routing, free placement fallback, macro board win/draw | M2 | R2 |
| 6 | Tic-Tac-Toe AI Opponents | Easy, Medium, and mathematically unbeatable Minimax for 3x3 | M2 | R2 |
| 7 | Tic-Tac-Toe UI, Highlighting & Pass-and-Play | Winning cell highlighting, clean draw handling, local 2P and room play | M2 | R2 |
| 8 | Rock-Paper-Scissors Classic & Lizard-Spock | 3-choice (Rock, Paper, Scissors) and 5-choice (+ Lizard, Spock) balanced cyclic graphs | M3 | R3 |
| 9 | Rock-Paper-Scissors Match Formats & Streaks | Best-of-3, Best-of-5, and Endless Streak formats with running win/loss/tie stats | M3 | R3 |
| 10 | Rock-Paper-Scissors Countdown Reveal | Animated 3, 2, 1 countdown prior to revealing secret committed choices | M3 | R3 |
| 11 | Rock-Paper-Scissors Interactive Rule Chart | Interactive pentagram tooltip/modal displaying all win relationships | M3 | R3 |
| 12 | Connect 4 Classic & 5-in-a-Row | Classic (7x6, 4-streak) and 5-in-a-Row (9x7, 5-streak) | M4 | R4 |
| 13 | Connect 4 Pop Out Mode | Bottom row disc removal, gravity shift, simultaneous double-win tie handling | M4 | R4 |
| 14 | Connect 4 Blitz Mode | Strict 5-second per-turn countdown integrated with _tick_timers | M4 | R4 |
| 15 | Connect 4 Drop Animations & Input Locks | Smooth vertical drop bounce, column input locking during drops, AI turns, and full columns | M4 | R4 |
| 16 | Reusable 52-Card Deck Module | Standard 52-card deck, Fisher-Yates shuffle, visual faces & backs, live deck counter | M5 | R5 |
| 17 | Playing Cards — Blackjack | Hit, Stand, Double Down, Split, Dealer draws to 17, soft/hard Ace scoring | M5 | R5 |
| 18 | Playing Cards — War | Click-to-flip, Auto-Battle, 3-card tie-breaker war piles, card collection | M5 | R5 |
| 19 | Playing Cards — Memory / Concentration | Card matching grid (4x4, 6x4), move tracker, elapsed timer, AI memory recall | M5 | R5 |
| 20 | Playing Cards — High-Low | Higher/lower guesses, multiplier streak progression, push preservation, bank feature | M5 | R5 |
| 21 | State & Deck Resets between Rounds | Clean state and deck resets without stale UI or memory leaks | M5 | R5 |
| 22 | Automated Test Suite & E2E Verification | Automated test suites for all 4 games, verifying rules, edge cases, room state transitions, and 100% pass | M6 | R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Platform Foundation & Session Architecture | pytest.ini, catalog registration (11 -> 15 games), room manager settings/forfeit rules, local pass-and-play support, updating test baseline | none | DONE |
| M2 | Tic-Tac-Toe Game Module | Engine, UI, AI (Easy, Medium, Minimax), Ultimate mode, Extended grids, Misère, local/room play, unit tests | M1 | DONE |
| M3 | Rock-Paper-Scissors Game Module | Engine, UI, Classic & Lizard-Spock, Bo3/Bo5/Endless, animated countdown, rule chart modal, stats tracking, unit tests | M1 | DONE |
| M4 | Connect 4 Game Module | Engine, UI, Classic 7x6, Pop Out (double-win tie), 5-in-a-Row 9x7, Blitz 5s timer, drop animations, input locks, unit tests | M1 | DONE |
| M5 | Playing Cards Game Module | Reusable 52-card deck (Fisher-Yates), Blackjack, War, Memory, High-Low, SVG card faces, clean resets, unit tests | M1 | DONE |
| M6 | E2E Testing Pass & Adversarial Hardening | Phase 1: Pass 100% of Tiers 1-4 E2E tests published in TEST_READY.md; Phase 2: Tier 5 adversarial hardening | M2, M3, M4, M5 | DONE |

*Note: E2E Testing Track is running in parallel (sub_orch: cdd23810-f0bd-4bd6-936f-8038a9a85e3b) to publish TEST_READY.md.*

## Interface Contracts

### Shell ↔ Game Module Contract
- **Frontend Export**: Every game module in `frontend/js/games/<game_type>.js` MUST export:
  ```javascript
  export function mount(container, context) {
    // context: { sendAction, sound, getPlayerId, getPlayers }
    return {
      update(publicState, privateState, players) { ... },
      destroy() { ... }
    };
  }
  ```
- **Backend Class**: Every game engine in `backend/games/<game_type>_game.py` MUST subclass `BaseGame`:
  - `start_game(settings: dict | None)`
  - `handle_action(player_id: str, action: str, data: dict) -> tuple[bool, str]`
  - `get_public_state() -> dict[str, Any]`
  - `get_private_state(player_id: str) -> dict[str, Any]` (optional)
  - `_tick_timers(now: float) -> bool` (optional)
  - `get_bot_action(bot_id: str) -> tuple[str, dict] | None` (optional)
  - `reset_for_rematch()`

### Shared 52-Card Deck Contract (`backend/games/playing_cards_deck.py`)
- Standard 52 cards: 4 suits (`spades`, `hearts`, `diamonds`, `clubs`), 13 ranks (`2` through `10`, `J`, `Q`, `K`, `A`).
- `fisher_yates_shuffle(deck: list[dict]) -> None`
- `draw_card() -> dict | None`, `deck_count() -> int`, `reset_deck() -> None`.

## Code Layout
- `pytest.ini` — Pytest path configuration.
- `backend/games/tic_tac_toe_game.py` — Tic-Tac-Toe backend engine.
- `backend/games/rock_paper_scissors_game.py` — Rock-Paper-Scissors backend engine.
- `backend/games/connect4_game.py` — Connect 4 backend engine.
- `backend/games/playing_cards_deck.py` — Reusable 52-card deck module.
- `backend/games/playing_cards_game.py` — Playing Cards backend engine.
- `backend/games/__init__.py` — Registry of all 15 games.
- `backend/room_manager.py` — Settings whitelisting and session forfeit mappings.
- `frontend/js/games/tic_tac_toe.js` — Tic-Tac-Toe frontend module.
- `frontend/js/games/rock_paper_scissors.js` — Rock-Paper-Scissors frontend module.
- `frontend/js/games/connect4.js` — Connect 4 frontend module.
- `frontend/js/games/playing_cards.js` — Playing Cards frontend module.
- `frontend/js/game_hub_data.js` — Game Hub metadata, SVG hero art, and activity cards.
- `frontend/js/app.js` — Hazard rail icons and settings schemas.
- `frontend/css/games.css` — Scoped Liquid Glass styling for all 4 game modules.
- `tests/test_tic_tac_toe.py` — Automated tests for Tic-Tac-Toe.
- `tests/test_rock_paper_scissors.py` — Automated tests for Rock-Paper-Scissors.
- `tests/test_connect4_game.py` — Automated tests for Connect 4.
- `tests/test_playing_cards_game.py` — Automated tests for Playing Cards.
- `tests/test_e2e_platform_suite.py` — Platform-wide E2E automated test suite.
