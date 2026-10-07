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
