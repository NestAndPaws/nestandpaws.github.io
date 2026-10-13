#!/usr/bin/env python3
"""Nest & Paws guide builder.

Reads tools/guides/*.json and writes:
  guides/{slug}.html      one page per guide
  guides/index.html       guides listing
  images/guides/{id}.jpg  small copies of product images (original PNGs untouched)

Idempotent. Run from the repo root:  python3 tools/build_guides.py
Links on guides are plain Amazon /dp/ASIN links (no tag). When a program approves
the site, set AFFILIATE_QUERY below and add the disclosure line (DISCLOSURE).
"""
import html, json, os, glob
from PIL import Image

SITE = "https://nestandpaws.github.io"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AFFILIATE_QUERY = ""      # e.g. "?tag=NEWTAG-20" once a program approves. Empty = plain links.
DISCLOSURE = ""           # e.g. "This page has affiliate links. I earn a commission if you buy through them."

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">')


def esc(s):
    return html.escape(s, quote=True)


def nav():
    return ('<nav>\n  <a href="/" class="nav-brand">Nest &amp; Paws</a>\n'
            '  <span class="nav-links"><a href="/guides/">Guides</a><a href="/start-here.html">Start here</a>'
            '<a href="/renter.html">Renter finds</a></span>\n</nav>')


def footer():
    return ('<footer>\n  <p>Nest &amp; Paws · <a href="/start-here.html">Start here</a> · <a href="/about.html">About</a> · '
            '<a href="/privacy.html">Privacy</a> · <a href="https://pinterest.com/NestandPaws" target="_blank" rel="noopener">@NestandPaws on Pinterest</a></p>\n'
            '  <p class="foot-note">Independent. Not affiliated with or endorsed by Amazon. Prices change, so check the listing.</p>\n</footer>')


def thumb(img_id):
    src = os.path.join(ROOT, "images", f"{img_id}.png")
    out_dir = os.path.join(ROOT, "images", "guides")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"{img_id}.jpg")
    if os.path.exists(src) and not os.path.exists(dst):
        im = Image.open(src).convert("RGB")
        im.thumbnail((720, 960))
        im.save(dst, "JPEG", quality=82, optimize=True)
    return f"/images/guides/{img_id}.jpg"


def link(asin):
    return f"https://www.amazon.com/dp/{asin}{AFFILIATE_QUERY}"


def stars_row(n):
    return "●" * n + "○" * (5 - n)


def render_guide(g, all_guides):
    url = f"{SITE}/guides/{g['slug']}.html"
    picks = g["picks"]
    rows = "\n".join(
        f'      <tr><td data-label="Pick"><a href="#pick-{i+1}">{esc(p["name"].split(" (")[0].split(",")[0])}</a></td>'
        f'<td data-label="Best for">{esc(p["best_for"])}</td><td data-label="Watch out">{esc(p["limit"])}</td>'
        f'<td data-label="Price">{esc(p["price_bracket"])}</td></tr>'
        for i, p in enumerate(picks))
    cards = []
    for i, p in enumerate(picks):
        cards.append(f'''  <article class="pick" id="pick-{i+1}">
    <div class="pick-img"><img src="{thumb(p["image"])}" alt="{esc(p["alt"])}" loading="lazy" width="360" height="480"><span class="img-note">Illustration, not a photo of the item</span></div>
    <div class="pick-body">
      <p class="pick-num">Pick {i+1}</p>
      <h3>{esc(p["name"])}</h3>
      <p class="pick-meta"><span>{esc(p["price_bracket"])}</span><span>{p["stars"]} stars, {p["ratings"]} ratings</span></p>
      <p class="safe" title="Deposit-safe score, research-based"><span class="dots" aria-hidden="true">{stars_row(p["safe"])}</span> Deposit-safe {p["safe"]} of 5. {esc(p["safe_note"])}</p>
      <p>{esc(p["why"])}</p>
      <p class="watch"><strong>Watch out:</strong> {esc(p["con"])}</p>
      <a class="btn" href="{link(p["asin"])}" target="_blank" rel="noopener noreferrer">See it on Amazon →</a>
      <p class="check">Check the current price on the listing. Rating and count as of {esc(g["last_checked"])}.</p>
    </div>
  </article>''')
    related = [x for x in all_guides if x["slug"] in g.get("related", [])]
    rel_html = ""
    if related:
        rel_html = ('<section class="g-section"><h2>Related guides</h2><ul class="rel">' +
                    "".join(f'<li><a href="/guides/{r["slug"]}.html">{esc(r["title"])}</a></li>' for r in related) +
                    "</ul></section>")
    article = {
        "@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["description"],
        "datePublished": g["published"], "dateModified": g["updated"], "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "Nest & Paws", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "Nest & Paws", "url": SITE + "/"}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nest & Paws", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": SITE + "/guides/"},
        {"@type": "ListItem", "position": 3, "name": g["title"], "item": url}]}
    disc = f'<p class="disclosure-line">{esc(DISCLOSURE)}</p>' if DISCLOSURE else ""
    skipped = "".join(f"<li>{esc(s)}</li>" for s in g["skipped"])
    how = "".join(f"<li>{esc(s)}</li>" for s in g["how_picked"])
    hook = "".join(f"<p>{esc(t)}</p>" for t in g["hook"])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(g["title"])} | Nest &amp; Paws</title>
  <meta name="description" content="{esc(g["description"])}">
  <link rel="canonical" href="{url}">
  {FONTS}
  <link rel="stylesheet" href="/shared.css">
  <meta property="og:site_name" content="Nest &amp; Paws">
  <meta property="og:title" content="{esc(g["title"])}">
  <meta property="og:description" content="{esc(g["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{json.dumps(article, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>
</head>
<body>
{nav()}
<main class="guide">
  <header class="g-head">
    <p class="g-kicker">{esc(g["problem_tag"])} guide · {esc(g["constraint"])}</p>
    <h1>{esc(g["title"])}</h1>
    <p class="g-dek">{esc(g["dek"])}</p>
    <p class="g-by">By Nest &amp; Paws · Checked {esc(g["last_checked"])} · <a href="/start-here.html">How I pick</a></p>
    {disc}
  </header>
  <section class="g-section">
    {hook}
  </section>
  <section class="g-section" id="quick-picks">
    <h2>Quick picks</h2>
    <div class="qp-scroll"><table class="qp">
      <thead><tr><th>Pick</th><th>Best for</th><th>Watch out</th><th>Price</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table></div>
    <p class="g-note">Deposit-safe score: how likely the item is to leave no mark if installed and removed the way the maker says (1 to 5). It comes from the mounting method and the maker's removal guidance. Research-based, not tested by us.</p>
  </section>
  <section class="g-section">
    <h2>The picks</h2>
{chr(10).join(cards)}
  </section>
  <section class="g-section">
    <h2>If you buy one</h2>
    <p>{esc(g["final"])}</p>
  </section>
  <section class="g-section">
    <h2>What I skipped</h2>
    <ul>{skipped}</ul>
  </section>
  <section class="g-section">
    <h2>How I picked</h2>
    <ul>{how}</ul>
    <p class="g-note">Not tested by us. Ratings and review notes come from the Amazon listing on {esc(g["last_checked"])}; review summaries on Amazon are generated from customer reviews. Prices are brackets because Amazon prices change. Product images on this page are illustrations.</p>
  </section>
  {rel_html}
</main>
{footer()}
</body>
</html>
'''


def render_index(all_guides):
    items = []
    for g in all_guides:
        items.append(f'''    <a class="g-card" href="/guides/{g["slug"]}.html">
      <p class="g-kicker">{esc(g["problem_tag"])} · {esc(g["constraint"])}</p>
      <h2>{esc(g["title"])}</h2>
      <p>{esc(g["dek"])}</p>
      <span class="g-more">Read the guide →</span>
    </a>''')
    url = SITE + "/guides/"
    lst = {"@context": "https://schema.org", "@type": "ItemList", "name": "Nest & Paws guides", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/guides/{g['slug']}.html", "name": g["title"]} for i, g in enumerate(all_guides)]}
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renter Guides | Nest &amp; Paws</title>
  <meta name="description" content="Short buying guides for renters and small homes. Each one matches picks to a job, shows the weight limit and the catch, and says how it was chosen.">
  <link rel="canonical" href="{url}">
  {FONTS}
  <link rel="stylesheet" href="/shared.css">
  <meta property="og:site_name" content="Nest &amp; Paws">
  <meta property="og:title" content="Renter Guides | Nest &amp; Paws">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="website">
  <script type="application/ld+json">{json.dumps(lst, ensure_ascii=False)}</script>
</head>
<body>
{nav()}
<main class="guide">
  <header class="g-head">
    <p class="g-kicker">Guides</p>
    <h1>Guides for renters and small homes</h1>
    <p class="g-dek">Each guide starts with a problem, shows three to five picks, and says what can go wrong.</p>
  </header>
  <section class="g-list">
{chr(10).join(items)}
  </section>
</main>
{footer()}
</body>
</html>
'''


def main():
    guides = []
    for f in glob.glob(os.path.join(ROOT, "tools", "guides", "*.json")):
        guides.append(json.load(open(f, encoding="utf-8")))
    guides.sort(key=lambda g: (g["published"], g["slug"]), reverse=True)
    os.makedirs(os.path.join(ROOT, "guides"), exist_ok=True)
    for g in guides:
        with open(os.path.join(ROOT, "guides", f"{g['slug']}.html"), "w", encoding="utf-8") as fh:
            fh.write(render_guide(g, guides))
    with open(os.path.join(ROOT, "guides", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_index(guides))
    print(f"built {len(guides)} guides + index")


if __name__ == "__main__":
    main()
