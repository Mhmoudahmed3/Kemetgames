import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  const GRID = 20;
  let snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }];
  let dir = { x: 1, y: 0 };
  let turnQueue = [];
  let food = spawnFood(snake);
  let score = 0;
  let alive = true;
  let paused = false;
  let stepMs = 125;
  let pointsPerFood = 10;
  let latestState = {};
  let latestPlayers = getPlayers();
  let isSpectator = Boolean(latestPlayers.find((p) => p.id === getPlayerId())?.role === 'spectator');

  container.innerHTML = `
    <div class="game-shell">
      <div class="game-statusbar">
        <span class="status-metric">SCORE <strong id="snk-score">0</strong></span>
        <span class="status-metric">LENGTH <strong id="snk-len">3</strong></span>
        <span class="status-metric" id="snk-diff-wrap">PACE <strong id="snk-diff">MID</strong></span>
        <span class="status-metric" id="snk-timer-wrap">TIMER <strong id="snk-timer">—</strong></span>
        <span class="status-metric">CONTROLS: <strong>WASD / ARROWS / SWIPE / D-PAD</strong></span>
        <button type="button" id="snk-pause-btn" class="pill-btn pill-btn-sm pill-btn-outline hidden" aria-pressed="false">PAUSE</button>
      </div>
      <div class="snake-layout">
        <div class="snake-canvas-wrap">
          <canvas id="snk-canvas" class="snake-canvas" width="400" height="400"></canvas>
          <div class="touch-dpad" id="snk-dpad">
            <span></span>
            <button type="button" class="dpad-btn" data-dir="up" aria-label="Move Up">▲</button>
            <span></span>
            <button type="button" class="dpad-btn" data-dir="left" aria-label="Move Left">◀</button>
            <button type="button" class="dpad-btn" data-dir="down" aria-label="Move Down">▼</button>
            <button type="button" class="dpad-btn" data-dir="right" aria-label="Move Right">▶</button>
          </div>
        </div>
        <div class="rival-panel">
          <div class="bunker-sublabel">LIVE ROOM TELEMETRY</div>
          <div id="snk-rivals"></div>
        </div>
      </div>
    </div>
  `;

  const canvas = container.querySelector('#snk-canvas');
  const ctx = canvas.getContext('2d');
  const scoreEl = container.querySelector('#snk-score');
  const lenEl = container.querySelector('#snk-len');
  const diffEl = container.querySelector('#snk-diff');
  const timerEl = container.querySelector('#snk-timer');
  const rivalsEl = container.querySelector('#snk-rivals');
  const pauseBtn = container.querySelector('#snk-pause-btn');
  const dpadEl = container.querySelector('#snk-dpad');

  function updatePauseBtn() {
    if (!pauseBtn) return;
    const show = Boolean(latestState.is_solo && latestState.phase === 'playing' && alive && !isSpectator);
    pauseBtn.classList.toggle('hidden', !show);
    pauseBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    pauseBtn.textContent = paused ? 'RESUME' : 'PAUSE';
  }

  function togglePause() {
    if (!latestState.is_solo || latestState.phase !== 'playing' || !alive || isSpectator) return;
    paused = !paused;
    sound.click();
    updatePauseBtn();
    draw();
  }

  pauseBtn?.addEventListener('click', togglePause);

  function spawnFood(body) {
    const occupied = new Set(body.map((s) => `${s.x},${s.y}`));
    const free = [];
    for (let x = 0; x < GRID; x++) {
      for (let y = 0; y < GRID; y++) {
        if (!occupied.has(`${x},${y}`)) free.push({ x, y });
      }
    }
    return free.length ? free[Math.floor(Math.random() * free.length)] : { x: 0, y: 0 };
  }

  function queueDir(nx, ny) {
    if (!alive || paused || isSpectator) return;
    const last = turnQueue.length ? turnQueue[turnQueue.length - 1] : dir;
    if (last.x + nx === 0 && last.y + ny === 0) return;
    if (last.x === nx && last.y === ny) return;
    if (turnQueue.length < 2) turnQueue.push({ x: nx, y: ny });
  }

  function handleDpadDir(d) {
    if (d === 'up') queueDir(0, -1);
    else if (d === 'down') queueDir(0, 1);
    else if (d === 'left') queueDir(-1, 0);
    else if (d === 'right') queueDir(1, 0);
  }

  function onKey(e) {
    const tag = document.activeElement?.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (document.querySelector('.modal-backdrop:not(.hidden)')) return;
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
      e.preventDefault();
    }
    const k = e.key.toLowerCase();
    if ((k === 'p' || k === ' ') && latestState.is_solo && latestState.phase === 'playing') {
      e.preventDefault();
      togglePause();
      return;
    }
    if (k === 'arrowup' || k === 'w') queueDir(0, -1);
    else if (k === 'arrowdown' || k === 's') queueDir(0, 1);
    else if (k === 'arrowleft' || k === 'a') queueDir(-1, 0);
    else if (k === 'arrowright' || k === 'd') queueDir(1, 0);
  }
  window.addEventListener('keydown', onKey);

  container.querySelectorAll('.dpad-btn').forEach((btn) => {
    btn.addEventListener('pointerdown', (e) => {
      if (e.button && e.button !== 0) return;
      e.preventDefault();
      handleDpadDir(btn.dataset.dir);
    });
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleDpadDir(btn.dataset.dir);
      }
    });
  });

  // Touch/pointer swipe controls on canvas
  let swipeOrigin = null;
  function onSwipeStart(x, y) {
    swipeOrigin = { x, y };
  }
  function onSwipeMove(x, y) {
    if (!swipeOrigin) return false;
    const dx = x - swipeOrigin.x;
    const dy = y - swipeOrigin.y;
    if (Math.abs(dx) < 22 && Math.abs(dy) < 22) return false;
    if (Math.abs(dx) > Math.abs(dy)) {
      queueDir(dx > 0 ? 1 : -1, 0);
    } else {
      queueDir(0, dy > 0 ? 1 : -1);
    }
    swipeOrigin = { x, y };
    return true;
  }
  const onCanvasPointerDown = (e) => {
    if (e.pointerType === 'touch') return; // Handled via touch events to block scroll
    if (e.button && e.button !== 0) return;
    onSwipeStart(e.clientX, e.clientY);
  };
  const onCanvasPointerMove = (e) => {
    if (e.pointerType === 'touch') return;
    onSwipeMove(e.clientX, e.clientY);
  };
  const onCanvasPointerEnd = () => {
    swipeOrigin = null;
  };
  const onCanvasTouchStart = (e) => {
    if (!e.touches.length) return;
    onSwipeStart(e.touches[0].clientX, e.touches[0].clientY);
  };
  const onCanvasTouchMove = (e) => {
    if (!e.touches.length) return;
    if (swipeOrigin) e.preventDefault();
    onSwipeMove(e.touches[0].clientX, e.touches[0].clientY);
  };
  const onCanvasTouchEnd = () => {
    swipeOrigin = null;
  };

  canvas.addEventListener('pointerdown', onCanvasPointerDown);
  canvas.addEventListener('pointermove', onCanvasPointerMove);
  canvas.addEventListener('pointerup', onCanvasPointerEnd);
  canvas.addEventListener('pointercancel', onCanvasPointerEnd);
  canvas.addEventListener('touchstart', onCanvasTouchStart, { passive: true });
  canvas.addEventListener('touchmove', onCanvasTouchMove, { passive: false });
  canvas.addEventListener('touchend', onCanvasTouchEnd);
  canvas.addEventListener('touchcancel', onCanvasTouchEnd);

  function draw() {
    const cell = canvas.width / GRID;
    const cs = getComputedStyle(document.documentElement);
    const accent = cs.getPropertyValue('--accent').trim() || '#e5484d';
    const bone = cs.getPropertyValue('--color-bone').trim() || '#ededed';

    ctx.fillStyle = '#0a0a0c';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Subtle coordinate grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 1;
    for (let i = 1; i < GRID; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cell, 0);
      ctx.lineTo(i * cell, canvas.height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cell);
      ctx.lineTo(canvas.width, i * cell);
      ctx.stroke();
    }

    // Accent-colored target food
    ctx.fillStyle = accent;
    ctx.fillRect(food.x * cell + 2, food.y * cell + 2, cell - 4, cell - 4);

    // Snow & Bone snake segments
    snake.forEach((seg, idx) => {
      ctx.fillStyle = !alive ? accent : idx === 0 ? '#ffffff' : bone;
      ctx.fillRect(seg.x * cell + 1, seg.y * cell + 1, cell - 2, cell - 2);
    });

    if (isSpectator) {
      ctx.fillStyle = 'rgba(10, 10, 12, 0.72)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = bone;
      ctx.font = '700 18px "DM Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('SPECTATOR VIEW', canvas.width / 2, canvas.height / 2);
    } else if (paused && latestState.phase === 'playing') {
      ctx.fillStyle = 'rgba(10, 10, 12, 0.65)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = accent;
      ctx.font = '700 24px "DM Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('PAUSED', canvas.width / 2, canvas.height / 2);
    }
  }

  function step() {
    if (!alive || paused || isSpectator || latestState.phase === 'finished') return;
    if (turnQueue.length) dir = turnQueue.shift();

    const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
    const hitWall = head.x < 0 || head.x >= GRID || head.y < 0 || head.y >= GRID;
    const hitSelf = snake.some((s) => s.x === head.x && s.y === head.y);

    if (hitWall || hitSelf) {
      alive = false;
      sound.capture();
      sendAction('sync', { score, length: snake.length, alive: false });
      updatePauseBtn();
      draw();
      return;
    }

    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      score += pointsPerFood;
      sound.click();
      food = spawnFood(snake);
    } else {
      snake.pop();
    }

    scoreEl.textContent = String(score);
    lenEl.textContent = String(snake.length);
    draw();
  }

  let moveInterval = setInterval(step, stepMs);
  const syncInterval = setInterval(() => {
    if (alive && !paused && !isSpectator && latestState.phase === 'playing') {
      sendAction('sync', { score, length: snake.length, alive: true });
    }
  }, 200);

  draw();

  return {
    update(publicState, _privateState, players) {
      latestState = publicState || {};
      latestPlayers = players || [];
      const meId = getPlayerId();
      const me = latestPlayers.find((p) => p.id === meId);
      isSpectator = Boolean(!me || me.role === 'spectator');
      if (dpadEl) dpadEl.classList.toggle('hidden', isSpectator);

      if (latestState.points_per_food) {
        pointsPerFood = Number(latestState.points_per_food) || 10;
      }
      if (diffEl && latestState.difficulty) {
        diffEl.textContent = String(latestState.difficulty).toUpperCase();
      }
      const nextStepMs = Number(latestState.step_ms) || 125;
      if (nextStepMs !== stepMs) {
        stepMs = nextStepMs;
        clearInterval(moveInterval);
        moveInterval = setInterval(step, stepMs);
      }
      if (latestState.phase === 'finished') {
        paused = true;
      }
      updatePauseBtn();
      timerEl.textContent = latestState.is_solo ? 'SOLO ENDLESS' : `${latestState.time_remaining ?? 0}s`;
      if (isSpectator || paused) draw();

      const snakes = latestState.snakes || {};
      const activePlayers = getActivePlayers(latestPlayers);
      const sorted = [...activePlayers].sort(
        (a, b) => (snakes[b.id]?.score || 0) - (snakes[a.id]?.score || 0)
      );
      rivalsEl.innerHTML = '';
      for (const p of sorted) {
        const s = snakes[p.id] || { score: 0, length: 3, alive: true };
        const row = document.createElement('div');
        row.className = `rival-row ${s.alive ? '' : 'dead'}`;
        const sc = Number(s.score) || 0;
        const ln = Number(s.length) || 3;
        row.innerHTML = `<span>${p.id === meId ? '★ ' : ''}${escapeHtml(p.name)}</span><span>${sc} PTS (LEN ${ln})</span>`;
        rivalsEl.appendChild(row);
      }
    },
    destroy() {
      clearInterval(moveInterval);
      clearInterval(syncInterval);
      window.removeEventListener('keydown', onKey);
      pauseBtn?.removeEventListener('click', togglePause);
      canvas.removeEventListener('pointerdown', onCanvasPointerDown);
      canvas.removeEventListener('pointermove', onCanvasPointerMove);
      canvas.removeEventListener('pointerup', onCanvasPointerEnd);
      canvas.removeEventListener('pointercancel', onCanvasPointerEnd);
      canvas.removeEventListener('touchstart', onCanvasTouchStart);
      canvas.removeEventListener('touchmove', onCanvasTouchMove);
      canvas.removeEventListener('touchend', onCanvasTouchEnd);
      canvas.removeEventListener('touchcancel', onCanvasTouchEnd);
    },
  };
}

