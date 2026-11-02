#!/usr/bin/env python3
"""Wave A gift pack builder. Idempotent: guides JSON rewritten, products.js appended only if id absent,
product pages and category cards written/inserted only if missing."""
import os, re, json, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gifts_data import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape
SITE = "https://nestandpaws.github.io"

def pick_json(p):
    return dict(id=p["id"], name=p["name"], image=p["id"], alt=p["alt"], best_for=p["best_for"], limit=p["limit"],
                price_bracket=p["bracket"], why=p["why"], con=p["con"],
                where_to_buy=[dict(retailer=r, url=u) for r, u in p["wtb"]])

HUB = dict(slug="holiday-gift-ideas-2026", title="Holiday Gift Ideas 2026: Five Picks, Two Price Bands", short="Holiday Gift Ideas 2026",
  dek="Start here: one pick each for the kitchen, the dog, the desk, the renter and the shelf.", constraint="Gifts under $25 and under $50",
  desc="Holiday gift ideas for 2026 under $25 and under $50: a skillet, a dog toy, a dog grooming tool, a bottle and smart bulbs. Links to the full gift guides.",
  hook=["This is the short list. Each pick comes from a longer gift guide, linked at the bottom.",
        "We did not test these. We read listings at two retailers on Nov 1, 2026. Prices change during holiday sales, so check each retailer."],
  picks=["lodge-8-inch-cast-iron-skillet","kong-classic-dog-toy-large","furminator-deshedding-tool-large-dog","hydro-flask-32-oz-wide-mouth-bottle","govee-smart-led-bulbs-4-pack"],
  final="Pick by person: a cook gets the skillet, a dog owner gets the KONG or the FURminator, a desk worker gets the bottle, a renter gets the bulbs.",
  related=["gift-ideas-under-25","gift-ideas-under-50","home-and-kitchen-gift-ideas","gifts-for-dog-owners"])

def write_guides():
    for g in GUIDES + [HUB]:
        j = dict(slug=g["slug"], title=g["title"], short_title=g["short"], description=g["desc"], dek=g["dek"],
                 constraint=g["constraint"], published=DATE, updated=DATE, last_checked="Nov 1, 2026", problem_tag="Gifts",
                 hook=g["hook"], picks=[pick_json(BY[i]) for i in g["picks"]],
                 skipped=["Items sold only by marketplace sellers with few reviews.",
                          "Items sold at only one major retailer.",
                          "Items whose price sits outside the band at either retailer on Nov 1, 2026."],
                 how_picked=["Sold at Amazon and at least one other major retailer, or at two non-Amazon retailers.",
                             "A price inside the band at both retailers on Nov 1, 2026.",
                             "A listing rating of 4.2 stars or higher at each retailer that shows one."],
                 how_note="Ratings and listing facts come from the retailer pages read on Nov 1, 2026. Prices are brackets because retailer prices change, and holiday sales can change them again. Product images on this page are concept images, not photos of the item.",
                 final=g["final"], related=g["related"], cta_text="Find it on the retailer",
                 hero_alt=g["title"], hero_caption="AI-generated concept images, not photos of the items")
        json.dump(j, open(os.path.join(ROOT, "tools", "guides", g["slug"] + ".json"), "w"), indent=1, ensure_ascii=False)

def js_entry(p):
    w = ",\n      ".join('{ retailer: %s, url: %s }' % (json.dumps(r), json.dumps(u)) for r, u in p["wtb"])
    aff = next((u for r, u in p["wtb"] if r == "Amazon"), p["wtb"][0][1])
    return f'''
  {{
    id: {json.dumps(p["id"])},
    title: {json.dumps(p["name"])},
    category: {json.dumps(p["cat"])},
    price: {p["price"]},
    price_bracket: {json.dumps(p["bracket"])},
    affiliate_link: {json.dumps(aff)},
    where_to_buy: [
      {w}
    ],
    image: "images/web/{p["id"]}.jpg",
    subtitle: {json.dumps(p["subtitle"])},
    story: {json.dumps(p["story"])},
    tags: {json.dumps(p["tags"])},
    badge: null,
    date_added: "{DATE}"
  }},
'''

def append_products():
    f = os.path.join(ROOT, "products.js"); s = open(f, encoding="utf-8").read()
    add = "".join(js_entry(p) for p in PICKS if f'id: "{p["id"]}"' not in s)
    if not add: return 0
    i = s.rindex("];")
    s = s[:i].rstrip() + "\n" + add + s[i:]
    open(f, "w", encoding="utf-8").write(s); return add.count("id: ")

def fmt_date(iso=DATE): return "Nov 2, 2026"

def product_page(p):
    tpl = open(os.path.join(ROOT, "products", "afiing-desk-pad.html"), encoding="utf-8").read()
    label, cpage = CATLABEL[p["cat"]]
    url = f"{SITE}/products/{p['id']}.html"
    title = f"{p['name']} — Nest & Paws"
    desc = (p["subtitle"] + ". " + p["story"])[:150].rstrip() + "…"
    s = tpl
    # head
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{E(desc, quote=True)}">', s, count=1, flags=re.S)
    s = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">', s, count=1)
    # json-ld product
    ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["subtitle"] + ". " + p["story"],
                     "category": label, "url": url, "image": f"{SITE}/images/web/{p['id']}.jpg", "releaseDate": DATE}, indent=2, ensure_ascii=False)
    s = re.sub(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "Product".*?</script>',
               lambda m: '<script type="application/ld+json">\n' + ld + '\n</script>', s, count=1, flags=re.S)
    # og
    s = re.sub(r'<!-- np-seo:og -->.*?<!-- /np-seo:og -->',
               lambda m: ('<!-- np-seo:og -->\n<meta property="og:site_name" content="Nest &amp; Paws">\n'
                          f'<meta property="og:title" content="{E(title, quote=True)}">\n<meta property="og:description" content="{E(desc, quote=True)}">\n'
                          f'<meta property="og:url" content="{url}">\n<meta property="og:type" content="website">\n<meta name="twitter:card" content="summary_large_image">\n'
                          f'<meta property="og:image" content="{SITE}/images/web/{p["id"]}.jpg">\n<!-- /np-seo:og -->'), s, count=1, flags=re.S)
    bc = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nest & Paws", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": label, "item": f"{SITE}/{cpage}"},
        {"@type": "ListItem", "position": 3, "name": p["name"], "item": url}]}, indent=2, ensure_ascii=False)
    s = re.sub(r'<!-- np-seo:breadcrumb -->.*?<!-- /np-seo:breadcrumb -->',
               lambda m: '<!-- np-seo:breadcrumb -->\n<script type="application/ld+json">\n' + bc + '\n</script>\n<!-- /np-seo:breadcrumb -->', s, count=1, flags=re.S)
    # body main
    btns = "\n      ".join(f'<a href="{u}" class="cta-btn" target="_blank" rel="noopener noreferrer" style="margin-bottom:10px">Find it on {E(r)}</a>' for r, u in p["wtb"])
    others = [q for q in PICKS if q["cat"] == p["cat"] and q["id"] != p["id"]]
    main = f'''<main class="product-wrap">
  <p class="crumbs"><a href="/">Home</a> <span aria-hidden="true">›</span> <a href="{SITE}/{cpage}">{E(label)}</a></p>
  <div class="product-layout">
    <div class="product-img">
      <img src="/images/web/{p["id"]}.jpg" alt="{E(p["alt"], quote=True)}" fetchpriority="high">
    </div>
    <div class="product-info">
      <div class="product-bracket">{E(p["bracket"])}</div>
      <h1 class="product-title">{E(p["name"])}</h1>
      <p class="product-subtitle">{E(p["subtitle"])}</p>
      <p class="product-story">{E(p["story"])}</p>
      <p class="product-story"><strong>Watch out:</strong> {E(p["con"])}</p>
      {btns}
      <p class="disclosure">Prices change, and holiday sales can change them again, so check each retailer. The image is an AI-generated concept image, not a photo of the item.</p>
      <p class="product-date">Added {fmt_date()}</p>
    </div>
  </div>
  <a href="{SITE}/{cpage}" class="back-link">More in {E(label)}</a>
</main>'''
    s = re.sub(r'<main class="product-wrap">.*?</main>', lambda m: main, s, count=1, flags=re.S)
    rel_items = "\n".join(f'      <li><a href="{q["id"]}.html">{E(q["name"])}</a> <span>{E(q["bracket"])}</span></li>' for q in others[:4])
    rel = (f'<section class="np-related" aria-label="Related finds">\n  <h2>More gift ideas</h2>\n  <ul>\n{rel_items}\n  </ul>\n'
           f'  <a class="np-cat" href="/guides/holiday-gift-ideas-2026.html">See the holiday gift guide →</a>\n</section>')
    s = re.sub(r'<section class="np-related".*?</section>', lambda m: rel, s, count=1, flags=re.S)
    return s

def card(p):
    return (f'      <a href="products/{p["id"]}.html" class="product-card reveal">\n'
            f'        <div class="card-img"><img src="images/web/{p["id"]}.jpg" alt="{E(p["name"], quote=True)}" loading="lazy" decoding="async"><span class="card-chip">{E(p["bracket"])}</span></div>\n'
            f'        <div class="card-body">\n          <h2 class="card-title">{E(p["name"])}</h2>\n          <p class="card-subtitle">{E(p["subtitle"])}</p>\n'
            f'          <span class="card-cta">See the pick</span><p class="card-date">Added {fmt_date()}</p>\n        </div>\n      </a>\n')

def insert_cards():
    n = 0
    for page, test in (("home.html", lambda p: p["cat"] == "home"), ("pets.html", lambda p: p["cat"] == "pets"),
                       ("renter.html", lambda p: p["cat"] == "renter"), ("under25.html", lambda p: p["price"] <= 25)):
        f = os.path.join(ROOT, page); s = open(f, encoding="utf-8").read()
        marker = '<div class="product-grid" id="grid">\n'
        if marker not in s: print("NO GRID", page); continue
        add = "".join(card(p) for p in PICKS if test(p) and f'products/{p["id"]}.html' not in s)
        if add:
            s = s.replace(marker, marker + add, 1); open(f, "w", encoding="utf-8").write(s); n += add.count("<a href")
    return n

if __name__ == "__main__":
    write_guides(); print("guides written")
    print("products.js added:", append_products())
    for p in PICKS:
        f = os.path.join(ROOT, "products", p["id"] + ".html")
        if not os.path.exists(f):
            open(f, "w", encoding="utf-8").write(product_page(p))
    print("product pages:", len(PICKS))
    print("cards inserted:", insert_cards())
