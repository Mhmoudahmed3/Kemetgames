/**
 * GLOBE PROTOCOL frontend module — 4 interactive world map game modes:
 * 1) Name -> Locate on Map
 * 2) Flag -> Pinpoint on Map
 * 3) Progressive Hints -> Find on Map
 * 4) Compare Two Countries -> Minimum Intermediate Land-Border Nations
 */

import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';
import { loadWorldAtlas, createInteractiveMap, heatFillColor } from '/js/world_map.js?v=20261112';

const MODE_LABELS = {
  name: 'LOCATE BY NAME',
  flag: 'FLAG PINPOINT',
  hint: 'HINT DETECTIVE',
  borders_between: 'BORDER BRIDGE',
};

function heatTier(heat, isCorrect = false) {
  if (isCorrect) return 'exact';
  const h = Number(heat) || 0;
  if (h >= 0.78) return 'hot';
  if (h >= 0.34) return 'warm';
  return 'far';
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let mapCtrl = null;
  let atlasData = null;
  let flownQuestionIdx = -1;
  let flownRevealIdx = -1;
  let lastTickSec = -1;
  let lastPromptSig = '';
  let lastMapSig = '';
  let destroyed = false;
  let latestPublic = {};
  let latestPrivate = {};
  let latestPlayers = getPlayers() || [];

  container.innerHTML = `
    <div class="globe-shell">
      <div class="game-statusbar">
        <span class="status-metric">ROUND <strong id="gl-round">1/8</strong></span>
        <span class="status-metric">MODE <strong id="gl-mode">—</strong></span>
        <span class="status-metric" id="gl-metric-mid">ATTEMPTS <strong id="gl-attempts">0/6</strong></span>
        <span class="status-metric">TIME <strong id="gl-time">40.0s</strong></span>
      </div>
      <div class="timer-bar-track"><div id="gl-bar" class="timer-bar-fill"></div></div>

      <div class="globe-prompt-banner glass-card">
        <div id="gl-prompt-content" class="globe-prompt-content">Loading world map...</div>
        <div id="gl-prompt-actions" class="globe-prompt-actions"></div>
      </div>

      <div class="globe-workspace">
        <div class="globe-map-panel glass-card">
          <div id="gl-map-host" class="globe-map-host">
            <div class="globe-loading">Projecting 197 sovereign territories...</div>
          </div>
          <div id="gl-guess-strip" class="globe-guess-strip"></div>
        </div>

        <aside class="globe-side-panel">
          <div id="gl-reveal-card" class="glass-card globe-side-card hidden"></div>
          <div class="glass-card globe-side-card">
            <div class="bunker-sublabel gl-sublabel-tight">HEATMAP LEGEND &amp; STANDINGS</div>
            <div class="heat-legend">
              <span class="legend-chip"><i class="gl-thermal-far"></i>Far</span>
              <span class="legend-chip"><i class="gl-thermal-warm"></i>Warm</span>
              <span class="legend-chip"><i class="gl-thermal-hot"></i>Hot</span>
              <span class="legend-chip"><i class="gl-thermal-exact"></i>Exact</span>
            </div>
            <div id="gl-standings" class="globe-standings-list"></div>
          </div>
        </aside>
      </div>
    </div>
  `;

  const roundEl = container.querySelector('#gl-round');
  const modeEl = container.querySelector('#gl-mode');
  const midMetricEl = container.querySelector('#gl-metric-mid');
  const timeEl = container.querySelector('#gl-time');
  const barEl = container.querySelector('#gl-bar');
  const promptContentEl = container.querySelector('#gl-prompt-content');
  const promptActionsEl = container.querySelector('#gl-prompt-actions');
  const mapHostEl = container.querySelector('#gl-map-host');
  const guessStripEl = container.querySelector('#gl-guess-strip');
  const revealCardEl = container.querySelector('#gl-reveal-card');
  const standingsEl = container.querySelector('#gl-standings');

  function flyForCurrentState() {
    if (!mapCtrl) return;
    const q = latestPublic.question || {};
    if (!q.index) return;
    const sub = latestPublic.subphase || 'question';
    const revealShown = sub === 'reveal' || latestPublic.phase === 'finished';
    const idx = q.index;

    if (sub === 'question' && flownQuestionIdx !== idx) {
      flownQuestionIdx = idx;
      if (q.mode === 'borders_between' && q.country_a && q.country_b && window.d3?.geoInterpolate) {
        const mid = window.d3.geoInterpolate(
          [q.country_a.lng, q.country_a.lat],
          [q.country_b.lng, q.country_b.lat]
        )(0.5);
        mapCtrl.flyTo(mid[1], mid[0], 1.15);
      }
    }

    if (revealShown && flownRevealIdx !== idx) {
      flownRevealIdx = idx;
      const rev = latestPublic.reveal || {};
      if (rev.target) {
        mapCtrl.flyTo(rev.target.lat, rev.target.lng, 1.8);
      } else if (rev.shortest_path && rev.shortest_path.length) {
        const midNode = rev.shortest_path[Math.floor(rev.shortest_path.length / 2)];
        mapCtrl.flyTo(midNode.lat, midNode.lng, 1.5);
      }
    }
  }

  loadWorldAtlas()
    .then((atlas) => {
      if (destroyed) return;
      atlasData = atlas;
      mapCtrl = createInteractiveMap(mapHostEl, atlas, {
        initialProjection: 'globe',
        onCountryClick(country) {
          const me = latestPlayers.find((p) => p.id === getPlayerId());
          if (!me || me.role === 'spectator') return;
          const q = latestPublic.question || {};
          if (latestPublic.subphase !== 'question' || latestPublic.phase !== 'playing') return;
          if (q.mode === 'borders_between') return;
          const priv = currentPrivateForRound(q);
          if (priv.solved || (priv.guesses || []).length >= (q.max_guesses || 6)) return;
          sound.click();
          sendAction('guess', { code: country.code });
        },
      });
      syncMapVisuals();
      flyForCurrentState();
    })
    .catch((err) => {
      if (destroyed) return;
      console.error('Failed to load Globe world atlas:', err);
      mapHostEl.innerHTML = '<div class="globe-loading">Unable to load world atlas. Reload to retry.</div>';
    });

  function currentPrivateForRound(q) {
    const roundIdx = (q.index || 1) - 1;
    if (latestPrivate.round_idx !== undefined && latestPrivate.round_idx !== roundIdx) {
      return {};
    }
    return latestPrivate;
  }

  function syncMapVisuals() {
    if (!mapCtrl || !atlasData) return;
    const q = latestPublic.question || {};
    const sub = latestPublic.subphase;
    const rev = latestPublic.reveal || {};
    const revealShown = sub === 'reveal' || latestPublic.phase === 'finished';
    const styles = {};
    const lines = [];

    if (q.mode === 'borders_between') {
      mapCtrl.setHideBorders(!revealShown);
      mapCtrl.setShowAllHoverNames(revealShown);
      const a = q.country_a;
      const b = q.country_b;
      if (a) {
        styles[a.code] = {
          fill: 'var(--accent)',
          stroke: '#FFFFFF',
          strokeWidth: 1.8,
          label: a.name,
          sublabel: 'Anchor Country A',
        };
      }
      if (b) {
        styles[b.code] = {
          fill: 'var(--accent)',
          stroke: '#FFFFFF',
          strokeWidth: 1.8,
          label: b.name,
          sublabel: 'Anchor Country B',
        };
      }

      if (revealShown && rev.shortest_path && rev.shortest_path.length >= 2) {
        const coords = [];
        rev.shortest_path.forEach((step, idx) => {
          coords.push([step.lng, step.lat]);
          if (idx > 0 && idx < rev.shortest_path.length - 1) {
            styles[step.code] = {
              fill: '#F59E0B',
              stroke: '#FFFFFF',
              strokeWidth: 1.5,
              label: step.name,
              sublabel: `Step ${idx} (${rev.min_between} between)`,
            };
          }
        });
        lines.push({ coordinates: coords, stroke: '#10B981', width: 3.2, dash: '' });
      } else if (a && b) {
        lines.push({
          coordinates: [
            [a.lng, a.lat],
            [b.lng, b.lat],
          ],
          stroke: 'var(--accent)',
          width: 2.2,
          dash: '6 5',
        });
      }
    } else {
      mapCtrl.setHideBorders(false);
      mapCtrl.setShowAllHoverNames(revealShown);

      const guesses = currentPrivateForRound(q).guesses || [];
      for (const g of guesses) {
        styles[g.code] = {
          fill: heatFillColor(g.heat, g.is_correct),
          stroke: '#FFFFFF',
          strokeWidth: g.is_correct ? 2 : 1.1,
          label: g.name,
          sublabel: g.is_correct ? 'Matched!' : `${Number(g.distance_km).toLocaleString()} km ${g.arrow || ''}`,
        };
      }

      if (revealShown && rev.target) {
        styles[rev.target.code] = {
          fill: '#10B981',
          stroke: '#FFFFFF',
          strokeWidth: 2.2,
          label: rev.target.name,
          sublabel: `Capital: ${rev.target.capital || '—'}`,
        };
      }
    }

    mapCtrl.setStyles(styles);
    mapCtrl.setLines(lines);
  }

  function renderPrompt(q, sub, priv, allPlayers, isSpectator) {
    const mode = q.mode;
    promptActionsEl.innerHTML = '';

    if (mode === 'name') {
      promptContentEl.innerHTML = `
        <div class="gl-prompt-eyebrow">LOCATE NATION ON THE MAP</div>
        <h3 class="gl-prompt-title">${escapeHtml(q.target_name || '')}</h3>
      `;
    } else if (mode === 'flag') {
      promptContentEl.innerHTML = `
        <div class="gl-flag-prompt">
          <img class="gl-flag-img" src="${escapeHtml(q.flag_svg || '')}" alt="Mystery country flag" />
          <div>
            <div class="gl-prompt-eyebrow">PINPOINT THIS FLAG</div>
            <p class="gl-prompt-sub">Click the nation matching this flag on the 3D Globe or 2D Map.</p>
          </div>
        </div>
      `;
    } else if (mode === 'hint') {
      const clues = priv.hints_visible && priv.hints_visible.length ? priv.hints_visible : q.starter_hints || [];
      const extraUsed = priv.extra_hints || 0;
      const clueHtml = clues
        .map((c, idx) => `<div class="gl-clue-pill"><span>0${idx + 1}</span><span>${escapeHtml(c)}</span></div>`)
        .join('');
      promptContentEl.innerHTML = `
        <div class="gl-full-width">
          <div class="gl-prompt-eyebrow">USE THE HINTS TO FIND THIS COUNTRY</div>
          <div class="gl-clues-grid">${clueHtml}</div>
        </div>
      `;
      if (!isSpectator && sub === 'question' && latestPublic.phase === 'playing' && !priv.solved && extraUsed < 2) {
        const hintBtn = document.createElement('button');
        hintBtn.type = 'button';
        hintBtn.className = 'pill-btn pill-btn-sm pill-btn-outline';
        hintBtn.textContent = `Reveal Extra Hint (-75 pts) · ${2 - extraUsed} left`;
        hintBtn.addEventListener('click', () => {
          sound.click();
          sendAction('reveal_hint', {});
        });
        promptActionsEl.appendChild(hintBtn);
      }
    } else if (mode === 'borders_between') {
      const a = q.country_a || {};
      const b = q.country_b || {};
      promptContentEl.innerHTML = `
        <div class="gl-compare-row">
          <div class="gl-country-chip">
            <img src="${escapeHtml(a.flag_svg || '')}" alt="${escapeHtml(a.name || '')}" class="gl-mini-flag" />
            <div><strong>${escapeHtml(a.name || '')}</strong><span>${escapeHtml(a.continent || '')}</span></div>
          </div>
          <span class="gl-vs-badge">↔ MIN NATIONS BETWEEN ↔</span>
          <div class="gl-country-chip">
            <img src="${escapeHtml(b.flag_svg || '')}" alt="${escapeHtml(b.name || '')}" class="gl-mini-flag" />
            <div><strong>${escapeHtml(b.name || '')}</strong><span>${escapeHtml(b.continent || '')}</span></div>
          </div>
        </div>
      `;

      const submitted = priv.between_guess;
      const lockedControl = isSpectator || (submitted !== null && submitted !== undefined);
      if (sub === 'question' && latestPublic.phase === 'playing' && !isSpectator) {
        const controls = document.createElement('div');
        controls.className = 'gl-between-controls';

        const quickWrap = document.createElement('div');
        quickWrap.className = 'gl-num-row';
        for (let n = 0; n <= 7; n++) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = `gl-num-btn ${submitted === n ? 'selected' : ''}`;
          btn.textContent = String(n);
          btn.disabled = lockedControl;
          btn.addEventListener('click', () => {
            sound.click();
            sendAction('answer_between', { count: n });
          });
          quickWrap.appendChild(btn);
        }

        const customForm = document.createElement('form');
        customForm.className = 'gl-num-form';
        customForm.innerHTML = `
          <label for="gl-between-input" class="sr-only">Custom country count</label>
          <input id="gl-between-input" name="between_count" type="number" min="0" max="20" placeholder="8+" class="text-input gl-num-input" ${lockedControl ? 'disabled' : ''} />
          <button type="submit" class="pill-btn pill-btn-sm" ${lockedControl ? 'disabled' : ''}>Lock In</button>
        `;
        customForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const val = Number(customForm.querySelector('#gl-between-input').value);
          if (!Number.isFinite(val) || val < 0 || val > 20) return;
          sound.click();
          sendAction('answer_between', { count: Math.round(val) });
        });

        controls.append(quickWrap, customForm);
        promptActionsEl.appendChild(controls);
      }
    }

    if (sub === 'reveal' && latestPublic.phase === 'playing' && !isSpectator) {
      const me = allPlayers.find((p) => p.id === getPlayerId());
      const activeCount = getActivePlayers(allPlayers).length;
      if (me?.is_host || activeCount <= 1) {
        const nextBtn = document.createElement('button');
        nextBtn.type = 'button';
        nextBtn.id = 'gl-next-btn';
        nextBtn.className = 'pill-btn pill-btn-md';
        nextBtn.textContent = 'Next Round →';
        nextBtn.addEventListener('click', () => {
          sound.click();
          sendAction('next', {});
        });
        promptActionsEl.appendChild(nextBtn);
      }
    }
  }

  return {
    update(publicState, privateState, players) {
      latestPublic = publicState || {};
      latestPrivate = privateState || {};
      latestPlayers = players || getPlayers() || [];

      const meId = getPlayerId();
      const me = latestPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const activePlayers = getActivePlayers(latestPlayers);

      const q = latestPublic.question || {};
      const sub = latestPublic.subphase || 'question';
      const revealShown = sub === 'reveal' || latestPublic.phase === 'finished';
      const rem = Number(latestPublic.time_remaining || 0);
      const dur = Number(latestPublic.duration || 40);

      roundEl.textContent = `${q.index || 1}/${q.total || 8}`;
      modeEl.textContent = MODE_LABELS[q.mode] || 'WORLD MAP';
      timeEl.textContent = sub === 'reveal' && latestPublic.phase === 'playing'
        ? `NEXT IN ${Math.max(0, Math.ceil(rem))}s`
        : `${rem.toFixed(1)}s`;
      barEl.style.width = sub === 'question' ? `${Math.max(0, Math.min(100, (rem / dur) * 100))}%` : '0%';

      if (sub === 'question' && latestPublic.phase === 'playing' && rem <= 5 && rem > 0) {
        const sec = Math.ceil(rem);
        if (sec !== lastTickSec) {
          lastTickSec = sec;
          sound.tick();
        }
      } else {
        lastTickSec = -1;
      }

      const priv = isSpectator ? {} : currentPrivateForRound(q);
      if (q.mode === 'borders_between') {
        const locked = priv.between_guess;
        midMetricEl.innerHTML = `LOCKED <strong>${isSpectator ? 'SPECTATING' : locked !== null && locked !== undefined ? escapeHtml(locked) : '—'}</strong>`;
      } else {
        const used = (priv.guesses || []).length;
        midMetricEl.innerHTML = isSpectator
          ? 'MODE <strong>SPECTATOR</strong>'
          : `ATTEMPTS <strong>${used}/${Number(q.max_guesses) || 6}</strong>`;
      }

      flyForCurrentState();

      const sig = `${q.index}:${sub}:${latestPublic.phase}:${isSpectator}:${Boolean(priv.solved)}:${priv.between_guess ?? ''}:${priv.extra_hints || 0}:${(priv.hints_visible || []).length}:${activePlayers.length}`;
      if (sig !== lastPromptSig) {
        lastPromptSig = sig;
        renderPrompt(q, sub, priv, latestPlayers, isSpectator);
      }

      const mapSig = `${q.index}:${sub}:${latestPublic.phase}:${priv.round_idx ?? ''}:${(priv.guesses || []).length}:${Boolean(latestPublic.reveal)}`;
      if (mapSig !== lastMapSig) {
        lastMapSig = mapSig;
        syncMapVisuals();
      }

      // Guided guess chips strip
      const guesses = priv.guesses || [];
      guessStripEl.innerHTML = '';
      if (q.mode !== 'borders_between') {
        if (isSpectator) {
          guessStripEl.innerHTML = '<span class="empty-ticker-msg">Spectator View — watching players pinpoint the target territory.</span>';
        } else if (!guesses.length) {
          guessStripEl.innerHTML = '<span class="empty-ticker-msg">Click any country or microstate pin on the globe to begin hunting.</span>';
        } else {
          for (const g of guesses) {
            const tier = heatTier(g.heat, g.is_correct);
            const pill = document.createElement('button');
            pill.type = 'button';
            pill.className = `gl-guess-chip heat-${tier}${g.is_correct ? ' is-correct' : ''}`;
            pill.innerHTML = `
              <span class="gl-heat-dot gl-thermal-${tier}"></span>
              <span>${escapeHtml(g.name)}</span>
              <strong>${g.is_correct ? 'FOUND!' : `${Number(g.distance_km).toLocaleString()} km ${escapeHtml(g.arrow || '')}`}</strong>
            `;
            pill.addEventListener('click', () => {
              if (mapCtrl) mapCtrl.flyTo(g.lat, g.lng, 1.6);
            });
            guessStripEl.appendChild(pill);
          }
        }
      } else if (revealShown && latestPublic.reveal?.shortest_path) {
        for (const step of latestPublic.reveal.shortest_path) {
          const badge = document.createElement('span');
          badge.className = 'gl-guess-chip';
          badge.innerHTML = `<img src="${escapeHtml(step.flag_svg || '')}" alt="" class="gl-tiny-flag" /><span>${escapeHtml(step.name)}</span>`;
          guessStripEl.appendChild(badge);
        }
      } else {
        guessStripEl.innerHTML = '<span class="empty-ticker-msg">Country borders are hidden — deduce the minimum intermediate nations connecting both highlights.</span>';
      }

      // Reveal dossier card (unified for reveal & finished)
      const rev = latestPublic.reveal;
      if (revealShown && rev) {
        revealCardEl.classList.remove('hidden');
        if (rev.target) {
          const t = rev.target;
          revealCardEl.innerHTML = `
            <div class="bunker-sublabel gl-sublabel-tight">TARGET NATION DOSSIER</div>
            <div class="gl-dossier-head">
              <img src="${escapeHtml(t.flag_svg || '')}" alt="${escapeHtml(t.name || '')}" class="gl-dossier-flag" />
              <div>
                <div class="gl-dossier-name">${escapeHtml(t.name)}</div>
                <div class="gl-dossier-meta">${escapeHtml(t.capital)} · ${escapeHtml(t.subregion)}</div>
              </div>
            </div>
            <div class="gl-stats-row">
              <span>Pop: <strong>${escapeHtml(t.population_label)}</strong> (#${Number(t.population_rank) || 0})</span>
              <span>Area: <strong>${escapeHtml(t.area_label)}</strong> (#${Number(t.area_rank) || 0})</span>
            </div>
            <p class="gl-dossier-trait">${escapeHtml(t.landmark_clue)}</p>
          `;
        } else {
          revealCardEl.innerHTML = `
            <div class="bunker-sublabel gl-sublabel-tight">SHORTEST BORDER BRIDGE</div>
            <div class="gl-bridge-count">${Number(rev.min_between) || 0} Nation(s) Between</div>
            <p class="gl-dossier-trait">${escapeHtml(rev.explanation)}</p>
          `;
        }
      } else {
        revealCardEl.classList.add('hidden');
      }

      // Standings & round_results breakdown (exclude spectators)
      const doneSet = new Set(latestPublic.done_players || []);
      const roundResults = latestPublic.round_results || {};
      const ranked = [...activePlayers].sort((a, b) => (b.score || 0) - (a.score || 0));
      standingsEl.innerHTML = '';
      for (const p of ranked) {
        const row = document.createElement('div');
        row.className = 'rival-row';
        const pts = Number(p.score) || 0;
        let status = 'ROUND END';
        if (sub === 'question' && latestPublic.phase === 'playing') {
          status = doneSet.has(p.id) ? 'DONE' : 'HUNTING';
        } else if (revealShown && roundResults[p.id]) {
          const res = roundResults[p.id];
          const rPts = Number(res.points) || 0;
          if (q.mode === 'borders_between') {
            const gLabel = res.between_guess !== null && res.between_guess !== undefined ? res.between_guess : '—';
            status = `Guess ${gLabel} · +${rPts} pts`;
          } else {
            const attLabel = res.solved ? `✓ ${Number(res.attempts) || 0} att` : `✗ ${Number(res.attempts) || 0} att`;
            status = `${attLabel} · +${rPts} pts`;
          }
        }
        row.innerHTML = `<span>${escapeHtml(p.name)}</span><span>${pts} PTS · ${escapeHtml(status)}</span>`;
        standingsEl.appendChild(row);
      }
    },
    destroy() {
      destroyed = true;
      if (mapCtrl) mapCtrl.destroy();
    },
  };
}
