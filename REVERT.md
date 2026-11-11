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

## Oct 26, 2026: guide "6 Living Room Furniture Styles in One Room"
Adds guides/living-room-furniture-styles-one-room.html, tools/guides/living-room-furniture-styles-one-room.json, hero + 6 look images, 2 new pick thumbs (hipiwe, enjoybasics; command pack thumb already existed); updates guides/index.html, sitemap.xml. No products.js change. Revert: `git revert <this commit>`.
Same day: footer note no longer mentions Amazon (tools/build_guides.py, tools/redesign.py; all rebuilt pages, one line each). Revert: `git revert <this commit>`. Not changed: start-here.html body text and the product button links (they go to amazon.com/dp pages).

## Oct 27 2026: Idea 2 guide
- Added `guides/empty-room-to-furnished-five-rooms.html` (+ hero, 5 look images, 2 pick images, `tools/guides/empty-room-to-furnished-five-rooms.json`); `guides/index.html` and `sitemap.xml` regenerated.
- Revert: `git revert <this commit>`.

## Nov 1, 2026: Series C capsule guides (Women's and Men's)
- Added `guides/fall-capsule-wardrobe-for-women-625-outfits.html` and `guides/fall-capsule-wardrobe-for-men-625-outfits.html` (+ `tools/guides/*.json`, 12 look images each in `images/guides/looks/...`, 30 pick images each in `images/guides/`). Guides index and sitemap regenerated. No hero image. No `products.js` change and no product pages (deferred).
- `tools/build_guides.py`: `link()` now takes the pick and uses `where_to_buy[0].url` when present (Target), else the plain Amazon link as before. Existing guides unchanged.
- Picks link to Target product pages (target.com/p/-/A-<id>); no affiliate tag, no Amazon wording on the new pages.
- Revert: `git revert <this commit>`.

## Nov 1, 2026 (PM): Series C Kids guide
- Added `guides/fall-capsule-wardrobe-for-kids-625-outfits.html` (tools/guides JSON, 30 Target picks via where_to_buy, 12 looks), 30 pick images (images/guides/kids-*), 12 look images, guides index and sitemap updated.
- Revert: `git revert <this commit>`.

## Holiday gift pack, Wave A (Nov 2, 2026)
- Added 10 gift products (products.js entries with optional `where_to_buy`, product pages, cards on home/pets/renter/under25), 5 guides (gift-ideas-under-25, gift-ideas-under-50, home-and-kitchen-gift-ideas, gifts-for-dog-owners, holiday-gift-ideas-2026 hub with hero), and the hub as the first Featured guide on the home page.
- `tools/build_guides.py`: new `buttons()` renders one "Find it on [Retailer]" button per `where_to_buy` entry (single-entry guides unchanged).
- New `tools/gifts_data.py` and `tools/build_gifts.py` (idempotent) hold the Wave A data and builder.
- Product images are AI-generated concept images (Higgsfield, Seedream 5.0 lite), not listing photos.
- Revert: `git revert <this commit>`; products.js entries are additive.

## Holiday gift pack, Wave B (Nov 2, 2026)
- Added 15 gift products in three price bands (products.js entries with `where_to_buy`, 15 product pages, cards on home/pets/renter, images/web and images/guides), 3 guides (gift-ideas-under-100, gift-ideas-under-200, gift-ideas-under-500) and a refreshed hub (holiday-gift-ideas-2026 now links to them; its picks are unchanged). Guides index, home page guide cards and sitemap updated.
- `tools/build_guides.py`: `buttons()` now also names the retailer for a single `where_to_buy` entry, but only for guides whose slug starts with "gift" (Dyson, Roborock and Bedsure each have one verified retailer). Other guides unchanged.
- New `tools/gifts_data_b.py` and `tools/build_gifts_b.py` (idempotent; reuses `build_gifts.py` helpers).
- Retailer links read on product pages Nov 2, 2026; Amazon ASINs confirmed on product pages. Product images are AI-generated concept images (Higgsfield, Seedream 5.0 lite), not listing photos.
- Revert: `git revert <this commit>`; products.js entries are additive.

## Guides page hero fix (Nov 3, 2026)
- Added 10 missing hero images (images/guides/hero/*.jpg, 1376x768, three-panel from the guide's own AI concept product images) for gift-ideas-under-25/50/100/200/500, home-and-kitchen-gift-ideas, gifts-for-dog-owners and the three fall capsule wardrobe guides. Every guide card on guides/index.html now shows an image: lead card image beside the title, other cards image above (existing CSS, unchanged).
- Fixed holiday-gift-ideas-2026 hero (removed a black bar at the bottom).
- Rebuilt guides/index.html, the 10 affected guide pages and sitemap lastmod via the normal build chain. No CSS or tools changes.
- Revert: `git revert <this commit>`.

## Cozy desk setup guide (Nov 11, 2026)
- New guide: `tools/guides/cozy-desk-setup-power-and-light-upgrades.json` builds `guides/cozy-desk-setup-power-and-light-upgrades.html` (5 picks: Anker Nano Smart Display charger, Mophie 3-in-1, Quntis light bar, BenQ ScreenBar Halo 2, Lofree Flow Lite 100). Rebuilt `guides/index.html` and `sitemap.xml` via the normal build chain.
- New images: 5 pick images in `images/web/` and `images/guides/` (AI concept images, Higgsfield Seedream 5.0 lite, unlimited, no credits) and one hero `images/guides/hero/cozy-desk-setup-power-and-light-upgrades.jpg` (1376x768).
- Retailer links read on the retailer pages Nov 11, 2026 (Amazon, Best Buy, Lofree). Quntis is Amazon only: the Quntis store listing could not be matched to the Amazon model. No tagged links. products.js, product pages and category pages untouched (deferred).
- Revert: `git revert <this commit>`.

## Cozy desk setup: products and button wording (Nov 11, 2026)
- `tools/build_guides.py`: new optional guide flag `name_retailer` shows "Find it on {retailer}" for a single-retailer pick (set on the cozy desk guide only; other guides unchanged).
- Added 4 products via `tools/build_desk.py` (Anker Nano charger, Mophie 3-in-1, BenQ ScreenBar Halo 2, Lofree Flow Lite 100): `products.js` appended (175 entries now), 4 product pages, 4 cards on `home.html`, sitemap rebuilt. Quntis not added (already on site as quntis-monitor-light-bar).
- Revert: `git revert <this commit>`; products.js entries are additive.
