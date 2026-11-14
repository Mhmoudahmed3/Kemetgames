/**
 * Blackout Arcade — Playing Cards Frontend Module
 * Server-authoritative Dimension Liquid Glass UI supporting:
 * 1. Blackjack (vs Dealer with Hit, Stand, Double Down, Split, Chips)
 * 2. War (Click-to-flip, Auto-Battle, 3-Card War Fan Pile)
 * 3. Memory / Concentration (3D flip card grid 4x4/6x4, timer, moves counter)
 * 4. High-Low (Higher/Lower guess, multiplier ladder, bank points)
 */

import { escapeHtml } from '/js/utils.js?v=20261112';

// ---------------------------------------------------------------------------
// Pure Vector SVG Card Graphics & Suit Icons
// ---------------------------------------------------------------------------

export const CARD_SUIT_SVGS = {
  hearts: `<svg viewBox="0 0 24 24" class="cards-suit-svg suit-hearts" fill="none"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="#e5484d"/></svg>`,
  diamonds: `<svg viewBox="0 0 24 24" class="cards-suit-svg suit-diamonds" fill="none"><path d="M12 2L21 12L12 22L3 12Z" fill="#f59e0b"/></svg>`,
  spades: `<svg viewBox="0 0 24 24" class="cards-suit-svg suit-spades" fill="none"><path d="M12 2C11 5 6 10 6 14.5C6 17.5 8.5 20 11.5 20C12.5 20 13.5 19.5 14 19C14 20.5 13 22.5 11 23H13C15 22.5 16 20.5 16 19C16.5 19.5 17.5 20 18.5 20C21.5 20 24 17.5 24 14.5C24 10 19 5 18 2C16.5 1 13.5 1 12 2Z" fill="#38bdf8"/></svg>`,
  clubs: `<svg viewBox="0 0 24 24" class="cards-suit-svg suit-clubs" fill="none"><circle cx="12" cy="7.5" r="4.5" fill="#10b981"/><circle cx="7.5" cy="14.5" r="4.5" fill="#10b981"/><circle cx="16.5" cy="14.5" r="4.5" fill="#10b981"/><path d="M10 16H14V22H10Z" fill="#10b981"/><path d="M8 22H16V21C15 20 14 18 12 16C10 18 9 20 8 21V22Z" fill="#10b981"/></svg>`,
};

export const CARD_BACK_SVG = `
  <svg viewBox="0 0 100 140" class="cards-back-svg" fill="none">
    <defs>
      <linearGradient id="cards-holo" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.35"/>
        <stop offset="50%" stop-color="#e5484d" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.35"/>
      </linearGradient>
      <pattern id="cards-lattice" width="12" height="12" patternUnits="userSpaceOnUse">
        <path d="M6 0L12 6L6 12L0 6Z" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="0.8"/>
        <circle cx="6" cy="6" r="1.2" fill="url(#cards-holo)"/>
      </pattern>
    </defs>
    <rect x="2" y="2" width="96" height="136" rx="10" fill="#0d0d12" stroke="rgba(255,255,255,0.18)" stroke-width="1.5"/>
    <rect x="6" y="6" width="88" height="128" rx="8" fill="url(#cards-lattice)"/>
    <rect x="6" y="6" width="88" height="128" rx="8" fill="none" stroke="url(#cards-holo)" stroke-width="1"/>
    <g transform="translate(50, 70)">
      <circle cx="0" cy="0" r="18" fill="#14141a" stroke="url(#cards-holo)" stroke-width="1.5"/>
      <path d="M0 -10 C-1 -6 -6 -2 -6 2 C-6 5 -3 7 0 5 C3 7 6 5 6 2 C6 -2 1 -6 0 -10 Z" fill="url(#cards-holo)"/>
      <path d="M-1 5 H1 V10 H-1 Z" fill="url(#cards-holo)"/>
    </g>
  </svg>
`;

export function renderCardHtml(card, { isFaceUp = true, isHole = false, isMatched = false, extraClasses = '' } = {}) {
  if (!card || isHole || !isFaceUp || card.hidden) {
    return `
      <div class="cards-card-item ${isHole ? 'is-hole-card' : ''} ${extraClasses}" data-face="down">
        <div class="cards-card-inner">
          <div class="cards-card-face cards-card-back">${CARD_BACK_SVG}</div>
        </div>
      </div>
    `;
  }

  const suit = String(card.suit || 'spades').toLowerCase();
  const rank = String(card.rank || 'A').toUpperCase();
  const suitSvg = CARD_SUIT_SVGS[suit] || CARD_SUIT_SVGS.spades;

  let centerArt = '';
  if (rank === 'A') {
    centerArt = `<div class="cards-center-ace">${suitSvg}<div class="cards-ace-aura"></div></div>`;
  } else if (['K', 'Q', 'J'].includes(rank)) {
    centerArt = `<div class="cards-center-face rank-${rank.toLowerCase()}"><span class="cards-face-letter">${rank}</span>${suitSvg}</div>`;
  } else {
    centerArt = `<div class="cards-center-pip">${suitSvg}</div>`;
  }

  return `
    <div class="cards-card-item is-flipped ${isMatched ? 'is-matched' : ''} ${extraClasses}" data-suit="${suit}" data-rank="${rank}" data-id="${escapeHtml(String(card.id || ''))}">
      <div class="cards-card-inner">
        <div class="cards-card-face cards-card-back">${CARD_BACK_SVG}</div>
        <div class="cards-card-face cards-card-front suit-${suit}">
          <div class="cards-card-corner top-left">
            <span class="cards-rank-text">${rank}</span>
            ${suitSvg}
          </div>
          <div class="cards-card-center">${centerArt}</div>
          <div class="cards-card-corner bottom-right">
            <span class="cards-rank-text">${rank}</span>
            ${suitSvg}
          </div>
        </div>
      </div>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Main Component Mount
// ---------------------------------------------------------------------------

export function mount(container, context = {}) {
  const {
    sendAction = () => {},
    sound = {},
    getPlayerId = () => '',
    getPlayers = () => [],
  } = context;

  container.setAttribute('data-game', 'playing_cards');

  let currentMode = 'blackjack';
  let lastPublicState = null;
  let lastPrivateState = null;
  let localBet = 25;
  let selectedChip = 25;
  let timerTicker = null;

  container.innerHTML = `
    <div class="game-shell cards-game-shell">
      <!-- Statusbar & Subgame Selector -->
      <div class="game-statusbar cards-statusbar">
        <div class="cards-mode-switcher" role="tablist">
          <button type="button" class="cards-mode-tab is-active" data-mode="blackjack">🃏 BLACKJACK</button>
          <button type="button" class="cards-mode-tab" data-mode="war">⚔️ WAR</button>
          <button type="button" class="cards-mode-tab" data-mode="memory">🧠 MEMORY</button>
          <button type="button" class="cards-mode-tab" data-mode="high_low">📈 HIGH-LOW</button>
        </div>
        <div class="cards-meta-group">
          <div class="cards-deck-badge" id="cards-deck-badge">
            <span class="cards-deck-icon">🂠</span>
            <span id="cards-deck-count">52 CARDS</span>
          </div>
          <button type="button" id="cards-rules-btn" class="pill-btn pill-btn-sm">RULES</button>
        </div>
      </div>

      <!-- Main Stage Container for Active Subgame -->
      <div id="cards-stage" class="cards-stage"></div>

      <!-- Rules Modal -->
      <div id="cards-rules-modal" class="cards-modal hidden">
        <div class="cards-modal-content">
          <div class="cards-modal-header">
            <h3 id="cards-modal-title">RULES</h3>
            <button type="button" id="cards-modal-close" class="cards-modal-close-btn">&times;</button>
          </div>
          <div id="cards-modal-body" class="cards-modal-body"></div>
        </div>
      </div>
    </div>
  `;

  const stageNode = container.querySelector('#cards-stage');
  const deckCountNode = container.querySelector('#cards-deck-count');
  const modeTabs = container.querySelectorAll('.cards-mode-tab');
  const rulesModal = container.querySelector('#cards-rules-modal');
  const rulesTitle = container.querySelector('#cards-modal-title');
  const rulesBody = container.querySelector('#cards-modal-body');
  const rulesBtn = container.querySelector('#cards-rules-btn');
  const rulesCloseBtn = container.querySelector('#cards-modal-close');

  // Subgame Tab Switching
  modeTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const targetMode = tab.getAttribute('data-mode');
      if (targetMode === currentMode) return;
      currentMode = targetMode;
      updateActiveTab(currentMode);
      sound?.click?.();
      sendAction('switch_mode', { mode: currentMode });
      renderActiveSubgame();
    });
  });

  function updateActiveTab(mode) {
    modeTabs.forEach((t) => {
      if (t.getAttribute('data-mode') === mode) {
        t.classList.add('is-active');
      } else {
        t.classList.remove('is-active');
      }
    });
  }

  // Rules Dialog Handlers
  rulesBtn.addEventListener('click', () => {
    sound?.click?.();
    showRulesModal();
  });
  rulesCloseBtn.addEventListener('click', () => {
    rulesModal.classList.add('hidden');
  });

  function showRulesModal() {
    rulesTitle.textContent = `${currentMode.toUpperCase().replace('_', '-')} RULES`;
    let html = '';
    if (currentMode === 'blackjack') {
      html = `
        <p><strong>Goal:</strong> Get closer to 21 than the Dealer without going over (bust).</p>
        <ul>
          <li><strong>Hit:</strong> Draw an additional card to your hand.</li>
          <li><strong>Stand:</strong> Finish your turn and let the dealer play.</li>
          <li><strong>Double Down:</strong> Double your bet and take exactly one final card.</li>
          <li><strong>Split:</strong> If dealt two matching ranks, split into two independent hands.</li>
          <li><strong>Dealer:</strong> Must hit until total is 17 or higher.</li>
        </ul>
      `;
    } else if (currentMode === 'war') {
      html = `
        <p><strong>Goal:</strong> Capture all 52 cards through high-card battle duels.</p>
        <ul>
          <li><strong>Flip / Battle:</strong> Both players reveal their top card. Higher rank wins (Ace high).</li>
          <li><strong>War Tie:</strong> Equal ranks trigger War! Each places 3 cards face-down and 1 face-up battle card.</li>
          <li><strong>Chained Wars:</strong> Consecutive ties create huge war pots!</li>
          <li><strong>Auto-Battle:</strong> Toggle automatic rapid-fire battles.</li>
        </ul>
      `;
    } else if (currentMode === 'memory') {
      html = `
        <p><strong>Goal:</strong> Uncover and match all pairs of identical ranks on the grid.</p>
        <ul>
          <li>Click any face-down card to flip it face-up.</li>
          <li>Click a second card to test for a match.</li>
          <li>Matching pairs remain face-up. Mismatches flip back after a brief pause.</li>
          <li>Aim for the lowest move count and fastest completion time!</li>
        </ul>
      `;
    } else if (currentMode === 'high_low') {
      html = `
        <p><strong>Goal:</strong> Predict whether the next card will be higher or lower.</p>
        <ul>
          <li><strong>Higher / Lower:</strong> Guess the relative value of the hidden card.</li>
          <li><strong>Streak Multiplier:</strong> Consecutive correct guesses boost the multiplier up to 50x!</li>
          <li><strong>Push:</strong> Equal cards preserve your streak without busting.</li>
          <li><strong>Bank:</strong> Lock in your current score at any time to preserve points.</li>
        </ul>
      `;
    }
    rulesBody.innerHTML = html;
    rulesModal.classList.remove('hidden');
  }

  // -------------------------------------------------------------------------
  // Subgame 1: Blackjack Stage Renderer
  // -------------------------------------------------------------------------

  function renderBlackjack(pub, priv) {
    const myId = getPlayerId();
    const dealerCards = pub.dealer_hand || [];
    const dealerScore = pub.dealer_score !== undefined ? pub.dealer_score : '';
    const myHand = (priv && priv.hand && priv.hand.length > 0)
      ? priv.hand
      : (pub.player_hand || (pub.hands && pub.hands[myId]) || []);

    const splits = (pub.split_hands && pub.split_hands[myId]) || (priv && priv.splits) || [];
    const activeSubIdx = pub.active_hand_indices ? (pub.active_hand_indices[myId] || 0) : 0;
    const chips = (priv && priv.chips !== undefined) ? priv.chips : (pub.chips ? (pub.chips[myId] || 1000) : 1000);
    const bet = (priv && priv.bet !== undefined) ? priv.bet : (pub.bets ? (pub.bets[myId] || localBet) : localBet);

    const isFinished = pub.phase === 'finished';
    const winMsg = pub.win_reason || '';
    const hasWon = pub.winner_ids && pub.winner_ids.includes(myId);

    stageNode.innerHTML = `
      <div class="bj-table">
        <!-- Dealer Zone -->
        <div class="bj-dealer-zone">
          <div class="bj-zone-header">
            <span class="bj-zone-label">DEALER</span>
            <span class="bj-score-pill">${pub.dealer_revealed ? `TOTAL: ${dealerScore}` : (dealerCards.length > 0 ? 'UPCARD SHOWING' : '')}</span>
          </div>
          <div class="cards-hand bj-dealer-hand">
            ${dealerCards.map((c, idx) => {
              const isHole = (!pub.dealer_revealed && idx === 1);
              return renderCardHtml(c, { isHole, isFaceUp: !isHole });
            }).join('')}
          </div>
        </div>

        <!-- Outcome Banner (if finished) -->
        ${isFinished ? `
          <div class="cards-outcome-banner ${hasWon ? 'is-win' : 'is-loss'}">
            <span class="outcome-icon">${hasWon ? '🏆' : '✋'}</span>
            <span class="outcome-text">${escapeHtml(winMsg || (hasWon ? 'YOU WON!' : 'ROUND OVER'))}</span>
            <button type="button" id="bj-rematch-btn" class="pill-btn pill-btn-accent">NEXT ROUND</button>
          </div>
        ` : ''}

        <!-- Player Zone -->
        <div class="bj-player-zone">
          <div class="bj-zone-header">
            <span class="bj-zone-label">YOUR HAND</span>
            <div class="bj-player-stats">
              <span class="bj-stat-pill">BET: $${bet}</span>
              <span class="bj-stat-pill">CHIPS: $${chips}</span>
            </div>
          </div>

          ${splits && splits.length > 1 ? `
            <div class="bj-split-container">
              ${splits.map((subHand, sIdx) => `
                <div class="bj-subhand ${sIdx === activeSubIdx ? 'is-active-hand' : ''}">
                  <div class="bj-subhand-label">HAND ${sIdx + 1} ${sIdx === activeSubIdx ? '(ACTIVE)' : ''}</div>
                  <div class="cards-hand">
                    ${subHand.map(c => renderCardHtml(c, { isFaceUp: true })).join('')}
                  </div>
                </div>
              `).join('')}
            </div>
          ` : `
            <div class="cards-hand bj-player-hand">
              ${myHand.map(c => renderCardHtml(c, { isFaceUp: true })).join('')}
            </div>
          `}
        </div>

        <!-- Action Controls -->
        <div class="bj-controls">
          <button type="button" id="bj-hit-btn" class="pill-btn pill-btn-lg pill-btn-accent" ${isFinished ? 'disabled' : ''}>➕ HIT</button>
          <button type="button" id="bj-stand-btn" class="pill-btn pill-btn-lg pill-btn-outline" ${isFinished ? 'disabled' : ''}>✋ STAND</button>
          <button type="button" id="bj-double-btn" class="pill-btn pill-btn-lg" ${isFinished || myHand.length !== 2 ? 'disabled' : ''}>✖️2 DOUBLE</button>
          <button type="button" id="bj-split-btn" class="pill-btn pill-btn-lg" ${isFinished || myHand.length !== 2 ? 'disabled' : ''}>➗ SPLIT</button>
        </div>

        <!-- Betting Chip Rack -->
        <div class="bj-chips-rack">
          <span class="bj-chips-label">CHIPS:</span>
          ${[5, 25, 50, 100, 500].map(val => `
            <button type="button" class="bj-chip chip-${val} ${selectedChip === val ? 'is-selected' : ''}" data-chip="${val}">
              $${val}
            </button>
          `).join('')}
        </div>
      </div>
    `;

    // Wire Action Handlers
    const hitBtn = stageNode.querySelector('#bj-hit-btn');
    const standBtn = stageNode.querySelector('#bj-stand-btn');
    const doubleBtn = stageNode.querySelector('#bj-double-btn');
    const splitBtn = stageNode.querySelector('#bj-split-btn');
    const rematchBtn = stageNode.querySelector('#bj-rematch-btn');

    if (hitBtn) hitBtn.addEventListener('click', () => { sound?.card?.(); sendAction('hit', {}); });
    if (standBtn) standBtn.addEventListener('click', () => { sound?.click?.(); sendAction('stand', {}); });
    if (doubleBtn) doubleBtn.addEventListener('click', () => { sound?.card?.(); sendAction('double', {}); });
    if (splitBtn) splitBtn.addEventListener('click', () => { sound?.card?.(); sendAction('split', {}); });
    if (rematchBtn) rematchBtn.addEventListener('click', () => { sound?.click?.(); sendAction('switch_mode', { mode: 'blackjack' }); });

    const chipBtns = stageNode.querySelectorAll('.bj-chip');
    chipBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        selectedChip = parseInt(btn.getAttribute('data-chip'), 10);
        localBet = selectedChip;
        sound?.click?.();
        chipBtns.forEach(b => b.classList.remove('is-selected'));
        btn.classList.add('is-selected');
        sendAction('place_bet', { bet: localBet });
      });
    });
  }

  // -------------------------------------------------------------------------
  // Subgame 2: War Stage Renderer
  // -------------------------------------------------------------------------

  function renderWar(pub, priv) {
    const myId = getPlayerId();
    const isFinished = pub.phase === 'finished';
    const inWar = pub.in_war || pub.war_active || false;
    const warPile = pub.war_pile || [];
    const currentCards = pub.current_cards || {};
    const autoBattle = pub.auto_battle || false;

    const pKeys = Object.keys(currentCards);
    const p1Card = currentCards[myId] || (pKeys.length > 0 ? currentCards[pKeys[0]] : null);
    const p2Key = pKeys.find(k => k !== myId) || (pKeys.length > 1 ? pKeys[1] : null);
    const p2Card = p2Key ? currentCards[p2Key] : null;

    const counts = pub.card_counts || pub.player_cards_count || {};
    const myCount = counts[myId] !== undefined ? counts[myId] : 26;
    const oppCount = p2Key && counts[p2Key] !== undefined ? counts[p2Key] : (52 - myCount);

    const hasWon = pub.winner_ids && pub.winner_ids.includes(myId);

    stageNode.innerHTML = `
      <div class="war-container">
        <!-- War Pot Banner if in Tie -->
        ${inWar ? `
          <div class="war-tie-banner">
            <span class="war-tie-spark">⚡</span>
            <span class="war-tie-title">WAR DECLARED! TIE-BREAKER PILE (${warPile.length} CARDS)</span>
            <span class="war-tie-spark">⚡</span>
          </div>
        ` : ''}

        <!-- Outcome Banner -->
        ${isFinished ? `
          <div class="cards-outcome-banner ${hasWon ? 'is-win' : 'is-loss'}">
            <span class="outcome-icon">${hasWon ? '🏆' : '⚔️'}</span>
            <span class="outcome-text">${escapeHtml(pub.win_reason || (hasWon ? 'WAR VICTORY!' : 'DEFEATED'))}</span>
            <button type="button" id="war-rematch-btn" class="pill-btn pill-btn-accent">PLAY AGAIN</button>
          </div>
        ` : ''}

        <!-- Arena Clash -->
        <div class="war-arena">
          <!-- Player Slot -->
          <div class="war-combatant player-side">
            <div class="war-combatant-tag">YOU (${myCount} CARDS)</div>
            <div class="war-card-slot">
              ${p1Card ? renderCardHtml(p1Card, { isFaceUp: true }) : `<div class="war-empty-slot">READY</div>`}
            </div>
          </div>

          <!-- Center Clash Spark -->
          <div class="war-clash-center">
            <span class="war-clash-icon">⚔️</span>
            ${inWar ? `
              <div class="war-pile-fan">
                <div class="war-pile-card">${renderCardHtml(null, { isFaceUp: false })}</div>
                <div class="war-pile-card">${renderCardHtml(null, { isFaceUp: false })}</div>
                <div class="war-pile-card">${renderCardHtml(null, { isFaceUp: false })}</div>
              </div>
            ` : ''}
          </div>

          <!-- Opponent Slot -->
          <div class="war-combatant opp-side">
            <div class="war-combatant-tag">OPPONENT (${oppCount} CARDS)</div>
            <div class="war-card-slot">
              ${p2Card ? renderCardHtml(p2Card, { isFaceUp: true }) : `<div class="war-empty-slot">READY</div>`}
            </div>
          </div>
        </div>

        <!-- Controls -->
        <div class="war-controls">
          <button type="button" id="war-flip-btn" class="pill-btn pill-btn-lg pill-btn-accent" ${isFinished ? 'disabled' : ''}>
            ${inWar ? '⚔️ RESOLVE WAR' : '🃏 FLIP BATTLE CARD'}
          </button>
          <button type="button" id="war-auto-btn" class="pill-btn pill-btn-lg ${autoBattle ? 'is-active pill-btn-glow' : 'pill-btn-outline'}" ${isFinished ? 'disabled' : ''}>
            ${autoBattle ? '⏸️ PAUSE AUTO-BATTLE' : '⚡ AUTO-BATTLE'}
          </button>
        </div>
      </div>
    `;

    const flipBtn = stageNode.querySelector('#war-flip-btn');
    const autoBtn = stageNode.querySelector('#war-auto-btn');
    const rematchBtn = stageNode.querySelector('#war-rematch-btn');

    if (flipBtn) flipBtn.addEventListener('click', () => { sound?.card?.(); sendAction('battle', {}); });
    if (autoBtn) autoBtn.addEventListener('click', () => { sound?.click?.(); sendAction('auto_battle', {}); });
    if (rematchBtn) rematchBtn.addEventListener('click', () => { sound?.click?.(); sendAction('switch_mode', { mode: 'war' }); });
  }

  // -------------------------------------------------------------------------
  // Subgame 3: Memory / Concentration Stage Renderer
  // -------------------------------------------------------------------------

  function renderMemory(pub, priv) {
    const grid = pub.grid || pub.cards || [];
    const matched = new Set(pub.matched_indices || []);
    const flipped = new Set(pub.flipped_indices || []);
    const moves = pub.moves !== undefined ? pub.moves : (pub.moves_count || pub.flips || 0);
    const elapsed = pub.elapsed_time !== undefined ? pub.elapsed_time : (pub.timer || pub.time_elapsed || 0);
    const pairsCount = pub.pairs_count || Math.floor(grid.length / 2) || 8;
    const matchedPairs = pub.matched_pairs !== undefined ? pub.matched_pairs : Math.floor(matched.size / 2);
    const isFinished = pub.phase === 'finished';

    const gridClass = grid.length > 16 ? 'memory-grid-6x4' : 'memory-grid-4x4';

    stageNode.innerHTML = `
      <div class="memory-container">
        <!-- Telemetry Metrics Bar -->
        <div class="memory-stats-bar">
          <span class="memory-stat">MOVES: <strong>${moves}</strong></span>
          <span class="memory-stat">MATCHES: <strong>${matchedPairs} / ${pairsCount}</strong></span>
          <span class="memory-stat">TIME: <strong>${formatTime(elapsed)}</strong></span>
        </div>

        <!-- Outcome Banner -->
        ${isFinished ? `
          <div class="cards-outcome-banner is-win">
            <span class="outcome-icon">🏆</span>
            <span class="outcome-text">ALL PAIRS MATCHED IN ${moves} MOVES (${formatTime(elapsed)})!</span>
            <button type="button" id="mem-rematch-btn" class="pill-btn pill-btn-accent">PLAY AGAIN</button>
          </div>
        ` : ''}

        <!-- 3D Card Grid -->
        <div class="memory-grid ${gridClass}">
          ${grid.map((card, idx) => {
            const isCardMatched = matched.has(idx);
            const isCardFlipped = isCardMatched || flipped.has(idx);
            return `
              <div class="memory-card-wrapper" data-index="${idx}">
                ${renderCardHtml(card, {
                  isFaceUp: isCardFlipped,
                  isMatched: isCardMatched,
                  extraClasses: isCardMatched ? 'is-matched' : ''
                })}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;

    // Click handler for card flipping
    const cardWrappers = stageNode.querySelectorAll('.memory-card-wrapper');
    cardWrappers.forEach((wrapper) => {
      wrapper.addEventListener('click', () => {
        if (isFinished) return;
        const idx = parseInt(wrapper.getAttribute('data-index'), 10);
        if (matched.has(idx) || flipped.has(idx)) return;
        sound?.card?.();
        sendAction('flip', { index: idx, card_index: idx });
      });
    });

    const rematchBtn = stageNode.querySelector('#mem-rematch-btn');
    if (rematchBtn) rematchBtn.addEventListener('click', () => {
      sound?.click?.();
      sendAction('switch_mode', { mode: 'memory' });
    });
  }

  // -------------------------------------------------------------------------
  // Subgame 4: High-Low Stage Renderer
  // -------------------------------------------------------------------------

  function renderHighLow(pub, priv) {
    const currentCard = pub.current_card;
    const nextCard = pub.next_card;
    const streak = pub.streak || 0;
    const maxStreak = pub.max_streak || 0;
    const mult = (pub.multiplier !== undefined) ? pub.multiplier : 1.0;
    const bankedScore = pub.banked_score !== undefined ? pub.banked_score : (pub.score || 0);
    const history = pub.card_history || [];
    const isFinished = pub.phase === 'finished';

    const ladderSteps = [
      { streak: 0, mult: '1.0×' },
      { streak: 1, mult: '1.5×' },
      { streak: 2, mult: '2.0×' },
      { streak: 3, mult: '3.0×' },
      { streak: 4, mult: '5.0×' },
      { streak: 5, mult: '8.0×' },
      { streak: 6, mult: '12.0×' },
      { streak: 7, mult: '18.0×+' },
    ];

    stageNode.innerHTML = `
      <div class="hl-container">
        <!-- Multiplier Ladder -->
        <div class="hl-ladder">
          ${ladderSteps.map((s, idx) => {
            const isActive = (streak === idx || (idx === 7 && streak >= 7));
            return `
              <div class="hl-ladder-step ${isActive ? 'is-active' : ''}">
                <span class="hl-ladder-mult">${s.mult}</span>
                <span class="hl-ladder-label">${s.streak} WINS</span>
              </div>
            `;
          }).join('')}
        </div>

        <!-- Outcome Banner -->
        ${isFinished ? `
          <div class="cards-outcome-banner is-win">
            <span class="outcome-icon">💰</span>
            <span class="outcome-text">FINAL BANKED SCORE: ${bankedScore} PTS!</span>
            <button type="button" id="hl-rematch-btn" class="pill-btn pill-btn-accent">NEW RUN</button>
          </div>
        ` : ''}

        <!-- Cards Display Table -->
        <div class="hl-table">
          <div class="hl-card-slot">
            <span class="hl-slot-label">CURRENT CARD</span>
            ${currentCard ? renderCardHtml(currentCard, { isFaceUp: true }) : `<div class="hl-empty-card">🂠</div>`}
          </div>

          <div class="hl-vs-badge">
            <span class="hl-streak-badge">${streak} STREAK</span>
            <span class="hl-mult-badge">${mult.toFixed(1)}× MULTIPLIER</span>
          </div>

          <div class="hl-card-slot">
            <span class="hl-slot-label">NEXT CARD</span>
            ${nextCard ? renderCardHtml(nextCard, { isFaceUp: true }) : renderCardHtml(null, { isFaceUp: false })}
          </div>
        </div>

        <!-- Guess Controls -->
        <div class="hl-controls">
          <button type="button" id="hl-higher-btn" class="pill-btn pill-btn-lg pill-btn-accent" ${isFinished ? 'disabled' : ''}>
            ⬆️ HIGHER
          </button>
          <button type="button" id="hl-lower-btn" class="pill-btn pill-btn-lg pill-btn-outline" ${isFinished ? 'disabled' : ''}>
            ⬇️ LOWER
          </button>
          <button type="button" id="hl-bank-btn" class="pill-btn pill-btn-lg pill-btn-glow" ${isFinished || streak === 0 ? 'disabled' : ''}>
            💰 BANK (${bankedScore} PTS)
          </button>
        </div>

        <!-- Streak History Ribbon -->
        ${history.length > 1 ? `
          <div class="hl-history-ribbon">
            <span class="hl-history-label">RECENT:</span>
            <div class="hl-history-cards">
              ${history.slice(-8).map(c => `
                <span class="hl-mini-card suit-${c.suit}">${c.label || `${c.rank}${c.symbol || ''}`}</span>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    const higherBtn = stageNode.querySelector('#hl-higher-btn');
    const lowerBtn = stageNode.querySelector('#hl-lower-btn');
    const bankBtn = stageNode.querySelector('#hl-bank-btn');
    const rematchBtn = stageNode.querySelector('#hl-rematch-btn');

    if (higherBtn) higherBtn.addEventListener('click', () => { sound?.card?.(); sendAction('guess', { guess: 'higher' }); });
    if (lowerBtn) lowerBtn.addEventListener('click', () => { sound?.card?.(); sendAction('guess', { guess: 'lower' }); });
    if (bankBtn) bankBtn.addEventListener('click', () => { sound?.win?.(); sendAction('bank', {}); });
    if (rematchBtn) rematchBtn.addEventListener('click', () => { sound?.click?.(); sendAction('switch_mode', { mode: 'high_low' }); });
  }

  // -------------------------------------------------------------------------
  // Subgame Dispatcher
  // -------------------------------------------------------------------------

  function renderActiveSubgame() {
    if (!lastPublicState) return;
    const pub = lastPublicState;
    const priv = lastPrivateState || {};

    if (pub.deck_count !== undefined && deckCountNode) {
      deckCountNode.textContent = `${pub.deck_count} CARDS`;
    }

    if (currentMode === 'blackjack') {
      renderBlackjack(pub, priv);
    } else if (currentMode === 'war') {
      renderWar(pub, priv);
    } else if (currentMode === 'memory') {
      renderMemory(pub, priv);
    } else if (currentMode === 'high_low') {
      renderHighLow(pub, priv);
    }
  }

  function formatTime(sec) {
    const s = Math.floor(sec || 0);
    const m = Math.floor(s / 60);
    const rem = s % 60;
    return `${m.toString().padStart(2, '0')}:${rem.toString().padStart(2, '0')}`;
  }

  // Initialize view
  updateActiveTab(currentMode);

  return {
    update(publicState, privateState, players) {
      lastPublicState = publicState || {};
      lastPrivateState = privateState || {};
      if (lastPublicState.mode && lastPublicState.mode !== currentMode) {
        currentMode = lastPublicState.mode;
        updateActiveTab(currentMode);
      }
      renderActiveSubgame();
    },
    destroy() {
      if (timerTicker) clearInterval(timerTicker);
      container.innerHTML = '';
    },
  };
}
