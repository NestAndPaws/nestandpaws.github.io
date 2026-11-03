#!/usr/bin/env python3
"""Wave B gift pack builder (Nov 2, 2026). Reuses build_gifts.py helpers with Wave B data.
Idempotent: guide JSON rewritten, products.js appended only if id absent, product pages and category cards only if missing.
Also writes the hub (with links to the new guides) and resizes masters to images/web."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gifts_data_b as b
import build_gifts as bg

bg.PICKS = b.PICKS; bg.BY = b.BY; bg.DATE = b.DATE; bg.CATLABEL = b.CATLABEL
ROOT = bg.ROOT
CHECKED = "Nov 2, 2026"

def write_guides_b():
    for g in b.GUIDES:
        j = dict(slug=g["slug"], title=g["title"], short_title=g["short"], description=g["desc"], dek=g["dek"],
                 constraint=g["constraint"], published=b.DATE, updated=b.DATE, last_checked=CHECKED, problem_tag="Gifts",
                 hook=g["hook"], picks=[bg.pick_json(b.BY[i]) for i in g["picks"]],
                 skipped=["Items whose regular price sits outside the band.",
                          "Items with very few reviews or only a marketplace seller.",
                          "Items where we could not match the model on a second retailer's page, unless noted on the pick."],
                 how_picked=["Sold at a major retailer, with a second retailer linked where we could match the model on its page.",
                             "A regular price inside the band on the retailer page we read on Nov 2, 2026.",
                             "Ratings noted from each retailer page we read. Where a rating is low, the pick says so."],
                 how_note="Ratings and listing facts come from the retailer pages read on Nov 2, 2026. Prices are brackets because retailer prices change, and holiday sales can change them again. Product images on this page are concept images, not photos of the item.",
                 final=g["final"], related=g["related"], cta_text="Find it on the retailer",
                 hero_alt=g["title"], hero_caption="AI-generated concept images, not photos of the items")
        json.dump(j, open(os.path.join(ROOT, "tools", "guides", g["slug"] + ".json"), "w"), indent=1, ensure_ascii=False)
    # hub: same picks and text as Wave A, plus links to the three new guides
    hub = dict(bg.HUB); hub["related"] = list(bg.HUB["related"]) + [s for s in b.HUB_EXTRA_RELATED if s not in bg.HUB["related"]]
    hub["constraint"] = "Gifts from under $25 to under $500"
    hub["desc"] = "Holiday gift ideas for 2026 from under $25 to under $500: a skillet, a dog toy, a bottle, smart bulbs and more. Links to the full gift guides by price."
    hub["dek"] = "Start here: one pick each for the kitchen, the dog, the desk, the renter and the shelf, then pick a price band."
    hub["final"] = bg.HUB["final"] + " For a bigger budget, open the under $100, under $200 and under $500 guides."
    j = dict(slug=hub["slug"], title=hub["title"], short_title=hub["short"], description=hub["desc"], dek=hub["dek"],
             constraint=hub["constraint"], published="2026-11-02", updated=b.DATE, last_checked="Nov 1, 2026", problem_tag="Gifts",
             hook=hub["hook"], picks=[bg.pick_json(bg.A_BY[i]) for i in hub["picks"]],
             skipped=["Items sold only by marketplace sellers with few reviews.", "Items sold at only one major retailer.",
                      "Items whose price sits outside the band at either retailer on Nov 1, 2026."],
             how_picked=["Sold at Amazon and at least one other major retailer, or at two non-Amazon retailers.",
                         "A price inside the band at both retailers on Nov 1, 2026.",
                         "A listing rating of 4.2 stars or higher at each retailer that shows one."],
             how_note="Ratings and listing facts come from the retailer pages read on Nov 1, 2026. Prices are brackets because retailer prices change, and holiday sales can change them again. Product images on this page are concept images, not photos of the item.",
             final=hub["final"], related=hub["related"], cta_text="Find it on the retailer",
             hero_alt=hub["title"], hero_caption="AI-generated concept images, not photos of the items")
    json.dump(j, open(os.path.join(ROOT, "tools", "guides", hub["slug"] + ".json"), "w"), indent=1, ensure_ascii=False)

def resize_images(src_dir):
    from PIL import Image
    n = 0
    for p in b.PICKS:
        dst = os.path.join(ROOT, "images", "web", p["id"] + ".jpg")
        if os.path.exists(dst): continue
        im = Image.open(os.path.join(src_dir, p["id"] + ".jpg")).convert("RGB").resize((900, 1350), Image.LANCZOS)
        im.save(dst, quality=85, optimize=True); n += 1  # no EXIF carried
    return n

if __name__ == "__main__":
    import gifts_data as a
    bg.A_BY = a.BY
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src: print("images:", resize_images(src))
    write_guides_b(); print("guides written")
    print("products.js added:", bg.append_products())
    for p in b.PICKS:
        f = os.path.join(ROOT, "products", p["id"] + ".html")
        if not os.path.exists(f):
            open(f, "w", encoding="utf-8").write(bg.product_page(p))
    print("product pages:", len(b.PICKS))
    print("cards inserted:", bg.insert_cards())
