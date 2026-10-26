"""Collect article photographs from official Sivasagar monument pages."""
import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

BASE = 'https://sivasagar.assam.gov.in'
ROOT = Path(__file__).resolve().parents[1] / 'images/referance/ahom'
DEST = ROOT / 'official-sivasagar'
PAGES = {275:'sivasagar-tank-temples',276:'rang-ghar',277:'talatal-ghar',328:'kareng-ghar',329:'joysagar',331:'ranganath-fakuwa',330:'ghanashyam-house',332:'rudrasagar',333:'gaurisagar',334:'namdang-stone-bridge',393:'jagadhatri-lakhisagar',394:'thowra-doul',395:'hara-gauri-doul',397:'namti-temples',396:'gorokhiya-doul',398:'maidams',399:'gola-ghar'}

def fetch(url):
    time.sleep(1)
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'AhomArchitectureReference/1.0 (local educational research)'}),timeout=60).read()

def main():
    if (ROOT / '.organized-reference-library.json').exists():
        raise SystemExit('This collection has been reorganized. Use 00_catalogue/reference-manifest.json; stage new downloads separately.')
    DEST.mkdir(parents=True, exist_ok=True)
    rows=[]
    failed=[]
    seen=set()
    for pageid, group in PAGES.items():
        page=f'{BASE}/tourist-place-detail/{pageid}'
        try:
            soup=BeautifulSoup(fetch(page),'html.parser')
            images=soup.select('.views-field-nothing img')
            for im in images:
                src=im.get('src','')
                if '/styles/style_350_200/' in src or re.search(r'\bIAS\b', im.get('alt','')):
                    continue
                if 'WhatsApp%20Image%202022-03-25' in src or 'WhatsApp Image 2022-03-25' in src:
                    continue
                if '/sites/default/files/' not in src or 'default' in src.rsplit('/',1)[-1].lower():
                    continue
                src=re.sub(r'/styles/[^/]+/public/', '/', src)
                url=urllib.parse.urljoin(BASE,src).split('?',1)[0]
                if url in seen:
                    continue
                seen.add(url)
                filename=group+'__'+re.sub(r'[^\w.()-]+','_',urllib.parse.unquote(url.rsplit('/',1)[-1]))
                path=DEST/filename
                payload=path.read_bytes() if path.exists() else fetch(url)
                with Image.open(BytesIO(payload)) as image:
                    image.verify()
                with Image.open(BytesIO(payload)) as image:
                    width,height=image.size
                path.write_bytes(payload)
                row=dict(file=str(path.relative_to(ROOT)),title=im.get('alt') or group,source_page=page,original_url=url,author='Not individually identified on source page',license='No individual photo licence stated; consult source website copyright policy',license_url='',credit='Sivasagar district, Government of Assam',description=im.get('alt') or group,width=width,height=height,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
                path.with_suffix(path.suffix+'.source.json').write_text(json.dumps(row,indent=2,ensure_ascii=False))
                rows.append(row)
            print(group,':',len(images),'article photos;',len(rows),'saved total',flush=True)
        except Exception as exc:
            failed.append(dict(page=page,error=str(exc)))
            print('Failed:',group,str(exc),flush=True)
        (ROOT/'official-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    with (ROOT/'official-manifest.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]) if rows else ['file'])
        writer.writeheader();writer.writerows(rows)
    (ROOT/'official-failures.json').write_text(json.dumps(failed,indent=2))
    print('Official photographs downloaded:',len(rows),flush=True)

if __name__=='__main__':
    main()
