// Detail page renderer ----------------------------------------------------
(function () {
  const PLACES = window.PERTH_PLACES || [];
  const COL = window.PERTH_CAT || {};
  const CATLABEL = window.PERTH_CATLABEL || {};
  const params = new URLSearchParams(location.search);
  const slug = params.get('slug') || (location.hash ? location.hash.slice(1) : '') || window.__SLUG__;
  const p = PLACES.find(x => x.slug === slug);
  const root = document.getElementById('detail');
  const crumb = document.getElementById('crumb');

  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  if (!p) {
    root.innerHTML = '<div class="notfound"><h1>Place not found</h1><p>Head back and pick a spot from the map.</p></div>';
    return;
  }
  document.title = p.name + ' · Perth Adventure Map';
  crumb.textContent = p.region;

  const color = COL[p.cat] || '#666';
  const catName = CATLABEL[p.cat] || p.cat;

  // ---- gallery: try images/<slug>/1..6.(jpg|jpeg|png|webp); fall back to placeholder ----
  const gallery = document.createElement('div');
  gallery.className = 'gallery';
  let loaded = 0, pending = 0, settled = false;
  const exts = ['jpg', 'jpeg', 'png', 'webp'];

  function placeholder() {
    if (settled) return;
    settled = true;
    if (loaded === 0) {
      gallery.innerHTML =
        `<div class="ph" style="background:linear-gradient(135deg,${color},#00000055)">
           <span class="cam">📷</span>
           <span>Add photos of ${esc(p.name)}</span>
           <small>Drop images into <code>images/${esc(p.slug)}/</code> (1.jpg, 2.jpg …)</small>
         </div>`;
    }
  }

  function tryImg(n) {
    if (n > 6) { if (pending === 0) placeholder(); return; }
    let ei = 0;
    const attempt = () => {
      if (ei >= exts.length) { pending--; if (n === 6 && pending === 0) placeholder(); return; }
      const img = new Image();
      pending++;
      img.onload = () => {
        pending--; loaded++; settled = false;
        img.className = 'gimg'; gallery.appendChild(img);
        // sort by filename order
        Array.from(gallery.querySelectorAll('img')).sort((a, b) => a.src.localeCompare(b.src))
          .forEach(el => gallery.appendChild(el));
        if (pending === 0 && loaded > 0) settled = true;
      };
      img.onerror = () => { pending--; ei++; attempt(); };
      img.src = `images/${p.slug}/${n}.${exts[ei]}`;
    };
    attempt();
    tryImg(n + 1);
  }
  // kick off; give the async loads a moment before deciding on placeholder
  tryImg(1);
  setTimeout(placeholder, 700);

  const hl = (p.hl || []).map(h => `<li>${esc(h)}</li>`).join('');
  const approx = p.approx
    ? `<div class="approx">ℹ️ Location &amp; details are approximate — feel free to correct this spot's info in <code>js/data.js</code> (or the build script).</div>`
    : '';
  const gmaps = `https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lon}`;

  root.innerHTML = `
    <div class="place-head">
      <h1>${esc(p.name)}</h1>
      <span class="badge" style="background:${color}">${esc(catName)}</span>
    </div>
    <div class="region-tag">📍 ${esc(p.region)}</div>
    <div id="gal"></div>
    ${approx}
    <p class="blurb">${esc(p.blurb)}</p>
    ${hl ? `<div class="card"><h2>Highlights</h2><ul>${hl}</ul></div>` : ''}
    ${p.tip ? `<div class="card"><h2>Good to know</h2><div class="tip">💡 <span>${esc(p.tip)}</span></div></div>` : ''}
    <div class="actions">
      <a class="btn-back" href="index.html">← Back to map</a>
      <a class="maplink" href="${gmaps}" target="_blank" rel="noopener">🗺️ Open in Google Maps</a>
    </div>`;
  document.getElementById('gal').appendChild(gallery);
})();
