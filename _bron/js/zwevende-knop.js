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
