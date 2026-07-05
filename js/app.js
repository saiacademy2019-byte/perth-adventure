// Interactive map: pan / zoom / search  -----------------------------------
(function () {
  const svg = document.getElementById('perthmap');
  const vp = document.getElementById('viewport');
  const canvas = document.getElementById('mapcanvas');
  if (!svg || !vp) return;

  let scale = 1, tx = 0, ty = 0;
  const MIN = 1, MAX = 8;

  function apply() { vp.setAttribute('transform', `translate(${tx} ${ty}) scale(${scale})`); }

  // client point -> svg user coords
  function toSvg(clientX, clientY) {
    const pt = svg.createSVGPoint();
    pt.x = clientX; pt.y = clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }

  function zoomAt(clientX, clientY, factor) {
    const ns = Math.min(MAX, Math.max(MIN, scale * factor));
    if (ns === scale) return;
    const p = toSvg(clientX, clientY);
    // keep the point under cursor fixed: p = (world*scale)+t  ->  solve new t
    tx = p.x - (p.x - tx) * (ns / scale);
    ty = p.y - (p.y - ty) * (ns / scale);
    scale = ns;
    clampPan(); apply();
  }

  function clampPan() {
    if (scale <= MIN) { tx = 0; ty = 0; }
  }

  // wheel zoom
  canvas.addEventListener('wheel', function (e) {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15);
  }, { passive: false });

  // drag pan
  let dragging = false, moved = 0, lx = 0, ly = 0;
  canvas.addEventListener('pointerdown', function (e) {
    dragging = true; moved = 0; lx = e.clientX; ly = e.clientY;
    canvas.classList.add('grabbing'); canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    const m = svg.getScreenCTM();
    const dx = (e.clientX - lx) / m.a, dy = (e.clientY - ly) / m.d;
    moved += Math.abs(e.clientX - lx) + Math.abs(e.clientY - ly);
    tx += dx; ty += dy; lx = e.clientX; ly = e.clientY;
    apply();
  });
  function endDrag(e) {
    if (!dragging) return;
    dragging = false; canvas.classList.remove('grabbing');
  }
  canvas.addEventListener('pointerup', endDrag);
  canvas.addEventListener('pointercancel', endDrag);

  // prevent a drag from triggering navigation
  svg.querySelectorAll('a.mk').forEach(function (a) {
    a.addEventListener('click', function (e) { if (moved > 6) e.preventDefault(); });
  });

  // buttons
  const rectC = () => canvas.getBoundingClientRect();
  document.getElementById('zin').onclick = () => { const r = rectC(); zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1.4); };
  document.getElementById('zout').onclick = () => { const r = rectC(); zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1 / 1.4); };
  document.getElementById('zreset').onclick = () => { scale = 1; tx = 0; ty = 0; apply(); };

  // ---------------- search ----------------
  const search = document.getElementById('search');
  const listLinks = Array.from(document.querySelectorAll('.reg li a'));
  const mapMarks = Array.from(document.querySelectorAll('a.mk'));

  search.addEventListener('input', function () {
    const q = search.value.trim().toLowerCase();
    // filter sidebar
    listLinks.forEach(function (a) {
      const hit = !q || a.dataset.name.includes(q);
      a.parentElement.classList.toggle('hide', !hit);
    });
    document.querySelectorAll('.reg').forEach(function (sec) {
      const any = Array.from(sec.querySelectorAll('li')).some(li => !li.classList.contains('hide'));
      sec.classList.toggle('hide', !any);
    });
    // highlight/dim on map
    mapMarks.forEach(function (m) {
      const name = (m.dataset.name || '').toLowerCase();
      const hit = !q || name.includes(q);
      m.classList.toggle('dim', q && !hit);
      m.classList.toggle('hit', q && hit);
    });
  });
})();
