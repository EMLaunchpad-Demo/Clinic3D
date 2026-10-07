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
