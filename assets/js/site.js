/* ---- js/header.js ---- */
/* Header: schaduw en compacte stand bij scrollen, mobiel menu, actieve pagina in de navigatie */
(function () {
  var h = document.querySelector(".site-header");
  if (h) {
    var s = function () { h.classList.toggle("is-scrolled", window.scrollY > 12); };
    s();
    window.addEventListener("scroll", s, { passive: true });
  }

  var m = document.getElementById("mobileMenu");
  var t = document.querySelector(".nav-toggle");
  function zet(open, terug) {
    if (!m || !t) return;
    m.classList.toggle("is-open", open);
    t.setAttribute("aria-expanded", open ? "true" : "false");
    t.setAttribute("aria-label", open ? "Menu sluiten" : "Menu openen");
    document.body.classList.toggle("no-scroll", open);
    document.querySelectorAll("main, .site-footer, .c3d-float-cta").forEach(function (x) { x.inert = open; });
    if (open) {
      var f = m.querySelector("a,summary");
      if (f) setTimeout(function () { f.focus({ preventScroll: true }); }, 60);
    } else if (terug) {
      t.focus();
    }
  }
  if (m && t) {
    t.addEventListener("click", function (e) { e.stopPropagation(); zet(!m.classList.contains("is-open")); });
    m.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { zet(false); }); });
    window.addEventListener("keydown", function (e) { if (e.key === "Escape" && m.classList.contains("is-open")) zet(false, true); });
    var bq = window.matchMedia("(min-width:981px)");
    var bf = function (q) { if (q.matches) zet(false); };
    if (bq.addEventListener) bq.addEventListener("change", bf); else bq.addListener(bf);
  }

  // actieve pagina (ook zonder .html in de URL)
  var here = location.pathname.replace(/\.html$/, "").replace(/\/+$/, "") || "/";
  document.querySelectorAll(".nav-links a, .mobile-menu a").forEach(function (a) {
    var hr = a.getAttribute("href");
    if (!hr || hr.charAt(0) !== "/") return;
    var hh = hr.split("#")[0].replace(/\/+$/, "") || "/";
    if (hh === here) a.setAttribute("aria-current", "page");
  });
  var groep = m && m.querySelector(".mm-groep");
  if (groep && groep.querySelector('a[aria-current="page"]')) groep.open = true;

  // dropdown Behandelingen: actief op subpagina's, sluiten met Escape
  var dd = document.querySelector(".nav-dropdown");
  if (dd) {
    var tg = dd.querySelector(".nav-drop-toggle");
    if (dd.querySelector('.nav-drop-menu a[aria-current="page"]')) tg.classList.add("is-actief");
    dd.addEventListener("keydown", function (e) { if (e.key === "Escape") { dd.classList.add("is-dicht"); tg.focus(); } });
    dd.addEventListener("mouseleave", function () { dd.classList.remove("is-dicht"); });
    dd.addEventListener("focusout", function (e) { if (!dd.contains(e.relatedTarget)) dd.classList.remove("is-dicht"); });
  }
})();

/* ---- js/zwevende-knop.js ---- */
/* Zwevende knop 'Boek een afspraak': verschijnt na de hero en verdwijnt bij de footer (zodat
   'Cookie-instellingen' bereikbaar blijft). Desktop opent het boekingspaneel; telefoon en lage
   schermen gaan naar de volledige boekingspagina. Het GHL-boekingssysteem laadt pas bij openen. */
(function () {
  var btn = document.getElementById("c3dFloatCta");
  var panel = document.getElementById("c3dFloatPanel");
  var closeBtn = document.getElementById("c3dFloatClose");
  var iframe = document.getElementById("c3dFloatIframe");
  if (!btn || !panel) return;

  var path = location.pathname.replace(/\.html$/, "").replace(/\/+$/, "") || "/";
  if (path === "/maak-een-afspraak") { btn.style.display = "none"; return; }

  var klein = window.matchMedia("(max-width:600px), (max-height:560px)");
  var geladen = false;
  var footerInBeeld = false;

  function aria() {
    if (klein.matches) {
      btn.removeAttribute("aria-controls");
      btn.removeAttribute("aria-expanded");
      panel.removeAttribute("role");
    } else {
      btn.setAttribute("aria-controls", "c3dFloatPanel");
      btn.setAttribute("aria-expanded", isOpen() ? "true" : "false");
      panel.setAttribute("role", "dialog");
      panel.setAttribute("aria-label", "Boek een afspraak");
    }
  }
  function isOpen() { return panel.classList.contains("is-open"); }
  function toon() {
    var voorbijHero = window.scrollY > Math.min(window.innerHeight * 0.6, 520);
    btn.classList.toggle("is-zichtbaar", isOpen() || (voorbijHero && !footerInBeeld));
  }
  function open() {
    if (!geladen) { iframe.src = iframe.getAttribute("data-src"); geladen = true; }
    panel.classList.add("is-open");
    btn.setAttribute("aria-expanded", "true");
    toon();
    setTimeout(function () { closeBtn.focus({ preventScroll: true }); }, 60);
  }
  function sluit(terug) {
    if (!isOpen()) return;
    panel.classList.remove("is-open");
    btn.setAttribute("aria-expanded", "false");
    if (terug) btn.focus({ preventScroll: true });
    toon();
  }

  btn.addEventListener("click", function () {
    if (klein.matches) { location.href = "/maak-een-afspraak"; return; }
    isOpen() ? sluit(false) : open();
  });
  closeBtn.addEventListener("click", function () { sluit(true); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") sluit(true); });
  document.addEventListener("click", function (e) {
    if (isOpen() && !panel.contains(e.target) && !btn.contains(e.target)) sluit(false);
  });
  if (klein.addEventListener) klein.addEventListener("change", function () { sluit(false); aria(); });

  var footer = document.querySelector(".site-footer");
  if (footer && "IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { footerInBeeld = e[0].isIntersecting; toon(); }, { rootMargin: "0px 0px -40px 0px" }).observe(footer);
  }
  aria();
  toon();
  window.addEventListener("scroll", toon, { passive: true });
})();

/* ---- js/cookies.js ---- */
/* Eigen cookiebeheer: Google Analytics en externe media (Google Maps, reviewwidget) laden pas na toestemming. */
(function () {
  var SLEUTEL = "c3d-cookies";
  var GA_ID = "G-P84XQ29HMT";
  var banner = document.getElementById("cookiebanner");

  function lees() {
    try { return JSON.parse(localStorage.getItem(SLEUTEL) || "null"); } catch (e) { return null; }
  }
  function bewaar(keuze) {
    keuze.v = 1;
    keuze.datum = new Date().toISOString();
    try { localStorage.setItem(SLEUTEL, JSON.stringify(keuze)); } catch (e) { /* privévenster: keuze geldt voor dit bezoek */ }
    pasToe(keuze);
  }

  // ---------- Google Analytics (enkel met toestemming 'statistieken')
  var gaGeladen = false;
  function laadAnalytics() {
    if (gaGeladen) return;
    gaGeladen = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "granted" });
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }
  function stopAnalytics() {
    if (window.gtag) window.gtag("consent", "update", { analytics_storage: "denied" });
    document.cookie.split(";").forEach(function (c) {
      var naam = c.split("=")[0].trim();
      if (/^_ga/.test(naam)) {
        ["", "; domain=" + location.hostname, "; domain=." + location.hostname.replace(/^www\./, "")].forEach(function (d) {
          document.cookie = naam + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + d;
        });
      }
    });
  }

  // ---------- Externe media (enkel met toestemming 'media')
  var reviewScript = false;
  function laadExtern(el) {
    if (el.classList.contains("is-geladen")) return;
    el.querySelectorAll("iframe[data-src]").forEach(function (f) { f.src = f.getAttribute("data-src"); f.removeAttribute("data-src"); });
    if (el.getAttribute("data-extern") === "reviews" && !reviewScript) {
      reviewScript = true;
      var s = document.createElement("script");
      s.src = "https://reputationhub.site/reputation/assets/review-widget.js";
      document.body.appendChild(s);
    }
    el.classList.add("is-geladen");
  }
  function laadAlleExtern() { document.querySelectorAll("[data-extern]").forEach(laadExtern); }
  document.querySelectorAll("[data-extern]").forEach(function (el) {
    var knop = el.querySelector(".extern-plaatshouder button");
    if (knop) knop.addEventListener("click", function () {
      var k = lees() || { statistieken: false, media: false };
      k.media = true;
      bewaar(k);
      verberg();
    });
  });

  function pasToe(k) {
    if (k.statistieken) laadAnalytics(); else stopAnalytics();
    if (k.media) laadAlleExtern();
  }

  // ---------- Banner
  var opener = null;
  function ruimte(aan) {
    var px = aan && window.matchMedia("(max-width:600px)").matches ? (banner.offsetHeight + 16) + "px" : "";
    document.body.style.paddingBottom = px;
    document.documentElement.style.scrollPaddingBottom = px;
  }
  function toon(metOpties) {
    if (!banner) return;
    opener = metOpties ? document.activeElement : null;
    var k = lees() || { statistieken: false, media: false };
    banner.querySelectorAll("[data-cc-cat]").forEach(function (i) { i.checked = !!k[i.getAttribute("data-cc-cat")]; });
    zetOpties(!!metOpties);
    banner.hidden = false;
    ruimte(true);
    if (metOpties) { var eerste = banner.querySelector("[data-cc-cat]"); if (eerste) eerste.focus(); }
  }
  function verberg() {
    if (!banner) return;
    var hadFocus = banner.contains(document.activeElement);
    banner.hidden = true;
    ruimte(false);
    if (hadFocus) {
      if (opener && document.contains(opener)) opener.focus();
      else { var m = document.getElementById("main"); if (m) { m.setAttribute("tabindex", "-1"); m.focus({ preventScroll: true }); } }
    }
    opener = null;
  }
  function zetOpties(open) {
    var opties = document.getElementById("cc-opties");
    var knop = banner.querySelector('[data-cc="instellingen"]');
    opties.hidden = !open;
    knop.setAttribute("aria-expanded", open ? "true" : "false");
    banner.querySelector('[data-cc="bewaar"]').hidden = !open;
  }
  if (banner) {
    banner.addEventListener("click", function (e) {
      var actie = e.target.closest("[data-cc]");
      if (!actie) return;
      var a = actie.getAttribute("data-cc");
      if (a === "alles") { bewaar({ statistieken: true, media: true }); verberg(); }
      else if (a === "noodzakelijk") { bewaar({ statistieken: false, media: false }); verberg(); }
      else if (a === "instellingen") { zetOpties(document.getElementById("cc-opties").hidden); }
      else if (a === "bewaar") {
        var k = { statistieken: false, media: false };
        banner.querySelectorAll("[data-cc-cat]").forEach(function (i) { k[i.getAttribute("data-cc-cat")] = i.checked; });
        bewaar(k); verberg();
      }
    });
  }
  document.querySelectorAll("[data-cookie-instellingen]").forEach(function (b) {
    b.addEventListener("click", function () { toon(true); });
  });

  var keuze = lees();
  if (keuze) pasToe(keuze); else toon(false);
})();

/* ---- js/animaties.js ---- */
/* Rustige scroll-animaties. Zonder JS, zonder IntersectionObserver/Web Animations of bij
   'minder beweging' wordt niets verborgen. Enkel wat bij het laden onder de vouw staat, wacht. */
(function () {
  var mq = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  if ((mq && mq.matches) || !("IntersectionObserver" in window) || !Element.prototype.animate) return;

  var BLOKKEN = [
    ".reveal", ".section-head",
    ".waarom-intro", ".waarom-knoppen", ".c3t .head", ".c3f .head", ".c3c .head", ".c3p .head", ".c3p .group", ".c3p .note",
    ".c3w .cta", ".c3t .foot", ".c3d-about-media", ".c3d-about-copy",
    ".c3b .photo", ".c3b .wrap > div:last-child", ".c3c .grid > *",
    ".tp-h2", ".tp-sub", ".tp-cta", ".tp-cross", ".tp .wrap > h2", ".tp .cta", ".tp .note",
    ".afs-info-grid > *", ".post-auteur", ".post-meer .section-head", ".map-embed", ".extern--reviews"
  ];
  var RASTERS = [ /* kinderen komen een voor een binnen */
    ".c3u .grid", ".waarom-lijst", ".c3t .grid", ".grid-3", ".blog-grid",
    ".tp-zones", ".tp-price-grid", ".tp-trust", ".tp-steps", ".tp .grid", ".tp-faq", ".c3f .wrap > details"
  ];

  var lijst = [];
  function voeg(el) { if (lijst.indexOf(el) === -1) lijst.push(el); }
  RASTERS.forEach(function (s) {
    document.querySelectorAll(s).forEach(function (r) {
      if (r.matches("details")) { voeg(r); return; }
      Array.prototype.forEach.call(r.children, voeg);
    });
  });
  BLOKKEN.forEach(function (s) { document.querySelectorAll(s).forEach(voeg); });
  // geen geneste animaties: alleen het buitenste element animeert
  lijst = lijst.filter(function (el) { return !lijst.some(function (o) { return o !== el && o.contains(el); }); });

  var KF = [{ opacity: 0, transform: "translateY(22px)" }, { opacity: 1, transform: "none" }];
  var vouw = window.innerHeight * 0.92, wachtend = [];

  var io = new IntersectionObserver(function (entries) {
    var n = 0;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target, a = el.__rv;
      io.unobserve(el);
      if (!a) return;
      var extra = (parseInt(el.getAttribute("data-delay"), 10) || 0) * 120;
      a.effect.updateTiming({ delay: Math.min(n++, 5) * 85 + extra });
      a.play();
      el.__rv = null;
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0 });

  lijst.forEach(function (el) {
    if (el.getBoundingClientRect().top < vouw) return; // al in beeld: gewoon tonen
    var a = el.animate(KF, { duration: 750, easing: "cubic-bezier(.22,.61,.36,1)", fill: "backwards" });
    a.pause(); // beginstand vasthouden tot het element in beeld komt
    el.__rv = a;
    wachtend.push(a);
    io.observe(el);
  });

  // afdrukken of naar een anker springen: alles meteen tonen
  function alles() { wachtend.forEach(function (a) { try { a.finish(); } catch (e) {} }); }
  window.addEventListener("beforeprint", alles);
})();

/* ---- js/blog.js ---- */
/* Blogoverzicht: filter op onderwerp (zonder JS staan gewoon alle artikels op de pagina) */
(function () {
  var filter = document.querySelector(".blog-filter");
  if (!filter) return;
  var knoppen = Array.prototype.slice.call(filter.querySelectorAll("[data-cat]"));
  var items = Array.prototype.slice.call(document.querySelectorAll(".blog-lijst [data-cats]"));
  var leeg = document.querySelector(".blog-leeg");
  var leegKnop = document.querySelector(".blog-leeg-knop");

  function kies(cat, stil) {
    var n = 0;
    knoppen.forEach(function (b) {
      var actief = b.getAttribute("data-cat") === cat;
      b.classList.toggle("is-actief", actief);
      b.setAttribute("aria-pressed", actief ? "true" : "false");
    });
    items.forEach(function (el) {
      var toon = !cat || (" " + el.getAttribute("data-cats") + " ").indexOf(" " + cat + " ") !== -1;
      el.hidden = !toon;
      if (toon) n++;
    });
    if (leeg) leeg.hidden = n > 0;
    if (!stil && window.history && history.replaceState) {
      history.replaceState(null, "", cat ? "#onderwerp=" + cat : location.pathname + location.search);
    }
  }

  filter.hidden = false;
  filter.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("[data-cat]") : null;
    if (b) kies(b.getAttribute("data-cat"));
  });
  if (leegKnop) leegKnop.addEventListener("click", function () { kies(""); });

  // #onderwerp=fillers: direct gefilterd openen (bv. vanuit een link)
  function uitHash() {
    var m = /onderwerp=([a-z0-9-]+)/.exec(location.hash || "");
    var cat = m && knoppen.some(function (b) { return b.getAttribute("data-cat") === m[1]; }) ? m[1] : "";
    kies(cat, true);
  }
  window.addEventListener("hashchange", uitHash);
  if (location.hash) uitHash();
})();
