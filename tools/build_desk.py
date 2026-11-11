#!/usr/bin/env python3
"""Desk guide product builder (Nov 11, 2026). Reuses build_gifts.py helpers.
Appends products.js entries (only if id absent), writes product pages and category cards (only if missing).
Quntis is not added: the site already has quntis-monitor-light-bar. Idempotent."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_gifts as bg

DATE = "2026-11-11"
bg.DATE = DATE
bg.fmt_date = lambda iso=DATE: "Nov 11, 2026"
bg.CATLABEL = {"home": ("Home & Kitchen Finds", "home.html")}
GUIDE = "cozy-desk-setup-power-and-light-upgrades"

PICKS = [
 dict(id="anker-nano-smart-display-charger-45w", name="Anker Nano Smart Display Charger, 45W", cat="home", price=39.99, bracket="Under $50",
  subtitle="A slim 45W wall charger with a small display and a foldable plug",
  story="Anker's 45W Nano charger has a small display and a foldable plug. The Amazon listing shows 4.7 stars from more than 6,000 ratings on Nov 11, 2026. A gift idea for someone who wants one slim charger for a phone and a laptop.",
  con="The listing says smart recognition works with supported iPhones only. Best Buy sold the blue version on Nov 11, so check the color on the listing.",
  alt="Concept image of a small white and blue wall charger with a tiny display on a cream linen desk beside a mug and a succulent",
  tags=["Desk Setup", "Wall Charger", "Desk Gifts", "Gifts Under $50"],
  wtb=[("Amazon", "https://www.amazon.com/dp/B0G1MRLXMV"), ("Best Buy", "https://www.bestbuy.com/product/anker-nano-smart-display-usb-c-charger-block-45w-max-gan-phone-charger180-foldable-plug-blue/JJ858RSJYG")]),
 dict(id="mophie-3-in-1-travel-charger-magsafe", name="Mophie 3-in-1 Travel Charger with MagSafe", cat="home", price=49.99, bracket="Under $60",
  subtitle="A folding charging stand for a phone, a watch and earbuds",
  story="Mophie's folding charger holds a phone, an Apple Watch and earbuds in one stand. The listing says it includes a 30W adapter. A gift idea for someone who wants a tidy bedside or desk charging spot.",
  con="Some lower-rated Amazon reviews say it did not charge an Apple Watch reliably. The listing rating is 4.0 stars from 246 ratings on Nov 11, 2026.",
  alt="Concept image of a charcoal folding three-in-one wireless charging stand on a cream linen desk beside a mug",
  tags=["Desk Setup", "Wireless Charger", "Desk Gifts", "Gifts Under $100"],
  wtb=[("Amazon", "https://www.amazon.com/dp/B0CPQ618TQ"), ("Best Buy", "https://www.bestbuy.com/product/mophie-3-in-1-travel-charger-with-magsafe-for-apple-iphone-airpods-pro-airpods-and-apple-watch-black/J39Q4WZRXH")]),
 dict(id="benq-screenbar-halo-2", name="BenQ ScreenBar Halo 2", cat="home", price=199.00, bracket="Under $250",
  subtitle="A premium monitor light bar with a wireless controller",
  story="BenQ's Halo 2 is a monitor light bar with a wireless controller puck and two light sources. The Best Buy page says it fits monitors 0.17 to 2.36 inches thick, flat or curved. The Amazon listing shows 4.7 stars from more than 1,300 ratings on Nov 11, 2026.",
  con="Lower-rated reviews call it bulky, and one reviewer saw light reach their eyes even after aiming it away.",
  alt="Concept image of a wide dark monitor light bar with a small round controller puck on a cream linen desk",
  tags=["Desk Setup", "Monitor Light", "Desk Lighting", "Gifts Under $250"],
  wtb=[("Amazon", "https://www.amazon.com/dp/B0DK59YKRS"), ("Best Buy", "https://www.bestbuy.com/product/benq-screenbar-halo-2-monitor-light-bar-with-wireless-controller-dark-gray/C3F276JCF5")]),
 dict(id="lofree-flow-lite-100-keyboard", name="Lofree Flow Lite 100 Keyboard", cat="home", price=109.99, bracket="Under $150",
  subtitle="A low-profile keyboard with three connection modes",
  story="Lofree's Flow Lite 100 is a low-profile keyboard with 100 keys, a gasket mount, a volume roller and three connection modes. The Amazon listing shows 4.4 stars from more than 700 ratings on Nov 11, 2026.",
  con="Lower-rated reviews mention tight key spacing that causes typos, and one reports a slow wake-up from sleep.",
  alt="Concept image of a low-profile marble white keyboard on a cream linen desk beside a plant and a mug",
  tags=["Desk Setup", "Mechanical Keyboard", "Desk Gifts", "Gifts Under $150"],
  wtb=[("Amazon", "https://www.amazon.com/dp/B0DP33XH4X"), ("Lofree", "https://www.lofree.co/products/flow-lite100-mechanical-keyboard?country=US")]),
]
bg.PICKS = PICKS

def page(p):
    s = bg.product_page(p)
    s = s.replace("More gift ideas", "More desk picks").replace(
        'href="/guides/holiday-gift-ideas-2026.html">See the holiday gift guide →',
        f'href="/guides/{GUIDE}.html">See the cozy desk setup guide →')
    s = s.replace("Prices change, and holiday sales can change them again, so check each retailer.", "Prices change, so check each retailer.")
    return s

if __name__ == "__main__":
    print("products.js added:", bg.append_products())
    for p in PICKS:
        f = os.path.join(bg.ROOT, "products", p["id"] + ".html")
        if not os.path.exists(f):
            open(f, "w", encoding="utf-8").write(page(p))
    print("product pages:", len(PICKS))
    print("cards inserted:", bg.insert_cards())
