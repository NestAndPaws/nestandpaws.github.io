#!/usr/bin/env python3
"""Rebuild the home page body (styles, hero, sections) and thumbnails in images/home/. Idempotent."""
import os, re, json, html
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def thumb(i, w=520, h=520):
    out = os.path.join(ROOT, "images", "home"); os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, i + ".jpg")
    if not os.path.exists(dst):
        im = Image.open(os.path.join(ROOT, "images", i + ".png")).convert("RGB"); im.thumbnail((w, h)); im.save(dst, "JPEG", quality=80, optimize=True)
    return f"/images/home/{i}.jpg"
E = html.escape

CATS = [("renter.html", "Renter friendly", "No drilling, no damage", "command-picture-strips", "c1"),
        ("home.html", "Home and kitchen", "Storage, cleaning, tools", "cisily-sink-caddy", "c2"),
        ("under25.html", "Under $25", "Small fixes, small price", "bluestars-outlet-extender-night-light", "c3"),
        ("seasonal.html", "Seasonal", "Timely picks", "artoid-mode-fall-table-runner", "c4"),
        ("pets.html", "Pets", "Dogs and cats", "dog-cooling-mat", "c5"),
        ("beauty.html", "Beauty", "Hair and skin", "cosrx-snail-mucin", "c6"),
        ("wedding.html", "Wedding table", "Decor and hosting", "ourholiday-acrylic-wedding-table-numbers", "c7")]
FRESH = [("korcci-suction-cup-hooks-12pack", "Clear suction cup hooks", "Under $10"),
         ("yasonic-adhesive-shower-caddy-2pack", "Adhesive shower caddy", "Under $10"),
         ("meohui-cat-wand-toys-2pack", "Cat feather wand toys", "Under $10"),
         ("duck-window-insulation-kit-10-windows", "Window insulation kit", "Under $20"),
         ("innqoo-candle-warmer-lamp", "Candle warmer lamp", "Under $20"),
         ("kitty-city-xl-cat-scratcher-pads-3pack", "XL cat scratcher pads", "Under $20"),
         ("lumigens-6-tier-pants-hangers", "6-tier pants hangers", "Under $15"),
         ("anua-pdrn-hyaluronic-acid-100-cream", "Hyaluronic acid cream", "Under $25")]
GUIDES = [("renter-winter-draft-fixes", "Stop Winter Drafts in a Rental Apartment", "Two fixes for the two places cold air gets in: the window glass and the gap under the door.", "2 picks · under $30", ["grotheory-door-draft-stopper", "duck-window-insulation-kit-10-windows"]),
          ("no-drill-hooks-for-renters", "No-Drill Hooks for Renters That Hold", "Four picks matched to the surface. Each under $20. Nothing goes into the wall.", "4 picks · under $20 each", ["command-variety-pack-19pc", "korcci-suction-cup-hooks-12pack", "optish-over-door-hooks"])]

CSS = """
    :root { --sage:#5C7A5A; --blush:#F2D9C8; --butter:#F6E3A8; }
    html { scroll-behavior: smooth; }
    .hero { background: linear-gradient(135deg,#2C2420 0%,#3b2a22 55%,#4a3024 100%); padding: 54px 24px 0; text-align: center; position: relative; overflow: hidden; }
    .hero::before { content:''; position:absolute; inset:-20%; background: radial-gradient(circle at 20% 30%, rgba(193,122,74,.38), transparent 45%), radial-gradient(circle at 80% 70%, rgba(92,122,90,.30), transparent 45%); animation: drift 14s ease-in-out infinite alternate; }
    @keyframes drift { to { transform: translate3d(3%,-3%,0) scale(1.08); } }
    .hero-inner { position:relative; z-index:2; max-width:640px; margin:0 auto; padding-bottom:26px; }
    .brand-tag { display:inline-block; font-size:11px; font-weight:500; letter-spacing:3px; text-transform:uppercase; color:#fff; background:var(--terra); padding:6px 14px; border-radius:100px; margin-bottom:16px; }
    .hero h1 { font-family:'Playfair Display',serif; font-size:clamp(40px,9vw,68px); font-weight:400; color:var(--white); line-height:1.05; margin-bottom:12px; }
    .hero h1 em { font-style:italic; color:var(--blush); display:inline-block; animation: sway 4s ease-in-out infinite; }
    @keyframes sway { 50% { transform: rotate(-6deg) scale(1.08); } }
    .hero-sub { font-size:17px; font-weight:300; color:var(--sand); margin-bottom:22px; }
    .chips { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-bottom:22px; }
    .chips span { font-size:13px; color:var(--cream); background:rgba(245,237,214,.12); border:1px solid rgba(245,237,214,.22); padding:6px 14px; border-radius:100px; }
    .search-wrap { max-width:480px; margin:0 auto; }
    .search-wrap input { width:100%; padding:15px 22px; border-radius:100px; border:2px solid transparent; background:var(--white); color:var(--charcoal); font-family:'DM Sans',sans-serif; font-size:15px; outline:none; box-shadow:0 8px 28px rgba(0,0,0,.25); transition:border-color .2s, transform .2s; }
    .search-wrap input:focus { border-color:var(--terra); transform:translateY(-1px); }
    .float { position:absolute; z-index:1; width:110px; height:110px; border-radius:50%; object-fit:cover; border:4px solid rgba(253,250,245,.9); box-shadow:0 10px 30px rgba(0,0,0,.35); animation: bob 6s ease-in-out infinite; }
    .f1 { left:6%; top:70px; animation-delay:0s; } .f2 { right:7%; top:110px; width:92px; height:92px; animation-delay:-2s; } .f3 { left:14%; bottom:70px; width:78px; height:78px; animation-delay:-4s; } .f4 { right:15%; bottom:60px; width:96px; height:96px; animation-delay:-1s; }
    @keyframes bob { 50% { transform: translateY(-14px) rotate(3deg); } }
    @media (max-width:760px) { .float { opacity:.28; } .f3,.f4 { display:none; } }
    .ticker { background:var(--terra); color:#fff; overflow:hidden; white-space:nowrap; position:relative; z-index:2; margin:0 -24px; }
    .ticker div { display:inline-block; padding:11px 0; animation: scroll 26s linear infinite; font-size:13px; letter-spacing:2px; text-transform:uppercase; font-weight:500; }
    .ticker i { font-style:normal; margin:0 18px; opacity:.7; }
    @keyframes scroll { to { transform: translateX(-50%); } }
    .home-wrap { max-width:960px; margin:0 auto; padding:34px 20px 56px; }
    .sec-head { display:flex; align-items:baseline; justify-content:space-between; margin:30px 0 14px; }
    .sec-head h2 { font-family:'Playfair Display',serif; font-size:26px; font-weight:600; }
    .sec-head a { color:var(--terra); font-size:14px; text-decoration:none; }
    .guides2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:18px; }
    .gcard { background:var(--white); border-radius:22px; overflow:hidden; text-decoration:none; color:var(--charcoal); box-shadow:0 4px 18px rgba(44,36,32,.08); transition:transform .25s, box-shadow .25s; display:block; }
    .gcard:hover { transform:translateY(-6px); box-shadow:0 14px 34px rgba(44,36,32,.16); }
    .gimgs { display:flex; height:190px; background:var(--blush); }
    .gimgs img { flex:1; min-width:0; object-fit:cover; transition:transform .5s; }
    .gcard:hover .gimgs img { transform:scale(1.07); }
    .gimgs .wrapi { flex:1; overflow:hidden; min-width:0; }
    .gbody { padding:18px 20px 20px; }
    .gpill { display:inline-block; font-size:11px; letter-spacing:2px; text-transform:uppercase; color:#fff; background:var(--sage); padding:4px 11px; border-radius:100px; margin-bottom:10px; }
    .gbody h3 { font-family:'Playfair Display',serif; font-size:21px; line-height:1.25; margin-bottom:8px; }
    .gbody p { font-size:14px; color:var(--wood); line-height:1.55; margin-bottom:12px; }
    .gmeta { font-size:12px; color:var(--sand); }
    .gmore { display:inline-block; color:var(--terra); font-weight:500; font-size:14px; transition:transform .2s; } .gcard:hover .gmore { transform:translateX(5px); }
    .strip { display:flex; gap:14px; overflow-x:auto; padding:4px 2px 16px; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; }
    .strip::-webkit-scrollbar { height:6px; } .strip::-webkit-scrollbar-thumb { background:var(--sand); border-radius:6px; }
    .fcard { flex:0 0 170px; scroll-snap-align:start; background:var(--white); border-radius:18px; overflow:hidden; text-decoration:none; color:var(--charcoal); box-shadow:0 3px 14px rgba(44,36,32,.07); transition:transform .25s; }
    .fcard:hover { transform:translateY(-5px) rotate(-1deg); }
    .fcard img { width:100%; height:170px; object-fit:cover; display:block; }
    .fcard div { padding:10px 12px 13px; font-size:13.5px; line-height:1.35; font-weight:500; }
    .fcard small { display:block; margin-top:3px; color:var(--terra); font-weight:400; font-size:12px; }
    .tiles { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:14px; }
    .tile { position:relative; border-radius:20px; overflow:hidden; aspect-ratio:4/3; text-decoration:none; color:#fff; display:block; box-shadow:0 4px 16px rgba(44,36,32,.12); }
    .tile img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transition:transform .5s; }
    .tile:hover img { transform:scale(1.1); }
    .tile::after { content:''; position:absolute; inset:0; background:linear-gradient(to top, rgba(44,36,32,.82) 0%, rgba(44,36,32,.05) 62%); }
    .tile b { position:absolute; left:14px; bottom:30px; z-index:2; font-family:'Playfair Display',serif; font-size:19px; font-weight:600; }
    .tile span { position:absolute; left:14px; bottom:11px; z-index:2; font-size:12px; opacity:.9; }
    @media (min-width:900px) { .tiles { grid-template-columns:repeat(4,1fr); } .tile:last-child { grid-column:span 2; aspect-ratio:auto; } }
    @media (max-width:899px) { .tiles { grid-template-columns:repeat(2,1fr); gap:10px; } .tile { aspect-ratio:1/1; } .tile b { font-size:16px; left:11px; bottom:27px; } .tile span { left:11px; } .tile:last-child { grid-column:span 2; aspect-ratio:2/1; } }
    .start-cta { background:linear-gradient(120deg,var(--butter),var(--blush)); border-radius:22px; padding:26px 24px; margin-top:34px; display:flex; flex-wrap:wrap; gap:14px; align-items:center; justify-content:space-between; }
    .start-cta p { font-size:16px; max-width:520px; line-height:1.5; }
    .start-cta a { background:var(--charcoal); color:var(--white); text-decoration:none; padding:13px 24px; border-radius:100px; font-weight:500; font-size:15px; transition:transform .2s, background .2s; }
    .start-cta a:hover { background:var(--terra); transform:scale(1.05); }
    .img-foot { font-size:12px; color:var(--sand); margin-top:10px; }
    .js .reveal { opacity:0; transform:translateY(22px); transition:opacity .7s ease, transform .7s ease; }
    .js .reveal.in { opacity:1; transform:none; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation:none !important; transition:none !important; } .js .reveal { opacity:1; transform:none; } html { scroll-behavior:auto; } }
    #search-results { display:none; }
    .results-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:16px; }
"""

def build():
    floats = "".join(f'<img class="float f{n+1}" src="{thumb(i,240,240)}" alt="" aria-hidden="true">' for n, i in enumerate(["command-variety-pack-19pc", "meohui-cat-wand-toys-2pack", "cisily-sink-caddy", "cosrx-snail-mucin"]))
    tick = "".join(f"<span>{t}</span><i>●</i>" for t in ["No drill", "No damage", "Deposit safe", "Under $25", "Renter approved picks", "Read, not tested"]) * 2
    gcards = ""
    for slug, t, d, meta, imgs in GUIDES:
        gi = "".join(f'<div class="wrapi"><img src="{thumb(i)}" alt="" loading="lazy"></div>' for i in imgs)
        gcards += f'<a class="gcard reveal" href="/guides/{slug}.html"><div class="gimgs">{gi}</div><div class="gbody"><span class="gpill">Renter guide</span><h3>{E(t)}</h3><p>{E(d)}</p><span class="gmeta">{meta}</span> &nbsp; <span class="gmore">Read the guide →</span></div></a>'
    fresh = "".join(f'<a class="fcard" href="/products/{i}.html"><img src="{thumb(i)}" alt="{E(t)}" loading="lazy"><div>{E(t)}<small>{b}</small></div></a>' for i, t, b in FRESH)
    tiles = "".join(f'<a class="tile reveal" href="/{u}"><img src="{thumb(i)}" alt="" loading="lazy"><b>{E(n)}</b><span>{E(s)}</span></a>' for u, n, s, i, _ in CATS)
    body = f'''<header class="hero">
  {floats}
  <div class="hero-inner">
    <div class="brand-tag">@NestandPaws</div>
    <h1>Nest <em>&amp;</em> Paws</h1>
    <p class="hero-sub">Renter-friendly picks, researched so you do not have to.</p>
    <div class="chips"><span>No drilling</span><span>No damage</span><span>No fuss</span></div>
    <div class="search-wrap">
      <input type="text" id="search-input" placeholder="Search finds: hooks, shelf, curtain..." autocomplete="off" aria-label="Search finds">
    </div>
  </div>
  <div class="ticker" aria-hidden="true"><div>{tick}</div></div>
</header>

<div class="home-wrap">
  <section id="search-results">
    <div class="sec-head"><h2>Search results</h2></div>
    <div class="results-grid" id="results-grid"></div>
  </section>

  <div id="home-sections">
    <div class="sec-head reveal"><h2>Latest guides</h2><a href="/guides/">All guides →</a></div>
    <div class="guides2">{gcards}</div>

    <div class="sec-head reveal"><h2>Fresh finds</h2><a href="/under25.html">Under $25 →</a></div>
    <div class="strip reveal">{fresh}</div>

    <div class="sec-head reveal"><h2>Browse by problem</h2></div>
    <div class="tiles">{tiles}</div>
    <p class="img-foot">Product images on this site are illustrations, not photos of the item.</p>

    <div class="start-cta reveal">
      <p><strong>New here?</strong> See how picks are chosen and what the deposit-safe score means. I read the listings so you do not have to.</p>
      <a href="/start-here.html">Start here →</a>
    </div>
  </div>
</div>
'''
    p = os.path.join(ROOT, "index.html"); s = open(p, encoding="utf-8").read()
    s = re.sub(r"(<link rel=\"stylesheet\" href=\"/shared.css\">\s*)<style>.*?</style>", lambda m: m.group(1) + "<style>" + CSS + "  </style>\n  <script>document.documentElement.classList.add('js')</script>", s, count=1, flags=re.S)
    s = re.sub(r"<body>.*?(<footer>)", lambda m: "<body>\n" + body + "\n" + m.group(1), s, count=1, flags=re.S)
    if "IntersectionObserver" not in s:
        s = s.replace("</body>", """<script>
  (function(){var els=document.querySelectorAll('.reveal');if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return;}
  var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}})},{threshold:.12});
  els.forEach(function(e,i){e.style.transitionDelay=((i%4)*70)+'ms';io.observe(e);});})();
</script>
</body>""")
    open(p, "w", encoding="utf-8").write(s)
    print("home rebuilt")
build()
