// Interactive Perth map on a real basemap (Leaflet + CARTO tiles) ----------
// Realistic map background, category pins, and decluttered labels that are
// recomputed per zoom so they never sit on top of each other.
(function () {
  const PLACES = (window.PERTH_PLACES || []).slice();
  const COL = window.PERTH_CAT || {};
  if (!PLACES.length || !window.L) return;

  // ---------------------------------------------------------------- basemap
  const LIGHT = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
  const DARK  = 'https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png';
  const ATTR  = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                '&copy; <a href="https://carto.com/attributions">CARTO</a>';

  const map = L.map('map', {
    zoomControl: false,
    minZoom: 8, maxZoom: 18,
    zoomSnap: 1,
    worldCopyJump: false,
  });
  map.createPane('leaders'); map.getPane('leaders').style.zIndex = 620;
  map.createPane('labels');  map.getPane('labels').style.zIndex = 640;
  map.getPane('labels').style.pointerEvents = 'none';
  map.getPane('leaders').style.pointerEvents = 'none';

  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  let tiles = L.tileLayer(mq.matches ? DARK : LIGHT, {
    attribution: ATTR, subdomains: 'abcd', maxZoom: 20, detectRetina: true,
  }).addTo(map);
  mq.addEventListener && mq.addEventListener('change', function (e) {
    tiles.setUrl(e.matches ? DARK : LIGHT);
  });

  // fit to all places
  const bounds = L.latLngBounds(PLACES.map(function (p) { return [p.lat, p.lon]; }));
  map.fitBounds(bounds, { padding: [40, 40] });

  // ---------------------------------------------------------------- icons
  function star(cx, cy, R, r, n) {
    let d = '';
    for (let i = 0; i < n * 2; i++) {
      const rad = (i % 2 === 0) ? R : r;
      const a = -Math.PI / 2 + i * Math.PI / n;
      d += (i ? 'L' : 'M') + (cx + rad * Math.cos(a)).toFixed(2) + ',' + (cy + rad * Math.sin(a)).toFixed(2) + ' ';
    }
    return d + 'Z';
  }
  // glyph per category (matches the printed map's shape system)
  function glyph(cat) {
    const c = COL[cat] || '#666', s = 'stroke="#fff" stroke-width="1.4"';
    const C = 12; // centre in a 24x24 box
    switch (cat) {
      case 'park':       return `<path d="M${C},4 L20,19 L4,19 Z" fill="${c}" ${s}/>`;
      case 'beach':      return `<circle cx="${C}" cy="${C}" r="7.5" fill="${c}" ${s}/>`;
      case 'attraction': return `<path d="M${C},3.5 L20.5,12 L${C},20.5 L3.5,12 Z" fill="${c}" ${s}/>`;
      case 'hills':      return `<rect x="5" y="5" width="14" height="14" rx="2" fill="${c}" ${s}/>`;
      case 'historic':   return `<path d="${star(C, C, 8.5, 3.6, 5)}" fill="${c}" ${s}/>`;
      case 'food':       return `<circle cx="${C}" cy="${C}" r="7.5" fill="${c}" ${s}/>` +
                                `<circle cx="${C}" cy="${C}" r="3" fill="#fff"/>`;
      case 'suburb':     return `<circle cx="${C}" cy="${C}" r="6" fill="#fff" stroke="${c}" stroke-width="2.2"/>`;
      case 'home':       return `<circle cx="${C}" cy="${C}" r="9" fill="#fff" stroke="${c}" stroke-width="1.6"/>` +
                                `<path d="${star(C, C, 7.5, 3.2, 5)}" fill="${c}"/>`;
      default:           return `<circle cx="${C}" cy="${C}" r="7" fill="${c}" ${s}/>`;
    }
  }
  function makeIcon(p) {
    const big = p.cat === 'home';
    const sz = big ? 30 : 24;
    return L.divIcon({
      className: '', // avoid leaflet default styles
      html: `<svg class="mk-ic" data-cat="${p.cat}" width="${sz}" height="${sz}" viewBox="0 0 24 24">${glyph(p.cat)}</svg>`,
      iconSize: [sz, sz], iconAnchor: [sz / 2, sz / 2],
    });
  }

  // ---------------------------------------------------------------- markers + labels
  const bySlug = {};        // slug -> {p, marker, label}
  const leaders = L.layerGroup([], { pane: 'leaders' }).addTo(map);

  PLACES.forEach(function (p) {
    const marker = L.marker([p.lat, p.lon], {
      icon: makeIcon(p), riseOnHover: true, title: p.name, keyboard: false,
    }).addTo(map);
    marker.on('click', function () { location.href = 'place.html?slug=' + encodeURIComponent(p.slug); });

    const text = p.cat === 'home' ? 'Home' : p.name;
    const label = L.marker([p.lat, p.lon], {
      pane: 'labels', interactive: false, keyboard: false,
      icon: L.divIcon({
        className: '',
        html: `<span class="mlabel${p.cat === 'home' ? ' home' : ''}">${escapeHtml(text)}</span>`,
        iconSize: null,
      }),
    });
    bySlug[p.slug] = { p: p, marker: marker, label: label, text: text, shown: false };
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // ---------------------------------------------------------------- declutter
  // Greedy collision avoidance in projected pixel space (pan-independent;
  // depends only on zoom, so we only recompute on zoomend). Ported from the
  // print-map's layout_labels(): try 8 directions at growing radii, skip any
  // box that overlaps a marker or an already-placed label; drop if none fit.
  const FS = 12, CHAR = 0.56, PADX = 8, LH = 16, DOT = 12;
  // higher priority (lower number) grabs a spot first -> survives when crowded
  const PRIO = { home: 0, attraction: 1, park: 1, historic: 1, beach: 2, hills: 2, food: 3, suburb: 4 };
  const DIRS = [[1, 0, 's'], [-1, 0, 'e'], [0, -1, 'm'], [0, 1, 'm'],
                [1, -0.85, 's'], [-1, -0.85, 'e'], [1, 0.85, 's'], [-1, 0.85, 'e']];

  function relayout() {
    const z = map.getZoom();
    const items = PLACES.map(function (p) {
      const pt = map.project([p.lat, p.lon], z);
      return { p: p, x: pt.x, y: pt.y };
    });
    const byId = {}; items.forEach(function (it) { byId[it.p.slug] = it; });

    // obstacles start with every marker's hit box
    const obstacles = items.map(function (it) {
      return [it.x - DOT, it.y - DOT, it.x + DOT, it.y + DOT];
    });
    function overlaps(b) {
      for (let i = 0; i < obstacles.length; i++) {
        const o = obstacles[i];
        if (!(b[2] <= o[0] || b[0] >= o[2] || b[3] <= o[1] || b[1] >= o[3])) return true;
      }
      return false;
    }
    function density(it) {
      let d = 0;
      for (let i = 0; i < items.length; i++) {
        const o = items[i];
        if (o !== it && Math.abs(o.x - it.x) < 80 && Math.abs(o.y - it.y) < 80) d++;
      }
      return d;
    }
    // important + isolated first; dense/low-priority last (they drop when crowded)
    const order = items.slice().sort(function (a, b) {
      return (PRIO[a.p.cat] - PRIO[b.p.cat]) || (density(a) - density(b)) || (a.y - b.y);
    });

    const radii = [DOT + 5, DOT + 12, DOT + 21, DOT + 33, DOT + 48, DOT + 66, DOT + 90, DOT + 120];
    const placement = {};

    order.forEach(function (it) {
      const rec = bySlug[it.p.slug];
      const w = rec.text.length * FS * CHAR + PADX, h = LH;
      let done = false;
      for (let ri = 0; ri < radii.length && !done; ri++) {
        const r = radii[ri];
        for (let di = 0; di < DIRS.length; di++) {
          const dx = DIRS[di][0], dy = DIRS[di][1], anch = DIRS[di][2];
          const ay = it.y + dy * r;
          let box, cx, cy, leadX, leadY;
          if (anch === 's') { const ax = it.x + dx * r; box = [ax, ay - h / 2, ax + w, ay + h / 2]; cx = ax + w / 2; cy = ay; leadX = ax; leadY = ay; }
          else if (anch === 'e') { const ax = it.x + dx * r; box = [ax - w, ay - h / 2, ax, ay + h / 2]; cx = ax - w / 2; cy = ay; leadX = ax; leadY = ay; }
          else { const ax = it.x; box = [ax - w / 2, ay - h / 2, ax + w / 2, ay + h / 2]; cx = ax; cy = ay; leadX = ax; leadY = (dy < 0 ? ay + h / 2 : ay - h / 2); }
          if (overlaps(box)) continue;
          obstacles.push(box);
          placement[it.p.slug] = {
            cx: cx, cy: cy,
            lead: (r > DOT + 14) ? [leadX, leadY] : null,
          };
          done = true;
          break;
        }
      }
      if (!done) placement[it.p.slug] = null; // dropped -> hidden this zoom
    });

    // apply
    leaders.clearLayers();
    PLACES.forEach(function (p) {
      const rec = bySlug[p.slug];
      const pl = placement[p.slug];
      if (!pl) {
        if (rec.shown) { map.removeLayer(rec.label); rec.shown = false; }
        return;
      }
      const ll = map.unproject([pl.cx, pl.cy], z);
      rec.label.setLatLng(ll);
      if (!rec.shown) { rec.label.addTo(map); rec.shown = true; }
      if (pl.lead) {
        const lead = map.unproject(pl.lead, z);
        L.polyline([[p.lat, p.lon], lead], {
          pane: 'leaders', interactive: false,
          color: '#9aa4ad', weight: 1, opacity: 0.85,
        }).addTo(leaders);
      }
    });
    applyFilter(); // keep search dimming in sync after a relayout
  }

  map.on('zoomend', relayout);
  map.whenReady(relayout);

  // ---------------------------------------------------------------- controls
  byId('zin').onclick   = function () { map.zoomIn(); };
  byId('zout').onclick  = function () { map.zoomOut(); };
  byId('zreset').onclick = function () { map.fitBounds(bounds, { padding: [40, 40] }); };
  function byId(id) { return document.getElementById(id); }

  window.addEventListener('resize', function () { map.invalidateSize(); });

  // ---------------------------------------------------------------- search
  const search = byId('search');
  const listLinks = Array.from(document.querySelectorAll('.reg li a'));
  let query = '';

  function applyFilter() {
    const q = query;
    PLACES.forEach(function (p) {
      const rec = bySlug[p.slug];
      const hit = !q || p.name.toLowerCase().includes(q);
      const el = rec.marker.getElement();
      if (el) {
        const svg = el.querySelector('svg');
        if (svg) { svg.classList.toggle('dim', q && !hit); svg.classList.toggle('hit', q && hit); }
      }
      if (rec.shown) {
        const lel = rec.label.getElement();
        if (lel) lel.style.opacity = (q && !hit) ? '0.15' : '';
      }
    });
  }

  if (search) {
    search.addEventListener('input', function () {
      query = search.value.trim().toLowerCase();
      // sidebar filter
      listLinks.forEach(function (a) {
        const hit = !query || (a.dataset.name || '').includes(query);
        a.parentElement.classList.toggle('hide', !hit);
      });
      document.querySelectorAll('.reg').forEach(function (sec) {
        const any = Array.from(sec.querySelectorAll('li')).some(function (li) { return !li.classList.contains('hide'); });
        sec.classList.toggle('hide', !any);
      });
      applyFilter();
    });
  }

  // sidebar hover -> gently locate the place on the map
  listLinks.forEach(function (a) {
    const slug = (a.getAttribute('href') || '').split('slug=')[1];
    if (!slug || !bySlug[slug]) return;
    a.addEventListener('mouseenter', function () {
      const el = bySlug[slug].marker.getElement();
      if (el) { const svg = el.querySelector('svg'); if (svg) svg.classList.add('focus'); }
    });
    a.addEventListener('mouseleave', function () {
      const el = bySlug[slug].marker.getElement();
      if (el) { const svg = el.querySelector('svg'); if (svg) svg.classList.remove('focus'); }
    });
  });
})();
