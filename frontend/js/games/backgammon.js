import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

function renderCheckerGroup(cls, count) {
  if (!count) return '';
  const shown = Math.min(count, 5);
  let html = '<div class="game-action-row-sm">';
  for (let i = 0; i < shown; i++) {
    html += `<span class="bg-checker-mini ${cls}"></span>`;
  }
  if (count > 5) html += `<span class="bg-bar-muted">+${count - 5}</span>`;
  html += '</div>';
  return html;
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let selectedFrom = null;
  let pendingChoice = null;
  let latestState = {};

  container.innerHTML = `
    <div class="game-shell">
      <div class="game-statusbar">
        <span class="status-metric status-accent" id="bg-mode-badge">CLASSIC</span>
        <span class="status-metric">DICE <strong id="bg-dice">—</strong></span>
        <span class="status-metric">REMAINING <strong id="bg-rem">—</strong></span>
        <span class="status-metric" id="bg-note">READY TO ROLL</span>
        <span class="status-metric" id="bg-legend"></span>
        <button type="button" id="bg-roll-btn" class="pill-btn pill-btn-md">ROLL 2D6</button>
      </div>
      <div id="bg-die-choice" class="game-action-row hidden"></div>
      <div id="bg-board" class="bg-board"></div>
    </div>
  `;

  const modeBadgeEl = container.querySelector('#bg-mode-badge');
  const diceEl = container.querySelector('#bg-dice');
  const remEl = container.querySelector('#bg-rem');
  const noteEl = container.querySelector('#bg-note');
  const legendEl = container.querySelector('#bg-legend');
  const rollBtn = container.querySelector('#bg-roll-btn');
  const dieChoiceEl = container.querySelector('#bg-die-choice');
  const boardEl = container.querySelector('#bg-board');

  const onRollClick = () => {
    sound.dice();
    selectedFrom = null;
    pendingChoice = null;
    sendAction('roll', {});
  };
  rollBtn.addEventListener('click', onRollClick);

  function renderPoint(idx, isTop, points, pinned, selectableSet, targetSet, legal) {
    const pt = document.createElement('div');
    pt.className = `bg-point ${isTop ? 'top' : 'bottom'} ${idx % 2 === 0 ? 'even' : 'odd'}`;
    if (selectableSet.has(idx)) pt.classList.add('selectable');
    if (targetSet.has(idx)) pt.classList.add('target-valid');

    const num = document.createElement('span');
    num.className = 'bg-point-num';
    num.textContent = String(idx + 1);
    pt.appendChild(num);

    const pinVal = (pinned && pinned[idx]) || 0;
    if (pinVal !== 0) {
      const pch = document.createElement('span');
      pch.className = `bg-checker ${pinVal > 0 ? 'p0' : 'p1'} pinned`;
      pch.title = 'Imprisoned / Pinned checker (Mahbosa)';
      pch.textContent = '🔒';
      pt.appendChild(pch);
    }

    const val = points[idx] || 0;
    const count = Math.abs(val);
    const cls = val > 0 ? 'p0' : 'p1';
    const shown = Math.min(count, 5);
    for (let i = 0; i < shown; i++) {
      const ch = document.createElement('span');
      ch.className = `bg-checker ${cls}`;
      if (i === shown - 1 && count > 5) ch.textContent = String(count);
      pt.appendChild(ch);
    }

    pt.addEventListener('click', () => onSquareClick(idx, selectableSet, targetSet, legal));
    return pt;
  }

  function renderDieChoice() {
    if (!pendingChoice) {
      dieChoiceEl.classList.add('hidden');
      dieChoiceEl.innerHTML = '';
      return;
    }
    dieChoiceEl.classList.remove('hidden');
    dieChoiceEl.innerHTML = '';
    const lbl = document.createElement('span');
    lbl.className = 'game-sub-label';
    lbl.textContent = 'CHOOSE DIE FOR MOVE:';
    dieChoiceEl.appendChild(lbl);

    for (const d of pendingChoice.dice) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pill-btn pill-btn-sm';
      btn.textContent = `DIE ${d}`;
      btn.addEventListener('click', () => {
        sound.chessMove();
        const { from, to } = pendingChoice;
        pendingChoice = null;
        selectedFrom = null;
        sendAction('move', { from, to, die: d });
      });
      dieChoiceEl.appendChild(btn);
    }

    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'pill-btn pill-btn-sm pill-btn-outline';
    cancel.textContent = 'Cancel';
    cancel.addEventListener('click', () => {
      sound.click();
      pendingChoice = null;
      render();
    });
    dieChoiceEl.appendChild(cancel);
  }

  function onSquareClick(coord, selectableSet, targetSet, legal) {
    const meId = getPlayerId();
    const me = getPlayers().find((p) => p.id === meId);
    if (!me || me.role === 'spectator') return;
    if (latestState.turn_player_id !== meId || latestState.subphase !== 'move') return;

    if (selectedFrom !== null && targetSet.has(coord)) {
      const matches = legal.filter((m) => m.from === selectedFrom && m.to === coord);
      const uniqueDice = [...new Set(matches.map((m) => m.die).filter((d) => d !== undefined && d !== null))];
      if (uniqueDice.length > 1) {
        sound.click();
        pendingChoice = { from: selectedFrom, to: coord, dice: uniqueDice };
        renderDieChoice();
        return;
      }
      sound.chessMove();
      const payload = { from: selectedFrom, to: coord };
      if (uniqueDice.length === 1) payload.die = uniqueDice[0];
      sendAction('move', payload);
      selectedFrom = null;
      pendingChoice = null;
      return;
    }

    pendingChoice = null;
    if (selectableSet.has(coord)) {
      sound.click();
      selectedFrom = selectedFrom === coord ? null : coord;
      render();
    } else if (selectedFrom !== null) {
      selectedFrom = null;
      render();
    }
  }

  function render() {
    const state = latestState;
    const points = state.points || [];
    if (!points.length) return;
    const pinned = state.pinned || [];
    const mode = state.mode || 'classic';
    const modeNames = { classic: 'FRANJIEH', tawla_31: 'TAWLA 31', mahbosa: 'MAHBOSA' };
    if (modeBadgeEl) modeBadgeEl.textContent = modeNames[mode] || 'CLASSIC';

    const allPlayers = getPlayers();
    const activePlayers = getActivePlayers(allPlayers);
    const meId = getPlayerId();
    const me = allPlayers.find((p) => p.id === meId);
    const isSpectator = Boolean(!me || me.role === 'spectator');
    const isMyTurn = !isSpectator && state.turn_player_id === meId && state.phase === 'playing';

    const p0Name = activePlayers[0]?.name || 'Cream';
    const p1Name = activePlayers[1]?.name || 'Red';
    if (legendEl) {
      legendEl.innerHTML = `<span class="bg-checker-mini p0"></span> ${escapeHtml(p0Name)} · <span class="bg-checker-mini p1"></span> ${escapeHtml(p1Name)}`;
    }

    const shownDice = (state.dice && state.dice.length) ? state.dice : (state.last_dice || []);
    diceEl.textContent = shownDice.length ? `[${shownDice.join(', ')}]` : '—';
    remEl.textContent = (state.remaining_dice || []).length ? state.remaining_dice.join(', ') : '—';
    noteEl.textContent = state.last_roll_note || 'ROLL TO START';

    rollBtn.classList.toggle('hidden', isSpectator);
    rollBtn.disabled = !(isMyTurn && state.subphase === 'roll');

    const legal = isMyTurn && state.subphase === 'move' ? state.legal_moves || [] : [];
    const selectableSet = new Set(legal.map((m) => m.from));
    if (selectedFrom !== null && !selectableSet.has(selectedFrom)) {
      selectedFrom = null;
      pendingChoice = null;
    }
    if (!isMyTurn || state.subphase !== 'move') {
      pendingChoice = null;
    }
    const targetSet = new Set(
      selectedFrom !== null ? legal.filter((m) => m.from === selectedFrom).map((m) => m.to) : []
    );
    renderDieChoice();

    const topLeft = [12, 13, 14, 15, 16, 17];
    const topRight = [18, 19, 20, 21, 22, 23];
    const botLeft = [11, 10, 9, 8, 7, 6];
    const botRight = [5, 4, 3, 2, 1, 0];

    boardEl.innerHTML = '';

    const leftCol = document.createElement('div');
    leftCol.className = 'bg-quadrant-col';
    const tlRow = document.createElement('div');
    tlRow.className = 'bg-row';
    topLeft.forEach((idx) => tlRow.appendChild(renderPoint(idx, true, points, pinned, selectableSet, targetSet, legal)));
    const blRow = document.createElement('div');
    blRow.className = 'bg-row';
    botLeft.forEach((idx) => blRow.appendChild(renderPoint(idx, false, points, pinned, selectableSet, targetSet, legal)));
    leftCol.append(tlRow, blRow);

    // Central Bar
    const barEl = document.createElement('div');
    barEl.className = 'bg-bar';
    barEl.classList.toggle('is-selectable', selectableSet.has('bar'));
    const barP1 = Number(state.bar?.['1']) || 0;
    const barP0 = Number(state.bar?.['0']) || 0;
    if (mode === 'tawla_31') {
      barEl.innerHTML = `<div class="bg-bar-muted">31<br/>NO BAR</div>`;
    } else if (mode === 'mahbosa') {
      barEl.innerHTML = `<div class="bg-bar-muted">MAHBOSA<br/>🔒 PINS</div>`;
    } else {
      barEl.innerHTML = `
        <div class="bg-bar-text">BAR<br/>RED: ${barP1}${renderCheckerGroup('p1', barP1)}</div>
        <div class="bg-bar-text">CREAM: ${barP0}${renderCheckerGroup('p0', barP0)}</div>
      `;
    }
    barEl.addEventListener('click', () => onSquareClick('bar', selectableSet, targetSet, legal));

    const rightCol = document.createElement('div');
    rightCol.className = 'bg-quadrant-col';
    const trRow = document.createElement('div');
    trRow.className = 'bg-row';
    topRight.forEach((idx) => trRow.appendChild(renderPoint(idx, true, points, pinned, selectableSet, targetSet, legal)));
    const brRow = document.createElement('div');
    brRow.className = 'bg-row';
    botRight.forEach((idx) => brRow.appendChild(renderPoint(idx, false, points, pinned, selectableSet, targetSet, legal)));
    rightCol.append(trRow, brRow);

    // Bearing-Off Tray
    const offEl = document.createElement('div');
    offEl.className = 'bg-off-tray';
    if (targetSet.has('off')) offEl.classList.add('target-valid');
    const offP1 = Number(state.off?.['1']) || 0;
    const offP0 = Number(state.off?.['0']) || 0;
    offEl.innerHTML = `
      <div class="bg-off-text">OFF<br/>${escapeHtml(p1Name)}<br/>${offP1}/15${renderCheckerGroup('p1', offP1)}</div>
      <div class="bg-off-text">${escapeHtml(p0Name)}<br/>${offP0}/15${renderCheckerGroup('p0', offP0)}<br/>BEAR OFF</div>
    `;
    offEl.addEventListener('click', () => onSquareClick('off', selectableSet, targetSet, legal));

    boardEl.append(leftCol, barEl, rightCol, offEl);
  }

  return {
    update(publicState) {
      latestState = publicState || {};
      render();
    },
    destroy() {
      rollBtn.removeEventListener('click', onRollClick);
    },
  };
}

