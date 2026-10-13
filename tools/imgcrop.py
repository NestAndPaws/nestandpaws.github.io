"""Crop pin art down to the product scene (drops text strips, price pills, title cards). Boxes live in tools/crops.json as fractions [x0,y0,x1,y1]."""
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROPS = json.load(open(os.path.join(ROOT, "tools", "crops.json")))

def cropped(img_id, out_dir, maxw=720, maxh=720, quality=82):
    """Write images/{out_dir}/{id}.jpg from the PNG, cropped. Returns the site path."""
    out = os.path.join(ROOT, "images", out_dir); os.makedirs(out, exist_ok=True)
    im = Image.open(os.path.join(ROOT, "images", img_id + ".png")).convert("RGB")
    x0, y0, x1, y1 = CROPS.get(img_id, [0, 0, 1, 1]); w, h = im.size
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    im.thumbnail((maxw, maxh)); im.save(os.path.join(out, img_id + ".jpg"), "JPEG", quality=quality, optimize=True)
    return f"/images/{out_dir}/{img_id}.jpg"
