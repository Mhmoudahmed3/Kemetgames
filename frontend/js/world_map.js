import { escapeHtml } from '/js/utils.js?v=20261112';

/**
 * Shared self-hosted 3D Orthographic Globe & 2D Natural Earth Vector Map controller
 * powered by d3-geo, topojson-client, /data/world-110m.json, and /api/countries.
 */

let _atlasPromise = null;

export async function loadWorldAtlas() {
  if (_atlasPromise) return _atlasPromise;
  _atlasPromise = (async () => {
    try {
      const [topoRes, countriesRes] = await Promise.all([
        fetch('/data/world-110m.json'),
        fetch('/api/countries'),
      ]);
      if (!topoRes.ok || !countriesRes.ok) {
        throw new Error(`Atlas fetch failed (${topoRes.status}/${countriesRes.status})`);
      }
      const [topo, countriesJson] = await Promise.all([
        topoRes.json(),
        countriesRes.json(),
      ]);
      const countryList = countriesJson.countries || [];
      const countriesByCode = {};
      const countriesByCcn3 = {};
      for (const c of countryList) {
        countriesByCode[c.code] = c;
        if (c.ccn3) {
          countriesByCcn3[String(c.ccn3).padStart(3, '0')] = c;
        }
      }
      const geo = window.topojson.feature(topo, topo.objects.countries);
      const landFeature = topo.objects.land
        ? window.topojson.feature(topo, topo.objects.land)
        : null;
      const features = (geo.features || []).map((f) => {
        const ccn3 = f.id ? String(f.id).padStart(3, '0') : '';
        const country = ccn3 ? countriesByCcn3[ccn3] || null : null;
        return { feature: f, ccn3, country };
      });
      return { features, landFeature, countryList, countriesByCode, countriesByCcn3 };
    } catch (err) {
      _atlasPromise = null;
      throw err;
    }
  })();
  return _atlasPromise;
}

export function heatFillColor(heat, isCorrect = false) {
  if (isCorrect) return '#10B981';
  if (heat >= 0.78) return 'rgba(239, 68, 68, 0.85)';
  if (heat >= 0.56) return 'rgba(245, 158, 11, 0.78)';
  if (heat >= 0.34) return 'rgba(234, 179, 8, 0.58)';
  if (heat >= 0.18) return 'rgba(56, 189, 248, 0.52)';
  return 'rgba(99, 102, 241, 0.48)';
}

export function createInteractiveMap(containerEl, atlas, options = {}) {
  const width = options.width || 920;
  const height = options.height || 520;
  let projMode = options.initialProjection || 'globe'; // 'globe' | 'flat'
  let rot = [-12, -20, 0];
  let zoom = projMode === 'globe' ? 1.0 : 1.0;
  let flatPan = [0, 0];
  let flyAnimId = null;

  let countryStyles = {}; // code -> { fill, stroke, strokeWidth, label, sublabel }
  let linesData = []; // [{ coordinates: [[lng, lat], ...], stroke, dash, width }]
  let showAllHoverNames = Boolean(options.showAllHoverNames);
  let hideBorders = Boolean(options.hideBorders);
  let onCountryClick = options.onCountryClick || null;

  containerEl.innerHTML = `
    <div class="globe-canvas-stage">
      <svg class="globe-svg" viewBox="0 0 ${width} ${height}" aria-label="Interactive World Map"></svg>
      <div class="globe-map-controls">
        ${options.hideProjectionToggle ? '' : `
          <div class="globe-proj-switch" role="group" aria-label="Map Projection">
            <button type="button" class="globe-ctrl-btn ${projMode === 'globe' ? 'active' : ''}" data-proj="globe">3D Globe</button>
            <button type="button" class="globe-ctrl-btn ${projMode === 'flat' ? 'active' : ''}" data-proj="flat">2D Map</button>
          </div>
        `}
        <div class="globe-zoom-group">
          <button type="button" class="globe-ctrl-btn" data-zoom="in" title="Zoom In" aria-label="Zoom In">+</button>
          <button type="button" class="globe-ctrl-btn" data-zoom="out" title="Zoom Out" aria-label="Zoom Out">−</button>
          <button type="button" class="globe-ctrl-btn" data-zoom="reset" title="Reset View" aria-label="Reset View">⟲</button>
        </div>
      </div>
      <div class="globe-hover-tooltip hidden"></div>
    </div>
  `;

  const svg = containerEl.querySelector('.globe-svg');
  const tooltipEl = containerEl.querySelector('.globe-hover-tooltip');
  const ns = 'http://www.w3.org/2000/svg';

  const defs = document.createElementNS(ns, 'defs');
  defs.innerHTML = `
    <radialGradient id="globeSphereBg-${Math.random().toString(36).slice(2, 7)}" cx="38%" cy="32%" r="68%">
      <stop offset="0%" stop-color="rgba(255,255,255,0.10)"/>
      <stop offset="55%" stop-color="rgba(20,22,28,0.86)"/>
      <stop offset="100%" stop-color="rgba(8,9,12,0.98)"/>
    </radialGradient>
  `;
  const gradId = defs.querySelector('radialGradient').id;
  svg.appendChild(defs);

  const gSphere = document.createElementNS(ns, 'g');
  const gGrat = document.createElementNS(ns, 'g');
  const gLand = document.createElementNS(ns, 'g');
  const gCountries = document.createElementNS(ns, 'g');
  const gLines = document.createElementNS(ns, 'g');
  const gPins = document.createElementNS(ns, 'g');
  svg.append(gSphere, gGrat, gLand, gCountries, gLines, gPins);

  const sphereCircle = document.createElementNS(ns, 'circle');
  sphereCircle.setAttribute('class', 'globe-ocean-sphere');
  sphereCircle.setAttribute('fill', `url(#${gradId})`);
  gSphere.appendChild(sphereCircle);

  const gratPath = document.createElementNS(ns, 'path');
  gratPath.setAttribute('class', 'globe-graticule');
  gGrat.appendChild(gratPath);

  const landPath = document.createElementNS(ns, 'path');
  landPath.setAttribute('class', 'globe-land-mass');
  gLand.appendChild(landPath);

  const pathNodes = [];
  for (const item of atlas.features) {
    const p = document.createElementNS(ns, 'path');
    p.setAttribute('class', item.country ? 'map-country playable' : 'map-country ambient');
    if (item.country) {
      p.dataset.code = item.country.code;
      p.setAttribute('tabindex', '0');
      p.setAttribute('role', 'button');
      p.setAttribute('aria-label', item.country.name);
    }
    gCountries.appendChild(p);
    pathNodes.push({ node: p, feature: item.feature, country: item.country });
  }

  // Clickable microstate & small island pin markers
  const pinCountries = atlas.countryList.filter((c) => !c.has_110m_polygon || c.area_km2 < 4500);
  const pinNodes = [];
  for (const c of pinCountries) {
    const circle = document.createElementNS(ns, 'circle');
    circle.setAttribute('class', c.has_110m_polygon ? 'map-pin-dot small-nation' : 'map-pin-dot microstate');
    circle.setAttribute('r', c.has_110m_polygon ? '3.5' : '4.5');
    circle.dataset.code = c.code;
    circle.setAttribute('tabindex', '0');
    circle.setAttribute('role', 'button');
    circle.setAttribute('aria-label', c.name);
    gPins.appendChild(circle);
    pinNodes.push({ node: circle, country: c });
  }

  function cancelFly() {
    if (flyAnimId) {
      cancelAnimationFrame(flyAnimId);
      flyAnimId = null;
    }
  }

  const graticuleData = window.d3.geoGraticule10();

  function buildProjection() {
    if (projMode === 'globe') {
      const baseScale = Math.min(width, height) * 0.44;
      return window.d3
        .geoOrthographic()
        .scale(baseScale * zoom)
        .translate([width / 2, height / 2])
        .clipAngle(90)
        .rotate(rot);
    }
    const baseFlat = Math.min(width / 5.4, height / 2.85);
    return window.d3
      .geoNaturalEarth1()
      .scale(baseFlat * zoom)
      .translate([width / 2 + flatPan[0], height / 2 + 12 + flatPan[1]]);
  }

  function render() {
    const projection = buildProjection();
    const geoPath = window.d3.geoPath(projection);

    if (projMode === 'globe') {
      const r = projection.scale();
      sphereCircle.style.display = '';
      sphereCircle.setAttribute('cx', String(width / 2));
      sphereCircle.setAttribute('cy', String(height / 2));
      sphereCircle.setAttribute('r', String(r));
    } else {
      sphereCircle.style.display = 'none';
    }

    gratPath.setAttribute('d', geoPath(graticuleData) || '');

    svg.classList.toggle('borderless', hideBorders);
    if (hideBorders && atlas.landFeature) {
      landPath.style.display = '';
      landPath.setAttribute('d', geoPath(atlas.landFeature) || '');
    } else {
      landPath.style.display = 'none';
    }

    for (const entry of pathNodes) {
      const d = geoPath(entry.feature) || '';
      entry.node.setAttribute('d', d);
      const st = entry.country ? countryStyles[entry.country.code] : null;
      if (st) {
        entry.node.style.fill = st.fill || '';
        entry.node.style.stroke = st.stroke || '';
        entry.node.style.strokeWidth = st.strokeWidth ? String(st.strokeWidth) : '';
        entry.node.classList.add('styled');
      } else {
        entry.node.style.fill = '';
        entry.node.style.stroke = '';
        entry.node.style.strokeWidth = '';
        entry.node.classList.remove('styled');
      }
    }

    gLines.innerHTML = '';
    for (const line of linesData) {
      if (!line.coordinates || line.coordinates.length < 2) continue;
      const d = geoPath({ type: 'LineString', coordinates: line.coordinates }) || '';
      if (!d) continue;
      const lp = document.createElementNS(ns, 'path');
      lp.setAttribute('d', d);
      lp.setAttribute('class', 'globe-arc-line');
      lp.setAttribute('stroke', line.stroke || 'var(--accent)');
      lp.setAttribute('stroke-width', String(line.width || 2.5));
      if (line.dash) lp.setAttribute('stroke-dasharray', line.dash);
      gLines.appendChild(lp);
    }

    const centerGeo = projMode === 'globe' ? [-rot[0], -rot[1]] : null;
    for (const pin of pinNodes) {
      const coords = [pin.country.lng, pin.country.lat];
      if (projMode === 'globe' && window.d3.geoDistance(coords, centerGeo) > Math.PI / 2 - 0.04) {
        pin.node.style.display = 'none';
        continue;
      }
      const pt = projection(coords);
      if (!pt || Number.isNaN(pt[0]) || Number.isNaN(pt[1])) {
        pin.node.style.display = 'none';
        continue;
      }
      pin.node.style.display = '';
      pin.node.setAttribute('cx', pt[0].toFixed(1));
      pin.node.setAttribute('cy', pt[1].toFixed(1));
      const st = countryStyles[pin.country.code];
      pin.node.style.fill = st?.fill || '';
      pin.node.style.stroke = st?.stroke || '';
      pin.node.classList.toggle('styled', Boolean(st));
    }
  }

  function showTooltip(clientX, clientY, country) {
    if (!country) {
      tooltipEl.classList.add('hidden');
      return;
    }
    const st = countryStyles[country.code];
    const allowName = showAllHoverNames || Boolean(st && st.label);
    if (!allowName) {
      tooltipEl.classList.add('hidden');
      return;
    }
    const rect = containerEl.getBoundingClientRect();
    const x = Math.min(rect.width - 170, Math.max(12, clientX - rect.left + 12));
    const y = Math.min(rect.height - 54, Math.max(12, clientY - rect.top - 36));
    tooltipEl.style.left = `${x}px`;
    tooltipEl.style.top = `${y}px`;
    tooltipEl.innerHTML = `
      <img src="${escapeHtml(country.flag_svg)}" alt="" class="tooltip-flag" />
      <div>
        <div class="tooltip-name">${escapeHtml(country.name)}</div>
        ${st?.sublabel ? `<div class="tooltip-sub">${escapeHtml(st.sublabel)}</div>` : ''}
      </div>
    `;
    tooltipEl.classList.remove('hidden');
  }

  // Pointer drag + click distinction (defer pointer capture until drag starts so clicks keep exact target)
  let dragging = false;
  let dragMoved = false;
  let captured = false;
  let downPointerType = 'mouse';
  let downCode = null;
  let startX = 0;
  let startY = 0;
  let startRot = [...rot];
  let startPan = [...flatPan];

  function extractCountryCode(target) {
    if (!target || typeof target.closest !== 'function') {
      return target?.dataset?.code || null;
    }
    return target.closest('[data-code]')?.dataset?.code || null;
  }

  svg.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    cancelFly();
    dragging = true;
    dragMoved = false;
    captured = false;
    downPointerType = e.pointerType || 'mouse';
    downCode = extractCountryCode(e.target);
    startX = e.clientX;
    startY = e.clientY;
    startRot = [...rot];
    startPan = [...flatPan];
  });

  svg.addEventListener('pointermove', (e) => {
    if (dragging) {
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      const threshold = downPointerType === 'touch' ? 8 : 6;
      if (!dragMoved && Math.hypot(dx, dy) > threshold) {
        dragMoved = true;
        tooltipEl.classList.add('hidden');
        try {
          svg.setPointerCapture(e.pointerId);
          captured = true;
        } catch {}
      }
      if (dragMoved) {
        if (projMode === 'globe') {
          const sens = 0.28 / zoom;
          rot = [
            startRot[0] + dx * sens,
            Math.max(-85, Math.min(85, startRot[1] - dy * sens)),
            0,
          ];
        } else {
          flatPan = [startPan[0] + dx, startPan[1] + dy];
        }
        render();
      }
      return;
    }

    const code = extractCountryCode(e.target);
    if (code && atlas.countriesByCode[code]) {
      showTooltip(e.clientX, e.clientY, atlas.countriesByCode[code]);
    } else {
      tooltipEl.classList.add('hidden');
    }
  });

  svg.addEventListener('pointerup', (e) => {
    if (!dragging) return;
    dragging = false;
    if (captured) {
      try { svg.releasePointerCapture(e.pointerId); } catch {}
      captured = false;
    }
    if (!dragMoved) {
      const hitEl = document.elementFromPoint(e.clientX, e.clientY);
      const code = extractCountryCode(e.target) || extractCountryCode(hitEl) || downCode;
      if (code && atlas.countriesByCode[code] && onCountryClick) {
        onCountryClick(atlas.countriesByCode[code]);
      }
    }
    downCode = null;
  });

  svg.addEventListener('pointercancel', (e) => {
    dragging = false;
    downCode = null;
    if (captured) {
      try { svg.releasePointerCapture(e.pointerId); } catch {}
      captured = false;
    }
  });

  svg.addEventListener('pointerleave', () => {
    tooltipEl.classList.add('hidden');
  });

  svg.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const code = extractCountryCode(e.target);
    if (code && atlas.countriesByCode[code] && onCountryClick) {
      e.preventDefault();
      onCountryClick(atlas.countriesByCode[code]);
    }
  });

  svg.addEventListener('focusin', (e) => {
    const code = extractCountryCode(e.target);
    if (code && atlas.countriesByCode[code]) {
      const r = e.target.getBoundingClientRect();
      showTooltip(r.left + r.width / 2, r.top + r.height / 2, atlas.countriesByCode[code]);
    }
  });

  svg.addEventListener('focusout', () => {
    tooltipEl.classList.add('hidden');
  });

  svg.addEventListener('wheel', (e) => {
    e.preventDefault();
    cancelFly();
    const factor = e.deltaY < 0 ? 1.16 : 0.86;
    zoom = Math.max(0.85, Math.min(6.0, zoom * factor));
    render();
  }, { passive: false });

  containerEl.querySelectorAll('[data-proj]').forEach((btn) => {
    btn.addEventListener('click', () => {
      cancelFly();
      projMode = btn.dataset.proj;
      containerEl.querySelectorAll('[data-proj]').forEach((b) =>
        b.classList.toggle('active', b.dataset.proj === projMode)
      );
      zoom = 1.0;
      flatPan = [0, 0];
      render();
    });
  });

  containerEl.querySelectorAll('[data-zoom]').forEach((btn) => {
    btn.addEventListener('click', () => {
      cancelFly();
      const action = btn.dataset.zoom;
      if (action === 'in') zoom = Math.min(6.0, zoom * 1.32);
      else if (action === 'out') zoom = Math.max(0.85, zoom / 1.32);
      else {
        zoom = 1.0;
        flatPan = [0, 0];
        rot = [-12, -20, 0];
      }
      render();
    });
  });

  function flyTo(lat, lng, targetZoom = null) {
    cancelFly();
    if (projMode !== 'globe') {
      const proj = window.d3.geoNaturalEarth1().scale(Math.min(width / 5.4, height / 2.85) * (targetZoom || zoom)).translate([width / 2, height / 2 + 12]);
      const pt = proj([lng, lat]);
      if (pt) {
        if (targetZoom) zoom = targetZoom;
        flatPan = [width / 2 - pt[0], height / 2 - pt[1]];
      }
      render();
      return;
    }

    const fromRot = [...rot];
    const toRot = [-lng, -Math.max(-75, Math.min(75, lat)), 0];
    // Shortest longitude delta
    let dLon = ((toRot[0] - fromRot[0] + 540) % 360) - 180;
    const fromZoom = zoom;
    const toZoom = targetZoom || zoom;
    const startTs = performance.now();
    const dur = 520;

    function step(now) {
      const t = Math.min(1, (now - startTs) / dur);
      const ease = 1 - Math.pow(1 - t, 3);
      rot = [fromRot[0] + dLon * ease, fromRot[1] + (toRot[1] - fromRot[1]) * ease, 0];
      zoom = fromZoom + (toZoom - fromZoom) * ease;
      render();
      if (t < 1) {
        flyAnimId = requestAnimationFrame(step);
      } else {
        flyAnimId = null;
      }
    }
    flyAnimId = requestAnimationFrame(step);
  }

  render();

  return {
    setStyles(nextStyles) {
      countryStyles = nextStyles || {};
      render();
    },
    setLines(nextLines) {
      linesData = nextLines || [];
      render();
    },
    setShowAllHoverNames(val) {
      showAllHoverNames = Boolean(val);
    },
    setHideBorders(val) {
      const next = Boolean(val);
      if (next === hideBorders) return;
      hideBorders = next;
      render();
    },
    setOnCountryClick(fn) {
      onCountryClick = fn;
    },
    setProjection(mode) {
      cancelFly();
      projMode = mode === 'flat' ? 'flat' : 'globe';
      containerEl.querySelectorAll('[data-proj]').forEach((b) =>
        b.classList.toggle('active', b.dataset.proj === projMode)
      );
      zoom = 1.0;
      flatPan = [0, 0];
      render();
    },
    flyTo,
    render,
    destroy() {
      cancelFly();
    },
  };
}
