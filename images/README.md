# Photos

Each place can show a small photo gallery. To add photos for a place:

1. Find the place's **slug** (the `?slug=…` in its page URL, e.g. `kings-park`).
2. Create a folder here named exactly that slug, e.g. `images/kings-park/`.
3. Drop in photos named `1.jpg`, `2.jpg`, `3.jpg` … (up to 6). `.jpeg`, `.png` and `.webp` also work.

The detail page loads them automatically. If a place has no photos yet, it shows a
coloured placeholder telling you where to add them — nothing breaks.

Slugs are listed in `js/data.js` (the `slug` field of every place).
