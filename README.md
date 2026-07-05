# Perth Adventure Map 🗺️⭐

An interactive, clickable map of Greater Perth built for exploring and remembering places —
plus a matching **A2 print map**. Home base is marked at **2 Zinnia Way, Willetton**.

## Two ways to use it

### 1. Interactive site
Open **`index.html`** in any browser (just double-click it).

- Pan (drag) and zoom (scroll / + − buttons) the map.
- **Click any place** → a detail page with photos + info, and a **← Back to map** button.
- Search box filters the list and highlights matching points.
- Every place is also listed on the right, grouped by region.

No server needed — it runs straight from the files (`file://`).

### 2. Printable A2 map
Open **`print/perth_adventure_map.html`** in Chrome → **⌘P** → Paper **A2**, Margins **None**,
Scale **100%** → *Save as PDF*. It's vector, so it prints razor-sharp. (`print/PREVIEW_full.png` is a quick look.)

## Adding photos
Drop images into `images/<slug>/1.jpg`, `2.jpg`, … See `images/README.md`. Places with no
photos yet show a labelled placeholder — nothing breaks.

## Editing places
Everything lives in **`build_site.py`** (the single source of truth: coordinates, categories,
descriptions). Edit it and run:

```bash
python3 build_site.py
```

This regenerates `index.html`, `js/data.js` and the print map.

## Note on approximate spots
A few smaller venues (some Swan Valley / Hills wineries, cafes and newer suburbs) are marked
**approximate** — their pin and blurb are best-guess and easy to fine-tune in `build_site.py`.
They're flagged with an ℹ️ note on their page. Places flagged approximate include:
Sacred India Gallery, Sandleford, Bailey Brewing Co, Aurelien, Seven Sins, The Avocado Grove,
Lavender Bistro, Secret Garden, Cohunu Koala Park, Carmel, and several newer southern suburbs.

## Layout
```
PERTH_ADVENTURE/
├── index.html          # interactive map
├── place.html          # place detail page (reads ?slug=)
├── build_site.py       # ← edit places here, then re-run
├── css/styles.css
├── js/
│   ├── data.js         # generated place data
│   ├── app.js          # map pan/zoom/search
│   └── place.js        # detail-page renderer
├── images/             # your photos: images/<slug>/1.jpg …
└── print/              # A2 printable map (svg + html + preview)
```
