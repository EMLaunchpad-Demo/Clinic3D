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
