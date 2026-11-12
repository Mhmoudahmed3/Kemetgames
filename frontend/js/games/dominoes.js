import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

/**
 * Elevated Dominoes Chain Game Module
 * Features authentic ivory/resin domino tiles with 3D recessed pips, brass spinner rivets,
 * luxury gaming felt tabletop, interactive tabletop boneyard draw pile, and wooden hand rack.
 */

// Generate 3x3 standard domino pips inside an SVG half
function getPipCoordinates(val, cx, cy, isVertical, halfW, halfH) {
  // Distance from center to dots
  const dx = Math.round(halfW * 0.28);
  const dy = Math.round(halfH * 0.28);

  switch (val) {
    case 0:
      return [];
    case 1:
      return [{ x: cx, y: cy }];
    case 2:
      return [
        { x: cx - dx, y: cy - dy },
        { x: cx + dx, y: cy + dy },
      ];
    case 3:
      return [
        { x: cx - dx, y: cy - dy },
        { x: cx, y: cy },
        { x: cx + dx, y: cy + dy },
      ];
    case 4:
      return [
        { x: cx - dx, y: cy - dy },
        { x: cx + dx, y: cy - dy },
        { x: cx - dx, y: cy + dy },
        { x: cx + dx, y: cy + dy },
      ];
    case 5:
      return [
        { x: cx - dx, y: cy - dy },
        { x: cx + dx, y: cy - dy },
        { x: cx, y: cy },
        { x: cx - dx, y: cy + dy },
        { x: cx + dx, y: cy + dy },
      ];
    case 6:
      if (isVertical) {
        const colDx = Math.round(halfW * 0.28);
        const rowDy = Math.round(halfH * 0.30);
        return [
          { x: cx - colDx, y: cy - rowDy },
          { x: cx - colDx, y: cy },
          { x: cx - colDx, y: cy + rowDy },
          { x: cx + colDx, y: cy - rowDy },
          { x: cx + colDx, y: cy },
          { x: cx + colDx, y: cy + rowDy },
        ];
      } else {
        const rowDy = Math.round(halfH * 0.28);
        const colDx = Math.round(halfW * 0.30);
        return [
          { x: cx - colDx, y: cy - rowDy },
          { x: cx, y: cy - rowDy },
          { x: cx + colDx, y: cy - rowDy },
          { x: cx - colDx, y: cy + rowDy },
          { x: cx, y: cy + rowDy },
          { x: cx + colDx, y: cy + rowDy },
        ];
      }
    default:
      return [];
  }
}

let defsCounter = 0;

export function renderDominoTileSvg(a, b, { orientation = 'vertical', width = null, height = null, isDouble = false } = {}) {
  defsCounter++;
  const uid = `dom-uid-${defsCounter}-${Date.now().toString(36)}`;
  const isVert = orientation === 'vertical';

  const w = width !== null ? width : (isVert ? 54 : 108);
  const h = height !== null ? height : (isVert ? 108 : 54);

  // Midpoint dividing groove coordinates
  const midX = w / 2;
  const midY = h / 2;

  // Halves centers and dimensions
  const half1Center = isVert ? { cx: w / 2, cy: h / 4 } : { cx: w / 4, cy: h / 2 };
  const half2Center = isVert ? { cx: w / 2, cy: (3 * h) / 4 } : { cx: (3 * w) / 4, cy: h / 2 };
  const halfW = isVert ? w : w / 2;
  const halfH = isVert ? h / 2 : h;

  const pips1 = getPipCoordinates(a, half1Center.cx, half1Center.cy, isVert, halfW, halfH);
  const pips2 = getPipCoordinates(b, half2Center.cx, half2Center.cy, isVert, halfW, halfH);

  const pipRadius = Math.max(2.6, Math.min(3.6, Math.round(Math.min(w, h) * 0.065)));

  const pipsMarkup = (list) =>
    list
      .map(
        (p) => `
        <g transform="translate(${p.x}, ${p.y})">
          <!-- Recessed shadow rim -->
          <circle cx="0" cy="0.6" r="${pipRadius + 0.3}" fill="rgba(0,0,0,0.25)"/>
          <!-- Pip Cavity -->
          <circle cx="0" cy="0" r="${pipRadius}" fill="url(#pipGrad-${uid})"/>
          <!-- Inner Specular Light reflection (10 o'clock) -->
          <circle cx="${-pipRadius * 0.32}" cy="${-pipRadius * 0.32}" r="${pipRadius * 0.35}" fill="rgba(255,255,255,0.4)"/>
        </g>`
      )
      .join('');

  return `
    <svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" class="domino-tile-svg" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Authentic Ivory Gradient -->
        <linearGradient id="ivoryGrad-${uid}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="25%" stop-color="#fcf9f2"/>
          <stop offset="70%" stop-color="#f1ebe0"/>
          <stop offset="100%" stop-color="#e3dacf"/>
        </linearGradient>

        <!-- Brass Spinner Rivet Gradient -->
        <radialGradient id="brassGrad-${uid}" cx="35%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#ffe885"/>
          <stop offset="40%" stop-color="#d4af37"/>
          <stop offset="85%" stop-color="#8f6b15"/>
          <stop offset="100%" stop-color="#4e3a09"/>
        </radialGradient>

        <!-- Sunken Pip Shadow Gradient -->
        <radialGradient id="pipGrad-${uid}" cx="40%" cy="40%" r="60%">
          <stop offset="0%" stop-color="#2a2c30"/>
          <stop offset="65%" stop-color="#141517"/>
          <stop offset="100%" stop-color="#0a0a0c"/>
        </radialGradient>
      </defs>

      <!-- Domino Body -->
      <rect x="1.5" y="1.5" width="${w - 3}" height="${h - 3}" rx="6" ry="6"
        fill="url(#ivoryGrad-${uid})"
        stroke="rgba(255,255,255,0.9)" stroke-width="1.2"/>

      <!-- Outer Bevel Cast Shadow Line -->
      <rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="5" ry="5"
        fill="none" stroke="rgba(0,0,0,0.14)" stroke-width="0.8"/>

      <!-- Recessed Center Dividing Groove -->
      ${
        isVert
          ? `
        <line x1="5" y1="${midY - 0.5}" x2="${w - 5}" y2="${midY - 0.5}" stroke="#2b2823" stroke-width="2" stroke-linecap="round"/>
        <line x1="5" y1="${midY + 0.8}" x2="${w - 5}" y2="${midY + 0.8}" stroke="rgba(255,255,255,0.75)" stroke-width="1" stroke-linecap="round"/>
      `
          : `
        <line x1="${midX - 0.5}" y1="5" x2="${midX - 0.5}" y2="${h - 5}" stroke="#2b2823" stroke-width="2" stroke-linecap="round"/>
        <line x1="${midX + 0.8}" y1="5" x2="${midX + 0.8}" y2="${h - 5}" stroke="rgba(255,255,255,0.75)" stroke-width="1" stroke-linecap="round"/>
      `
      }

      <!-- Center Brass Spinner Rivet (Tournament Domino Spinner Pin) -->
      <circle cx="${midX}" cy="${midY + 0.5}" r="3.4" fill="rgba(0,0,0,0.3)"/>
      <circle cx="${midX}" cy="${midY}" r="3.2" fill="url(#brassGrad-${uid})" stroke="#5c440a" stroke-width="0.6"/>
      <circle cx="${midX - 0.9}" cy="${midY - 0.9}" r="1.1" fill="rgba(255,255,255,0.85)"/>

      <!-- Half 1 Pips -->
      ${pipsMarkup(pips1)}

      <!-- Half 2 Pips -->
      ${pipsMarkup(pips2)}
    </svg>
  `;
}

export function renderBoneyardTileSvg({ width = 42, height = 72 } = {}) {
  defsCounter++;
  const uid = `bone-uid-${defsCounter}-${Date.now().toString(36)}`;
  return `
    <svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" class="boneyard-tile-svg" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Dark Ebony Resin Gradient -->
        <linearGradient id="ebonyGrad-${uid}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#2a2e38"/>
          <stop offset="35%" stop-color="#191c22"/>
          <stop offset="80%" stop-color="#111317"/>
          <stop offset="100%" stop-color="#08090b"/>
        </linearGradient>
        <!-- Brass Pin Gradient -->
        <radialGradient id="brassBackGrad-${uid}" cx="35%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#ffd566"/>
          <stop offset="50%" stop-color="#caa230"/>
          <stop offset="100%" stop-color="#6b500c"/>
        </radialGradient>
      </defs>

      <!-- Tile Body -->
      <rect x="1.5" y="1.5" width="${width - 3}" height="${height - 3}" rx="5" ry="5"
        fill="url(#ebonyGrad-${uid})"
        stroke="rgba(255,255,255,0.18)" stroke-width="1"/>

      <!-- Gold Filigree Inlay Border -->
      <rect x="4" y="4" width="${width - 8}" height="${height - 8}" rx="3.5" ry="3.5"
        fill="none" stroke="rgba(212,175,55,0.55)" stroke-width="0.8" stroke-dasharray="6 2"/>

      <!-- Diamond Rosette Centerpiece -->
      <g transform="translate(${width / 2}, ${height / 2})">
        <polygon points="0,-10 8,0 0,10 -8,0" fill="none" stroke="rgba(212,175,55,0.3)" stroke-width="0.8"/>
        <!-- Brass Center Spinner Pin -->
        <circle cx="0" cy="0.6" r="2.8" fill="rgba(0,0,0,0.5)"/>
        <circle cx="0" cy="0" r="2.6" fill="url(#brassBackGrad-${uid})" stroke="#473406" stroke-width="0.5"/>
        <circle cx="-0.7" cy="-0.7" r="0.8" fill="rgba(255,255,255,0.85)"/>
      </g>
    </svg>
  `;
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let pendingTileChoice = null;
  let currentPlayableList = [];
  let currentBoneyardCount = 0;
  let isCurrentTurn = false;
  let isSpectator = false;
  let activeChain = [];

  container.innerHTML = `
    <div class="domino-arena">
      <!-- Top Luxury Statusbar -->
      <div class="game-statusbar domino-statusbar">
        <span class="status-metric">ROUND <strong id="dom-round">1</strong></span>
        <span class="status-metric">TARGET <strong id="dom-target">100</strong></span>
        <span class="status-metric">BONEYARD <strong id="dom-bone">0</strong> TILES</span>
        <span class="status-metric">OPEN ENDS <strong id="dom-ends" class="dom-ends-glow">OPEN BOARD</strong></span>
      </div>

      <!-- Opponents Banner -->
      <div id="dom-opponents" class="domino-opponents-strip"></div>

      <!-- Main Arena Split: Left Boneyard Station + Right Felt Tabletop -->
      <div class="domino-table-layout">
        <!-- LEFT SIDE: Boneyard Draw Station -->
        <div id="dom-boneyard-box" class="domino-boneyard-station">
          <div class="domino-boneyard-header">
            <div class="dom-bone-title-wrap">
              <span class="dom-bone-icon">🁢</span>
              <span class="dom-bone-title">BONEYARD</span>
            </div>
            <span id="dom-bone-badge" class="dom-bone-badge">14 TILES</span>
          </div>
          <div id="dom-bone-hint" class="dom-bone-hint">Click any piece to draw when stuck</div>

          <!-- Tactile Face-down Domino Draw Grid -->
          <div id="dom-boneyard-tray" class="domino-boneyard-tray"></div>

          <!-- Draw Station Action Controls -->
          <div class="dom-bone-actions">
            <button type="button" id="dom-draw-btn" class="pill-btn pill-btn-sm dom-action-draw hidden">
              <span class="dom-btn-icon">⚡</span> DRAW PIECE
            </button>
            <button type="button" id="dom-pass-btn" class="pill-btn pill-btn-sm pill-btn-outline dom-action-pass hidden">
              PASS TURN
            </button>
            <div id="dom-bone-toast" class="domino-toast hidden"></div>
          </div>
        </div>

        <!-- RIGHT SIDE: Felt Tabletop Board -->
        <div class="domino-tabletop">
          <div class="domino-table-header">
            <span class="domino-table-title">DOMINO CHAIN FELT TABLE</span>
            <span id="dom-table-note" class="domino-table-sub">Connect matching pip numbers to either open end</span>
          </div>

          <div id="dom-chain" class="domino-chain-wrap">
            <div class="domino-empty-lead">
              <span class="domino-empty-lead-icon">🎲</span>
              <span>Board empty — lead the round with any domino from your rack.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Side Selection Modal Overlay -->
      <div id="dom-side-prompt" class="domino-side-modal hidden">
        <div class="domino-side-card">
          <div class="domino-side-title">CHOOSE CHAIN END</div>
          <div class="domino-side-desc">This domino matches both open ends of the board:</div>
          <div id="dom-chosen-preview" class="domino-chosen-preview"></div>
          <div class="domino-side-btns">
            <button type="button" id="dom-play-left" class="pill-btn pill-btn-md dom-side-btn">
              ◄ PLAY ON LEFT (<span id="dom-left-num">?</span>)
            </button>
            <button type="button" id="dom-play-right" class="pill-btn pill-btn-md dom-side-btn">
              PLAY ON RIGHT (<span id="dom-right-num">?</span>) ►
            </button>
          </div>
          <button type="button" id="dom-play-cancel" class="pill-btn pill-btn-sm pill-btn-outline dom-play-cancel">
            CANCEL
          </button>
        </div>
      </div>

      <!-- Wooden Player Hand Rack -->
      <div class="domino-hand-rack-wrap">
        <div class="domino-rack-header">
          <div class="domino-rack-label">
            <span class="domino-rack-gem">◆</span>
            <span>YOUR DOMINO RACK</span>
            <span id="dom-hand-count" class="domino-hand-badge">7 TILES</span>
          </div>
          <span id="dom-hand-tip" class="domino-rack-tip">Playable tiles glow with active end targets</span>
        </div>

        <div id="dom-hand-rack" class="domino-hand-rack">
          <div id="dom-hand" class="domino-hand-tiles"></div>
        </div>
      </div>
    </div>
  `;

  // DOM Elements
  const roundEl = container.querySelector('#dom-round');
  const targetEl = container.querySelector('#dom-target');
  const boneEl = container.querySelector('#dom-bone');
  const endsEl = container.querySelector('#dom-ends');
  const oppEl = container.querySelector('#dom-opponents');
  const chainEl = container.querySelector('#dom-chain');
  const boneyardBox = container.querySelector('#dom-boneyard-box');
  const boneBadge = container.querySelector('#dom-bone-badge');
  const boneHint = container.querySelector('#dom-bone-hint');
  const boneyardTray = container.querySelector('#dom-boneyard-tray');
  const drawBtn = container.querySelector('#dom-draw-btn');
  const passBtn = container.querySelector('#dom-pass-btn');
  const boneToast = container.querySelector('#dom-bone-toast');
  const sidePrompt = container.querySelector('#dom-side-prompt');
  const chosenPreview = container.querySelector('#dom-chosen-preview');
  const leftNumEl = container.querySelector('#dom-left-num');
  const rightNumEl = container.querySelector('#dom-right-num');
  const leftBtn = container.querySelector('#dom-play-left');
  const rightBtn = container.querySelector('#dom-play-right');
  const cancelBtn = container.querySelector('#dom-play-cancel');
  const handEl = container.querySelector('#dom-hand');
  const handCountEl = container.querySelector('#dom-hand-count');
  const handTipEl = container.querySelector('#dom-hand-tip');

  let toastTimer = null;
  let shakeTimer = null;
  function showToast(msg) {
    if (toastTimer) clearTimeout(toastTimer);
    if (shakeTimer) clearTimeout(shakeTimer);
    boneToast.textContent = msg;
    boneToast.classList.remove('hidden');
    boneToast.classList.add('shake');
    shakeTimer = setTimeout(() => {
      boneToast.classList.remove('shake');
      shakeTimer = null;
    }, 400);
    toastTimer = setTimeout(() => {
      boneToast.classList.add('hidden');
      toastTimer = null;
    }, 3200);
  }

  // Draw Action Helper
  function attemptDraw() {
    if (isSpectator) return;
    if (!isCurrentTurn) {
      showToast('Wait for your turn to draw from the boneyard.');
      return;
    }
    if (currentPlayableList.length > 0) {
      sound.click();
      showToast('You already hold playable tiles in your rack! Play a matching domino.');
      return;
    }
    if (currentBoneyardCount <= 0) {
      sound.click();
      showToast('The boneyard is empty! You must pass your turn.');
      return;
    }
    sound.card();
    sendAction('draw', {});
  }

  // Draw & Pass buttons
  drawBtn.addEventListener('click', attemptDraw);

  passBtn.addEventListener('click', () => {
    if (!isCurrentTurn || isSpectator) return;
    sound.click();
    sendAction('pass', {});
  });

  // Side Selection Modal Events
  leftBtn.addEventListener('click', () => {
    if (!pendingTileChoice) return;
    sound.chessMove();
    sendAction('play', { tile: pendingTileChoice, side: 'left' });
    pendingTileChoice = null;
    sidePrompt.classList.add('hidden');
  });

  rightBtn.addEventListener('click', () => {
    if (!pendingTileChoice) return;
    sound.chessMove();
    sendAction('play', { tile: pendingTileChoice, side: 'right' });
    pendingTileChoice = null;
    sidePrompt.classList.add('hidden');
  });

  cancelBtn.addEventListener('click', () => {
    sound.click();
    pendingTileChoice = null;
    sidePrompt.classList.add('hidden');
  });

  return {
    update(publicState, privateState, players) {
      const meId = getPlayerId();
      const allPlayers = players || getPlayers();
      const me = allPlayers.find((p) => p.id === meId);
      isSpectator = Boolean(!me || me.role === 'spectator');
      isCurrentTurn = !isSpectator && publicState.turn_player_id === meId && publicState.phase === 'playing';
      activeChain = publicState.chain || [];
      currentBoneyardCount = publicState.boneyard_count ?? 0;

      // Status Metrics
      roundEl.textContent = String(publicState.round_number || 1);
      targetEl.textContent = String(publicState.target_score || 100);
      boneEl.textContent = String(currentBoneyardCount);

      const hasEnds = publicState.left_end !== null && publicState.left_end !== undefined;
      endsEl.textContent = hasEnds
        ? `◄ LEFT [${publicState.left_end}]  ·  RIGHT [${publicState.right_end}] ►`
        : 'OPEN BOARD';

      // Opponents Strip (exclude spectators)
      const activePlayers = getActivePlayers(allPlayers);
      oppEl.innerHTML = '';
      for (const p of activePlayers) {
        if (p.id === meId) continue;
        const cnt = Number(publicState.hand_counts?.[p.id] ?? 0);
        const isTurn = publicState.turn_player_id === p.id;
        const box = document.createElement('div');
        box.className = `domino-opponent-card ${isTurn ? 'is-turn' : ''}`;
        box.innerHTML = `
          <div class="dom-opp-header">
            <span class="dom-opp-name">${escapeHtml(p.name)}</span>
            ${isTurn ? '<span class="dom-opp-turn-tag">THINKING</span>' : ''}
          </div>
          <div class="dom-opp-stats">
            <span class="dom-opp-cnt">🁢 ${cnt} TILES</span>
            <span class="dom-opp-score">${Number(p.score) || 0} PTS</span>
          </div>
        `;
        oppEl.appendChild(box);
      }

      // Board Chain Render
      chainEl.innerHTML = '';
      if (!activeChain.length) {
        chainEl.innerHTML = `
          <div class="domino-empty-lead">
            <span class="domino-empty-lead-icon">🎲</span>
            <span>Board empty — lead the round with any domino from your rack.</span>
          </div>
        `;
      } else {
        // Open Left Indicator
        const leftIndicator = document.createElement('div');
        leftIndicator.className = 'domino-chain-end-pill left-end';
        leftIndicator.innerHTML = `<span>◄ LEFT</span><strong>${escapeHtml(publicState.left_end)}</strong>`;
        chainEl.appendChild(leftIndicator);

        // Chain Tiles
        activeChain.forEach(([a, b]) => {
          const isDouble = a === b;
          const tileNode = document.createElement('div');
          tileNode.className = `domino-piece on-chain ${isDouble ? 'is-spinner-double' : 'is-horizontal'}`;
          // Doubles in authentic domino matches are placed crosswise (perpendicular to chain flow)
          tileNode.innerHTML = renderDominoTileSvg(a, b, {
            orientation: isDouble ? 'vertical' : 'horizontal',
            width: isDouble ? 42 : 84,
            height: isDouble ? 84 : 42,
            isDouble,
          });
          chainEl.appendChild(tileNode);
        });

        // Open Right Indicator
        const rightIndicator = document.createElement('div');
        rightIndicator.className = 'domino-chain-end-pill right-end';
        rightIndicator.innerHTML = `<strong>${escapeHtml(publicState.right_end)}</strong><span>RIGHT ►</span>`;
        chainEl.appendChild(rightIndicator);
      }

      // Hand & Playables Logic
      const hand = isSpectator ? [] : (privateState?.hand || []);
      currentPlayableList = isSpectator ? [] : (privateState?.playable || []);
      const playableMap = new Map(
        currentPlayableList.map((item) => [`${item.tile[0]}-${item.tile[1]}`, item.sides])
      );

      handCountEl.textContent = isSpectator ? 'SPECTATING' : `${hand.length} TILES`;
      if (handTipEl) {
        handTipEl.classList.toggle('hidden', isSpectator);
      }

      const canDraw = !isSpectator && isCurrentTurn && currentPlayableList.length === 0 && currentBoneyardCount > 0;
      const mustPass = !isSpectator && isCurrentTurn && currentPlayableList.length === 0 && currentBoneyardCount === 0;

      // Update Boneyard Station
      boneBadge.textContent = `${currentBoneyardCount} TILES AVAILABLE`;
      boneyardBox.classList.toggle('can-draw', canDraw);

      if (isSpectator) {
        boneHint.textContent = 'Spectator View — watching Dominoes table live.';
      } else if (canDraw) {
        boneHint.innerHTML = `<strong class="dom-bone-hint-active">⚡ NO MATCHING TILES IN HAND</strong> — Click any boneyard piece below to draw`;
      } else if (mustPass) {
        boneHint.innerHTML = `<strong class="dom-bone-hint-empty">Boneyard empty and no moves</strong> — Click Pass Turn`;
      } else if (isCurrentTurn) {
        boneHint.textContent = 'You have matching playable tiles in your rack. Click a highlighted domino to play.';
      } else {
        boneHint.textContent = 'Click any face-down piece below to draw when stuck on your turn.';
      }

      drawBtn.classList.toggle('hidden', !canDraw);
      passBtn.classList.toggle('hidden', !mustPass);

      // Render Tactile Face-down Boneyard Pieces
      boneyardTray.innerHTML = '';
      if (currentBoneyardCount === 0) {
        boneyardTray.innerHTML = `<span class="dom-boneyard-depleted">BONEYARD DEPLETED</span>`;
      } else {
        // Show up to min(currentBoneyardCount, 14) tactile face-down tiles
        const tilesToShow = Math.min(currentBoneyardCount, 14);
        for (let i = 0; i < tilesToShow; i++) {
          const piece = document.createElement('div');
          piece.className = 'boneyard-tile-interactive';
          piece.title = canDraw ? 'Click to draw this domino!' : `${currentBoneyardCount} tiles in boneyard`;
          piece.innerHTML = renderBoneyardTileSvg({ width: 40, height: 68 });
          if (!isSpectator) {
            piece.addEventListener('click', () => attemptDraw());
          }
          boneyardTray.appendChild(piece);
        }
      }

      // Render Player's Domino Hand Rack
      handEl.innerHTML = '';
      if (hand.length === 0) {
        const emptyMsg = isSpectator
          ? 'Spectator View — watching Dominoes table live.'
          : publicState.phase === 'finished'
            ? 'Match finished — final scores settled.'
            : 'Round over — no dominoes in hand.';
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'domino-hand-empty';
        emptyDiv.textContent = emptyMsg;
        handEl.appendChild(emptyDiv);
      }

      for (const [a, b] of hand) {
        const sides = isCurrentTurn ? playableMap.get(`${a}-${b}`) : null;
        const isPlayable = Boolean(sides && sides.length > 0);

        const node = document.createElement('div');
        node.className = `domino-piece in-hand ${isPlayable ? 'playable' : 'inactive'}`;

        // Side match badge tag
        if (isPlayable) {
          const badge = document.createElement('div');
          badge.className = 'domino-side-badge';
          if (!activeChain.length) {
            badge.textContent = 'LEAD';
          } else if (sides.includes('left') && sides.includes('right') && publicState.left_end !== publicState.right_end) {
            badge.textContent = '◄ BOTH ►';
          } else if (sides.includes('left')) {
            badge.textContent = '◄ LEFT';
          } else {
            badge.textContent = 'RIGHT ►';
          }
          node.appendChild(badge);
        }

        const tileSvg = renderDominoTileSvg(a, b, {
          orientation: 'vertical',
          width: 54,
          height: 108,
          isDouble: a === b,
        });

        const svgWrap = document.createElement('div');
        svgWrap.innerHTML = tileSvg;
        node.appendChild(svgWrap.firstElementChild);

        if (isPlayable) {
          node.addEventListener('click', () => {
            if (!activeChain.length || sides.length <= 1 || publicState.left_end === publicState.right_end) {
              sound.chessMove();
              sendAction('play', { tile: [a, b], side: sides[0] || 'right' });
              pendingTileChoice = null;
              sidePrompt.classList.add('hidden');
            } else {
              sound.click();
              pendingTileChoice = [a, b];
              leftNumEl.textContent = String(publicState.left_end);
              rightNumEl.textContent = String(publicState.right_end);
              chosenPreview.innerHTML = renderDominoTileSvg(a, b, {
                orientation: 'vertical',
                width: 50,
                height: 100,
                isDouble: a === b,
              });
              sidePrompt.classList.remove('hidden');
            }
          });
        }

        handEl.appendChild(node);
      }

      if (!isCurrentTurn) {
        pendingTileChoice = null;
        sidePrompt.classList.add('hidden');
      }
    },
    destroy() {
      if (toastTimer) clearTimeout(toastTimer);
      if (shakeTimer) clearTimeout(shakeTimer);
    },
  };
}
