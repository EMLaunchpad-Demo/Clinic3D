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
