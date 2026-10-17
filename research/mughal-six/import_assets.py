"""Import the inspected mughal-six generation outputs and update only their rows."""
import csv
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
items = json.loads((HERE / 'manifest.json').read_text())
dest = ROOT / 'media/scenes/ahom/1603-1681-mughal-ahom-wars'
archive = ROOT / 'archive/mughal-six'
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
        'AHOM-244': ' Marriage ceremony staging is illustrative; Mangaldoi parentage varies across sources.',
        'AHOM-245': ' Painting depicts the passage dispute being reported to Pratap Singha, not the later battle. No identified bride or Kachari commander is shown.',
        'AHOM-246': ' Balinarayan has a provisional face because no project sheet exists. Painting depicts asylum; Qasim Khan is not physically shown.',
        'AHOM-247': ' Night-action staging, boat designs and deployment are interpretive; Abu Bakr and Satrajit follow project sheets. Pratap Singha and Qasim Khan are not physically shown. Catalogue retains the 1615–1616 range.',
        'AHOM-248': ' The artwork selects Momai Tamuli directing river defence as a representative moment of the multi-year war. Pratap Singha and Allah Yar Khan are not physically shown; vessels and deployments are interpretive.',
        'AHOM-249': ' Workshop, hand tools and royal visit are illustrative. Small silver coin marks are not an authenticated transcription of a specific issue.',
    }
    note += extra[row['id']]
    if row['id'] == 'AHOM-247':
        row['main_people'] = 'abu-bakr; satrajit'
    if row['id'] == 'AHOM-248':
        row['main_people'] = 'momai-tamuli'
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
