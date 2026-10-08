# Bouwt de volledige Clinic3D-site uit _bron/ (zonder GoHighLevel).
# Gebruik (vanuit de repo-root of _bron/):  py _bron/bouw.py
#
# Uitvoer (rechtstreeks in de repo-root, zo serveert Cloudflare de site):
#   <pagina>.html, post/<slug>.html, 404.html, sitemap.xml, assets/css/site.css, assets/js/site.js
# Enige externe diensten: GHL-boekingssysteem, GHL-contactformulier en GHL-reviewwidget,
# plus Google Analytics en Google Maps (die twee pas na toestemming via de cookiebanner).
import datetime as dt
import glob
import hashlib
import html
import json
import math
import os
import re

BRON = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BRON)
SITE = "https://clinic3d.be"
VANDAAG = dt.date.today()

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
LOGO_BEELDEN = ("/img/logo-clinic3d-vierkant.png", "/img/logo-clinic3d-vierkant-creme.png", "/img/og-clinic3d.jpg")


def lees(rel):
    with open(os.path.join(BRON, rel), encoding="utf-8") as f:
        return f.read()


def schrijf(rel, tekst):
    pad = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(pad) or ".", exist_ok=True)
    with open(pad, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)


def esc(t):
    return html.escape(t or "", quote=True)


def versie(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def brussel(iso):
    """UTC-tijdstip -> datum in Brussel (CET/CEST zonder tzdata-afhankelijkheid)."""
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).replace(tzinfo=None)
    def laatste_zondag(jaar, maand):
        d = dt.date(jaar, maand, 31)
        return d - dt.timedelta(days=(d.weekday() + 1) % 7)
    zomer_start = dt.datetime.combine(laatste_zondag(t.year, 3), dt.time(1))
    zomer_einde = dt.datetime.combine(laatste_zondag(t.year, 10), dt.time(1))
    return (t + dt.timedelta(hours=2 if zomer_start <= t < zomer_einde else 1)).date()


def nl_datum(d):
    return f"{d.day} {MAANDEN[d.month - 1]} {d.year}"


# ---------------------------------------------------------------- CSS en JS bundelen
def scope(css, prefix, only=None):
    """Zet prefix voor elke selector (of enkel die met `only` beginnen); @media/@supports worden doorlopen."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, skip_depth, depth = [], 0, None, 0
    while i < len(css):
        j = min([k for k in (css.find("{", i), css.find("}", i)) if k != -1], default=-1)
        if j == -1:
            out.append(css[i:])
            break
        if css[j] == "}":
            out.append(css[i:j + 1])
            depth -= 1
            if skip_depth is not None and depth < skip_depth:
                skip_depth = None
            i = j + 1
            continue
        head = css[i:j]
        h = head.strip()
        if skip_depth is not None or h.startswith(("@media", "@supports")):
            out.append(head + "{")
        elif h.startswith("@"):
            out.append(head + "{")
            skip_depth = depth + 1
        else:
            lead = head[: len(head) - len(head.lstrip())]
            sels = [s.strip() for s in h.split(",")]
            out.append(lead + ",".join(s if (only and not s.startswith(only)) or s.startswith(prefix) else f"{prefix} {s}" for s in sels) + "{")
        depth += 1
        i = j + 1
    return "".join(out)


def css_deel(pad):
    css = open(pad, encoding="utf-8").read().strip()
    naam = os.path.basename(pad)
    # De zes behandelpagina's delen de wortelklasse .tp maar hebben elk eigen regels:
    # binden aan de eigen pagina (body-klasse p-<pagina>), anders lekken ze naar elkaar.
    if naam.startswith("tp-") and os.path.basename(os.path.dirname(pad)) == "paginas":
        css = scope(css, ".p-" + naam[3:-4], only=".tp")
    return f"/* ---- {os.path.relpath(pad, BRON).replace(os.sep, '/')} ---- */\n" + css


def bundel():
    css_delen = (sorted(glob.glob(os.path.join(BRON, "css", "*.css")))
                 + sorted(glob.glob(os.path.join(BRON, "css", "paginas", "*.css")))
                 + sorted(glob.glob(os.path.join(BRON, "css", "verfijning", "*.css"))))  # laatste laag: verfijning
    css = "\n\n".join(css_deel(p) for p in css_delen)
    schrijf("assets/css/site.css", css + "\n")
    js_delen = ["header.js", "zwevende-knop.js", "cookies.js", "animaties.js", "blog.js"]
    js = "\n\n".join(f"/* ---- js/{n} ---- */\n" + lees("js/" + n).strip() for n in js_delen if os.path.exists(os.path.join(BRON, "js", n)))
    schrijf("assets/js/site.js", js + "\n")
    return versie("assets/css/site.css"), versie("assets/js/site.js")


# ---------------------------------------------------------------- externe media achter toestemming
KAART_PH = ('<div class="extern-plaatshouder"><p>Deze kaart komt van Google Maps en laadt pas na jouw toestemming voor externe media.</p>'
            '<button type="button">Kaart tonen</button></div>')
REVIEW_PH = ('<div class="extern-plaatshouder"><p>Onze reviews worden getoond via een externe reviewdienst en laden pas na jouw toestemming voor externe media.</p>'
             '<button type="button">Reviews tonen</button></div>')


def extern_achter_toestemming(inhoud):
    def kaart(m):
        tag = m.group(1).replace(' src="', ' data-src="', 1)
        return f'<div class="extern extern--kaart" data-extern="kaart">{KAART_PH}{tag}</iframe></div>'
    inhoud = re.sub(r'(<iframe\b[^>]*\ssrc="https://www\.google\.com/maps[^"]*"[^>]*>)\s*</iframe>', kaart, inhoud)
    inhoud = inhoud.replace('<div class="extern" data-extern="reviews">', f'<div class="extern extern--reviews" data-extern="reviews">{REVIEW_PH}')
    return inhoud


# ---------------------------------------------------------------- head en paginaskelet
def head(p, css_v):
    titel = esc(p["titel"])
    beschr = esc(p.get("beschrijving"))
    url = p.get("canonical") or ""
    index = p.get("robots") == "index"
    og_img = p.get("og_image") or f"{SITE}/img/og-clinic3d.jpg"
    regels = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{titel}</title>",
        f'<meta name="description" content="{beschr}">' if beschr else "",
        f'<link rel="canonical" href="{esc(url)}">' if index and url else "",
        '<meta name="robots" content="index, follow, max-image-preview:large">' if index else '<meta name="robots" content="noindex">',
        f'<meta property="og:type" content="{p.get("og_type", "website")}">',
        '<meta property="og:site_name" content="Clinic3D">',
        '<meta property="og:locale" content="nl_BE">',
        f'<meta property="og:title" content="{titel}">',
        f'<meta property="og:description" content="{beschr}">' if beschr else "",
        f'<meta property="og:url" content="{esc(url)}">' if index and url else "",
        f'<meta property="og:image" content="{esc(og_img)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="keywords" content="{esc(p["keywords"])}">' if p.get("keywords") else "",
        '<meta name="theme-color" content="#FDFAF5">',
        '<meta name="geo.region" content="BE-VLI"><meta name="geo.placename" content="Hasselt">',
        '<meta name="geo.position" content="50.9081954;5.3557564"><meta name="ICBM" content="50.9081954, 5.3557564">' if p.get("uitvoer") == "index.html" else "",
        '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="preload" href="/assets/fonts/jost-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/cormorant-garamond-latin.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="/assets/css/site.css?v={css_v}">',
    ]
    for ld in p.get("ldjson", []):
        regels.append('<script type="application/ld+json">' + json.dumps(json.loads(ld), ensure_ascii=False, separators=(",", ":")) + "</script>")
    return "\n".join(r for r in regels if r)


def pagina(p, inhoud, css_v, js_v, body_klasse):
    hdr = lees("onderdelen/header.html")
    ftr = lees("onderdelen/footer.html").replace("{{jaar}}", str(VANDAAG.year))
    zwevend = lees("onderdelen/zwevende-knop.html")
    banner = lees("onderdelen/cookiebanner.html")
    return f"""<!DOCTYPE html>
<html lang="nl-BE">
<head>
{head(p, css_v)}
</head>
<body class="{body_klasse}">
{banner.strip()}
{hdr.strip()}
<main id="main">
{extern_achter_toestemming(inhoud).strip()}
</main>
{ftr.strip()}
{zwevend.strip()}
<script src="/assets/js/site.js?v={js_v}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- schemadata voor pagina's zonder eigen blok
PROCEDURES = {  # pagina -> (naam, procedureType, bodyLocation)
    "skinboosters-hasselt": ("Skinboosters", "PercutaneousProcedure", "Gelaat, hals en decolleté"),
    "biostimulators-hasselt": ("Biostimulators", "PercutaneousProcedure", "Gelaat"),
    "medische-hifu-hasselt": ("Medische HIFU", "NoninvasiveProcedure", "Gelaat, hals en lichaam"),
    "haaruitval-behandeling-hasselt": ("Haaruitval behandeling", "PercutaneousProcedure", "Hoofdhuid"),
}


def kliniek():
    for ld in json.loads(lees("paginas.json"))["home"]["ldjson"]:
        for n in json.loads(ld).get("@graph", []):
            if n.get("@id") == SITE + "/#clinic":
                return {k: v for k, v in n.items() if k != "@context"}
    raise SystemExit("kliniek-entiteit niet gevonden in paginas.json (home)")


def kruimelpad(*items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def schema_aanvullen(naam, p):
    if naam in PROCEDURES:
        nm, typ, zone = PROCEDURES[naam]
        url = p["canonical"]
        graaf = [
            {"@type": "MedicalProcedure", "@id": url + "#procedure", "name": nm, "description": p["beschrijving"],
             "procedureType": "https://schema.org/" + typ, "bodyLocation": zone, "url": url, "provider": {"@id": SITE + "/#clinic"}},
            kruimelpad(("Home", SITE + "/"), ("Behandelingen", SITE + "/behandelingen"), (nm, url)),
            kliniek(),
        ]
        p["ldjson"] = [json.dumps({"@context": "https://schema.org", "@graph": graaf}, ensure_ascii=False)]


# ---------------------------------------------------------------- blog
def maat(src):
    """' width="…" height="…"' van een eigen afbeelding (tegen verspringen); leeg als Pillow ontbreekt"""
    try:
        from PIL import Image
        with Image.open(os.path.join(ROOT, src.lstrip("/"))) as im:
            return f' width="{im.width}" height="{im.height}"'
    except Exception:
        return ""


def leestijd(html_tekst):
    woorden = len(re.sub(r"<[^>]+>", " ", html_tekst).split())
    return max(1, math.ceil(woorden / 200))


def blog_bouwen(css_v, js_v):
    data = json.loads(lees("blog.json"))
    auteur = data["auteur"]
    artikels = []
    for slug, a in data["artikels"].items():
        inhoud = lees(f"blog/{slug}.html")
        d = brussel(a["datum"])
        gewijzigd = max(d, brussel(a["gewijzigd"] or a["datum"]))
        artikels.append(dict(a, slug=slug, inhoud=inhoud, d=d, gw=gewijzigd, minuten=a.get("leestijd") or leestijd(inhoud)))
    artikels.sort(key=lambda a: a["d"], reverse=True)

    def cat_slug(c):
        return re.sub(r"[^a-z0-9]+", "-", c.lower().replace("&", "en")).strip("-")

    def beeld_html(a, merk_klasse="blog-kaart-merk", lazy=True):
        beeld = a["afbeelding"]
        logo = beeld in LOGO_BEELDEN or not beeld
        if logo:
            return True, f'<span class="{merk_klasse}" aria-hidden="true">Clinic<b>3D</b></span>'
        extra = ' loading="lazy"' if lazy else ' fetchpriority="high"'
        return False, f'<img src="{esc(beeld)}" alt="{esc(a["afbeelding_alt"] or a["titel"])}"{maat(beeld)}{extra} decoding="async">'

    def meta_html(a):
        cat = a["categorieen"][0] if a["categorieen"] else "Blog"
        return (f'<p class="blog-kaart-meta"><span class="blog-kaart-cat">{esc(cat)}</span>'
                f'<span class="blog-kaart-tijd"><time datetime="{a["d"].isoformat()}">{nl_datum(a["d"])}</time>'
                f'<span class="blog-leestijd">{a["minuten"]} min leestijd</span></span></p>')

    def kaart(a, kop="h2"):
        logo, img = beeld_html(a)
        cats = " ".join(cat_slug(c) for c in a["categorieen"])
        return (f'<article class="blog-kaart reveal" data-cats="{esc(cats)}"><a class="blog-kaart-link" href="/post/{a["slug"]}">'
                f'<div class="blog-kaart-beeld{" is-logo" if logo else ""}">{img}</div>'
                f'<div class="blog-kaart-tekst">{meta_html(a)}'
                f'<{kop}>{esc(a["titel"])}</{kop}><p>{esc(a["beschrijving"])}</p>'
                f'<span class="blog-kaart-meer">Lees het artikel <span aria-hidden="true">→</span></span></div></a></article>')

    def uitgelicht(a):
        logo, img = beeld_html(a, "blog-top-merk", lazy=False)
        cats = " ".join(cat_slug(c) for c in a["categorieen"])
        return (f'<article class="blog-top reveal" data-cats="{esc(cats)}"><a class="blog-top-link" href="/post/{a["slug"]}">'
                f'<div class="blog-top-beeld{" is-logo" if logo else ""}">{img}</div>'
                f'<div class="blog-top-tekst"><span class="blog-top-label">Nieuwste artikel</span>{meta_html(a)}'
                f'<h2>{esc(a["titel"])}</h2><p>{esc(a["beschrijving"])}</p>'
                f'<span class="btn btn--primary">Lees het artikel <span aria-hidden="true">→</span></span></div></a></article>')

    # onderwerpen voor de filter: op aantal artikels, dan op naam
    telling = {}
    for a in artikels:
        for c in a["categorieen"]:
            telling[c] = telling.get(c, 0) + 1
    cats = sorted(telling, key=lambda c: (-telling[c], c.lower()))
    filter_html = (
        '<div class="blog-filter" role="group" aria-label="Filter op onderwerp" hidden>'
        f'<button type="button" class="blog-filter-knop is-actief" data-cat="" aria-pressed="true">Alles <span>{len(artikels)}</span></button>'
        + "".join(f'<button type="button" class="blog-filter-knop" data-cat="{cat_slug(c)}" aria-pressed="false">{esc(c)} <span>{telling[c]}</span></button>' for c in cats)
        + '</div>')
    vinkje = ('<span class="tick"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg></span>')

    # overzicht: hero met auteurskaart, nieuwste artikel uitgelicht, filter, raster en afsluitende CTA
    nieuwste, rest = artikels[0], artikels[1:]
    overzicht = (
        '<section class="page-hero blog-hero"><div class="container"><div class="blog-hero-grid">'
        '<div class="blog-hero-tekst">'
        '<span class="eyebrow">Blog</span>'
        '<h1>Advies van dr. Sasha Kenis</h1>'
        '<p class="lead">Eerlijke uitleg over behandelingen, resultaten en huidverzorging, zodat je goed geïnformeerd een keuze maakt.</p>'
        '<ul class="blog-hero-punten">'
        f'<li>{vinkje}Geschreven door een erkend esthetisch arts</li>'
        f'<li>{vinkje}Eerlijk over wat een behandeling wél en niet doet</li>'
        f'<li>{vinkje}Begrijpelijke taal, geen verkooppraat</li>'
        '</ul></div>'
        '<aside class="blog-auteur reveal" aria-label="Over de auteur">'
        '<img src="/img/dr-sasha-kenis-portret-720.webp" alt="Portret van dr. Sasha Kenis, esthetisch arts en oprichter van Clinic3D" width="720" height="720" decoding="async">'
        '<div class="blog-auteur-tekst"><span class="blog-auteur-label">Over de auteur</span>'
        f'<p class="blog-auteur-naam">{esc(auteur["naam"])}</p>'
        '<p class="blog-auteur-rol">Esthetisch arts en oprichter van Clinic3D in Hasselt</p>'
        '<p class="blog-auteur-bio">Subtiele, op maat gemaakte behandelingen die je eigen schoonheid versterken in plaats van veranderen. Dat is de rode draad in de praktijk én in elk artikel.</p>'
        '<a class="textlink" href="/over-ons">Meer over dr. Kenis <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
        '</div></aside>'
        '</div></div></section>'
        '<section class="section section--tight blog-lijst"><div class="container">'
        + uitgelicht(nieuwste) +
        '<div class="blog-lijst-kop"><div class="section-head"><span class="eyebrow">Alle artikels</span><h2>Lees verder</h2></div>'
        + filter_html + '</div>'
        '<div class="blog-grid">' + "".join(kaart(a) for a in rest) + '</div>'
        '<p class="blog-leeg" hidden>Geen artikels in dit onderwerp. <button type="button" class="blog-leeg-knop">Toon alle artikels</button></p>'
        '</div></section>'
        '<section class="section section--tight blog-cta"><div class="container"><div class="cta-band reveal">'
        '<span class="eyebrow eyebrow--center blog-cta-eyebrow">Liever persoonlijk advies?</span>'
        '<h2>Bespreek het tijdens een gratis consult</h2>'
        '<p>Lezen is een goed begin. Tijdens een vrijblijvend consult bekijkt dr. Kenis samen met jou wat bij jouw huid en wensen past.</p>'
        '<div class="btn-row btn-row--center"><a class="btn btn--primary" href="/maak-een-afspraak">Boek je gratis consult</a>'
        '<a class="btn btn--light" href="tel:+32468216136">Bel +32 468 21 61 36</a></div>'
        '</div></div></section>'
    )
    meta = json.loads(lees("paginas.json"))["blog"]
    meta["ldjson"] = [json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": SITE + "/blog#blog", "name": "Blog van Clinic3D", "url": SITE + "/blog", "inLanguage": "nl-BE",
         "publisher": {"@id": SITE + "/#clinic"},
         "blogPost": [{"@type": "BlogPosting", "headline": a["titel"], "url": f"{SITE}/post/{a['slug']}", "datePublished": a["d"].isoformat()} for a in artikels]},
        kruimelpad(("Home", SITE + "/"), ("Blog", SITE + "/blog")),
        kliniek(),
    ]}, ensure_ascii=False)]
    schrijf("blog.html", pagina(meta, overzicht, css_v, js_v, "p-blog"))

    # artikels
    for i, a in enumerate(artikels):
        url = f"{SITE}/post/{a['slug']}"
        cat = a["categorieen"][0] if a["categorieen"] else "Blog"
        beeld = a["afbeelding"]
        toon_beeld = beeld and beeld not in LOGO_BEELDEN
        verwant = [x for x in artikels if x["slug"] != a["slug"] and set(x["categorieen"]) & set(a["categorieen"])]
        verwant += [x for x in artikels if x["slug"] != a["slug"] and x not in verwant]
        inhoud = (
            f'<article class="post">'
            f'<header class="post-kop"><div class="container narrow">'
            f'<nav class="kruimel" aria-label="Kruimelpad"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/blog">Blog</a><span aria-hidden="true">/</span><span>{esc(cat)}</span></nav>'
            f'<span class="eyebrow">{esc(cat)}</span><h1>{esc(a["titel"])}</h1>'
            f'<p class="post-meta">Door <a href="/over-ons">dr. Sasha Kenis</a><span aria-hidden="true">·</span>'
            f'<time datetime="{a["d"].isoformat()}">{nl_datum(a["d"])}</time><span aria-hidden="true">·</span>{a["minuten"]} min leestijd</p>'
            f'</div></header>'
            + (f'<figure class="post-beeld container narrow"><img src="{esc(beeld)}" alt="{esc(a["afbeelding_alt"] or a["titel"])}"{maat(beeld)} decoding="async"></figure>' if toon_beeld else "")
            + f'<div class="post-inhoud container">{a["inhoud"]}</div>'
            f'<div class="container narrow"><aside class="post-auteur" aria-label="Over de auteur">'
            f'<img src="/img/dr-sasha-kenis-portret-192.jpg" alt="Dr. Sasha Kenis, esthetisch arts bij Clinic3D in Hasselt" width="96" height="96" loading="lazy">'
            f'<div><p class="post-auteur-naam">{esc(auteur["naam"])}</p><p>{esc(auteur["bio"])}</p>'
            f'<a href="/over-ons">Meer over dr. Kenis <span aria-hidden="true">→</span></a></div></aside></div>'
            f'</article>'
            f'<section class="section section--cream post-cta"><div class="container narrow center reveal">'
            f'<span class="eyebrow eyebrow--center">Gratis consult</span><h2>Benieuwd wat bij jou past?</h2>'
            f'<p>Tijdens een gratis en vrijblijvend consult bekijkt dr. Kenis samen met jou welke aanpak het best bij je past.</p>'
            f'<div class="post-cta-knoppen"><a class="btn btn--primary" href="/maak-een-afspraak">Boek je gratis consult</a>'
            f'<a class="btn btn--ghost" href="tel:+32468216136">Bel +32 468 21 61 36</a></div></div></section>'
            f'<section class="section section--tight post-meer"><div class="container"><div class="section-head"><span class="eyebrow">Verder lezen</span><h2>Meer artikels</h2></div>'
            f'<div class="blog-grid">' + "".join(kaart(x, "h3") for x in verwant[:3]) + '</div></div></section>'
        )
        p = {
            "uitvoer": f"post/{a['slug']}.html", "titel": a["titel"], "beschrijving": a["beschrijving"], "canonical": url, "robots": "index",
            "og_type": "article", "og_image": (SITE + beeld) if beeld else "",
            "ldjson": [json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "BlogPosting", "@id": url + "#artikel", "headline": a["titel"], "description": a["beschrijving"],
                 "datePublished": a["d"].isoformat(), "dateModified": a["gw"].isoformat(),
                 "inLanguage": "nl-BE", "mainEntityOfPage": url, "image": SITE + (beeld or "/img/og-clinic3d.jpg"),
                 "author": {"@type": "Person", "name": "Dr. Sasha Kenis", "jobTitle": "Esthetisch arts", "url": SITE + "/over-ons"},
                 "publisher": {"@id": SITE + "/#clinic"}},
                kruimelpad(("Home", SITE + "/"), ("Blog", SITE + "/blog"), (a["titel"], url)),
                kliniek(),
            ]}, ensure_ascii=False)],
        }
        schrijf(p["uitvoer"], pagina(p, inhoud, css_v, js_v, f"p-post post--{a['type']}"))
    return artikels


# ---------------------------------------------------------------- sitemap
def sitemap(paginas, artikels):
    def gewijzigd(n):
        pad = os.path.join(BRON, "paginas", n + ".html")
        return dt.date.fromtimestamp(os.path.getmtime(pad)) if os.path.exists(pad) else VANDAAG
    urls = [(p["canonical"], gewijzigd(n)) for n, p in paginas.items() if p.get("robots") == "index" and p.get("canonical")]
    urls += [(f"{SITE}/post/{a['slug']}", a["gw"]) for a in artikels]
    regels = "".join(f"<url><loc>{u}</loc><lastmod>{d.isoformat()}</lastmod></url>" for u, d in urls)
    schrijf("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{regels}</urlset>\n')
    return len(urls)


HEADERS = """# Cachingregels voor Cloudflare (gegenereerd door _bron/bouw.py)
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=604800
/favicon.ico
  Cache-Control: public, max-age=604800
"""


def main():
    schrijf("_headers", HEADERS)
    css_v, js_v = bundel()
    paginas = json.loads(lees("paginas.json"))
    for naam, p in paginas.items():
        if naam == "blog":
            continue
        schema_aanvullen(naam, p)
        inhoud = lees(f"paginas/{naam}.html")
        uit = "404.html" if naam == "404" else p["uitvoer"]
        schrijf(uit, pagina(p, inhoud, css_v, js_v, f"p-{naam}"))
    artikels = blog_bouwen(css_v, js_v)
    n = sitemap(paginas, artikels)
    print(f"Klaar: {len(paginas) - 1} pagina's, blogoverzicht, {len(artikels)} artikels, sitemap met {n} URL's (css {css_v}, js {js_v})")


if __name__ == "__main__":
    main()
