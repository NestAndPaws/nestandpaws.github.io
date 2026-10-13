"""One-time: apply neutral copy + cropped images to products.js, product pages, category cards."""
import re, json, html, sys, os
sys.path.insert(0,'/tmp/claude-0/copy')
import b1,b2,b3
A={**b1.C,**b2.C,**b3.C}
ST={i:s for i,s in json.load(open('/tmp/claude-0/stems.json'))}
def stem(i): return ST[i]
def meta_desc(sub,story):
    t=sub.rstrip('.')+'. '+story
    if len(t)<=158: return t
    cut=t[:158]; k=cut.rfind('. ')
    return cut[:k+1] if k>80 else cut[:cut.rfind(' ')]+'…'
E=lambda s: html.escape(s,quote=True)
STR=r'"(?:[^"\\]|\\.)*"'
# products.js
js=open('products.js').read()
def fix_entry(m):
    blk=m.group(0); pid=re.search(r'id:\s*"([^"]+)"',blk).group(1)
    if pid not in A: return blk
    sub,story=A[pid]
    blk=re.sub(r'(subtitle:\s*)'+STR,lambda x:x.group(1)+json.dumps(sub),blk,1)
    blk=re.sub(r'(story:\s*)'+STR,lambda x:x.group(1)+json.dumps(story),blk,1)
    blk=re.sub(r'(image:\s*)'+STR,lambda x:x.group(1)+json.dumps(f"images/web/{stem(pid)}.jpg"),blk,1)
    return blk
js2=re.sub(r'\{\s*\n\s*id:\s*"[^"]+".*?\n  \}',fix_entry,js,flags=re.S)
open('products.js','w').write(js2)
# product pages
n=0
for pid,(sub,story) in A.items():
    f=f'products/{pid}.html'
    if not os.path.exists(f): print('missing',f); continue
    h=open(f).read(); st=stem(pid); img=f'https://nestandpaws.github.io/images/web/{st}.jpg'
    md=meta_desc(sub,story)
    h=re.sub(r'(<meta name="description" content=")[^"]*(")',lambda m:m.group(1)+E(md)+m.group(2),h,1)
    h=re.sub(r'(<meta property="og:description" content=")[^"]*(")',lambda m:m.group(1)+E(md)+m.group(2),h,1)
    h=re.sub(r'("description": )'+STR,lambda m:m.group(1)+json.dumps(sub.rstrip('.')+'. '+story.split('. ')[0].rstrip('.')+'.'),h,1)
    h=re.sub(r'("image": )"https://nestandpaws.github.io/images/[^"]+"',lambda m:m.group(1)+json.dumps(img),h)
    h=re.sub(r'(<meta property="og:image" content=")[^"]*(")',lambda m:m.group(1)+img+m.group(2),h)
    h=re.sub(r'(<div class="product-img">\s*<img src=")[^"]*(")',lambda m:m.group(1)+img+m.group(2),h)
    h=re.sub(r'(<p class="product-subtitle">).*?(</p>)',lambda m:m.group(1)+E(sub)+m.group(2),h,1,flags=re.S)
    h=re.sub(r'(<p class="product-story">).*?(</p>)',lambda m:m.group(1)+E(story)+m.group(2),h,1,flags=re.S)
    h=h.replace('Shop on Amazon →','Check price on Amazon')
    open(f,'w').write(h); n+=1
print('pages',n)
# category + home cards
for f in ['home','renter','pets','beauty','under25','seasonal','wedding','index']:
    p=f+'.html'; h=open(p).read(); c=0
    def card(m):
        global c
        blk=m.group(0); pid=m.group(1)
        if pid not in A: return blk
        sub,_=A[pid]; c+=1
        blk=re.sub(r'(<div class="card-subtitle">).*?(</div>)',lambda x:x.group(1)+E(sub)+x.group(2),blk,1,flags=re.S)
        blk=re.sub(r'(<div class="card-img">\s*<img src=")[^"]*(")',lambda x:x.group(1)+f'images/web/{stem(pid)}.jpg'+x.group(2),blk,1)
        blk=blk.replace('Shop on Amazon →','See the pick')
        return blk
    h=re.sub(r'<a href="products/([^"]+)\.html" class="product-card">.*?</a>',card,h,flags=re.S)
    h=h.replace('Shop on Amazon →','See the pick')
    open(p,'w').write(h); print(p,c)
