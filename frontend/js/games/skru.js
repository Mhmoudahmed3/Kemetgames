import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let basraMode = false;
  let blindOwnSlot = null;
  let kingOwnSlot = null;
  let localReady = false;
  let rememberedOwn = {};
  let latestPublic = {};
  let latestPrivate = {};
  let latestPlayers = getPlayers();

  container.innerHTML = `
    <div class="skru-table">
      <div class="game-statusbar">
        <span class="status-metric">STAGE <strong id="sk-stage">—</strong></span>
        <span class="status-metric">DECK <strong id="sk-deck">0</strong></span>
        <span class="status-metric status-accent hidden" id="sk-final-turns"></span>
        <span class="status-metric" id="sk-prompt">WAITING</span>
        <button type="button" id="sk-ready-btn" class="pill-btn pill-btn-md hidden">READY TO START</button>
      </div>

      <div id="sk-opponents" class="skru-opponents"></div>

      <div class="skru-center-pile">
        <div class="skru-pile-col">
          <div class="skru-pile-label">DRAW DECK</div>
          <button type="button" id="sk-draw-btn" class="skru-card selectable">DRAW<br/>DECK</button>
        </div>

        <div class="skru-pile-col">
          <div class="skru-pile-label">TOP DISCARD</div>
          <div id="sk-discard" class="skru-card face-up">—</div>
          <button type="button" id="sk-take-discard" class="pill-btn pill-btn-sm skru-pile-btn">TAKE DISCARD</button>
        </div>

        <div id="sk-drawn-box" class="skru-pile-col hidden">
          <div class="skru-pile-label-accent">DRAWN CARD</div>
          <div id="sk-drawn-card" class="skru-card face-up"></div>
          <button type="button" id="sk-discard-drawn" class="pill-btn pill-btn-sm skru-pile-btn">DISCARD</button>
        </div>

        <div id="sk-king-box" class="skru-king-box hidden">
          <div class="skru-king-title">KING POWER — KAAB DAYER</div>
          <div class="skru-king-cards">
            <div><div class="skru-king-col-label">YOUR CARD</div><div id="sk-king-mine" class="skru-card face-up"></div></div>
            <div><div class="skru-king-col-label">RIVAL CARD</div><div id="sk-king-opp" class="skru-card face-up"></div></div>
          </div>
          <div class="skru-king-actions">
            <button type="button" id="sk-king-swap" class="pill-btn pill-btn-sm">SWAP THEM</button>
            <button type="button" id="sk-king-keep" class="pill-btn pill-btn-sm pill-btn-outline">KEEP AS IS</button>
          </div>
        </div>
      </div>

      <div id="sk-action-row" class="skru-bottom-actions">
        <button type="button" id="sk-basra-btn" class="pill-btn pill-btn-md pill-btn-outline">BASRA TOSS</button>
        <button type="button" id="sk-call-btn" class="pill-btn pill-btn-md pill-btn-alarm">CALL SKRU!</button>
      </div>

      <div id="sk-peek-banner" class="clue-item hidden"></div>

      <div id="sk-my-section">
        <div class="bunker-sublabel">YOUR 2×2 GRID</div>
        <div id="sk-my-grid" class="skru-grid-2x2"></div>
      </div>
    </div>
  `;

  const stageEl = container.querySelector('#sk-stage');
  const deckEl = container.querySelector('#sk-deck');
  const finalTurnsEl = container.querySelector('#sk-final-turns');
  const promptEl = container.querySelector('#sk-prompt');
  const readyBtn = container.querySelector('#sk-ready-btn');
  const oppEl = container.querySelector('#sk-opponents');
  const drawBtn = container.querySelector('#sk-draw-btn');
  const discardEl = container.querySelector('#sk-discard');
  const takeDiscardBtn = container.querySelector('#sk-take-discard');
  const drawnBox = container.querySelector('#sk-drawn-box');
  const drawnCardEl = container.querySelector('#sk-drawn-card');
  const discardDrawnBtn = container.querySelector('#sk-discard-drawn');
  const kingBox = container.querySelector('#sk-king-box');
  const kingMineEl = container.querySelector('#sk-king-mine');
  const kingOppEl = container.querySelector('#sk-king-opp');
  const kingSwapBtn = container.querySelector('#sk-king-swap');
  const kingKeepBtn = container.querySelector('#sk-king-keep');
  const actionRowEl = container.querySelector('#sk-action-row');
  const basraBtn = container.querySelector('#sk-basra-btn');
  const callBtn = container.querySelector('#sk-call-btn');
  const peekBanner = container.querySelector('#sk-peek-banner');
  const mySectionEl = container.querySelector('#sk-my-section');
  const myGrid = container.querySelector('#sk-my-grid');

  readyBtn.addEventListener('click', () => {
    sound.click();
    localReady = true;
    sendAction('ready', {});
    render();
  });
  drawBtn.addEventListener('click', () => {
    sound.card();
    basraMode = false;
    sendAction('draw_deck', {});
  });
  takeDiscardBtn.addEventListener('click', () => {
    sound.card();
    basraMode = false;
    sendAction('take_discard', {});
  });
  discardDrawnBtn.addEventListener('click', () => {
    sound.card();
    sendAction('discard_drawn', {});
  });
  basraBtn.addEventListener('click', () => {
    sound.click();
    basraMode = !basraMode;
    basraBtn.classList.toggle('pill-btn-alarm', basraMode);
    basraBtn.classList.toggle('pill-btn-outline', !basraMode);
    render();
  });
  callBtn.addEventListener('click', () => {
    sound.skru();
    sendAction('skru', {});
  });
  kingSwapBtn.addEventListener('click', () => {
    sound.card();
    sendAction('king_decide', { swap: true });
  });
  kingKeepBtn.addEventListener('click', () => {
    sound.click();
    sendAction('king_decide', { swap: false });
  });

  function renderCardFace(el, card) {
    el.className = 'skru-card face-up';
    if (!card) {
      el.textContent = '—';
      return;
    }
    if (card.code === 'RED_SKRU') el.classList.add('red-skru');
    if (card.code === 'GREEN_SKRU') el.classList.add('green-skru');
    el.innerHTML = `<span class="skru-card-label">${escapeHtml(card.label)}</span><span class="skru-card-pts">(${Number(card.points) || 0} PTS)</span>`;
  }

  function render() {
    const publicState = latestPublic;
    const privateState = latestPrivate;
    const allPlayers = latestPlayers || [];
    const activePlayers = getActivePlayers(allPlayers);
    const meId = getPlayerId();
    const me = allPlayers.find((p) => p.id === meId);
    const isSpectator = Boolean(!me || me.role === 'spectator');

    const phase = publicState.phase;
    const stage = publicState.turn_stage || 'choose_source';
    if (phase !== 'pre_game') {
      localReady = false;
    }
    const isMyTurn = !isSpectator && phase === 'playing' && publicState.turn_player_id === meId;
    const readyList = Array.isArray(publicState.ready_players) ? publicState.ready_players : [];
    const readySet = new Set(readyList);
    if (localReady && phase === 'pre_game' && !isSpectator) readySet.add(meId);

    stageEl.textContent =
      phase === 'pre_game'
        ? `PEEK PHASE (${publicState.pre_game_remaining ?? 0}s)`
        : phase === 'finished'
        ? 'REVEALED'
        : String(stage).toUpperCase();
    deckEl.textContent = String(publicState.deck_count ?? 0);

    if (publicState.skru_caller_id && phase === 'playing') {
      finalTurnsEl.classList.remove('hidden');
      const left = publicState.final_turns_left ?? 0;
      finalTurnsEl.textContent = `SKRU CALLED · ${left} FINAL TURN${left === 1 ? '' : 'S'} LEFT`;
    } else {
      finalTurnsEl.classList.add('hidden');
    }

    const iAmReady = readySet.has(meId);
    readyBtn.classList.toggle('hidden', phase !== 'pre_game' || isSpectator);
    readyBtn.disabled = iAmReady;
    readyBtn.textContent = iAmReady ? 'READY ✓ (WAITING FOR RIVALS)' : 'READY TO START';

    drawBtn.disabled = !(isMyTurn && stage === 'choose_source');
    takeDiscardBtn.disabled = !(isMyTurn && stage === 'choose_source' && publicState.discard_top);
    actionRowEl.classList.toggle('hidden', isSpectator);
    mySectionEl.classList.toggle('hidden', isSpectator);
    basraBtn.disabled = !(isMyTurn && stage === 'choose_source' && publicState.discard_top);
    callBtn.disabled = !(isMyTurn && stage === 'choose_source' && !publicState.skru_caller_id);

    if (!isMyTurn) {
      basraMode = false;
      blindOwnSlot = null;
      kingOwnSlot = null;
      basraBtn.classList.remove('pill-btn-alarm');
      basraBtn.classList.add('pill-btn-outline');
    } else {
      if (stage !== 'power_blind_swap') blindOwnSlot = null;
      if (stage !== 'power_king_peek') kingOwnSlot = null;
    }

    const prompts = {
      choose_source: 'Draw Deck, Take Discard, Basra Toss, or Call SKRU!',
      resolve_drawn: 'Click one of your grid slots to SWAP, or click DISCARD to activate power.',
      choose_swap_discard: 'Click one of your grid slots to swap with the taken discard card.',
      power_peek_self: '7/8 POWER: Click one of YOUR cards to secretly peek.',
      power_peek_opp: '9/10 POWER: Click any unlocked RIVAL card to secretly peek.',
      power_blind_swap:
        blindOwnSlot === null
          ? 'JACK POWER: Click one of YOUR cards first.'
          : 'JACK POWER: Now click an unlocked RIVAL card (or click your selected card to change).',
      power_king_peek:
        kingOwnSlot === null
          ? 'KING POWER: Click one of YOUR cards first.'
          : 'KING POWER: Now click an unlocked RIVAL card (or click your selected card to change).',
      power_king_decide: 'KING POWER: Decide whether to swap the two inspected cards.',
    };
    const turnPlayer = activePlayers.find((p) => p.id === publicState.turn_player_id);
    promptEl.textContent =
      phase === 'pre_game'
        ? isSpectator
          ? `Players are memorizing cards (${readySet.size}/${activePlayers.length} ready)`
          : `Memorize your bottom 2 revealed cards! (${readySet.size}/${activePlayers.length} ready)`
        : phase === 'finished'
        ? 'ROUND FINISHED — ALL HANDS REVEALED'
        : isSpectator
        ? turnPlayer
          ? `SPECTATING · ${turnPlayer.name.toUpperCase()}'S TURN`
          : 'SPECTATING SKRU TABLE'
        : basraMode
        ? 'BASRA MODE: Click your card matching the discard pile!'
        : isMyTurn
        ? prompts[stage] || 'YOUR TURN'
        : turnPlayer
        ? `WAIT FOR ${turnPlayer.name.toUpperCase()}`
        : 'WAIT FOR ACTIVE PLAYER';

    renderCardFace(discardEl, publicState.discard_top);

    const drawnCard = privateState?.drawn_card;
    if (isMyTurn && drawnCard && (stage === 'resolve_drawn' || stage === 'choose_swap_discard')) {
      drawnBox.classList.remove('hidden');
      renderCardFace(drawnCardEl, drawnCard);
      discardDrawnBtn.classList.toggle('hidden', stage !== 'resolve_drawn');
    } else {
      drawnBox.classList.add('hidden');
    }

    const kingView = privateState?.king_view;
    if (isMyTurn && stage === 'power_king_decide' && kingView) {
      kingBox.classList.remove('hidden');
      renderCardFace(kingMineEl, kingView.my_card);
      renderCardFace(kingOppEl, kingView.opp_card);
    } else {
      kingBox.classList.add('hidden');
    }

    // Track pre-game bottom 2 memory & last peek
    const initBottom = privateState?.initial_bottom || {};
    if (phase === 'pre_game') {
      rememberedOwn = { ...initBottom };
    }
    const hands = publicState.hands || {};
    const lp = privateState?.last_peek;
    const lpSlotMissing = lp && hands[lp.owner_id] && hands[lp.owner_id][lp.slot] === null;
    if (!isSpectator && phase === 'playing' && lp && lp.card && !lpSlotMissing) {
      peekBanner.classList.remove('hidden');
      const owner = activePlayers.find((p) => p.id === lp.owner_id);
      peekBanner.textContent = `SECRET PEEK (${owner?.name || 'PLAYER'} SLOT #${Number(lp.slot) + 1}): ${lp.card.label} (${Number(lp.card.points) || 0} PTS)`;
    } else {
      peekBanner.classList.add('hidden');
    }

    // Render Opponents (or all active players if spectator)
    oppEl.innerHTML = '';
    for (const p of activePlayers) {
      if (!isSpectator && p.id === meId) continue;
      const box = document.createElement('div');
      const isLocked = publicState.skru_caller_id === p.id;
      const isOppReady = phase === 'pre_game' && readySet.has(p.id);
      box.className = `skru-seat-box ${publicState.turn_player_id === p.id && phase === 'playing' ? 'is-turn' : ''} ${isLocked ? 'locked-caller' : ''}`;
      const header = document.createElement('div');
      header.innerHTML = `<strong>${escapeHtml(p.name)}</strong>${isOppReady ? ' [READY ✓]' : ''}${isLocked ? ' [SKRU LOCKED]' : ''}`;
      const grid = document.createElement('div');
      grid.className = 'skru-grid-2x2';

      const cards = hands[p.id] || [];
      const canTargetOpp =
        isMyTurn &&
        !isLocked &&
        (stage === 'power_peek_opp' ||
          (stage === 'power_blind_swap' && blindOwnSlot !== null) ||
          (stage === 'power_king_peek' && kingOwnSlot !== null));

      cards.forEach((c, idx) => {
        const cardEl = document.createElement('button');
        cardEl.type = 'button';
        if (c === null) {
          cardEl.className = 'skru-card removed';
          cardEl.textContent = 'EMPTY';
          cardEl.disabled = true;
        } else if (phase === 'finished' && c.label) {
          renderCardFace(cardEl, c);
        } else {
          cardEl.className = `skru-card ${canTargetOpp ? 'selectable' : ''}`;
          cardEl.textContent = `#${idx + 1}`;
          cardEl.disabled = !canTargetOpp;
          if (canTargetOpp) {
            cardEl.addEventListener('click', () => {
              sound.card();
              if (stage === 'power_peek_opp') {
                sendAction('peek', { target_id: p.id, slot: idx });
              } else if (stage === 'power_blind_swap') {
                sendAction('swap', { my_slot: blindOwnSlot, target_id: p.id, opp_slot: idx });
                blindOwnSlot = null;
              } else if (stage === 'power_king_peek') {
                sendAction('peek', { my_slot: kingOwnSlot, target_id: p.id, opp_slot: idx });
                kingOwnSlot = null;
              }
            });
          }
        }
        grid.appendChild(cardEl);
      });
      box.append(header, grid);
      oppEl.appendChild(box);
    }

    // Render My 2x2 Grid (hidden for spectators)
    myGrid.innerHTML = '';
    if (!isSpectator) {
      const myCards = hands[meId] || [];
      myCards.forEach((c, idx) => {
        const el = document.createElement('button');
        el.type = 'button';
        if (c === null) {
          el.className = 'skru-card removed';
          el.textContent = 'EMPTY';
          el.disabled = true;
        } else if (phase === 'finished' && c.label) {
          renderCardFace(el, c);
        } else if (phase === 'pre_game' && rememberedOwn[String(idx)]) {
          renderCardFace(el, rememberedOwn[String(idx)]);
        } else {
          const isSelectedOwn =
            (stage === 'power_blind_swap' && blindOwnSlot === idx) ||
            (stage === 'power_king_peek' && kingOwnSlot === idx);
          const clickable =
            isMyTurn &&
            (basraMode ||
              stage === 'resolve_drawn' ||
              stage === 'choose_swap_discard' ||
              stage === 'power_peek_self' ||
              stage === 'power_blind_swap' ||
              stage === 'power_king_peek');
          el.className = `skru-card ${clickable ? 'selectable' : ''} ${isSelectedOwn ? 'skru-slot-selected' : ''}`;
          el.textContent = `SLOT ${idx + 1}`;
          el.disabled = !clickable;
          if (clickable) {
            el.addEventListener('click', () => {
              sound.card();
              if (basraMode) {
                basraMode = false;
                sendAction('basra', { slot: idx });
              } else if (stage === 'resolve_drawn' || stage === 'choose_swap_discard') {
                sendAction('swap_drawn', { slot: idx });
              } else if (stage === 'power_peek_self') {
                sendAction('peek', { slot: idx });
              } else if (stage === 'power_blind_swap') {
                blindOwnSlot = blindOwnSlot === idx ? null : idx;
                render();
              } else if (stage === 'power_king_peek') {
                kingOwnSlot = kingOwnSlot === idx ? null : idx;
                render();
              }
            });
          }
        }
        myGrid.appendChild(el);
      });
    }
  }

  return {
    update(publicState, privateState, players) {
      latestPublic = publicState || {};
      latestPrivate = privateState || {};
      latestPlayers = players || getPlayers();
      render();
    },
    destroy() {},
  };
}

