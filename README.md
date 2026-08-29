# Zərrə — demo e-commerce site

A static shop for an Azerbaijani skincare brand, built as a portfolio piece and a
sales demo. **The brand is fictional** — no real business's name, branding, products
or photography are used, the forms take nothing, and the site says so in its own
footer.

**Live:** https://kulieff21.github.io/ecommerce-site-demo/

24 products · 39 pages · no framework · no build step at runtime · no CDN

## The three demos

Three sales demos for Azerbaijani small businesses, deliberately different in
sector, palette **and shape** — a service site, a catalogue and a booking site —
so they read as three pieces of work rather than one template three times. Each
is a fictional business, holds itself to the same audit checklist, and ships as
static files with no framework and no CDN.

| | | |
| --- | --- | --- |
| [`cargo-site-demo`](https://github.com/kulieff21/cargo-site-demo) | Xəzər Ekspres — Courier | Tracking, tariffs and an order form — a dark, service-shaped site · [live](https://kulieff21.github.io/cargo-site-demo/) |
| `ecommerce-site-demo` **← you are here** | Zərrə — Skincare retail | 24 products, cart and checkout — a light, catalogue-shaped site |
| [`hotel-site-demo`](https://github.com/kulieff21/hotel-site-demo) | Qırx Pəncərə — Şəki guesthouse | 365 published nightly prices and a booking form — a calendar-shaped site · [live](https://kulieff21.github.io/hotel-site-demo/) |

## Why it exists

I audit small-business websites in Azerbaijan. On shops, the same faults keep coming
back: 61 of 63 product images with an empty `alt`, no `<h1>`, products that exist only
as JavaScript routes and so appear in no search result, a sitemap listing pages that
404, an email link written `mail:` so nothing opens, and product pages carrying no
structured data at all — which is why they never show a price or a star rating in
Google.

Telling a shop owner that is easier when you can show them what the alternative looks
like. This is that.

## What it does

- **24 products, each on its own static URL** with `Product` structured data —
  offer price in AZN, availability, `aggregateRating` and the individual reviews.
  Nothing is routed by script, because a shop whose products cannot be crawled has
  no organic traffic.
- **A catalogue that filters, searches and sorts** by category, skin concern and
  price, without fetching anything. The 24 cards are in the HTML; scripting only
  hides and reorders them.
- **A working cart and checkout** — `localStorage`, quantity editing, free shipping
  over 50 ₼, live totals, and forms that validate properly in Azerbaijani.
- **A share card per product.** Product links get pasted into WhatsApp constantly
  here, and chat apps do not preview SVG, so each product has its own 1200×630 PNG
  showing the product, its name and its price.
- **Light and dark**, both measured against WCAG AA.

## The signature: the tərkib kartı

Every product publishes its ingredient percentages, adding up to 100 — including the
last few per cent of emulsifier, preservative and fragrance that labels normally
bundle away. It is the brand's whole argument, so it is also its visual identity: the
same data is a full table on the product page and a five-pixel colour spine under
every card in the grid.

That constraint is enforced, not decorative — `tools/catalog.py` refuses to build if
a formula does not total 100, if a product cites an ingredient the glossary does not
define, or if the glossary lists an ingredient no product actually uses.

## The bar it is held to

`tools/audit.py` runs the same checklist I run against client sites, plus the
e-commerce items, against this repository:

| Check | |
| --- | --- |
| `<html lang="az">` | on every page |
| `<h1>` | exactly one, naming the page's subject rather than the brand |
| `alt` | on every image; missing, empty and generic counted as separate faults |
| `<title>` / meta description | present, sensible length, unique across 39 pages |
| Open Graph | all five tags, and `og:image` must be a file that exists |
| Canonical | on every page, pointing at this site |
| JSON-LD | OnlineStore, WebSite+SearchAction, ItemList, BreadcrumbList, and Product with offers + aggregateRating — parsed, not just present |
| Prices | the price on the page, in the JSON-LD offer and in the cart data must agree |
| Protocol links | `mailto:` and `tel:` well-formed; `mail:`-style typos rejected |
| Internal links | every target exists |
| Assets | every referenced file exists, and nothing is fetched from a third party |
| Placeholders | no lorem ipsum, no TODO, no leftover scaffolding |
| `robots.txt` / `sitemap.xml` | present, listing only real pages, and listing all of them |
| Crawlability | every product is a static URL linked from the catalogue markup |
| Contrast | 28 colour pairs measured in both schemes against WCAG AA |
| No-JS | the catalogue ships its cards as HTML; cart and product pages offer a scriptless way to order |

```bash
python3 tools/audit.py           # 14 checks across 39 pages; exit 1 on failure
python3 tools/audit_selftest.py  # breaks the site 15 ways and checks the audit notices
```

A checklist that only ever prints ticks is indistinguishable from one that does not
run, so `audit_selftest.py` copies the site, injects one real fault at a time — an
emptied `alt`, a `mail:` typo, a schema price that disagrees with the page, body text
dropped below AA, a catalogue emptied out as if it were script-built — and asserts
the audit fails and says why. All 15 are caught.

The audit found two things on its own first run: every page pointed `og:image` at a
file that did not exist, and the ingredient glossary listed a substance no product
contained.

## Build

Nothing is built at runtime — the site is HTML, CSS and vanilla JS, and it runs from
a folder with no server and no network.

```bash
python3 tools/build_pages.py   # all 39 pages, product drawings, data.js, robots.txt, sitemap.xml
python3 tools/og_render.py     # the 25 share cards (needs Chrome; nothing else does)
python3 tools/audit.py
```

`tools/catalog.py` is the only source of a price, a percentage or a rating. It feeds
the card, the product page, the JSON-LD offer, the cart data and the share card at
once, so the number a shopper is quoted cannot drift from the number that is
published.

## Decisions worth naming

- **The products are drawn, not photographed.** A demo shop cannot use a real brand's
  product shots, and generic cosmetics stock reads as borrowed the moment twenty-four
  of them sit in one grid. Each product is an SVG vessel — jar, dropper, tube, stick,
  compact — tinted from its own leading ingredient. Licence-clean for a public repo,
  consistent across the line, and **the entire 24-product catalogue is 28 KB**, less
  than one unoptimised product photo. That is a sales point, not a compromise.
- **No CDN, no framework.** A client should be able to take the folder and host it
  anywhere. Nothing renders on a third-party request; the audit fails the build if
  anything is fetched off-site.
- **Young Serif and Inter, self-hosted and subset**, 105 KB together. Both were
  rendered and checked for Ə ə Ğ ğ İ ı Ş ş Ç ç Ö ö Ü ü and ₼ *before* anything was
  built on them — a display face missing Ə is unusable here and silently falls back.
- **Scripting enhances, never builds.** With JS off the catalogue still lists all 24
  products, the filters degrade to the category pages, and the product page shows a
  phone number and an email instead of a cart.
- **The forms admit they are a demo.** They validate for real, in Azerbaijani, and
  then say plainly that nothing was sent. Faking a confirmation teaches a visitor to
  trust a message that is not true.
- **The reviews are consistent with the ratings they sit under.** The catalogue
  refuses to build if the printed star rating drifts from the reviews actually shown,
  or if a product claims fewer total reviews than it displays.

## Credits

Typefaces: [Young Serif](https://fonts.google.com/specimen/Young+Serif) and
[Inter](https://rsms.me/inter/) by Rasmus Andersson, both under the SIL Open Font
License 1.1. No photography is used.
