# Zərrə — demo e-commerce site

## What this is
A public portfolio piece and a sales demo: a skincare shop for the Azerbaijani market,
shown to the retail companies in `AZ-AI-Automation-Leads/companies-list.md` as "this is
what your shop could be". The brand is fictional — no real business's name, branding,
product or photography is used. The footer says so plainly, and nothing on the site
takes money or personal data.

Sibling piece: `cargo-site-demo` (courier sector, dark theme). This one is light,
retail, and catalog-shaped on purpose — two pieces, not one piece twice.

## The rule that outranks everything else
**This site must pass every item of our own audit checklist**
(`AZ-AI-Automation-Leads/site-audit-checklist.md`), plus the e-commerce items that
checklist calls out specifically. We tell clients 61 of 63 product images have an empty
`alt` — the demo cannot repeat that, or the audit report loses its standing.

Non-negotiable:
- `<html lang="az">` on every page
- Exactly one `<h1>` per page, naming the page's subject rather than the brand
- Every product image carries a meaningful `alt` that describes the product, not "image"
- Unique `<title>` and meta description per page — never copies of each other
- `og:` tags on every page (products get shared into WhatsApp; a bare URL loses the sale)
- JSON-LD, filled in and valid: Organization, WebSite+SearchAction, ItemList on the
  catalog, and **Product with offers + aggregateRating + review on every product page**
- A real `robots.txt` and `sitemap.xml` listing what actually exists
- `mailto:` and `tel:` written with the right protocol
- No placeholder content, no lorem ipsum, no dead links, no invented certification
- **Every product is its own static URL.** No JS routing. A shop whose products are not
  crawlable has no organic traffic, and that is half of what we sell.
- Content readable with JS disabled — scripts enhance, they never build the page.
  With JS off: the catalog still lists every product, filters degrade to category links,
  and the product page still shows a way to order.

## Technical
- Static HTML, CSS and vanilla JS. No framework, no build step, **no CDN** — the whole
  thing runs from a folder, because that is how it gets handed to a client.
- One stylesheet, themed with CSS custom properties. Light is the design target;
  dark follows `prefers-color-scheme` and must hold the same contrast bar.
- Product imagery is **generated SVG**, not stock photography: a vessel silhouette
  coloured from the product's own formula. Licence-clean for a public repo, consistent
  across 24 products, and the entire catalogue weighs less than one unoptimised JPEG —
  which is itself part of the pitch.
- Cart lives in `localStorage`. It is an enhancement, never a prerequisite.
- Icons are inline SVG, never emoji.
- Published with GitHub Pages.

## Language
- Every user-facing string is Azerbaijani. Correct letters: Ə ə Ç ç Ş ş Ğ ğ I ı İ i Ö ö Ü ü X x
- Code, identifiers, comments and commit messages are English.
- Currency AZN, written `24,90 ₼` (comma decimal). Dates `dd.MM.yyyy`.

## Design
- Contrast at WCAG AA or better, in both schemes — `tools/audit.py` measures it.
- 8px spacing grid. Touch targets at least 44px.
- Display face Young Serif, body Inter, both self-hosted and subset. Verified to carry
  Ə ə Ğ ğ İ ı Ş ş Ç ç Ö ö Ü ü and ₼ before anything was built on them.
- The signature is the **tərkib kartı**: every product publishes its real ingredient
  percentages as a stacked bar. It is the brand promise, the card's identity at small
  size, and the product page's core content. It is not decoration and it is not faked.
- Restrained motion, `prefers-reduced-motion` respected.

## Working notes
- Commit in small, reviewable steps.
- After each significant chunk, append one line to `LOG.md`. Terse — it exists so a later
  session can catch up in a few hundred tokens.
