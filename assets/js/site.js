/* Zərrə — every behaviour on the site.
 *
 * Ground rule: the page is already complete when this file runs. Nothing here
 * builds content, and with scripting off the catalogue still lists every product,
 * the filters degrade to the category pages, and the product page still shows a
 * way to order. This file only makes those things faster.
 */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };
  var DATA = window.ZERRE || { mehsullar: {}, catdirilma: { baki: 4 }, pulsuzHedd: 50 };
  var KEY = "zerre.sebet.v1";

  function manat(v) {
    return v.toFixed(2).replace(".", ",") + " ₼";
  }

  /* --- Cart state ---------------------------------------------------------
   * Lives in localStorage, which can throw in private mode or when a browser is
   * set to block site data. Every access is guarded: a shop that breaks when
   * storage is unavailable is worse than a shop with no cart memory at all. */
  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (err) {
      return {};
    }
  }

  function write(cart) {
    try {
      localStorage.setItem(KEY, JSON.stringify(cart));
    } catch (err) { /* session-only cart; nothing else to do about it */ }
    paint();
  }

  function count(cart) {
    return Object.keys(cart).reduce(function (n, k) { return n + cart[k]; }, 0);
  }

  function subtotal(cart) {
    return Object.keys(cart).reduce(function (sum, slug) {
      var item = DATA.mehsullar[slug];
      return item ? sum + item.qiymet * cart[slug] : sum;
    }, 0);
  }

  function shipping(sum, city) {
    if (sum <= 0) return 0;
    if (sum >= DATA.pulsuzHedd) return 0;
    return DATA.catdirilma[city || "baki"] || DATA.catdirilma.baki;
  }

  function add(slug, qty) {
    var cart = read();
    cart[slug] = Math.min((cart[slug] || 0) + (qty || 1), 20);
    write(cart);
    return cart[slug];
  }

  function setQty(slug, qty) {
    var cart = read();
    if (qty <= 0) delete cart[slug]; else cart[slug] = Math.min(qty, 20);
    write(cart);
  }

  /* --- Header badge -------------------------------------------------------- */
  function paintBadge() {
    var n = count(read());
    $$("[data-cart-count]").forEach(function (el) {
      el.hidden = n === 0;
      if (el.textContent !== String(n)) {
        el.textContent = n;
        el.classList.remove("is-bumped");
        void el.offsetWidth;                     /* restart the animation */
        el.classList.add("is-bumped");
      }
      var link = el.closest("a");
      if (link) {
        link.setAttribute("aria-label", n ? "Səbət — " + n + " məhsul" : "Səbət (boş)");
      }
    });
  }

  /* --- Toast --------------------------------------------------------------- */
  var toastTimer;
  function toast(message, href, linkText) {
    var el = $("[data-toast]");
    if (!el) return;
    el.innerHTML = "";
    el.appendChild(document.createTextNode(message));
    if (href) {
      var a = document.createElement("a");
      a.href = href;
      a.textContent = linkText;
      el.appendChild(document.createTextNode(" "));
      el.appendChild(a);
    }
    el.classList.add("is-open");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove("is-open"); }, 4000);
  }

  /* --- Add to cart --------------------------------------------------------- */
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-add]");
    if (!btn) return;
    ev.preventDefault();
    var slug = btn.getAttribute("data-add");
    var item = DATA.mehsullar[slug];
    if (!item) return;
    add(slug, 1);
    btn.classList.add("is-added");
    setTimeout(function () { btn.classList.remove("is-added"); }, 900);
    toast(item.ad + " səbətə atıldı.", "sebet.html", "Səbətə bax");
  });

  /* --- Product page: quantity and buy -------------------------------------- */
  $$("[data-buy]").forEach(function (form) {
    var input = $("input[name='say']", form);
    $$("[data-qty]", form).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var step = parseInt(btn.getAttribute("data-qty"), 10);
        var next = Math.max(1, Math.min(20, (parseInt(input.value, 10) || 1) + step));
        input.value = next;
      });
    });
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var slug = form.getAttribute("data-buy");
      var item = DATA.mehsullar[slug];
      add(slug, Math.max(1, parseInt(input.value, 10) || 1));
      toast(item.ad + " səbətə atıldı.", "sebet.html", "Səbətə bax");
    });
  });

  /* --- Cart page ----------------------------------------------------------- */
  function line(slug, qty) {
    var item = DATA.mehsullar[slug];
    var li = document.createElement("li");
    li.className = "cart__line";
    li.innerHTML =
      '<a class="cart__thumb" href="' + item.unvan + '">' +
        '<img src="' + item.sekil + '" alt="' + item.alt + '" width="320" height="400" loading="lazy">' +
      "</a>" +
      '<div class="stack-sm">' +
        '<a href="' + item.unvan + '" style="text-decoration:none"><b>' + item.ad + "</b></a>" +
        '<span class="muted" style="font-size:.85rem">' + item.hecm + " · " + manat(item.qiymet) + "</span>" +
        '<div class="qty">' +
          '<button type="button" data-line="' + slug + '" data-step="-1" aria-label="Sayı azalt">−</button>' +
          '<input type="number" value="' + qty + '" min="1" max="20" data-line-input="' + slug + '" aria-label="' + item.ad + ' sayı">' +
          '<button type="button" data-line="' + slug + '" data-step="1" aria-label="Sayı artır">+</button>' +
        "</div>" +
      "</div>" +
      '<div class="stack-sm" style="text-align:end;justify-items:end">' +
        '<b class="num">' + manat(item.qiymet * qty) + "</b>" +
        '<button class="btn btn--quiet" type="button" data-remove="' + slug + '">Sil</button>' +
      "</div>";
    return li;
  }

  function paintCart() {
    var wrap = $("[data-cart]");
    var lines = $("[data-cart-lines]");
    var empty = $("[data-cart-empty]");
    if (!lines && !$("[data-cart-mini]")) return;

    var cart = read();
    var slugs = Object.keys(cart).filter(function (s) { return DATA.mehsullar[s]; });

    if (lines) {
      lines.innerHTML = "";
      slugs.forEach(function (slug) { lines.appendChild(line(slug, cart[slug])); });
      if (wrap) wrap.hidden = slugs.length === 0;
      if (empty) empty.hidden = slugs.length !== 0;
    }

    var mini = $("[data-cart-mini]");
    if (mini) {
      mini.innerHTML = "";
      slugs.forEach(function (slug) {
        var item = DATA.mehsullar[slug];
        var li = document.createElement("li");
        li.className = "cart__row";
        li.innerHTML = "<span>" + item.ad + " × " + cart[slug] + "</span>" +
          '<span class="num">' + manat(item.qiymet * cart[slug]) + "</span>";
        mini.appendChild(li);
      });
      if (!slugs.length) {
        mini.innerHTML = '<li class="muted">Səbət boşdur. ' +
          '<a href="magaza.html">Mağazaya keçin</a>.</li>';
      }
    }

    var citySelect = $("select[name='sehir']");
    var city = citySelect && citySelect.value ? citySelect.value : "baki";
    var sum = subtotal(cart);
    var ship = shipping(sum, city);

    $$("[data-cart-subtotal]").forEach(function (el) { el.textContent = manat(sum); });
    $$("[data-cart-shipping]").forEach(function (el) {
      el.textContent = sum > 0 && ship === 0 ? "Pulsuz" : manat(ship);
    });
    $$("[data-cart-total]").forEach(function (el) { el.textContent = manat(sum + ship); });

    var hint = $("[data-cart-freehint]");
    if (hint) {
      var left = DATA.pulsuzHedd - sum;
      hint.textContent = sum > 0 && left > 0
        ? "Daha " + manat(left) + " əlavə etsəniz çatdırılma pulsuz olur."
        : (sum > 0 ? "Çatdırılma pulsuzdur." : "");
    }
  }

  document.addEventListener("click", function (ev) {
    var step = ev.target.closest("[data-line]");
    if (step) {
      var slug = step.getAttribute("data-line");
      var delta = parseInt(step.getAttribute("data-step"), 10);
      setQty(slug, (read()[slug] || 0) + delta);
      return;
    }
    var rm = ev.target.closest("[data-remove]");
    if (rm) {
      var gone = DATA.mehsullar[rm.getAttribute("data-remove")];
      setQty(rm.getAttribute("data-remove"), 0);
      toast((gone ? gone.ad : "Məhsul") + " səbətdən silindi.");
    }
  });

  document.addEventListener("change", function (ev) {
    var input = ev.target.closest("[data-line-input]");
    if (input) setQty(input.getAttribute("data-line-input"), parseInt(input.value, 10) || 0);
    if (ev.target.name === "sehir") paintCart();
  });

  function paint() { paintBadge(); paintCart(); }

  /* Another tab changed the cart -- keep the two windows telling the same story. */
  window.addEventListener("storage", function (ev) { if (ev.key === KEY) paint(); });

  /* --- Catalogue: filter, search, sort ------------------------------------- */
  (function catalogue() {
    var form = $("[data-filters]");
    var grid = $(".shop .grid");
    if (!grid) return;

    var cards = $$(".card", grid);
    var search = $("[data-search]");
    var sort = $("[data-sort]");
    var counter = $("[data-result-count]");
    var empty = $("[data-empty]");
    var order = cards.slice();

    function checked(name) {
      return $$("input[name='" + name + "']:checked", form || document)
        .map(function (i) { return i.value; });
    }

    function inBand(price, band) {
      if (!band || band === "hamisi") return true;
      var parts = band.split("-");
      var lo = parseFloat(parts[0]) || 0;
      var hi = parts[1] ? parseFloat(parts[1]) : Infinity;
      return price >= lo && price < hi;
    }

    function apply() {
      var cats = checked("kateqoriya");
      var tags = checked("teleb");
      var bandInput = $("input[name='qiymet']:checked", form || document);
      var band = bandInput ? bandInput.value : "hamisi";
      var term = (search && search.value || "").trim().toLowerCase();
      var shown = 0;

      cards.forEach(function (card) {
        var okCat = !cats.length || cats.indexOf(card.getAttribute("data-cat")) > -1;
        var cardTags = (card.getAttribute("data-tags") || "").split(" ");
        var okTag = !tags.length || tags.some(function (t) { return cardTags.indexOf(t) > -1; });
        var okBand = inBand(parseFloat(card.getAttribute("data-price")), band);
        var okTerm = !term || (card.getAttribute("data-find") || "").indexOf(term) > -1;
        var visible = okCat && okTag && okBand && okTerm;
        card.hidden = !visible;
        if (visible) shown++;
      });

      if (counter) counter.textContent = shown;
      if (empty) empty.hidden = shown !== 0;
    }

    function reorder() {
      var mode = sort ? sort.value : "secilmis";
      var list = order.slice();
      if (mode === "ucuz" || mode === "baha") {
        list.sort(function (a, b) {
          var d = parseFloat(a.getAttribute("data-price")) - parseFloat(b.getAttribute("data-price"));
          return mode === "ucuz" ? d : -d;
        });
      } else if (mode === "reyting") {
        list.sort(function (a, b) {
          return parseFloat(b.getAttribute("data-rating")) - parseFloat(a.getAttribute("data-rating"));
        });
      }
      list.forEach(function (card) { grid.appendChild(card); });
    }

    if (form) form.addEventListener("change", apply);
    if (search) search.addEventListener("input", apply);
    if (sort) sort.addEventListener("change", reorder);
    $$("[data-clear-filters]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$("input[type='checkbox']", form).forEach(function (i) { i.checked = false; });
        var all = $("input[name='qiymet'][value='hamisi']", form);
        if (all) all.checked = true;
        if (search) search.value = "";
        apply();
      });
    });

    /* The drawer ships open so that with scripting off every filter is reachable.
       On a phone that buries the products, so close it once we know we can reopen it. */
    var drawer = $(".filters--drawer");
    if (drawer && window.matchMedia && window.matchMedia("(max-width: 900px)").matches) {
      drawer.open = false;
    }

    /* The WebSite SearchAction in the JSON-LD points here, so honour the parameter. */
    var q = new URLSearchParams(location.search).get("axtaris");
    if (q && search) { search.value = q; }
    apply();
  })();

  /* --- Forms ---------------------------------------------------------------
   * The forms validate for real and then say plainly that nothing was sent. A
   * demo that fakes a confirmation teaches the visitor to trust a message that
   * is not true. */
  var RULES = {
    ad: function (v) {
      return v.trim().length >= 2 ? "" : "Adınızı yazın — ən azı iki hərf.";
    },
    telefon: function (v) {
      var digits = v.replace(/\D/g, "");
      return digits.length >= 9
        ? "" : "Telefon nömrəsini tam yazın, məsələn 055 123 45 67.";
    },
    email: function (v) {
      if (!v.trim()) return "";
      return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim())
        ? "" : "E-poçt ünvanı düzgün görünmür. @ və nöqtə olmalıdır.";
    },
    sehir: function (v) { return v ? "" : "Çatdırılma üçün şəhəri seçin."; },
    unvan: function (v) {
      return v.trim().length >= 10
        ? "" : "Ünvanı bir az ətraflı yazın — küçə, bina və mənzil.";
    },
    elaqe: function (v) {
      return v.trim().length >= 5
        ? "" : "Sizə necə cavab verək? Telefon və ya e-poçt yazın.";
    },
    mesaj: function (v) {
      return v.trim().length >= 10 ? "" : "Sualınızı bir neçə sözlə açın.";
    }
  };

  function validate(form) {
    var firstBad = null;
    $$("[name]", form).forEach(function (field) {
      var rule = RULES[field.name];
      if (!rule) return;
      var msg = rule(field.value);
      var slot = $("[data-err='" + field.name + "']", form);
      if (slot) slot.textContent = msg;
      field.setAttribute("aria-invalid", msg ? "true" : "false");
      if (msg && !firstBad) firstBad = field;
    });
    if (firstBad) firstBad.focus();
    return !firstBad;
  }

  function demoResult(form, slot, message) {
    slot.hidden = false;
    slot.innerHTML =
      '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" ' +
      'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>' +
      '<path d="M12 11v6M12 7.6v.8"/></svg><span><strong>Forma yoxlandı, hər şey qaydasındadır.</strong>' +
      message + "</span>";
    slot.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  var checkout = $("[data-checkout]");
  if (checkout) {
    checkout.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!validate(checkout)) return;
      demoResult(checkout, $("[data-checkout-result]"),
        " Amma bu nümunə saytdır: sifariş göndərilmədi və heç bir məlumat saxlanılmadı. " +
        "Səbətiniz olduğu kimi qalır.");
    });
  }

  var contact = $("[data-contact]");
  if (contact) {
    contact.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!validate(contact)) return;
      demoResult(contact, $("[data-contact-result]"),
        " Amma bu nümunə saytdır: mesaj göndərilmədi və heç yerdə saxlanılmadı.");
    });
  }

  /* --- Reveal on scroll ---------------------------------------------------- */
  (function reveal() {
    var items = $$(".reveal");
    if (!items.length) return;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        el.style.transitionDelay = Math.min(i * 55, 220) + "ms";
        el.classList.add("is-in");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    items.forEach(function (el) { io.observe(el); });
  })();

  paint();
})();
