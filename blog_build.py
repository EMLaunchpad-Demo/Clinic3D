# Bouwt de blog: leest de CSV met de 16 artikels en maakt blog/index.html + blog/<slug>/index.html
import csv
import html
import os
import re

import build

ROOT = build.ROOT
CSV = os.path.join(ROOT, "..", "blog-posts-sept-dec-2026", "clinic3d-blog-import-sept-dec-2026.csv")

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni",
           "juli", "augustus", "september", "oktober", "november", "december"]


def nl_datum(iso):
    """2026-09-08T09:00:00.000+00:00 -> 8 september 2026"""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
    if not m:
        return ""
    jaar, maand, dag = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{dag} {MAANDEN[maand - 1]} {jaar}"


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def md_naar_html(md):
    """Kleine omzetter: koppen, lijsten, citaten en alinea's."""
    out, lijst, alinea = [], [], []

    def sluit_alinea():
        if alinea:
            out.append("<p>" + inline(" ".join(alinea)) + "</p>")
            alinea.clear()

    def sluit_lijst():
        if lijst:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lijst) + "</ul>")
            lijst.clear()

    for regel in md.replace("\r\n", "\n").split("\n"):
        r = regel.strip()
        if not r:
            sluit_alinea(); sluit_lijst(); continue
        if r.startswith("### "):
            sluit_alinea(); sluit_lijst(); out.append(f"<h3>{inline(r[4:])}</h3>")
        elif r.startswith("## "):
            sluit_alinea(); sluit_lijst(); out.append(f"<h2>{inline(r[3:])}</h2>")
        elif r.startswith("# "):
            sluit_alinea(); sluit_lijst(); out.append(f"<h2>{inline(r[2:])}</h2>")
        elif r.startswith("> "):
            sluit_alinea(); sluit_lijst(); out.append(f"<blockquote><p>{inline(r[2:])}</p></blockquote>")
        elif re.match(r"^[-*] ", r):
            sluit_alinea(); lijst.append(r[2:])
        else:
            sluit_lijst(); alinea.append(r)
    sluit_alinea(); sluit_lijst()
    return "\n".join(out)


def lees_posts():
    with open(CSV, encoding="utf-8-sig") as f:
        rijen = list(csv.DictReader(f))
    posts = []
    for r in rijen:
        iso = (r.get("Scheduled Date") or r.get("Publish Date") or "").strip()
        posts.append(dict(
            slug=r["URL Slug"].strip(),
            titel=r["Blog Post Title"].strip(),
            omschrijving=r["Meta description"].strip(),
            categorie=(r.get("Category ") or r.get("Category") or "").strip(),
            auteur=(r.get("Author") or "").strip(),
            iso=iso,
            datum=nl_datum(iso),
            inhoud=r["Blog Post Content"],
        ))
    posts.sort(key=lambda p: p["iso"], reverse=True)
    return posts


def kaart(p, prefix):
    return f'''        <article class="post-card reveal">
          <a href="{prefix}blog/{p["slug"]}/">
            <span class="post-card-meta"><span class="post-cat">{html.escape(p["categorie"])}</span><time datetime="{p["iso"][:10]}">{p["datum"]}</time></span>
            <h2 class="post-card-title">{html.escape(p["titel"])}</h2>
            <p class="post-card-text">{html.escape(p["omschrijving"])}</p>
            <span class="card-link">Lees het artikel</span>
          </a>
        </article>'''


def bouw():
    posts = lees_posts()

    # --- overzicht ---
    kaarten = "\n".join(kaart(p, "{P}") for p in posts)
    index_body = f'''<section class="page-hero compact">
  <div class="hero-glow" aria-hidden="true"></div>
  <div class="wrap page-hero-inner">
    <p class="eyebrow anim" data-anim="1">Blog</p>
    <h1 class="h1 anim" data-anim="2">Uitleg van <em>de arts</em></h1>
    <p class="lead anim" data-anim="3">
      Wat behandelingen wel en niet doen, hoe ze verlopen en waar je op let. Geschreven door dr. Sasha Kenis.
    </p>
  </div>
</section>

<section class="blog">
  <div class="wrap">
    <div class="post-grid">
{kaarten}
    </div>
  </div>
</section>

<section class="end">
  <div class="wrap end-inner">
    <div class="reveal">
      <h2 class="h2">Liever een persoonlijk antwoord?</h2>
      <p>Tijdens het consult bekijken we jouw situatie. Gratis en vrijblijvend.</p>
      <div class="cta-row">
        <a class="btn btn--gold" href="{{P}}maak-een-afspraak/">Boek een afspraak</a>
        <a class="btn btn--ghost" href="tel:+32468216136">+32&nbsp;468&nbsp;21&nbsp;61&nbsp;36</a>
      </div>
    </div>
    <dl class="end-info reveal">
      <div><dt>Adres</dt><dd>Luikersteenweg 301 bus 1<br>3500 Hasselt</dd></div>
      <div><dt>Openingsuren</dt><dd>Ma 10&ndash;19u<br>Di &amp; Do 16&ndash;19u <em>(wisselend)</em><br>Vr 11&ndash;19u</dd></div>
    </dl>
  </div>
</section>'''

    build.page(out="blog/index.html", src=None, prefix="../", active="blog", body=index_body,
               title="Blog | Clinic3D Hasselt",
               description="Uitleg over esthetische behandelingen door dr. Sasha Kenis: wat ze doen, hoe ze verlopen en waar je op let.",
               canonical="/blog")

    # --- artikels ---
    for i, p in enumerate(posts):
        verder = [q for q in posts if q["slug"] != p["slug"]][:2]
        verder_html = "\n".join(kaart(q, "{P}") for q in verder)
        inhoud = md_naar_html(p["inhoud"])
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": p["titel"],
            "description": p["omschrijving"],
            "datePublished": p["iso"][:10],
            "author": {"@type": "Person", "name": "dr. Sasha Kenis"},
            "publisher": {"@type": "Organization", "name": "Clinic3D"},
            "mainEntityOfPage": f"https://clinic3d.be/blog/{p['slug']}",
        }
        import json
        body = f'''<article class="post">
  <header class="post-head">
    <div class="wrap post-wrap">
      <p class="eyebrow anim" data-anim="1"><a href="{{P}}blog/">Blog</a> &middot; {html.escape(p["categorie"])}</p>
      <h1 class="h1 post-title anim" data-anim="2">{html.escape(p["titel"])}</h1>
      <p class="post-meta anim" data-anim="3">
        <time datetime="{p["iso"][:10]}">{p["datum"]}</time> &middot; door dr. Sasha Kenis
      </p>
    </div>
  </header>

  <div class="wrap post-wrap">
    <div class="prose post-body">
{inhoud}
    </div>

    <aside class="post-cta reveal">
      <h2 class="h2">Vraag over jouw situatie?</h2>
      <p>Het eerste consult bij Clinic3D is gratis en vrijblijvend.</p>
      <a class="btn btn--gold" href="{{P}}maak-een-afspraak/">Boek een afspraak</a>
    </aside>
  </div>
</article>

<section class="blog">
  <div class="wrap">
    <header class="section-head reveal">
      <p class="eyebrow">Lees ook</p>
      <h2 class="h2">Meer uitleg</h2>
    </header>
    <div class="post-grid">
{verder_html}
    </div>
  </div>
</section>'''
        os.makedirs(os.path.join(ROOT, "blog", p["slug"]), exist_ok=True)
        with open(os.path.join(ROOT, "src", "_post.schema.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(schema, ensure_ascii=False, indent=2))
        build.page(out=f"blog/{p['slug']}/index.html", src=None, prefix="../../", active="blog", body=body,
                   title=f'{p["titel"]} | Clinic3D',
                   description=p["omschrijving"],
                   canonical=f"/blog/{p['slug']}", schema="_post.schema.json")
    os.remove(os.path.join(ROOT, "src", "_post.schema.json"))
    print(f"blog: {len(posts)} artikels + overzicht")


if __name__ == "__main__":
    bouw()
