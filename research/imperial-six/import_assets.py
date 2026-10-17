"""Import the inspected imperial-six generation outputs and update only their rows."""
import csv
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
items = json.loads((HERE / 'manifest.json').read_text())
dest = ROOT / 'media/scenes/ahom/1497-1603-imperial-expansion'
archive = ROOT / 'archive/imperial-six'
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
    item['review'] = 'Visually inspected: character identity, single main figures, scene coherence, local biome and architectural context.'

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
    extra = {
        'AHOM-238': ' The rural registration is illustrative; no fully developed later paik bureaucracy is implied.',
        'AHOM-239': ' Dimapur architecture and campaign staging are interpretive; no authenticated portraits of Khunkhara or Detsung are shown.',
        'AHOM-240': ' Non-graphic reconstruction of the remembered last battle; no exact personal duel with Turbak is asserted. Phrasengmung is not shown alive.',
        'AHOM-241': ' Painting shows campaign aftermath at Dimapur, not Detsung dying there; his death is placed during pursuit at Jangmarang. Pillar placement and damage are interpretive.',
        'AHOM-242': ' Depicts the moment before the attack. Suklenmung and the queen are absent; their complicity remains an allegation.',
        'AHOM-243': ' Painting depicts Sankardeva departing after Hari’s execution. No individual character sheet exists for either; appearance is provisional and the teacher is shown mostly from behind. Suklenmung is not physically shown.',
    }
    note += extra[row['id']]
    row['notes'] = (row['notes'].strip() + ' ' + note).strip()
with path.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(HERE / 'manifest.json').write_text(json.dumps(items, indent=2) + '\n')

# A contact sheet is a review artifact, not an alternative to generated artwork.
board = Image.new('RGB', (1440, 3 * 354), '#f3efe6')
draw = ImageDraw.Draw(board)
for i, item in enumerate(items):
    x, y = (i % 2) * 720, (i // 2) * 354
    with Image.open(ROOT / item['final_asset']) as im:
        im.thumbnail((696, 312), Image.Resampling.LANCZOS)
        board.paste(im, (x + 12, y + 8))
    draw.text((x + 14, y + 325), item['id'] + '  ' + item['slug'].replace('_', ' '), fill='#222222')
board.save(HERE / 'preview.jpg', quality=92)
print('Imported 6 scenes and 6 thumbnails; saved PNG masters and review contact sheet.')
