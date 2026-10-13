#!/usr/bin/env python3
"""Oct 13 2026: strip dead Associates tag, normalize Amazon links to /dp/ASIN, neutral disclosure text."""
import re, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMZ = re.compile(r'https://www\.amazon\.com/[^"\'\s<>]*?dp/([A-Z0-9]{10})[^"\'\s<>]*')
subs = [
 (re.compile(r'<p class="disclosure">Affiliate link\s*—\s*I earn a small commission at no extra cost to you</p>'),
  '<p class="disclosure">Links go to Amazon. Prices change, so check the listing.</p>'),
 (re.compile(r'This page contains affiliate links\. I earn a small commission at no extra cost to you\.'),
  'Links go to Amazon. Prices change, so check the listing.'),
]
files = [f for f in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True)
         if f.endswith((".html", ".js", ".txt")) and "/tools/" not in f and "/guides/" not in f]
changed = 0
for f in files:
    s = open(f, encoding="utf-8").read(); o = s
    s = AMZ.sub(lambda m: f"https://www.amazon.com/dp/{m.group(1)}", s)
    for rx, rep in subs: s = rx.sub(rep, s)
    if s != o:
        open(f, "w", encoding="utf-8").write(s); changed += 1
print("changed", changed)
