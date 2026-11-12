# BLACKOUT ARCADE — Real-Time Multiplayer Games Hub

A server-authoritative, real-time multiplayer and single-player web gaming platform hosting **11 complete games**, powered by **FastAPI + WebSockets** on the backend and **Vanilla ES6+ / HTML5 Canvas / SVG / d3-geo / Web Audio API** on the frontend, built with the **Dimension Liquid Glass Console** design system in [`DESIGN.md`](DESIGN.md).

## Platform Highlights
- **Liquid Glass Console UI:** PS5-inspired horizontal game rail with full-viewport dynamic SVG hero artwork, personalizable `--accent` presets (Crimson Glow `#E5484D`, Dusk Violet, Cobalt Ice, Sunset Amber, Emerald Mist, Rose Quartz, Pure Mono `#EDEDED`, plus custom hex picker), adjustable Liquid Glass refraction (`Subtle Frost`, `Liquid Glass`, `Deep Refraction`), and persistent synthesized Web Audio SFX (`SFX: ON/OFF` toggle in Settings and Arena HUD).
- **Room Chat & Live Event Log Sidebar:** Collapsible Arena Comms drawer (`Comms` HUD toggle with unread notification indicator) combining a live match event stream with 280-character room chat, alongside a dockable **Pinned Game Help** panel and Spectator mode (Chess, Tawla, UNO).
- **World Country Encyclopedia (197 Nations):** Built-in searchable dossier accessible from the top console bar (`GET /api/countries`), with continent filters, interactive 3D Orthographic Globe / 2D Natural Earth vector map preview, clickable land-border neighbor chips, population/area rankings, and SVG flags.
- **Custom Chess & Minesweeper Modes:** Interactive **Custom Chess Board Editor** (free placement with 1 White King and 1 Black King required, supporting checkmate or capture-all victory) and **Custom Minesweeper Grid & Booms** configuration (`8–36` width × `8–30` height, customizable mine counts).

## Included Games (11 Modules)
1. **Snake Protocol** (`Arcade`) — Solo Classic & 2–8P Score Race (`60`/`90`/`120`s timer, `20×20` canvas, WASD / Arrows / Touch D-Pad, Easy/Mid/Hard speeds `165ms` / `125ms` / `85ms`).
2. **Minefield Sweep** (`Arcade`) — 1–8P seeded time-attack: Easy (`9×9`, 10 mines), Mid (`16×16`, 40 mines), Hard (`30×16`, 99 mines), and **Custom Mode** (`8–36 × 8–30` grid with custom mine count), guaranteed zero-mine `3×3` first click, flood-fill, chording, and live race progress.
3. **Chess Protocol** (`Strategy`) — 2P + Spectators (`3+2`, `5+0`, `10+0` clocks): full legal validation (castling, *en passant*, promotion, checkmate, stalemate, 50-move, threefold repetition, insufficient material), SAN log, dual clocks, Easy/Mid/Hard alpha-beta AI bot, and **Custom Chess Board** mode (checkmate or capture all rival non-king pieces).
4. **Tawla / Backgammon** (`Strategy`) — 2P + Spectators across 3 modes (**Classic / Franjieh**, **Tawla 31**, and **Mahbosa**), 24 points, 2d6 server dice, doubles ×4, Bar hits & re-entry / single-checker blocking / blot pinning, bearing-off, and Easy/Mid/Hard AI bot.
5. **Dominoes Chain** (`Tabletop`) — 2–4P Double-Six with hidden server boneyard, multi-round pip scoring (`50` / `100` / `150` target points), blocked-board resolution, and Easy/Mid/Hard AI bot.
6. **Ludo Bunker Race** (`Tabletop`) — 2–4P `15×15` board, safe star squares, triple-6 forfeit, captures, exact home entry, and Easy/Mid/Hard AI bot.
7. **Skru / Screw** (`Card & Party`) — 2–6P hidden `2×2` hand memory game (difficulty-scaled `12s`/`10s`/`7s` pre-game peek, 7/8, 9/10, Jack, King, Red/Green Skru, `+20`, Basra toss, `SKRU!` call, and Easy/Mid/Hard AI bot).
8. **UNO Protocol** (`Card & Party`) — 2–6P + Spectators with official 108-card deck, Skip / Reverse / `+2` / Wild / Wild `+4` action cards, draw-and-play or keep-pass, live `UNO!` callouts & `+2` penalty catches, and Easy/Mid/Hard AI bot.
9. **QA** (`IQ & Atlas`) — 1–16P synchronized countdown quiz (`20s`/`15s`/`10s` standard; `24s`/`18s`/`12s` 3-clue mystery) across **9 selectable categories** (`All`, `Atlas`, `Flags`, `War`, `History`, `Science`, `Logic & Pattern IQ`, `General Knowledge`, `Tech & Pop Culture`), combining `1,800` curated questions with 6 World Atlas quiz modes (`flag`, `capital`, `borders`, `mystery`, `population_area`, `characteristics`).
10. **Globe Atlas QA / Globe Protocol** (`IQ & Trivia`) — 1–16P interactive self-hosted **3D Orthographic Globe & 2D Natural Earth Vector Map** across 4 modes (**Locate by Name**, **Flag Pinpoint**, **Hint Detective** with unlockable clues, and **Border Bridge** shortest land-border nation count) spanning 197 sovereign nations, with thermal distance heatmaps, km/compass bearings, great-circle arcs, and Easy/Mid/Hard profiles.
11. **Blackout Monopoly** (`Tabletop`) — 2–6P 40-tile board, difficulty-scaled starting cash (`$1,800` / `$1,500` / `$1,200`), 15s live auctions, color monopolies, even houses/hotels, railroads/utilities, Jail, live trades, mortgages, bankruptcy, and Easy/Mid/Hard AI bot.

## Quick Launch (Windows)
Run the one-click launcher:
```powershell
.\start.ps1
```
Or double-click `start.bat`, then open [http://localhost:8000](http://localhost:8000).

## Manual Run & Automated Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Cloud Deployment
- **Docker**: `docker build -t blackout-arcade . && docker run -p 8000:8000 blackout-arcade`
- **Render**: Blueprint ready via `render.yaml` (`GET /health` probe included).
- **Railway / Heroku-style**: `Procfile` included.
