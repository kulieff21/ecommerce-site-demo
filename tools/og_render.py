#!/usr/bin/env python3
"""Renders the share cards with headless Chrome.

Product links get pasted into WhatsApp constantly in this market, and a link with
no image is a link nobody taps. Chat apps do not render SVG previews, so each
product's drawing is composed onto a 1200x630 card and saved as PNG: the product,
its name, its size and its price.

    python3 tools/og_render.py            # 1 cover + 24 product cards

Chrome is only needed here. The site itself never depends on it, and if Chrome is
missing this exits with a message rather than half a set of images.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from catalog import PRODUCTS
from render import BRAND, money

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "og"

CHROME_CANDIDATES = [
    os.environ.get("CHROME"),
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    shutil.which("google-chrome"), shutil.which("chromium"),
    shutil.which("chromium-browser"), shutil.which("chrome"),
]


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def win_path(p: Path) -> str:
    """Chrome on this machine is the Windows build driven from WSL, so it needs a
    Windows path. Anywhere else, the POSIX path is already right."""
    s = str(p)
    m = re.match(r"^/mnt/([a-z])/(.*)$", s)
    if m:
        return f"{m.group(1).upper()}:\\" + m.group(2).replace("/", "\\")
    return s


CARD = """<!doctype html><html lang="az"><head><meta charset="utf-8"><style>
@font-face {{ font-family:"Young Serif"; src:url("FONTS/youngserif-latin.woff2") format("woff2");
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+2000-206F,U+20AC,U+2122; }}
@font-face {{ font-family:"Young Serif"; src:url("FONTS/youngserif-latin-ext.woff2") format("woff2");
  unicode-range:U+0100-02BA,U+1E00-1E9F,U+20A0-20AB,U+20AD-20C0,U+2C60-2C7F,U+A720-A7FF; }}
@font-face {{ font-family:"Inter"; src:url("FONTS/inter-var.woff2") format("woff2"); font-weight:100 900; }}
* {{ margin:0; box-sizing:border-box; }}
body {{ width:1200px; height:630px; background:#e9ede6; color:#171a16;
  font-family:Inter,sans-serif; display:grid; grid-template-columns:1fr 470px;
  align-items:center; gap:56px; padding:64px; overflow:hidden; }}
.brand {{ display:flex; align-items:center; gap:12px; font-family:"Young Serif",serif;
  font-size:34px; margin-bottom:28px; }}
.brand svg {{ width:30px; height:30px; color:#75182f; }}
.eyebrow {{ display:flex; align-items:center; gap:12px; font-size:16px; font-weight:600;
  letter-spacing:.16em; text-transform:uppercase; color:#5c6558; margin-bottom:20px; }}
.eyebrow::before {{ content:""; width:30px; height:2px; background:#75182f; }}
h1 {{ font-family:"Young Serif",serif; font-weight:400; font-size:{size}px; line-height:1.04;
  letter-spacing:-.015em; }}
.sub {{ margin-top:22px; font-size:23px; color:#414a3e; line-height:1.45; }}
.price {{ margin-top:30px; font-size:40px; font-weight:700; font-variant-numeric:tabular-nums; }}
.stage {{ background:#dee4da; border-radius:999px 999px 0 0; height:502px;
  display:grid; justify-items:center; align-content:center; padding:0 40px; position:relative; }}
.stage img {{ width:270px; }}
.spine {{ position:absolute; left:0; right:0; bottom:0; height:14px; display:flex; }}
.spine span {{ display:block; }}
.foot {{ position:absolute; left:64px; bottom:34px; font-size:17px; color:#5c6558; }}
</style></head><body>
<div>
  <div class="brand"><svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="9.1" fill="none" stroke="currentColor" stroke-width="1.9"/>
    <circle cx="15.1" cy="8.9" r="2.6" fill="currentColor"/></svg>{brand}</div>
  <p class="eyebrow">{eyebrow}</p>
  <h1>{title}</h1>
  <p class="sub">{sub}</p>
  {price}
</div>
<div class="stage"><img src="{img}" alt="">{spine}</div>
<p class="foot">{foot}</p>
</body></html>
"""


def spine_html(product) -> str:
    from catalog import INGREDIENTS
    parts = "".join(f'<span style="flex:{pct};background:{INGREDIENTS[i][0]}"></span>'
                    for i, pct in product.formula)
    return f'<div class="spine">{parts}</div>'


def render(chrome: str, html: str, out: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=str(ROOT / "tools"),
                                     delete=False, encoding="utf-8") as fh:
        fh.write(html)
        tmp = Path(fh.name)
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--window-size=1200,630",
             "--virtual-time-budget=6000", "--blink-settings=preferredColorScheme=1",
             f"--screenshot={win_path(out)}", "file:///" + win_path(tmp).replace("\\", "/")],
            check=True, capture_output=True, timeout=90)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    chrome = find_chrome()
    if not chrome:
        print("og_render.py: no Chrome found. Set CHROME=/path/to/chrome and re-run.")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    fonts = win_path(ROOT / "assets" / "fonts").replace("\\", "/")
    hero = PRODUCTS[0]

    cover = CARD.format(
        brand=BRAND, size=62,
        eyebrow="Açıq tərkib",
        title="Dərinizə nə sürtdüyünüzü bilirsiniz.",
        sub="Hər məhsulun tərkibi faizlə yazılır — yüzdə yüzü, sonuncu konservanta qədər.",
        price="", img=win_path(ROOT / hero.img).replace("\\", "/"),
        spine=spine_html(hero), foot="zerre.az — nümunə layihə",
    ).replace("FONTS", fonts)
    render(chrome, cover, ROOT / "assets" / "img" / "og-cover.png")
    print("  og-cover.png")

    for p in PRODUCTS:
        size = 58 if len(p.name) < 20 else 48
        card = CARD.format(
            brand=BRAND, size=size,
            eyebrow=f"{p.cat_name} · {p.kind}",
            title=p.name,
            sub=p.lead,
            price=f'<p class="price">{money(p.price)} · {p.volume}</p>',
            img=win_path(ROOT / p.img).replace("\\", "/"),
            spine=spine_html(p), foot="Tərkibi faizlə açıq yazılıb",
        ).replace("FONTS", fonts)
        render(chrome, card, OUT / f"{p.slug}.png")
    total = sum(f.stat().st_size for f in OUT.glob("*.png"))
    cover_size = (ROOT / "assets" / "img" / "og-cover.png").stat().st_size
    print(f"  {len(PRODUCTS)} product share cards, {total / 1024:.0f} KB "
          f"({total / len(PRODUCTS) / 1024:.0f} KB each); cover {cover_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
