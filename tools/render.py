#!/usr/bin/env python3
"""The shell and the shared components.

Every page on the site is assembled here: one <head> builder, one header, one
footer, one product card. A nav link exists in exactly one place rather than in
thirty-nine files, which is how a dead internal link stops being possible.

This is a development aid, not a runtime dependency -- what ships is plain HTML.
"""

from __future__ import annotations

import html
import json

from catalog import CAT_SLUG, CATEGORIES, INGREDIENTS, Product

SITE = "https://kulieff21.github.io/ecommerce-site-demo/"
BRAND = "Zərrə"
PHONE_HUMAN = "+994 12 000 00 00"
PHONE_LINK = "+99412000000"
EMAIL = "salam@zerre.example"

e = html.escape


def money(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " ₼"


# --- Icons. Inline SVG, never emoji: emoji render differently on every platform
#     and are read aloud by screen readers as their unicode name. ---------------
_ICONS = {
    "cart": '<path d="M3 4h2l2.4 10.4a2 2 0 0 0 2 1.6h7.5a2 2 0 0 0 2-1.55L20.5 8H6"/>'
            '<circle cx="10" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    "plus": '<path d="M12 6v12M6 12h12"/>',
    "check": '<path d="M4.5 12.5l5 5 10-11"/>',
    "arrow": '<path d="M4 12h15M13 6l6 6-6 6"/>',
    "truck": '<path d="M2 6h11v11H2zM13 9h4l4 4v4h-8z"/><circle cx="7" cy="18.5" r="1.6"/>'
             '<circle cx="17" cy="18.5" r="1.6"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "leaf": '<path d="M20 4C10 4 4 9 4 16c0 2 1 4 1 4s2-8 15-11c0 0-4 3-7 4-3.5 1.2-6 3-7 7 8 1 14-4 14-16z"/>',
    "return": '<path d="M4 9h11a5 5 0 0 1 0 10H8"/><path d="M8 5L4 9l4 4"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.6v.8"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 12l5 2v4a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 3 5.2 2 2 0 0 1 5 3z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5L12 13l8.5-6.5"/>',
    "flask": '<path d="M10 3h4M11 3v6L5.5 18A2 2 0 0 0 7.2 21h9.6a2 2 0 0 0 1.7-3L13 9V3"/>'
             '<path d="M8 15h8"/>',
    "trash": '<path d="M4 7h16M9 7V5h6v2M6 7l1 13h10l1-13"/>',
    "star_full": '<path d="M12 3.5l2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.9l6-.8z" '
                 'fill="currentColor" stroke="none"/>',
    "star_half": '<path d="M12 3.5l2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.9l6-.8z"/>'
                 '<path d="M12 3.5V18.2l-5.3 2.9 1.1-6L3.4 9.9l6-.8z" fill="currentColor" stroke="none"/>',
}


def icon(name: str, cls: str = "i") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{_ICONS[name]}</svg>')


def stars(rating: float, count: int | None = None) -> str:
    full = int(rating)
    half = (rating - full) >= 0.35
    out = [icon("star_full") for _ in range(full)]
    if half:
        out.append(icon("star_half"))
    label = f"5 ulduzdan {rating}".replace(".", ",")
    tail = f' <span class="muted">({count})</span>' if count is not None else ""
    return (f'<span class="rating"><span class="vh">{label}</span>{"".join(out)}'
            f'<b aria-hidden="true">{str(rating).replace(".", ",")}</b>{tail}</span>')


# --- The formula spine -------------------------------------------------------
def spine(p: Product) -> str:
    """The product's own percentages, edge to edge under the image. It is the same
    data as the table on the product page, at a size where it works as identity."""
    parts = []
    for ing, pct in p.formula:
        colour = INGREDIENTS[ing][0]
        parts.append(f'<span style="flex:{pct};background:{colour}"></span>')
    return f'<div class="spine" aria-hidden="true">{"".join(parts)}</div>'


def formula_card(p: Product, note: str | None = None) -> str:
    bar = "".join(
        f'<span style="flex:{pct};background:{INGREDIENTS[ing][0]}"></span>'
        for ing, pct in p.formula
    )
    rows = []
    for ing, pct in p.formula:
        colour, role, origin = INGREDIENTS[ing]
        chip = f'<span class="origin">{e(origin)}</span>' if origin else ""
        rows.append(
            f'<li><span class="formula__sw" style="background:{colour}"></span>'
            f'<span><span class="formula__name">{e(ing)}</span>{chip}<br>'
            f'<span class="formula__role">{e(role)}</span></span>'
            f'<span class="formula__pct num">{str(pct).replace(".", ",")}%</span></li>'
        )
    note = note or ("Yüzdə yüzün hamısı yazılıb — “təbii tərkib” yazıb qalanını gizlətmirik.")
    return (
        f'<div class="formula">'
        f'<div class="formula__bar" role="img" aria-label="{e(p.name)} tərkibinin faiz payları">{bar}</div>'
        f'<ul class="formula__rows">{"".join(rows)}</ul>'
        f'<p class="formula__note">{icon("flask")} {e(note)}</p>'
        f"</div>"
    )


def product_card(p: Product, reveal: bool = True) -> str:
    badge = ""
    if p.badge:
        text = {"yeni": "Yeni", "endirim": f"−{p.discount_pct}%", "cox-satilan": "Çox alınan"}[p.badge]
        badge = f'<span class="badge badge--{p.badge}">{e(text)}</span>'
    old = f'<span class="price__old">{money(p.old)}</span>' if p.old else ""
    # The filter and sort controls read these off the card, so a shopper with
    # scripting on never waits for a second copy of the catalogue to download.
    ings = " ".join(i for i, _ in p.formula)
    return (
        f'<li class="card{" reveal" if reveal else ""}" data-slug="{p.slug}" '
        f'data-cat="{p.cat}" data-tags="{" ".join(p.tags)}" data-price="{p.price}" '
        f'data-rating="{p.rating}" data-find="{e((p.name + " " + p.kind + " " + ings).lower())}">'
        f'<div class="card__media">{badge}'
        f'<img src="{p.img}" alt="{e(p.alt)}" width="320" height="400" loading="lazy" decoding="async">'
        f"</div>{spine(p)}"
        f'<div class="card__body">'
        f'<span class="card__cat">{e(p.cat_name)}</span>'
        f'<h3 class="card__name"><a href="{p.url}">{e(p.name)}</a></h3>'
        f'<span class="card__meta">{e(p.kind)} · {e(p.volume)}</span>'
        f"{stars(p.rating, p.reviews)}"
        f'<div class="card__foot">'
        f'<span class="price"><span class="price__now num">{money(p.price)}</span>{old}</span>'
        f'<button class="btn-add" type="button" data-add="{p.slug}" '
        f'aria-label="{e(p.name)} — səbətə at">{icon("plus")}</button>'
        f"</div></div></li>"
    )


def product_grid(items: list[Product], cls: str = "grid") -> str:
    return f'<ul class="{cls}">{"".join(product_card(p) for p in items)}</ul>'


# --- Shell -------------------------------------------------------------------
def _jsonld(blocks: list[dict]) -> str:
    if not blocks:
        return ""
    out = []
    for b in blocks:
        out.append('    <script type="application/ld+json">\n'
                   + json.dumps(b, ensure_ascii=False, indent=2)
                   + "\n    </script>")
    return "\n" + "\n".join(out) + "\n"


def head(*, title: str, desc: str, slug: str, og_title: str | None = None,
         og_desc: str | None = None, jsonld: list[dict] | None = None,
         og_image: str = "assets/img/og-cover.png") -> str:
    url = SITE + ("" if slug == "index.html" else slug)
    return f"""<!doctype html>
<html lang="az" class="no-js">
  <head>
    <meta charset="utf-8" />
    <!-- Drops .no-js before first paint, so nothing that scripting will hide flashes first. -->
    <script>document.documentElement.className="js";</script>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}" />
    <link rel="canonical" href="{url}" />
    <meta name="theme-color" content="#e9ede6" media="(prefers-color-scheme: light)" />
    <meta name="theme-color" content="#12150f" media="(prefers-color-scheme: dark)" />
    <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml" />
    <link rel="preload" href="assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="stylesheet" href="assets/css/style.css" />

    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{BRAND}" />
    <meta property="og:locale" content="az_AZ" />
    <meta property="og:title" content="{e(og_title or title)}" />
    <meta property="og:description" content="{e(og_desc or desc)}" />
    <meta property="og:image" content="{SITE}{og_image}" />
    <meta property="og:url" content="{url}" />
    <meta name="twitter:card" content="summary_large_image" />
{_jsonld(jsonld or [])}  </head>
"""


NAV = [
    ("magaza.html", "Mağaza"),
    ("terkib.html", "Tərkib"),
    ("catdirilma.html", "Çatdırılma"),
    ("haqqimizda.html", "Haqqımızda"),
    ("elaqe.html", "Əlaqə"),
]

_MARK = ('<svg class="brand__mark" viewBox="0 0 24 24" aria-hidden="true">'
         '<circle cx="12" cy="12" r="9.1" fill="none" stroke="currentColor" stroke-width="1.9"/>'
         '<circle cx="15.1" cy="8.9" r="2.6" fill="currentColor"/></svg>')


def header(active: str) -> str:
    def link(href, label, cls=""):
        cur = ' aria-current="page"' if href == active else ""
        return f'<a href="{href}"{cur}{cls}>{label}</a>'

    nav = "".join(link(h, l) for h, l in NAV)
    menu = "".join(link(h, l) for h, l in NAV)
    return f"""    <header class="site-header">
      <div class="wrap site-header__bar">
        <a class="brand" href="index.html">{_MARK}{BRAND}</a>
        <nav class="nav" aria-label="Əsas menyu">{nav}</nav>
        <details class="menu">
          <summary aria-label="Menyunu aç">{icon("menu")}</summary>
          <div class="menu__panel">{menu}</div>
        </details>
        <div class="site-header__actions">
          <a class="iconbtn" href="magaza.html#axtaris" aria-label="Məhsul axtar">{icon("search")}</a>
          <a class="iconbtn" href="sebet.html" aria-label="Səbət">
            {icon("cart")}<span class="cart-count num" data-cart-count hidden>0</span>
          </a>
        </div>
      </div>
    </header>"""


def footer() -> str:
    cats = "".join(
        f'<li><a href="kateqoriya-{CAT_SLUG[key]}.html">{e(name)}</a></li>'
        for key, name, _slug, _d in CATEGORIES
    )
    return f"""    <footer class="site-footer">
      <div class="wrap site-footer__grid">
        <div class="site-footer__about">
          <a class="brand" href="index.html">{_MARK}{BRAND}</a>
          <p>Bakıda hazırlanan dəri və saç baxımı. Hər məhsulun tərkibi faizlə yazılır —
             içində nə olduğunu almadan əvvəl bilirsiniz.</p>
          <p class="demo-note">Bu sayt nümunə işidir. {BRAND} mövcud bir şirkət deyil,
             sifariş qəbul edilmir və heç bir məlumat saxlanılmır.</p>
        </div>
        <div>
          <h4>Kateqoriyalar</h4>
          <ul>{cats}</ul>
        </div>
        <div>
          <h4>Kömək</h4>
          <ul>
            <li><a href="catdirilma.html">Çatdırılma və ödəniş</a></li>
            <li><a href="qaytarma.html">Qaytarma şərtləri</a></li>
            <li><a href="terkib.html">Tərkib haqqında</a></li>
            <li><a href="mexfilik.html">Məxfilik siyasəti</a></li>
          </ul>
        </div>
        <div>
          <h4>Əlaqə</h4>
          <ul>
            <li><a href="tel:{PHONE_LINK}">{icon("phone")}&nbsp;{PHONE_HUMAN}</a></li>
            <li><a href="mailto:{EMAIL}">{icon("mail")}&nbsp;{EMAIL}</a></li>
          </ul>
          <p class="muted" style="font-size:.84rem;margin-top:8px">
            Hər gün 09:00–20:00<br>Bakı, Azərbaycan</p>
        </div>
      </div>
      <div class="wrap site-footer__bottom">
        <span>© 2026 {BRAND} — nümunə layihə</span>
        <span>Qiymətlər AZN ilə göstərilir</span>
      </div>
    </footer>"""


def page(*, slug: str, title: str, desc: str, body: str, active: str = "",
         og_title: str | None = None, og_desc: str | None = None,
         jsonld: list[dict] | None = None) -> str:
    return (
        head(title=title, desc=desc, slug=slug, og_title=og_title, og_desc=og_desc,
             jsonld=jsonld)
        + '\n  <body>\n    <a class="skip-link" href="#main">Əsas məzmuna keç</a>\n\n'
        + header(active or slug) + "\n\n"
        + '    <main id="main">\n' + body.rstrip() + "\n    </main>\n\n"
        + footer() + "\n\n"
        + '    <div class="toast" data-toast role="status" aria-live="polite"></div>\n'
        + '    <script src="assets/js/data.js" defer></script>\n'
        + '    <script src="assets/js/site.js" defer></script>\n'
        + "  </body>\n</html>\n"
    )
