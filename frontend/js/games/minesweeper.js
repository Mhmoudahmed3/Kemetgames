import { getActivePlayers } from '/js/utils.js?v=20261112';

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let flagMode = false;
  let lastStatus = 'playing';
  let builtRows = 0;
  let builtCols = 0;
  let cellNodes = [];
  let latestLocked = false;
  let latestRevealedMap = new Map();

  container.innerHTML = `
    <div class="game-shell">
      <div class="game-statusbar">
        <span class="status-metric">MINES LEFT <strong id="ms-mines">0</strong></span>
        <span class="status-metric">PROGRESS <strong id="ms-pct">0%</strong></span>
        <span class="status-metric">TIME <strong id="ms-time">0.0s</strong></span>
        <span class="status-metric">STATUS <strong id="ms-status">ACTIVE</strong></span>
        <button type="button" id="ms-flag-toggle" class="pill-btn pill-btn-sm pill-btn-outline">MODE: REVEAL</button>
      </div>
      <div class="ms-layout">
        <div id="ms-progress-strip" class="ms-progress-strip"></div>
        <div class="ms-grid-scroll">
          <div id="ms-grid" class="ms-grid"></div>
        </div>
      </div>
    </div>
  `;

  const minesEl = container.querySelector('#ms-mines');
  const pctEl = container.querySelector('#ms-pct');
  const timeEl = container.querySelector('#ms-time');
  const statusEl = container.querySelector('#ms-status');
  const flagToggle = container.querySelector('#ms-flag-toggle');
  const progressStrip = container.querySelector('#ms-progress-strip');
  const gridEl = container.querySelector('#ms-grid');

  const onToggleFlag = () => {
    sound.click();
    flagMode = !flagMode;
    flagToggle.textContent = flagMode ? 'MODE: FLAG' : 'MODE: REVEAL';
    flagToggle.classList.toggle('pill-btn-alarm', flagMode);
    flagToggle.classList.toggle('pill-btn-outline', !flagMode);
  };
  flagToggle.addEventListener('click', onToggleFlag);

  const onGridClick = (e) => {
    if (latestLocked) return;
    const cell = e.target.closest('.ms-cell');
    if (!cell) return;
    const r = Number(cell.dataset.r);
    const c = Number(cell.dataset.c);
    const key = `${r},${c}`;
    if (latestRevealedMap.has(key)) {
      if (latestRevealedMap.get(key) > 0) {
        sound.click();
        sendAction('chord', { r, c });
      }
      return;
    }
    sound.click();
    sendAction(flagMode ? 'flag' : 'reveal', { r, c });
  };

  const onGridContextMenu = (e) => {
    const cell = e.target.closest('.ms-cell');
    if (!cell) return;
    e.preventDefault();
    if (latestLocked) return;
    const r = Number(cell.dataset.r);
    const c = Number(cell.dataset.c);
    const key = `${r},${c}`;
    if (!latestRevealedMap.has(key)) {
      sound.click();
      sendAction('flag', { r, c });
    }
  };

  gridEl.addEventListener('click', onGridClick);
  gridEl.addEventListener('contextmenu', onGridContextMenu);

  function ensureGrid(rows, cols) {
    gridEl.style.setProperty('--ms-cols', String(cols));
    if (rows === builtRows && cols === builtCols && cellNodes.length === rows * cols) {
      return;
    }
    builtRows = rows;
    builtCols = cols;
    cellNodes = [];
    gridEl.innerHTML = '';
    const frag = document.createDocumentFragment();
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cell = document.createElement('button');
        cell.type = 'button';
        cell.className = 'ms-cell';
        cell.dataset.r = String(r);
        cell.dataset.c = String(c);
        cell.setAttribute('aria-label', `Row ${r + 1}, Column ${c + 1}`);
        frag.appendChild(cell);
        cellNodes.push(cell);
      }
    }
    gridEl.appendChild(frag);
  }

  return {
    update(publicState, privateState, players) {
      const rows = publicState.rows || 9;
      const cols = publicState.cols || 9;
      const totalMines = publicState.total_mines || 10;
      const progress = publicState.progress || {};
      const allPlayers = players || getPlayers();
      const meId = getPlayerId();
      const me = allPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const myProg = progress[meId] || { progress_pct: 0, flags_used: 0, status: 'playing', elapsed: 0 };
      const priv = privateState || {};

      flagToggle.classList.toggle('hidden', isSpectator);
      minesEl.textContent = isSpectator
        ? String(totalMines)
        : String(Math.max(0, totalMines - (priv.flagged?.length || 0)));
      pctEl.textContent = isSpectator ? '—' : `${myProg.progress_pct || 0}%`;
      timeEl.textContent = `${Number(myProg.elapsed || 0).toFixed(1)}s`;
      statusEl.textContent = isSpectator
        ? 'SPECTATING'
        : String(priv.status || myProg.status || 'playing').toUpperCase();

      if (!isSpectator && priv.status === 'exploded' && lastStatus !== 'exploded') {
        sound.capture();
      }
      lastStatus = priv.status || 'playing';

      // Progress bars for active human players (exclude spectators)
      const activePlayers = getActivePlayers(allPlayers);
      progressStrip.innerHTML = '';
      for (const p of activePlayers) {
        const pr = progress[p.id] || { progress_pct: 0, status: 'playing', elapsed: 0 };
        const row = document.createElement('div');
        row.className = 'ms-progress-row';
        const label = document.createElement('span');
        label.className = 'ms-progress-label';
        const st = String(pr.status || 'playing').toUpperCase();
        const elapsedStr = `${Number(pr.elapsed || 0).toFixed(1)}s`;
        label.textContent = `${p.name} (${st} · ${elapsedStr})`;
        const track = document.createElement('div');
        track.className = 'ms-bar-track';
        const fill = document.createElement('div');
        fill.className = 'ms-bar-fill';
        const pctVal = Math.max(0, Math.min(100, Number(pr.progress_pct) || 0));
        fill.style.width = `${pctVal}%`;
        track.appendChild(fill);
        const pct = document.createElement('span');
        pct.textContent = `${pctVal}%`;
        row.append(label, track, pct);
        progressStrip.appendChild(row);
      }

      // Build board lookup maps
      const revealedMap = new Map();
      for (const [r, c, val] of priv.revealed || []) {
        revealedMap.set(`${r},${c}`, val);
      }
      latestRevealedMap = revealedMap;
      const flaggedSet = new Set((priv.flagged || []).map(([r, c]) => `${r},${c}`));
      const mineSet = new Set((priv.mines || []).map(([r, c]) => `${r},${c}`));

      latestLocked =
        isSpectator ||
        publicState.phase !== 'playing' ||
        Boolean(priv.status && priv.status !== 'playing');

      ensureGrid(rows, cols);

      let idx = 0;
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const cell = cellNodes[idx++];
          const key = `${r},${c}`;
          let nextClass = 'ms-cell';
          let nextText = '';

          if (mineSet.has(key)) {
            if (flaggedSet.has(key)) {
              nextClass = 'ms-cell flagged';
              nextText = '⚑';
            } else {
              nextClass = 'ms-cell mine';
              nextText = '✸';
            }
          } else if (revealedMap.has(key)) {
            const val = revealedMap.get(key);
            nextClass = val > 0 ? `ms-cell revealed ms-num-${val}` : 'ms-cell revealed';
            nextText = val > 0 ? String(val) : '';
          } else if (flaggedSet.has(key)) {
            nextClass = 'ms-cell flagged';
            nextText = latestLocked && mineSet.size > 0 ? '✕' : '⚑';
          }

          if (cell.className !== nextClass) cell.className = nextClass;
          if (cell.textContent !== nextText) cell.textContent = nextText;
          if (cell.disabled !== latestLocked) cell.disabled = latestLocked;
        }
      }
    },
    destroy() {
      flagToggle.removeEventListener('click', onToggleFlag);
      gridEl.removeEventListener('click', onGridClick);
      gridEl.removeEventListener('contextmenu', onGridContextMenu);
      cellNodes = [];
    },
  };
}

