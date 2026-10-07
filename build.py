# Bouwt de statische Clinic3D-site: src/<pagina>.html -> <pad>/index.html
# Gebruik: py build.py
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))


def asset_version(rel):
    """Korte hash achter css/js, zodat browsers een nieuwe versie zeker ophalen."""
    data = open(os.path.join(ROOT, rel), "rb").read()
    return hashlib.md5(data).hexdigest()[:8]
SITE = "https://clinic3d.be"

NAV_ITEMS = [
    ("Home", "", ""),
    ("Over ons", "over-ons/", "over-ons"),
    ("Behandelingen", "behandelingen/", "behandelingen"),
    ("Blog", "blog/", "blog"),
    ("Contact", "contact/", "contact"),
]

FOOT_TREATMENTS = [
    ("Spierontspanners", "behandelingen/#spierontspanners"),
    ("Fillers", "behandelingen/#fillers"),
    ("Skinboosters", "behandelingen/#skinboosters"),
    ("Biostimulators", "behandelingen/#biostimulators"),
    ("Huidverbetering", "behandelingen/#huidverbetering"),
    ("Medische HIFU", "behandelingen/#hifu"),
    ("Haarbehandelingen", "behandelingen/#haar"),
]

FOOT_CLINIC = [
    ("Over ons", "over-ons/"),
    ("Blog", "blog/"),
    ("Contact", "contact/"),
    ("Boek een afspraak", "maak-een-afspraak/"),
    ("Privacybeleid", "privacybeleid/"),
    ("Algemene voorwaarden", "algemene-voorwaarden/"),
]


def nav(p, active):
    links = "".join(
        f'      <a href="{p}{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>\n'
        for label, href, key in NAV_ITEMS
    )
    return f"""<header class="nav" id="nav">
  <div class="nav-inner">
    <a class="nav-logo" href="{p or './'}" aria-label="Clinic3D, naar de startpagina">
      <img src="{p}img/logo-clinic3d.jpg" alt="Clinic3D" width="150" height="54">
    </a>

    <nav class="nav-links" id="navLinks" aria-label="Hoofdnavigatie">
{links}      <a class="nav-links-cta" href="{p}maak-een-afspraak/">Boek een afspraak</a>
    </nav>

    <a class="btn btn--gold nav-cta" href="{p}maak-een-afspraak/">Boek een afspraak</a>

    <button class="nav-toggle" id="navToggle" type="button" aria-expanded="false" aria-controls="navLinks" aria-label="Menu openen">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>"""


def foot(p):
    treats = "".join(f'      <a href="{p}{href}">{label}</a>\n' for label, href in FOOT_TREATMENTS)
    clinic = "".join(f'      <a href="{p}{href}">{label}</a>\n' for label, href in FOOT_CLINIC)
    return f"""<footer class="foot">
  <div class="wrap foot-grid">
    <div>
      <img class="foot-logo" src="{p}img/logo-clinic3d.jpg" alt="Clinic3D" width="150" height="54" loading="lazy">
      <p>Medisch-esthetische kliniek in Hasselt.<br>Uitsluitend op afspraak.</p>
    </div>
    <nav aria-label="Behandelingen">
      <h2>Behandelingen</h2>
{treats}    </nav>
    <nav aria-label="Clinic3D">
      <h2>Clinic3D</h2>
{clinic}    </nav>
    <div>
      <h2>Contact</h2>
      <p>
        Luikersteenweg 301 bus 1<br>3500 Hasselt<br>
        <a href="tel:+32468216136">+32&nbsp;468&nbsp;21&nbsp;61&nbsp;36</a><br>
        <a href="mailto:info@clinic3d.be">info@clinic3d.be</a>
      </p>
      <p class="foot-social">
        <a href="https://www.instagram.com/aesthetics_clinic_3d/" target="_blank" rel="noopener">Instagram</a>
        <a href="https://www.facebook.com/clinic3d" target="_blank" rel="noopener">Facebook</a>
      </p>
    </div>
  </div>
  <div class="wrap foot-bottom">
    <p>&copy; 2026 Clinic3D &middot; dr. Sasha Kenis, erkend esthetisch arts &middot; RIZIV 101.85748.004</p>
  </div>
</footer>"""


def page(out, src, title, description, canonical, active, schema="", prefix="", body=None):
    if body is None:
        body = open(os.path.join(ROOT, "src", src), encoding="utf-8").read().strip()
    body = body.replace("{P}", prefix)
    schema_html = ""
    if schema:
        raw = open(os.path.join(ROOT, "src", schema), encoding="utf-8").read().strip()
        for block in raw.split("\n---\n"):
            schema_html += '<script type="application/ld+json">\n' + block.strip() + "\n</script>\n"

    html = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{SITE}{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="nl_BE">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}{canonical}">
<meta property="og:image" content="{SITE}/img/portret-sasha.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap">
<link rel="stylesheet" href="{prefix}assets/styles.css?v={asset_version("assets/styles.css")}">
</head>
<body>

<a class="skip" href="#main">Naar de inhoud</a>

{nav(prefix, active)}

<main id="main">

{body}

</main>

{foot(prefix)}

<script src="{prefix}assets/site.js?v={asset_version("assets/site.js")}" defer></script>
{schema_html}</body>
</html>
"""
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"{out:38} {len(html)//1024} KB")


PAGES = [
    dict(out="index.html", src="home.html", prefix="", active="",
         title="Clinic3D | Medisch-esthetische kliniek in Hasselt",
         description="Clinic3D is de medisch-esthetische kliniek van dr. Sasha Kenis in Hasselt. Fillers, spierontspanners, skinboosters, biostimulators, HIFU en haarbehandelingen door een erkend arts.",
         canonical="/", schema="home.schema.json"),
    dict(out="behandelingen/index.html", src="behandelingen.html", prefix="../", active="behandelingen",
         title="Behandelingen bij Clinic3D in Hasselt",
         description="Alle behandelingen van Clinic3D in Hasselt: spierontspanners, fillers, skinboosters, biostimulators, huidverbetering, medische HIFU en haarbehandelingen, met de duur per behandeling.",
         canonical="/behandelingen", schema="behandelingen.schema.json"),
    dict(out="over-ons/index.html", src="over-ons.html", prefix="../", active="over-ons",
         title="Over Clinic3D | dr. Sasha Kenis, esthetisch arts in Hasselt",
         description="Clinic3D is een medisch-esthetische kliniek in Hasselt, geleid door dr. Sasha Kenis, erkend esthetisch arts. Lees waar we voor staan en hoe we werken.",
         canonical="/over-ons", schema=""),
    dict(out="contact/index.html", src="contact.html", prefix="../", active="contact",
         title="Contact Clinic3D Hasselt | Adres, uren en route",
         description="Contacteer Clinic3D in Hasselt: Luikersteenweg 301 bus 1, +32 468 21 61 36, info@clinic3d.be. Bekijk de openingsuren en plan je route.",
         canonical="/contact", schema=""),
    dict(out="privacybeleid/index.html", src="privacybeleid.html", prefix="../", active="",
         title="Privacybeleid | Clinic3D Hasselt",
         description="Hoe Clinic3D omgaat met je persoonsgegevens volgens de AVG: welke gegevens we verzamelen, waarvoor we ze gebruiken en welke rechten je hebt.",
         canonical="/privacybeleid", schema=""),
    dict(out="algemene-voorwaarden/index.html", src="algemene-voorwaarden.html", prefix="../", active="",
         title="Algemene voorwaarden | Clinic3D Hasselt",
         description="De algemene voorwaarden van Clinic3D in Hasselt: afspraken maken, annuleren, betalen en wat je van een behandeling mag verwachten.",
         canonical="/algemene-voorwaarden", schema=""),
    dict(out="maak-een-afspraak/index.html", src="maak-een-afspraak.html", prefix="../", active="",
         title="Maak een afspraak bij Clinic3D in Hasselt",
         description="Boek online je afspraak bij Clinic3D in Hasselt. Kies je behandeling en een moment dat jou past. Het eerste consult is gratis en vrijblijvend.",
         canonical="/maak-een-afspraak", schema=""),
]

if __name__ == "__main__":
    for cfg in PAGES:
        if os.path.exists(os.path.join(ROOT, "src", cfg["src"])):
            page(**cfg)
        else:
            print(f"overgeslagen (geen src): {cfg['src']}")
