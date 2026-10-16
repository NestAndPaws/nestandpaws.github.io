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
