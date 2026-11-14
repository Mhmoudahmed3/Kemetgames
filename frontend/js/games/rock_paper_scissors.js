/**
 * Blackout Arcade — Rock-Paper-Scissors Frontend Module
 * Server-authoritative Liquid Glass UI supporting Classic 3-Choice and
 * RPS-Lizard-Spock (5-Choice) across Best-of-3, Best-of-5, and Endless Streak formats.
 *
 * Features:
 * - Pure vector SVGs for all 5 hands (Rock, Paper, Scissors, Lizard, Spock)
 * - Animated 3-2-1 countdown reveal with Web Audio sound synthesis
 * - Secrecy curtain for local pass-and-play
 * - Interactive Liquid Glass pentagram SVG rule chart modal
 * - Responsive HUD with streak flame counters and score pips
 */

import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

// Vector Hand SVG graphics
export const RPS_ICONS = {
  rock: `
    <svg class="rps-hand-svg" viewBox="0 0 64 64" fill="none" aria-label="Rock">
      <path d="M22 26V16C22 13.8 23.8 12 26 12C28.2 12 30 13.8 30 16V22M30 20C30 17.8 31.8 16 34 16C36.2 16 38 17.8 38 20V24M38 22C38 19.8 39.8 18 42 18C44.2 18 46 19.8 46 22V28M46 26C46 23.8 47.8 22 50 22C52.2 22 54 23.8 54 26V40C54 48.8 46.8 56 38 56H30C21.2 56 14 48.8 14 40V34C14 31.8 15.8 30 18 30C20.2 30 22 31.8 22 34V26Z" 
            fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M18 36H36M22 42H38M22 48H36" stroke="rgba(0,0,0,0.3)" stroke-width="2" stroke-linecap="round"/>
    </svg>
  `,
  paper: `
    <svg class="rps-hand-svg" viewBox="0 0 64 64" fill="none" aria-label="Paper">
      <path d="M18 32V18C18 15.8 19.8 14 22 14C24.2 14 26 15.8 26 18V28M26 16C26 13.8 27.8 12 30 12C32.2 12 34 13.8 34 16V28M34 16C34 13.8 35.8 12 38 12C40.2 12 42 13.8 42 16V28M42 20C42 17.8 43.8 16 46 16C48.2 16 50 17.8 50 20V36C50 47 41 56 30 56H26C16 56 8 48 8 38V34C8 31.8 9.8 30 12 30C14.2 30 16 31.8 16 34V32" 
            fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5" stroke-linejoin="round"/>
    </svg>
  `,
  scissors: `
    <svg class="rps-hand-svg" viewBox="0 0 64 64" fill="none" aria-label="Scissors">
      <path d="M22 14C22 11.8 23.8 10 26 10C28.2 10 30 11.8 30 14V30M30 14C30 11.8 31.8 10 34 10C36.2 10 38 11.8 38 14V30M38 32C38 30 39.8 28 42 28C44.2 28 46 30 46 32V38M46 34C46 32 47.8 30 50 30C52.2 30 54 32 54 34V42C54 50 46 56 38 56H30C22 56 16 50 16 42V38C16 36 17.8 34 20 34C22.2 34 24 36 24 38V32" 
            fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M26 12L34 28M34 12L26 28" stroke="rgba(0,0,0,0.25)" stroke-width="2"/>
    </svg>
  `,
  lizard: `
    <svg class="rps-hand-svg" viewBox="0 0 64 64" fill="none" aria-label="Lizard">
      <path d="M12 36C12 30 18 24 26 24H38C46 24 54 30 54 36C54 40 48 42 38 42H28C22 42 12 40 12 36Z" fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5"/>
      <path d="M16 40C16 46 22 52 30 52H40C46 52 50 48 50 44C50 42 46 42 40 42H26C20 42 16 40 16 40Z" fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5"/>
      <circle cx="44" cy="30" r="3" fill="#000"/>
      <circle cx="45" cy="29" r="1" fill="#fff"/>
    </svg>
  `,
  spock: `
    <svg class="rps-hand-svg" viewBox="0 0 64 64" fill="none" aria-label="Spock">
      <path d="M18 28V16C18 13.8 19.8 12 22 12C24.2 12 26 13.8 26 16V28M26 18C26 15.8 27.8 14 30 14C32.2 14 34 15.8 34 18V28M38 18C38 15.8 39.8 14 42 14C44.2 14 46 15.8 46 18V28M46 20C46 17.8 47.8 16 50 16C52.2 16 54 17.8 54 20V36C54 48 44 56 34 56H30C20 56 12 48 12 38V32C12 30 13.8 28 16 28C18.2 28 20 30 20 32" 
            fill="currentColor" stroke="var(--color-snow-white)" stroke-width="2.5" stroke-linejoin="round"/>
    </svg>
  `,
  fist_left: `
    <svg class="rps-countdown-fist-svg" viewBox="0 0 64 64" fill="none">
      <path d="M10 32C10 24 16 20 26 20H42C48 20 54 26 54 32C54 38 48 44 42 44H26C16 44 10 40 10 32Z" fill="var(--accent)" stroke="#fff" stroke-width="2.5"/>
      <path d="M24 22V42M32 20V44M40 22V42" stroke="rgba(0,0,0,0.3)" stroke-width="2"/>
    </svg>
  `,
  fist_right: `
    <svg class="rps-countdown-fist-svg" viewBox="0 0 64 64" fill="none" transform="scale(-1, 1) translate(-64, 0)">
      <path d="M10 32C10 24 16 20 26 20H42C48 20 54 26 54 32C54 38 48 44 42 44H26C16 44 10 40 10 32Z" fill="var(--color-ash)" stroke="#fff" stroke-width="2.5"/>
      <path d="M24 22V42M32 20V44M40 22V42" stroke="rgba(0,0,0,0.3)" stroke-width="2"/>
    </svg>
  `,
};

const CLASSIC_KEYS = ['rock', 'paper', 'scissors'];
const LIZARD_SPOCK_KEYS = ['rock', 'paper', 'scissors', 'lizard', 'spock'];

const BEATS = {
  rock: ['scissors', 'lizard'],
  paper: ['rock', 'spock'],
  scissors: ['paper', 'lizard'],
  lizard: ['spock', 'paper'],
  spock: ['scissors', 'rock'],
};

const RELATIONSHIP_DESCRIPTIONS = {
  rock: 'Crushes ✌️ Scissors & 🦎 Lizard. Defeated by ✋ Paper & 🖖 Spock.',
  paper: 'Covers ✊ Rock & Disproves 🖖 Spock. Defeated by ✌️ Scissors & 🦎 Lizard.',
  scissors: 'Cuts ✋ Paper & Decapitates 🦎 Lizard. Defeated by ✊ Rock & 🖖 Spock.',
  lizard: 'Poisons 🖖 Spock & Eats ✋ Paper. Defeated by ✊ Rock & ✌️ Scissors.',
  spock: 'Smashes ✌️ Scissors & Vaporizes ✊ Rock. Defeated by ✋ Paper & 🦎 Lizard.',
};

export function mount(container, context = {}) {
  const {
    sendAction = () => {},
    sound = {},
    getPlayerId = () => '',
    getPlayers = () => [],
  } = context;

  container.setAttribute('data-game', 'rock_paper_scissors');

  // Internal state
  let currentPublicState = null;
  let currentPrivateState = null;
  let allPlayers = [];
  let isCountingDown = false;
  let countdownTimer = null;
  let autoDismissTimer = null;
  let confirmResign = false;
  let confirmResignTimer = null;
  let lastRevealedRound = 0;
  let selectedChoice = null;

  // Local Pass-and-Play tracking
  let pnpP1Choice = null;
  let pnpCurrentTurn = 1; // 1 = P1 choosing, 2 = P2 choosing

  container.innerHTML = `
    <div class="game-shell rps-game-shell">
      <!-- Statusbar & Header -->
      <div class="game-statusbar rps-statusbar">
        <div class="rps-badge-group">
          <span class="status-metric status-accent" id="rps-mode-badge">CLASSIC 3-CHOICE</span>
          <span class="status-metric" id="rps-format-badge">BEST OF 3</span>
          <span class="status-metric" id="rps-round-badge">ROUND 1</span>
        </div>

        <div id="rps-scoreboard" class="rps-scoreboard"></div>

        <div class="rps-actions">
          <button type="button" id="rps-rules-btn" class="pill-btn pill-btn-sm">RULES CHART</button>
          <button type="button" id="rps-resign-btn" class="pill-btn pill-btn-sm pill-btn-outline">RESIGN</button>
        </div>
      </div>

      <!-- Turn & Rival Status Strip -->
      <div id="rps-status-strip" class="rps-status-strip">
        <div id="rps-player-status" class="rps-status-chip">CHOOSE YOUR WEAPON</div>
        <div id="rps-rival-status" class="rps-status-chip is-waiting">RIVAL CHOOSING...</div>
      </div>

      <!-- Main Interactive Arena -->
      <div class="rps-arena" id="rps-arena">
        <!-- View A: Choice Buttons Grid -->
        <div id="rps-choice-grid" class="rps-choice-grid"></div>

        <!-- View B: Animated 3-2-1 Countdown Overlay -->
        <div id="rps-countdown-overlay" class="rps-countdown-overlay hidden">
          <div class="rps-countdown-fists">
            <div class="rps-fist rps-fist-left" id="rps-fist-left">${RPS_ICONS.fist_left}</div>
            <div class="rps-countdown-number" id="rps-countdown-number">3</div>
            <div class="rps-fist rps-fist-right" id="rps-fist-right">${RPS_ICONS.fist_right}</div>
          </div>
          <div class="rps-countdown-label">SHOOT!</div>
        </div>

        <!-- View C: Hand Reveal Stage -->
        <div id="rps-reveal-stage" class="rps-reveal-stage hidden">
          <div class="rps-fighter-card" id="rps-fighter-p1">
            <div class="rps-fighter-name" id="rps-p1-name">Player 1</div>
            <div class="rps-fighter-hand" id="rps-p1-hand"></div>
            <div class="rps-fighter-choice" id="rps-p1-choice">ROCK</div>
          </div>

          <div class="rps-clash-divider">
            <div class="rps-clash-vs">VS</div>
            <div class="rps-clash-outcome" id="rps-clash-outcome">ROUND RESOLVED</div>
          </div>

          <div class="rps-fighter-card" id="rps-fighter-p2">
            <div class="rps-fighter-name" id="rps-p2-name">Player 2</div>
            <div class="rps-fighter-hand" id="rps-p2-hand"></div>
            <div class="rps-fighter-choice" id="rps-p2-choice">SCISSORS</div>
          </div>
        </div>

        <!-- View D: Pass-and-Play Privacy Curtain -->
        <div id="rps-curtain-overlay" class="rps-curtain-overlay hidden">
          <div class="rps-curtain-card">
            <div class="rps-curtain-icon">🔒</div>
            <h3 class="rps-curtain-title">CHOICE LOCKED</h3>
            <p class="rps-curtain-text">Pass the device to <strong id="rps-curtain-next-player">Player 2</strong></p>
            <button type="button" id="rps-curtain-ready-btn" class="pill-btn pill-btn-accent">READY, PLAYER 2 →</button>
          </div>
        </div>
      </div>

      <!-- Endgame Victory / Rematch Banner -->
      <div id="rps-endgame-banner" class="rps-endgame-banner hidden"></div>

      <!-- Interactive Rule Chart Modal -->
      <div id="rps-rule-modal" class="rps-rule-modal hidden" role="dialog" aria-modal="true">
        <div class="rps-modal-backdrop" id="rps-modal-backdrop"></div>
        <div class="rps-modal-content">
          <div class="rps-modal-header">
            <h3 class="rps-modal-title">WEAPON RELATIONSHIP GRAPH</h3>
            <button type="button" class="rps-modal-close" id="rps-modal-close" aria-label="Close">✕</button>
          </div>
          <div class="rps-modal-body">
            <div id="rps-graph-stage" class="rps-graph-stage"></div>
            <div id="rps-graph-info" class="rps-graph-info">
              Hover or click any weapon node to highlight what it beats and what beats it.
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  // DOM Elements
  const modeBadge = container.querySelector('#rps-mode-badge');
  const formatBadge = container.querySelector('#rps-format-badge');
  const roundBadge = container.querySelector('#rps-round-badge');
  const scoreboard = container.querySelector('#rps-scoreboard');
  const rulesBtn = container.querySelector('#rps-rules-btn');
  const resignBtn = container.querySelector('#rps-resign-btn');
  const playerStatus = container.querySelector('#rps-player-status');
  const rivalStatus = container.querySelector('#rps-rival-status');
  const choiceGrid = container.querySelector('#rps-choice-grid');
  const countdownOverlay = container.querySelector('#rps-countdown-overlay');
  const countdownNumber = container.querySelector('#rps-countdown-number');
  const revealStage = container.querySelector('#rps-reveal-stage');
  const p1Card = container.querySelector('#rps-fighter-p1');
  const p2Card = container.querySelector('#rps-fighter-p2');
  const p1Name = container.querySelector('#rps-p1-name');
  const p2Name = container.querySelector('#rps-p2-name');
  const p1Hand = container.querySelector('#rps-p1-hand');
  const p2Hand = container.querySelector('#rps-p2-hand');
  const p1ChoiceLabel = container.querySelector('#rps-p1-choice');
  const p2ChoiceLabel = container.querySelector('#rps-p2-choice');
  const clashOutcome = container.querySelector('#rps-clash-outcome');
  const curtainOverlay = container.querySelector('#rps-curtain-overlay');
  const curtainNextPlayer = container.querySelector('#rps-curtain-next-player');
  const curtainReadyBtn = container.querySelector('#rps-curtain-ready-btn');
  const endgameBanner = container.querySelector('#rps-endgame-banner');
  const ruleModal = container.querySelector('#rps-rule-modal');
  const modalBackdrop = container.querySelector('#rps-modal-backdrop');
  const modalClose = container.querySelector('#rps-modal-close');
  const graphStage = container.querySelector('#rps-graph-stage');
  const graphInfo = container.querySelector('#rps-graph-info');

  // Rules Chart Modal Handlers
  function openRuleModal() {
    renderRuleGraph();
    ruleModal.classList.remove('hidden');
    sound?.click?.();
  }

  function closeRuleModal() {
    ruleModal.classList.add('hidden');
    sound?.click?.();
  }

  rulesBtn?.addEventListener('click', openRuleModal);
  modalClose?.addEventListener('click', closeRuleModal);
  modalBackdrop?.addEventListener('click', closeRuleModal);

  // Resign Button Handler
  resignBtn?.addEventListener('click', () => {
    if (!confirmResign) {
      confirmResign = true;
      resignBtn.textContent = 'CONFIRM?';
      resignBtn.classList.add('pill-btn-danger');
      sound?.click?.();
      confirmResignTimer = setTimeout(() => {
        confirmResign = false;
        resignBtn.textContent = 'RESIGN';
        resignBtn.classList.remove('pill-btn-danger');
      }, 3500);
    } else {
      clearTimeout(confirmResignTimer);
      confirmResign = false;
      resignBtn.textContent = 'RESIGN';
      resignBtn.classList.remove('pill-btn-danger');
      sound?.error?.();
      sendAction('forfeit', {});
    }
  });

  // Pass-and-Play Curtain Ready Button
  curtainReadyBtn?.addEventListener('click', () => {
    curtainOverlay.classList.add('hidden');
    pnpCurrentTurn = 2;
    renderChoiceGrid();
    updateStatusIndicators();
    sound?.click?.();
  });

  // Handle Choice Selection
  function handleSelectChoice(choice) {
    if (isCountingDown) return;
    const isPassAndPlay = Boolean(
      currentPublicState?.settings?.pass_and_play || currentPublicState?.pass_and_play
    );

    if (isPassAndPlay) {
      if (pnpCurrentTurn === 1) {
        pnpP1Choice = choice;
        curtainNextPlayer.textContent = allPlayers[1]?.name || 'Player 2';
        curtainOverlay.classList.remove('hidden');
        sound?.click?.();
      } else {
        const p2Choice = choice;
        const p1Id = allPlayers[0]?.id || 'p1';
        const p2Id = allPlayers[1]?.id || `${p1Id}_p2`;

        // Commit both choices
        sendAction('choose', { choice: pnpP1Choice, player_id: p1Id });
        sendAction('choose', { choice: p2Choice, player_id: p2Id });

        pnpP1Choice = null;
        pnpCurrentTurn = 1;
        sound?.click?.();
      }
    } else {
      selectedChoice = choice;
      sound?.click?.();
      sendAction('choose', { choice });
      renderChoiceGrid();
      updateStatusIndicators();
    }
  }

  // Render Choice Buttons Grid
  function renderChoiceGrid() {
    const isLizardSpock = currentPublicState?.mode === 'lizard_spock';
    const keys = isLizardSpock ? LIZARD_SPOCK_KEYS : CLASSIC_KEYS;

    const meId = getPlayerId();
    const hasCommitted = Boolean(
      currentPrivateState?.committed || currentPrivateState?.has_committed || selectedChoice
    );
    const isFinished = currentPublicState?.phase === 'finished';

    choiceGrid.innerHTML = keys
      .map((k) => {
        const isSelected = (currentPrivateState?.choice === k) || (selectedChoice === k);
        const disabledAttr = (hasCommitted || isFinished || isCountingDown) ? 'disabled' : '';
        const activeClass = isSelected ? 'is-selected' : '';

        return `
          <button type="button" class="rps-choice-btn ${activeClass}" data-choice="${k}" ${disabledAttr}>
            <div class="rps-choice-icon">${RPS_ICONS[k] || ''}</div>
            <div class="rps-choice-label">${k.toUpperCase()}</div>
            ${isSelected ? '<span class="rps-locked-tag">LOCKED 🔒</span>' : ''}
          </button>
        `;
      })
      .join('');

    choiceGrid.querySelectorAll('.rps-choice-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const choice = btn.getAttribute('data-choice');
        if (choice) handleSelectChoice(choice);
      });
    });
  }

  // Update Status Indicators
  function updateStatusIndicators() {
    const isPassAndPlay = Boolean(
      currentPublicState?.settings?.pass_and_play || currentPublicState?.pass_and_play
    );
    const meId = getPlayerId();
    const isFinished = currentPublicState?.phase === 'finished';

    if (isFinished) {
      playerStatus.textContent = 'MATCH COMPLETED';
      rivalStatus.textContent = currentPublicState?.win_reason || 'Finished';
      return;
    }

    if (isPassAndPlay) {
      if (pnpCurrentTurn === 1) {
        playerStatus.textContent = `${allPlayers[0]?.name || 'Player 1'}: CHOOSE WEAPON`;
        playerStatus.classList.remove('is-committed');
        rivalStatus.textContent = `${allPlayers[1]?.name || 'Player 2'} WAITING...`;
      } else {
        playerStatus.textContent = `${allPlayers[1]?.name || 'Player 2'}: CHOOSE WEAPON`;
        playerStatus.classList.remove('is-committed');
        rivalStatus.textContent = `${allPlayers[0]?.name || 'Player 1'} LOCKED IN 🔒`;
      }
      return;
    }

    const hasCommitted = Boolean(
      currentPrivateState?.committed || currentPrivateState?.has_committed || selectedChoice
    );
    if (hasCommitted) {
      playerStatus.textContent = 'CHOICE LOCKED IN 🔒';
      playerStatus.classList.add('is-committed');
    } else {
      playerStatus.textContent = 'CHOOSE YOUR WEAPON';
      playerStatus.classList.remove('is-committed');
    }

    // Rival status
    const otherPlayer = allPlayers.find((p) => p.id !== meId);
    const otherId = otherPlayer?.id;
    const otherCommitted = Boolean(
      otherId && currentPublicState?.choices_committed?.[otherId]
    );

    if (otherCommitted) {
      rivalStatus.textContent = `${otherPlayer?.name || 'RIVAL'} LOCKED IN 🔒`;
      rivalStatus.classList.add('is-committed');
      rivalStatus.classList.remove('is-waiting');
    } else {
      rivalStatus.textContent = `${otherPlayer?.name || 'RIVAL'} CHOOSING...`;
      rivalStatus.classList.remove('is-committed');
      rivalStatus.classList.add('is-waiting');
    }
  }

  // Update Header Badges and Scoreboard
  function updateHeader() {
    const isLizardSpock = currentPublicState?.mode === 'lizard_spock';
    modeBadge.textContent = isLizardSpock ? 'LIZARD-SPOCK (5-CHOICE)' : 'CLASSIC 3-CHOICE';

    const fmt = currentPublicState?.format || 'bo3';
    if (fmt === 'bo5') {
      formatBadge.textContent = 'BEST OF 5';
    } else if (fmt === 'endless') {
      formatBadge.textContent = 'ENDLESS STREAK';
    } else if (fmt === 'single') {
      formatBadge.textContent = 'SINGLE ROUND';
    } else {
      formatBadge.textContent = 'BEST OF 3';
    }

    roundBadge.textContent = `ROUND ${currentPublicState?.round || 1}`;

    // Scoreboard
    const p1 = allPlayers[0];
    const p2 = allPlayers[1];
    const scores = currentPublicState?.scores || {};
    const streaks = currentPublicState?.streaks || {};
    const maxStreaks = currentPublicState?.max_streaks || {};

    if (fmt === 'endless') {
      const p1Strk = streaks[p1?.id] ?? currentPublicState?.p1_streak ?? 0;
      const p1Max = maxStreaks[p1?.id] ?? currentPublicState?.p1_max_streak ?? 0;
      scoreboard.innerHTML = `
        <div class="rps-streak-bar">
          <span class="rps-streak-pill">🔥 STREAK: <strong>${p1Strk}</strong></span>
          <span class="rps-streak-pill">🏆 BEST: <strong>${p1Max}</strong></span>
        </div>
      `;
    } else {
      const target = currentPublicState?.target_wins || (fmt === 'bo5' ? 3 : (fmt === 'single' ? 1 : 2));
      const s1 = scores[p1?.id] ?? currentPublicState?.p1_score ?? 0;
      const s2 = scores[p2?.id] ?? currentPublicState?.p2_score ?? 0;

      const p1Pips = Array.from({ length: target }, (_, idx) => `<span class="rps-pip ${idx < s1 ? 'is-filled' : ''}"></span>`).join('');
      const p2Pips = Array.from({ length: target }, (_, idx) => `<span class="rps-pip ${idx < s2 ? 'is-filled' : ''}"></span>`).join('');

      scoreboard.innerHTML = `
        <div class="rps-score-track">
          <span class="rps-player-label">${escapeHtml(p1?.name || 'P1')}</span>
          <div class="rps-pips">${p1Pips}</div>
          <span class="rps-vs-tag">VS</span>
          <div class="rps-pips">${p2Pips}</div>
          <span class="rps-player-label">${escapeHtml(p2?.name || 'P2')}</span>
        </div>
      `;
    }
  }

  // Trigger Animated Countdown Sequence
  function triggerCountdown(lastChoices, winnerId, reason) {
    if (isCountingDown) return;
    isCountingDown = true;

    countdownOverlay.classList.remove('hidden');
    choiceGrid.classList.add('hidden');
    revealStage.classList.add('hidden');

    let count = 3;
    countdownNumber.textContent = '3';
    sound?.tick?.();

    countdownTimer = setInterval(() => {
      count -= 1;
      if (count > 0) {
        countdownNumber.textContent = String(count);
        sound?.tick?.();
      } else {
        clearInterval(countdownTimer);
        countdownTimer = null;
        showRevealStage(lastChoices, winnerId, reason);
      }
    }, 600);
  }

  // Display Hand Reveal Stage
  function showRevealStage(lastChoices, winnerId, reason) {
    countdownOverlay.classList.add('hidden');
    revealStage.classList.remove('hidden');
    sound?.capture?.();

    const p1 = allPlayers[0];
    const p2 = allPlayers[1];
    const c1 = lastChoices?.[p1?.id] || 'rock';
    const c2 = lastChoices?.[p2?.id] || 'scissors';

    p1Name.textContent = p1?.name || 'Player 1';
    p2Name.textContent = p2?.name || 'Player 2';
    p1Hand.innerHTML = RPS_ICONS[c1] || '';
    p2Hand.innerHTML = RPS_ICONS[c2] || '';
    p1ChoiceLabel.textContent = c1.toUpperCase();
    p2ChoiceLabel.textContent = c2.toUpperCase();
    clashOutcome.textContent = reason || `${c1.toUpperCase()} vs ${c2.toUpperCase()}`;

    p1Card.classList.remove('is-winner', 'is-loser', 'is-tie');
    p2Card.classList.remove('is-winner', 'is-loser', 'is-tie');

    if (!winnerId) {
      p1Card.classList.add('is-tie');
      p2Card.classList.add('is-tie');
    } else if (winnerId === p1?.id) {
      p1Card.classList.add('is-winner');
      p2Card.classList.add('is-loser');
      if (getPlayerId() === p1?.id) sound?.win?.();
    } else {
      p2Card.classList.add('is-winner');
      p1Card.classList.add('is-loser');
      if (getPlayerId() === p2?.id) sound?.win?.();
    }

    selectedChoice = null;

    // Auto dismiss reveal stage after 2.4s if game is still playing
    clearTimeout(autoDismissTimer);
    autoDismissTimer = setTimeout(() => {
      isCountingDown = false;
      if (currentPublicState?.phase === 'playing') {
        revealStage.classList.add('hidden');
        choiceGrid.classList.remove('hidden');
        renderChoiceGrid();
        updateStatusIndicators();
      }
    }, 2400);
  }

  // Render Endgame Banner
  function renderEndgameBanner() {
    const winnerIds = currentPublicState?.winner_ids || [];
    const isWinner = winnerIds.includes(getPlayerId());
    const isFinished = currentPublicState?.phase === 'finished';

    if (!isFinished) {
      endgameBanner.classList.add('hidden');
      return;
    }

    endgameBanner.classList.remove('hidden');
    const winnerSlot = allPlayers.find((p) => winnerIds.includes(p.id));
    const winnerTitle = winnerIds.length === 0
      ? 'MATCH DRAW'
      : (isWinner ? 'VICTORY!' : `${escapeHtml(winnerSlot?.name || 'WINNER')} WINS!`);

    endgameBanner.innerHTML = `
      <div class="rps-endgame-card ${isWinner ? 'is-victory' : ''}">
        <h2 class="rps-endgame-title">${winnerTitle}</h2>
        <p class="rps-endgame-reason">${escapeHtml(currentPublicState?.win_reason || '')}</p>
        <button type="button" id="rps-rematch-btn" class="pill-btn pill-btn-accent">REMATCH</button>
      </div>
    `;

    endgameBanner.querySelector('#rps-rematch-btn')?.addEventListener('click', () => {
      sound?.click?.();
      sendAction('rematch', {});
    });
  }

  // Interactive Pentagram Rule Graph
  function renderRuleGraph() {
    const isLizardSpock = currentPublicState?.mode === 'lizard_spock';
    const keys = isLizardSpock ? LIZARD_SPOCK_KEYS : CLASSIC_KEYS;

    const width = 480;
    const height = 400;
    const cx = 240;
    const cy = 200;
    const radius = 140;

    const nodeCoords = {};
    keys.forEach((key, idx) => {
      const angle = (idx * 2 * Math.PI) / keys.length - Math.PI / 2;
      nodeCoords[key] = {
        x: Math.round(cx + radius * Math.cos(angle)),
        y: Math.round(cy + radius * Math.sin(angle)),
      };
    });

    // Edges
    const edges = [];
    keys.forEach((source) => {
      const defeats = BEATS[source] || [];
      defeats.forEach((target) => {
        if (keys.includes(target)) {
          edges.push({ source, target });
        }
      });
    });

    const edgeSvg = edges
      .map(({ source, target }) => {
        const p1 = nodeCoords[source];
        const p2 = nodeCoords[target];
        // Calculate shortened segment for arrowhead clarity
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const dist = Math.hypot(dx, dy);
        const offset = 26;
        const x1 = Math.round(p1.x + (dx * offset) / dist);
        const y1 = Math.round(p1.y + (dy * offset) / dist);
        const x2 = Math.round(p2.x - (dx * offset) / dist);
        const y2 = Math.round(p2.y - (dy * offset) / dist);

        return `
          <line class="rps-graph-edge" data-source="${source}" data-target="${target}" 
                x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" 
                marker-end="url(#rps-arrow)" />
        `;
      })
      .join('');

    const nodeSvg = keys
      .map((k) => {
        const { x, y } = nodeCoords[k];
        return `
          <g class="rps-graph-node" data-node="${k}" transform="translate(${x}, ${y})">
            <circle class="rps-node-circle" r="26" />
            <text class="rps-node-text" y="5" text-anchor="middle">${k.toUpperCase()}</text>
          </g>
        `;
      })
      .join('');

    graphStage.innerHTML = `
      <svg class="rps-pentagram-svg" viewBox="0 0 ${width} ${height}" fill="none">
        <defs>
          <marker id="rps-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-ash)" class="rps-arrowhead" />
          </marker>
        </defs>
        <g class="rps-graph-edges">${edgeSvg}</g>
        <g class="rps-graph-nodes">${nodeSvg}</g>
      </svg>
    `;

    // Interactivity
    const nodes = graphStage.querySelectorAll('.rps-graph-node');
    const edgeLines = graphStage.querySelectorAll('.rps-graph-edge');

    nodes.forEach((n) => {
      const k = n.getAttribute('data-node');
      const highlight = () => {
        nodes.forEach((other) => other.classList.toggle('is-active', other === n));
        edgeLines.forEach((line) => {
          const s = line.getAttribute('data-source');
          const t = line.getAttribute('data-target');
          if (s === k) {
            line.classList.add('is-outgoing');
            line.classList.remove('is-incoming', 'is-dimmed');
          } else if (t === k) {
            line.classList.add('is-incoming');
            line.classList.remove('is-outgoing', 'is-dimmed');
          } else {
            line.classList.add('is-dimmed');
            line.classList.remove('is-outgoing', 'is-incoming');
          }
        });
        graphInfo.innerHTML = `<strong>${k.toUpperCase()}</strong>: ${RELATIONSHIP_DESCRIPTIONS[k] || ''}`;
      };

      const reset = () => {
        nodes.forEach((other) => other.classList.remove('is-active'));
        edgeLines.forEach((line) => line.classList.remove('is-outgoing', 'is-incoming', 'is-dimmed'));
        graphInfo.textContent = 'Hover or click any weapon node to highlight what it beats and what beats it.';
      };

      n.addEventListener('mouseenter', highlight);
      n.addEventListener('mouseleave', reset);
      n.addEventListener('click', highlight);
    });
  }

  // Initial renders
  renderChoiceGrid();
  renderRuleGraph();

  return {
    update(publicState, privateState, players) {
      currentPublicState = publicState || currentPublicState;
      currentPrivateState = privateState || currentPrivateState;
      allPlayers = getActivePlayers(players || getPlayers?.() || []);

      updateHeader();
      updateStatusIndicators();

      // Check if a round just resolved
      const lastRound = currentPublicState?.rounds_history?.slice(-1)[0];
      const roundIdx = lastRound?.round || 0;

      if (roundIdx > 0 && roundIdx > lastRevealedRound) {
        lastRevealedRound = roundIdx;
        triggerCountdown(
          lastRound.choices,
          lastRound.winner,
          lastRound.reason
        );
      } else if (!isCountingDown) {
        renderChoiceGrid();
      }

      renderEndgameBanner();
    },

    destroy() {
      clearInterval(countdownTimer);
      clearTimeout(autoDismissTimer);
      clearTimeout(confirmResignTimer);
      container.removeAttribute('data-game');
      container.innerHTML = '';
    },
  };
}
