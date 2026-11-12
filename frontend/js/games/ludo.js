import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

const SAFE_COORDS = new Set([
  '6,1', '2,6', '1,8', '6,12', '8,13', '12,8', '13,6', '8,2',
]);
const COLOR_LABELS = ['RED', 'GREEN', 'YELLOW', 'BLUE'];

function cellClass(r, c) {
  if (r < 6 && c < 6) return 'ludo-yard-0';
  if (r < 6 && c > 8) return 'ludo-yard-1';
  if (r > 8 && c > 8) return 'ludo-yard-2';
  if (r > 8 && c < 6) return 'ludo-yard-3';
  if (r >= 6 && r <= 8 && c >= 6 && c <= 8) return 'ludo-center';
  if (r === 7 && c >= 1 && c <= 5) return 'ludo-home-0';
  if (c === 7 && r >= 1 && r <= 5) return 'ludo-home-1';
  if (r === 7 && c >= 9 && c <= 13) return 'ludo-home-2';
  if (c === 7 && r >= 9 && r <= 13) return 'ludo-home-3';
  if (SAFE_COORDS.has(`${r},${c}`)) return 'ludo-safe';
  return '';
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let hopTimer = null;
  let hasInitialSync = false;
  let lastHopSig = '';
  let activeHopPath = [];
  let currentHopIdx = -1;
  let cellMap = new Map();

  container.innerHTML = `
    <div class="game-shell">
      <div class="game-statusbar">
        <span class="status-metric">DIE <strong id="lu-die">—</strong></span>
        <span class="status-metric">SIXES STREAK <strong id="lu-six">0/3</strong></span>
        <span class="status-metric" id="lu-turn-note">WAITING</span>
        <button type="button" id="lu-roll-btn" class="pill-btn pill-btn-md">ROLL DIE</button>
      </div>
      <div class="ludo-layout">
        <div id="lu-board" class="ludo-board"></div>
        <div class="rival-panel">
          <div class="bunker-sublabel">PLAYER SEATS</div>
          <div id="lu-seats"></div>
        </div>
      </div>
    </div>
  `;

  const dieEl = container.querySelector('#lu-die');
  const sixEl = container.querySelector('#lu-six');
  const noteEl = container.querySelector('#lu-turn-note');
  const rollBtn = container.querySelector('#lu-roll-btn');
  const boardEl = container.querySelector('#lu-board');
  const seatsEl = container.querySelector('#lu-seats');

  const onRollClick = () => {
    sound.dice();
    sendAction('roll', {});
  };
  rollBtn.addEventListener('click', onRollClick);

  function applyHopHighlight() {
    cellMap.forEach((cell) => cell.classList.remove('ludo-hop-active'));
    if (currentHopIdx >= 0 && currentHopIdx < activeHopPath.length) {
      const [hr, hc] = activeHopPath[currentHopIdx];
      const cell = cellMap.get(`${hr},${hc}`);
      if (cell) cell.classList.add('ludo-hop-active');
    }
  }

  function startHopAnimation(path) {
    if (hopTimer) {
      clearInterval(hopTimer);
      hopTimer = null;
    }
    activeHopPath = path;
    currentHopIdx = 0;
    applyHopHighlight();
    hopTimer = setInterval(() => {
      currentHopIdx += 1;
      if (currentHopIdx >= activeHopPath.length) {
        clearInterval(hopTimer);
        hopTimer = null;
        activeHopPath = [];
        currentHopIdx = -1;
        applyHopHighlight();
        return;
      }
      applyHopHighlight();
    }, 80);
  }

  return {
    update(publicState, _privateState, players) {
      const meId = getPlayerId();
      const allPlayers = players || getPlayers();
      const me = allPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const activePlayers = getActivePlayers(allPlayers);

      const isMyTurn = !isSpectator && publicState.turn_player_id === meId && publicState.phase === 'playing';
      const sub = publicState.subphase;
      dieEl.textContent = publicState.dice_value ? String(publicState.dice_value) : '—';
      sixEl.textContent = `${publicState.consecutive_sixes || 0}/3`;
      rollBtn.classList.toggle('hidden', isSpectator);
      rollBtn.disabled = !(isMyTurn && sub === 'roll');

      const turnPlayer = activePlayers.find((p) => p.id === publicState.turn_player_id);
      noteEl.textContent = isMyTurn
        ? sub === 'roll'
          ? 'YOUR TURN — ROLL DIE'
          : 'SELECT HIGHLIGHTED TOKEN'
        : `${turnPlayer?.name || 'RIVAL'}'S TURN`;

      const seatColors = publicState.seat_colors || {};
      const tokens = publicState.tokens || {};
      const movable = new Set(isMyTurn && sub === 'move' ? publicState.movable_tokens || [] : []);

      // Index active players' tokens by grid cell
      const cellTokens = new Map();
      for (const p of activePlayers) {
        const cIdx = seatColors[p.id] ?? 0;
        const list = tokens[p.id] || [];
        list.forEach((tk, idx) => {
          const [r, c] = tk.coord || [7, 7];
          const key = `${r},${c}`;
          if (!cellTokens.has(key)) cellTokens.set(key, []);
          cellTokens.get(key).push({
            pid: p.id,
            cIdx,
            idx,
            isMovable: !isSpectator && p.id === meId && movable.has(idx),
          });
        });
      }

      boardEl.innerHTML = '';
      cellMap = new Map();
      for (let r = 0; r < 15; r++) {
        for (let c = 0; c < 15; c++) {
          const cell = document.createElement('div');
          const cls = cellClass(r, c);
          cell.className = `ludo-cell ${cls}`;
          const list = cellTokens.get(`${r},${c}`) || [];
          if (r === 7 && c === 7 && list.length === 0) cell.textContent = '★';

          if (list.length) {
            const sorted = [...list].sort((a, b) => Number(b.isMovable) - Number(a.isMovable));
            if (sorted.length === 1) {
              const item = sorted[0];
              const tok = document.createElement('span');
              tok.className = `ludo-token color-${item.cIdx}`;
              if (item.isMovable) {
                tok.classList.add('movable');
                tok.addEventListener('click', () => {
                  sound.chessMove();
                  sendAction('move', { token: item.idx });
                });
              }
              tok.textContent = String(item.idx + 1);
              cell.appendChild(tok);
            } else {
              cell.classList.add('is-stacked');
              sorted.slice(0, 4).forEach((item) => {
                const tok = document.createElement('span');
                tok.className = `ludo-token color-${item.cIdx}`;
                if (item.isMovable) {
                  tok.classList.add('movable');
                  tok.addEventListener('click', () => {
                    sound.chessMove();
                    sendAction('move', { token: item.idx });
                  });
                }
                tok.textContent = String(item.idx + 1);
                cell.appendChild(tok);
              });
              if (sorted.length > 4) {
                const badge = document.createElement('span');
                badge.className = 'ludo-overflow-badge';
                badge.textContent = `+${sorted.length - 4}`;
                cell.appendChild(badge);
              }
            }
          }
          cellMap.set(`${r},${c}`, cell);
          boardEl.appendChild(cell);
        }
      }

      const hopPath = Array.isArray(publicState.last_hop_path) ? publicState.last_hop_path : [];
      const hopSig = `${JSON.stringify(tokens)}|${JSON.stringify(hopPath)}`;
      if (hopSig !== lastHopSig) {
        lastHopSig = hopSig;
        if (hasInitialSync && hopPath.length > 0) {
          startHopAnimation(hopPath);
        }
      } else {
        applyHopHighlight();
      }
      hasInitialSync = true;

      seatsEl.innerHTML = '';
      for (const p of activePlayers) {
        const cIdx = seatColors[p.id] ?? 0;
        const homeCount = (tokens[p.id] || []).filter((t) => t.rel === 56).length;
        const row = document.createElement('div');
        row.className = 'rival-row';
        row.classList.toggle('is-turn', publicState.turn_player_id === p.id);
        row.innerHTML = `<span>${COLOR_LABELS[cIdx] || 'SEAT'} · ${escapeHtml(p.name)}</span><span>${homeCount}/4 HOME</span>`;
        seatsEl.appendChild(row);
      }
    },
    destroy() {
      if (hopTimer) {
        clearInterval(hopTimer);
        hopTimer = null;
      }
      rollBtn.removeEventListener('click', onRollClick);
    },
  };
}
