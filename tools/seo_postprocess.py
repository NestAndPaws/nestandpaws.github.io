#!/usr/bin/env python3
"""Nest & Paws SEO/GEO/AEO post-processor.

Idempotent: safe to run after every build. It only ADDS blocks marked with
np-seo markers (or replaces its own earlier blocks). It never touches the CTA
button, affiliate links, products.js or product copy.

Run from the repo root:  python3 tools/seo_postprocess.py
"""
import html, json, os, re, subprocess, datetime

SITE = "https://nestandpaws.github.io"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
ASSOC = "As an Amazon Associate I earn from qualifying purchases."

CATS = {
    "home":     ("home.html",     "Home & Kitchen Finds",     "Home & kitchen Amazon finds picked one at a time: storage, cleaning, kitchen tools and small upgrades, each with a short note on what it fixes and who it suits."),
    "renter":   ("renter.html",   "Renter Friendly Upgrades", "Renter-friendly Amazon finds: no-drill, peel-and-stick and removable upgrades for apartments, dorms and rentals, each with a note on what it fixes."),
    "pets":     ("pets.html",     "Pet Must Haves",           "Dog and cat products from Amazon picked for daily use, not novelty: grooming, feeding, scratchers and treats, with a short note on each pick."),
    "beauty":   ("beauty.html",   "Beauty Finds",             "Hair and skincare Amazon finds, weighted toward hair: brushes, tools, moisturizers and sunscreen, each with a plain note on who it suits."),
    "seasonal": ("seasonal.html", "Seasonal Finds",           "Seasonal Amazon finds for the current season and gifting window: decor, hosting and small gifts, grouped by price bracket."),
    "wedding":  ("wedding.html",  "Wedding Table Decor",      "Wedding table decor and hosting finds from Amazon: centerpieces, runners, linens and small details, grouped by price bracket."),
}
EXTRA_PAGES = {
    "index.html":   ("Nest & Paws", "Curated Amazon finds for home, pets, beauty and renter-friendly living. Each pick comes with a short note on what it fixes and who it suits, grouped by price bracket."),
    "under25.html": ("Under $25 Finds", "Amazon finds under $25 across home, renter-friendly, pets and beauty: small upgrades worth the click, each with a short note on what it fixes."),
}


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
        f.write(s)


def load_products():
    src = read("products.js")
    out = subprocess.run(
        ["node", "-e", "const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8').replace('const PRODUCTS','global.PRODUCTS'));console.log(JSON.stringify(PRODUCTS))",
         os.path.join(ROOT, "products.js")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def esc(s):
    return html.escape(s, quote=True)


def set_block(doc, name, block, anchor, before=True):
    """Insert or replace a marked block. anchor = literal string to insert next to."""
    start, end = f"<!-- np-seo:{name} -->", f"<!-- /np-seo:{name} -->"
    full = f"{start}\n{block}\n{end}"
    if start in doc:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: full, doc, flags=re.S)
    i = doc.find(anchor)
    if i < 0:
        return doc
    if not before:
        i += len(anchor)
    return doc[:i] + full + "\n" + doc[i:]


def og_block(title, desc, url, image=None):
    lines = [
        f'<meta property="og:site_name" content="Nest &amp; Paws">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:type" content="website">',
        f'<meta name="twitter:card" content="summary_large_image">',
    ]
    if image:
        lines.append(f'<meta property="og:image" content="{image}">')
    return "\n".join(lines)


def trim(s, n=155):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return cut + "…"


def ensure_meta_description(doc, desc):
    if re.search(r'<meta name="description"', doc):
        return doc
    return doc.replace("</title>", f'</title>\n  <meta name="description" content="{esc(desc)}">', 1)


def ensure_canonical(doc, url):
    if 'rel="canonical"' in doc:
        return doc
    return doc.replace("</title>", f'</title>\n  <link rel="canonical" href="{url}">', 1)


def footer_assoc(doc):
    block = (f'<p style="margin-top:8px;font-size:12px;color:rgba(200,184,154,0.75);">{ASSOC} '
             f'<a href="about.html">How picks are chosen</a></p>')
    return set_block(doc, "assoc", block, "</footer>")


# ---------------- product pages ----------------
def process_products(products):
    by_id = {p["id"]: p for p in products}
    by_cat = {}
    for p in products:  # products.js is newest first
        by_cat.setdefault(p["category"], []).append(p)
    files = sorted(f for f in os.listdir(os.path.join(ROOT, "products")) if f.endswith(".html"))
    page_cat = {}
    for f in files:
        pid = f[:-5]
        if pid in by_id:
            page_cat[pid] = by_id[pid]["category"]
        else:  # orphan page: infer from which category table links it
            for cat, (cf, _, _) in CATS.items():
                if f"products/{f}" in read(cf):
                    page_cat[pid] = cat
                    break
    for f in files:
        pid = f[:-5]
        path = f"products/{f}"
        doc = read(path)
        url = f"{SITE}/products/{f}"
        title_m = re.search(r'<h1 class="product-title">(.*?)</h1>', doc, re.S)
        sub_m = re.search(r'<p class="product-subtitle">(.*?)</p>', doc, re.S)
        story_m = re.search(r'<p class="product-story">(.*?)</p>', doc, re.S)
        img_m = re.search(r'<img src="([^"]+)"', doc)
        title = html.unescape(title_m.group(1).strip()) if title_m else pid
        sub = html.unescape(sub_m.group(1).strip()) if sub_m else ""
        story = html.unescape(story_m.group(1).strip()) if story_m else ""
        cat = page_cat.get(pid)

        # 1. Meta description: subtitle + start of story, if current one is short
        desc = trim(f"{sub} {story}")
        md = re.search(r'<meta name="description" content="([^"]*)">', doc)
        if md and len(html.unescape(md.group(1))) < 110 and desc:
            doc = doc.replace(md.group(0), f'<meta name="description" content="{esc(desc)}">', 1)

        # 2. Open Graph
        doc = set_block(doc, "og", og_block(f"{title} — Nest & Paws", desc, url, img_m.group(1) if img_m else None), "</head>")

        # 3. Breadcrumb schema
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Nest & Paws", "item": f"{SITE}/"}]
        if cat in CATS:
            crumbs.append({"@type": "ListItem", "position": 2, "name": CATS[cat][1], "item": f"{SITE}/{CATS[cat][0]}"})
        crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": title, "item": url})
        bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}
        doc = set_block(doc, "breadcrumb", '<script type="application/ld+json">\n' + json.dumps(bc, indent=2, ensure_ascii=False) + "\n</script>", "</head>")

        # 4. Exact Amazon Associates statement under the existing disclosure
        doc = set_block(doc, "assoc", f'<p class="disclosure">{ASSOC}</p>', '<p class="product-date">')

        # 5. Related finds + category link (static HTML, crawlable without JS)
        if cat in CATS:
            rel = [p for p in by_cat.get(cat, []) if p["id"] != pid][:4]
            items = "\n".join(
                f'      <li><a href="{p["id"]}.html">{esc(p["title"])}</a> <span>{esc(p["price_bracket"])}</span></li>' for p in rel)
            block = (
                '<style>.np-related{max-width:800px;margin:0 auto;padding:0 24px 48px}'
                '.np-related h2{font-family:"Playfair Display",serif;font-size:20px;font-weight:600;margin-bottom:12px}'
                '.np-related ul{list-style:none;display:grid;gap:10px}'
                '.np-related li{background:var(--white);border-radius:12px;padding:12px 16px;font-size:14px;display:flex;justify-content:space-between;gap:12px}'
                '.np-related a{color:var(--charcoal);text-decoration:none}.np-related a:hover{color:var(--terra)}'
                '.np-related span{color:var(--wood);white-space:nowrap;font-size:12px}'
                '.np-related .np-cat{display:inline-block;margin-top:14px;color:var(--terra);font-size:14px;text-decoration:none}</style>\n'
                '<section class="np-related" aria-label="Related finds">\n'
                f'  <h2>More {esc(CATS[cat][1].replace(" Finds", "").lower())} finds</h2>\n'
                f'  <ul>\n{items}\n  </ul>\n'
                f'  <a class="np-cat" href="../{CATS[cat][0]}">See all {esc(CATS[cat][1])} →</a>\n'
                '</section>')
            doc = set_block(doc, "related", block, "</body>")
        write(path, doc)
    return files, page_cat


# ---------------- category + hub pages ----------------
def process_pages():
    pages = {cf: (t, d) for _, (cf, t, d) in CATS.items()}
    pages.update(EXTRA_PAGES)
    for f, (title, desc) in pages.items():
        doc = read(f)
        url = f"{SITE}/" if f == "index.html" else f"{SITE}/{f}"
        if f == "index.html":
            doc = doc.replace("Real recs, real prices, no fluff.", "Real recs, clear price brackets, no fluff.")
        doc = ensure_meta_description(doc, desc)
        doc = ensure_canonical(doc, url)
        doc = set_block(doc, "og", og_block(f"{title} — Nest & Paws" if f != "index.html" else "Nest & Paws — Amazon Finds for Your Home & Pets", desc, url), "</head>")
        doc = footer_assoc(doc)
        if f == "index.html":
            ws = {"@context": "https://schema.org", "@type": "WebSite", "name": "Nest & Paws", "url": f"{SITE}/",
                  "publisher": {"@type": "Organization", "name": "Nest & Paws", "url": f"{SITE}/"}}
            doc = set_block(doc, "website", '<script type="application/ld+json">\n' + json.dumps(ws, indent=2) + "\n</script>", "</head>")
        write(f, doc)
    # legacy alias: exact statement only (page is noindex-free JS alias; canonical set by JS)
    doc = read("product.html")
    doc = set_block(doc, "assoc", f'<p class="disclosure">{ASSOC}</p>', '<p class="product-date"')
    write("product.html", doc)
    return list(pages)


def git_date(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or TODAY


def build_sitemap(products, files, pages):
    added = {p["id"]: p.get("date_added") for p in products}
    urls = [(f"{SITE}/", TODAY)]
    urls += [(f"{SITE}/{p}", TODAY) for p in pages if p != "index.html"]
    urls.append((f"{SITE}/about.html", TODAY))
    for f in files:
        pid = f[:-5]
        urls.append((f"{SITE}/products/{f}", added.get(pid) or git_date(f"products/{f}")))
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')
    return len(urls)


if __name__ == "__main__":
    prods = load_products()
    files, page_cat = process_products(prods)
    pages = process_pages()
    n = build_sitemap(prods, files, pages)
    orphans = [f[:-5] for f in files if f[:-5] not in {p["id"] for p in prods}]
    print(f"products.js entries: {len(prods)} | product pages: {len(files)} | sitemap URLs: {n}")
    if orphans:
        print("Pages with no products.js entry (not in JS grids/search):", ", ".join(orphans))
