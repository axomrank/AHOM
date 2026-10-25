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
    files=[ROOT/'index.html']
    for folder in ['people','scenes','chapters','films','trails']:
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
    print(f'PASS: {len(files)} HTML pages, {len(ids)} films, {len(scenes)} scenes; internal assets and references exist.')


if __name__=='__main__':
    main()
