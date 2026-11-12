# Blackout Arcade — Global Workspace Rules

These rules apply across the entire **Blackout Arcade** workspace (`d:\LEARNING\cs50\games website`) and persist across all sessions.

---

## Core Multi-Agent Orchestration Rules

- **Rule 1 – Zero Direct File Access in Main Thread:** Never read codebase files (`frontend/`, `backend/`, `tests/`), run terminal checks, or edit code directly in the main thread—even for small, 1-file prompts. You must spawn specialized subagent instances for all file inspection, coding, and testing.
- **Rule 2 – Mandatory Subagent Spawning (No Roleplaying):** For every user prompt, act strictly as the **Manager** (`manager`) orchestrator. Do not simulate or roleplay the other agents in a single thread; actively spawn the dedicated subagent tools by domain:
  - **UI, Lobby, Arena Chrome & CSS** -> Spawn `frontend-shell` ([`.antigravity/agents/frontend-shell.md`](agents/frontend-shell.md))
  - **Python Server, Rooms & Game Engines** -> Spawn `backend-core` ([`.antigravity/agents/backend-core.md`](agents/backend-core.md))
  - **Cross-Layer Game Wiring (All 11 Modules)** -> Spawn `game-integrator` ([`.antigravity/agents/game-integrator.md`](agents/game-integrator.md))
  - **QA, Regression Tests & Verification** -> Spawn `tester` ([`.antigravity/agents/tester.md`](agents/tester.md))
- **Rule 3 – Mandatory Attribution Summary:** Always end responses with a clear summary listing which spawned subagent handled each part of the task and what files or checks they owned.

---

## Project Architecture & Quality Standards

- **Frontend Stack:** Semantic HTML5 (`<main>`, `<section>`, `<aside>`, `<dialog>`, `<h3>`, `aria-*`), Dimension Liquid Glass CSS (`frontend/css/main.css`, `frontend/css/games.css`), and Vanilla ES6+ JavaScript (`frontend/js/`).
  - Never use inline `style="..."` or `on*=` attributes in HTML or JS template strings.
  - Always escape user-supplied or server-derived strings via `escapeHtml` (`frontend/js/utils.js`) or `.textContent` before DOM insertion.
  - Ensure all accents (including Pure Mono `#EDEDED`) maintain contrast via `--accent-contrast`.
- **Backend Stack:** FastAPI + WebSockets (`Python 3.10+`, PEP 8, type hints, server-authoritative state).
  - Never leak hidden hands, mine maps, or ISO-2 flag codes in `public_state`.
  - Keep all 11 engines (`snake`, `minesweeper`, `chess`, `backgammon`, `dominoes`, `ludo`, `skru`, `uno`, `qa_trivia`, `globe`, `monopoly`) crash-free and soft-lock-free across all difficulties (`easy`, `mid`, `hard`, plus `custom` for Minesweeper).
- **Verification Standard:** Never claim tests pass without running:
  `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -v`
  (isolated via `tests/conftest.py` so `backend/data/leaderboard.json` is never mutated) and validating JS syntax with `node --check`.

