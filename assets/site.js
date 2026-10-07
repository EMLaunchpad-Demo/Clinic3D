/* Clinic3D 2026 - navigatie, scroll-animaties en lichte parallax */
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('js');

  /* --- Mobiel menu --- */
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Menu sluiten' : 'Menu openen');
    });
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        links.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('is-open')) {
        links.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* --- Navigatiebalk bij scrollen --- */
  var nav = document.getElementById('nav');
  function onScrollNav() {
    if (nav) nav.classList.toggle('is-scrolled', window.scrollY > 12);
  }
  onScrollNav();

  /* --- Secties die invliegen ---
     Vangnet: wat er ook misgaat, na 2,5 seconde staat alles zichtbaar. */
  var reveals = document.querySelectorAll('.reveal');
  function show(el) { el.classList.add('is-in'); }
  function showAll() { reveals.forEach(show); }

  reveals.forEach(function (el) {
    if (el.getBoundingClientRect().top < window.innerHeight * 0.92) show(el);
  });

  if (reduced || !('IntersectionObserver' in window)) {
    showAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          show(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
    window.setTimeout(showAll, 2500);
  }

  /* --- Lichte parallax op portret en sfeerbeeld --- */
  var portrait = document.getElementById('heroPortrait');
  var quote = document.getElementById('quoteMedia');
  var ticking = false;

  function parallax() {
    ticking = false;
    var y = window.scrollY;
    if (portrait && y < window.innerHeight * 1.5) {
      portrait.style.transform = 'translate3d(0,' + (y * 0.05).toFixed(2) + 'px,0) scale(1.04)';
    }
    if (quote) {
      var rect = quote.parentElement.getBoundingClientRect();
      if (rect.bottom > 0 && rect.top < window.innerHeight) {
        var progress = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
        quote.style.transform = 'translate3d(0,' + ((progress - 0.5) * 60).toFixed(2) + 'px,0)';
      }
    }
  }

  function onScroll() {
    onScrollNav();
    if (!reduced && !ticking) {
      ticking = true;
      window.requestAnimationFrame(parallax);
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  if (!reduced) parallax();
})();

/* Boekingssysteem: laadscherm weg zodra het systeem geladen is */
(function () {
  var frame = document.getElementById('bookingFrame');
  if (!frame) return;
  var iframe = document.getElementById('bookingIframe');
  var done = false;
  function ready() {
    if (done) return;
    done = true;
    window.setTimeout(function () { frame.classList.add('is-loaded'); }, 400);
  }
  if (iframe) iframe.addEventListener('load', ready);
  window.setTimeout(ready, 8000);
})();
