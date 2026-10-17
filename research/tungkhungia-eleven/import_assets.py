import csv, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
items = json.loads((HERE / 'manifest.json').read_text())
dest = ROOT / 'media/scenes/ahom/1681-1769-tungkhungia-restoration'
archive = ROOT / 'archive/tungkhungia-eleven'
archive.mkdir(parents=True, exist_ok=True)
(dest / 'thumb').mkdir(exist_ok=True)
for item in items:
    name = f"{item['id']}_{item['slug']}.webp"
    final = dest / name
    if final.exists():
        raise SystemExit(f'Refusing to overwrite {final}')
    source = Path(item['generated_path'])
    shutil.copy2(source, archive / f"{item['id']}-final.png")
    with Image.open(source) as im:
        im.convert('RGB').save(final, quality=94, method=6)
        thumb = im.convert('RGB')
        thumb.thumbnail((640, 480), Image.Resampling.LANCZOS)
        thumb.save(dest / 'thumb' / name, quality=86, method=6)
    item['final_asset'] = str(final.relative_to(ROOT))

path = ROOT / 'data/ahom.csv'
with path.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
by_id = {x['id']: x for x in items}
for row in rows:
    if row['id'] not in by_id:
        continue
    if row['scene_image']:
        raise SystemExit(f"Row already illustrated: {row['id']}")
    row['scene_image'] = by_id[row['id']]['final_asset']
    row['status'] = 'illustrated'
    extra_sources = {
        'AHOM-257': 'https://sivasagar.assam.gov.in/tourist-place-detail/334',
        'AHOM-264': 'https://sivasagar.assam.gov.in/tourist-place-detail/328',
        'AHOM-265': 'https://en.wikipedia.org/wiki/Buranji',
    }
    if row['id'] in extra_sources:
        row['sources'] = row['sources'].rstrip('; ') + '; ' + extra_sources[row['id']]
    limits = {
        'AHOM-255': 'Anonymous troops depict the riverine breakthrough and its aftermath; Gadadhar is not personally placed on the battlefield. Exact fort layout is reconstructed.',
        'AHOM-256': 'Confiscation and displacement are shown without graphic violence. Gadadhar is absent; motives remain debated.',
        'AHOM-257': 'The painting selects Namdang bridge construction; Rangnath Dol is a separate site and is not placed beside the bridge. Construction methods and stone arrangement are interpretive.',
        'AHOM-258': 'Depicts preparations for the proposed campaign, which was not launched, rather than a conquest of Bengal. The route sketch is illustrative.',
        'AHOM-259': 'Rudra and Siva appear in an imagined Guwahati camp deathbed scene. Exact words, witnesses and furnishings are not authenticated.',
        'AHOM-260': 'The document handover illustrates royal patronage, not an authenticated ceremony. Temple courtyard and grant format are reconstructed.',
        'AHOM-261': 'Workshop staging and the appearances of Sukumar Barkaith, Dilbar and Dosai are provisional. Painted folios are decorative reconstructions, not manuscript facsimiles.',
        'AHOM-262': 'Sarbeswari receives state papers as Bar Raja with Siva nearby. The ceremony is illustrative; accounts vary on her earlier name.',
        'AHOM-263': 'Kirti Chandra presents an accession order at court. The deceased Pramatta is absent; the ceremony is interpretive.',
        'AHOM-264': 'Shows a general 1750s worksite. Sources differ between 1752 and 1758; scaffolding, work methods and palace proportions are reconstructed.',
        'AHOM-265': 'Selected chronicles are destroyed while other records survive. Exact timing, participants and staging are uncertain; the king is absent.',
    }
    note = 'Modern artistic reconstruction; project character identities, costumes, buildings and staging are interpretive. ' + limits[row['id']]
    row['notes'] = (row['notes'].strip() + ' ' + note).strip()
with path.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(HERE / 'manifest.json').write_text(json.dumps(items, indent=2) + '\n')
board = Image.new('RGB', (1440, 6 * 354), '#f3efe6')
draw = ImageDraw.Draw(board)
for i, item in enumerate(items):
    x, y = (i % 2) * 720, (i // 2) * 354
    with Image.open(ROOT / item['final_asset']) as im:
        im.thumbnail((696, 312), Image.Resampling.LANCZOS)
        board.paste(im, (x + 12, y + 8))
    draw.text((x + 14, y + 325), item['id'] + ' ' + item['slug'].replace('_', ' '), fill='#222222')
board.save(HERE / 'preview.jpg', quality=92)
print(f'Imported {len(items)} scenes, thumbnails and PNG masters.')
