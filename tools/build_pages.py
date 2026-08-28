#!/usr/bin/env python3
"""Builds every page, plus data.js, robots.txt, sitemap.xml and the favicon.

Run from the project root:  python3 tools/build_pages.py

The catalogue is the single source. A price shown on a card, the price in the
JSON-LD offer, the price the cart totals and the price in the sitemap-listed
product page all come from the same number, so they cannot drift apart.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import catalog
import product_art
from catalog import CAT_NAME, CAT_SLUG, CATEGORIES, INGREDIENTS, PRODUCTS, TAGS, Product
from render import (BRAND, EMAIL, PHONE_HUMAN, PHONE_LINK, SITE, e, formula_card,
                    head, icon, money, page, product_card, product_grid, spine, stars)

ROOT = Path(__file__).resolve().parent.parent


# --- shared JSON-LD ----------------------------------------------------------
ORG = {
    "@context": "https://schema.org",
    "@type": "OnlineStore",
    "name": BRAND,
    "url": SITE,
    "logo": SITE + "assets/img/favicon.svg",
    "image": SITE + "assets/img/og-cover.png",
    "description": "Bakıda hazırlanan dəri və saç baxımı məhsulları. Hər məhsulun "
                   "tərkibi faizlə açıq yazılır.",
    "areaServed": {"@type": "Country", "name": "Azərbaycan"},
    "currenciesAccepted": "AZN",
    "paymentAccepted": "Nağd, Kart",
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+994 12 000 00 00",
        "email": EMAIL,
        "contactType": "customer service",
        "availableLanguage": ["az"],
    },
}

WEBSITE = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": BRAND,
    "url": SITE,
    "inLanguage": "az",
    "potentialAction": {
        "@type": "SearchAction",
        "target": {"@type": "EntryPoint", "urlTemplate": SITE + "magaza.html?axtaris={search_term_string}"},
        "query-input": "required name=search_term_string",
    },
}


def crumbs(trail: list[tuple[str, str]]) -> tuple[str, dict]:
    """Renders the visible breadcrumb and the matching BreadcrumbList together, so
    the two can never describe different paths."""
    items, lis = [], []
    for i, (label, href) in enumerate(trail, start=1):
        items.append({"@type": "ListItem", "position": i, "name": label,
                      "item": SITE + ("" if href == "index.html" else href)})
        lis.append(f'<li><a href="{href}">{e(label)}</a></li>' if i < len(trail)
                   else f'<li aria-current="page">{e(label)}</li>')
    nav = (f'<nav class="wrap crumbs" aria-label="Səhifə yolu"><ol>{"".join(lis)}</ol></nav>')
    return nav, {"@context": "https://schema.org", "@type": "BreadcrumbList",
                 "itemListElement": items}


def item_list(items: list[Product], name: str) -> dict:
    return {
        "@context": "https://schema.org", "@type": "ItemList", "name": name,
        "numberOfItems": len(items),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "url": SITE + p.url, "name": p.name}
            for i, p in enumerate(items, start=1)
        ],
    }


# ============================================================ home =============
def build_index() -> str:
    hero = catalog.BY_SLUG["nar-c-serumu"]
    callouts = "".join(
        f'<div class="callout"><span class="callout__dot" style="background:{INGREDIENTS[ing][0]}"></span>'
        f'<span>{e(ing)}<br><span class="muted" style="font-size:.82rem">{e(INGREDIENTS[ing][1])}</span></span>'
        f'<span class="callout__pct num">{pct}%</span></div>'
        for ing, pct in hero.hero_ingredients(3)
    )

    best = [catalog.BY_SLUG[s] for s in
            ("nar-dodaq-balzami", "zeytun-beden-sudu", "gulab-toniki", "nar-c-serumu")]
    fresh = [p for p in PRODUCTS if p.badge == "yeni"] + [catalog.BY_SLUG["bal-mumu-el-kremi"]]

    cats = "".join(
        f'<a class="cat reveal" href="kateqoriya-{slug}.html">'
        f'<div class="cat__row"><h3>{e(name)}</h3>'
        f'<span class="cat__count num">{sum(1 for p in PRODUCTS if p.cat == key)}</span></div>'
        f"<p>{e(desc)}</p></a>"
        for key, name, slug, desc in CATEGORIES
    )

    voices = []
    for slug in ("nar-dodaq-balzami", "bal-mumu-el-kremi", "gulab-toniki"):
        p = catalog.BY_SLUG[slug]
        name, star_n, text = p.voices[0]
        voices.append(
            f'<li class="voice reveal"><figure class="stack-sm">'
            f"{stars(float(star_n))}"
            f"<blockquote>“{e(text)}”</blockquote>"
            f'<figcaption>{e(name)}<br>'
            f'<span class="voice__product"><a href="{p.url}">{e(p.name)}</a></span></figcaption>'
            f"</figure></li>"
        )

    faqs = [
        ("Sifariş nə vaxt çatdırılır?",
         "Bakı daxilində saat 14:00-a qədər verilən sifarişlər həmin gün, sonrakılar "
         "növbəti gün çatdırılır. Regionlara kuryer şirkəti ilə 2–3 iş günü."),
        ("Ödənişi necə edə bilərəm?",
         "Kuryerə nağd, kuryerin terminalı ilə kartla, və ya sayt üzərindən onlayn kartla. "
         "Onlayn ödənişdə kart məlumatları bankın səhifəsində daxil edilir, sayta düşmür."),
        ("Məhsul dərimə uyğun gəlməsə nə olur?",
         "14 gün ərzində açılmamış məhsulu qaytara bilərsiniz. Açılmış məhsulda reaksiya "
         "olubsa, bizə yazın — fotosuz və izahsız geri götürürük."),
        ("Tərkibdəki faizlər həqiqətənmi dəqiqdir?",
         "Bəli, hər məhsulun səhifəsində tərkibin 100%-i sadalanır. Adətən gizlədilən son "
         "hissə — emulqator, konservant və ətir — bizdə də ayrıca sətir kimi yazılıb."),
        ("Məhsullar heyvanlar üzərində sınaqdan keçirilir?",
         "Xeyr. Nə məhsullar, nə də tərkib maddələri heyvan üzərində sınaqdan keçirilmir."),
    ]
    faq_html = "".join(
        f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faqs)
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
    }

    body = f"""
      <section class="hero">
        <div class="wrap hero__grid">
          <div class="hero__copy">
            <p class="eyebrow">Açıq tərkib</p>
            <h1>Dərinizə nə sürtdüyünüzü <em>bilirsiniz</em>.</h1>
            <p class="lede hero__lede">Hər {BRAND} məhsulunun tərkibi faizlə yazılır —
              yüzdə yüzü, sonuncu konservanta qədər. Nə var, nə qədər var, haradan gəlir.</p>
            <div class="hero__cta">
              <a class="btn btn--primary" href="magaza.html">Mağazaya keç {icon("arrow")}</a>
              <a class="btn btn--ghost" href="terkib.html">Faizləri niyə yazırıq?</a>
            </div>
          </div>
          <div class="hero__figure">
            <div class="hero__stage">
              <img src="{hero.img}" alt="{e(hero.alt)}" width="320" height="400"
                   fetchpriority="high" decoding="async">
              <div class="callouts">{callouts}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="promise">
        <div class="wrap">
          <ul class="promise__list">
            <li>{icon("truck")}<span>Bakıya eyni gün çatdırılma</span></li>
            <li>{icon("return")}<span>14 gün ərzində qaytarma</span></li>
            <li>{icon("shield")}<span>Kuryerə nağd və ya kartla ödəniş</span></li>
            <li>{icon("leaf")}<span>Heyvan üzərində sınaqdan keçirilmir</span></li>
          </ul>
        </div>
      </section>

      <section class="section">
        <div class="wrap">
          <div class="section-head">
            <p class="eyebrow">Kateqoriyalar</p>
            <h2>Nə axtarırsınız?</h2>
          </div>
          <div class="cats">{cats}</div>
        </div>
      </section>

      <section class="section" style="padding-top:0">
        <div class="wrap">
          <div class="section-head section-head--split">
            <div>
              <p class="eyebrow">Çox alınanlar</p>
              <h2>Müştərilərin təkrar aldığı dörd məhsul</h2>
            </div>
            <a class="linky" href="magaza.html">Hamısına bax {icon("arrow")}</a>
          </div>
          {product_grid(best)}
        </div>
      </section>

      <section class="explain">
        <div class="wrap section explain__grid">
          <div class="explain__copy">
            <p class="eyebrow">Tərkib kartı</p>
            <h2>“Təbii tərkibli” yazmaq asandır. Faiz yazmaq deyil.</h2>
            <p class="lede">Bir məhsulun içində 0,1% nar yağı ola bilər və etiketdə yenə
              “nar ekstraktı ilə” yazılar. Ona görə biz rəqəmi yazırıq: hansı maddə,
              nə qədər, nə üçün və haradan.</p>
            <p>Sağdakı kart <a href="{hero.url}">{e(hero.name)}</a> məhsulunundur və
              səhifədəki ilə eyni məlumatdır — reklam üçün ayrıca hazırlanmış versiya deyil.</p>
            <a class="linky" href="terkib.html">Bu qaydanı necə tətbiq edirik {icon("arrow")}</a>
          </div>
          <div class="reveal">{formula_card(hero)}</div>
        </div>
      </section>

      <section class="section">
        <div class="wrap">
          <div class="section-head section-head--split">
            <div>
              <p class="eyebrow">Yeni gələnlər</p>
              <h2>Rəfə bu ay qoyulanlar</h2>
            </div>
            <a class="linky" href="magaza.html">Bütün məhsullar {icon("arrow")}</a>
          </div>
          {product_grid(fresh)}
        </div>
      </section>

      <section class="section" style="padding-top:0">
        <div class="wrap">
          <div class="section-head">
            <p class="eyebrow">Rəylər</p>
            <h2>Alanlar nə deyir</h2>
          </div>
          <ul class="voices">{"".join(voices)}</ul>
        </div>
      </section>

      <section class="section" style="padding-top:0">
        <div class="wrap">
          <div class="section-head">
            <p class="eyebrow">Tez-tez verilən suallar</p>
            <h2>Sifarişdən əvvəl</h2>
          </div>
          <div class="faq">{faq_html}</div>
        </div>
      </section>
"""
    return page(
        slug="index.html", active="index.html",
        title=f"{BRAND} — tərkibi açıq yazılan dəri və saç baxımı | Bakı",
        desc="Bakıda hazırlanan üz, saç və bədən baxımı. Hər məhsulun tərkibi faizlə "
             "yazılır. Eyni gün çatdırılma, 14 gün qaytarma, kuryerə nağd və ya kartla ödəniş.",
        og_title=f"{BRAND} — dərinizə nə sürtdüyünüzü bilirsiniz",
        og_desc="Tərkibin yüzdə yüzü yazılır: hansı maddə, nə qədər, haradan.",
        body=body, jsonld=[ORG, WEBSITE, faq_ld],
    )


# ========================================================= catalogue ===========
def _filters(active_cat: str | None) -> str:
    cat_inputs = "".join(
        f'<label><input type="checkbox" name="kateqoriya" value="{key}"'
        f'{" checked" if key == active_cat else ""}> {e(name)}</label>'
        for key, name, _s, _d in CATEGORIES
    )
    tag_inputs = "".join(
        f'<label><input type="checkbox" name="teleb" value="{key}"> {e(label)}</label>'
        for key, label in TAGS.items() if key != "her"
    )
    cat_links = "".join(
        f'<li><a href="kateqoriya-{slug}.html">{e(name)}</a></li>'
        for _k, name, slug, _d in CATEGORIES
    )
    return f"""<details class="filters--drawer" open>
            <summary>{icon("search")} Süzgəclər</summary>
            <form class="filters" data-filters>
              <fieldset>
                <legend>Kateqoriya</legend>
                {cat_inputs}
              </fieldset>
              <fieldset>
                <legend>Dəri və saç ehtiyacı</legend>
                {tag_inputs}
              </fieldset>
              <fieldset>
                <legend>Qiymət</legend>
                <label><input type="radio" name="qiymet" value="hamisi" checked> Hamısı</label>
                <label><input type="radio" name="qiymet" value="0-20"> 20 ₼-dək</label>
                <label><input type="radio" name="qiymet" value="20-35"> 20–35 ₼</label>
                <label><input type="radio" name="qiymet" value="35-"> 35 ₼-dən yuxarı</label>
              </fieldset>
              <button class="btn btn--ghost" type="button" data-clear-filters>Süzgəcləri sıfırla</button>
              <noscript>
                <p class="muted" style="font-size:.86rem">Süzgəclər üçün brauzerdə skript
                  lazımdır. Kateqoriyalar ayrıca səhifə kimi də açılır:</p>
                <ul style="padding-inline-start:1.2rem">{cat_links}</ul>
              </noscript>
            </form>
          </details>"""


def _shop_body(items: list[Product], heading: str, lede: str, eyebrow: str,
               active_cat: str | None, crumb_html: str) -> str:
    return f"""
      {crumb_html}
      <div class="wrap section" style="padding-top:var(--s4)">
        <div class="section-head" style="margin-bottom:var(--s5)">
          <p class="eyebrow">{e(eyebrow)}</p>
          <h1>{e(heading)}</h1>
          <p class="lede">{e(lede)}</p>
        </div>
        <div class="shop">
          {_filters(active_cat)}
          <div>
            <div class="shop__bar">
              <p class="shop__count"><b data-result-count>{len(items)}</b> məhsul</p>
              <label class="field" id="axtaris">
                {icon("search")}
                <span class="vh">Məhsul adı ilə axtar</span>
                <input type="search" data-search placeholder="Məhsul adı və ya tərkib" autocomplete="off">
              </label>
              <label class="field">
                <span class="vh">Sıralama</span>
                <select data-sort>
                  <option value="secilmis">Seçilmiş sıra</option>
                  <option value="ucuz">Əvvəlcə ucuz</option>
                  <option value="baha">Əvvəlcə baha</option>
                  <option value="reyting">Reytinqə görə</option>
                </select>
              </label>
            </div>
            {product_grid(items)}
            <p class="empty" data-empty hidden>
              {icon("search")}
              <strong>Bu şərtlərə uyğun məhsul tapılmadı.</strong>
              <span class="muted">Süzgəcləri azaldın və ya axtarış sözünü dəyişin.</span>
              <button class="btn btn--ghost" type="button" data-clear-filters>Süzgəcləri sıfırla</button>
            </p>
          </div>
        </div>
      </div>
"""


def build_shop() -> str:
    nav, ld = crumbs([("Ana səhifə", "index.html"), ("Mağaza", "magaza.html")])
    body = _shop_body(
        PRODUCTS, "Bütün məhsullar",
        "24 məhsul, dördü kateqoriya. Hər birinin tərkibi öz səhifəsində faizlə yazılıb.",
        "Mağaza", None, nav)
    return page(slug="magaza.html", active="magaza.html",
                title=f"Mağaza — bütün məhsullar | {BRAND}",
                desc="Üz, saç, bədən və makiyaj məhsulları. Kateqoriya, dəri ehtiyacı və "
                     "qiymətə görə süzgəcləyin. Bakıya eyni gün çatdırılma.",
                body=body, jsonld=[item_list(PRODUCTS, "Bütün məhsullar"), ld])


def build_category(key: str, name: str, slug: str, desc: str) -> str:
    items = [p for p in PRODUCTS if p.cat == key]
    nav, ld = crumbs([("Ana səhifə", "index.html"), ("Mağaza", "magaza.html"),
                      (name, f"kateqoriya-{slug}.html")])
    body = _shop_body(items, name, desc, "Kateqoriya", key, nav)
    return page(slug=f"kateqoriya-{slug}.html", active="magaza.html",
                title=f"{name} — {len(items)} məhsul | {BRAND}",
                desc=f"{desc} {len(items)} məhsul, tərkibi faizlə açıq. "
                     f"Bakıya eyni gün çatdırılma, 14 gün qaytarma.",
                body=body, jsonld=[item_list(items, name), ld])


# =========================================================== product ===========
def build_product(p: Product) -> str:
    nav, crumb_ld = crumbs([("Ana səhifə", "index.html"), ("Mağaza", "magaza.html"),
                            (p.cat_name, f"kateqoriya-{CAT_SLUG[p.cat]}.html"), (p.name, p.url)])
    old = f'<span class="price__old num">{money(p.old)}</span>' if p.old else ""
    badge = ""
    if p.badge:
        text = {"yeni": "Yeni", "endirim": f"−{p.discount_pct}% endirim",
                "cox-satilan": "Çox alınan"}[p.badge]
        badge = f'<span class="badge badge--{p.badge}">{e(text)}</span>'

    tag_line = " · ".join(TAGS[t] for t in p.tags)
    steps = "".join(f"<li>{e(s)}</li>" for s in p.usage)
    paras = "".join(f"<p>{s}</p>" for s in p.body)

    voices = "".join(
        f'<li class="voice"><figure class="stack-sm">{stars(float(n))}'
        f"<blockquote>“{e(t)}”</blockquote><figcaption>{e(who)}</figcaption></figure></li>"
        for who, n, t in p.voices
    ) or '<li class="voice"><p class="muted">Bu məhsula hələ rəy yazılmayıb.</p></li>'

    related = [q for q in PRODUCTS if q.cat == p.cat and q.slug != p.slug][:4]

    product_ld = {
        "@context": "https://schema.org", "@type": "Product",
        "name": p.name, "sku": p.slug.upper().replace("-", "")[:16],
        "image": SITE + p.img, "description": p.lead,
        "brand": {"@type": "Brand", "name": BRAND},
        "category": p.cat_name,
        "size": p.volume,
        "offers": {
            "@type": "Offer", "url": SITE + p.url, "price": f"{p.price:.2f}",
            "priceCurrency": "AZN",
            "availability": "https://schema.org/InStock" if p.stock
                            else "https://schema.org/OutOfStock",
            "itemCondition": "https://schema.org/NewCondition",
            "priceValidUntil": "2026-12-31",
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "AZN"},
                "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "AZ"},
            },
        },
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": str(p.rating),
                            "reviewCount": str(p.reviews), "bestRating": "5", "worstRating": "1"},
        "review": [
            {"@type": "Review", "author": {"@type": "Person", "name": who},
             "reviewRating": {"@type": "Rating", "ratingValue": str(n), "bestRating": "5"},
             "reviewBody": t}
            for who, n, t in p.voices
        ],
    }
    if p.old:
        product_ld["offers"]["priceSpecification"] = {
            "@type": "UnitPriceSpecification",
            "priceType": "https://schema.org/ListPrice",
            "price": f"{p.old:.2f}", "priceCurrency": "AZN",
        }

    related_html = ""
    if related:
        related_html = f"""
      <section class="section" style="padding-top:0">
        <div class="wrap">
          <div class="section-head"><p class="eyebrow">Eyni kateqoriyadan</p>
            <h2>Bunlarla birlikdə istifadə olunur</h2></div>
          {product_grid(related)}
        </div>
      </section>"""

    body = f"""
      {nav}
      <div class="wrap pdp">
        <div class="pdp__media">{badge}
          <img src="{p.img}" alt="{e(p.alt)}" width="320" height="400"
               fetchpriority="high" decoding="async">
        </div>
        <div class="pdp__info">
          <div class="pdp__head">
            <p class="eyebrow">{e(p.cat_name)} · {e(p.kind)}</p>
            <h1>{e(p.name)}</h1>
            <p class="lede">{e(p.lead)}</p>
            <p><a class="linky" href="#reyler">{stars(p.rating, p.reviews)}</a></p>
          </div>

          <div class="pdp__price">
            <span class="price"><span class="price__now num">{money(p.price)}</span>{old}</span>
            <span class="muted">{e(p.volume)}</span>
          </div>

          <form class="pdp__buy" data-buy="{p.slug}">
            <div class="qty">
              <button type="button" data-qty="-1" aria-label="Sayı azalt">−</button>
              <input type="number" name="say" value="1" min="1" max="20" step="1"
                     inputmode="numeric" aria-label="Say">
              <button type="button" data-qty="1" aria-label="Sayı artır">+</button>
            </div>
            <button class="btn btn--primary btn--block" type="submit">
              {icon("cart")} Səbətə at
            </button>
          </form>

          <p class="pdp__note">{icon("truck")}
            <span>Bakı daxilində saat 14:00-a qədər verilən sifariş <b>bu gün</b> çatdırılır.
            50 ₼-dən yuxarı sifarişlərdə çatdırılma pulsuzdur.</span></p>
          <p class="pdp__note">{icon("return")}
            <span>Açılmamış məhsulu 14 gün ərzində qaytara bilərsiniz.
            <a href="qaytarma.html">Şərtlər</a>.</span></p>
          <p class="pdp__note">{icon("info")}
            <span>Uyğundur: {e(tag_line)}</span></p>

          <noscript>
            <p class="notice" style="font-size:.9rem">{icon("phone")}
              <span>Səbət brauzer skripti ilə işləyir. Skript sönülüdürsə,
              <a href="tel:{PHONE_LINK}">{PHONE_HUMAN}</a> nömrəsinə zəng edərək və ya
              <a href="mailto:{EMAIL}">{EMAIL}</a> ünvanına yazaraq sifariş verə bilərsiniz.</span></p>
          </noscript>
        </div>
      </div>

      <section class="section">
        <div class="wrap explain__grid">
          <div class="stack">
            <div class="section-head" style="margin-bottom:0">
              <p class="eyebrow">Tərkib kartı</p>
              <h2>İçində nə var</h2>
            </div>
            <div class="prose">{paras}</div>
            <div class="panel stack-sm">
              <h3>Necə istifadə olunur</h3>
              <ol class="steps">{steps}</ol>
            </div>
          </div>
          <div>{formula_card(p)}</div>
        </div>
      </section>

      <section class="section" style="padding-top:0" id="reyler">
        <div class="wrap">
          <div class="section-head section-head--split">
            <div><p class="eyebrow">Rəylər</p>
              <h2>{e(p.name)} haqqında</h2></div>
            <p>{stars(p.rating, p.reviews)}</p>
          </div>
          <ul class="voices">{voices}</ul>
        </div>
      </section>
      {related_html}
"""
    return page(slug=p.url, active="magaza.html",
                title=f"{p.name} — {p.volume} | {BRAND}",
                desc=f"{p.lead} {money(p.price)}. Tərkibi faizlə açıq yazılıb. "
                     f"Bakıya eyni gün çatdırılma.",
                og_title=f"{p.name} — {BRAND}", og_desc=p.lead,
                body=body, jsonld=[product_ld, crumb_ld])


# ====================================================== cart & checkout ========
def build_cart() -> str:
    nav, ld = crumbs([("Ana səhifə", "index.html"), ("Səbət", "sebet.html")])
    body = f"""
      {nav}
      <div class="wrap section" style="padding-top:var(--s4)">
        <div class="section-head"><p class="eyebrow">Sifariş</p><h1>Səbət</h1></div>

        <div class="cart" data-cart hidden>
          <ul class="cart__lines" data-cart-lines></ul>
          <aside class="panel cart__sum">
            <h2 style="font-size:1.2rem">Yekun</h2>
            <div class="cart__row"><span>Məhsullar</span>
              <span class="num" data-cart-subtotal>0,00 ₼</span></div>
            <div class="cart__row"><span>Çatdırılma (Bakı)</span>
              <span class="num" data-cart-shipping>0,00 ₼</span></div>
            <p class="muted" style="font-size:.84rem" data-cart-freehint></p>
            <div class="cart__row cart__row--total"><span>Ümumi</span>
              <span class="num" data-cart-total>0,00 ₼</span></div>
            <a class="btn btn--primary btn--block" href="odenis.html">Sifarişi tamamla {icon("arrow")}</a>
            <a class="linky" href="magaza.html">Alış-verişə davam et</a>
          </aside>
        </div>

        <div class="empty" data-cart-empty>
          {icon("cart")}
          <strong>Səbətiniz boşdur.</strong>
          <span class="muted">Mağazadan bəyəndiyinizi əlavə edin — səbət brauzerinizdə saxlanılır.</span>
          <a class="btn btn--primary" href="magaza.html">Mağazaya keç</a>
        </div>

        <noscript>
          <p class="notice">{icon("info")}
            <span><strong>Səbət skript tələb edir.</strong>
            Brauzerinizdə skript sönülüdür. Sifarişi telefonla vermək üçün
            <a href="tel:{PHONE_LINK}">{PHONE_HUMAN}</a>, yazışmaq üçün
            <a href="mailto:{EMAIL}">{EMAIL}</a>.</span></p>
        </noscript>
      </div>
"""
    return page(slug="sebet.html", title=f"Səbət | {BRAND}",
                desc="Seçdiyiniz məhsullar və yekun məbləğ. Bakı daxilində 50 ₼-dən "
                     "yuxarı sifarişlərdə çatdırılma pulsuzdur.",
                body=body, jsonld=[ld])


def build_checkout() -> str:
    nav, ld = crumbs([("Ana səhifə", "index.html"), ("Səbət", "sebet.html"),
                      ("Sifarişi tamamla", "odenis.html")])
    body = f"""
      {nav}
      <div class="wrap section" style="padding-top:var(--s4)">
        <div class="section-head"><p class="eyebrow">Addım 2 / 2</p><h1>Sifarişi tamamla</h1>
          <p class="lede">Kuryer sizinlə çatdırılmadan əvvəl əlaqə saxlayacaq.</p></div>

        <div class="cart">
          <form class="form" data-checkout novalidate>
            <div class="panel stack">
              <h2 style="font-size:1.2rem">Əlaqə</h2>
              <div class="form__row">
                <label>Ad və soyad
                  <input type="text" name="ad" autocomplete="name" required>
                  <span class="err" data-err="ad"></span></label>
                <label>Telefon
                  <input type="tel" name="telefon" autocomplete="tel"
                         placeholder="0XX XXX XX XX" required>
                  <span class="err" data-err="telefon"></span></label>
              </div>
              <label>E-poçt <span class="hint">(istəyə bağlı — sifariş təsdiqi üçün)</span>
                <input type="email" name="email" autocomplete="email">
                <span class="err" data-err="email"></span></label>
            </div>

            <div class="panel stack">
              <h2 style="font-size:1.2rem">Çatdırılma</h2>
              <label>Şəhər / rayon
                <select name="sehir" required>
                  <option value="">Seçin</option>
                  <option value="baki">Bakı</option>
                  <option value="sumqayit">Sumqayıt</option>
                  <option value="gence">Gəncə</option>
                  <option value="diger">Digər region</option>
                </select>
                <span class="err" data-err="sehir"></span></label>
              <label>Ünvan
                <textarea name="unvan" rows="3" autocomplete="street-address" required></textarea>
                <span class="err" data-err="unvan"></span></label>
              <label>Kuryerə qeyd <span class="hint">(istəyə bağlı)</span>
                <textarea name="qeyd" rows="2"></textarea></label>
            </div>

            <div class="panel stack">
              <h2 style="font-size:1.2rem">Ödəniş</h2>
              <div class="filters">
                <label><input type="radio" name="odenis" value="nagd" checked>
                  Kuryerə nağd</label>
                <label><input type="radio" name="odenis" value="terminal">
                  Kuryerin terminalı ilə kartla</label>
                <label><input type="radio" name="odenis" value="onlayn">
                  Onlayn kartla (bankın səhifəsində)</label>
              </div>
            </div>

            <button class="btn btn--primary" type="submit">Sifarişi təsdiqlə</button>
            <p class="notice" data-checkout-result hidden></p>
          </form>

          <aside class="panel cart__sum">
            <h2 style="font-size:1.2rem">Sifariş</h2>
            <ul class="cart__lines" data-cart-mini style="gap:var(--s2)"></ul>
            <div class="cart__row"><span>Məhsullar</span>
              <span class="num" data-cart-subtotal>0,00 ₼</span></div>
            <div class="cart__row"><span>Çatdırılma</span>
              <span class="num" data-cart-shipping>0,00 ₼</span></div>
            <div class="cart__row cart__row--total"><span>Ümumi</span>
              <span class="num" data-cart-total>0,00 ₼</span></div>
            <a class="linky" href="sebet.html">Səbətə qayıt</a>
          </aside>
        </div>
      </div>
"""
    return page(slug="odenis.html", title=f"Sifarişi tamamla | {BRAND}",
                desc="Çatdırılma ünvanı və ödəniş üsulu. Kuryerə nağd, terminalla kartla "
                     "və ya onlayn ödəniş.",
                body=body, jsonld=[ld])


# ==================================================== content pages ============
def _content(slug: str, title: str, desc: str, eyebrow: str, h1: str,
             lede: str, inner: str, crumb_label: str, extra_ld: list | None = None) -> str:
    nav, ld = crumbs([("Ana səhifə", "index.html"), (crumb_label, slug)])
    body = f"""
      {nav}
      <div class="wrap section" style="padding-top:var(--s4)">
        <div class="section-head"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(h1)}</h1>
          <p class="lede">{e(lede)}</p></div>
        {inner}
      </div>
"""
    return page(slug=slug, active=slug, title=title, desc=desc, body=body,
                jsonld=[ld] + (extra_ld or []))


def build_terkib() -> str:
    rows = []
    for name, (colour, role, origin) in sorted(INGREDIENTS.items()):
        used_in = [p for p in PRODUCTS if any(i == name for i, _ in p.formula)]
        chip = f'<span class="origin">{e(origin)}</span>' if origin else ""
        rows.append(
            f'<li><span class="formula__sw" style="background:{colour}"></span>'
            f'<span><span class="formula__name">{e(name)}</span>{chip}<br>'
            f'<span class="formula__role">{e(role)} · {len(used_in)} məhsulda</span></span>'
            f'<span class="formula__pct num">{max(pct for p in used_in for i, pct in p.formula if i == name)}%</span></li>'
        )
    example = catalog.BY_SLUG["gulab-toniki"]
    inner = f"""
      <div class="explain__grid" style="align-items:start">
        <div class="prose">
          <h2>Etiketdə adətən nə olur</h2>
          <p>Azərbaycanda satılan baxım məhsullarının çoxunda tərkib INCI adları ilə,
             çoxdan aza doğru sıralanır. Bu, qanuna uyğundur və faydalıdır — amma bir
             şeyi demir: <b>nə qədər</b>.</p>
          <p>“Nar ekstraktı ilə” yazan bir kremdə nar 0,1% ola bilər. Sıralamada
             sonuncudan əvvəl durar və heç kim yalan danışmamış olar.</p>
          <h2>Bizim qaydamız</h2>
          <ul>
            <li>Hər məhsulun tərkibi <b>faizlə</b> yazılır.</li>
            <li>Faizlərin cəmi <b>100</b>-dür. Yerdə qalan hissə “və digərləri” kimi
                yığılmır.</li>
            <li>Emulqator, konservant və ətir də ayrıca sətir kimi görünür — adətən
                gizlədilən hissə budur.</li>
            <li>Bilinən mənbə varsa yazılır: Göyçay, Lənkəran, Quba, Zaqatala, Qəbələ.</li>
          </ul>
          <h2>Kartı necə oxumaq lazımdır</h2>
          <p>Yuxarıdakı zolaq tərkibin faiz payını miqyasda göstərir — hansı maddənin
             həqiqətən çox olduğu bir baxışda görünür. Altındakı sətirlərdə isə hər
             maddənin nə üçün olduğu yazılıb.</p>
          <p>Su birinci sırada durursa, bu pis əlamət deyil. Krem və toniklərin əsası
             sudur; əsas sual suyun içində nə olduğudur.</p>
          <h2>Nə vəd etmirik</h2>
          <p>Faiz yazmaq məhsulun işləyəcəyinə zəmanət deyil. Dəri fərqlidir və bir
             adamda nəticə verən tərkib başqasında verməyə bilər. Bizim iddiamız yalnız
             bundan ibarətdir: aldığınız şeyin içində nə olduğunu bilirsiniz.</p>
        </div>
        <div class="stack">
          <p class="eyebrow">Nümunə: {e(example.name)}</p>
          {formula_card(example, "Bu məhsulun 74%-i gülün özündən damıdılmış sudur — "
                                 "qalan 26% yazıldığı kimidir.")}
        </div>
      </div>

      <div class="section" style="padding-bottom:0">
        <div class="section-head"><p class="eyebrow">Lüğət</p>
          <h2>İstifadə etdiyimiz {len(INGREDIENTS)} maddə</h2>
          <p class="lede">Sağdakı rəqəm həmin maddənin bir məhsulda çatdığı ən yüksək faizdir.</p></div>
        <div class="formula"><ul class="formula__rows">{"".join(rows)}</ul></div>
      </div>
"""
    return _content(
        "terkib.html", f"Tərkibi niyə faizlə yazırıq | {BRAND}",
        "Tərkib kartı nədir, necə oxunur və istifadə etdiyimiz 40 maddənin hər birinin "
        "nə işə yaradığı.",
        "Açıq tərkib", "Tərkibi niyə faizlə yazırıq",
        "Bir sətir yazmaq asandır: “təbii tərkibli”. Rəqəm yazanda geri çəkilmək olmur.",
        inner, "Tərkib")


def build_delivery() -> str:
    inner = f"""
      <div class="explain__grid" style="align-items:start">
        <div class="prose">
          <h2>Çatdırılma</h2>
          <ul>
            <li><b>Bakı:</b> saat 14:00-a qədər verilən sifariş həmin gün, sonrakılar
                növbəti gün. 4 ₼ — 50 ₼-dən yuxarı sifarişdə pulsuz.</li>
            <li><b>Sumqayıt və Abşeron:</b> 1 iş günü. 5 ₼ — 50 ₼-dən yuxarı pulsuz.</li>
            <li><b>Regionlar:</b> kuryer şirkəti ilə 2–3 iş günü. 7 ₼.</li>
          </ul>
          <p>Kuryer yola çıxmazdan əvvəl zəng edir. Cavab verilmədikdə sifariş həmin
             gün bir dəfə də təkrar edilir.</p>

          <h2>Ödəniş</h2>
          <ul>
            <li><b>Kuryerə nağd</b> — çatdırılma anında.</li>
            <li><b>Kuryerin terminalı ilə kartla</b> — bütün yerli bank kartları.</li>
            <li><b>Onlayn kartla</b> — kart məlumatları bankın öz səhifəsində daxil edilir
                və sayta düşmür.</li>
          </ul>
          <p>Qiymətlər AZN ilə göstərilir və ƏDV daxildir.</p>

          <h2>Sifarişi izləmək</h2>
          <p>Sifariş qeydə alınandan sonra telefon nömrənizə SMS gəlir. Sualınız olsa
             <a href="tel:{PHONE_LINK}">{PHONE_HUMAN}</a> nömrəsinə zəng edin —
             hər gün 09:00–20:00.</p>
        </div>
        <div class="stack">
          <div class="panel stack-sm">
            <h3>Qısa cavab</h3>
            <p class="muted">Bakıya bu gün. 50 ₼-dən yuxarı pulsuz. Nağd və ya kartla.</p>
          </div>
          <p class="notice">{icon("info")}
            <span><strong>Bu nümunə saytdır.</strong> Yuxarıdakı şərtlər real bir
            mağazanın necə yazacağını göstərmək üçündür; burada sifariş qəbul edilmir.</span></p>
        </div>
      </div>
"""
    return _content("catdirilma.html", f"Çatdırılma və ödəniş | {BRAND}",
                    "Bakıya eyni gün, regionlara 2–3 iş günü. 50 ₼-dən yuxarı sifarişdə "
                    "çatdırılma pulsuz. Nağd, terminal və onlayn kart ödənişi.",
                    "Kömək", "Çatdırılma və ödəniş",
                    "Nə vaxt gəlir, neçəyə gəlir və necə ödəyə bilərsiniz.",
                    inner, "Çatdırılma")


def build_returns() -> str:
    inner = """
      <div class="prose">
        <h2>14 gün</h2>
        <p>Açılmamış məhsulu çatdırılma tarixindən 14 gün ərzində qaytara bilərsiniz.
           Məhsul öz qablaşdırmasında və istifadə olunmamış olmalıdır.</p>

        <h2>Açılmış məhsul</h2>
        <p>Kosmetika açıldıqdan sonra adətən qaytarılmır. Bir istisna qoyuruq: məhsul
           dərinizdə reaksiya veribsə, bizə yazın. Foto və izahat tələb etmirik —
           qalan hissəsini geri götürüb məbləği qaytarırıq.</p>

        <h2>Necə qaytarılır</h2>
        <ol class="steps">
          <li>Zəng edin və ya yazın, sifariş nömrəsini deyin.</li>
          <li>Kuryer razılaşdırılan gün məhsulu ünvanınızdan götürür.</li>
          <li>Məbləğ 3–5 iş günü ərzində ödədiyiniz üsulla qaytarılır.</li>
        </ol>

        <h2>Çatdırılma haqqı</h2>
        <p>Səhv bizdədirsə (yanlış məhsul, zədəli qablaşdırma) qaytarma tam bizim
           hesabımızadır. Fikir dəyişikliyi halında yalnız kuryer haqqı sizin
           üzərinizdə qalır.</p>

        <h2>Qaytarılmayan hallar</h2>
        <ul>
          <li>Möhürü açılmış sabun və dodaq məhsulları (gigiyena səbəbi ilə).</li>
          <li>14 gündən sonra gətirilən məhsullar.</li>
          <li>Qablaşdırması itmiş və ya zədələnmiş məhsullar.</li>
        </ul>
      </div>
"""
    return _content("qaytarma.html", f"Qaytarma şərtləri | {BRAND}",
                    "Açılmamış məhsul 14 gün ərzində qaytarılır. Dəridə reaksiya olduqda "
                    "açılmış məhsul da geri götürülür.",
                    "Kömək", "Qaytarma şərtləri",
                    "Nə vaxt, necə və hansı halda geri götürürük.",
                    inner, "Qaytarma")


def build_about() -> str:
    inner = f"""
      <div class="explain__grid" style="align-items:start">
        <div class="prose">
          <h2>Necə başladı</h2>
          <p>{BRAND} 2023-cü ildə Bakıda, kiçik bir sexdə başladı. Səbəb sadə idi:
             rəfdəki məhsulların etiketini oxuyanda içində nə qədər nə olduğunu tapmaq
             mümkün deyildi.</p>
          <p>Biz də tərsini etməyi qərara aldıq — əvvəlcə rəqəmi yazırıq, sonra məhsulu
             ona uyğun qururuq. Bu, bəzi məhsulların rəfə çıxmamasına səbəb oldu, çünki
             faizi yazanda öz-özünə görünür ki, içində iddia ediləcək bir şey yoxdur.</p>

          <h2>Harada hazırlanır</h2>
          <p>İstehsal Bakıdadır. Xammalın bir hissəsi ölkə daxilindən gəlir: nar toxumu
             Göyçaydan, çay Lənkərandan, fındıq Zaqataladan, palıd qabığı Qəbələdən.
             Laboratoriya maddələri (niasinamid, hialuron turşusu, ceramid) idxaldır və
             bunu gizlətmirik — “tam təbii” demirik.</p>

          <h2>Nə etmirik</h2>
          <ul>
            <li>Heyvan üzərində sınaq keçirmirik.</li>
            <li>Məhsulun müalicə etdiyini iddia etmirik. Kosmetika dərmanın yerini tutmur.</li>
            <li>“Əvvəl / sonra” fotoları istifadə etmirik. Onları hazırlamaq işıqla
                bir dəqiqəlik işdir.</li>
          </ul>
        </div>
        <div class="stack">
          <div class="panel stack-sm">
            <h3>Rəqəmlərlə</h3>
            <ul style="list-style:none;padding:0;display:grid;gap:var(--s3)">
              <li><b class="num" style="font-size:1.6rem">{len(PRODUCTS)}</b><br>
                <span class="muted">məhsul, {len(CATEGORIES)} kateqoriyada</span></li>
              <li><b class="num" style="font-size:1.6rem">{len(INGREDIENTS)}</b><br>
                <span class="muted">istifadə olunan maddə, hamısı yazılıb</span></li>
              <li><b class="num" style="font-size:1.6rem">100%</b><br>
                <span class="muted">tərkibin açıqlanan payı</span></li>
            </ul>
          </div>
          <p class="notice">{icon("info")}
            <span><strong>Bu bir nümunə saytdır.</strong> {BRAND} mövcud şirkət deyil;
            yuxarıdakı hekayə bir brendin öz səhifəsini necə yazacağını göstərmək üçün
            hazırlanıb.</span></p>
        </div>
      </div>
"""
    return _content("haqqimizda.html", f"Haqqımızda | {BRAND}",
                    f"{BRAND} Bakıda hazırlanan baxım məhsulları brendidir. Tərkibi faizlə "
                    "yazırıq, heyvan üzərində sınaq keçirmirik.",
                    "Haqqımızda", "Rəqəmi əvvəl yazırıq",
                    "Kiçik bir sex, açıq bir qayda və rəfə çıxmayan bir neçə məhsul.",
                    inner, "Haqqımızda")


def build_contact() -> str:
    inner = f"""
      <div class="explain__grid" style="align-items:start">
        <form class="form" data-contact novalidate>
          <div class="panel stack">
            <h2 style="font-size:1.2rem">Yazın</h2>
            <div class="form__row">
              <label>Adınız
                <input type="text" name="ad" autocomplete="name" required>
                <span class="err" data-err="ad"></span></label>
              <label>Telefon və ya e-poçt
                <input type="text" name="elaqe" required>
                <span class="err" data-err="elaqe"></span></label>
            </div>
            <label>Mövzu
              <select name="movzu">
                <option>Məhsul haqqında sual</option>
                <option>Sifarişim haqqında</option>
                <option>Qaytarma</option>
                <option>Əməkdaşlıq</option>
              </select></label>
            <label>Mesaj
              <textarea name="mesaj" rows="5" required></textarea>
              <span class="err" data-err="mesaj"></span></label>
            <button class="btn btn--primary" type="submit">Göndər</button>
            <p class="notice" data-contact-result hidden></p>
          </div>
        </form>
        <div class="stack">
          <div class="panel stack-sm">
            <h3>Birbaşa əlaqə</h3>
            <p><a class="linky" href="tel:{PHONE_LINK}">{icon("phone")} {PHONE_HUMAN}</a></p>
            <p><a class="linky" href="mailto:{EMAIL}">{icon("mail")} {EMAIL}</a></p>
            <p class="muted">Hər gün 09:00–20:00<br>Bakı, Azərbaycan</p>
          </div>
          <div class="panel stack-sm">
            <h3>Tez-tez soruşulanlar</h3>
            <p class="muted">Çatdırılma və ödəniş sualları çox vaxt
              <a href="catdirilma.html">bu səhifədə</a>, qaytarma isə
              <a href="qaytarma.html">burada</a> cavablanır.</p>
          </div>
          <p class="notice">{icon("info")}
            <span><strong>Forma nümunədir.</strong> Göndər düyməsi məlumatı heç yerə
            göndərmir və heç nə saxlanılmır.</span></p>
        </div>
      </div>
"""
    return _content("elaqe.html", f"Əlaqə | {BRAND}",
                    f"{BRAND} ilə əlaqə: telefon, e-poçt və mesaj forması. "
                    "Hər gün 09:00–20:00.",
                    "Əlaqə", "Sualınız varsa yazın",
                    "Telefonla, e-poçtla və ya aşağıdakı forma ilə.",
                    inner, "Əlaqə")


def build_privacy() -> str:
    inner = f"""
      <div class="prose">
        <p class="notice">{icon("info")}
          <span><strong>Bu sayt bir nümunə işidir.</strong> Server yoxdur, forma heç nə
          göndərmir, heç bir məlumat toplanmır və ötürülmür. Aşağıdakı mətn real bir
          mağazanın bu səhifəni necə yazacağını göstərir.</span></p>

        <h2>Brauzerinizdə saxlanılan yeganə şey</h2>
        <p>Səbətə əlavə etdiyiniz məhsullar <b>localStorage</b> vasitəsilə sizin öz
           brauzerinizdə saxlanılır. Bu məlumat bizə göndərilmir və başqa saytlar tərəfindən
           oxuna bilməz. Brauzerin məlumatlarını təmizlədikdə səbət də silinir.</p>

        <h2>İzləyici yoxdur</h2>
        <p>Saytda analitika skripti, reklam pikseli və ya üçüncü tərəf kuki yoxdur.
           Şriftlər, şəkillər və skriptlər saytın öz ünvanından yüklənir — heç bir
           xarici serverə sorğu getmir.</p>

        <h2>Real mağaza olsaydı</h2>
        <ul>
          <li>Sifariş üçün ad, telefon və ünvan toplanardı — yalnız çatdırılma üçün.</li>
          <li>Kart məlumatları bankın səhifəsində daxil edilər, mağazaya heç vaxt düşməzdi.</li>
          <li>Məlumatlarınızın silinməsini istəmək hüququnuz olardı.</li>
          <li>Sifariş tarixçəsi mühasibat tələbi qədər saxlanılardı.</li>
        </ul>

        <h2>Sual</h2>
        <p>Bu səhifə ilə bağlı sualınız üçün <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </div>
"""
    return _content("mexfilik.html", f"Məxfilik siyasəti | {BRAND}",
                    "Bu nümunə saytda heç bir məlumat toplanmır. Səbət yalnız sizin "
                    "brauzerinizdə saxlanılır, izləyici skript yoxdur.",
                    "Hüquqi", "Məxfilik siyasəti",
                    "Nə toplanır, nə toplanmır və niyə.", inner, "Məxfilik")


def build_404() -> str:
    picks = [catalog.BY_SLUG[s] for s in
             ("gulab-toniki", "nar-dodaq-balzami", "zeytun-beden-sudu", "bal-mumu-el-kremi")]
    body = f"""
      <div class="wrap section">
        <div class="section-head center" style="margin-inline:auto;text-align:center">
          <p class="eyebrow" style="justify-content:center">Səhifə tapılmadı</p>
          <h1>Bu ünvanda bir şey yoxdur</h1>
          <p class="lede">Axtardığınız səhifə silinmiş və ya ünvanı dəyişmiş ola bilər.
            Aşağıdakılar çox axtarılanlardır.</p>
          <p class="row" style="justify-content:center">
            <a class="btn btn--primary" href="magaza.html">Mağazaya keç</a>
            <a class="btn btn--ghost" href="index.html">Ana səhifə</a>
          </p>
        </div>
        {product_grid(picks)}
      </div>
"""
    return page(slug="404.html", title=f"Səhifə tapılmadı | {BRAND}",
                desc="Axtardığınız səhifə mövcud deyil. Mağazadan davam edin.",
                body=body)


# ================================================= assets & site files =========
FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <rect width="24" height="24" rx="5" fill="#75182f"/>
  <circle cx="12" cy="12" r="6.6" fill="none" stroke="#f6efe9" stroke-width="2.1"/>
  <circle cx="14.3" cy="9.6" r="2" fill="#f6efe9"/>
</svg>
"""


def build_data_js() -> str:
    """What the cart needs to redraw a line from nothing but a slug. Prices live here
    once; the page markup and this file are generated from the same catalogue."""
    data = {
        p.slug: {"ad": p.name, "qiymet": p.price, "sekil": p.img, "hecm": p.volume,
                 "unvan": p.url, "alt": p.alt}
        for p in PRODUCTS
    }
    return ("/* Generated by tools/build_pages.py -- do not edit by hand. */\n"
            "window.ZERRE = {\n"
            '  pulsuzHedd: 50,           /* free shipping above this, in AZN */\n'
            '  catdirilma: { baki: 4, sumqayit: 5, gence: 6, diger: 7 },\n'
            "  mehsullar: " + json.dumps(data, ensure_ascii=False, indent=2)
            .replace("\n", "\n  ") + "\n};\n")


def build_sitemap(pages: list[str]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">']
    out[1] = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for slug in pages:
        if slug == "404.html":
            continue
        url = SITE + ("" if slug == "index.html" else slug)
        prio = "1.0" if slug == "index.html" else ("0.8" if slug.startswith(("mehsul-", "kateqoriya-", "magaza")) else "0.5")
        out.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>2026-08-28</lastmod>\n"
                   f"    <priority>{prio}</priority>\n  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


ROBOTS = f"""User-agent: *
Allow: /

# The cart and the checkout are per-visitor states, not pages worth indexing.
Disallow: /sebet.html
Disallow: /odenis.html

Sitemap: {SITE}sitemap.xml
"""


# ================================================================ main =========
def main() -> int:
    problems = catalog.validate()
    if problems:
        for msg in problems:
            print("  ✗", msg)
        print("catalogue is not sound -- nothing was written")
        return 1

    pages: dict[str, str] = {"index.html": build_index(), "magaza.html": build_shop()}
    for key, name, slug, desc in CATEGORIES:
        pages[f"kateqoriya-{slug}.html"] = build_category(key, name, slug, desc)
    for p in PRODUCTS:
        pages[p.url] = build_product(p)
    pages["sebet.html"] = build_cart()
    pages["odenis.html"] = build_checkout()
    pages["terkib.html"] = build_terkib()
    pages["catdirilma.html"] = build_delivery()
    pages["qaytarma.html"] = build_returns()
    pages["haqqimizda.html"] = build_about()
    pages["elaqe.html"] = build_contact()
    pages["mexfilik.html"] = build_privacy()
    pages["404.html"] = build_404()

    total = 0
    for slug, html_text in pages.items():
        (ROOT / slug).write_text(html_text, encoding="utf-8")
        total += len(html_text.encode())

    art = product_art.build(ROOT)
    (ROOT / "assets" / "img" / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "js" / "data.js").write_text(build_data_js(), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(list(pages)), encoding="utf-8")
    (ROOT / "robots.txt").write_text(ROBOTS, encoding="utf-8")

    print(f"{len(pages)} pages  {total / 1024:.0f} KB")
    print(f"{len(PRODUCTS)} product drawings  {art / 1024:.0f} KB")
    print(f"sitemap.xml lists {len(pages) - 1} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
