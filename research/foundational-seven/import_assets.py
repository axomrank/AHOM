"""Import the inspected foundational-seven generation outputs and update only their rows."""
import csv
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
items = json.loads((HERE / 'manifest.json').read_text())
dest = ROOT / 'media/scenes/ahom/1228-1497-foundational-era'
archive = ROOT / 'archive/foundational-seven'
archive.mkdir(parents=True, exist_ok=True)
(dest / 'thumb').mkdir(exist_ok=True)
for item in items:
    name = f"{item['id']}_{item['slug']}.webp"
    final = dest / name
    source = Path(item.get('correction_path', item['generated_path']))
    if final.exists():
        raise SystemExit(f'Refusing to overwrite {final}')
    shutil.copy2(source, archive / f"{item['id']}-final.png")
    with Image.open(source) as im:
        im.convert('RGB').save(final, quality=94, method=6)
        thumb = im.convert('RGB')
        thumb.thumbnail((640, 480), Image.Resampling.LANCZOS)
        thumb.save(dest / 'thumb' / name, quality=86, method=6)
    item['final_asset'] = str(final.relative_to(ROOT))
    item['review'] = 'Visually inspected; targeted character duplication corrections applied where needed.'

path = ROOT / 'data/ahom.csv'
with path.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
by_id = {x['id']: x for x in items}
for row in rows:
    if row['id'] not in by_id:
        continue
    row['scene_image'] = by_id[row['id']]['final_asset']
    row['status'] = 'illustrated'
    note = 'Modern artistic reconstruction using project character sheets; setting, architecture and staging are interpretive.'
    if row['id'] == 'AHOM-235':
        row['people'] = 'sudangphaa; nangchukham-borgohain; tasim-pou-borgohain'
        row['main_people'] = 'nangchukham-borgohain; tasim-pou-borgohain'
        note += ' Painting depicts the two negotiating commanders; Sudangphaa is not physically shown.'
    if row['id'] == 'AHOM-278':
        note += ' Empty royal seat and unnamed ministers; the deceased Sukhrangphaa is not depicted alive.'
    if row['id'] == 'AHOM-279':
        note += ' The river withdrawal and opposing Chutia ruler are illustrative, not a documented personal confrontation; campaign dates vary.'
    if row['id'] == 'AHOM-280':
        note += ' Exact chronology and Ahom military participation are uncertain; the Sultan at the ford is an illustrative reconstruction. Sudangphaa is not shown in battle.'
    row['notes'] = (row['notes'].strip() + ' ' + note).strip()
with path.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(HERE / 'manifest.json').write_text(json.dumps(items, indent=2) + '\n')

# A contact sheet is a review artifact, not an alternative to generated artwork.
board = Image.new('RGB', (1440, 4 * 354), '#f3efe6')
draw = ImageDraw.Draw(board)
for i, item in enumerate(items):
    x, y = (i % 2) * 720, (i // 2) * 354
    with Image.open(ROOT / item['final_asset']) as im:
        im.thumbnail((696, 312), Image.Resampling.LANCZOS)
        board.paste(im, (x + 12, y + 8))
    draw.text((x + 14, y + 325), item['id'] + '  ' + item['slug'].replace('_', ' '), fill='#222222')
board.save(HERE / 'preview.jpg', quality=92)
print('Imported 7 scenes and 7 thumbnails; saved PNG masters and review contact sheet.')
