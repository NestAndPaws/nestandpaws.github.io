# Revert guide: Oct 2026 redesign

Pre-redesign state is the git tag `pre-redesign-2026-10-16` (commit 1b30fb7).

## Full revert
    git revert --no-commit pre-redesign-2026-10-16..HEAD && git commit -m "Revert redesign"
or restore any single file: `git checkout pre-redesign-2026-10-16 -- shared.css renter.html`

## What the redesign changed
- `shared.css`: rewritten (glass nav, collection header, cards, footer, guide jump bar, scroll reveals, view transitions).
- Every `.html` page: one shared nav and footer (`tools/redesign.py`).
- Category pages: header without emoji, cards rebuilt from `products.js` (adds 12 under-$25 picks the old JS showed), JSON-LD rebuilt, client-side re-render script removed.
- Product pages: link `/shared.css`, old nav CSS removed, crumbs added.
- Home: trust strip replaces the scrolling ticker.

## Guide hero test (lifestyle scene)
Heroes are optional and file-gated. A guide shows a hero only if `images/guides/hero/{slug}.jpg` exists.
- Keep the old illustrated look: delete those files and run `python3 tools/build_guides.py && python3 tools/redesign.py`.
- Pre-test guide cards used product illustrations in `images/guides/{product}.jpg` (unchanged).

## Rebuild order
`build_home.py`, `build_guides.py`, `redesign.py` (all idempotent).

## Round 3 (Oct 16, 2026)
- Hero captions/AI pill removed. Heroes are file-gated: images/guides/hero/{slug}.jpg, no caption, none going forward.
- 7 new guides (tools/guides/*.json) with Gemini heroes; guides index now image cards; home guide cards use heroes.
- Home hero: 10 floating product images (extras hidden under 1180px; all hidden under 760px). Trust strip replaces "Not tested by us". "Home & Kitchen" label.
- barn-door-hardware moved from renter to home.
- Revert this round: git revert <this commit>. Full rollback: tag pre-redesign-2026-10-16.

## Fashion build, Oct 20, 2026 (branch `fashion-build`, not pushed until Vatsal says "push")
- New `fashion` category: `fashion.html`, nav and footer link on every page, home tile, sitemap entry (`tools/redesign.py`, `seo_postprocess.py`, `build_home.py`).
- 10 new products prepended to `products.js` (category `fashion`) plus 10 product pages, images and crops.
- 2 new guides: `guides/fall-outfit-ideas-for-women.html`, `guides/fall-outfit-ideas-for-men.html` (JSON in `tools/guides/`), 12-look galleries and hero images.
- `tools/build_guides.py`: look-book gallery block, and the deposit-safe footnote now shows only on guides with safe scores.
- Revert: `git revert` the fashion commits, or `git checkout main -- <file>`.

## Oct 22, 2026: Kids fall guide
Added `guides/fall-outfit-ideas-for-kids.html` (from `tools/guides/fall-outfit-ideas-for-kids.json`), 5 products appended to `products.js` (category fashion), their product pages and images, 12 look images, hero, and crops.json entries. Revert: `git revert <commit>` or delete those files and re-run the build order.

## Oct 25, 2026: Bedroom wall paint colors look-book guide
Added `guides/bedroom-wall-paint-colors-on-paneled-wall.html` (from `tools/guides/bedroom-wall-paint-colors-on-paneled-wall.json`), 8 look images and a hero (`images/guides/looks/...`, `images/guides/hero/...`), 2 pick thumbnails, guides index and sitemap entries. No `products.js` change. Revert: `git revert <commit>` or delete those files and re-run the build order.

## Oct 26, 2026: guide "6 Bedroom Furniture Styles in One Room"
Adds guides/bedroom-furniture-styles-one-room.html, tools/guides/bedroom-furniture-styles-one-room.json, hero + 6 look images, 2 pick thumbs; updates guides/index.html, sitemap.xml; tools/build_guides.py gets optional `cta_text` and `how_note` flags (default unchanged). Revert: `git revert <this commit>`.
