/**
 * Blackout Arcade — Tic-Tac-Toe Frontend Module
 * High-contrast Liquid Glass UI supporting Classic 3x3, Misère 3x3,
 * Extended Grids (4x4 & 5x5), and Ultimate Tic-Tac-Toe (9 nested sub-boards).
 */

import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

const SVG_X = `
  <svg class="ttt-mark-svg ttt-mark-x" viewBox="0 0 64 64" aria-label="X">
    <line x1="16" y1="16" x2="48" y2="48" stroke="currentColor" stroke-width="7" stroke-linecap="round" />
    <line x1="48" y1="16" x2="16" y2="48" stroke="currentColor" stroke-width="7" stroke-linecap="round" />
  </svg>
`;

const SVG_O = `
  <svg class="ttt-mark-svg ttt-mark-o" viewBox="0 0 64 64" aria-label="O">
    <circle cx="32" cy="32" r="18" fill="none" stroke="currentColor" stroke-width="7" />
  </svg>
`;

const SVG_DRAW = `
  <svg class="ttt-mark-svg ttt-mark-draw" viewBox="0 0 64 64" aria-label="Draw">
    <line x1="16" y1="32" x2="48" y2="32" stroke="currentColor" stroke-width="6" stroke-linecap="round" />
  </svg>
`;

const MODE_LABELS = {
  classic: 'CLASSIC 3×3',
  misere: 'MISÈRE 3×3',
  extended_4x4: 'EXTENDED 4×4',
  extended_5x5: 'EXTENDED 5×5',
  ultimate: 'ULTIMATE 9×9',
};

function getModeDimensions(mode) {
  if (mode === 'extended_4x4') return 4;
  if (mode === 'extended_5x5') return 5;
  return 3; // classic, misere, ultimate
}

export function mount(container, context = {}) {
  const { sendAction = () => {}, sound = {}, getPlayerId = () => '', getPlayers = () => [] } = context;

  // Ensure game container has data-game attribute for scoped CSS
  container.setAttribute('data-game', 'tic_tac_toe');

  let lastState = null;
  let lastBoardSignature = '';
  let lastWonSubBoards = new Set();
  let lastPhase = 'pre_game';
  let builtMode = null;
  let builtDim = 0;
  let cellNodes = [];
  let macroBoardNodes = [];
  let subBoardCellNodes = []; // 9 arrays of 9 nodes for ultimate
  let confirmResign = false;
  let confirmResignTimer = null;

  container.innerHTML = `
    <div class="game-shell ttt-game-shell">
      <div class="game-statusbar ttt-statusbar">
        <span class="status-metric status-accent" id="ttt-mode-badge">CLASSIC 3×3</span>
        <div id="ttt-turn-indicator" class="ttt-turn-indicator"></div>
        <span class="status-metric" id="ttt-target-metric"></span>
        <div class="ttt-actions">
          <button type="button" id="ttt-resign-btn" class="pill-btn pill-btn-sm pill-btn-outline">RESIGN</button>
        </div>
      </div>

      <div id="ttt-misere-alert" class="ttt-misere-alert hidden">
        ⚠️ MISÈRE RULES: 3-IN-A-ROW LOSES THE MATCH!
      </div>

      <div class="ttt-board-container" id="ttt-board-container">
        <div id="ttt-board-stage" class="ttt-board-stage"></div>
        <svg id="ttt-slash-overlay" class="ttt-slash-overlay hidden" viewBox="0 0 100 100" preserveAspectRatio="none">
          <line id="ttt-slash-line" x1="0" y1="0" x2="0" y2="0" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
        </svg>
      </div>

      <div id="ttt-endgame-banner" class="ttt-endgame-banner hidden"></div>
    </div>
  `;

  const modeBadgeEl = container.querySelector('#ttt-mode-badge');
  const turnIndicatorEl = container.querySelector('#ttt-turn-indicator');
  const targetMetricEl = container.querySelector('#ttt-target-metric');
  const resignBtn = container.querySelector('#ttt-resign-btn');
  const misereAlertEl = container.querySelector('#ttt-misere-alert');
  const boardStageEl = container.querySelector('#ttt-board-stage');
  const slashOverlayEl = container.querySelector('#ttt-slash-overlay');
  const slashLineEl = container.querySelector('#ttt-slash-line');
  const endgameBannerEl = container.querySelector('#ttt-endgame-banner');

  // Resign interaction with two-step confirmation
  const onResignClick = () => {
    if (!confirmResign) {
      confirmResign = true;
      resignBtn.textContent = 'CONFIRM RESIGN?';
      resignBtn.classList.add('pill-btn-alarm');
      if (sound.click) sound.click();
      confirmResignTimer = setTimeout(() => {
        confirmResign = false;
        resignBtn.textContent = 'RESIGN';
        resignBtn.classList.remove('pill-btn-alarm');
      }, 3500);
      return;
    }
    clearTimeout(confirmResignTimer);
    confirmResign = false;
    resignBtn.textContent = 'RESIGN';
    resignBtn.classList.remove('pill-btn-alarm');
    if (sound.error) sound.error();
    sendAction('resign', {});
  };
  resignBtn.addEventListener('click', onResignClick);

  // Cell click handler for Standard Grids (3x3, 4x4, 5x5)
  const onStandardGridClick = (e) => {
    const btn = e.target.closest('.ttt-cell');
    if (!btn || !lastState) return;
    if (lastState.phase !== 'playing') return;

    const meId = getPlayerId();
    const isPassAndPlay = Boolean(lastState.settings?.pass_and_play || lastState.pass_and_play);
    const isMyTurn = isPassAndPlay || (lastState.turn_player_id === meId);

    if (!isMyTurn) {
      if (sound.error) sound.error();
      return;
    }

    const r = Number(btn.dataset.r);
    const c = Number(btn.dataset.c);
    const idx = Number(btn.dataset.idx);

    // Occupied check
    const cellVal = getStandardCellVal(lastState.board, r, c, idx, builtDim);
    if (cellVal) {
      if (sound.error) sound.error();
      btn.classList.add('ttt-shake');
      setTimeout(() => btn.classList.remove('ttt-shake'), 400);
      return;
    }

    if (sound.chessMove) sound.chessMove();
    sendAction('place_mark', {
      row: r,
      col: c,
      r,
      c,
      cell: idx,
      index: idx,
      player_id: isPassAndPlay ? lastState.turn_player_id : meId,
    });
  };

  // Cell click handler for Ultimate Tic-Tac-Toe
  const onUltimateGridClick = (e) => {
    const btn = e.target.closest('.ttt-sub-cell');
    if (!btn || !lastState) return;
    if (lastState.phase !== 'playing') return;

    const meId = getPlayerId();
    const isPassAndPlay = Boolean(lastState.settings?.pass_and_play || lastState.pass_and_play);
    const isMyTurn = isPassAndPlay || (lastState.turn_player_id === meId);

    if (!isMyTurn) {
      if (sound.error) sound.error();
      return;
    }

    const boardIdx = Number(btn.dataset.boardIdx);
    const cellIdx = Number(btn.dataset.cellIdx);
    const r = Number(btn.dataset.r);
    const c = Number(btn.dataset.c);

    // Validate sub-board target routing
    const targetBoard = lastState.target_board ?? lastState.active_subboard;
    const subBoardWinners = lastState.sub_board_winners || lastState.macro_board || [];
    const isTargetWonOrFull = Boolean(subBoardWinners[targetBoard] && subBoardWinners[targetBoard] !== null);
    const isFreePlacement = targetBoard === null || targetBoard === undefined || targetBoard < 0 || isTargetWonOrFull;

    if (!isFreePlacement && boardIdx !== targetBoard) {
      if (sound.error) sound.error();
      const parentBoard = btn.closest('.ttt-sub-board');
      if (parentBoard) {
        parentBoard.classList.add('ttt-shake');
        setTimeout(() => parentBoard.classList.remove('ttt-shake'), 400);
      }
      return;
    }

    // Check if sub-board is already decided
    if (subBoardWinners[boardIdx]) {
      if (sound.error) sound.error();
      return;
    }

    // Check if cell is occupied
    const cellVal = getUltimateCellVal(lastState.board, boardIdx, cellIdx, r, c);
    if (cellVal) {
      if (sound.error) sound.error();
      btn.classList.add('ttt-shake');
      setTimeout(() => btn.classList.remove('ttt-shake'), 400);
      return;
    }

    if (sound.chessMove) sound.chessMove();
    sendAction('place_mark', {
      subboard: boardIdx,
      macro: boardIdx,
      board_idx: boardIdx,
      row: r,
      col: c,
      r,
      c,
      micro_r: r,
      micro_c: c,
      cell: r * 3 + c,
      cell_idx: cellIdx,
      player_id: isPassAndPlay ? lastState.turn_player_id : meId,
    });
  };

  boardStageEl.addEventListener('click', (e) => {
    if (builtMode === 'ultimate') {
      onUltimateGridClick(e);
    } else {
      onStandardGridClick(e);
    }
  });

  function getStandardCellVal(board, r, c, idx, dim) {
    if (!board) return null;
    if (Array.isArray(board[0])) return board[r]?.[c] ?? null;
    return board[idx] ?? board[r * dim + c] ?? null;
  }

  function getUltimateCellVal(board, boardIdx, cellIdx, r, c) {
    if (!board) return null;
    if (Array.isArray(board[boardIdx])) {
      if (Array.isArray(board[boardIdx][0])) {
        return board[boardIdx][r]?.[c] ?? null;
      }
      return board[boardIdx][cellIdx] ?? null;
    }
    if (Array.isArray(board) && board.length === 81) {
      return board[boardIdx * 9 + cellIdx] ?? null;
    }
    return null;
  }

  function buildStandardGrid(dim) {
    builtMode = 'standard';
    builtDim = dim;
    cellNodes = [];
    macroBoardNodes = [];
    subBoardCellNodes = [];
    boardStageEl.innerHTML = '';
    boardStageEl.className = `ttt-board-stage ttt-grid-${dim}x${dim}`;

    const frag = document.createDocumentFragment();
    for (let r = 0; r < dim; r++) {
      for (let c = 0; c < dim; c++) {
        const idx = r * dim + c;
        const cell = document.createElement('button');
        cell.type = 'button';
        cell.className = 'ttt-cell';
        cell.dataset.r = String(r);
        cell.dataset.c = String(c);
        cell.dataset.idx = String(idx);
        cell.setAttribute('aria-label', `Row ${r + 1}, Column ${c + 1}`);
        frag.appendChild(cell);
        cellNodes.push(cell);
      }
    }
    boardStageEl.appendChild(frag);
  }

  function buildUltimateGrid() {
    builtMode = 'ultimate';
    builtDim = 3;
    cellNodes = [];
    macroBoardNodes = [];
    subBoardCellNodes = [];
    boardStageEl.innerHTML = '';
    boardStageEl.className = 'ttt-board-stage ttt-ultimate-macro-grid';

    const macroFrag = document.createDocumentFragment();
    for (let b = 0; b < 9; b++) {
      const subBoard = document.createElement('div');
      subBoard.className = 'ttt-sub-board';
      subBoard.dataset.boardIdx = String(b);
      subBoard.setAttribute('aria-label', `Sub-board ${b + 1}`);

      const watermark = document.createElement('div');
      watermark.className = 'ttt-sub-board-watermark hidden';
      subBoard.appendChild(watermark);

      const subGrid = document.createElement('div');
      subGrid.className = 'ttt-sub-board-grid';

      const cellArr = [];
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const cellIdx = r * 3 + c;
          const cell = document.createElement('button');
          cell.type = 'button';
          cell.className = 'ttt-sub-cell';
          cell.dataset.boardIdx = String(b);
          cell.dataset.cellIdx = String(cellIdx);
          cell.dataset.r = String(r);
          cell.dataset.c = String(c);
          cell.setAttribute('aria-label', `Sub-board ${b + 1}, Row ${r + 1}, Column ${c + 1}`);
          subGrid.appendChild(cell);
          cellArr.push(cell);
        }
      }
      subBoard.appendChild(subGrid);
      macroFrag.appendChild(subBoard);
      macroBoardNodes.push(subBoard);
      subBoardCellNodes.push(cellArr);
    }
    boardStageEl.appendChild(macroFrag);
  }

  function renderSymbol(val) {
    if (!val) return '';
    const upper = String(val).toUpperCase();
    if (upper === 'X') return SVG_X;
    if (upper === 'O') return SVG_O;
    if (upper === '-' || upper === 'DRAW') return SVG_DRAW;
    return escapeHtml(upper);
  }

  function drawSlashLine(lineCoords, dim) {
    if (!lineCoords || lineCoords.length < 2) {
      slashOverlayEl.classList.add('hidden');
      return;
    }
    let p1 = lineCoords[0];
    let p2 = lineCoords[lineCoords.length - 1];
    let r1, c1, r2, c2;

    if (Array.isArray(p1)) {
      [r1, c1] = p1;
      [r2, c2] = p2;
    } else {
      r1 = Math.floor(p1 / dim);
      c1 = p1 % dim;
      r2 = Math.floor(p2 / dim);
      c2 = p2 % dim;
    }

    const step = 100 / dim;
    const x1 = c1 * step + step / 2;
    const y1 = r1 * step + step / 2;
    const x2 = c2 * step + step / 2;
    const y2 = r2 * step + step / 2;

    slashLineEl.setAttribute('x1', String(x1));
    slashLineEl.setAttribute('y1', String(y1));
    slashLineEl.setAttribute('x2', String(x2));
    slashLineEl.setAttribute('y2', String(y2));
    slashOverlayEl.classList.remove('hidden');
  }

  return {
    update(publicState, privateState, players) {
      lastState = publicState || {};
      const allPlayers = players || getPlayers();
      const activePlayers = getActivePlayers(allPlayers);
      const meId = getPlayerId();
      const me = allPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const isPassAndPlay = Boolean(publicState?.settings?.pass_and_play || publicState?.pass_and_play);

      const mode = String(publicState?.mode || publicState?.settings?.mode || 'classic').toLowerCase();
      const isUltimate = mode === 'ultimate';
      const isMisere = mode === 'misere';
      const dim = getModeDimensions(mode);

      // Mode Badge
      modeBadgeEl.textContent = MODE_LABELS[mode] || mode.toUpperCase();
      misereAlertEl.classList.toggle('hidden', !isMisere);

      // Player symbols mapping
      const p1 = activePlayers[0] || { id: 'p1', name: 'Player 1' };
      const p2 = activePlayers[1] || { id: 'p2', name: 'Player 2' };
      const playerSymbols = publicState?.player_symbols || publicState?.player_marks || {
        [p1.id]: 'X',
        [p2.id]: 'O',
      };

      const turnPlayerId = publicState?.turn_player_id;
      const turnSymbol = playerSymbols[turnPlayerId] || (turnPlayerId === p1.id ? 'X' : 'O');
      const isMyTurn = isPassAndPlay || (!isSpectator && turnPlayerId === meId);

      // Turn Indicator Rendering
      if (publicState?.phase === 'finished') {
        const winnerIds = publicState?.winner_ids || [];
        if (winnerIds.length === 0) {
          turnIndicatorEl.innerHTML = `<span class="ttt-turn-pill is-draw">MATCH DRAW</span>`;
        } else {
          const winnerId = winnerIds[0];
          const winnerPlayer = allPlayers.find((p) => p.id === winnerId);
          const winnerSymbol = playerSymbols[winnerId] || '★';
          const winnerName = winnerPlayer?.name || 'Winner';
          turnIndicatorEl.innerHTML = `
            <span class="ttt-turn-pill is-won ${winnerSymbol === 'X' ? 'is-x' : 'is-o'}">
              VICTORY: ${escapeHtml(winnerName)} (${winnerSymbol})
            </span>
          `;
        }
      } else if (isPassAndPlay) {
        const turnPlayer = allPlayers.find((p) => p.id === turnPlayerId) || (turnSymbol === 'X' ? p1 : p2);
        turnIndicatorEl.innerHTML = `
          <span class="ttt-turn-pill is-pass-play ${turnSymbol === 'X' ? 'is-x' : 'is-o'}">
            PASS & PLAY: ${escapeHtml(turnPlayer.name)}'S TURN (${turnSymbol})
          </span>
        `;
      } else if (isSpectator) {
        const turnPlayer = allPlayers.find((p) => p.id === turnPlayerId) || p1;
        turnIndicatorEl.innerHTML = `
          <span class="ttt-turn-pill is-spectator">
            SPECTATING · ${escapeHtml(turnPlayer.name)}'S TURN (${turnSymbol})
          </span>
        `;
      } else if (isMyTurn) {
        turnIndicatorEl.innerHTML = `
          <span class="ttt-turn-pill is-my-turn ${turnSymbol === 'X' ? 'is-x' : 'is-o'}">
            YOUR TURN (${turnSymbol})
          </span>
        `;
      } else {
        const turnPlayer = allPlayers.find((p) => p.id === turnPlayerId) || p2;
        turnIndicatorEl.innerHTML = `
          <span class="ttt-turn-pill is-rival-turn">
            WAITING FOR ${escapeHtml(turnPlayer.name).toUpperCase()} (${turnSymbol})...
          </span>
        `;
      }

      resignBtn.classList.toggle('hidden', isSpectator || publicState?.phase !== 'playing');

      // Audio cues on state transitions
      const boardStr = JSON.stringify(publicState?.board || '');
      if (lastPhase === 'playing' && publicState?.phase === 'finished') {
        const winnerIds = publicState?.winner_ids || [];
        if (winnerIds.length === 0) {
          if (sound.tick) sound.tick();
        } else if (winnerIds.includes(meId) || isPassAndPlay) {
          if (sound.win) sound.win();
        } else if (!isSpectator) {
          if (sound.error) sound.error();
        }
      }
      lastBoardSignature = boardStr;
      lastPhase = publicState?.phase || 'playing';

      // ==========================================
      // RENDER BOARD MODES
      // ==========================================
      if (isUltimate) {
        if (builtMode !== 'ultimate') {
          buildUltimateGrid();
        }

        const targetBoard = publicState?.target_board ?? publicState?.active_subboard;
        const subBoardWinners = publicState?.sub_board_winners || publicState?.macro_board || [];
        const isTargetWonOrFull = Boolean(subBoardWinners[targetBoard] && subBoardWinners[targetBoard] !== null);
        const isFreePlacement = targetBoard === null || targetBoard === undefined || targetBoard < 0 || isTargetWonOrFull;

        if (isFreePlacement) {
          targetMetricEl.innerHTML = `<span class="status-accent">FREE CHOICE: ANY OPEN BOARD</span>`;
        } else {
          const tr = Math.floor(targetBoard / 3) + 1;
          const tc = (targetBoard % 3) + 1;
          targetMetricEl.innerHTML = `TARGET: <strong>BOARD (${tr}, ${tc})</strong>`;
        }

        // Sub-board conquered detection for sound
        for (let b = 0; b < 9; b++) {
          const winner = subBoardWinners[b];
          if (winner && !lastWonSubBoards.has(b)) {
            lastWonSubBoards.add(b);
            if (sound.capture) sound.capture();
          }
        }

        const macroWinningLine = new Set(publicState?.macro_winning_line || []);

        for (let b = 0; b < 9; b++) {
          const subBoard = macroBoardNodes[b];
          const winner = subBoardWinners[b];
          const isTarget = isFreePlacement ? !winner : b === targetBoard;

          subBoard.classList.toggle('is-target-board', isTarget && publicState?.phase === 'playing');
          subBoard.classList.toggle('is-free-placement', isFreePlacement && !winner && publicState?.phase === 'playing');
          subBoard.classList.toggle('is-inactive-board', !isTarget && publicState?.phase === 'playing');
          subBoard.classList.toggle('is-macro-winner', macroWinningLine.has(b));

          // Watermark overlay
          const watermarkEl = subBoard.querySelector('.ttt-sub-board-watermark');
          if (winner) {
            watermarkEl.className = `ttt-sub-board-watermark watermark-${String(winner).toLowerCase()}`;
            watermarkEl.innerHTML = renderSymbol(winner);
          } else {
            watermarkEl.className = 'ttt-sub-board-watermark hidden';
            watermarkEl.innerHTML = '';
          }

          // Micro cells
          const cells = subBoardCellNodes[b];
          for (let cIdx = 0; cIdx < 9; cIdx++) {
            const cell = cells[cIdx];
            const r = Math.floor(cIdx / 3);
            const c = cIdx % 3;
            const cellVal = getUltimateCellVal(publicState?.board, b, cIdx, r, c);
            const currentSymbol = cell.dataset.symbol || '';

            if (cellVal !== currentSymbol) {
              cell.dataset.symbol = cellVal || '';
              cell.innerHTML = renderSymbol(cellVal);
              cell.classList.toggle('has-mark', Boolean(cellVal));
              cell.classList.toggle('mark-x', cellVal === 'X');
              cell.classList.toggle('mark-o', cellVal === 'O');
            }

            const isLocked = Boolean(winner) || Boolean(cellVal) || !isTarget || !isMyTurn || publicState?.phase !== 'playing';
            cell.disabled = isLocked;
          }
        }

        slashOverlayEl.classList.add('hidden');
      } else {
        // Standard Grids (3x3, 4x4, 5x5)
        if (builtMode !== 'standard' || builtDim !== dim) {
          buildStandardGrid(dim);
        }

        targetMetricEl.innerHTML = isMisere
          ? `<span class="status-accent">3-IN-A-ROW LOSES</span>`
          : dim > 3
          ? `GOAL: <strong>4 IN A ROW</strong>`
          : `GOAL: <strong>3 IN A ROW</strong>`;

        const winningSet = new Set(
          (publicState?.winning_cells || publicState?.winning_line || []).map((coord) =>
            Array.isArray(coord) ? coord[0] * dim + coord[1] : coord
          )
        );

        for (let idx = 0; idx < cellNodes.length; idx++) {
          const cell = cellNodes[idx];
          const r = Math.floor(idx / dim);
          const c = idx % dim;
          const cellVal = getStandardCellVal(publicState?.board, r, c, idx, dim);
          const currentSymbol = cell.dataset.symbol || '';

          if (cellVal !== currentSymbol) {
            cell.dataset.symbol = cellVal || '';
            cell.innerHTML = renderSymbol(cellVal);
            cell.classList.toggle('has-mark', Boolean(cellVal));
            cell.classList.toggle('mark-x', cellVal === 'X');
            cell.classList.toggle('mark-o', cellVal === 'O');
          }

          const isWinCell = winningSet.has(idx);
          cell.classList.toggle('is-winning-cell', isWinCell && !isMisere);
          cell.classList.toggle('is-losing-cell', isWinCell && isMisere);

          const isLocked = Boolean(cellVal) || !isMyTurn || publicState?.phase !== 'playing';
          cell.disabled = isLocked;
        }

        const winLine = publicState?.winning_cells || publicState?.winning_line;
        if (publicState?.phase === 'finished' && winLine && winLine.length >= 3) {
          drawSlashLine(winLine, dim);
        } else {
          slashOverlayEl.classList.add('hidden');
        }
      }

      // In-board Endgame Banner
      if (publicState?.phase === 'finished') {
        const winnerIds = publicState?.winner_ids || [];
        const isDraw = winnerIds.length === 0;
        const reason = publicState?.win_reason || (isDraw ? 'Game ended in a draw.' : 'Match completed.');

        endgameBannerEl.className = `ttt-endgame-banner ${isDraw ? 'is-draw' : 'is-win'}`;
        endgameBannerEl.innerHTML = `
          <div class="ttt-endgame-card">
            <h3 class="ttt-endgame-title">${isDraw ? 'STALEMATE' : 'MATCH VICTORY'}</h3>
            <p class="ttt-endgame-reason">${escapeHtml(reason)}</p>
          </div>
        `;
        endgameBannerEl.classList.remove('hidden');
      } else {
        endgameBannerEl.classList.add('hidden');
        endgameBannerEl.innerHTML = '';
      }
    },

    destroy() {
      clearTimeout(confirmResignTimer);
      resignBtn.removeEventListener('click', onResignClick);
      cellNodes = [];
      macroBoardNodes = [];
      subBoardCellNodes = [];
      lastWonSubBoards.clear();
      container.removeAttribute('data-game');
      container.innerHTML = '';
    },
  };
}
