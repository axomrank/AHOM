"""Create crawlable, script-free reference pages alongside the interactive archive."""
import html
import json
from urllib.parse import quote

BASE = 'https://axomrank.github.io/AHOM/'


def e(value):
    return html.escape(str(value or ''), quote=True)


def build_pages(root, data):
    urls = []
    people = data['people']
    scenes = {s['id']: s for s in data['scenes']}
    eras = {x['id']: x for x in data['eras']}

    def link(path, label):
        return f'<a href="{BASE}{path}">{e(label)}</a>'

    def sources(values):
        if not values:
            return '<p class="quiet">Sources have not yet been catalogued for this record.</p>'
        return '<details class="sources"><summary>Sources</summary><ul>' + ''.join(
            f'<li><a href="{e(u)}" rel="noopener">{e(u)}</a></li>' if u.startswith(('https://', 'http://')) else f'<li>{e(u)}</li>' for u in values) + '</ul></details>'

    def cards(ids):
        return '<div class="reference-grid">' + ''.join(f'<article><a href="{BASE}scenes/{sid.lower()}/"><img src="{e(BASE+s["images"][0][1])}" alt="{e(s["alt"])}" loading="lazy"><p>{e(s["date"])}</p><h2>{e(s["title"])}</h2></a></article>' for sid in ids if (s := scenes[sid])['images']) + '</div>'

    def page(path, title, description, body, image=None, kind='Article'):
        url = BASE + path
        urls.append(url)
        schema = {'@context': 'https://schema.org', '@type': kind, 'name': title, 'description': description, 'url': url, 'inLanguage': 'en'}
        if kind == 'Article':
            schema['headline'] = title
        if image:
            schema['image'] = BASE + image
        metaimage = f'<meta property="og:image" content="{e(BASE+image)}">' if image else ''
        doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Ahom</title><meta name="description" content="{e(description[:300])}"><link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description[:300])}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="{'article' if kind == 'Article' else 'website'}">{metaimage}
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{BASE}favicon.svg"><link rel="stylesheet" href="{BASE}assets/site.css"><link rel="stylesheet" href="{BASE}assets/library.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<','&lt;')}</script></head>
<body><a class="skip" href="#content">Skip to content</a><header class="bar"><a class="brand" href="{BASE}">Ahom · আহোম</a><nav aria-label="Sections">{link('chapters/','Chapters')}{link('people/','People')}{link('scenes/','Scenes')}{link('films/','Films')}{link('#/map','MAP')}</nav></header>
<main id="content" class="reference"><nav class="crumbs" aria-label="Breadcrumb">{link('', 'Home')} / {link('chapters/', 'Reference library')}</nav><h1>{e(title)}</h1>{body}</main>
<footer class="foot"><div class="reference"><p>The paintings, portraits and films are modern reconstructions. Dialogue is dramatised; source records may disagree.</p>{link('', 'Explore the interactive archive')}</div></footer></body></html>'''
        prefix = '../' * len(path.strip('/').split('/'))
        doc = doc.replace('<a href="'+BASE, '<a href="'+prefix).replace('src="'+BASE, 'src="'+prefix)
        doc = doc.replace('href="'+BASE+'assets/', 'href="'+prefix+'assets/').replace('href="'+BASE+'favicon.svg', 'href="'+prefix+'favicon.svg')
        target = root / path / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding='utf-8')

    page('chapters/', 'The Ahom kingdom: eight chapters', 'Explore Ahom history from 1228 to 1838 through sourced people, scenes and films.', '<ul>' + ''.join(f'<li>{link("chapters/"+x["id"]+"/", x["title"])} · {x["start"]}–{x["end"]}</li>' for x in data['eras']) + '</ul>', kind='CollectionPage')
    for era in data['eras']:
        page('chapters/'+era['id']+'/', era['title'], era['lead'][0], f'<p>{era["start"]}–{era["end"]}</p>'+''.join(f'<p>{e(t)}</p>' for t in era['lead'])+cards(era['scenes']))
    page('people/', 'People of the Ahom chronicles', 'A source-linked directory of Ahom rulers, queens, officers, rebels and rivals.', '<ul>'+''.join('<li>'+link('people/'+p['id']+'/', p['name'])+'</li>' for p in people.values())+'</ul>', kind='CollectionPage')
    for p in people.values():
        body = f'<p>{e(p.get("as"))}</p><p>{e(p.get("date"))} · {e(p.get("role"))}</p>'
        if p.get('face'):
            body += f'<img class="reference-portrait" src="{e(BASE+p["face"])}" alt="Modern reconstructed portrait of {e(p["name"])}">'
        body += f'<p>{e(p.get("summary"))}</p><p>{e(p.get("notes"))}</p>'
        body += '<dl class="facts">'+''.join(f'<div><dt>{label}</dt><dd>{e(p[key])}</dd></div>' for key,label in [('tai','Tai name'),('hindu','Hindu name'),('aka','Also called'),('relation','Family'),('consort','Consort'),('fate','Fate')] if p.get(key))+'</dl>'
        body += f'<p>Record confidence: {e(p.get("confidence","unrated"))}.</p>'+sources(p.get('sources',[]))
        body += f'<p>{link("#/person/"+p["id"], "Open interactive profile")}</p><h2>Related scenes</h2>'+cards(p.get('scenes',[]))
        page('people/'+p['id']+'/',p['name'],p.get('summary',p['name']),body,p.get('face'))
    page('scenes/', 'Illustrated Ahom history', 'Explore 226 illustrated moments from the Ahom chronicles with historical context and sources.', cards(list(scenes)), kind='CollectionPage')
    ordered = sorted(data['scenes'], key=lambda s: s.get('year') or 0)
    for i,s in enumerate(ordered):
        im = s['images'][0][0] if s['images'] else None
        body = f'<p>{e(s["date"])} · {link("chapters/"+s["era"]+"/",eras[s["era"]]["title"])}</p>'
        if im:
            body += f'<img class="reference-painting" src="{e(BASE+im)}" alt="{e(s["alt"])}">'
        body += f'<p>{e(s["summary"])}</p><p>{e(s.get("notes"))}</p>'+sources(s.get('sources',[]))
        body += '<p>People: '+', '.join(link('people/'+pid+'/',people[pid]['name']) for pid in s['people'])+'</p>'
        body += f'<p>{link("#/scene/"+s["id"],"Open this scene in the interactive archive")} · {link("#/map?event="+s["id"],"Follow this event on MAP")}</p><nav class="pager" aria-label="Chronological scenes">'
        if i: body += link('scenes/'+ordered[i-1]['id'].lower()+'/', 'Earlier: '+ordered[i-1]['title'])
        if i+1 < len(ordered): body += link('scenes/'+ordered[i+1]['id'].lower()+'/', 'Later: '+ordered[i+1]['title'])
        body += '</nav>'
        page('scenes/'+s['id'].lower()+'/',s['title'],s['summary'],body,im)
    page('films/','Short films from Ahom history', f'{len(data["reels"])} unique reconstructed films, with dates, context and source-linked scenes.', '<ul>'+''.join('<li>'+link('films/'+r['id']+'/',r['title'])+'</li>' for r in data['reels'])+'</ul>', kind='CollectionPage')
    for r in data['reels']:
        tracks = ''.join(f'<track kind="subtitles" src="{e(BASE+t["src"])}" srclang="{t["lang"]}" label="{e(t["label"])}">' for t in r.get('tracks',[]))
        body = f'<p>{e(r["year"])}</p><video class="reference-video" controls playsinline preload="none" poster="{e(BASE+r["poster"])}" src="{e(BASE+quote(r["src"],safe="/"))}">{tracks}</video><p>English and Assamese subtitles provide scene context, rather than transcribed speech.</p><h2>Scene description</h2><p>{e(r["description"])}</p>'
        if r.get('line'): body += f'<p lang="as">{e(r["line"])}</p><p>{e(r["translation"])}</p><p class="quiet">Scripted dialogue; not a verified audio transcript.</p>'
        body += f'<p>{link("scenes/"+r["scene"].lower()+"/", "Read the historical scene and sources")}</p>'
        page('films/'+r['id']+'/',r['title'],r['description'],body,r['poster'])
    for t in data['trails']:
        page('trails/'+t['id']+'/', t['title'], t['summary'], '<p>'+e(t['summary'])+'</p>'+cards(t['scenes']))
    urls.insert(0, BASE)
    (root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{e(url)}</loc></url>\n' for url in urls)+'</urlset>\n')
    (root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
    print(f'{len(urls)} crawlable URLs in sitemap.xml')
