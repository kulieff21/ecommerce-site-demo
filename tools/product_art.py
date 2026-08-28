#!/usr/bin/env python3
"""Draws every product as an SVG.

A demo shop cannot use a real brand's product photography, and generic cosmetics
stock shots read as borrowed the moment you put twenty-four of them in a grid. So
each product is drawn instead: a vessel silhouette chosen by container type, filled
with the colour of the product's own dominant ingredient. The catalogue is the
single input, which is why nothing here needs a colour picked by hand.

Output: assets/img/products/<slug>.svg, about 1.5 KB each.
"""

from __future__ import annotations

from pathlib import Path

from catalog import INGREDIENTS, PRODUCTS, Product

W, H = 320, 400


# --- colour helpers ----------------------------------------------------------
def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def shade(c: str, amount: float) -> str:
    """amount < 0 darkens, > 0 lightens. Kept linear on purpose: the vessels are
    flat shapes, and eased shading would fight the flatness."""
    r, g, b = _hex(c)
    if amount >= 0:
        r, g, b = (int(v + (255 - v) * amount) for v in (r, g, b))
    else:
        r, g, b = (int(v * (1 + amount)) for v in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


def palette(p: Product) -> dict[str, str]:
    """The content colour is the product's leading active, not a decorative pick."""
    lead = p.tint_from or p.hero_ingredients(1)[0][0]
    tint = INGREDIENTS[lead][0]
    return {
        "tint": tint,
        "tint_dark": shade(tint, -0.28),
        "tint_light": shade(tint, 0.34),
        "cap": shade(tint, -0.46),
        "cap_light": shade(tint, -0.30),
        "label": "#F7F6F1",
        "label_line": shade(tint, -0.15),
    }


# --- shared parts ------------------------------------------------------------
def ground() -> str:
    return ('<ellipse cx="160" cy="368" rx="104" ry="13" fill="#000" opacity=".07"/>')


def label(x: int, y: int, w: int, h: int, c: dict[str, str], lines: int = 3) -> str:
    """A product label at thumbnail size is texture, not text. Drawing rules rather
    than setting type keeps the SVG font-independent -- an <img> cannot load the
    page's webfont, so real text here would render in whatever serif the OS supplies."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
           f'fill="{c["label"]}" opacity=".93"/>']
    cx = x + w / 2
    mark_y = y + 16
    out.append(f'<circle cx="{cx:.0f}" cy="{mark_y}" r="7" fill="none" '
               f'stroke="{c["label_line"]}" stroke-width="2"/>')
    out.append(f'<rect x="{cx - 3:.0f}" y="{mark_y - 1}" width="6" height="2" '
               f'fill="{c["label_line"]}"/>')
    for i in range(lines):
        lw = w * (0.62 if i == 0 else 0.40 if i == 1 else 0.26)
        ly = mark_y + 18 + i * 9
        out.append(f'<rect x="{cx - lw / 2:.1f}" y="{ly}" width="{lw:.1f}" height="3" '
                   f'rx="1.5" fill="{c["label_line"]}" opacity="{0.85 - i * 0.2:.2f}"/>')
    return "".join(out)


def gloss(x: float, y: float, w: float, h: float) -> str:
    """One highlight down the left third. Glass reads as glass with a single stripe."""
    return (f'<rect x="{x + w * 0.12:.1f}" y="{y + h * 0.06:.1f}" width="{w * 0.13:.1f}" '
            f'height="{h * 0.72:.1f}" rx="{w * 0.065:.1f}" fill="#fff" opacity=".22"/>')


# --- vessels -----------------------------------------------------------------
def v_dropper(c):
    return (f'<rect x="136" y="46" width="48" height="62" rx="9" fill="{c["cap"]}"/>'
            f'<rect x="130" y="102" width="60" height="20" rx="4" fill="{c["cap_light"]}"/>'
            f'<rect x="142" y="118" width="36" height="26" fill="{c["tint_dark"]}"/>'
            f'<rect x="110" y="140" width="100" height="204" rx="12" fill="{c["tint"]}"/>'
            f'<rect x="110" y="140" width="100" height="30" rx="12" fill="{c["tint_light"]}" opacity=".5"/>'
            + gloss(110, 140, 100, 204)
            + label(122, 196, 76, 100, c))


def v_jar(c):
    return (f'<rect x="76" y="122" width="168" height="52" rx="10" fill="{c["cap"]}"/>'
            f'<rect x="76" y="160" width="168" height="14" fill="{c["cap_light"]}"/>'
            f'<rect x="88" y="174" width="144" height="132" rx="16" fill="{c["tint"]}"/>'
            f'<rect x="88" y="174" width="144" height="24" fill="{c["tint_light"]}" opacity=".45"/>'
            + gloss(88, 174, 144, 132)
            + label(122, 206, 76, 76, c, lines=2))


def v_pump(c):
    return (f'<rect x="150" y="34" width="20" height="40" rx="4" fill="{c["cap"]}"/>'
            f'<rect x="126" y="60" width="68" height="20" rx="8" fill="{c["cap"]}"/>'
            f'<rect x="120" y="76" width="80" height="14" rx="4" fill="{c["cap_light"]}"/>'
            f'<rect x="146" y="88" width="28" height="34" fill="{c["tint_dark"]}"/>'
            f'<rect x="104" y="118" width="112" height="226" rx="16" fill="{c["tint"]}"/>'
            f'<rect x="104" y="118" width="112" height="30" rx="16" fill="{c["tint_light"]}" opacity=".45"/>'
            + gloss(104, 118, 112, 226)
            + label(118, 178, 84, 112, c))


def v_tube(c):
    # Crimp seam: the flattened, serrated end is what says "tube" rather than "bottle".
    teeth = "".join(f'<rect x="{x}" y="322" width="3" height="18" fill="#000" opacity=".13"/>'
                    for x in range(112, 208, 11))
    return (f'<rect x="140" y="44" width="40" height="34" rx="5" fill="{c["cap"]}"/>'
            f'<rect x="136" y="76" width="48" height="10" rx="3" fill="{c["cap_light"]}"/>'
            f'<path d="M152 86 h16 q46 10 46 62 v168 q0 6 -8 6 h-100 q-8 0 -8 -6 V148 '
            f'q0 -52 46 -62 Z" fill="{c["tint"]}"/>'
            f'<path d="M152 86 h16 q46 10 46 62 h-108 q0 -52 46 -62 Z" '
            f'fill="{c["tint_light"]}" opacity=".45"/>'
            + gloss(112, 150, 96, 150)
            + label(126, 196, 68, 98, c)
            + f'<rect x="106" y="316" width="108" height="26" rx="4" fill="{c["tint_dark"]}"/>'
            + teeth)


def v_mist(c):
    return (f'<rect x="140" y="40" width="40" height="50" rx="5" fill="{c["cap"]}"/>'
            f'<rect x="122" y="56" width="20" height="12" rx="3" fill="{c["cap_light"]}"/>'
            f'<rect x="132" y="88" width="56" height="18" rx="4" fill="{c["cap_light"]}"/>'
            f'<rect x="148" y="104" width="24" height="26" fill="{c["tint_dark"]}"/>'
            f'<rect x="106" y="126" width="108" height="218" rx="10" fill="{c["tint"]}"/>'
            f'<rect x="106" y="126" width="108" height="28" fill="{c["tint_light"]}" opacity=".45"/>'
            + gloss(106, 126, 108, 218)
            + label(120, 184, 80, 106, c))


def v_bar(c):
    return (f'<rect x="66" y="152" width="188" height="132" rx="26" fill="{c["tint"]}"/>'
            f'<rect x="66" y="152" width="188" height="26" rx="26" fill="{c["tint_light"]}" opacity=".5"/>'
            f'<rect x="66" y="188" width="188" height="56" fill="{c["label"]}" opacity=".93"/>'
            f'<circle cx="160" cy="208" r="8" fill="none" stroke="{c["label_line"]}" stroke-width="2"/>'
            f'<rect x="157" y="207" width="6" height="2" fill="{c["label_line"]}"/>'
            f'<rect x="126" y="226" width="68" height="3" rx="1.5" fill="{c["label_line"]}" opacity=".85"/>')


def v_flacon(c):
    return (f'<rect x="140" y="58" width="40" height="38" rx="4" fill="{c["cap"]}"/>'
            f'<rect x="146" y="94" width="28" height="36" fill="{c["tint_dark"]}"/>'
            f'<path d="M146 130 q-38 18 -38 56 v122 q0 20 20 20 h64 q20 0 20 -20 V186 '
            f'q0 -38 -38 -56 Z" fill="{c["tint"]}"/>'
            + gloss(112, 150, 96, 150)
            + label(124, 208, 72, 88, c))


def v_stick(c):
    return (f'<rect x="132" y="72" width="56" height="102" rx="9" fill="{c["cap"]}"/>'
            f'<rect x="132" y="164" width="56" height="12" fill="{c["cap_light"]}"/>'
            f'<rect x="134" y="176" width="52" height="164" rx="7" fill="{c["tint"]}"/>'
            f'<rect x="134" y="176" width="52" height="18" fill="{c["tint_light"]}" opacity=".5"/>'
            f'<rect x="134" y="326" width="52" height="14" rx="4" fill="{c["tint_dark"]}"/>'
            + label(140, 208, 40, 84, c, lines=2))


def v_compact(c):
    # Drawn open: lid tipped back with its mirror, pan in front. Closed, a compact is
    # a featureless disc and the product's own colour never shows.
    return (f'<ellipse cx="160" cy="132" rx="94" ry="46" fill="{c["cap"]}"/>'
            f'<ellipse cx="160" cy="132" rx="76" ry="34" fill="#EDF1EE"/>'
            f'<path d="M124 126 q26 -16 58 -12" stroke="#fff" stroke-width="5" '
            f'fill="none" opacity=".7" stroke-linecap="round"/>'
            f'<rect x="140" y="172" width="40" height="18" rx="4" fill="{c["cap"]}"/>'
            f'<path d="M66 256 v22 q0 8 12 12 a200 40 0 0 0 164 0 q12 -4 12 -12 v-22 Z" '
            f'fill="{c["cap"]}"/>'
            f'<ellipse cx="160" cy="256" rx="94" ry="46" fill="{c["cap_light"]}"/>'
            f'<ellipse cx="160" cy="256" rx="76" ry="35" fill="{c["tint_dark"]}"/>'
            f'<ellipse cx="160" cy="254" rx="71" ry="31" fill="{c["tint"]}"/>'
            f'<ellipse cx="136" cy="244" rx="24" ry="10" fill="#fff" opacity=".20"/>')


def v_pencil(c):
    return (f'<rect x="138" y="56" width="44" height="16" rx="4" fill="{c["cap"]}"/>'
            f'<rect x="138" y="72" width="44" height="200" fill="{c["tint_light"]}"/>'
            f'<rect x="138" y="72" width="13" height="200" fill="#fff" opacity=".28"/>'
            f'<rect x="169" y="72" width="13" height="200" fill="#000" opacity=".08"/>'
            f'<path d="M138 272 h44 l-14 52 h-16 Z" fill="{shade(c["tint_light"], .22)}"/>'
            f'<path d="M152 324 h16 l-8 26 Z" fill="{c["cap"]}"/>'
            f'<rect x="138" y="150" width="44" height="46" fill="{c["label"]}" opacity=".93"/>'
            f'<circle cx="160" cy="164" r="6" fill="none" stroke="{c["label_line"]}" stroke-width="2"/>'
            f'<rect x="157" y="163" width="6" height="2" fill="{c["label_line"]}"/>'
            f'<rect x="146" y="180" width="28" height="3" rx="1.5" fill="{c["label_line"]}" opacity=".8"/>')


VESSELS = {
    "dropper": v_dropper, "jar": v_jar, "pump": v_pump, "tube": v_tube,
    "mist": v_mist, "bar": v_bar, "flacon": v_flacon, "stick": v_stick,
    "compact": v_compact, "pencil": v_pencil,
}


def svg_for(p: Product) -> str:
    c = palette(p)
    body = VESSELS[p.vessel](c)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-labelledby="t">'
        f'<title id="t">{p.name} — {p.volume}</title>'
        f'{ground()}{body}</svg>\n'
    )


def build(root: Path) -> int:
    out = root / "assets" / "img" / "products"
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for p in PRODUCTS:
        data = svg_for(p)
        (out / f"{p.slug}.svg").write_text(data, encoding="utf-8")
        total += len(data.encode())
    return total


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    total = build(root)
    print(f"{len(PRODUCTS)} product drawings, {total / 1024:.1f} KB total "
          f"({total / len(PRODUCTS) / 1024:.1f} KB each)")
