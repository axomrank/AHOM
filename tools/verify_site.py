#!/usr/bin/env python3
"""Check content integrity and every generated internal reference before deployment."""
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        for key in ['src','href','poster']:
            if a.get(key): self.links.append(a[key])


def main():
    data=json.loads((ROOT/'data/site.js').read_text().split('window.AHOM = ',1)[1].strip().rstrip(';'))
    errors=[]
    scenes={s['id']:s for s in data['scenes']}
    def check(path, context):
        if not (ROOT/path).is_file(): errors.append(f'{context}: missing {path}')
    ids=[r['id'] for r in data['reels']]
    assert len(set(ids))==len(ids), 'Duplicate reel IDs'
    assert len({r['src'] for r in data['reels']})==len(ids), 'Duplicate film source paths'
    assert len(data['reigns'])==41
    assert data['basemap']==json.loads((ROOT/'assets/maps/assam.json').read_text())
    assert data['basemap']['districts'] and data['basemap']['rivers'].get('brahmaputra')
    assert data['boundaries']==json.loads((ROOT/'assets/maps/boundaries.json').read_text())
    for key in ['assam','india']:
        layer=data['boundaries'][key]
        assert layer['source'] and len(layer['sha256'])==64
        assert layer['rings']
        for ring in layer['rings']:
            assert len(ring)>=4 and ring[0]==ring[-1], f'Open boundary ring: {key}'
            assert all(-90<=lat<=90 and -180<=lon<=180 for lat,lon in ring)
    for place in data['places']:
        lat,lon=place['geo']
        assert -90<=lat<=90 and -180<=lon<=180, f'Invalid coordinates for {place["id"]}'
        assert all(sid in scenes for sid in place['scenes'])
    world=json.loads((ROOT/'assets/maps/world.json').read_text())
    assert len(world['countries'])>=250 and world['license']=='Public domain'
    assert {'IND','CHN','MMR','BTN','BGD','SGP','VAT'} <= {c['id'] for c in world['countries']}
    for country in world['countries']:
        assert country['rings'] and country['name']
        for ring in country['rings']:
            assert len(ring)>=4 and ring[0]==ring[-1]
            assert all(-90<=lat<=90 and -180<=lon<=180 for lat,lon in ring)
    atlas=data['atlas']
    site_ids={p['id'] for p in atlas['sites']}
    assert len(site_ids)==len(atlas['sites'])
    assert set(atlas['events'])==set(scenes), 'Every story needs an explicit map state'
    for pid in atlas['sites']:
        lat,lon=pid['geo']
        assert -90<=lat<=90 and -180<=lon<=180
        assert all(sid in scenes for sid in pid['scenes'])
    for sid,event in atlas['events'].items():
        assert set(event['sites'])<=site_ids and set(event['route'])<=site_ids
        assert set(event['rivers'])<=set(data['basemap']['rivers'])
        assert not event['route'] or len(event['route'])>=2
        assert set(event['route'])<=set(event['sites']), f'Route endpoints must be visible for {sid}'
    assert atlas['events']['AHOM-157']['sites']==['saraighat']
    assert atlas['events']['AHOM-209']['route']==['rangpur','guwahati']
    assert atlas['events']['AHOM-209']['mode']=='river'
    assert atlas['events']['AHOM-001']['route']==['mongmao','pangsau','namrup','tipam','habung','simaluguri','charaideo']
    assert len(atlas['events']['AHOM-001']['sources'])==2
    assert next(t for t in data['trails'] if t['id']=='sukaphaa')['scenes']==['AHOM-001','AHOM-006','AHOM-011','AHOM-012','AHOM-017']
    for r in data['reels']:
        check(r['src'],r['id']);check(r['poster'],r['id'])
        assert r['scene'] in scenes, f'Unknown scene for {r["id"]}'
        assert r['era']==scenes[r['scene']]['era']
        assert r['duration']>0 and r['description']
        assert {t['lang'] for t in r['tracks']} == {'en','as'}
        for t in r['tracks']:
            check(t['src'], r['id'])
            assert (ROOT/t['src']).read_text().startswith('WEBVTT\n')
    for s in data['scenes']:
        assert s.get('alt'), f'Missing alt text for {s["id"]}'
        assert 'sources' in s, f'Lost scene sources for {s["id"]}'
        for im in s['images']:
            for path in im: check(path,s['id'])
        for pid in s['people']: assert pid in data['people']
    life=data['life']['sections']
    assert life and len({s['id'] for s in life})==len(life)
    life_ids=[it['id'] for s in life for it in s['items']]
    assert len(set(life_ids))==len(life_ids), 'Duplicate life image IDs'
    for s in life:
        assert s['intro'] and s['caveat']
        for it in s['items']:
            assert it['alt'] and it['img'][0].startswith('media/life/'), it['id']
            for path in it['img']: check(path,it['id'])
    files=[ROOT/'index.html']
    for folder in ['people','scenes','life','chapters','films','trails']:
        files+=list((ROOT/folder).rglob('index.html'))
    for path in files:
        parser=Links();parser.feed(path.read_text())
        for link in parser.links:
            u=urlsplit(link)
            if u.scheme or u.netloc or not u.path: continue
            target=(path.parent/unquote(u.path)).resolve()
            if target.is_dir(): target=target/'index.html'
            if not target.is_file(): errors.append(f'{path.relative_to(ROOT)}: broken link {link}')
    ET.parse(ROOT/'sitemap.xml')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(files)} HTML pages, {len(ids)} films, {len(scenes)} scenes, {len(life_ids)} life images; internal assets and references exist.')


if __name__=='__main__':
    main()
