import csv, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
items = json.loads((HERE / 'manifest.json').read_text())
dest = ROOT / 'media/scenes/ahom/1826-1833-early-british-resistance'
archive = ROOT / 'archive/british-resistance-two'
archive.mkdir(parents=True, exist_ok=True)
(dest / 'thumb').mkdir(parents=True, exist_ok=True)
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
    row['main_people'] = by_id[row['id']]['main_people']
    sources = by_id[row['id']].get('additional_sources', [])
    for source in sources:
        if source not in row['sources']:
            row['sources'] = row['sources'].rstrip('; ') + '; ' + source
    note = 'Modern artistic reconstruction with provisional appearances; appearance, material details and staging are interpretive. ' + by_id[row['id']]['limitation']
    row['notes'] = (row['notes'].strip() + ' ' + note).strip()
with path.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(HERE / 'manifest.json').write_text(json.dumps(items, indent=2) + '\n')
board = Image.new('RGB', (1440, 354), '#f3efe6')
draw = ImageDraw.Draw(board)
for i, item in enumerate(items):
    x, y = (i % 2) * 720, (i // 2) * 354
    with Image.open(ROOT / item['final_asset']) as im:
        im.thumbnail((696, 312), Image.Resampling.LANCZOS)
        board.paste(im, (x + 12, y + 8))
    draw.text((x + 14, y + 325), item['id'] + ' ' + item['slug'].replace('_', ' '), fill='#222222')
board.save(HERE / 'preview.jpg', quality=92)
print(f'Imported {len(items)} scenes, thumbnails and PNG masters.')
