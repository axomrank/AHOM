"""Download a resumable Wikimedia Commons Ahom architecture reference collection."""
import csv
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'images/referance/ahom'
UA = 'AhomArchitectureReference/1.0 (local educational photo research; Wikimedia Commons attribution preserved)'
SEEDS = {
    'rang-ghar': ['Rang Ghar', 'Ranghar Pavallions, Joysagar'],
    'talatal-ghar': ['Talatal Ghar'],
    'kareng-ghar': ['Kareng Ghar', "Ahom Raja's Palace"],
    'charaideo-moidams': ['Charaideo Moidam', 'Charaideo Maidam'],
    'sivasagar': ['Sibasagar Shiva Doul', 'Sivasagar Tank (Borpukhuri)', 'Devidol', 'Vishnu Dol, Sivasagar'],
    'joysagar': ['Joysagar Lake', 'Devidol, Joysagar', 'Sivadol Joysagar', 'Joysagar Vishnudol', "Ghanashyam's house, Joysagar"],
    'gaurisagar': ['Gaurisagar Tank', 'Gaurisagar Devidol', 'Gaurisagar Sivadol', 'Gaurisagar Vishnudol'],
    'rudrasagar': ['Rudrasagar Shiva Dol', 'Rudrasagar Lake'],
    'namdang-stone-bridge': ['Namdang Stone Bridge'],
    'ranganath-temple': ['Rangnath Dol'],
    'na-pukhuri': ['Na-Pukhuri Tank'],
    'golaghar': ['Golaghar or Magzine House, Joysagar'],
    'fakuwa-doul': ['Fakuwa Doul'],
}

def fetch(url):
    for attempt in range(6):
        try:
            request_url = url
            if 'w/api.php?' in url:
                request_url += '&requestid=' + str(time.time_ns())
            with urllib.request.urlopen(urllib.request.Request(request_url, headers={'User-Agent': UA}), timeout=75) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == 5:
                raise
            retry_after = exc.headers.get('Retry-After', '') if isinstance(exc, urllib.error.HTTPError) else ''
            delay = max(min(90, 5 * 2 ** attempt), int(retry_after) if retry_after.isdigit() else 0)
            print(f'Retrying in {delay}s: {str(exc)[:100]}', flush=True)
            time.sleep(delay)

def api(**params):
    time.sleep(2)
    return json.loads(fetch('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(action='query', format='json', maxlag=5, **params))))

def plain(value):
    return html.unescape(re.sub('<[^>]+>', '', value or '')).strip()

def main():
    if (ROOT / '.organized-reference-library.json').exists():
        raise SystemExit('This completed collection has been reorganized. Use 00_catalogue/reference-manifest.json; stage any new downloads separately instead of recreating the old folders.')
    ROOT.mkdir(parents=True, exist_ok=True)
    catalog_path = ROOT / 'catalogue.json'
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text())
    else:
        catalog = {}
        visited = set()
        for group, seeds in SEEDS.items():
            queue = [('Category:' + name, 0) for name in seeds]
            while queue:
                category, depth = queue.pop(0)
                if category in visited:
                    continue
                visited.add(category)
                cont = {}
                while True:
                    data = api(list='categorymembers', cmtitle=category, cmlimit=500, cmtype='file|subcat', **cont)
                    members = data.get('query', {}).get('categorymembers', [])
                    for item in members:
                        title = item['title']
                        if item['ns'] == 14 and depth < 2:
                            queue.append((title, depth + 1))
                        elif item['ns'] == 6 and re.search(r'\.(jpe?g|png|tiff?)$', title, re.I):
                            if re.search(r'\b(map|plan|drawing|illustration|painting|reconstruction|render|logo|diagram)\b', title, re.I):
                                continue
                            key = str(item['pageid'])
                            catalog.setdefault(key, dict(pageid=item['pageid'], title=title, group=group, categories=[]))
                            catalog[key]['categories'].append(category)
                    if 'continue' not in data:
                        break
                    cont = data['continue']
                print(f'{category}: {len(members)} entries; {len(catalog)} unique candidates', flush=True)
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    ids = list(catalog)
    for offset in range(0, len(ids), 25):
        batch = ids[offset:offset + 25]
        if all(catalog[key].get('rendition_width') == 1280 for key in batch):
            continue
        data = api(pageids='|'.join(batch), prop='imageinfo', iiprop='url|size|mime|sha1|extmetadata', iiurlwidth=1280)
        for key, page in data.get('query', {}).get('pages', {}).items():
            if key in catalog:
                catalog[key]['info'] = page.get('imageinfo', [{}])[0]
                catalog[key]['rendition_width'] = 1280
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
        print(f'Metadata: {min(offset + 25, len(ids))}/{len(ids)}', flush=True)
    rows, failures, excluded = [], [], []
    seen = set()
    for index, (key, item) in enumerate(catalog.items(), 1):
        info = item.get('info', {})
        meta = info.get('extmetadata', {})
        description = plain(meta.get('ImageDescription', {}).get('value', ''))
        if not info.get('url') or not info.get('mime', '').startswith('image/'):
            excluded.append(dict(title=item['title'], reason='No downloadable image'))
            continue
        if re.search(r'AI.generated|AI-generated|generative AI|digital reconstruction|architectural drawing|oil painting', description, re.I):
            excluded.append(dict(title=item['title'], reason='Non-photographic description'))
            continue
        sha = info.get('sha1', '')
        if sha and sha in seen:
            continue
        seen.add(sha)
        filename = re.sub(r'[^\w.()-]+', '_', item['title'][5:], flags=re.UNICODE)
        filename = key + '_' + filename[:180]
        path = ROOT / item['group'] / filename
        path.parent.mkdir(exist_ok=True)
        row = dict(file=str(path.relative_to(ROOT)), title=item['title'], source_page=info.get('descriptionurl', ''), original_url=info['url'], author=plain(meta.get('Artist', {}).get('value', '')), license=plain(meta.get('LicenseShortName', {}).get('value', '')), license_url=meta.get('LicenseUrl', {}).get('value', ''), credit=plain(meta.get('Credit', {}).get('value', '')), description=description, width=info.get('width'), height=info.get('height'), bytes=info.get('size'), commons_sha1=sha)
        try:
            if not path.exists():
                (ROOT / 'download-progress.json').write_text(json.dumps(dict(candidate=index, candidates=len(catalog), current=item['title'], saved_commons=len(rows), failed=len(failures), updated_at=time.time()), indent=2))
                time.sleep(.5 if info.get('thumburl') else 2)
                download_url = info.get('thumburl', info['url']).split('?', 1)[0]
                payload = fetch(download_url)
                if not info.get('thumburl') and len(payload) != info.get('size'):
                    raise ValueError('Downloaded size differs from Commons metadata')
                expected_sha = int(sha, 16 if len(sha) == 40 else 36) if sha else None
                if not info.get('thumburl') and sha and int(hashlib.sha1(payload).hexdigest(), 16) != expected_sha:
                    raise ValueError('Downloaded SHA1 differs from Commons metadata')
                temporary = path.with_suffix(path.suffix + '.part')
                temporary.write_bytes(payload)
                temporary.replace(path)
            from PIL import Image
            with Image.open(path) as downloaded_image:
                downloaded_image.verify()
            with Image.open(path) as downloaded_image:
                row['width'], row['height'] = downloaded_image.size
            row['original_width'] = info.get('width')
            row['original_height'] = info.get('height')
            row['original_bytes'] = info.get('size')
            row['bytes'] = path.stat().st_size
            row['download_url'] = info['url'] if path.stat().st_size == info.get('size') else info.get('thumburl', info['url'])
            path.with_suffix(path.suffix + '.source.json').write_text(json.dumps(row, ensure_ascii=False, indent=2))
            rows.append(row)
        except Exception as exc:
            failures.append(dict(title=item['title'], url=info['url'], error=str(exc)))
            (ROOT / 'failures.json').write_text(json.dumps(failures, ensure_ascii=False, indent=2))
        if index % 10 == 0:
            print(f'Downloads: {index}/{len(catalog)}; saved {len(rows)}; failed {len(failures)}', flush=True)
            (ROOT / 'manifest.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    (ROOT / 'manifest.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    with (ROOT / 'manifest.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ['file'])
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / 'failures.json').write_text(json.dumps(failures, ensure_ascii=False, indent=2))
    (ROOT / 'excluded.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2))
    counts = {}
    for row in rows:
        group = row['file'].split('/')[0]
        counts[group] = counts.get(group, 0) + 1
    summary = dict(downloaded=len(rows), total_bytes=sum(row['bytes'] for row in rows), groups=counts, failed=len(failures), excluded=len(excluded))
    (ROOT / 'summary.json').write_text(json.dumps(summary, indent=2))
    all_rows = [json.loads(p.read_text()) for p in ROOT.glob('*/*.source.json')]
    (ROOT / 'all-sources-manifest.json').write_text(json.dumps(all_rows, ensure_ascii=False, indent=2))
    with (ROOT / 'all-sources-manifest.csv').open('w') as stream:
        fields = list(dict.fromkeys(key for row in all_rows for key in row))
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    (ROOT / 'README.md').write_text('# Ahom architecture photographic references\n\nPhotographs from Wikimedia Commons monument categories and their subcategories (up to two levels), plus official Sivasagar district pages. Existing original-resolution downloads are retained; remaining Commons images use reference renditions up to 1280 pixels wide. Original URLs are preserved. This is a bounded collection, not every photograph on the internet.\n\nImages are grouped by the category that first supplied them; Commons naming sometimes conflates Kareng Ghar and Talatal Ghar. Consult each source description before identifying a building. Obvious drawings, maps, reconstructions and AI descriptions are filtered; image classification is based on source metadata and requires visual review before publication. Photographs of information boards, artefacts and architectural details may be included.\n\nSee all-sources-manifest.csv or all-sources-manifest.json for the whole collection, and manifest.csv or manifest.json for Commons only. Each image has a .source.json attribution sidecar. Retain attribution and follow each image\'s licence when reusing. Official government photographs have no individual reuse licence stated. catalogue.json records discovery and full Commons metadata; failures.json records downloads that could not be completed. Re-run tools/collect_ahom_photographs.py to resume.\n\n' + '\n'.join(f'- {group}: {count} photographs' for group, count in counts.items()) + '\n')
    print(json.dumps(summary), flush=True)

if __name__ == '__main__':
    main()
