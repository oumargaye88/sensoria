#!/usr/bin/env python3
"""
Sensoria static site generator — Home -> Collections -> Products.

Reads data/products.json (single source of truth) and generates:
  1. index.html        — landing page: hero, story, quiz, "4 gammes" overview, featured picks
  2. collections/*.html — one page per gamme (eaux-de-parfum, huiles-precieuses, huiles-a-bruler, rituel-hammam)
  3. produits/*.html     — one presentation page per product (31 pages)

Run after editing data/products.json:
    python3 generate.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "products.json")
INDEX_PATH = os.path.join(ROOT, "index.html")
PRODUITS_DIR = os.path.join(ROOT, "produits")
COLLECTIONS_DIR = os.path.join(ROOT, "collections")
WA_NUMBER = "221781537491"

HEART_SVG = '<svg viewBox="0 0 24 24" fill="none"><path d="M12 20s-7.2-4.6-9.5-9.1C.8 7.6 2.4 4.5 5.6 4c2-.3 3.6.6 4.9 2.3.4.5.7.9 1.5.9s1.1-.4 1.5-.9C14.8 4.6 16.4 3.7 18.4 4c3.2.5 4.8 3.6 3.1 6.9C19.2 15.4 12 20 12 20Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>'
WA_SVG = '<svg viewBox="0 0 32 32" fill="currentColor"><path d="M16.04 3C9.37 3 3.96 8.4 3.96 15.06c0 2.24.62 4.4 1.79 6.3L3 29l7.82-2.71a12.9 12.9 0 0 0 5.22 1.1h.01c6.66 0 12.07-5.4 12.07-12.06C28.12 8.4 22.71 3 16.04 3Zm0 21.98h-.01a10 10 0 0 1-5.1-1.4l-.37-.22-4.64 1.6 1.55-4.52-.24-.38a9.9 9.9 0 0 1-1.53-5.3c0-5.48 4.46-9.94 9.95-9.94 2.66 0 5.15 1.03 7.03 2.92a9.88 9.88 0 0 1 2.91 7.03c0 5.48-4.46 9.94-9.95 9.94Zm5.46-7.44c-.3-.15-1.77-.87-2.04-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.25-.46-2.38-1.47-.88-.78-1.47-1.75-1.65-2.05-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.6-.91-2.2-.24-.58-.49-.5-.67-.5-.17 0-.37-.02-.57-.02-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.47 0 1.46 1.06 2.87 1.21 3.07.15.2 2.09 3.2 5.07 4.48.71.31 1.26.49 1.69.63.71.22 1.35.19 1.86.12.57-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35Z"/></svg>'
CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

COLLECTION_LABELS = {
    "eaux-de-parfum": "Eaux de Parfum",
    "huiles-precieuses": "Huiles Précieuses",
    "huiles-a-bruler": "Huiles & Diffuseurs",
    "rituel-hammam": "Rituel Hammam",
}


def fmt_price(n):
    return f"{int(n):,}".replace(",", " ")


def wa_link(message):
    from urllib.parse import quote
    return f"https://wa.me/{WA_NUMBER}?text={quote(message)}"


def e(s):
    return html.escape(str(s), quote=True)


# ------------------------------------------------------------- PAGE PATHS --
def paths_for(page_type):
    """page_type in {'home','collection','product'} -> dict of path helpers."""
    if page_type == "home":
        return dict(
            base="", top_href="#top", idx_page="index.html",
            col=lambda slug: f"collections/{slug}.html",
            prod=lambda slug: f"produits/{slug}.html",
            quiz="#quiz",
        )
    elif page_type == "collection":
        return dict(
            base="../", top_href="../index.html", idx_page="../index.html",
            col=lambda slug: f"{slug}.html",
            prod=lambda slug: f"../produits/{slug}.html",
            quiz="../index.html#quiz",
        )
    else:  # product
        return dict(
            base="../", top_href="../index.html", idx_page="../index.html",
            col=lambda slug: f"../collections/{slug}.html",
            prod=lambda slug: f"{slug}.html",
            quiz="../index.html#quiz",
        )


# ---------------------------------------------------------------- CARDS ----
def render_card(item, kind, base=""):
    """base = '' on homepage, '../' on collection/product pages."""
    slug = item["slug"]
    img = base + item["img"]
    img_canonical = item["img"]
    url = f"{base}produits/{slug}.html"

    if kind == "parfum":
        cart_name = f"{item['name']} — Eau de Parfum {item['size']}"
        top_label = item["family"]
        subtitle = item["en"]
        price_html = f"{fmt_price(item['price'])} F CFA"
    elif kind == "huile":
        cart_name = f"Huile Précieuse {item['name']} — 50 ml"
        top_label = "Huile Précieuse"
        subtitle = item["en"]
        price_html = f"{fmt_price(item['price'])} F CFA"
    elif kind == "bruler":
        cart_name = f"Huile à Brûler {item['name']} — 50 ml"
        top_label = item["family"]
        subtitle = ""
        price_html = f"{fmt_price(item['price'])} F CFA"
    elif kind == "hammam":
        cart_name = item["name"]
        top_label = item.get("categoryLabel", "").replace("Rituel Hammam · ", "")
        subtitle = item["en"]
        price_html = item.get("priceLabel") or f"{fmt_price(item['price'])} F CFA"
    else:
        cart_name = item["name"]
        top_label = ""
        subtitle = ""
        price_html = ""

    subtitle_html = f'<p class="card-en">{e(subtitle)}</p>' if subtitle else ""
    desc = item.get("desc", "")

    return f'''<div class="card reveal">
  <button class="wish-btn" aria-label="Ajouter à ma sélection" data-wish data-name="{e(cart_name)}" data-price="{item.get('price',0)}" data-price-label="{e(item.get('priceLabel',''))}" data-img="{e(img_canonical)}">{HEART_SVG}</button>
  <a href="{url}" class="card-link">
    <div class="card-media"><img src="{e(img)}" alt="Sensoria {e(item['name'])}" loading="lazy"></div>
    <p class="card-fam">{e(top_label)}</p>
    <h3>{e(item['name'])}</h3>
    {subtitle_html}
  </a>
  <p class="desc">{e(desc)}</p>
  <div class="price-row">
    <span class="price">{price_html}</span>
    <div class="card-actions">
      <a class="btn btn-outline btn-sm" href="{url}">Voir</a>
      <button class="btn btn-primary btn-sm" data-order data-name="{e(cart_name)}" data-price="{item.get('price',0)}" data-price-label="{e(item.get('priceLabel',''))}">Commander</button>
    </div>
  </div>
</div>'''


# ------------------------------------------------------------ SHARED HTML --
def header_html(page_type, active_collection=""):
    p = paths_for(page_type)
    home_href = "#top" if page_type == "home" else p["idx_page"]

    def navlink(slug, label):
        cls = ' class="active"' if slug == active_collection else ""
        return f'<a href="{p["col"](slug)}"{cls}>{label}</a>'

    return f'''<header class="site-header" id="top">
  <div class="header-inner">
    <a href="{home_href}" class="brand">
      <img src="{p['base']}assets/logo.png" alt="Sensoria" class="brand-logo">
      <span class="brand-name">Sensoria</span>
    </a>
    <nav class="main-nav" id="mainNav">
      {navlink('eaux-de-parfum', 'Eaux de Parfum')}
      {navlink('huiles-precieuses', 'Huiles Précieuses')}
      {navlink('huiles-a-bruler', 'Huiles &amp; Diffuseurs')}
      {navlink('rituel-hammam', 'Rituel Hammam')}
      <a href="{p['quiz']}">Mon Rituel</a>
    </nav>
    <div class="header-actions">
      <button class="icon-btn" id="cartToggle" aria-label="Ma sélection">
        <svg viewBox="0 0 24 24" fill="none"><path d="M6 8h12l-1.2 10.2a2 2 0 0 1-2 1.8H9.2a2 2 0 0 1-2-1.8L6 8Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M9 8V6a3 3 0 0 1 6 0v2" stroke="currentColor" stroke-width="1.6"/></svg>
        <span class="cart-badge" id="cartBadge">0</span>
      </button>
      <button class="hamburger" id="hamburger" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>'''


def footer_html(base):
    return f'''<footer class="site-footer" id="contact">
  <div class="footer-inner">
    <div class="footer-brand">
      <img src="{base}assets/logo.png" alt="Sensoria">
      <p>Sensoriarituals — le soin comme rituel.<br>Fragrances, precious oils, burning oils and hammam care.</p>
    </div>
    <div class="footer-col">
      <h4>Où nous trouver</h4>
      <p>🇸🇳 Sénégal — Centre commercial Casino Sahm<br>Centre commercial Sea Plazza</p>
      <p>🇲🇦 Également au Maroc — détails sur demande</p>
      <p class="soon">Boutique en ligne : ouverture prochaine</p>
    </div>
    <div class="footer-col">
      <h4>Commandes</h4>
      <p><a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener" class="footer-link">WhatsApp · +221 78 153 74 91</a></p>
      <p><a href="https://instagram.com/sensoriarituals" target="_blank" rel="noopener" class="footer-link">@Sensoriarituals</a></p>
      <p class="muted">Instagram · TikTok · Snapchat · Facebook</p>
    </div>
  </div>
  <div class="footer-bottom">© Sensoria — Sensoriarituals. Tous droits réservés.</div>
</footer>'''


def cart_and_float_html():
    return f'''<div class="cart-panel" id="cartPanel">
  <div class="cart-panel-head">
    <h3>Ma sélection</h3>
    <button id="cartClose" aria-label="Fermer">&times;</button>
  </div>
  <div class="cart-items" id="cartItems">
    <p class="cart-empty">Votre sélection est vide.<br>Ajoutez des produits pour commander en une fois.</p>
  </div>
  <div class="cart-footer">
    <div class="cart-total"><span>Total estimé</span><strong id="cartTotal">0 F CFA</strong></div>
    <a class="btn btn-primary btn-block" id="cartCheckout" href="#" target="_blank" rel="noopener">Commander via WhatsApp</a>
  </div>
</div>
<div class="cart-overlay" id="cartOverlay"></div>
<a href="{wa_link('Bonjour Sensoria 🌸 je souhaite avoir des renseignements sur votre collection.')}" target="_blank" rel="noopener" class="wa-float" aria-label="Contacter sur WhatsApp">{WA_SVG}</a>'''


def page_shell(title, description, page_type, body, active_collection=""):
    p = paths_for(page_type)
    base = p["base"]
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="icon" href="{base}assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700;9..144,900&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<div class="bg-pattern" aria-hidden="true"></div>
{header_html(page_type, active_collection)}
{body}
{footer_html(base)}
{cart_and_float_html()}
<script src="{base}script.js"></script>
</body>
</html>
'''


def meta_rows(rows):
    out = '<div class="product-meta">'
    for label, val in rows:
        if not val:
            continue
        out += f'<div><dt>{e(label)}</dt><dd>{e(val)}</dd></div>'
    out += '</div>'
    return out


def trust_row():
    items = ["Fait main, Sénégal &amp; Maroc", "Livraison main à main · Dakar", "Réponse rapide sur WhatsApp"]
    return '<div class="trust-row">' + "".join(
        f'<div class="trust-item">{CHECK_SVG}<span>{t}</span></div>' for t in items
    ) + '</div>'


def breadcrumb(page_type, cat_label, cat_slug, name):
    p = paths_for(page_type)
    cat_label = cat_label or COLLECTION_LABELS.get(cat_slug, "")
    return f'''<nav class="breadcrumb">
  <a href="{p['idx_page']}">Accueil</a><span class="sep">/</span>
  <a href="{p['col'](cat_slug)}">{e(cat_label)}</a><span class="sep">/</span>
  <span class="current">{e(name)}</span>
</nav>'''


def related_section(items, kind, base, exclude_slug):
    pool = [it for it in items if it["slug"] != exclude_slug][:3]
    if not pool:
        return ""
    cards = "\n".join(render_card(it, kind, base) for it in pool)
    return f'''<section class="related">
  <div class="related-head"><p class="eyebrow">Vous aimerez aussi</p><h2>Complétez votre rituel</h2></div>
  <div class="product-grid">{cards}</div>
</section>'''


def cross_links(current_slug, base):
    items = [(s, l) for s, l in COLLECTION_LABELS.items() if s != current_slug]
    links = "".join(f'<a href="{base}collections/{s}.html">{l}</a>' for s, l in items)
    return f'''<section class="gamme-crosslinks">
  <div class="gamme-crosslinks-inner">
    <p>Découvrez aussi :</p>
    {links}
  </div>
</section>'''


def diffuser_swatch_button(color, base, active=False):
    hexmap = {
        "Bleu": "#2447ad", "Turquoise": "#1f8f7c", "Rouge": "#a02334", "Rose": "#f0a9ad",
        "Blanc": "#ffffff", "Beige": "#e7c9a1", "Bleu ciel": "#bfe1e6",
    }
    light = ' swatch-light' if color["name"] == "Blanc" else ""
    active_cls = " active" if active else ""
    return (f'<button class="swatch{light}{active_cls}" style="background:{hexmap.get(color["name"], "#ccc")}" '
            f'data-value="{e(color["name"])}" data-img="{base}{e(color["img"])}" data-img-canonical="{e(color["img"])}" '
            f'title="{e(color["name"])}"></button>')


# --------------------------------------------------------- PRODUCT PAGES ---
def simple_product_page(item, kind, all_items, out_path, cat_slug, cart_name, price_html_override=None):
    name = item["name"]
    price_html = price_html_override or f"{fmt_price(item['price'])} F CFA"

    rows = []
    if item.get("family"):
        rows.append(("Famille", item["family"]))
    if item.get("size"):
        rows.append(("Contenance", item["size"]))
    if item.get("wear"):
        rows.append(("À porter", item["wear"]))
    rows.append(("Catégorie", item.get("categoryLabel", "")))

    conseil_html = ""
    if item.get("conseil"):
        conseil_html = f'<div class="conseil-box"><strong>Conseil d\'utilisation</strong><p>{e(item["conseil"])}</p></div>'

    en_html = f'<p class="p-en">{e(item["en"])}</p>' if item.get("en") else ""
    base = "../"

    body = f'''{breadcrumb("product", item.get("categoryLabel",""), cat_slug, name)}
<section class="product-hero">
  <div class="studio-frame">
    <span class="studio-badge">Sensoria</span>
    <img class="studio-img" src="{base}{item['img']}" alt="Sensoria {e(name)}">
    <img class="studio-reflection" src="{base}{item['img']}" alt="" aria-hidden="true">
  </div>
  <div class="product-info">
    <p class="eyebrow p-cat">{e(item.get("categoryLabel",""))}</p>
    <h1>{e(name)}</h1>
    {en_html}
    <p class="p-price">{price_html}</p>
    <p class="p-desc">{e(item.get("desc",""))}</p>
    {meta_rows(rows)}
    {conseil_html}
    <div class="product-actions">
      <button class="btn btn-primary" data-add-cart data-name="{e(cart_name)}" data-price="{item.get('price',0)}" data-price-label="{e(item.get('priceLabel',''))}" data-img="{e(item['img'])}">Ajouter à ma sélection</button>
      <button class="btn btn-outline" data-order data-name="{e(cart_name)}" data-price="{item.get('price',0)}" data-price-label="{e(item.get('priceLabel',''))}">Commander sur WhatsApp</button>
    </div>
    {trust_row()}
  </div>
</section>
{related_section(all_items, kind, base, item["slug"])}'''

    html_out = page_shell(f"{name} — Sensoria", item.get("desc", "")[:155], "product", body, cat_slug)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)


def build_product_pages(data):
    count = 0
    for p in data["parfums"]:
        cart_name = f"{p['name']} — Eau de Parfum {p['size']}"
        simple_product_page(p, "parfum", data["parfums"], os.path.join(PRODUITS_DIR, f"{p['slug']}.html"), "eaux-de-parfum", cart_name)
        count += 1

    for h in data["huiles"]:
        cart_name = f"Huile Précieuse {h['name']} — 50 ml"
        simple_product_page(h, "huile", data["huiles"], os.path.join(PRODUITS_DIR, f"{h['slug']}.html"), "huiles-precieuses", cart_name)
        count += 1

    for b in data["bruler"]:
        cart_name = f"Huile à Brûler {b['name']} — 50 ml"
        simple_product_page(b, "bruler", data["bruler"], os.path.join(PRODUITS_DIR, f"{b['slug']}.html"), "huiles-a-bruler", cart_name)
        count += 1

    for hm in data["hammam"]:
        if hm["slug"] == "gel-nettoyant":
            continue
        cart_name = hm["name"]
        simple_product_page(hm, "hammam", data["hammam"], os.path.join(PRODUITS_DIR, f"{hm['slug']}.html"), "rituel-hammam", cart_name,
                             price_html_override=hm.get("priceLabel") or None)
        count += 1

    base = "../"

    # ---- grand format (price on request) ----
    gf = data["grandFormat"]
    comp_tags = "".join(f'<span>{e(c)}</span>' for c in gf.get("composition", []))
    body = f'''{breadcrumb("product", gf["categoryLabel"], "huiles-precieuses", gf["name"])}
<section class="product-hero">
  <div class="studio-frame">
    <span class="studio-badge">Sensoria</span>
    <img class="studio-img" src="{base}{gf['img']}" alt="Sensoria {e(gf['name'])}">
    <img class="studio-reflection" src="{base}{gf['img']}" alt="" aria-hidden="true">
  </div>
  <div class="product-info">
    <p class="eyebrow p-cat">{e(gf["categoryLabel"])}</p>
    <h1>{e(gf["name"])}</h1>
    <p class="p-en">{e(gf["en"])}</p>
    <p class="p-price">Prix sur demande <small>· réponse rapide sur WhatsApp</small></p>
    <p class="p-desc">{e(gf["desc"])}</p>
    {meta_rows([("Contenance", gf["size"]), ("Catégorie", gf["categoryLabel"])])}
    <div class="tag-row">{comp_tags}</div>
    <div class="product-actions">
      <button class="btn btn-primary" data-order-info data-name="{e(gf['name'])}">Demander le prix sur WhatsApp</button>
    </div>
    {trust_row()}
  </div>
</section>
{related_section(data["huiles"], "huile", base, "__none__")}'''
    with open(os.path.join(PRODUITS_DIR, f"{gf['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(page_shell(f"{gf['name']} — Sensoria", gf["desc"][:155], "product", body, "huiles-precieuses"))
    count += 1

    # ---- diffuseur (variant page) ----
    dif = data["diffuseur"]
    swatches_html = "\n        ".join(diffuser_swatch_button(c, base, active=(c["name"] == "Bleu")) for c in dif["colors"])
    body = f'''{breadcrumb("product", dif["categoryLabel"], "huiles-a-bruler", dif["name"])}
<section class="product-hero">
  <div class="studio-frame">
    <span class="studio-badge">Sensoria</span>
    <img class="studio-img" id="diffuserPageImg" src="{base}{dif['colors'][0]['img']}" alt="Sensoria {e(dif['name'])}">
  </div>
  <div class="product-info">
    <p class="eyebrow p-cat">{e(dif["categoryLabel"])}</p>
    <h1>{e(dif["name"])}</h1>
    <p class="p-en">{e(dif["en"])}</p>
    <p class="p-price">{fmt_price(dif['price'])} F CFA</p>
    <p class="p-desc">{e(dif["desc"])}</p>
    <div class="variant-picker">
      <p class="swatch-label">Coloris — <span id="diffuserPageColorName">Bleu</span></p>
      <div class="variant-group swatches" id="diffuserPageSwatches"
           data-base-name="{e(dif['name'])}" data-base-price="{dif['price']}"
           data-target-img="#diffuserPageImg" data-label-target="#diffuserPageColorName"
           data-chosen="Bleu" data-chosen-img="{base}{dif['colors'][0]['img']}" data-chosen-img-canonical="{dif['colors'][0]['img']}">
        {swatches_html}
      </div>
    </div>
    {meta_rows([("Contenance", dif["size"]), ("Catégorie", dif["categoryLabel"])])}
    <div class="product-actions">
      <button class="btn btn-primary" data-add-cart-variant data-variant-group="#diffuserPageSwatches">Ajouter à ma sélection</button>
      <button class="btn btn-outline" data-order-variant data-variant-group="#diffuserPageSwatches">Commander sur WhatsApp</button>
    </div>
    {trust_row()}
  </div>
</section>
{related_section(data["bruler"], "bruler", base, "__none__")}'''
    with open(os.path.join(PRODUITS_DIR, f"{dif['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(page_shell(f"{dif['name']} — Sensoria", dif["desc"][:155], "product", body, "huiles-a-bruler"))
    count += 1

    # ---- gel nettoyant (variant page: scent) ----
    gel = next(h for h in data["hammam"] if h["slug"] == "gel-nettoyant")
    variants_html = "\n        ".join(
        f'<button class="variant-opt{" active" if i==0 else ""}" data-value="{e(v["name"])}" '
        f'data-img="{base}{v["img"]}" data-img-canonical="{e(v["img"])}">{e(v["name"])}</button>'
        for i, v in enumerate(gel["variants"])
    )
    body = f'''{breadcrumb("product", gel["categoryLabel"], "rituel-hammam", gel["name"])}
<section class="product-hero">
  <div class="studio-frame">
    <span class="studio-badge">Sensoria</span>
    <img class="studio-img" id="gelPageImg" src="{base}{gel['variants'][0]['img']}" alt="Sensoria {e(gel['name'])}">
    <img class="studio-reflection" src="{base}{gel['variants'][0]['img']}" alt="" aria-hidden="true">
  </div>
  <div class="product-info">
    <p class="eyebrow p-cat">{e(gel["categoryLabel"])}</p>
    <h1>{e(gel["name"])}</h1>
    <p class="p-en">{e(gel["en"])}</p>
    <p class="p-price">{fmt_price(gel['price'])} F CFA</p>
    <p class="p-desc">{e(gel["desc"])}</p>
    <div class="variant-picker">
      <p class="swatch-label">Senteur</p>
      <div class="variant-group" id="gelPageVariants"
           data-base-name="{e(gel['name'])}" data-base-price="{gel['price']}"
           data-target-img="#gelPageImg"
           data-chosen="{e(gel['variants'][0]['name'])}" data-chosen-img="{base}{gel['variants'][0]['img']}" data-chosen-img-canonical="{gel['variants'][0]['img']}">
        {variants_html}
      </div>
    </div>
    {meta_rows([("Contenance", gel["size"]), ("Catégorie", gel["categoryLabel"])])}
    <div class="product-actions">
      <button class="btn btn-primary" data-add-cart-variant data-variant-group="#gelPageVariants">Ajouter à ma sélection</button>
      <button class="btn btn-outline" data-order-variant data-variant-group="#gelPageVariants">Commander sur WhatsApp</button>
    </div>
    {trust_row()}
  </div>
</section>
{related_section(data["hammam"], "hammam", base, gel["slug"])}'''
    with open(os.path.join(PRODUITS_DIR, f"{gel['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(page_shell(f"{gel['name']} — Sensoria", gel["desc"][:155], "product", body, "rituel-hammam"))
    count += 1

    return count


# ------------------------------------------------------------- COLLECTIONS -
def cluster_html(imgs, base):
    """imgs: list of (src, inline_style) -> absolutely positioned image cluster."""
    return "".join(f'<img src="{base}{e(src)}" style="{style}" alt="">' for src, style in imgs)


def collection_hero(eyebrow, title, desc, price_pill, imgs, base):
    cluster = cluster_html(imgs, base)
    return f'''<section class="collection-hero">
  <div class="collection-hero-inner">
    <div class="collection-hero-text">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{desc}</p>
      <span class="price-pill">{price_pill}</span>
    </div>
    <div class="collection-hero-cluster">{cluster}</div>
  </div>
</section>'''


def build_collections(data):
    os.makedirs(COLLECTIONS_DIR, exist_ok=True)
    base = "../"

    # ---- 1. Eaux de Parfum ----
    hero = collection_hero(
        "01 · Le rituel commence ici", "Eaux de Parfum",
        "Flacon carré de 50&nbsp;ml, verre épais, bouchon coloré. Chaque composition porte une matière dominante — fleur d'oranger, musc, miel, oud, épices, cèdre.",
        "12&nbsp;500 F&nbsp;CFA · 50&nbsp;ml",
        [("assets/parfum-fleur-oranger.png", "height:230px;left:8%;top:14%;transform:rotate(-6deg);z-index:1"),
         ("assets/parfum-shahad.png", "height:250px;left:38%;top:2%;z-index:2"),
         ("assets/parfum-oud-hijaz.png", "height:230px;right:6%;top:16%;transform:rotate(6deg);z-index:1")],
        base)
    cards = "\n".join(render_card(p, "parfum", base) for p in data["parfums"])
    body = f'''{breadcrumb("collection", "", "eaux-de-parfum", "")}
{hero}
<section class="collection">
  <div class="product-grid">{cards}</div>
</section>
{cross_links("eaux-de-parfum", base)}'''
    # breadcrumb with no middle label doesn't make sense on a collection page — use simplified version
    body = f'''<nav class="breadcrumb"><a href="../index.html">Accueil</a><span class="sep">/</span><span class="current">Eaux de Parfum</span></nav>
{hero}
<section class="collection">
  <div class="product-grid">{cards}</div>
</section>
{cross_links("eaux-de-parfum", base)}'''
    with open(os.path.join(COLLECTIONS_DIR, "eaux-de-parfum.html"), "w", encoding="utf-8") as f:
        f.write(page_shell("Eaux de Parfum — Sensoria",
                            "Six eaux de parfum Sensoria : fleur d'oranger, musc blanc, shahad, oud hijaz, lumière de marrakech, saladin. 12 500 F CFA, 50 ml.",
                            "collection", body, "eaux-de-parfum"))

    # ---- 2. Huiles Précieuses ----
    hero = collection_hero(
        "02 · La beauté au naturel", "Huiles Précieuses",
        "Flacon pompe habillé de cuir découpé à la main, dans les couleurs de la collection. Pour le corps et les cheveux, quelques gouttes suffisent.",
        "15&nbsp;000 F&nbsp;CFA · 50&nbsp;ml",
        [("assets/huile-fleur-orientale.png", "height:220px;left:10%;top:10%;transform:rotate(-5deg);z-index:1"),
         ("assets/huile-jasmin.png", "height:240px;left:40%;top:0%;z-index:2"),
         ("assets/huile-the-vert.png", "height:220px;right:8%;top:12%;transform:rotate(5deg);z-index:1")],
        base)
    cards = "\n".join(render_card(h, "huile", base) for h in data["huiles"])
    gf = data["grandFormat"]
    comp_tags = "".join(f'<span>{e(c)}</span>' for c in gf.get("composition", []))
    feature = f'''<div class="feature-banner">
  <a href="../produits/{gf['slug']}.html"><img src="{base}{gf['img']}" alt="{e(gf['name'])}"></a>
  <div>
    <p class="eyebrow">Le grand format</p>
    <h3><a href="../produits/{gf['slug']}.html">{e(gf['name'])}</a></h3>
    <p>{e(gf['desc'])}</p>
    <div class="tag-row">{comp_tags}</div>
    <div class="card-actions">
      <a class="btn btn-outline" href="../produits/{gf['slug']}.html">Voir le produit</a>
      <button class="btn btn-primary" data-order-info data-name="{e(gf['name'])}">Demander le prix sur WhatsApp</button>
    </div>
  </div>
</div>'''
    body = f'''<nav class="breadcrumb"><a href="../index.html">Accueil</a><span class="sep">/</span><span class="current">Huiles Précieuses</span></nav>
{hero}
<section class="collection">
  <div class="product-grid">{cards}</div>
  {feature}
</section>
{cross_links("huiles-precieuses", base)}'''
    with open(os.path.join(COLLECTIONS_DIR, "huiles-precieuses.html"), "w", encoding="utf-8") as f:
        f.write(page_shell("Huiles Précieuses — Sensoria",
                            "Six huiles précieuses Sensoria pour le corps et les cheveux, flacon habillé de cuir. 15 000 F CFA, 50 ml. Grand format 100 ml disponible.",
                            "collection", body, "huiles-precieuses"))

    # ---- 3. Huiles à Brûler + Diffuseurs ----
    hero = collection_hero(
        "03 · Votre rituel Sensoriarituals", "Huiles &amp; Diffuseurs",
        "Flacon ambré compte-gouttes, habillage cuir ajouré. Quelques gouttes dans un brûle-parfum suffisent à parfumer une pièce entière.",
        "10&nbsp;000 — 14&nbsp;000 F&nbsp;CFA · 50&nbsp;ml",
        [("assets/bruler-marrakchi.png", "height:210px;left:10%;top:14%;transform:rotate(-6deg);z-index:1"),
         ("assets/diffuseur-bleu.png", "height:210px;left:40%;top:6%;z-index:2"),
         ("assets/bruler-atlas.png", "height:210px;right:10%;top:14%;transform:rotate(6deg);z-index:1")],
        base)
    cards = "\n".join(render_card(b, "bruler", base) for b in data["bruler"])
    dif = data["diffuseur"]
    swatches_html = "\n        ".join(diffuser_swatch_button(c, base, active=(c["name"] == "Bleu")) for c in dif["colors"])
    diffuser_widget = f'''<div class="section-head" style="margin-top:4rem">
    <p class="eyebrow">Terre cuite · fait main</p>
    <h2>Diffuseurs</h2>
    <p class="section-sub">Façonnés à la main en terre blanche cuite, puis émaillés un à un. Choisissez votre teinte. <strong>8&nbsp;500 F&nbsp;CFA</strong> · pièce unique. <a href="../produits/{dif['slug']}.html" style="color:var(--terracotta);font-weight:600">Voir la fiche produit →</a></p>
  </div>
  <div class="diffuser-card">
    <div class="diffuser-media"><img id="diffuserImg" src="{base}{dif['colors'][0]['img']}" alt="Diffuseur en terre cuite"></div>
    <div class="diffuser-info">
      <h3>{e(dif['name'])}</h3>
      <p>{e(dif['desc'])}</p>
      <p class="swatch-label">Coloris — <span id="diffuserColorName">Bleu</span></p>
      <div class="swatches variant-group" id="diffuserSwatches"
           data-base-name="{e(dif['name'])}" data-base-price="{dif['price']}"
           data-target-img="#diffuserImg" data-label-target="#diffuserColorName"
           data-chosen="Bleu" data-chosen-img="{base}{dif['colors'][0]['img']}" data-chosen-img-canonical="{dif['colors'][0]['img']}">
        {swatches_html}
      </div>
      <div class="price-row">
        <span class="price">8&nbsp;500 F CFA</span>
        <div class="card-actions">
          <button class="btn btn-outline" data-add-cart-variant data-variant-group="#diffuserSwatches">Ajouter à ma sélection</button>
          <button class="btn btn-primary" data-order-variant data-variant-group="#diffuserSwatches">Commander</button>
        </div>
      </div>
    </div>
  </div>'''
    body = f'''<nav class="breadcrumb"><a href="../index.html">Accueil</a><span class="sep">/</span><span class="current">Huiles &amp; Diffuseurs</span></nav>
{hero}
<section class="collection">
  <div class="product-grid">{cards}</div>
  {diffuser_widget}
</section>
{cross_links("huiles-a-bruler", base)}'''
    with open(os.path.join(COLLECTIONS_DIR, "huiles-a-bruler.html"), "w", encoding="utf-8") as f:
        f.write(page_shell("Huiles à Brûler & Diffuseurs — Sensoria",
                            "Dix huiles à brûler Sensoria et diffuseurs en terre cuite faits main, en sept coloris. À partir de 10 000 F CFA.",
                            "collection", body, "huiles-a-bruler"))

    # ---- 4. Rituel Hammam ----
    hero = collection_hero(
        "04 · Prendre soin de soi", "Rituel Hammam",
        "Savon noir, gant de gommage, gommage au sucre, huile précieuse : quatre gestes dans l'ordre, une peau nette et souple à la sortie.",
        "Dès 2&nbsp;500 F&nbsp;CFA",
        [("assets/gommage-sucre.png", "height:190px;left:8%;top:18%;transform:rotate(-4deg);z-index:1"),
         ("assets/savon-fleur-oranger.png", "height:170px;left:42%;top:6%;z-index:2"),
         ("assets/gant-gommage.png", "height:190px;right:10%;top:20%;transform:rotate(5deg);z-index:1")],
        base)
    steps = '''<div class="steps-row">
    <div class="step"><span class="step-num">1</span><h4>Savon noir</h4><p>Sur peau humide, 5 à 10 minutes dans la vapeur.</p></div>
    <div class="step"><span class="step-num">2</span><h4>Gant kessa</h4><p>Mouvements longs, sans appuyer, puis rincer.</p></div>
    <div class="step"><span class="step-num">3</span><h4>Gommage au sucre</h4><p>En massage circulaire, puis rinçage à l'eau claire.</p></div>
    <div class="step"><span class="step-num">4</span><h4>Huile précieuse</h4><p>Sur peau encore tiède, pour finir le rituel.</p></div>
  </div>'''
    cards = "\n".join(render_card(h, "hammam", base) for h in data["hammam"])
    body = f'''<nav class="breadcrumb"><a href="../index.html">Accueil</a><span class="sep">/</span><span class="current">Rituel Hammam</span></nav>
{hero}
<section class="collection">
  {steps}
  <div class="product-grid">{cards}</div>
</section>
{cross_links("rituel-hammam", base)}'''
    with open(os.path.join(COLLECTIONS_DIR, "rituel-hammam.html"), "w", encoding="utf-8") as f:
        f.write(page_shell("Rituel Hammam — Sensoria",
                            "Savon noir, gant de gommage, gommage au sucre, sel de bain, gel nettoyant et savons parfumés Sensoria. Le rituel hammam en quatre gestes.",
                            "collection", body, "rituel-hammam"))

    print("4 collection pages generated in /collections")


# ------------------------------------------------------------- HOMEPAGE ----
def gamme_card(slug, cls, title, teaser, count, imgs, base=""):
    cluster = cluster_html(imgs, base)
    return f'''<a href="collections/{slug}.html" class="gamme-card {cls} reveal">
  <div class="gamme-cluster">{cluster}</div>
  <div class="gamme-body">
    <h3>{title}</h3>
    <p>{teaser}</p>
    <div class="gamme-meta">
      <span class="gamme-count">{count}</span>
      <span class="gamme-link">Découvrir →</span>
    </div>
  </div>
</a>'''


def build_gammes_overview(data):
    cards = [
        gamme_card("eaux-de-parfum", "g-parfum", "Eaux de Parfum",
                   "Six sillages, flacon carré 50 ml, bouchon coloré.", "6 références · 12 500 F CFA",
                   [("assets/parfum-fleur-oranger.png", "height:130px;left:22%;top:20%;transform:rotate(-6deg)"),
                    ("assets/parfum-oud-hijaz.png", "height:140px;left:52%;top:10%;transform:rotate(5deg);z-index:2")]),
        gamme_card("huiles-precieuses", "g-huile", "Huiles Précieuses",
                   "Flacon cuir découpé à la main, pour corps et cheveux.", "6 références · 15 000 F CFA",
                   [("assets/huile-fleur-orientale.png", "height:150px;left:26%;top:8%;transform:rotate(-5deg)"),
                    ("assets/huile-the-vert.png", "height:150px;left:54%;top:14%;transform:rotate(5deg);z-index:2")]),
        gamme_card("huiles-a-bruler", "g-bruler", "Huiles &amp; Diffuseurs",
                   "Dix senteurs à brûler, diffuseurs en terre cuite faits main.", "11 références · dès 8 500 F CFA",
                   [("assets/bruler-marrakchi.png", "height:130px;left:24%;top:18%;transform:rotate(-6deg)"),
                    ("assets/diffuseur-bleu.png", "height:130px;left:54%;top:16%;transform:rotate(5deg);z-index:2")]),
        gamme_card("rituel-hammam", "g-hammam", "Rituel Hammam",
                   "Savon noir, gommage, sel de bain — quatre gestes, dans l'ordre.", "7 références · dès 2 500 F CFA",
                   [("assets/gommage-sucre.png", "height:120px;left:22%;top:22%;transform:rotate(-5deg)"),
                    ("assets/savon-fleur-oranger.png", "height:110px;left:54%;top:24%;transform:rotate(5deg);z-index:2")]),
    ]
    return "\n".join(cards)


def build_featured_picks(data):
    picks = [
        (data["parfums"][0], "parfum"),
        (next(h for h in data["huiles"] if h["slug"] == "fleur-orientale-huile"), "huile"),
        (next(b for b in data["bruler"] if b["slug"] == "bakhour-bruler"), "bruler"),
        (next(h for h in data["hammam"] if h["slug"] == "gommage-sucre"), "hammam"),
    ]
    return "\n".join(render_card(item, kind, "") for item, kind in picks)


def build_homepage(data):
    quiz_data = json.dumps([
        {
            "key": {"fleur-oranger-edp": "oranger", "musc-blanc-edp": "musc", "shahad-edp": "shahad",
                    "oud-hijaz-edp": "oud", "lumiere-marrakech-edp": "marrakech", "saladin-edp": "saladin"}[p["slug"]],
            "name": p["name"], "family": p["family"], "desc": p["desc"], "price": p["price"],
            "img": p["img"], "url": f"produits/{p['slug']}.html",
        } for p in data["parfums"]
    ], ensure_ascii=False)

    index_html = open(INDEX_PATH, encoding="utf-8").read()
    index_html = index_html.replace("<!--GAMMES_OVERVIEW-->", build_gammes_overview(data))
    index_html = index_html.replace("<!--FEATURED_PICKS-->", build_featured_picks(data))
    index_html = index_html.replace("<!--QUIZ_DATA-->", quiz_data)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(index_html)
    print("index.html updated")


def build():
    data = json.load(open(DATA_PATH, encoding="utf-8"))
    os.makedirs(PRODUITS_DIR, exist_ok=True)
    os.makedirs(COLLECTIONS_DIR, exist_ok=True)

    build_homepage(data)
    build_collections(data)
    count = build_product_pages(data)
    print(f"{count} product pages generated in /produits")


if __name__ == "__main__":
    build()
