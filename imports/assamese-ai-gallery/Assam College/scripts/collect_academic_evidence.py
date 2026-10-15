"""Cache public academic evidence; never treat scraped mentions as verified facts."""
import csv, hashlib, json, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'academic_evidence'
OUT.mkdir(exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; AcademicDirectoryVerification/1.0)'}

def get(url):
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    path = OUT / (key + '.json')
    if path.exists(): return json.loads(path.read_text())
    result = {'url': url, 'retrieved': time.strftime('%Y-%m-%d'), 'status': 'error'}
    try:
        r = requests.get(url, timeout=(8, 25), headers=HEADERS)
        r.raise_for_status()
        result.update(final_url=r.url, status='ok')
        if r.content.startswith(b'%PDF'):
            import subprocess
            pdf = OUT / (key + '.pdf'); pdf.write_bytes(r.content)
            txt = subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True,timeout=30)
            result.update(text=txt.stdout, links=[], kind='pdf')
        else:
            s = BeautifulSoup(r.content, 'html.parser')
            links = [{'label': a.get_text(' ',strip=True), 'url':urljoin(r.url,a['href'])} for a in s.select('a[href]')]
            for tag in s.select('script,style,noscript'): tag.decompose()
            result.update(text=s.get_text('\n',strip=True),links=links,kind='html')
    except Exception as e: result['error'] = type(e).__name__ + ': ' + str(e)[:200]
    path.write_text(json.dumps(result,ensure_ascii=False))
    return result

def samarth():
    base='https://assamadmission.samarth.ac.in/index.php/site/vacancy-list'
    records=[]; seen=set(); page=1
    while True:
        url=f'{base}?page={page}&per-page=50'
        r=requests.get(url,timeout=35,headers=HEADERS); r.raise_for_status()
        (OUT/f'samarth_vacancies_{page:03d}.html').write_text(r.text)
        s=BeautifulSoup(r.content,'html.parser'); added=0
        for tr in s.select('tbody tr[data-key]'):
            key=tr['data-key']; vals=[td.get_text(' ',strip=True) for td in tr.select('td')]
            if key in seen: continue
            assert len(vals)==6, vals
            seen.add(key); added+=1
            records.append(dict(zip(['university','college','programme','discipline','seats','vacancies'],vals),key=key,source_url=url))
        if not added: break
        if page%10==0: print(f'Samarth: {page} pages, {len(records)} rows',flush=True)
        if not s.select_one('.pagination .next:not(.disabled) a'): break
        page+=1; time.sleep(.15)
    (OUT/'samarth_seat_matrix.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(f'Saved {len(records)} official seat matrix records',flush=True)

def colleges():
    rows=list(csv.DictReader((ROOT/'general_colleges.csv').open(encoding='utf-8-sig')))
    audit={r['No.']:r for r in csv.DictReader((ROOT/'general_colleges_scrape_audit.csv').open(encoding='utf-8-sig'))}
    def collect(row):
        urls=[]; a=audit.get(row['No.'],{})
        home=a.get('Final URL') or row['Website URL']
        if home and not any(x in home for x in ['samarth','nearme.','google.com']): urls.append(home)
        urls += re.findall(r'https?://[^\s;]+',row['Department Source URL'])
        urls=list(dict.fromkeys(urls))[:5]
        pages=[get(u) for u in urls]
        links=[]
        for p in pages:
            for l in p.get('links',[]):
                if re.search(r'prospectus|programmes? offered|courses? offered|courses? of study|post.?gradu|\bpg\b|academic|department',l['label']+' '+l['url'],re.I):
                    if urlparse(l['url']).hostname == urlparse(p['url']).hostname and not re.search(r'\.(jpg|png|zip)$',l['url']): links.append(l)
        links.sort(key=lambda l:(0 if re.search('2026|2025',l['url']+l['label']) else 1,0 if re.search('prospectus|post.?grad|courses? offered|programmes? offered',l['url']+l['label'],re.I) else 1))
        for l in links:
            if l['url'] not in urls:
                urls.append(l['url']); pages.append(get(l['url']))
            if len(pages)>=8: break
        rec={'id':row['No.'],'college':row['College / Institute'],'pages':[{'url':p['url'],'status':p['status'],'cache':hashlib.sha256(p['url'].encode()).hexdigest()[:20]+'.json'} for p in pages]}
        (OUT/f"college_{row['No.']}.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2))
        return rec
    with ThreadPoolExecutor(max_workers=6) as pool:
        fs=[pool.submit(collect,r) for r in rows]
        for n,f in enumerate(as_completed(fs),1):
            f.result()
            if n%20==0: print(f'College evidence: {n}/{len(rows)}',flush=True)

def pg_merit():
    base='https://assamadmission.samarth.ac.in/pg/index.php/site/merit-list'
    records=[]; seen=set(); page=1
    while True:
        url=f'{base}?page={page}'
        r=requests.get(url,timeout=35,headers=HEADERS); r.raise_for_status()
        (OUT/f'samarth_pg_metadata_{page:03d}.html').write_text(r.text)
        s=BeautifulSoup(r.content,'html.parser'); added=0
        for tr in s.select('tbody tr[data-key]'):
            key=tr['data-key']; cells=tr.select('td')
            if key in seen: continue
            vals=[td.get_text(' ',strip=True) for td in cells]
            assert len(vals)==4, vals
            seen.add(key); added+=1
            records.append(dict(zip(['university','college','programme'],vals[:3]),key=key,source_url=url,document_url=cells[3].select_one('a')['href']))
        if not added: break
        if not s.select_one('.pagination .next:not(.disabled) a'): break
        page+=1; time.sleep(.2)
    (OUT/'samarth_pg_metadata.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(f'Saved {len(records)} PG programme metadata records; no student lists downloaded',flush=True)

if __name__=='__main__':
    import sys
    if '--samarth' in sys.argv: samarth()
    if '--colleges' in sys.argv: colleges()
    if '--pg' in sys.argv: pg_merit()
