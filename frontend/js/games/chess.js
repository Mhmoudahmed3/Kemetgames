import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

const PIECE_SVGS = {
  K: '<path d="M22.5 11.63V6M20 8h5M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/><path d="M11.5 37c5.5 3.5 15.5 3.5 21 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V27v-3.5c-3.5-7.5-13-10.5-16-4-3 6 5 10 5 10V37z"/><path d="M11.5 30c5.5-3 15.5-3 21 0m-21 3.5c5.5-3 15.5-3 21 0m-21 3.5c5.5-3 15.5-3 21 0"/>',
  Q: '<circle cx="6" cy="12" r="2.75"/><circle cx="14" cy="9" r="2.75"/><circle cx="22.5" cy="8" r="2.75"/><circle cx="31" cy="9" r="2.75"/><circle cx="39" cy="12" r="2.75"/><path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15-5.5-14V25L7 14l2 12z"/><path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z"/>',
  R: '<path d="M9 39h27v-3H9v3zM12 36v-4h21v4H12zM11 14V9h4v2h5V9h5v2h5V9h4v5"/><path d="M34 14l-3 3H14l-3-3"/><path d="M31 17v12.5H14V17"/><path d="M31 29.5l1.5 2.5h-20l1.5-2.5"/><path d="M11 14h23"/>',
  B: '<path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.354.49-2.323.47-3-.5 1.354-1.94 3-2 3-2z"/><path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/><circle cx="22.5" cy="8" r="2.5"/><path d="M17.5 26h10M15 30h15m-7.5-14.5v5M20 18h5"/>',
  N: '<path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21"/><path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.042-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3"/>',
  P: '<path d="M22.5 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03-3 1.06-7.41 5.55-7.41 13.47h23c0-7.92-4.41-12.41-7.41-13.47 1.47-1.19 2.41-3 2.41-5.03 0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z"/>',
};

const GLYPHS = {
  K: '♔', Q: '♕', R: '♖', B: '♗', N: '♘', P: '♙',
  k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟',
};

function renderPieceSvg(piece) {
  const safePiece = String(piece || '');
  const isWhite = safePiece === safePiece.toUpperCase();
  const body = PIECE_SVGS[safePiece.toUpperCase()] || '';
  const fill = isWhite ? '#ffffff' : '#141414';
  const stroke = isWhite ? '#000000' : '#ebe4d8';
  return `<svg class="chess-piece-svg" viewBox="0 0 45 45" aria-label="${escapeHtml(safePiece)}"><g fill="${fill}" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</g></svg>`;
}
const FILES = 'abcdefgh';
const RANKS = '87654321';

function formatClock(sec) {
  const s = Math.max(0, Math.floor(sec));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}:${String(rem).padStart(2, '0')}`;
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let selectedSq = null;
  let pendingPromo = null;
  let latestState = {};
  let lastHistoryLen = 0;
  let hasInitialSync = false;
  let lastBoardKey = '';
  let confirmResign = false;
  let confirmResignTimer = null;

  container.innerHTML = `
    <div class="game-shell">
      <div class="chess-layout">
        <div class="chess-board-wrap">
          <div id="ch-clock-top" class="chess-clock-bar">
            <span id="ch-top-name">BLACK</span>
            <span id="ch-top-time" class="chess-clock-time">5:00</span>
          </div>
          <div id="ch-board" class="chess-board"></div>
          <div id="ch-clock-bot" class="chess-clock-bar">
            <span id="ch-bot-name">WHITE</span>
            <span id="ch-bot-time" class="chess-clock-time">5:00</span>
          </div>
        </div>

        <aside class="chess-sidebar">
          <div id="ch-custom-badge" class="chess-editor-status valid ch-custom-badge hidden">
            CUSTOM RULES · Checkmate or capture all rival pieces to win
          </div>
          <div class="bunker-sublabel">CAPTURED PIECES</div>
          <div>
            <div class="ch-tray-label">WHITE CAPTURED</div>
            <div id="ch-cap-w" class="captured-tray"></div>
          </div>
          <div>
            <div class="ch-tray-label">BLACK CAPTURED</div>
            <div id="ch-cap-b" class="captured-tray"></div>
          </div>
          <div class="bunker-sublabel">ALGEBRAIC LOG</div>
          <div id="ch-history" class="move-history-box"></div>
          <button type="button" id="ch-resign-btn" class="pill-btn pill-btn-sm pill-btn-outline">RESIGN MATCH</button>
        </aside>
      </div>

      <div id="ch-promo-modal" class="modal-overlay hidden">
        <div class="modal-box ch-promo-modal-box">
          <h3 class="heading">PROMOTE PAWN</h3>
          <div class="modal-actions" id="ch-promo-choices"></div>
          <button type="button" id="ch-promo-cancel" class="pill-btn pill-btn-sm pill-btn-outline ch-promo-cancel">Cancel</button>
        </div>
      </div>
    </div>
  `;

  const boardEl = container.querySelector('#ch-board');
  const customBadge = container.querySelector('#ch-custom-badge');
  const topBar = container.querySelector('#ch-clock-top');
  const botBar = container.querySelector('#ch-clock-bot');
  const topName = container.querySelector('#ch-top-name');
  const botName = container.querySelector('#ch-bot-name');
  const topTime = container.querySelector('#ch-top-time');
  const botTime = container.querySelector('#ch-bot-time');
  const capW = container.querySelector('#ch-cap-w');
  const capB = container.querySelector('#ch-cap-b');
  const histEl = container.querySelector('#ch-history');
  const resignBtn = container.querySelector('#ch-resign-btn');
  const promoModal = container.querySelector('#ch-promo-modal');
  const promoChoices = container.querySelector('#ch-promo-choices');
  const promoCancel = container.querySelector('#ch-promo-cancel');

  function resetResignConfirm() {
    confirmResign = false;
    clearTimeout(confirmResignTimer);
    confirmResignTimer = null;
    resignBtn.textContent = 'RESIGN MATCH';
    resignBtn.classList.remove('pill-btn-alarm');
    resignBtn.classList.add('pill-btn-outline');
  }

  const onResignClick = () => {
    sound.click();
    if (!confirmResign) {
      confirmResign = true;
      resignBtn.textContent = 'CONFIRM RESIGN?';
      resignBtn.classList.remove('pill-btn-outline');
      resignBtn.classList.add('pill-btn-alarm');
      clearTimeout(confirmResignTimer);
      confirmResignTimer = setTimeout(resetResignConfirm, 4000);
      return;
    }
    resetResignConfirm();
    sendAction('resign', {});
  };
  resignBtn.addEventListener('click', onResignClick);

  const onPromoCancel = () => {
    sound.click();
    pendingPromo = null;
    selectedSq = null;
    promoModal.classList.add('hidden');
    render();
  };
  promoCancel.addEventListener('click', onPromoCancel);

  ['Q', 'R', 'B', 'N'].forEach((piece) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pill-btn pill-btn-md';
    btn.textContent = `${GLYPHS[piece]} ${piece}`;
    btn.addEventListener('click', () => {
      promoModal.classList.add('hidden');
      if (pendingPromo) {
        sendAction('move', { from: pendingPromo.from, to: pendingPromo.to, promotion: piece });
        pendingPromo = null;
        selectedSq = null;
      }
    });
    promoChoices.appendChild(btn);
  });

  function render() {
    const state = latestState;
    const board = state.board || [];
    if (!board.length) return;

    const meId = getPlayerId();
    const players = getPlayers();
    const me = players.find((p) => p.id === meId);
    const isSpectator = Boolean(!me || me.role === 'spectator');
    const colorMap = state.color_map || {};
    const myColor = !isSpectator && colorMap.b === meId ? 'b' : !isSpectator && colorMap.w === meId ? 'w' : null;
    const flipped = myColor === 'b';
    const turn = state.turn || 'w';
    const isMyTurn = Boolean(myColor && myColor === turn && state.phase === 'playing');
    const legalMoves = state.legal_moves || {};
    const activeTargets = selectedSq && isMyTurn ? legalMoves[selectedSq] || [] : [];
    const targetMap = new Map(activeTargets.map((t) => [t.to, t]));

    if (!isMyTurn || state.phase !== 'playing') {
      pendingPromo = null;
      promoModal.classList.add('hidden');
    }

    const activePlayers = getActivePlayers(players);
    const whiteP = activePlayers.find((p) => p.id === colorMap.w) || players.find((p) => p.id === colorMap.w);
    const blackP = activePlayers.find((p) => p.id === colorMap.b) || players.find((p) => p.id === colorMap.b);
    const clocks = state.clocks || { w: 300, b: 300 };

    if (flipped) {
      topName.textContent = `WHITE · ${whiteP?.name || 'White'}`;
      topTime.textContent = formatClock(clocks.w);
      topBar.classList.toggle('active-clock', turn === 'w' && state.phase === 'playing');
      botName.textContent = `BLACK · ${blackP?.name || 'Black'}`;
      botTime.textContent = formatClock(clocks.b);
      botBar.classList.toggle('active-clock', turn === 'b' && state.phase === 'playing');
    } else {
      topName.textContent = `BLACK · ${blackP?.name || 'Black'}`;
      topTime.textContent = formatClock(clocks.b);
      topBar.classList.toggle('active-clock', turn === 'b' && state.phase === 'playing');
      botName.textContent = `WHITE · ${whiteP?.name || 'White'}`;
      botTime.textContent = formatClock(clocks.w);
      botBar.classList.toggle('active-clock', turn === 'w' && state.phase === 'playing');
    }

    customBadge.classList.toggle('hidden', !state.custom_mode);
    const canResign = Boolean(myColor && state.phase === 'playing');
    resignBtn.classList.toggle('hidden', !canResign);
    if (!canResign && confirmResign) resetResignConfirm();

    const boardKey = JSON.stringify({
      board,
      selectedSq: isMyTurn ? selectedSq : null,
      turn,
      flipped,
      phase: state.phase,
      last: state.last_move,
      check: state.in_check_square,
    });

    if (boardKey !== lastBoardKey) {
      lastBoardKey = boardKey;
      boardEl.innerHTML = '';
      const rows = flipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
      const cols = flipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];

      rows.forEach((r, vr) => {
        cols.forEach((c, vc) => {
          const sq = `${FILES[c]}${RANKS[r]}`;
          const cell = document.createElement('div');
          cell.className = `chess-square ${(r + c) % 2 === 0 ? 'light' : 'dark'}`;
          if (isMyTurn && selectedSq === sq) cell.classList.add('selected');
          if (state.last_move && (state.last_move.from === sq || state.last_move.to === sq)) {
            cell.classList.add('last-move');
          }
          if (state.in_check_square === sq) {
            cell.classList.add('in-check');
          }

          if (vc === 0) {
            const rankEl = document.createElement('span');
            rankEl.className = 'ch-coords ch-rank';
            rankEl.textContent = RANKS[r];
            cell.appendChild(rankEl);
          }
          if (vr === 7) {
            const fileEl = document.createElement('span');
            fileEl.className = 'ch-coords ch-file';
            fileEl.textContent = FILES[c];
            cell.appendChild(fileEl);
          }

          const targetInfo = targetMap.get(sq);
          if (targetInfo) {
            const ind = document.createElement('span');
            ind.className = targetInfo.capture ? 'chess-legal-capture' : 'chess-legal-dot';
            cell.appendChild(ind);
          }

          const p = board[r][c];
          if (p) {
            const span = document.createElement('span');
            span.className = 'chess-piece';
            span.innerHTML = renderPieceSvg(p);
            cell.appendChild(span);
          }

          cell.addEventListener('click', () => {
            if (!isMyTurn) return;
            if (selectedSq && targetMap.has(sq)) {
              const mvInfo = targetMap.get(sq);
              if (mvInfo.promo) {
                pendingPromo = { from: selectedSq, to: sq };
                promoModal.classList.remove('hidden');
              } else {
                sendAction('move', { from: selectedSq, to: sq });
                selectedSq = null;
              }
              return;
            }
            if (p && ((myColor === 'w' && p === p.toUpperCase()) || (myColor === 'b' && p === p.toLowerCase()))) {
              selectedSq = selectedSq === sq ? null : sq;
              sound.click();
              render();
            } else if (selectedSq) {
              selectedSq = null;
              render();
            }
          });

          boardEl.appendChild(cell);
        });
      });
    }

    capW.textContent = (state.captured?.w || []).map((p) => GLYPHS[p]).join(' ');
    capB.textContent = (state.captured?.b || []).map((p) => GLYPHS[p]).join(' ');

    const hist = state.move_history || [];
    if (hasInitialSync && hist.length > lastHistoryLen) {
      const lastSan = String(hist[hist.length - 1] || '');
      if (lastSan.includes('x')) sound.capture();
      else sound.chessMove();
    }
    hasInitialSync = true;
    lastHistoryLen = hist.length;
    histEl.innerHTML = '';
    for (let i = 0; i < hist.length; i += 2) {
      const n = document.createElement('span');
      n.textContent = `${i / 2 + 1}.`;
      const w = document.createElement('span');
      w.textContent = hist[i] || '';
      const b = document.createElement('span');
      b.textContent = hist[i + 1] || '';
      histEl.append(n, w, b);
    }
    histEl.scrollTop = histEl.scrollHeight;
  }

  return {
    update(publicState) {
      latestState = publicState || {};
      render();
    },
    destroy() {
      clearTimeout(confirmResignTimer);
      resignBtn.removeEventListener('click', onResignClick);
      promoCancel.removeEventListener('click', onPromoCancel);
    },
  };
}
