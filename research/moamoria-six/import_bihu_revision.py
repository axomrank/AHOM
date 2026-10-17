import csv, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
revision = json.loads((HERE / 'AHOM-266-remake.json').read_text())
source = Path(revision['generated_path'])
dest = ROOT / 'media/scenes/ahom/1769-1817-moamoria-rebellions'
name = 'AHOM-266_Bihu_Ambush_on_Gaurinath_v02.webp'
final = dest / name
if final.exists():
    raise SystemExit('Version already exists; refusing to overwrite.')
shutil.copy2(source, ROOT / 'archive/moamoria-six/AHOM-266-final-v02.png')
with Image.open(source) as im:
    im.convert('RGB').save(final, quality=94, method=6)
    thumb = im.convert('RGB')
    thumb.thumbnail((640, 480), Image.Resampling.LANCZOS)
    thumb.save(dest / 'thumb' / name, quality=86, method=6)
revision['final_asset'] = str(final.relative_to(ROOT))

catalogue = ROOT / 'data/ahom.csv'
with catalogue.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
for row in rows:
    if row['id'] == 'AHOM-266':
        revision['previous_final_asset'] = row['scene_image']
        row['scene_image'] = revision['final_asset']
        row['notes'] += ' Revised Bihu troupe uses a user-supplied contemporary cultural photograph for dance gestures, cream/red textiles, dhol and pepa. Exact eighteenth-century festival costume and troupe staging remain interpretive; performers are not identified as attackers.'
with catalogue.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
items = json.loads((HERE / 'manifest.json').read_text())
for item in items:
    if item['id'] == 'AHOM-266':
        item['previous_final_asset'] = item['final_asset']
        item['final_asset'] = revision['final_asset']
        item['remake'] = revision
(HERE / 'manifest.json').write_text(json.dumps(items, indent=2) + '\n')
(HERE / 'AHOM-266-remake.json').write_text(json.dumps(revision, indent=2) + '\n')
board = Image.new('RGB', (1440, 1062), '#f3efe6')
draw = ImageDraw.Draw(board)
for i, item in enumerate(items):
    x, y = (i % 2) * 720, (i // 2) * 354
    with Image.open(ROOT / item['final_asset']) as im:
        im.thumbnail((696, 312), Image.Resampling.LANCZOS)
        board.paste(im, (x + 12, y + 8))
    draw.text((x + 14, y + 325), item['id'] + ' ' + item['slug'].replace('_', ' '), fill='#222222')
board.save(HERE / 'preview.jpg', quality=92)
print('Imported Bihu revision, preserved original and refreshed contact sheet.')
