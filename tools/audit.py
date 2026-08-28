#!/usr/bin/env python3
"""Runs our own client audit checklist against this site.

We tell clients their shop has no <h1>, that 61 of 63 product images carry an
empty alt, that the sitemap lists pages which 404, that the email link is written
`mail:` so nothing opens. This script asserts none of that is true here, because a
demo that fails its own report is worth less than no demo.

    python3 tools/audit.py        # exit 1 if anything fails

It is deliberately independent of the builder: it reads the HTML that shipped,
not the data that produced it, so a bug in build_pages.py cannot hide from it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://kulieff21.github.io/ecommerce-site-demo/"

FAILS: list[str] = []
NOTES: list[tuple[str, str]] = []


def fail(page: str, msg: str) -> None:
    FAILS.append(f"{page}: {msg}")


def ok(check: str, detail: str) -> None:
    NOTES.append((check, detail))


def pages() -> list[Path]:
    return sorted(ROOT.glob("*.html"))


TEXT = {p.name: p.read_text(encoding="utf-8") for p in pages()}


# --- 1. lang -----------------------------------------------------------------
def check_lang() -> None:
    bad = [n for n, t in TEXT.items() if '<html lang="az"' not in t]
    for n in bad:
        fail(n, 'missing <html lang="az">')
    ok("lang", f'{len(TEXT) - len(bad)}/{len(TEXT)} pages declare lang="az"')


# --- 2. headings -------------------------------------------------------------
def check_h1() -> None:
    for n, t in TEXT.items():
        h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
        if len(h1s) != 1:
            fail(n, f"{len(h1s)} <h1> elements, expected exactly 1")
            continue
        text = re.sub(r"<[^>]+>", "", h1s[0]).strip()
        if not text:
            fail(n, "<h1> is empty")
        elif text.lower() in {"zərrə", "zerre"}:
            fail(n, "<h1> is the brand name rather than the page's subject")
    ok("h1", "every page has exactly one <h1>, and it names the page's subject")


# --- 3. image alt ------------------------------------------------------------
GENERIC_ALT = re.compile(r"^(image|photo|şəkil|foto|img|picture|product|məhsul)\W*$", re.I)


def check_alt() -> None:
    missing = empty = generic = total = 0
    for n, t in TEXT.items():
        for tag in re.findall(r"<img\b[^>]*>", t):
            total += 1
            m = re.search(r'\balt="([^"]*)"', tag)
            if m is None:
                missing += 1
                fail(n, f"<img> with no alt attribute: {tag[:80]}")
            elif not m.group(1).strip():
                empty += 1
                fail(n, f"<img> with an empty alt: {tag[:80]}")
            elif GENERIC_ALT.match(m.group(1).strip()):
                generic += 1
                fail(n, f"<img> alt says nothing: {m.group(1)!r}")
    ok("alt", f"{total} images, {missing} missing / {empty} empty / {generic} generic")


# --- 4 & 5. title and description --------------------------------------------
def check_meta() -> None:
    titles: dict[str, str] = {}
    descs: dict[str, str] = {}
    for n, t in TEXT.items():
        m = re.search(r"<title>(.*?)</title>", t, re.S)
        if not m or not m.group(1).strip():
            fail(n, "no <title>")
        else:
            title = m.group(1).strip()
            if not 15 <= len(title) <= 70:
                fail(n, f"<title> is {len(title)} characters (want 15-70): {title!r}")
            if title in titles:
                fail(n, f"<title> is a copy of the one on {titles[title]}")
            titles[title] = n

        d = re.search(r'<meta name="description" content="([^"]*)"', t)
        if not d or not d.group(1).strip():
            fail(n, "no meta description")
        else:
            desc = d.group(1).strip()
            if not 50 <= len(desc) <= 175:
                fail(n, f"meta description is {len(desc)} characters (want 50-175)")
            if desc in descs:
                fail(n, f"meta description is a copy of the one on {descs[desc]}")
            descs[desc] = n
    ok("title/description", f"{len(titles)} unique titles, {len(descs)} unique descriptions")


# --- 6. Open Graph -----------------------------------------------------------
OG_REQUIRED = ["og:title", "og:description", "og:image", "og:url", "og:type"]


def check_og() -> None:
    for n, t in TEXT.items():
        for prop in OG_REQUIRED:
            if f'property="{prop}"' not in t:
                fail(n, f"missing {prop}")
        m = re.search(r'<meta property="og:image" content="([^"]+)"', t)
        if m:
            rel = m.group(1).replace(SITE, "")
            if not (ROOT / rel).exists():
                fail(n, f"og:image points at a file that does not exist: {rel}")
        c = re.search(r'<link rel="canonical" href="([^"]+)"', t)
        if not c:
            fail(n, "no canonical link")
        elif not c.group(1).startswith(SITE):
            fail(n, f"canonical does not point at this site: {c.group(1)}")
    ok("open graph", f"all five og: tags plus a canonical on {len(TEXT)} pages")


# --- 7. structured data ------------------------------------------------------
def blocks(text: str) -> list[dict]:
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
        out.append(json.loads(raw))
    return out


def check_jsonld() -> None:
    kinds: dict[str, int] = {}
    for n, t in TEXT.items():
        try:
            found = blocks(t)
        except json.JSONDecodeError as err:
            fail(n, f"JSON-LD does not parse: {err}")
            continue
        types = [b.get("@type") for b in found]
        for ty in types:
            kinds[ty] = kinds.get(ty, 0) + 1

        if n == "index.html":
            for want in ("OnlineStore", "WebSite", "FAQPage"):
                if want not in types:
                    fail(n, f"home page has no {want} block")
        if n.startswith("mehsul-"):
            if "Product" not in types:
                fail(n, "product page has no Product block")
            else:
                prod = found[types.index("Product")]
                for field in ("name", "image", "description", "brand", "offers",
                              "aggregateRating"):
                    if not prod.get(field):
                        fail(n, f"Product block has no {field}")
                offer = prod.get("offers", {})
                if offer.get("priceCurrency") != "AZN":
                    fail(n, "offer is not priced in AZN")
                if not re.fullmatch(r"\d+\.\d{2}", str(offer.get("price", ""))):
                    fail(n, f"offer price is not a plain decimal: {offer.get('price')!r}")
                rating = prod.get("aggregateRating", {})
                if not rating.get("reviewCount"):
                    fail(n, "aggregateRating has no reviewCount")
        if n.startswith(("magaza", "kateqoriya-")) and "ItemList" not in types:
            fail(n, "listing page has no ItemList block")
        if n != "404.html" and "BreadcrumbList" not in types and n != "index.html":
            fail(n, "no BreadcrumbList")
    ok("json-ld", ", ".join(f"{k}×{v}" for k, v in sorted(kinds.items())))


# --- 8. protocol links -------------------------------------------------------
def check_protocols() -> None:
    mails = tels = 0
    for n, t in TEXT.items():
        for href in re.findall(r'href="([^"]+)"', t):
            if href.startswith("mailto:"):
                mails += 1
                if not re.fullmatch(r"mailto:[^\s@]+@[^\s@]+\.[^\s@]+", href):
                    fail(n, f"malformed mailto: {href}")
            elif href.startswith("tel:"):
                tels += 1
                if not re.fullmatch(r"tel:\+?[0-9]+", href):
                    fail(n, f"tel: link must be digits with no spaces: {href}")
            elif re.match(r"^mail:|^phone:|^telephone:", href):
                fail(n, f"wrong protocol, nothing will open: {href}")
    ok("protocol links", f"{mails} mailto: and {tels} tel: links, all well-formed")


# --- 9 & 10. links and assets ------------------------------------------------
def check_links() -> None:
    internal = external = 0
    for n, t in TEXT.items():
        for href in re.findall(r'href="([^"]+)"', t):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            internal += 1
            if not (ROOT / target).exists():
                fail(n, f"link to a file that does not exist: {href}")
        for src in re.findall(r'\bsrc="([^"]+)"', t):
            if src.startswith(("http://", "https://")):
                external += 1
                fail(n, f"loads from a third party -- the site must run from a folder: {src}")
            elif not src.startswith("data:") and not (ROOT / src).exists():
                fail(n, f"asset does not exist: {src}")
    # Stylesheets and fonts too: a CDN reference is the thing being audited against.
    for n, t in TEXT.items():
        for tag in re.findall(r"<link\b[^>]*>", t):
            if not re.search(r'rel="(stylesheet|preload|modulepreload)"', tag):
                continue          # canonical and icon links are meant to be absolute
            href = re.search(r'href="(https?://[^"]+)"', tag)
            if href:
                fail(n, f"external stylesheet or font: {href.group(1)}")
    css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
    for url in re.findall(r"url\(\s*['\"]?(https?://[^)'\"]+)", css):
        fail("assets/css/style.css", f"stylesheet fetches from a third party: {url}")
    for url in re.findall(r"url\(\s*['\"]?(?!https?:|data:)([^)'\"]+)", css):
        path = (ROOT / "assets/css" / url).resolve()
        if not path.exists():
            fail("assets/css/style.css", f"missing asset: {url}")
    ok("links & assets", f"{internal} internal links and every referenced asset resolve; "
                         f"{external} third-party requests")


# --- 11. placeholders --------------------------------------------------------
PLACEHOLDERS = [r"lorem ipsum", r"\bTODO\b", r"\bFIXME\b", r"\bXXX\b", r"Salam dünya",
                r"\bplaceholder\b", r"Hello world", r"\bfoo\b", r"Xəta 404",
                r"text here", r"buraya yazın"]


def visible_text(html_text: str) -> str:
    """Only what a visitor actually reads. Attribute values are markup, not copy."""
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", html_text, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", body)


def check_placeholders() -> None:
    for n, t in TEXT.items():
        text = visible_text(t)
        for pat in PLACEHOLDERS:
            if re.search(pat, text, re.I):
                fail(n, f"placeholder text left in the page: {pat}")
    ok("placeholders", "no lorem ipsum, no TODO, no leftover scaffolding")


# --- 12. robots and sitemap --------------------------------------------------
def check_sitemap() -> None:
    if not (ROOT / "robots.txt").exists():
        fail("robots.txt", "does not exist")
        return
    sm = ROOT / "sitemap.xml"
    if not sm.exists():
        fail("sitemap.xml", "does not exist")
        return
    listed = re.findall(r"<loc>([^<]+)</loc>", sm.read_text(encoding="utf-8"))
    for url in listed:
        rel = url.replace(SITE, "") or "index.html"
        if not (ROOT / rel).exists():
            fail("sitemap.xml", f"lists a URL that does not exist: {url}")
    have = {p.name for p in pages()} - {"404.html"}
    listed_names = {u.replace(SITE, "") or "index.html" for u in listed}
    for missing in sorted(have - listed_names):
        fail("sitemap.xml", f"does not list {missing}")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap:" not in robots:
        fail("robots.txt", "does not point at the sitemap")
    ok("robots & sitemap", f"{len(listed)} URLs listed, all of them real")


# --- 13. prices agree across the page, the schema and the cart data ----------
def check_prices() -> None:
    data = (ROOT / "assets/js/data.js").read_text(encoding="utf-8")
    raw = data[data.index("mehsullar:") + len("mehsullar:"):data.rindex("}\n};")]
    cart_prices = {m.group(1): float(m.group(2)) for m in
                   re.finditer(r'"([a-z0-9-]+)":\s*\{[^}]*?"qiymet":\s*([0-9.]+)', raw, re.S)}
    checked = 0
    for n, t in TEXT.items():
        if not n.startswith("mehsul-"):
            continue
        slug = n[len("mehsul-"):-len(".html")]
        schema = float(blocks(t)[0]["offers"]["price"])
        shown = re.search(r'<span class="price__now num">([\d\s]+,\d\d) ₼</span>', t)
        if not shown:
            fail(n, "no price rendered on the page")
            continue
        visible = float(shown.group(1).replace(" ", "").replace(",", "."))
        if abs(visible - schema) > 0.005:
            fail(n, f"page shows {visible} but the schema offer says {schema}")
        if slug not in cart_prices:
            fail(n, "product is missing from data.js, so the cart cannot price it")
        elif abs(cart_prices[slug] - schema) > 0.005:
            fail(n, f"cart price {cart_prices[slug]} disagrees with the offer {schema}")
        checked += 1
    ok("prices", f"{checked} products: page, JSON-LD offer and cart data all agree")


# --- 14. every product is reachable without scripting ------------------------
def check_reachable() -> None:
    catalogue = TEXT["magaza.html"]
    unreachable = [n for n in TEXT if n.startswith("mehsul-") and f'href="{n}"' not in catalogue]
    for n in unreachable:
        fail("magaza.html", f"{n} is not linked from the catalogue")
    ok("crawlability", f"{sum(1 for n in TEXT if n.startswith('mehsul-'))} product pages are "
                       "static URLs linked from the catalogue markup")


# --- 15. contrast ------------------------------------------------------------
def srgb(c: str) -> tuple[float, float, float]:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(c: str) -> float:
    def lin(v: float) -> float:
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in srgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def tokens() -> tuple[dict[str, str], dict[str, str]]:
    css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
    light_block = css[css.index(":root {"):css.index("@media (prefers-color-scheme: dark)")]
    dark_start = css.index("@media (prefers-color-scheme: dark)")
    dark_block = css[dark_start:css.index("/* --- Reset")]
    grab = lambda block: {m.group(1): m.group(2) for m in
                          re.finditer(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6});", block)}
    light = grab(light_block)
    dark = dict(light)
    dark.update(grab(dark_block))
    return light, dark


PAIRS = [
    ("ink", "ground", 4.5), ("ink-2", "ground", 4.5), ("ink-3", "ground", 4.5),
    ("ink", "surface", 4.5), ("ink-2", "surface", 4.5), ("ink-3", "surface", 4.5),
    ("ink-2", "panel", 4.5), ("ink-3", "panel", 4.5),
    ("nar", "ground", 4.5), ("nar", "surface", 4.5),
    ("zefaran", "zefaran-soft", 4.5), ("ok", "surface", 4.5),
    ("ink", "panel", 4.5),
]
# Button label colour is not a token -- it is set per scheme in the button rules.
BUTTON = {"light": "#ffffff", "dark": "#1a0a11"}


def check_contrast() -> None:
    light, dark = tokens()
    worst = 99.0
    for scheme, vars_ in (("light", light), ("dark", dark)):
        for fg, bg, minimum in PAIRS:
            r = ratio(vars_[fg], vars_[bg])
            worst = min(worst, r)
            if r < minimum:
                fail(f"contrast/{scheme}", f"--{fg} on --{bg} is {r:.2f}:1, below {minimum}:1")
        r = ratio(BUTTON[scheme], vars_["nar"])
        worst = min(worst, r)
        if r < 4.5:
            fail(f"contrast/{scheme}", f"primary button label on --nar is {r:.2f}:1")
    ok("contrast", f"{len(PAIRS) * 2 + 2} colour pairs measured in both schemes, "
                   f"lowest {worst:.2f}:1 (WCAG AA wants 4.5:1)")


# --- 16. scripting is an enhancement, never a prerequisite -------------------
def check_no_js() -> None:
    for n, t in TEXT.items():
        if re.search(r"\son(click|load|error|submit|change)=", t):
            fail(n, "inline event handler in the markup")
    cat = TEXT["magaza.html"]
    cards = len(re.findall(r'<li class="card[ "]', cat))
    if cards < 24:
        fail("magaza.html", f"only {cards} product cards in the markup; the catalogue "
                            "must not be built by script")
    for n in ("sebet.html", "mehsul-nar-c-serumu.html"):
        if "<noscript>" not in TEXT[n]:
            fail(n, "no <noscript> route for a visitor without scripting")
    ok("no-js", f"catalogue ships {cards} cards in the HTML; cart and product pages "
                "offer a scriptless way to order")


def main() -> int:
    for check in (check_lang, check_h1, check_alt, check_meta, check_og, check_jsonld,
                  check_protocols, check_links, check_placeholders, check_sitemap,
                  check_prices, check_reachable, check_contrast, check_no_js):
        check()

    width = max(len(c) for c, _ in NOTES)
    for name, detail in NOTES:
        print(f"  \033[32m✓\033[0m {name.ljust(width)}  {detail}")
    if FAILS:
        print()
        for f in FAILS:
            print(f"  \033[31m✗\033[0m {f}")
        print(f"\n{len(FAILS)} problems across {len(TEXT)} pages")
        return 1
    print(f"\n{len(NOTES)} checks passed across {len(TEXT)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
