#!/usr/bin/env python3
"""Oct 2026 redesign pass (stage 1): one nav, one footer, calmer category pages.

Idempotent. Run from the repo root AFTER build_home.py, build_guides.py and
seo_postprocess.py:   python3 tools/redesign.py

What it does
  * Replaces the nav and footer on every .html page with one shared version.
  * Category pages: new header (no emoji, neutral subtitle, pick count), cards rebuilt
    from products.js (plus any HTML-only cards), JSON-LD rebuilt with neutral text and
    cropped web images, client-side re-render script removed.
  * Product pages: shared.css linked, old nav CSS stripped, hovers gated, crumbs added.
Revert point: git tag pre-redesign-2026-10-16 (see REVERT.md).
"""
import glob, html, json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://nestandpaws.github.io"
E = html.escape

NAV_LINKS = [("/guides/", "Guides"), ("/renter.html", "Renter"), ("/home.html", "Home"), ("/pets.html", "Pets"),
             ("/beauty.html", "Beauty"), ("/under25.html", "Under $25"), ("/start-here.html", "Start here")]

CATS = {  # page: (h1, subtitle, meta description)
    "renter.html": ("Renter Friendly Upgrades", "No-drill, peel-and-stick and removable fixes for rentals",
                    "Renter-friendly picks: no-drill, peel-and-stick and removable upgrades for apartments, dorms and rentals, each with a note on what it fixes."),
    "home.html": ("Home & Kitchen Finds", "Storage, cleaning and kitchen picks for everyday homes",
                  "Home and kitchen picks, chosen one at a time: storage, cleaning, kitchen tools and small upgrades, each with a short note on what it fixes and who it suits."),
    "pets.html": ("Pet Must Haves", "Dog and cat picks, from grooming to scratchers",
                  "Dog and cat picks for daily use, not novelty: grooming, feeding, scratchers and treats, each with a short note."),
    "beauty.html": ("Beauty Finds", "Hair and skin care picks, each with a plain note on who it suits",
                    "Hair and skin care picks, weighted toward hair: brushes, tools, moisturizers and sunscreen, each with a plain note on who it suits."),
    "under25.html": ("Under $25 Finds", "Small fixes at small prices, across every category",
                     "Picks under $25 across home, renter-friendly, pets and beauty: small upgrades, each with a short note on what it fixes."),
    "seasonal.html": ("Seasonal Finds", "Timely picks for the current season",
                      "Seasonal picks for the current season and gifting window: decor, hosting and small gifts, grouped by price bracket."),
    "wedding.html": ("Wedding Table Decor", "Centerpieces, linens and hosting picks for the table",
                     "Wedding table decor and hosting picks: centerpieces, runners, linens and small details, grouped by price bracket."),
}
FILTERS = {"renter.html": lambda p: p["category"] == "renter", "home.html": lambda p: p["category"] == "home",
           "pets.html": lambda p: p["category"] == "pets", "beauty.html": lambda p: p["category"] == "beauty",
           "under25.html": lambda p: p["price"] <= 25.0, "seasonal.html": lambda p: p["category"] == "seasonal",
           "wedding.html": lambda p: p["category"] == "wedding"}


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def load_products():
    js = os.path.join(ROOT, "products.js")
    node = "const fs=require('fs');const P=new Function(fs.readFileSync(process.argv[1],'utf8')+';return PRODUCTS')();console.log(JSON.stringify(P))"
    return json.loads(subprocess.check_output(["node", "-e", node, js]))


# ---------------------------------------------------------------- shared chrome
def nav_html(page):
    links = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u.strip("/") == page or (u == "/guides/" and page.startswith("guides/")) else ""}>{E(t)}</a>'
                    for u, t in NAV_LINKS)
    return ('<a class="skip-link" href="#main">Skip to content</a>\n'
            '<nav class="site-nav" aria-label="Main">\n  <div class="nav-inner">\n'
            '    <a href="/" class="nav-brand">Nest <span>&amp;</span> Paws</a>\n'
            f'    <div class="nav-links">{links}</div>\n  </div>\n</nav>\n<div id="main" tabindex="-1"></div>')


def footer_html():
    cols = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in [("/guides/", "Guides"), ("/renter.html", "Renter friendly"), ("/home.html", "Home and kitchen"),
                                                         ("/pets.html", "Pets"), ("/beauty.html", "Beauty"), ("/under25.html", "Under $25")])
    about = "".join(f'<a href="{u}"{x}>{E(t)}</a>' for u, t, x in [("/start-here.html", "Start here", ""), ("/about.html", "About", ""), ("/privacy.html", "Privacy", ""),
                                                                   ("https://pinterest.com/NestandPaws", "Pinterest", ' target="_blank" rel="noopener"')])
    return ('<footer class="site-footer">\n  <div class="foot-grid">\n'
            '    <div><p class="foot-brand">Nest &amp; Paws</p><p class="foot-tag">Independent picks for small spaces, pets and everyday routines. Researched from listings, not tested by us.</p></div>\n'
            f'    <div><p class="foot-h">Browse</p><div class="foot-links">{cols}</div></div>\n'
            f'    <div><p class="foot-h">About</p><div class="foot-links">{about}</div></div>\n  </div>\n'
            '  <p class="foot-note">Independent. Not affiliated with or endorsed by Amazon. Links go to Amazon. Prices change, so check the listing. Product images are illustrations, not photos of the item.</p>\n</footer>')


def swap_chrome(s, page):
    s = re.sub(r'href="/?shared\.css(?:\?v=\d+)?"', 'href="/shared.css?v=3"', s)
    s = s.replace('content="/images/', 'content="' + SITE + '/images/').replace('"image": "/images/', '"image": "' + SITE + '/images/')
    nav = nav_html(page)
    if re.search(r"<nav[\s>]", s):
        s = re.sub(r'(?:<a class="skip-link"[^>]*>[^<]*</a>\s*)?<nav[\s>].*?</nav>(?:\s*<div id="main" tabindex="-1"></div>)?', lambda m: nav, s, count=1, flags=re.S)
    else:
        s = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + nav, s, count=1)
    foot = footer_html()
    if re.search(r"<footer[\s>]", s):
        s = re.sub(r"<footer[\s>].*?</footer>", lambda m: foot, s, count=1, flags=re.S)
    else:
        s = s.replace("</body>", foot + "\n</body>", 1)
    return s


# ---------------------------------------------------------------- category pages
def parse_cards(s):
    cards = {}
    for m in re.finditer(r'<a href="products/([^"]+)\.html" class="product-card[^"]*"[^>]*>(.*?)</a>', s, flags=re.S):
        pid, b = m.group(1), m.group(2)
        if "$" in pid: continue   # JS template literal, not a real card
        g = lambda rx: (re.search(rx, b, flags=re.S).group(1) if re.search(rx, b, flags=re.S) else "")
        cards[pid] = dict(id=pid, title=html.unescape(g(r'card-title">(.*?)</')), subtitle=html.unescape(g(r'card-subtitle">(.*?)</')),
                          bracket=html.unescape(g(r'card-(?:bracket|chip)">(.*?)</')), date=g(r'card-date">Added (.*?)</'),
                          image=g(r'<img src="([^"]+)"'))
    return cards


def fmt_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def card_html(c):
    date = f'<p class="card-date">Added {E(c["date"])}</p>' if c["date"] else ""
    return (f'      <a href="products/{c["id"]}.html" class="product-card reveal">\n'
            f'        <div class="card-img"><img src="{E(c["image"])}" alt="{E(c["title"])}" loading="lazy" decoding="async">'
            f'<span class="card-chip">{E(c["bracket"])}</span></div>\n'
            f'        <div class="card-body">\n          <h2 class="card-title">{E(c["title"])}</h2>\n'
            f'          <p class="card-subtitle">{E(c["subtitle"])}</p>\n'
            f'          <span class="card-cta">See the pick</span>{date}\n        </div>\n      </a>')


def asin_of(link):
    m = re.search(r"/dp/([A-Z0-9]{10})", link or "")
    return m.group(1) if m else None


ALL_IDS = set()


def do_category(page, products):
    p = os.path.join(ROOT, page); s = read(p)
    h1, sub, desc = CATS[page]
    old = parse_cards(s)
    cards, order = {}, []
    for pr in products:
        if FILTERS[page](pr):
            cards[pr["id"]] = dict(id=pr["id"], title=pr["title"], subtitle=pr["subtitle"], bracket=pr["price_bracket"],
                                   date=fmt_date(pr["date_added"]) if pr.get("date_added") else "", image=pr["image"],
                                   asin=asin_of(pr.get("affiliate_link")), iso=pr.get("date_added"))
            order.append(pr["id"])
    for pid, c in old.items():          # HTML-only products stay
        if pid not in cards and pid not in ALL_IDS:
            cards[pid] = dict(c, asin=None, iso=None); order.append(pid)
    # old LD for sku/date of HTML-only cards
    ld_old = {}
    for m in re.finditer(r'"url": "https://nestandpaws.github.io/products/([^"]+)\.html".*?(?:"sku": "([^"]+)")?(?:,\s*"releaseDate": "([^"]+)")?\s*\}', s, flags=re.S):
        ld_old[m.group(1)] = (m.group(2), m.group(3))
    grid = "\n".join(card_html(cards[i]) for i in order)
    # header
    hdr = (f'<header class="cat-header">\n  <div class="inner">\n    <p class="cat-kicker">Collection</p>\n    <h1>{E(h1, quote=False)}</h1>\n'
           f'    <p class="cat-sub">{E(sub)}</p>\n    <p class="cat-count">{len(order)} picks</p>\n  </div>\n</header>')
    s = re.sub(r'<div class="cat-header">.*?</div>\s*</div>', lambda m: hdr, s, count=1, flags=re.S)
    s = re.sub(r'<header class="cat-header">.*?</header>', lambda m: hdr, s, count=1, flags=re.S)
    # grid
    s = re.sub(r'(<div class="product-grid" id="grid">).*?(\n  </div>\n</div>\n)(?=\s*<footer)',
               lambda m: m.group(1) + "\n" + grid + m.group(2), s, count=1, flags=re.S)
    # drop client-side re-render
    s = re.sub(r'<script src="products.js"></script>\s*<script>.*?</script>\s*', "", s, flags=re.S)
    s = s.replace('<p class="section-label">All finds in this category</p>', '<p class="section-label">All picks in this collection</p>')
    # JSON-LD ItemList
    items = []
    for n, pid in enumerate(order, 1):
        c = cards[pid]; sku, rel = (c.get("asin"), c.get("iso"))
        if not sku and pid in ld_old: sku, rel = ld_old[pid]
        item = {"@type": "Product", "name": c["title"], "url": f"{SITE}/products/{pid}.html", "description": c["subtitle"],
                "category": h1, "image": f"{SITE}/{c['image']}" if not c["image"].startswith("http") else c["image"]}
        if sku: item["sku"] = sku
        if rel: item["releaseDate"] = rel
        items.append({"@type": "ListItem", "position": n, "item": item})
    ld = json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": f"{h1} — Nest & Paws", "itemListElement": items}, indent=2, ensure_ascii=False)
    s = re.sub(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "ItemList".*?</script>',
               lambda m: '<script type="application/ld+json">\n' + ld + "\n</script>", s, count=1, flags=re.S)
    # meta descriptions
    d = E(desc)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), s)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), s)
    # compare table: drop rows for products no longer in this collection
    def keep_row(m):
        r = re.search(r'href="products/([^"]+)\.html"', m.group(0))
        return m.group(0) if (not r or r.group(1) in cards) else ''
    s = re.sub(r'\s*<tr>\s*<td class="compare-product".*?</tr>', keep_row, s, flags=re.S)
    # main landmark
    s = swap_chrome(s, page)
    write(p, s)
    return len(order)


# ---------------------------------------------------------------- product pages
INLINE_NAV = re.compile(r"\n\s*nav \{.*?\}\n(?:\s*\.nav-brand \{.*?\}\n)?(?:\s*\.nav-back \{.*?\}\n)?(?:\s*\.nav-back:hover \{.*?\}\n)?", re.S)


def gate_hovers(css):
    def wrap(m):
        return "@media (hover: hover) and (pointer: fine) { " + m.group(0).strip() + " }"
    css = re.sub(r"(?<!\{ )\.cta-btn:hover \{[^}]*\}", wrap, css)
    css = re.sub(r"(?<!\{ )\.back-link:hover \{[^}]*\}", wrap, css)
    return css


def do_product(path):
    s = read(path); name = os.path.basename(path)
    page = "products/" + name
    if "/shared.css" not in s:
        s = s.replace("  <style>", '  <link rel="stylesheet" href="/shared.css">\n  <style>', 1)
    s = INLINE_NAV.sub("\n", s, count=1)
    s = gate_hovers(s)
    s = s.replace('src="https://nestandpaws.github.io/images/', 'src="/images/')
    s = re.sub(r'(<div class="product-img">\s*<img [^>]*?) onerror="[^"]*"', r'\1 fetchpriority="high"', s)
    s = re.sub(r'(\.(?:disclosure|product-date) \{[^}]*?)color: var\(--sand\);', lambda m: m.group(1) + 'color: var(--wood);', s)
    cat = re.search(r'"position": 2,\s*"name": "([^"]+)",\s*"item": "([^"]+)"', s)
    if cat and "crumbs" not in s:
        cn, cu = cat.group(1), cat.group(2)
        crumbs = f'<p class="crumbs"><a href="/">Home</a> <span aria-hidden="true">›</span> <a href="{cu}">{E(cn)}</a></p>\n'
        s = s.replace('<div class="product-wrap">\n', '<div class="product-wrap">\n  ' + crumbs, 1)
        s = re.sub(r'<a href="\.\./index\.html" class="back-link">[^<]*</a>', lambda m: f'<a href="{cu}" class="back-link">More in {E(cn)}</a>', s)
    s = s.replace('<div class="product-wrap">', '<main class="product-wrap">', 1)
    s = re.sub(r'(</div>\s*)(<!-- np-seo:related -->)', lambda m: m.group(1).replace("</div>", "</main>", 1) + m.group(2), s, count=1) if "</main>" not in s else s
    s = swap_chrome(s, page)
    write(path, s)


def main():
    products = load_products()
    ALL_IDS.update(p['id'] for p in products)
    for page in CATS:
        n = do_category(page, products); print(page, n, "cards")
    for path in sorted(glob.glob(os.path.join(ROOT, "products", "*.html"))):
        do_product(path)
    print("products", len(glob.glob(os.path.join(ROOT, "products", "*.html"))))
    others = ["index.html", "404.html", "about.html", "privacy.html", "start-here.html", "product.html", "guides/index.html"] + \
             [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "guides", "*.html")) if not p.endswith("index.html")]
    for rel in sorted(set(others)):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            s = read(p)
            if rel == "product.html":
                if "/shared.css" not in s: s = s.replace("  <style>", '  <link rel="stylesheet" href="/shared.css">\n  <style>', 1)
                s = INLINE_NAV.sub("\n", s, count=1)
            write(p, swap_chrome(s, rel))
    # keep seo_postprocess descriptions in step so reruns do not undo the neutral copy
    sp = os.path.join(ROOT, "tools", "seo_postprocess.py"); t = read(sp)
    for page, (h1, sub, desc) in CATS.items():
        t = re.sub(r'(\("' + re.escape(page) + r'",\s*"[^"]*",\s*)"[^"]*"(\))', lambda m: m.group(1) + json.dumps(desc) + m.group(2), t)
        key = page.replace(".html", "")
        t = re.sub(r'("' + key + r'":\s*\("' + re.escape(page) + r'",\s*"[^"]*",\s*)"[^"]*"(\))', lambda m: m.group(1) + json.dumps(desc) + m.group(2), t)
    write(sp, t)


if __name__ == "__main__":
    main()
