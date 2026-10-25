#!/usr/bin/env python3
"""Stage only public website assets; omit production work and duplicate video encodes."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    dest = Path(sys.argv[1] if len(sys.argv)>1 else '_site').resolve()
    if dest.exists():
        raise SystemExit(f'Refusing to overwrite an existing directory: {dest}')
    dest.mkdir(parents=True)
    for name in ['index.html','favicon.svg','.nojekyll','robots.txt','sitemap.xml']:
        shutil.copy2(ROOT/name, dest/name)
    for name in ['assets','chapters','people','scenes','films','trails']:
        shutil.copytree(ROOT/name, dest/name)
    (dest/'data').mkdir()
    shutil.copy2(ROOT/'data/site.js',dest/'data/site.js')
    for name in ['characters','faces','scenes']:
        shutil.copytree(ROOT/'media'/name,dest/'media'/name)
    data = json.loads((ROOT/'data/site.js').read_text().split('window.AHOM = ',1)[1].strip().rstrip(';'))
    for r in data['reels']:
        for name in [r['src'],r['poster'], *[t['src'] for t in r.get('tracks',[])]]:
            target=dest/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name,target)
    print(f'Public site staged at {dest}; {len(data["reels"])} films, no research/studio/alternate cuts.')


if __name__ == '__main__':
    main()
