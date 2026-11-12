# AI AGENT MASTER SPECIFICATION & ARCHITECTURE REFERENCE

> **SYSTEM DIRECTIVE:**
>
> Blackout Arcade is a complete, production-ready, real-time multiplayer and single-player web gaming platform built around **11 server-authoritative game modules** and the **Dimension Liquid Glass Console** UI documented in [`DESIGN.md`](DESIGN.md).
>
> **CORE ARCHITECTURAL INVARIANTS:**
>
> 1. **Complete Rule Enforcement:** No stubs or placeholders (`// TODO` / `pass`) in core game rules; every module ships full server-side move validation, win/draw resolution, and optional Easy/Mid/Hard AI bots.
> 2. **Server-Authoritative State:** All multiplayer game states, dice rolls, hidden card hands, boneyards, mine grids, and trivia/map timers are validated and controlled by the Python backend so clients cannot cheat via the browser console.
> 3. **Frictionless Onboarding:** Users enter a display callsign to receive a session secret (`/ws/{client_id}?secret=...`) and immediately access the Liquid Glass Console Hub, launch solo/bot matches, or create/join 6-character rooms.
> 4. **Clean Modular Architecture:** Every engine implements [`BaseGame`](backend/base_game.py) and registers in [`GAME_REGISTRY`](backend/games/__init__.py) with a matching frontend ES module under `frontend/js/games/`.

## 1. Technology Stack

* **Backend:** Python `3.10+` using `FastAPI`, `uvicorn[standard]`, `pydantic`, and native `WebSockets` (64 KB frame cap + background 200 ms room tick loop).
* **Frontend:** Semantic HTML5 (`frontend/index.html` with zero inline styles), Modern CSS3 (Dimension Liquid Glass tokens, Flexbox, Grid, `:focus-visible` accessibility), Vanilla JavaScript (ES6+ Modules, HTML5 `<canvas>`, SVG, and zero-dependency Web Audio API synthesizer), plus self-hosted `d3-array`, `d3-geo`, `topojson-client`, Natural Earth `world-110m.json`, and 197 SVG nation flags.
* **State Storage:** In-memory Python state manager (`RoomManager`) using dataclasses/dictionaries for active rooms and sessions, atomic JSON persistence for `backend/data/leaderboard.json`, and static JSON data banks (`qa_questions.json` with 1,800 questions; `countries_data.json` with 197 sovereign nations).
* **Testing:** `pytest` + `httpx` (`tests/test_engines_core.py`, `tests/test_protocol_and_security.py`).

## 2. Live Project Directory Structure

```
games website/
├── .dockerignore
├── .env.example
├── Dockerfile
├── Procfile
├── render.yaml
├── requirements.txt             # fastapi, uvicorn[standard], websockets, pydantic, pytest, httpx
├── start.bat                    # Windows one-click launcher
├── start.ps1                    # Windows PowerShell launcher
├── DESIGN.md                    # Dimension Liquid Glass design tokens & UI spec
├── README.md                    # Platform overview, 11-game roster & run commands
├── ai_master_specification_multiplayer_games_platform.md
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server, static mounts, REST endpoints, /ws/{client_id}
│   ├── room_manager.py          # Room lifecycle, 6-char codes, bot/disconnect takeover, leaderboard
│   ├── base_game.py             # Abstract BaseGame contract, PlayerSlot & difficulty helpers
│   ├── data/
│   │   ├── country_store.py     # 197-nation atlas loader, Haversine/bearing math, BFS border graph & sanitized SVG flags
│   │   ├── countries_data.json  # 197 countries: capitals, ISO codes, coords, borders, ranks, clues
│   │   ├── leaderboard.json     # Persistent per-game wins & high scores
│   │   └── qa_questions.json    # 1,800 curated IQ, War, History, Science, Tech & General questions
│   ├── games/
│   │   ├── __init__.py          # GAME_REGISTRY mapping all 11 game_type keys
│   │   ├── snake_game.py        # Solo & 2–8P Score-Race Snake engine
│   │   ├── minesweeper_game.py  # Seeded Minesweeper (Easy/Mid/Hard/Custom) & race tracker
│   │   ├── chess_game.py        # Full legal Chess + Custom Board mode, clocks & alpha-beta AI
│   │   ├── backgammon_game.py   # Classic / Tawla 31 / Mahbosa dice, bar/pinning & AI
│   │   ├── dominoes_game.py     # 2–4P Double-Six boneyard, chain & pip counter
│   │   ├── ludo_game.py         # 2–4P 15x15 Ludo track, safe zones & capture logic
│   │   ├── skru_game.py         # 2–6P Skru hidden-hand memory & action card engine
│   │   ├── uno_game.py          # 2–6P official 108-card UNO engine, Wild +4 & UNO call/catch
│   │   ├── qa_trivia_game.py    # Unified 1–16P QA quiz (Trivia + 6 World Atlas modes, 9 categories)
│   │   ├── globe_game.py        # 1–16P 3D/2D interactive Globe & Border Bridge engine
│   │   └── monopoly_game.py     # 2–6P Monopoly economy, 15s auctions, mortgages & trades
│   └── scripts/                 # Question bank builders (build_qa_bank.py + qa_*_data.py)
├── frontend/
│   ├── index.html               # Semantic SPA shell, Liquid Glass Console, Arena & Modals
│   ├── css/
│   │   ├── main.css             # Dimension Liquid Glass tokens, accent system, shell, comms drawer
│   │   └── games.css            # Scoped board, card, globe, and Pure Mono contrast styles
│   ├── data/
│   │   └── world-110m.json      # Natural Earth TopoJSON world geometry
│   ├── flags/                   # 197 vector SVG flags (<iso2>.svg)
│   ├── vendor/                  # Self-hosted d3-array, d3-geo, topojson-client
│   └── js/
│       ├── app.js               # BroadcastApp controller, personalization, WS client & comms
│       ├── game_hub_data.js     # 11-module metadata, deep-link activities, help & SVG hero art
│       ├── sound.js             # Zero-dependency Web Audio API SFX synthesizer
│       ├── utils.js             # HTML escaping, resilient storage, active player filtering
│       ├── world_map.js         # Shared 3D Orthographic Globe & 2D Natural Earth vector controller
│       └── games/
│           ├── snake.js
│           ├── minesweeper.js
│           ├── chess.js
│           ├── backgammon.js
│           ├── dominoes.js
│           ├── ludo.js
│           ├── skru.js
│           ├── uno.js
│           ├── qa_trivia.js
│           ├── globe.js
│           └── monopoly.js
└── tests/
    ├── conftest.py
    ├── test_engines_core.py
    └── test_protocol_and_security.py
```

## 3. Unified HTTP & WebSocket Protocol (JSON Contract)

### REST Endpoints (`backend/main.py`)
* `GET /` — Serves `frontend/index.html` SPA shell.
* `GET /health` — Health probe returning `{"status": "ok", "active_rooms": ..., "connected_clients": ...}`.
* `GET /api/games` — Returns the 11-module catalog metadata (`GAME_REGISTRY` capabilities, defaults, player bounds).
* `GET /api/leaderboard` — Returns top-10 persistent standings per game module.
* `GET /api/countries?q=&continent=All` — Filterable 197-nation dossier list powering the World Country Encyclopedia and interactive globe.

### Client $\rightarrow$ Server WebSocket Payloads (`/ws/{client_id}?secret=...`)

```json
{
  "type": "SET_NAME | CREATE_ROOM | JOIN_ROOM | LEAVE_ROOM | START_GAME | GAME_ACTION | CHAT_MSG",
  "player_name": "String",
  "room_code": "6-char String (optional)",
  "game_type": "snake | minesweeper | chess | backgammon | dominoes | ludo | skru | uno | qa_trivia | globe | monopoly",
  "payload": {
    "action": "move | roll | draw | play | pass_turn | shout_uno | catch_uno | peek | swap | answer | guess | answer_between | reveal_hint | bid | buy | add_bot | remove_bot | update_settings | rematch",
    "data": {}
  }
}
```

### Server $\rightarrow$ Client WebSocket Payloads

```json
{
  "type": "LOBBY_STATE | ROOM_JOINED | ROOM_UPDATE | GAME_STARTED | GAME_STATE | PRIVATE_STATE | ERROR | GAME_OVER",
  "room_code": "ABC123",
  "game_type": "uno",
  "public_state": {},
  "private_state": {},
  "players": [
    {"id": "p1", "name": "Alex", "score": 0, "is_host": true, "connected": true, "is_bot": false, "seat": 0, "role": "player"}
  ],
  "message": "Optional status or error notification"
}
```

> **Note on `private_state` & Room Isolation:**
> * Games with hidden or per-player state (**Dominoes**, **Skru**, **UNO**, **Minesweeper**, **Globe**) deliver sensitive hands, peeked cards, private mine progress, or personal guess heatmaps exclusively via `PRIVATE_STATE` (or per-client `ROOM_JOINED`/`ROOM_UPDATE` snapshots) to that participant's socket, never in `public_state`.
> * During Flag identification rounds in **QA** and **Globe**, `get_sanitized_flag_data_uri` strips ISO-2 IDs and embeds a base64 `data:image/svg+xml` URI so players cannot inspect DOM attributes to deduce the country code.
> * `RoomManager._is_active_room_recipient` and client-side `room_code` guards in `app.js` prevent stale broadcasts from reaching leavers or mismatched rooms, and permanent bot takeovers clear old reclaimable session room bindings after rematch.

## 4. Detailed Game Specifications (11 Modules)

### 4.1 Snake (`snake_game.py` & `snake.js`)
* **Modes:** Solo Classic & Multiplayer Score Race ($2\text{--}8$ players; configurable `duration`: `60` / `90` / `120` s, clamped `15–600` s).
* **Difficulty Profiles:** `easy` (`165ms` step, `10` pts/food), `mid` (`125ms` step, `10` pts/food), `hard` (`85ms` step, `15` pts/food).
* **Mechanics & Sync:** HTML5 `<canvas>` $20 \times 20$ grid with WASD, Arrow keys, and Touch D-Pad (with turn queueing). Clients sync telemetry (`sync` action) every $200\text{ ms}$ under server rate/anti-cheat checks; last snake alive or highest score at timer expiration wins.

### 4.2 Minesweeper (`minesweeper_game.py` & `minesweeper.js`)
* **Modes:** Solo & Multiplayer Seeded Time-Attack ($1\text{--}8$ players).
* **Difficulties & Custom Mode:**
  * `easy` / `beginner`: $9 \times 9$, $10$ mines.
  * `mid` / `intermediate`: $16 \times 16$, $40$ mines.
  * `hard` / `expert`: $30 \times 16$ (`16` rows × `30` cols), $99$ mines.
  * `custom`: User-defined `width` ($8\text{--}36$), `height` ($8\text{--}30$), and `mines` / `booms` ($1$ up to $(\text{rows} \times \text{cols}) - 9$).
* **Mechanics:** Server generates each player's seeded mine matrix after their first click, guaranteeing a $3 \times 3$ zero-mine clearing around the opening tile. Supports flood-fill reveal, right-click / flag-mode toggle, chording, and live race completion bars.

### 4.3 Chess (`chess_game.py` & `chess.js`)
* **Players:** $2$ players (White vs. Black) + Spectators, plus Easy (depth 1) / Mid (depth 2) / Hard (depth 3) alpha-beta AI bot.
* **Time Controls:** `3+2`, `5+0`, `10+0` dual server-synced clocks.
* **Standard & Custom Rules:**
  * Full FIDE validation: piece movement, castling, *en passant*, pawn promotion (Q/R/B/N), check, checkmate, stalemate, $50$-move rule, threefold repetition, and insufficient material.
  * **Custom Chess Board Mode (`custom_board` / `custom_fen`):** Interactive board editor allowing free placement of pieces (requiring exactly 1 White King and 1 Black King). Supports Preset templates (`Standard`, `K+Q vs K`, `Clear`) and wins by checkmate **or** capturing all of the opponent's non-king pieces.
* **UI:** Interactive $8 \times 8$ board that auto-flips for Black, legal move dot indicators, captured piece trays, and SAN move history log.

### 4.4 Backgammon / Tawla (`backgammon_game.py` & `backgammon.js`)
* **Players:** $2$ players + Spectators + Easy/Mid/Hard AI bot.
* **3 Modes (`mode`):**
  * `classic` (Franjieh): Standard setup (`2, 5, 3, 5`), hitting blots to the central Bar with mandatory re-entry.
  * `tawla_31` (طاولة 31): All $15$ checkers start stacked on the opponent's 1-point; no hitting allowed—even a single checker blocks a point.
  * `mahbosa` (المحبوسة): All $15$ checkers start on the opponent's 1-point; landing on a lone opponent checker pins (imprisons) it underneath the stack until freed.
* **Rules:** $24$ triangles (points), $15$ checkers per player, server-generated $2\text{d}6$ dice (doubles grant $4$ moves), and bearing-off rules.

### 4.5 Dominoes (`dominoes_game.py` & `dominoes.js`)
* **Players:** $2\text{--}4$ players + Easy/Mid/Hard AI bot.
* **Rules:** Standard Double-Six set ($28$ tiles), $7$ dealt privately per player, remaining tiles in server boneyard. Match open ends of the chain, draw from boneyard when stuck, pass only when boneyard is empty. First to empty hand or lowest pip sum on blocked board collects opponent pips toward `target_score` (`50` / `100` / `150`).

### 4.6 Ludo (`ludo_game.py` & `ludo.js`)
* **Players:** $2\text{--}4$ players (Red, Green, Yellow, Blue), $4$ tokens each + Easy/Mid/Hard AI bot.
* **Rules:** $15 \times 15$ board with $52$-square outer track, roll `6` to deploy, bonus roll on `6` / capture / Home entry, triple-6 turn forfeit, safe starred squares (`★`), exact roll to enter Home triangle, and step-by-step hop animations.

### 4.7 Skru / Screw (`skru_game.py` & `skru.js`)
* **Players:** $2\text{--}6$ players + Easy/Mid/Hard AI bot.
* **Goal:** Finish the round with the **lowest** total card points.
* **Deck & Powers:** `1–6` face value; `7`/`8` (Peek Self); `9`/`10` (Peek Opponent); `Jack` (Blind Swap); `King` (Look & Swap); `Red Skru` (`0` pts); `Green Skru` (`+25` pts); `+20 Card` (`+20` pts).
* **Flow:** $2 \times 2$ face-down grid with difficulty-scaled opening peek (`12s` Easy / `10s` Mid / `7s` Hard) of bottom $2$ cards, Draw / Discard Swap / Basra matching toss (penalty `+1` card on wrong guess), and `SKRU!` call triggering 1 final turn per rival while locking the caller's cards.

### 4.8 UNO Protocol (`uno_game.py` & `uno.js`)
* **Players:** $2\text{--}6$ players + Spectators + Easy/Mid/Hard AI bot.
* **Deck Composition (`build_uno_deck`):** Official $108$-card deck—four colors (`red`, `blue`, `green`, `yellow`), one `0`, two each of `1–9`, two each of `Skip`, `Reverse`, and `+2` (`20` pts), plus four `Wild` and four `Wild +4` (`50` pts).
* **Rules & Actions:**
  * `play`: Match active color, symbol/number, or play a Wild (choosing next `red`/`blue`/`green`/`yellow`). In 2-player matches, `Reverse` acts like `Skip` so the active player keeps the turn. `Skip` / `+2` / `Wild +4` force draws and advance past the penalized seat.
  * `draw` / `pass_turn`: Drawing a playable card permits immediate play or keeping it via `pass_turn`. Discard pile automatically reshuffles into the draw deck when depleted; if both are exhausted, stalled passes resolve by lowest remaining hand points.
  * `shout_uno` & `catch_uno`: Call `UNO!` when holding `1` or `2` cards; rivals can catch an uncalled `1`-card hand to deal `+2` penalty cards.

### 4.9 Unified QA (`qa_trivia_game.py` & `qa_trivia.js`)
* **Modes:** Solo Brain Test & Multiplayer Party QA ($1\text{--}16$ players), configurable `rounds` (`8` / `10` / `12` / `15`, clamped `3–25`).
* **9 Selectable Categories (`QA_CATEGORIES`):** `All`, `Atlas`, `Flags`, `War`, `History`, `Science`, `Logic & Pattern IQ`, `General Knowledge`, `Tech & Pop Culture`.
* **Difficulty Timers & Pools (`QA_DURATIONS`):**
  * `easy`: `20s` standard / `24s` 3-clue mystery; Atlas draws from top-65 most populous nations.
  * `mid`: `15s` standard / `18s` 3-clue mystery; full 197-nation atlas + `1,800`-question `qa_questions.json` bank.
  * `hard`: `10s` standard / `12s` 3-clue mystery; same-continent distractors on Atlas questions.
* **6 Rotating World Atlas Modes (`ATLAS_MODES`):** `flag` (sanitized SVG flag ID), `capital` (country $\leftrightarrow$ capital), `borders` (3-neighbor Border Detective), `population_area` (largest population, largest/smallest area), `characteristics` (coordinates, scale & traits), and `mystery` (progressive 3-clue mystery: `1000` pts before $1/3$ clock, `600` pts before $2/3$ clock, `300` pts in final third).
* **Standard Speed Scoring Formula:**
  $$\text{Points} = 500 + \left\lfloor 500 \times \frac{\text{Time Remaining}}{\text{Round Duration}} \right\rfloor$$

### 4.10 Globe Protocol / Globe Atlas QA (`globe_game.py`, `globe.js`, `world_map.js`, `country_store.py`)
* **Players:** $1\text{--}16$ players over `197` sovereign nations, rendered on a self-hosted interactive **3D Orthographic Globe & 2D Natural Earth Vector Map** (`d3-geo` + `topojson-client` + `/data/world-110m.json`), supporting rotation, zoom, microstate click pins, and smooth `flyTo` transitions.
* **Difficulty Profiles (`GLOBE_DIFFICULTY_PROFILES`):**
  * `easy`: `55s` locate / `35s` border bridge, `7` locate attempts, top-70 nations.
  * `mid`: `40s` locate / `25s` border bridge, `6` locate attempts, all `197` nations.
  * `hard`: `25s` locate / `16s` border bridge, `4` locate attempts, all `197` nations.
* **4 Modes (`mix`, `name`, `flag`, `hint`, `borders_between`):**
  1. **Locate by Name (`name`):** Pinpoint the named nation directly on the globe/map.
  2. **Flag Pinpoint (`flag`):** Sanitized SVG flag (ISO-2 IDs stripped) $\rightarrow$ locate the country on the globe/map.
  3. **Hint Detective (`hint`):** Start with `2` starter clues (Region & Characteristic) and optionally spend `reveal_hint` up to `2` times (unlocking Scale & Identity/Capital at `-75` pts per extra clue) to deduce the country.
  4. **Border Bridge (`borders_between`):** Two highlighted countries connected by a great-circle arc; submit `answer_between` (`0–20`) for the minimum intermediate land-border nations computed via server BFS (`shortest_border_path`). Exact match scores `1000 + floor(300 * remaining / duration)`; off-by-1 scores `450`; off-by-2 scores `200`.
* **Locate Scoring & Thermal Feedback:** Every wrong map guess returns Haversine `distance_km`, compass `bearing` + arrow, and thermal `heat` tier (`Far` / `Warm` / `Hot` / `Exact`). Solving scores `max(150, ATTEMPT_BASE_SCORES[attempt] - 75 * extra_hints) + floor(150 * remaining / duration)`.

### 4.11 Monopoly (`monopoly_game.py` & `monopoly.js`)
* **Players:** $2\text{--}6$ players + Easy/Mid/Hard AI bot.
* **Mechanics:** $40$-tile perimeter board, difficulty-scaled starting treasury (`$1,800` Easy / `$1,500` Mid / `$1,200` Hard), passing GO collects `$200`, $15$-second live multiplayer **Auctions**, color-set monopolies with even House/Hotel building, Railroads & Utilities, Jail mechanics, live **Player-to-Player Trade Modal**, mortgages (`50%`), and automatic Bankruptcy asset transfer.

## 5. UI/UX, Personalization & Audio Architecture

1. **Dimension Liquid Glass Entry Gate (`<main id="view-entry">`):**
   * Centered frosted `.entry-glass-card` on `#0a0a0a` Void Canvas with live WebSocket status badge (`#ws-status-dot`, `#ws-status-entry`), Callsign input (`maxlength="20"`), inline Accent Swatch strip, and Customize button.
2. **PS5-Inspired Liquid Glass Console Hub (`#view-lobby`):**
   * Floating `.ps5-topbar-inner.glass-nav` with `Hub` tab, **World Country Encyclopedia** modal button (197 searchable nations, continent tabs, interactive 3D/2D map preview, clickable border chips), **Bunker Records** leaderboard modal button, **Appearance & Settings** modal button, Callsign Avatar rename trigger, and live clock.
   * Top horizontal Game Switcher Rail (`#ps5-game-rail`, keyboard `ArrowLeft`/`ArrowRight` navigation) featuring `Explore` + all `11` game modules, full-bleed dynamic SVG hero artwork tinted by `--accent`, inline Difficulty / QA Category / Custom Minesweeper controls, `Play Solo` / `Host Game` / `Join Game` CTAs, 16:9 bottom Activity Card strip (deep-linking straight into presets or Custom Chess Board Editor), and below-the-fold Contextual Help, Live Rooms, and Top Module Records.
3. **Personalizable Accent & Glass Intensity (`#modal-settings`):**
   * 7 curated swatches (`Crimson Glow #E5484D`, `Dusk Violet #6B62F2`, `Cobalt Ice #3B82F6`, `Sunset Amber #F59E0B`, `Emerald Mist #10B981`, `Rose Quartz #F43F5E`, `Pure Mono #EDEDED`) + custom spectrum color picker and hex input. Dynamically updates `--accent`, `--accent-rgb`, `--accent-glow`, `--accent-contrast` (`#0A0A0A` vs `#FFFFFF`), and the live SVG favicon.
   * 3 Liquid Glass Refraction tiers: `Subtle Frost` (`10px` / `130%`), `Liquid Glass` (`20px` / `165%`), and `Deep Refraction` (`32px` / `195%`).
4. **In-Game Arena HUD, Waiting Bunker & Collapsible Sidebars (`#view-arena`):**
   * Sticky `.arena-hud.glass-nav` displaying `← Hub`, Room Code + Copy button, active game `<h1>`, Turn Indicator + Spectator Badge (`#arena-spectator-badge`), Player Chips strip, **Arena Sound Mute Toggle** (`#btn-arena-mute`, `SFX: ON`/`OFF` synced with Settings), Theme shortcut (`#btn-arena-settings`), **Pin Help** (`#btn-pin-help` toggling left-docked `#pip-help-panel`), and **Comms** toggle (`#btn-toggle-comms` with `#comms-unread-dot`).
   * Collapsible right-hand **Room Chat & Live Event Log Sidebar** (`#arena-comms-drawer`, sticky `320px` side dock on desktop and fixed slide-over drawer at `<= 1024px`) containing `LIVE EVENT LOG` (`#arena-events-list`) and `ROOM CHAT` (`#arena-chat-list` + `#arena-chat-form`, max `280` chars).
   * Pre-game `#waiting-bunker` with live participant roster, dynamic settings controls, Custom Minesweeper Grid & Booms inputs, and Host `+ Add AI Bot` / `- Remove Bot` & `Launch Match` controls.
5. **Synthesized Sound Effects (`sound.js`):**
   * Native `AudioContext` oscillators and bandpass-filtered noise buffers generating zero-dependency UI clicks, dice rolls, card flips, chess clacks, countdown ticks, and victory fanfares, persisted via `localStorage` (`blackout_muted`) and toggled from either `#modal-settings` or `#btn-arena-mute`.

## 6. Verification & Launch Commands

* **Automated Test Suite (`tests/`):**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest -v
  ```
* **Local Development Server:**
  ```powershell
  .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
* **Frontend Syntax Check:**
  ```powershell
  node --check frontend/js/app.js
  ```
