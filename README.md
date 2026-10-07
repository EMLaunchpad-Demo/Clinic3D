# Clinic3D — website (clinic3d.be)

Statische website, gehost op Cloudflare Workers (static assets). Elke push naar `main`
op GitHub wordt automatisch gebouwd en gepubliceerd.

De site staat los van GoHighLevel. Alleen deze drie onderdelen komen nog uit GHL:

- **het boekingssysteem**, ingesloten op `/maak-een-afspraak` en in de zwevende knop "Boek een afspraak"
- **het contactformulier**, ingesloten op `/contact`
- **de reviewwidget**, op de homepage

Google Analytics, Google Maps en de reviewwidget laden pas na toestemming via de eigen
cookiebanner. Het boekingssysteem en het contactformulier laden altijd, op de pagina waar
je ze gebruikt.

## Structuur

| Map / bestand | Inhoud |
|---|---|
| `_bron/` | De bron van de site. Pas hier aan, niet in de gebouwde `.html`-bestanden. |
| `_bron/paginas/*.html` | De inhoud van elke pagina. |
| `_bron/paginas.json` | Per pagina: titel, beschrijving, canonical, robots en schemadata. |
| `_bron/blog/*.html` + `_bron/blog.json` | De blogartikels en hun gegevens (titel, datum, categorie, afbeelding). |
| `_bron/onderdelen/` | Header, footer, zwevende boekingsknop en cookiebanner (één keer, voor alle pagina's). |
| `_bron/css/`, `_bron/js/` | Opmaak en scripts. Ze worden gebundeld tot `assets/css/site.css` en `assets/js/site.js`. |
| `_bron/bouw.py` | De generator. |
| `assets/fonts/` | Cormorant Garamond en Jost, zelf gehost. |
| `img/` | Alle afbeeldingen, zelf gehost. |
| `_redirects` | De 301-doorverwijzingen van oude URL's. |
| `wrangler.jsonc` | De Cloudflare-config, met de eigen 404-pagina. |
| `.assetsignore` | Wat niet publiek mag, zoals `_bron/` en `.git`. |

## Aanpassen en publiceren

```
py _bron/bouw.py
```

Dit bouwt alle pagina's, het blogoverzicht, de artikels, `sitemap.xml`, `site.css` en `site.js`
opnieuw. Commit daarna de bron en het resultaat samen en push naar `main`.

Na een publicatie kan je de URL's ook bij IndexNow aanmelden (Bing en co.). De sleutel staat
in `cd61a45429f547a1af359f474a676430.txt`.

## Vaste gegevens

De vaste gegevens van de praktijk staan in de inhoud, de footer en de schemadata: adres,
telefoon, e-mail, openingsuren en prijzen. Wijzig je er een, zoek die dan overal in `_bron/`.
Op de site staat nooit "botox" als behandelnaam; gebruik spierontspanners of botulinetoxine.
