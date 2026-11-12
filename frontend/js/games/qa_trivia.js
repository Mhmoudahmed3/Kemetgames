import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

function renderFlagSvg(flag) {
  if (!flag) return '';
  const c = (flag.colors || ['#000', '#fff', '#f00']).map((col) => escapeHtml(col));
  let inner = '';
  switch (flag.type) {
    case 'v3':
      inner = `<rect width="100" height="200" fill="${c[0]}"/><rect x="100" width="100" height="200" fill="${c[1]}"/><rect x="200" width="100" height="200" fill="${c[2]}"/>`;
      break;
    case 'v3_emblem':
      inner = `<rect width="100" height="200" fill="${c[0]}"/><rect x="100" width="100" height="200" fill="${c[1]}"/><rect x="200" width="100" height="200" fill="${c[2]}"/><circle cx="150" cy="100" r="22" fill="${c[3] || '#8b5a2b'}"/>`;
      break;
    case 'v2_offset':
      inner = `<rect width="120" height="200" fill="${c[0]}"/><rect x="120" width="180" height="200" fill="${c[1]}"/><circle cx="120" cy="100" r="30" fill="${c[2] || '#fc0'}"/>`;
      break;
    case 'v2_crescent':
      inner = `<rect width="150" height="200" fill="${c[0]}"/><rect x="150" width="150" height="200" fill="${c[1]}"/><circle cx="150" cy="100" r="36" fill="${c[2]}"/><circle cx="162" cy="100" r="28" fill="${c[1]}"/>`;
      break;
    case 'h2':
      inner = `<rect width="300" height="100" fill="${c[0]}"/><rect y="100" width="300" height="100" fill="${c[1]}"/>`;
      break;
    case 'h3':
      inner = `<rect width="300" height="67" fill="${c[0]}"/><rect y="67" width="300" height="67" fill="${c[1]}"/><rect y="133" width="300" height="67" fill="${c[2]}"/>`;
      break;
    case 'h3_wide':
      inner = `<rect width="300" height="50" fill="${c[0]}"/><rect y="50" width="300" height="100" fill="${c[1]}"/><rect y="150" width="300" height="50" fill="${c[2]}"/>`;
      break;
    case 'h3_topheavy':
      inner = `<rect width="300" height="100" fill="${c[0]}"/><rect y="100" width="300" height="50" fill="${c[1]}"/><rect y="150" width="300" height="50" fill="${c[2]}"/>`;
      break;
    case 'h3_emblem':
      inner = `<rect width="300" height="67" fill="${c[0]}"/><rect y="67" width="300" height="67" fill="${c[1]}"/><rect y="133" width="300" height="67" fill="${c[2]}"/><circle cx="150" cy="100" r="20" fill="${c[3] || '#cc0'}"/>`;
      break;
    case 'h3_wheel':
      inner = `<rect width="300" height="67" fill="${c[0]}"/><rect y="67" width="300" height="67" fill="${c[1]}"/><rect y="133" width="300" height="67" fill="${c[2]}"/><circle cx="150" cy="100" r="22" fill="none" stroke="${c[3]}" stroke-width="5"/>`;
      break;
    case 'h3_sun':
      inner = `<rect width="300" height="67" fill="${c[0]}"/><rect y="67" width="300" height="67" fill="${c[1]}"/><rect y="133" width="300" height="67" fill="${c[2]}"/><circle cx="150" cy="100" r="18" fill="${c[3]}"/>`;
      break;
    case 'h3_fimb':
      inner = `<rect width="300" height="60" fill="${c[0]}"/><rect y="60" width="300" height="80" fill="${c[3]}"/><rect y="70" width="300" height="60" fill="${c[1]}"/><rect y="140" width="300" height="60" fill="${c[2]}"/><ellipse cx="150" cy="100" rx="18" ry="30" fill="${c[1]}" stroke="${c[3]}" stroke-width="4"/>`;
      break;
    case 'swiss':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect x="128" y="45" width="44" height="110" fill="${c[1]}"/><rect x="95" y="78" width="110" height="44" fill="${c[1]}"/>`;
      break;
    case 'nordic':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect x="85" width="36" height="200" fill="${c[1]}"/><rect y="82" width="300" height="36" fill="${c[1]}"/>`;
      break;
    case 'nordic_double':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect x="80" width="46" height="200" fill="${c[1]}"/><rect y="77" width="300" height="46" fill="${c[1]}"/><rect x="91" width="24" height="200" fill="${c[2]}"/><rect y="88" width="300" height="24" fill="${c[2]}"/>`;
      break;
    case 'greece':
      inner = Array.from({ length: 9 }, (_, i) => `<rect y="${i * 22.2}" width="300" height="22.3" fill="${i % 2 === 0 ? c[0] : c[1]}"/>`).join('')
        + `<rect width="111" height="111" fill="${c[0]}"/><rect x="44" width="23" height="111" fill="${c[1]}"/><rect y="44" width="111" height="23" fill="${c[1]}"/>`;
      break;
    case 'uk':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><path d="M0,0 L300,200 M300,0 L0,200" stroke="${c[1]}" stroke-width="34"/><path d="M0,0 L300,200 M300,0 L0,200" stroke="${c[2]}" stroke-width="14"/><rect x="122" width="56" height="200" fill="${c[1]}"/><rect y="72" width="300" height="56" fill="${c[1]}"/><rect x="132" width="36" height="200" fill="${c[2]}"/><rect y="82" width="300" height="36" fill="${c[2]}"/>`;
      break;
    case 'crescent':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><circle cx="122" cy="100" r="46" fill="${c[1]}"/><circle cx="136" cy="100" r="36" fill="${c[0]}"/><polygon points="184,82 190,96 205,96 193,105 198,119 184,110 170,119 175,105 163,96 178,96" fill="${c[1]}"/>`;
      break;
    case 'solid_star':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><polygon points="150,48 164,88 206,88 172,113 185,153 150,128 115,153 128,113 94,88 136,88" fill="${c[1]}"/>`;
      break;
    case 'solid_stars':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><polygon points="56,36 64,58 88,58 68,72 76,94 56,80 36,94 44,72 24,58 48,58" fill="${c[1]}"/><circle cx="106" cy="34" r="6" fill="${c[1]}"/><circle cx="118" cy="54" r="6" fill="${c[1]}"/><circle cx="114" cy="78" r="6" fill="${c[1]}"/><circle cx="96" cy="94" r="6" fill="${c[1]}"/>`;
      break;
    case 'solid_badge':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect x="85" y="72" width="130" height="22" rx="8" fill="${c[1]}"/><rect x="90" y="114" width="120" height="10" fill="${c[1]}"/>`;
      break;
    case 'circle':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><circle cx="150" cy="100" r="54" fill="${c[1]}"/>`;
      break;
    case 'korea':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><circle cx="150" cy="100" r="46" fill="${c[1]}"/><path d="M104,100 A46,46 0 0,0 196,100 A23,23 0 0,0 150,100 A23,23 0 0,1 104,100 Z" fill="${c[2]}"/><rect x="46" y="42" width="38" height="8" transform="rotate(-35 65 46)" fill="${c[3]}"/><rect x="216" y="42" width="38" height="8" transform="rotate(35 235 46)" fill="${c[3]}"/><rect x="46" y="148" width="38" height="8" transform="rotate(35 65 152)" fill="${c[3]}"/><rect x="216" y="148" width="38" height="8" transform="rotate(-35 235 152)" fill="${c[3]}"/>`;
      break;
    case 'thailand':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect y="33" width="300" height="134" fill="${c[1]}"/><rect y="66" width="300" height="68" fill="${c[2]}"/>`;
      break;
    case 'canada':
      inner = `<rect width="75" height="200" fill="${c[0]}"/><rect x="75" width="150" height="200" fill="${c[1]}"/><rect x="225" width="75" height="200" fill="${c[0]}"/><polygon points="150,48 164,84 196,76 176,108 192,130 156,126 156,154 144,154 144,126 108,130 124,108 104,76 136,84" fill="${c[0]}"/>`;
      break;
    case 'brazil':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><polygon points="150,26 266,100 150,174 34,100" fill="${c[1]}"/><circle cx="150" cy="100" r="40" fill="${c[2]}"/><path d="M112,95 Q150,82 188,105" fill="none" stroke="#fff" stroke-width="6"/>`;
      break;
    case 'chile':
      inner = `<rect width="300" height="100" fill="${c[1]}"/><rect y="100" width="300" height="100" fill="${c[2]}"/><rect width="105" height="100" fill="${c[0]}"/><polygon points="52,25 59,45 80,45 63,57 69,77 52,65 35,77 41,57 24,45 45,45" fill="${c[1]}"/>`;
      break;
    case 'za':
      inner = `<rect width="300" height="100" fill="${c[0]}"/><rect y="100" width="300" height="100" fill="${c[1]}"/><polygon points="0,0 130,85 300,85 300,115 130,115 0,200" fill="${c[5]}"/><polygon points="0,14 122,92 300,92 300,108 122,108 0,186" fill="${c[2]}"/><polygon points="0,30 92,100 0,170" fill="${c[3]}"/><polygon points="0,46 72,100 0,154" fill="${c[4]}"/>`;
      break;
    case 'canton_stars':
      inner = `<rect width="300" height="200" fill="${c[0]}"/><rect width="130" height="90" fill="${c[0]}"/><path d="M0,0 L130,90 M130,0 L0,90" stroke="${c[1]}" stroke-width="14"/><rect x="55" width="20" height="90" fill="${c[1]}"/><rect y="35" width="130" height="20" fill="${c[1]}"/><rect x="59" width="12" height="90" fill="${c[2]}"/><rect y="39" width="130" height="12" fill="${c[2]}"/><circle cx="215" cy="52" r="9" fill="${c[1]}"/><circle cx="245" cy="94" r="9" fill="${c[1]}"/><circle cx="195" cy="112" r="9" fill="${c[1]}"/><circle cx="218" cy="152" r="10" fill="${c[1]}"/>`;
      break;
    case 'stripes_canton':
      inner = Array.from({ length: 13 }, (_, i) => `<rect y="${i * 15.4}" width="300" height="15.5" fill="${i % 2 === 0 ? c[0] : c[1]}"/>`).join('')
        + `<rect width="130" height="108" fill="${c[2]}"/><circle cx="32" cy="28" r="5" fill="${c[1]}"/><circle cx="65" cy="28" r="5" fill="${c[1]}"/><circle cx="98" cy="28" r="5" fill="${c[1]}"/><circle cx="48" cy="54" r="5" fill="${c[1]}"/><circle cx="82" cy="54" r="5" fill="${c[1]}"/><circle cx="32" cy="80" r="5" fill="${c[1]}"/><circle cx="65" cy="80" r="5" fill="${c[1]}"/><circle cx="98" cy="80" r="5" fill="${c[1]}"/>`;
      break;
    default:
      inner = `<rect width="300" height="200" fill="${c[0]}"/><circle cx="150" cy="100" r="40" fill="${c[1] || '#fff'}"/>`;
  }
  return `<svg viewBox="0 0 300 200" width="100%" height="100%" preserveAspectRatio="none">${inner}</svg>`;
}

const MODE_LABELS = {
  flag: 'FLAG ID',
  capital: 'CAPITAL MATCH',
  borders: 'BORDER DETECTIVE',
  mystery: '3-CLUE MYSTERY',
  population_area: 'POPULATION & SIZE',
  characteristics: 'COUNTRY TRAITS',
};

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let myChoice = null;
  let lastRoundIdx = -1;
  let lastTickSec = -1;
  let renderedVisualKey = '';
  let renderedCluesKey = '';
  let renderedOptionsKey = '';

  container.innerHTML = `
    <div class="trivia-shell">
      <div class="game-statusbar">
        <span class="status-metric">ROUND <strong id="qa-round">1/10</strong></span>
        <span class="status-metric">CATEGORY <strong id="qa-cat">—</strong></span>
        <span class="status-metric">TIME <strong id="qa-time">15.0s</strong></span>
      </div>
      <div class="timer-bar-track"><div id="qa-bar" class="timer-bar-fill"></div></div>
      <div class="question-box">
        <div id="qa-visual"></div>
        <h3 id="qa-question" class="qa-question-title"></h3>
        <div id="qa-clues" class="clue-stack hidden"></div>
        <div id="qa-options" class="options-grid"></div>
        <div id="qa-explain" class="clue-item qa-explain hidden"></div>
        <div id="qa-next-wrap" class="qa-next-wrap hidden">
          <button type="button" id="qa-next-btn" class="pill-btn pill-btn-md">NEXT QUESTION →</button>
        </div>
      </div>
      <div class="rival-panel">
        <div class="bunker-sublabel">LIVE SCOREBOARD</div>
        <div id="qa-standings"></div>
      </div>
    </div>
  `;

  const roundEl = container.querySelector('#qa-round');
  const catEl = container.querySelector('#qa-cat');
  const timeEl = container.querySelector('#qa-time');
  const barEl = container.querySelector('#qa-bar');
  const visualEl = container.querySelector('#qa-visual');
  const qEl = container.querySelector('#qa-question');
  const cluesEl = container.querySelector('#qa-clues');
  const optsEl = container.querySelector('#qa-options');
  const explainEl = container.querySelector('#qa-explain');
  const nextWrap = container.querySelector('#qa-next-wrap');
  const nextBtn = container.querySelector('#qa-next-btn');
  const standingsEl = container.querySelector('#qa-standings');

  const onNextClick = () => {
    sound.click();
    sendAction('next', {});
  };
  nextBtn.addEventListener('click', onNextClick);

  return {
    update(publicState, _privateState, players) {
      const q = publicState.question || {};
      if (q.index !== lastRoundIdx) {
        lastRoundIdx = q.index;
        myChoice = null;
      }

      const allPlayers = players || getPlayers() || [];
      const meId = getPlayerId();
      const me = allPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const activePlayers = getActivePlayers(allPlayers);

      const sub = publicState.subphase;
      const rem = Number(publicState.time_remaining || 0);
      const dur = Number(publicState.question_duration || publicState.duration || 15);
      roundEl.textContent = `${q.index || 1}/${q.total || 10}`;

      const modeTag = MODE_LABELS[q.mode];
      const baseCat = (q.category || 'GENERAL').toUpperCase();
      catEl.textContent = modeTag && !baseCat.includes(modeTag) ? `${baseCat} · ${modeTag}` : (modeTag || baseCat);

      if (sub === 'reveal' && publicState.phase === 'playing') {
        timeEl.textContent = `NEXT IN ${Math.max(0, Math.ceil(rem))}s`;
      } else {
        timeEl.textContent = `${rem.toFixed(1)}s`;
      }
      barEl.style.width = sub === 'question' ? `${Math.max(0, Math.min(100, (rem / dur) * 100))}%` : '0%';

      if (sub === 'question' && rem <= 5 && rem > 0) {
        const sec = Math.ceil(rem);
        if (sec !== lastTickSec) {
          lastTickSec = sec;
          sound.tick();
        }
      } else {
        lastTickSec = -1;
      }

      const visualKey = q.mode === 'flag' ? `${q.index}:${q.flag_svg || q.flag_code || 'fallback'}` : `${q.index}:none`;
      if (visualKey !== renderedVisualKey) {
        renderedVisualKey = visualKey;
        visualEl.innerHTML = '';
        if (q.mode === 'flag' && (q.flag_svg || q.flag)) {
          const frame = document.createElement('div');
          frame.className = 'country-flag-frame';
          if (q.flag_svg) {
            const img = document.createElement('img');
            img.className = 'country-flag-img';
            img.alt = 'Country flag';
            img.src = q.flag_svg;
            img.addEventListener('error', () => {
              frame.innerHTML = renderFlagSvg(q.flag);
            }, { once: true });
            frame.appendChild(img);
          } else {
            frame.innerHTML = renderFlagSvg(q.flag);
          }
          visualEl.appendChild(frame);
        }
      }

      qEl.textContent = q.question || q.prompt || '';

      const cluesKey = `${q.index}:${(q.clues || []).length}`;
      if (cluesKey !== renderedCluesKey) {
        renderedCluesKey = cluesKey;
        if (q.clues && q.clues.length) {
          cluesEl.classList.remove('hidden');
          cluesEl.innerHTML = '';
          for (const clue of q.clues) {
            const item = document.createElement('div');
            item.className = 'clue-item';
            item.textContent = clue;
            cluesEl.appendChild(item);
          }
        } else {
          cluesEl.classList.add('hidden');
          cluesEl.innerHTML = '';
        }
      }

      const lockedSet = new Set(publicState.locked_players || []);
      const meLocked = lockedSet.has(meId);
      const results = publicState.round_results || {};
      const resolvedChoice = results[meId]?.choice ?? myChoice;

      const optionsKey = `${q.index}:${(q.options || []).join('|')}`;
      if (optionsKey !== renderedOptionsKey) {
        renderedOptionsKey = optionsKey;
        optsEl.innerHTML = '';
        (q.options || []).forEach((label, idx) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'option-btn';
          btn.textContent = `${String.fromCharCode(65 + idx)}. ${label}`;
          btn.addEventListener('click', () => {
            if (btn.disabled) return;
            myChoice = idx;
            sound.click();
            sendAction('answer', { choice: idx });
          });
          optsEl.appendChild(btn);
        });
      }

      const revealState = sub === 'reveal' || publicState.phase === 'finished';
      Array.from(optsEl.children).forEach((btn, idx) => {
        btn.classList.toggle('selected', resolvedChoice === idx);
        btn.classList.toggle('correct', revealState && idx === q.correct_index);
        btn.classList.toggle('wrong', revealState && resolvedChoice === idx && idx !== q.correct_index);
        btn.disabled = isSpectator || revealState || meLocked;
      });

      if (revealState && (q.explanation || q.country_stats)) {
        explainEl.classList.remove('hidden');
        explainEl.innerHTML = '';
        const myRes = !isSpectator ? results[meId] : null;
        const prefix = myRes ? (myRes.is_correct ? `+${myRes.points} PTS — ` : 'INCORRECT — ') : '';
        if (q.explanation) {
          const expLine = document.createElement('div');
          expLine.textContent = `${prefix}${q.explanation}`;
          explainEl.appendChild(expLine);
        }
        if (q.country_stats) {
          const st = q.country_stats;
          const statsLine = document.createElement('div');
          statsLine.className = 'game-sub-label';
          const parts = [
            st.name,
            st.capital ? `Capital: ${st.capital}` : null,
            st.subregion,
            st.population ? `Pop: ${st.population}` : null,
            st.area ? `Area: ${st.area}` : null,
            st.trait,
          ].filter(Boolean);
          statsLine.textContent = parts.join(' · ');
          explainEl.appendChild(statsLine);
        }
        nextWrap.classList.toggle(
          'hidden',
          isSpectator || sub !== 'reveal' || publicState.phase !== 'playing' || !(me?.is_host || activePlayers.length <= 1)
        );
      } else {
        explainEl.classList.add('hidden');
        explainEl.innerHTML = '';
        nextWrap.classList.add('hidden');
      }

      const ranked = [...activePlayers].sort((a, b) => (b.score || 0) - (a.score || 0));
      standingsEl.innerHTML = '';
      for (const p of ranked) {
        const row = document.createElement('div');
        row.className = 'rival-row';
        const pts = Number(p.score) || 0;
        const status = sub === 'question' ? (lockedSet.has(p.id) ? 'LOCKED' : 'THINKING') : `${pts} PTS`;
        row.innerHTML = `<span>${escapeHtml(p.name)}</span><span>${pts} PTS · ${status}</span>`;
        standingsEl.appendChild(row);
      }
    },
    destroy() {
      nextBtn.removeEventListener('click', onNextClick);
    },
  };
}
