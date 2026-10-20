#!/usr/bin/env python3
"""Rebuild the home page body and its cropped product images. Idempotent."""
import os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcrop import cropped, ROOT
E = html.escape

def img(i, w=640, h=640): return cropped(i, "home", w, h)

CATS = [("renter.html", "Renter friendly", "No drilling, no damage", "command-picture-strips"),
        ("home.html", "Home and kitchen", "Storage, cleaning, tools", "cisily-sink-caddy"),
        ("under25.html", "Under $25", "Small fixes, small price", "bluestars-outlet-extender-night-light"),
        ("seasonal.html", "Seasonal", "Timely picks", "artoid-mode-fall-table-runner"),
        ("pets.html", "Pets", "Dogs and cats", "dog-cooling-mat"),
        ("beauty.html", "Beauty", "Hair and skin", "cosrx-snail-mucin"),
        ("fashion.html", "Fashion", "Fall outfit picks", "amazon-essentials-womens-cable-knit-sweater"),
        ("wedding.html", "Wedding table", "Decor and hosting", "ourholiday-acrylic-wedding-table-numbers")]
FRESH = [("korcci-suction-cup-hooks-12pack", "Clear suction cup hooks", "Under $10"),
         ("yasonic-adhesive-shower-caddy-2pack", "Adhesive shower caddy", "Under $10"),
         ("meohui-cat-wand-toys-2pack", "Cat feather wand toys", "Under $10"),
         ("duck-window-insulation-kit-10-windows", "Window insulation kit", "Under $20"),
         ("innqoo-candle-warmer-lamp", "Candle warmer lamp", "Under $20"),
         ("kitty-city-xl-cat-scratcher-pads-3pack", "XL cat scratcher pads", "Under $20"),
         ("lumigens-6-tier-pants-hangers", "6-tier pants hangers", "Under $15"),
         ("anua-pdrn-hyaluronic-acid-100-cream", "Hyaluronic acid cream", "Under $25")]
import json, glob
FEATURED = ["renter-winter-draft-fixes", "no-drill-hooks-for-renters", "indoor-cat-toys-and-scratchers", "simple-k-beauty-routine"]
def load_guides():
    gs = {}
    for f in glob.glob(os.path.join(ROOT, "tools", "guides", "*.json")):
        g = json.load(open(f, encoding="utf-8")); gs[g["slug"]] = g
    return [gs[k] for k in FEATURED if k in gs]

CSS = """
    :root { --sage:#5C7A5A; --blush:#F2D9C8; --butter:#F3E7C2; --s1:8px; --s2:12px; --s3:16px; --s4:24px; --s5:32px; --s6:48px; --s7:72px; --ease:cubic-bezier(.22,1,.36,1); }
    @media (prefers-reduced-motion:no-preference) { html { scroll-behavior:smooth; } }
    .hero { background: var(--charcoal); padding: 44px 24px 0; text-align: center; position: relative; overflow: hidden; }
    .hero::before { content:''; position:absolute; inset:-20%; background: radial-gradient(circle at 20% 30%, rgba(193,122,74,.34), transparent 45%), radial-gradient(circle at 80% 70%, rgba(92,122,90,.26), transparent 45%); animation: drift 16s ease-in-out infinite alternate; }
    @keyframes drift { to { transform: translate3d(3%,-3%,0) scale(1.08); } }
    .hero-inner { position:relative; z-index:2; max-width:640px; margin:0 auto; padding-bottom:var(--s5); }
    .brand-tag { display:inline-block; font-size:11px; font-weight:500; letter-spacing:3px; text-transform:uppercase; color:var(--terra); margin-bottom:14px; }
    .hero h1 { font-family:'Playfair Display',serif; font-size:clamp(36px,8vw,60px); font-weight:400; color:var(--white); line-height:1.1; margin-bottom:10px; }
    .hero h1 em { font-style:italic; color:var(--sand); }
    .hero-sub { font-size:17px; font-weight:300; color:var(--sand); margin-bottom:var(--s4); }
    .chips { display:flex; flex-wrap:wrap; gap:var(--s1); justify-content:center; margin-bottom:var(--s4); }
    .chips span { font-size:14px; color:var(--cream); background:rgba(245,237,214,.10); border:1px solid rgba(245,237,214,.22); padding:6px 14px; border-radius:100px; }
    .search-wrap { max-width:480px; margin:0 auto; }
    .search-wrap input { width:100%; padding:15px 22px; border-radius:100px; border:2px solid transparent; background:var(--white); color:var(--charcoal); font-family:'DM Sans',sans-serif; font-size:16px; outline:none; box-shadow:0 8px 28px rgba(0,0,0,.25); transition:border-color .2s; }
    .search-wrap input:focus-visible { border-color:var(--terra); }
    .float { position:absolute; z-index:1; width:84px; height:84px; animation: bob 7s ease-in-out infinite; }
    .float img { box-sizing:border-box; max-width:none; width:100%; height:100%; aspect-ratio:1/1; clip-path:circle(50%); border-radius:50%; object-fit:cover; border:4px solid rgba(253,250,245,.92); box-shadow:0 10px 30px rgba(0,0,0,.35); display:block; transition:transform 1.1s cubic-bezier(.3,.7,.2,1); }
    .float.big { z-index:3; } .float.big img { transform:scale(1.6); }
    .f1 { left:3%; top:11%; } .f2 { left:13%; top:25.5%; animation-delay:-1.4s; } .f3 { left:3%; top:40%; animation-delay:-3.1s; } .f4 { left:13%; top:54.5%; animation-delay:-4.6s; } .f5 { left:3%; top:69%; animation-delay:-2.2s; }
    .f6 { right:3%; top:11%; animation-delay:-5.3s; } .f7 { right:13%; top:25.5%; animation-delay:-0.7s; } .f8 { right:3%; top:40%; animation-delay:-3.9s; } .f9 { right:13%; top:54.5%; animation-delay:-6.1s; } .f10 { right:3%; top:69%; animation-delay:-2.8s; }
    .f2,.f7 { animation-duration:8.2s; } .f4,.f9 { animation-duration:6.4s; } .f5,.f8 { animation-duration:7.6s; }
    @media (max-width:1180px) { .f2,.f4,.f7,.f9 { display:none; } }
    @keyframes bob { 25% { transform: translate3d(5px,-9px,0); } 50% { transform: translate3d(0,-14px,0); } 75% { transform: translate3d(-5px,-7px,0); } }
    @media (max-width:760px) { .float { display:none; } }
    @media (prefers-reduced-motion:reduce) { .float { animation:none; } .float img { transition:none; } }
    .trust { position:relative; z-index:2; margin:0 -24px; border-top:1px solid rgba(245,237,214,.16); background:rgba(245,237,214,.06); }
    .trust div { max-width:1000px; margin:0 auto; padding:14px 20px; display:flex; flex-wrap:wrap; gap:6px 26px; justify-content:center; font-size:14px; color:var(--sand); }
    .trust span::before { content:''; display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--terra); margin-right:9px; vertical-align:middle; }
    .hero-inner > * { animation: rise .8s var(--ease) both; }
    .hero-inner > :nth-child(2) { animation-delay:.08s; } .hero-inner > :nth-child(3) { animation-delay:.16s; } .hero-inner > :nth-child(4) { animation-delay:.24s; } .hero-inner > :nth-child(5) { animation-delay:.32s; }
    @keyframes rise { from { opacity:0; transform:translateY(16px); } }
    .home-wrap { max-width:1000px; margin:0 auto; padding:var(--s6) 20px var(--s7); }
    .sec-head { display:flex; align-items:baseline; justify-content:space-between; gap:var(--s3); margin:var(--s7) 0 var(--s4); }
    .sec-head:first-child { margin-top:0; }
    .sec-head h2 { font-family:'Playfair Display',serif; font-size:clamp(24px,4vw,30px); font-weight:600; line-height:1.2; }
    .sec-head a { color:var(--terra); font-size:15px; text-decoration:underline; text-underline-offset:3px; }
    .guides2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr)); gap:var(--s5) var(--s4); }
    .gcard { text-decoration:none; color:var(--charcoal); display:block; }
    .gimg { border-radius:20px; overflow:hidden; aspect-ratio:16/9; background:var(--blush); }
    .gimg img { width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s var(--ease); }
    @media (hover:hover) and (pointer:fine) { .gcard:hover .gimg img { transform:scale(1.04); } .gcard:hover h3 { color:var(--terra); } .fcard:hover div { color:var(--terra); } .tile:hover img { transform:scale(1.06); } .start-cta a:hover { background:var(--terra); } }
    .gbody { padding:var(--s3) 2px 0; }
    .gmeta { font-size:14px; color:var(--wood); margin-bottom:6px; }
    .gmeta b { color:var(--sage); font-weight:500; }
    .gbody h3 { font-family:'Playfair Display',serif; font-size:clamp(22px,3.4vw,26px); line-height:1.25; margin-bottom:var(--s1); }
    .gbody p { font-size:16px; color:var(--wood); line-height:1.6; max-width:60ch; }
    .strip { display:flex; gap:var(--s3); overflow-x:auto; padding:0 2px var(--s3); scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; }
    .strip::-webkit-scrollbar { height:6px; } .strip::-webkit-scrollbar-thumb { background:var(--sand); border-radius:6px; }
    .fcard { flex:0 0 190px; scroll-snap-align:start; text-decoration:none; color:var(--charcoal); }
    .fcard img { width:100%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:16px; background:var(--blush); }
    .fcard div { padding:10px 2px 0; font-size:15px; line-height:1.35; font-weight:500; }
    .fcard small { display:block; margin-top:2px; color:var(--wood); font-weight:400; font-size:14px; }
    .tiles { display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:var(--s3); }
    .tile { position:relative; border-radius:20px; overflow:hidden; aspect-ratio:4/3; text-decoration:none; color:#fff; display:block; }
    .tile img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transition:transform .6s var(--ease); }
    .tile:last-child img { object-position:50% 22%; }
    .tile::after { content:''; position:absolute; inset:0; background:linear-gradient(to top, rgba(44,36,32,.8) 0%, rgba(44,36,32,0) 60%); }
    .tile b { position:absolute; left:14px; bottom:32px; z-index:2; font-family:'Playfair Display',serif; font-size:20px; font-weight:600; }
    .tile span { position:absolute; left:14px; bottom:12px; z-index:2; font-size:14px; }
    @media (min-width:900px) { .tiles { grid-template-columns:repeat(4,1fr); } .tile:last-child { grid-column:span 2; aspect-ratio:auto; } }
    @media (max-width:899px) { .tiles { grid-template-columns:repeat(2,1fr); gap:var(--s2); } .tile { aspect-ratio:1/1; } .tile b { font-size:17px; left:12px; bottom:30px; } .tile span { left:12px; } .tile:last-child { grid-column:span 2; aspect-ratio:2/1; } }
    .start-cta { background:var(--butter); border-radius:22px; padding:var(--s5) var(--s4); margin-top:var(--s7); display:flex; flex-wrap:wrap; gap:var(--s3); align-items:center; justify-content:space-between; }
    .start-cta p { font-size:17px; max-width:52ch; line-height:1.55; }
    .start-cta a { min-height:48px; display:inline-flex; align-items:center; background:var(--charcoal); color:var(--white); text-decoration:none; padding:13px 26px; border-radius:100px; font-weight:500; font-size:16px; transition:background .2s; }
        .img-foot { font-size:14px; color:var(--wood); margin-top:var(--s2); }
        #search-results { display:none; }
    .results-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:var(--s3); }
"""

def build():
    floats = "".join(f'<span class="float f{n+1}" aria-hidden="true"><img src="{img(i,260,260)}" alt=""></span>' for n, i in enumerate(["korcci-suction-cup-hooks-12pack", "meohui-cat-wand-toys-2pack", "cisily-sink-caddy", "cosrx-snail-mucin", "kitty-city-xl-cat-scratcher-pads-3pack", "innqoo-candle-warmer-lamp", "dog-cooling-mat", "lumigens-6-tier-pants-hangers", "anua-pdrn-hyaluronic-acid-100-cream", "yasonic-adhesive-shower-caddy-2pack"]))
    tick = "".join(f"<span>{t}</span>" for t in ["Independent", "Researched from listings", "Checked Oct 2026"])
    gcards = "".join(f'<a class="gcard reveal" href="/guides/{g["slug"]}.html"><div class="gimg"><img src="/images/guides/hero/{g["slug"]}.jpg" alt="" width="1376" height="768" loading="lazy"></div><div class="gbody"><p class="gmeta"><b>{E(g["problem_tag"])} guide</b>, {len(g["picks"])} picks</p><h3>{E(g["title"])}</h3><p>{E(g["dek"])}</p></div></a>' for g in load_guides())
    fresh = "".join(f'<a class="fcard" href="/products/{i}.html"><img src="{img(i,420,420)}" alt="{E(t)}" loading="lazy"><div>{E(t)}<small>{b}</small></div></a>' for i, t, b in FRESH)
    tiles = "".join(f'<a class="tile" href="/{u}"><img src="{img(i,720,540)}" alt="" loading="lazy"><b>{E(n)}</b><span>{E(s)}</span></a>' for u, n, s, i in CATS)
    body = f'''<header class="hero">
  {floats}
  <script>
  (function(){{
    var f=[].slice.call(document.querySelectorAll('.float'));
    if(!f.length||window.matchMedia('(prefers-reduced-motion: reduce)').matches||window.innerWidth<761) return;
    function vis(a){{return a.filter(function(e){{return e.offsetParent!==null;}});}}
    function shuffle(a){{for(var i=a.length-1;i>0;i--){{var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t;}}return a;}}
    var queue=[],prev=null;
    function next(){{
      if(document.hidden){{setTimeout(next,1500);return;}}
      if(!queue.length){{queue=shuffle(vis(f));if(queue.length>1&&queue[0]===prev){{queue.push(queue.shift());}}}}
      var el=queue.shift(); if(!el){{setTimeout(next,1500);return;}}
      prev=el; el.classList.add('big');
      setTimeout(function(){{el.classList.remove('big'); setTimeout(next,700+Math.random()*900);}},2600);
    }}
    setTimeout(next,1200);
  }})();
  </script>
  <div class="hero-inner">
    <div class="brand-tag">@NestandPaws</div>
    <h1>Nest <em>&amp;</em> Paws</h1>
    <p class="hero-sub">Home, pet and beauty picks, researched so you do not have to.</p>
    <div class="chips"><span>Renter fixes</span><span>Home &amp; Kitchen</span><span>Pets</span><span>Beauty</span></div>
    <div class="search-wrap">
      <input type="text" id="search-input" placeholder="Search picks: hooks, scratcher, serum..." autocomplete="off" aria-label="Search finds">
    </div>
  </div>
  <div class="trust"><div>{tick}</div></div>
</header>

<div class="home-wrap">
  <section id="search-results">
    <div class="sec-head"><h2>Search results</h2></div>
    <div class="results-grid" id="results-grid"></div>
  </section>

  <div id="home-sections">
    <div class="sec-head"><h2>Latest guides</h2><a href="/guides/">All guides</a></div>
    <div class="guides2">{gcards}</div>

    <div class="sec-head"><h2>Fresh finds</h2><a href="/under25.html">Everything under $25</a></div>
    <div class="strip">{fresh}</div>

    <div class="sec-head"><h2>Browse by problem</h2></div>
    <div class="tiles">{tiles}</div>
    <p class="img-foot">Product images on this site are illustrations, not photos of the item.</p>

    <div class="start-cta">
      <p><strong>New here?</strong> See how picks are chosen and what the deposit-safe score means.</p>
      <a href="/start-here.html">Start here</a>
    </div>
  </div>
</div>
'''
    p = os.path.join(ROOT, "index.html"); s = open(p, encoding="utf-8").read()
    s = re.sub(r"(<link rel=\"stylesheet\" href=\"/shared.css(?:\?v=\d+)?\">\s*)<style>.*?</style>(\s*<script>document.documentElement.classList.add\('js'\)</script>)?", lambda m: m.group(1) + "<style>" + CSS + "  </style>", s, count=1, flags=re.S)
    s = re.sub(r"<body>.*?(<footer[\s>])", lambda m: "<body>\n" + body + "\n" + m.group(1), s, count=1, flags=re.S)
    s = re.sub(r"<script>\s*\(function\(\)\{var els=document.querySelectorAll\('.reveal'\).*?</script>\n", "", s, flags=re.S)
    open(p, "w", encoding="utf-8").write(s); print("home rebuilt")
build()
