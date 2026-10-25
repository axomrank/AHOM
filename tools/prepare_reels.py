#!/usr/bin/env python3
"""Catalogue distinct shots, generate web posters, and record excluded alternate encodes.

Never modifies source footage. Run before tools/build.py after adding films.
The Clean folder repeats the original films; 14_cut is a shorter naming-scene cut.
clean2 contains 22 distinct shots, including two views of the assassination.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Scene links are explicit editorial matches, not inferred from file numbering.
ORIGINAL_SCENES = ['001','006','009','015','015','016','017','021','017','017','022','024','026','030','032','036','041','046','047','047','048','052','278','053','055','279','240']
ORIGINAL_DATES = ['1215','1215–1228','1228','1230s','1235–1240','c. 1240–1250','1215–1253','1253','1253','1253','1268','1268','c. 1270','c. 1275','c. 1277','c. 1279','c. 1305','c. 1308','c. 1310','c. 1310','c. 1335','c. 1339','1364–1369','1376','1376–1380','1380–1387','1532–1533']
NEW = [
    ('pregnant-queen-cast-adrift', 'The pregnant queen is cast adrift', '056'),
    ('sudangphaa-born-habung', 'Prince Sudangphaa is born at Habung', '058'),
    ('sudangphaa-coronation', 'Sudangphaa takes the throne', '066'),
    ('tipam-conspirators', 'The feast trap for the Tipam conspirators', '236'),
    ('bhuyan-marriage-alliance', 'Sudangphaa and the Bhuyan marriage alliance', '072'),
    ('nongnyang-treaty', 'The boundary treaty at Nongnyang Lake', '235'),
    ('tangshu-raids', 'The Tangshu raids on the lowlands', '078'),
    ('kachari-war', 'The battle against the Kacharis', '082'),
    ('kachari-peace', 'Peace with the Kacharis', '083'),
    ('suhenphaa-assassination', 'The assassination of Suhenphaa', '087'),
    ('queen-naga-village', 'The exiled queen reaches a Naga village', '090'),
    ('konseng-born', 'Konseng is born in the Naga hills', '091'),
    ('konseng-borpatrogohain', 'Konseng becomes Barpatragohain', '093'),
    ('swarganarayan-title', 'Suhungmung adopts the title Swarganarayan', '094'),
    ('count-fighting-men', 'Suhungmung orders a count of fighting men', '238'),
    ('sadiya-captured', 'The Ahom banner rises at Sadiya', '096'),
    ('bengal-naval-campaign', 'Suhungmung commands the river campaign', '103'),
    ('march-dimapur', 'The army marches toward Dimapur', '239'),
    ('ruins-dimapur', 'Soldiers patrol the ruins of Dimapur', '241'),
    ('mula-gabharu-charge', 'Mula Gabharu leads the charge', '240'),
    ('suhungmung-assassination-palace', 'The assassination of Suhungmung: the palace', '242'),
    ('suhungmung-assassination-servant', 'The assassination of Suhungmung: the servant', '242'),
]


def main():
    cfg = json.loads((ROOT / 'data/eras.json').read_text())
    runtime = json.loads((ROOT / 'data/site.js').read_text().split('window.AHOM = ', 1)[1].strip().rstrip(';'))
    scenes = {sid: s for s in runtime['scenes'] for sid in [s['id'], *s.get('alias', [])]}
    reels = cfg['reels'][:27]
    for r, sid, date in zip(reels, ORIGINAL_SCENES, ORIGINAL_DATES):
        r['scene'] = 'AHOM-' + sid
        r['src'] = f"media/reels/{r['id']}.mp4"
        r['year'] = date
    reels[18]['title'] = 'The birth of Chao Pulai'
    files = sorted((ROOT / 'media/reels/clean2').glob('*.mp4'))
    if len(files) != len(NEW):
        raise SystemExit(f'Expected {len(NEW)} reviewed new clips, found {len(files)}; update the editorial mapping.')
    for i, (path, (slug, title, sid)) in enumerate(zip(files, NEW), 28):
        reels.append({'id': f'{i:02d}-{slug}', 'title': title, 'scene': 'AHOM-' + sid,
                      'src': path.relative_to(ROOT).as_posix(), 'line': '', 'translation': ''})
    for r in reels:
        s = scenes[r['scene']]
        r.setdefault('year', s['date'])
        r['era'] = s['era']
        r['poster'] = f"media/reels/{r['id']}.webp"
        r['description'] = s['summary']
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_format', '-show_streams', '-of', 'json', str(ROOT / r['src'])]))
        r['duration'] = round(float(probe['format']['duration']), 2)
        r['hasAudio'] = any(x['codec_type'] == 'audio' for x in probe['streams'])
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(min(2, r['duration']/3)), '-i', str(ROOT / r['src']),
                        '-frames:v', '1', '-vf', 'scale=420:-2', '-quality', '82', '-y', str(ROOT / r['poster'])], check=True)
    cfg['reels'] = reels
    (ROOT / 'data/eras.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
    selected = {r['src'] for r in reels}
    inventory = [{'file': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                  'published': p.relative_to(ROOT).as_posix() in selected,
                  'reason': 'Distinct published shot' if p.relative_to(ROOT).as_posix() in selected else 'Alternate clean encode or shortened cut of an existing film'}
                 for p in sorted((ROOT / 'media/reels').rglob('*.mp4'))]
    (ROOT / 'research/reel-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(f'{len(reels)} distinct films, {len(inventory)-len(reels)} alternate copies/cuts excluded; posters generated.')


if __name__ == '__main__':
    main()
