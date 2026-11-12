import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

const UNO_COLOR_NAMES = {
  red: 'RED',
  blue: 'BLUE',
  green: 'GREEN',
  yellow: 'YELLOW',
};
const VALID_COLORS = new Set(['red', 'blue', 'green', 'yellow', 'wild']);

function safeUnoColor(c) {
  return VALID_COLORS.has(c) ? c : 'red';
}

function cardSymbol(card) {
  if (!card) return '—';
  if (card.kind === 'reverse') return '⇄';
  if (card.kind === 'skip') return '⊘';
  if (card.kind === 'draw2') return '+2';
  if (card.kind === 'wild') return '◈';
  if (card.kind === 'wild4') return '+4';
  return card.label || card.kind || '?';
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let pendingWildIdx = null;
  let lastTurnId = null;

  container.innerHTML = `
    <div class="uno-table">
      <div class="game-statusbar">
        <span class="status-metric">COLOR <span id="uno-color-pill" class="uno-color-badge">—</span></span>
        <span class="status-metric">FLOW <strong id="uno-dir">↻ CLOCKWISE</strong></span>
        <span class="status-metric">DECK <strong id="uno-deck">0</strong></span>
        <span class="status-metric">MODE <strong id="uno-diff">MID</strong></span>
      </div>

      <div id="uno-note" class="uno-action-banner">Waiting for opening play...</div>

      <div id="uno-rivals" class="uno-rivals"></div>

      <div class="uno-center-arena">
        <div class="uno-pile-col">
          <span class="bunker-sublabel uno-pile-label">DRAW DECK</span>
          <button type="button" id="uno-draw-btn" class="uno-card uno-card-back uno-card-lg">
            <span class="uno-back-badge">UNO</span>
            <span class="uno-back-sub" id="uno-draw-sub">DRAW</span>
          </button>
        </div>

        <div class="uno-pile-col">
          <span class="bunker-sublabel uno-pile-label">TOP DISCARD</span>
          <div id="uno-discard-ring" class="uno-discard-ring">
            <div id="uno-discard" class="uno-card uno-card-lg">—</div>
          </div>
        </div>
      </div>

      <div id="uno-drawn-bar" class="uno-prompt-bar hidden">
        <span>Playable card drawn! Click the highlighted card in your hand or keep it.</span>
        <button type="button" id="uno-pass-btn" class="pill-btn pill-btn-sm pill-btn-outline">Keep &amp; Pass Turn</button>
      </div>

      <div id="uno-wild-picker" class="uno-prompt-bar hidden">
        <span class="uno-wild-label">CHOOSE WILD COLOR:</span>
        <div class="uno-wild-swatches">
          <button type="button" class="uno-swatch-btn is-red" data-wild-color="red">RED</button>
          <button type="button" class="uno-swatch-btn is-blue" data-wild-color="blue">BLUE</button>
          <button type="button" class="uno-swatch-btn is-green" data-wild-color="green">GREEN</button>
          <button type="button" class="uno-swatch-btn is-yellow" data-wild-color="yellow">YELLOW</button>
        </div>
        <button type="button" id="uno-wild-cancel" class="pill-btn pill-btn-sm pill-btn-outline">Cancel</button>
      </div>

      <div id="uno-hand-head" class="uno-hand-head">
        <span class="bunker-sublabel uno-hand-title">YOUR HAND (<span id="uno-hand-cnt">0</span>)</span>
        <div class="game-action-row-sm">
          <span id="uno-self-safe" class="uno-self-badge hidden">UNO! SAFE</span>
          <button type="button" id="uno-shout-btn" class="pill-btn pill-btn-md pill-btn-alarm">CALL UNO!</button>
        </div>
      </div>

      <div id="uno-hand" class="uno-hand"></div>
    </div>
  `;

  const colorPill = container.querySelector('#uno-color-pill');
  const dirEl = container.querySelector('#uno-dir');
  const deckEl = container.querySelector('#uno-deck');
  const diffEl = container.querySelector('#uno-diff');
  const noteEl = container.querySelector('#uno-note');
  const rivalsEl = container.querySelector('#uno-rivals');
  const drawBtn = container.querySelector('#uno-draw-btn');
  const drawSub = container.querySelector('#uno-draw-sub');
  const discardRing = container.querySelector('#uno-discard-ring');
  const discardEl = container.querySelector('#uno-discard');
  const drawnBar = container.querySelector('#uno-drawn-bar');
  const passBtn = container.querySelector('#uno-pass-btn');
  const wildPicker = container.querySelector('#uno-wild-picker');
  const wildCancel = container.querySelector('#uno-wild-cancel');
  const handHeadEl = container.querySelector('#uno-hand-head');
  const handCntEl = container.querySelector('#uno-hand-cnt');
  const selfSafeBadge = container.querySelector('#uno-self-safe');
  const shoutBtn = container.querySelector('#uno-shout-btn');
  const handEl = container.querySelector('#uno-hand');

  const onDrawClick = () => {
    pendingWildIdx = null;
    sound.card();
    sendAction('draw', {});
  };
  drawBtn.addEventListener('click', onDrawClick);

  const onPassClick = () => {
    pendingWildIdx = null;
    sound.click();
    sendAction('pass_turn', {});
  };
  passBtn.addEventListener('click', onPassClick);

  const onShoutClick = () => {
    sound.skru();
    sendAction('shout_uno', {});
  };
  shoutBtn.addEventListener('click', onShoutClick);

  const onWildCancel = () => {
    pendingWildIdx = null;
    sound.click();
    wildPicker.classList.add('hidden');
  };
  wildCancel.addEventListener('click', onWildCancel);

  wildPicker.querySelectorAll('[data-wild-color]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (pendingWildIdx === null) return;
      const color = btn.dataset.wildColor;
      const idx = pendingWildIdx;
      pendingWildIdx = null;
      wildPicker.classList.add('hidden');
      sound.card();
      sendAction('play', { index: idx, color });
    });
  });

  function renderCardEl(el, card) {
    if (!card) {
      el.className = 'uno-card uno-card-lg';
      el.innerHTML = '—';
      return;
    }
    const sym = cardSymbol(card);
    const corner = card.label || sym;
    const color = safeUnoColor(card.color);
    el.className = `uno-card uno-card-lg uno-color-${color}`;
    el.innerHTML = `
      <span class="uno-corner top">${escapeHtml(corner)}</span>
      <span class="uno-center-glyph">${escapeHtml(sym)}</span>
      <span class="uno-corner bottom">${escapeHtml(corner)}</span>
    `;
  }

  return {
    update(publicState, privateState, players) {
      const meId = getPlayerId();
      const playerList = players || getPlayers() || [];
      const me = playerList.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const activePlayers = getActivePlayers(playerList);

      const phase = publicState.phase;
      const activeColor = safeUnoColor(publicState.active_color || 'red');
      const isMyTurn = !isSpectator && phase === 'playing' && publicState.turn_player_id === meId;
      const drawnId = privateState?.drawn_playable_id ?? null;

      if (publicState.turn_player_id !== lastTurnId) {
        lastTurnId = publicState.turn_player_id;
        if (!isMyTurn) {
          pendingWildIdx = null;
        }
      }

      colorPill.className = `uno-color-badge is-${activeColor}`;
      colorPill.textContent = UNO_COLOR_NAMES[activeColor] || activeColor.toUpperCase();
      dirEl.textContent = publicState.direction === -1 ? '↺ REVERSE' : '↻ CLOCKWISE';
      deckEl.textContent = String(publicState.deck_count ?? 0);
      diffEl.textContent = String(publicState.difficulty || 'mid').toUpperCase();

      const turnP = activePlayers.find((p) => p.id === publicState.turn_player_id);
      const turnHint = phase === 'finished'
        ? 'Match Finished'
        : isMyTurn
        ? 'YOUR TURN'
        : turnP
        ? `${turnP.name}'s turn`
        : 'Waiting';
      noteEl.textContent = publicState.last_action_note
        ? `${turnHint} — ${publicState.last_action_note}`
        : turnHint;
      noteEl.classList.toggle('is-my-turn', isMyTurn);

      discardRing.className = `uno-discard-ring is-${activeColor}`;
      renderCardEl(discardEl, publicState.discard_top);

      drawBtn.disabled = !(isMyTurn && drawnId === null);
      drawSub.textContent = isMyTurn && drawnId === null ? 'DRAW CARD' : String(publicState.deck_count ?? 0);

      drawnBar.classList.toggle('hidden', !(isMyTurn && drawnId !== null));

      // Rivals row (spectators see all active seats)
      const counts = publicState.card_counts || {};
      const declared = publicState.uno_declared || {};
      const vulnerableSet = new Set(publicState.uno_vulnerable_ids || []);
      const revealedHands = phase === 'finished' ? (publicState.revealed_hands || {}) : {};
      const rivals = isSpectator ? activePlayers : activePlayers.filter((p) => p.id !== meId);

      rivalsEl.innerHTML = '';
      for (const r of rivals) {
        const cnt = Number(counts[r.id] ?? 0);
        const box = document.createElement('div');
        box.className = 'uno-rival-card glass-subcard';
        if (phase === 'playing' && r.id === publicState.turn_player_id) box.classList.add('is-turn');

        let fanHtml = '';
        if (phase === 'finished' && Array.isArray(revealedHands[r.id])) {
          const revCards = revealedHands[r.id];
          if (revCards.length === 0) {
            fanHtml = '<span class="uno-safe-tag">OUT (0 CARDS)</span>';
          } else {
            fanHtml = revCards
              .map((c) => {
                const cCls = ['red', 'blue', 'green', 'yellow'].includes(c.color) ? `is-${c.color}` : '';
                return `<span class="uno-color-badge ${cCls}">${escapeHtml(c.label || cardSymbol(c))}</span>`;
              })
              .join('');
          }
        } else {
          const pips = Array.from({ length: Math.min(cnt, 8) }, () => '<span class="uno-mini-back"></span>').join('');
          const extra = cnt > 8 ? `<span class="uno-extra-cnt">+${cnt - 8}</span>` : '';
          fanHtml = `${pips}${extra}`;
        }

        box.innerHTML = `
          <div class="uno-rival-head">
            <strong>${escapeHtml(r.name)}${r.is_bot ? ' (AI)' : ''}</strong>
            <span class="uno-rival-cnt">${cnt} ${cnt === 1 ? 'CARD' : 'CARDS'}</span>
          </div>
          <div class="uno-mini-fan">${fanHtml}</div>
        `;

        if (phase === 'playing' && cnt === 1 && declared[r.id]) {
          const badge = document.createElement('span');
          badge.className = 'uno-safe-tag';
          badge.textContent = 'UNO! SAFE';
          box.appendChild(badge);
        } else if (!isSpectator && phase === 'playing' && vulnerableSet.has(r.id)) {
          const catchBtn = document.createElement('button');
          catchBtn.type = 'button';
          catchBtn.className = 'pill-btn pill-btn-sm pill-btn-alarm';
          catchBtn.textContent = 'CATCH UNO! (+2)';
          catchBtn.addEventListener('click', () => {
            sound.capture();
            sendAction('catch_uno', { target_id: r.id });
          });
          box.appendChild(catchBtn);
        }

        rivalsEl.appendChild(box);
      }

      // Hand & Wild Picker (hidden controls for spectators)
      const hand = isSpectator ? [] : (privateState?.hand || []);
      const playableSet = new Set(isSpectator ? [] : (privateState?.playable_indices || []));
      handCntEl.textContent = String(hand.length);
      handHeadEl.classList.toggle('hidden', isSpectator);
      shoutBtn.classList.toggle('hidden', isSpectator);
      selfSafeBadge.classList.toggle('hidden', !(!isSpectator && phase === 'playing' && Boolean(declared[meId])));

      const canShout = Boolean(!isSpectator && phase === 'playing' && privateState?.can_shout_uno);
      shoutBtn.disabled = !canShout;
      shoutBtn.classList.toggle('is-ready', canShout);

      if (pendingWildIdx !== null && (!isMyTurn || !hand[pendingWildIdx] || hand[pendingWildIdx].color !== 'wild')) {
        pendingWildIdx = null;
      }
      wildPicker.classList.toggle('hidden', pendingWildIdx === null);

      handEl.innerHTML = '';
      if (isSpectator) {
        handEl.innerHTML = phase === 'finished'
          ? '<p class="empty-ticker-msg">Match finished — all remaining hands revealed above.</p>'
          : '<p class="empty-ticker-msg">Spectator View — watching table cards live.</p>';
        return;
      }
      if (!hand.length && phase === 'finished') {
        handEl.innerHTML = '<p class="empty-ticker-msg">Match finished — you emptied your hand!</p>';
        return;
      }

      hand.forEach((card, idx) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        const isPlayable = isMyTurn && playableSet.has(idx);
        const sym = cardSymbol(card);
        const corner = card.label || sym;
        const color = safeUnoColor(card.color);
        btn.className = `uno-card uno-hand-card uno-color-${color}`;
        if (isPlayable) btn.classList.add('playable');
        else if (isMyTurn) btn.classList.add('unplayable');
        if (pendingWildIdx === idx) btn.classList.add('wild-selected');

        btn.innerHTML = `
          <span class="uno-corner top">${escapeHtml(corner)}</span>
          <span class="uno-center-glyph">${escapeHtml(sym)}</span>
          <span class="uno-corner bottom">${escapeHtml(corner)}</span>
        `;

        btn.disabled = !isPlayable;
        btn.addEventListener('click', () => {
          if (!isPlayable) return;
          if (card.color === 'wild') {
            sound.click();
            pendingWildIdx = idx;
            wildPicker.classList.remove('hidden');
            return;
          }
          pendingWildIdx = null;
          wildPicker.classList.add('hidden');
          sound.card();
          sendAction('play', { index: idx });
        });
        handEl.appendChild(btn);
      });
    },
    destroy() {
      pendingWildIdx = null;
      drawBtn.removeEventListener('click', onDrawClick);
      passBtn.removeEventListener('click', onPassClick);
      shoutBtn.removeEventListener('click', onShoutClick);
      wildCancel.removeEventListener('click', onWildCancel);
    },
  };
}

