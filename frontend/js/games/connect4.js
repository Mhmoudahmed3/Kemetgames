/**
 * Blackout Arcade — Connect 4 Frontend Module
 * High-contrast Dimension Liquid Glass UI supporting Classic 7x6,
 * Pop Out mode, 5-in-a-Row (9x7), and Blitz Mode with 5s countdown timer.
 */

import { escapeHtml } from '/js/utils.js?v=20261112';

const MODE_LABELS = {
  classic: 'CLASSIC 7×6',
  pop_out: 'POP OUT 7×6',
  five_in_a_row: '5-IN-A-ROW 9×7',
  '5_in_a_row': '5-IN-A-ROW 9×7',
  blitz: 'BLITZ 5S',
};

export function mount(container, context = {}) {
  const {
    sendAction = () => {},
    sound = {},
    getPlayerId = () => '',
    getPlayers = () => [],
  } = context;

  // Set scoped attribute
  container.setAttribute('data-game', 'connect4');

  let lastState = null;
  let lastMoveSig = '';
  let lastPhase = 'pre_game';
  let isAnimating = false;
  let animTimer = null;
  let blitzTimerId = null;
  let serverTurnStartWall = null;
  let clientTurnStartLocal = null;
  let lastBlitzSecond = -1;
  let confirmResign = false;
  let confirmResignTimer = null;
  let builtCols = 0;
  let builtRows = 0;
  let slotNodes = []; // 2D array [row][col]
  let headerDropBtns = [];
  let popoutBtns = [];

  container.innerHTML = `
    <div class="game-shell c4-game-shell">
      <!-- Status Bar -->
      <div class="game-statusbar c4-statusbar">
        <div class="c4-badge-group">
          <span class="status-metric status-accent" id="c4-mode-badge">CLASSIC 7×6</span>
          <span class="status-metric hidden" id="c4-blitz-badge">
            <span class="c4-blitz-icon">⚡</span>
            <span id="c4-blitz-timer-text">5.0s</span>
          </span>
        </div>
        <div id="c4-turn-indicator" class="c4-turn-indicator"></div>
        <div class="c4-actions">
          <button type="button" id="c4-rules-btn" class="pill-btn pill-btn-sm">RULES</button>
          <button type="button" id="c4-resign-btn" class="pill-btn pill-btn-sm pill-btn-outline">RESIGN</button>
        </div>
      </div>

      <!-- Blitz Progress Bar -->
      <div id="c4-blitz-progress-bar" class="c4-blitz-progress-bar hidden">
        <div id="c4-blitz-progress-fill" class="c4-blitz-progress-fill"></div>
      </div>

      <!-- Pop Out Mode Alert Banner -->
      <div id="c4-popout-alert" class="c4-popout-alert hidden">
        ⏏ POP OUT ENABLED: Drop a disc from the top OR pop out your own disc from the bottom row!
      </div>

      <!-- Main Board Stage Container -->
      <div class="c4-stage-container" id="c4-stage-container">
        <!-- Top Column Drop Selectors -->
        <div class="c4-col-drop-header" id="c4-col-drop-header"></div>

        <!-- Liquid Glass Cabinet with Circular Cutouts -->
        <div class="c4-board-cabinet" id="c4-board-cabinet">
          <div class="c4-grid-stage" id="c4-grid-stage"></div>
          <!-- Laser Winning Slash Overlay -->
          <svg id="c4-slash-overlay" class="c4-slash-overlay hidden" viewBox="0 0 100 100" preserveAspectRatio="none">
            <line id="c4-slash-line" x1="0" y1="0" x2="0" y2="0" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" />
          </svg>
        </div>

        <!-- Bottom Row Pop-Out Controls -->
        <div class="c4-popout-controls-row hidden" id="c4-popout-controls-row"></div>
      </div>

      <!-- In-board Endgame Banner -->
      <div id="c4-endgame-banner" class="c4-endgame-banner hidden"></div>

      <!-- Rules Modal -->
      <div id="c4-rules-modal" class="c4-rules-modal hidden" role="dialog" aria-modal="true">
        <div class="c4-modal-backdrop" id="c4-modal-backdrop"></div>
        <div class="c4-modal-content">
          <div class="c4-modal-header">
            <h3 class="c4-modal-title">CONNECT 4 RULES & MODES</h3>
            <button type="button" class="c4-modal-close" id="c4-modal-close" aria-label="Close">✕</button>
          </div>
          <div class="c4-modal-body">
            <div>
              <h4>CLASSIC (7×6)</h4>
              <p>Take turns dropping discs into columns. Gravity pulls discs to the lowest open row. First player to connect 4 discs horizontally, vertically, or diagonally wins!</p>
            </div>
            <div>
              <h4>POP OUT MODE</h4>
              <p>On your turn, either drop a disc from the top OR pop out your own disc from the bottom row! When popped, discs above drop down by gravity. If both players achieve 4-in-a-row on the same pop, the match ends in a draw!</p>
            </div>
            <div>
              <h4>5-IN-A-ROW (9×7)</h4>
              <p>Expanded 9 columns by 7 rows board. You must connect 5 discs in a line to win. 4-in-a-row does NOT win!</p>
            </div>
            <div>
              <h4>BLITZ MODE</h4>
              <p>Strict 5-second per-turn countdown. Make your move before time expires or forfeit the match!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  // DOM Elements
  const modeBadgeEl = container.querySelector('#c4-mode-badge');
  const blitzBadgeEl = container.querySelector('#c4-blitz-badge');
  const blitzTimerTextEl = container.querySelector('#c4-blitz-timer-text');
  const turnIndicatorEl = container.querySelector('#c4-turn-indicator');
  const rulesBtn = container.querySelector('#c4-rules-btn');
  const resignBtn = container.querySelector('#c4-resign-btn');
  const blitzProgressBarEl = container.querySelector('#c4-blitz-progress-bar');
  const blitzProgressFillEl = container.querySelector('#c4-blitz-progress-fill');
  const popoutAlertEl = container.querySelector('#c4-popout-alert');
  const colDropHeaderEl = container.querySelector('#c4-col-drop-header');
  const boardCabinetEl = container.querySelector('#c4-board-cabinet');
  const gridStageEl = container.querySelector('#c4-grid-stage');
  const slashOverlayEl = container.querySelector('#c4-slash-overlay');
  const slashLineEl = container.querySelector('#c4-slash-line');
  const popoutControlsRowEl = container.querySelector('#c4-popout-controls-row');
  const endgameBannerEl = container.querySelector('#c4-endgame-banner');
  const rulesModalEl = container.querySelector('#c4-rules-modal');
  const modalCloseBtn = container.querySelector('#c4-modal-close');
  const modalBackdrop = container.querySelector('#c4-modal-backdrop');

  // Rules Modal toggle
  const openRules = () => rulesModalEl.classList.remove('hidden');
  const closeRules = () => rulesModalEl.classList.add('hidden');
  rulesBtn.addEventListener('click', openRules);
  modalCloseBtn.addEventListener('click', closeRules);
  modalBackdrop.addEventListener('click', closeRules);

  // Resign button with two-step confirmation
  const onResignClick = () => {
    if (!confirmResign) {
      confirmResign = true;
      resignBtn.textContent = 'CONFIRM RESIGN?';
      resignBtn.classList.add('status-accent');
      confirmResignTimer = setTimeout(() => {
        confirmResign = false;
        resignBtn.textContent = 'RESIGN';
        resignBtn.classList.remove('status-accent');
      }, 4000);
    } else {
      clearTimeout(confirmResignTimer);
      confirmResign = false;
      resignBtn.textContent = 'RESIGN';
      resignBtn.classList.remove('status-accent');
      sendAction('resign', {});
    }
  };
  resignBtn.addEventListener('click', onResignClick);

  // Column Drop Click
  function triggerDrop(col) {
    if (isAnimating) return;
    if (!lastState || lastState.phase !== 'playing') return;
    const isPassAndPlay = Boolean(lastState.settings?.pass_and_play || lastState.pass_and_play);
    const meId = getPlayerId();
    if (!isPassAndPlay && lastState.turn_player_id !== meId) return;

    if (lastState.board && lastState.board[0] && lastState.board[0][col] !== null) {
      // Column is full
      return;
    }

    sendAction('drop', { col, column: col });
  }

  // Column Pop Click
  function triggerPop(col) {
    if (isAnimating) return;
    if (!lastState || lastState.phase !== 'playing' || lastState.mode !== 'pop_out') return;
    const isPassAndPlay = Boolean(lastState.settings?.pass_and_play || lastState.pass_and_play);
    const meId = getPlayerId();
    const activePid = isPassAndPlay ? lastState.turn_player_id : meId;
    if (!isPassAndPlay && lastState.turn_player_id !== meId) return;

    const bottomRow = (lastState.rows || 6) - 1;
    const bottomDisc = lastState.board?.[bottomRow]?.[col];
    if (bottomDisc !== activePid) return;

    sendAction('pop', { col, column: col });
  }

  // Build / Rebuild Board Grid
  function buildBoard(cols, rows) {
    gridStageEl.innerHTML = '';
    colDropHeaderEl.innerHTML = '';
    popoutControlsRowEl.innerHTML = '';
    slotNodes = [];
    headerDropBtns = [];
    popoutBtns = [];

    gridStageEl.style.setProperty('--c4-cols', cols);
    gridStageEl.style.setProperty('--c4-rows', rows);
    colDropHeaderEl.style.setProperty('--c4-cols', cols);
    popoutControlsRowEl.style.setProperty('--c4-cols', cols);

    // Build Top Drop Header Buttons
    for (let c = 0; c < cols; c++) {
      const dropBtn = document.createElement('button');
      dropBtn.type = 'button';
      dropBtn.className = 'c4-drop-btn';
      dropBtn.dataset.col = String(c);
      dropBtn.setAttribute('aria-label', `Drop in column ${c + 1}`);
      dropBtn.innerHTML = '<span class="c4-drop-arrow">▼</span>';
      dropBtn.addEventListener('click', () => triggerDrop(c));
      colDropHeaderEl.appendChild(dropBtn);
      headerDropBtns.push(dropBtn);
    }

    // Build Grid Slots
    for (let r = 0; r < rows; r++) {
      slotNodes[r] = [];
      for (let c = 0; c < cols; c++) {
        const slot = document.createElement('div');
        slot.className = 'c4-slot';
        slot.dataset.row = String(r);
        slot.dataset.col = String(c);

        // Clicking anywhere in the column attempts a drop
        slot.addEventListener('click', (e) => {
          // If clicking a poppable bottom disc in pop_out mode, trigger pop instead
          if (r === rows - 1 && lastState?.mode === 'pop_out') {
            const discEl = slot.querySelector('.c4-disc.is-poppable');
            if (discEl && (e.target === discEl || discEl.contains(e.target))) {
              triggerPop(c);
              return;
            }
          }
          triggerDrop(c);
        });

        // Column hover preview highlighting
        slot.addEventListener('mouseenter', () => setColumnHover(c, true));
        slot.addEventListener('mouseleave', () => setColumnHover(c, false));

        gridStageEl.appendChild(slot);
        slotNodes[r][c] = slot;
      }
    }

    // Build Bottom Pop-Out Buttons
    for (let c = 0; c < cols; c++) {
      const popBtn = document.createElement('button');
      popBtn.type = 'button';
      popBtn.className = 'c4-pop-col-btn';
      popBtn.dataset.col = String(c);
      popBtn.setAttribute('aria-label', `Pop disc from column ${c + 1}`);
      popBtn.innerHTML = 'POP ⏏';
      popBtn.addEventListener('click', () => triggerPop(c));
      popoutControlsRowEl.appendChild(popBtn);
      popoutBtns.push(popBtn);
    }

    builtCols = cols;
    builtRows = rows;
  }

  function setColumnHover(col, isHovered) {
    if (!lastState || lastState.phase !== 'playing') return;
    if (headerDropBtns[col]) {
      headerDropBtns[col].classList.toggle('is-hovered', isHovered);
    }
    for (let r = 0; r < builtRows; r++) {
      if (slotNodes[r] && slotNodes[r][col]) {
        slotNodes[r][col].classList.toggle('is-col-hovered', isHovered);
      }
    }
  }

  // Draw Laser Winning Line Overlay
  function drawWinningLine(cells, cols, rows, color) {
    if (!cells || cells.length < 2) {
      slashOverlayEl.classList.add('hidden');
      return;
    }
    const sorted = [...cells].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const start = sorted[0];
    const end = sorted[sorted.length - 1];

    const x1 = ((start[1] + 0.5) * (100 / cols)).toFixed(2);
    const y1 = ((start[0] + 0.5) * (100 / rows)).toFixed(2);
    const x2 = ((end[1] + 0.5) * (100 / cols)).toFixed(2);
    const y2 = ((end[0] + 0.5) * (100 / rows)).toFixed(2);

    slashLineEl.setAttribute('x1', `${x1}%`);
    slashLineEl.setAttribute('y1', `${y1}%`);
    slashLineEl.setAttribute('x2', `${x2}%`);
    slashLineEl.setAttribute('y2', `${y2}%`);
    slashLineEl.setAttribute('stroke', color || 'var(--c4-red)');

    slashOverlayEl.classList.remove('hidden');
  }

  // Blitz Timer Animation Loop
  function startBlitzLoop(limit, startedAt) {
    stopBlitzLoop();
    serverTurnStartWall = startedAt;
    clientTurnStartLocal = Date.now() / 1000;
    lastBlitzSecond = -1;

    blitzTimerId = setInterval(() => {
      if (!lastState || lastState.phase !== 'playing' || !limit) {
        stopBlitzLoop();
        return;
      }
      const now = Date.now() / 1000;
      const elapsed = now - clientTurnStartLocal;
      const remaining = Math.max(0, limit - elapsed);

      blitzTimerTextEl.textContent = `${remaining.toFixed(1)}s`;
      const pct = Math.max(0, Math.min(100, (remaining / limit) * 100));
      blitzProgressFillEl.style.width = `${pct}%`;

      if (remaining <= 1.5) {
        blitzProgressFillEl.className = 'c4-blitz-progress-fill is-danger';
      } else if (remaining <= 2.5) {
        blitzProgressFillEl.className = 'c4-blitz-progress-fill is-warning';
      } else {
        blitzProgressFillEl.className = 'c4-blitz-progress-fill';
      }

      // Audio tick countdown on integer seconds <= 3
      const intSec = Math.ceil(remaining);
      if (intSec <= 3 && intSec > 0 && intSec !== lastBlitzSecond) {
        lastBlitzSecond = intSec;
        sound?.tick?.();
      }
    }, 50);
  }

  function stopBlitzLoop() {
    if (blitzTimerId) {
      clearInterval(blitzTimerId);
      blitzTimerId = null;
    }
  }

  return {
    update(publicState, privateState, players = []) {
      if (!publicState) return;

      const prevBoard = lastState?.board;
      const prevPhase = lastPhase;
      lastState = publicState;
      lastPhase = publicState.phase;

      const cols = publicState.cols || 7;
      const rows = publicState.rows || 6;
      const mode = publicState.mode || 'classic';
      const meId = getPlayerId();
      const allPlayers = players.length > 0 ? players : getPlayers();
      const isPassAndPlay = Boolean(publicState.settings?.pass_and_play || publicState.pass_and_play);

      // Identify Player 1 and Player 2
      const p1 = allPlayers[0] ? allPlayers[0].id : 'p1';
      const p2 = allPlayers[1] ? allPlayers[1].id : 'p2';
      const p1Name = allPlayers[0]?.name || 'Player 1';
      const p2Name = allPlayers[1]?.name || 'Player 2';

      // Rebuild board grid if geometry changed
      if (builtCols !== cols || builtRows !== rows) {
        buildBoard(cols, rows);
      }

      // Header Mode Badge
      modeBadgeEl.textContent = MODE_LABELS[mode] || mode.toUpperCase();

      // Blitz Mode UI
      const hasBlitz = mode === 'blitz' || Boolean(publicState.turn_time_limit);
      blitzBadgeEl.classList.toggle('hidden', !hasBlitz);
      blitzProgressBarEl.classList.toggle('hidden', !hasBlitz);

      if (hasBlitz && publicState.phase === 'playing') {
        const limit = publicState.turn_time_limit || 5.0;
        const startedAt = publicState.turn_started_at || Date.now() / 1000;
        if (serverTurnStartWall !== startedAt) {
          startBlitzLoop(limit, startedAt);
        }
      } else {
        stopBlitzLoop();
      }

      // Pop Out Alert Banner
      const isPopOut = mode === 'pop_out';
      popoutAlertEl.classList.toggle('hidden', !isPopOut || publicState.phase !== 'playing');
      popoutControlsRowEl.classList.toggle('hidden', !isPopOut || publicState.phase !== 'playing');

      // Turn Determination & Input Locking
      const turnPid = publicState.turn_player_id;
      const isP1Turn = turnPid === p1;
      const turnColor = isP1Turn ? 'var(--c4-red)' : 'var(--c4-yellow)';
      const turnName = isP1Turn ? p1Name : p2Name;
      const isMyTurn = publicState.phase === 'playing' && (isPassAndPlay || turnPid === meId);
      const isSpectator = !isPassAndPlay && allPlayers.find((p) => p.id === meId)?.role === 'spectator';
      const isAiTurn = !isPassAndPlay && Boolean(allPlayers.find((p) => p.id === turnPid)?.is_bot);

      // Turn Indicator
      if (publicState.phase === 'playing') {
        const turnLabel = isPassAndPlay
          ? `PASS & PLAY: ${escapeHtml(turnName.toUpperCase())} (${isP1Turn ? 'RED' : 'YELLOW'})`
          : isMyTurn
            ? `YOUR TURN (${isP1Turn ? 'RED' : 'YELLOW'})`
            : `WAITING FOR ${escapeHtml(turnName.toUpperCase())}...`;

        turnIndicatorEl.innerHTML = `
          <div class="c4-turn-pill ${isP1Turn ? 'is-red' : 'is-yellow'}">
            <span class="c4-turn-pip"></span>
            <span>${turnLabel}</span>
          </div>
        `;
      } else if (publicState.phase === 'finished') {
        turnIndicatorEl.innerHTML = `
          <div class="c4-turn-pill">
            <span>MATCH CONCLUDED</span>
          </div>
        `;
      } else {
        turnIndicatorEl.innerHTML = '';
      }

      // Detect last move for animation & sound
      const lastMove = publicState.last_move;
      const curMoveSig = lastMove ? `${lastMove.player_id}_${lastMove.action}_${lastMove.row}_${lastMove.col}` : '';
      const isNewMove = Boolean(lastMove && curMoveSig !== lastMoveSig && prevPhase === 'playing');
      if (isNewMove) {
        lastMoveSig = curMoveSig;
        isAnimating = true;
        clearTimeout(animTimer);
        animTimer = setTimeout(() => {
          isAnimating = false;
        }, 380);

        if (lastMove.action === 'drop') {
          sound?.capture?.() || sound?.chessMove?.() || sound?.tick?.();
        } else if (lastMove.action === 'pop') {
          sound?.capture?.();
        }
      }

      // Winning Cells & Double Win Detection
      const rawWinningCells = publicState.winning_cells || publicState.winning_line || [];
      const winningSet = new Set(rawWinningCells.map(([r, c]) => `${r},${c}`));

      // Render Grid Slots
      const board = publicState.board || [];
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const slot = slotNodes[r]?.[c];
          if (!slot) continue;

          const cellVal = board[r]?.[c];
          const isWinning = winningSet.has(`${r},${c}`);
          const isBottomRow = r === rows - 1;
          const isPoppable =
            isPopOut &&
            isBottomRow &&
            Boolean(cellVal) &&
            cellVal === (isPassAndPlay ? turnPid : meId) &&
            isMyTurn &&
            !isAnimating &&
            publicState.phase === 'playing';

          // Check if this slot was the destination of a new drop
          const isJustDropped = isNewMove && lastMove?.action === 'drop' && lastMove.row === r && lastMove.col === c;

          if (cellVal) {
            const isRed = cellVal === p1;
            const discClass = isRed ? 'c4-disc-red' : 'c4-disc-yellow';
            const droppingClass = isJustDropped ? 'is-dropping' : '';
            const winClass = isWinning ? 'is-winning-disc' : '';
            const poppableClass = isPoppable ? 'is-poppable' : '';

            slot.innerHTML = `
              <div class="c4-disc ${discClass} ${droppingClass} ${winClass} ${poppableClass}"
                   style="--drop-row: ${r};"
                   ${isPoppable ? 'title="Click to Pop Out"' : ''}>
                <div class="c4-disc-core">${isPoppable ? '⏏' : ''}</div>
              </div>
            `;
          } else {
            slot.innerHTML = '';
          }
        }
      }

      // Update Column Drop Header Buttons
      for (let c = 0; c < cols; c++) {
        const dropBtn = headerDropBtns[c];
        if (!dropBtn) continue;
        const isFull = board[0] && board[0][c] !== null;
        const isLocked = isFull || !isMyTurn || isAiTurn || isSpectator || isAnimating || publicState.phase !== 'playing';
        dropBtn.disabled = isLocked;
        dropBtn.style.setProperty('--turn-color', turnColor);
      }

      // Update Pop-Out Bottom Controls
      if (isPopOut) {
        const bottomRow = rows - 1;
        const activePid = isPassAndPlay ? turnPid : meId;
        for (let c = 0; c < cols; c++) {
          const popBtn = popoutBtns[c];
          if (!popBtn) continue;
          const bottomDisc = board[bottomRow]?.[c];
          const canPop =
            bottomDisc === activePid &&
            isMyTurn &&
            !isAiTurn &&
            !isSpectator &&
            !isAnimating &&
            publicState.phase === 'playing';

          popBtn.disabled = !canPop;
          popBtn.classList.toggle('is-active-pop', canPop);
          popBtn.classList.toggle('is-red', canPop && activePid === p1);
        }
      }

      // Winning Laser Slash Overlay
      if (publicState.phase === 'finished' && rawWinningCells.length >= (publicState.target_streak || 4)) {
        const winColor = publicState.winner_ids?.[0] === p1 ? 'var(--c4-red)' : 'var(--c4-yellow)';
        drawWinningLine(rawWinningCells, cols, rows, winColor);
      } else {
        slashOverlayEl.classList.add('hidden');
      }

      // In-board Endgame Banner
      if (publicState.phase === 'finished') {
        const winnerIds = publicState.winner_ids || [];
        const isDraw = winnerIds.length === 0;
        const isDoubleWin = isDraw && (publicState.win_reason || '').toLowerCase().includes('double-win');
        const winnerName = winnerIds[0] === p1 ? p1Name : p2Name;
        const reason = publicState.win_reason || (isDraw ? 'Match ended in a draw.' : `${winnerName} won the match!`);

        let title = 'MATCH VICTORY';
        if (isDoubleWin) {
          title = 'SIMULTANEOUS DOUBLE-WIN TIE!';
        } else if (isDraw) {
          title = 'STALEMATE · BOARD FULL';
        }

        endgameBannerEl.className = `c4-endgame-banner ${isDraw ? 'is-draw' : 'is-win'}`;
        endgameBannerEl.innerHTML = `
          <div class="c4-endgame-card">
            <h3 class="c4-endgame-title">${title}</h3>
            <p class="c4-endgame-reason">${escapeHtml(reason)}</p>
          </div>
        `;
        endgameBannerEl.classList.remove('hidden');

        // Play win sound on match conclusion
        if (prevPhase === 'playing') {
          sound?.win?.();
        }
      } else {
        endgameBannerEl.classList.add('hidden');
        endgameBannerEl.innerHTML = '';
      }
    },

    destroy() {
      clearTimeout(confirmResignTimer);
      clearTimeout(animTimer);
      stopBlitzLoop();

      resignBtn.removeEventListener('click', onResignClick);
      rulesBtn.removeEventListener('click', openRules);
      modalCloseBtn.removeEventListener('click', closeRules);
      modalBackdrop.removeEventListener('click', closeRules);

      slotNodes = [];
      headerDropBtns = [];
      popoutBtns = [];

      container.removeAttribute('data-game');
      container.innerHTML = '';
    },
  };
}
