# Kopie van de live site clinic3d.be — 7 oktober 2026

Dit is een momentopname van de HTML-broncode van elke pagina op clinic3d.be, zoals
die vandaag (7 oktober 2026) live stond. Opgehaald rechtstreeks van de site zelf,
want GoHighLevel geeft geen exporteerbare broncode of repo — dit is dus de enige
manier om een "kopie" te hebben.

## Wat zit erin
27 pagina's, elk als `index.html` in een map die de URL volgt (bv. `/fillers-hasselt/`
→ `fillers-hasselt/index.html`), plus `sitemap.xml` en `robots.txt`.

- De 15 hoofdpagina's (home, over ons, behandelingen, contact, afspraak, blog,
  juridische pagina's, de 6 behandelcategorieën)
- 9 blogartikels uit het overzicht, + 2 "verweesde" artikels die niet meer in het
  overzicht staan maar wel nog bestaan (`fillers-of-botox`, `botox-mythes` — zie de
  P3-taak "Sitemap herindienen en oude blogartikels controleren" in Notion)
- `/home` (de dubbele kopie van de homepage) en `/404-pagina`, allebei ter
  referentie voor de redirect-taak

## Wat hier NIET in zit
Enkel de HTML-broncode is gedownload. Afbeeldingen, CSS en JavaScript staan nog op
de servers van GoHighLevel/Cloudflare en laden dus niet als je deze bestanden
rechtstreeks in een browser opent — de pagina's tonen dan vooral platte tekst zonder
opmaak. Voor een volledig offline-doorklikbare kopie (met werkende afbeeldingen en
stijl) is een uitgebreidere spiegeling nodig; laat het weten als je dat ook wil.

## Waarvoor dit dient
Een archief/referentiepunt van de huidige site, los van GoHighLevel. Handig om
terug te grijpen tijdens de overstap naar de nieuwe site (`nieuwe-site-2026`), of
gewoon als backup voor het geval er op het GHL-account iets misloopt.
