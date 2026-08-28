# Log

One line per significant chunk. Newest at the bottom. Keep it terse.

- `2026-08-28` Project set up: fictional skincare brand "Zərrə", light theme, retail/catalogue shape so it is not the cargo demo re-skinned. Display face picked by rendering candidates and checking Ə/ə/₼ actually exist — Young Serif passed, 43 KB; Inter subset reused from cargo-site-demo.
- `2026-08-28` `tools/catalog.py`: 24 products, 39 ingredients, 51 reviews. It validates itself — formulas must total 100, no unknown or unused ingredients, ratings must match the reviews shown. Caught one unused glossary entry (Retinal) on the first run.
- `2026-08-28` `tools/product_art.py`: 10 vessel silhouettes, each tinted from the product's own leading ingredient. Contact-sheet review caught four faults: tubes reading as bottles (added a crimp seam), compacts reading as two floating discs (drew them open with a rim), jars too tall, and a saffron soap coming out olive-green — hence `tint_from`, for products whose identity ingredient is not their bulkiest. 28 KB for all 24.
- `2026-08-28` `tools/render.py` owns the shell and every shared component; `build_pages.py` generates all 39 pages from it, including index.html. Improvement on cargo-site-demo, where render.py had to re-parse index.html for the header.
- `2026-08-28` Signature landed: the **tərkib kartı**. Full percentage table on the product page, 5px colour spine under every card. Same data in both, from one source.
- `2026-08-28` site.js: cart in localStorage, catalogue filter/search/sort over the shipped markup, AZ form validation, reveal-on-scroll. Every storage access guarded — a shop that breaks in private mode is worse than one with no cart memory.
- `2026-08-28` `tools/audit.py`, 14 checks, and `audit_selftest.py`, which injects 15 real faults and asserts each is caught. All 15 caught. The audit found two live faults itself: og-cover.png did not exist on any page, and two titles were under 15 characters.
- `2026-08-28` Per-product share cards (`og_render.py`, Chrome): a product link in WhatsApp shows the product, its name and its price, because chat apps do not preview SVG.
- `2026-08-28` Visual review at 1440 and a true 390 phone viewport (Windows headless Chrome floors the viewport at ~504px, so phone shots go through an iframe harness). Fixed: unsized icons filling their containers, the search field refusing to shrink below min-content, the filter drawer burying products on mobile, and `hidden` losing to `display:grid` so the empty-cart message printed under a full cart.
