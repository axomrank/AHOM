"""Organize downloaded reference photos, preserving bytes, attribution and a move ledger."""
from collections import Counter
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import shutil

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1] / 'images/referance/ahom'
CAT = ROOT / '00_catalogue'
FAMILIES = {
    '01_ahom_royal_and_civic': 'Ahom royal and civic buildings',
    '02_tai_ahom_funerary': 'Tai-Ahom funerary tradition',
    '03_hindu_temple_architecture': 'Hindu temple architecture',
    '04_mixed_and_memorial': 'Mixed architecture and memorials',
    '05_water_and_landscape': 'Tanks and landscape context',
    '06_material_culture': 'Objects and military material culture',
    '07_modern_site_context': 'Modern visitor infrastructure and nature',
    '90_needs_identity_review': 'Monument identity needs review',
    '99_excluded_unrelated': 'Unrelated geography — excluded',
}

def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in rows)

def shot(title):
    t = title.lower()
    if re.search(r'information|signage|signboard|sign board|information tablet|display board|welcome.+sign', t):
        return '05_information_boards'
    if re.search(r'carv|relief|ornament|terracotta|sculpt|texture|pattern|design|brick|wall', t):
        return '03_details_and_materials'
    if re.search(r'interior|inside|chamber|corridor|passage|stair|tunnel|doorway|door|steps|entrance', t):
        return '02_interiors_and_access'
    if re.search(r'landscape|tank|lake|pukhuri|pond|garden|premises|campus|grounds|bird.eye|panoram|view from', t):
        return '04_site_and_landscape'
    return '01_general_views'

def classify(row, source):
    old = row.get('original_collection_file', row['file'])
    group, filename = old.split('/', 1)
    subject_filename = filename.split('__', 1)[-1] if group == 'official-sivasagar' else filename
    t = (row['title'] + ' ' + subject_filename).lower()
    cats = source.get('categories', [])
    period = 'Object or feature date unverified; do not infer from photo date'
    note = 'Classified from source title/category; not a full visual authentication.'
    family, monument = '90_needs_identity_review', group
    if group == 'official-sivasagar':
        group = filename.split('__')[0]
    if ('Category:Rudrasagar Lake' in cats and group == 'rudrasagar') or re.search(r'neer.?mahal|tripura|rodhrasagar', t):
        return '99_excluded_unrelated', 'tripura_rudrasagar_neermahal', '20th-century palace / unrelated Tripura lake', 'Wrong Rudrasagar: Tripura, not Assam. Exclude from all Ahom image prompts.'
    if re.search(r'cannon|\bcanons?\b|bortup|bortope|bortoop|bortope', t):
        return '06_material_culture', 'cannons', 'Individual weapon date unverified', 'Object reference only; not architecture and not automatically appropriate for 15th-century scenes.'
    if 'iron boat' in t:
        return '06_material_culture', 'charaideo_iron_boat', period, 'Artefact and its present display shelter; do not infer early construction details.'
    if re.search(r'swamphen|cormorant|eurasian coot|rain sheds?|paved pathways?|tourists|moorhen', t) or 'এজোপা গছ' in t:
        return '07_modern_site_context', group, 'Modern photograph / visitor infrastructure / wildlife', 'Landscape or visitor context only. Do not copy modern site works into historical scenes.'
    if group in ['charaideo-moidams', 'maidams']:
        family, monument = '02_tai_ahom_funerary', 'charaideo' if group == 'charaideo-moidams' else 'other_maidams'
        period = 'Tradition spans 13th–19th centuries; individual visible mound and restoration must be dated'
        note = 'Tai-Ahom funerary reference. Mounds are not palace or dwelling designs; modern shelters, gates and landscaping require exclusion.'
        if re.search(r'toron|moidam road|iron boat shed', t):
            family = '07_modern_site_context'
    elif group in ['rang-ghar','talatal-ghar','kareng-ghar','golaghar','gola-ghar','namdang-stone-bridge']:
        family = '01_ahom_royal_and_civic'
        monument = {'gola-ghar':'golaghar'}.get(group, group)
        period = 'Surviving masonry predominantly 18th century; not direct evidence for a 15th-century palace'
        if group == 'namdang-stone-bridge':
            period = 'Early 18th-century bridge; not evidence for a 15th-century town layout'
        if group == 'talatal-ghar' and re.search(r'kareng', t) and not re.search(r'talatal|talataal|talatol|talat', t):
            family, monument = '90_needs_identity_review', 'kareng_or_talatal'
            note = 'Title says Kareng Ghar but source category says Talatal Ghar; identify from the actual photograph before use.'
        if group == 'kareng-ghar' and 'n-as-34' in t:
            family, monument = '90_needs_identity_review', 'kareng_or_talatal'
            note = 'Source monument identifier/title conflicts with the collected Kareng group; verify identity before use.'
    elif group == 'ranganath-temple':
        family, monument, period = '03_hindu_temple_architecture', 'ranganath_shiva_temple', 'Early 18th century'
    elif group == 'fakuwa-doul':
        family, monument, period = '04_mixed_and_memorial', 'fakuwa_doul_memorial', '1703–1704 according to district source'
        note = 'Memorial/shrine with disputed popular burial identification. Keep separate from authenticated Tai-Ahom maidams and generic royal palace references.'
    elif group == 'ghanashyam-house' or re.search(r'ghanashyam|ghono|nati gohain', t):
        family, monument, period = '04_mixed_and_memorial', 'ghanashyam_house', '18th century'
        note = 'District source describes Hindu and Islamic architectural influences. Do not treat this masonry building as a 15th-century Ahom dwelling template.'
    elif group == 'na-pukhuri':
        family, monument, period = '05_water_and_landscape', 'na_pukhuri_assam', 'Later Ahom-period waterworks; visible pavilion date unverified'
    elif group in ['ranganath-fakuwa']:
        if 'fakua' in t or 'fakuwa' in t:
            family, monument, period = '04_mixed_and_memorial', 'fakuwa_doul_memorial', '1703–1704 according to district source'
            note = 'Memorial/shrine; burial interpretation requires qualification.'
        else:
            family, monument, period = '03_hindu_temple_architecture', 'ranganath_shiva_temple', 'Early 18th century'
    elif group in ['sivasagar','sivasagar-tank-temples','joysagar','gaurisagar','rudrasagar','namti-temples','jagadhatri-lakhisagar','thowra-doul','hara-gauri-doul','gorokhiya-doul']:
        site = {'sivasagar-tank-temples':'sivasagar','jagadhatri-lakhisagar':'jagadhatri_lakhisagar'}.get(group,group)
        temple = re.search(r'dol|doul|doll|doul|temple|shiv|siva|devi|vishnu|keshav|joydol|devighar|devi.ghar|দ’ল|শিৱদল', t)
        if temple or group in ['namti-temples','jagadhatri-lakhisagar','thowra-doul','hara-gauri-doul','gorokhiya-doul']:
            family = '03_hindu_temple_architecture'
            deity = 'complex'
            if re.search(r'devi|durga|devighar|দেৱী', t): deity = 'devi'
            elif re.search(r'vishnu|keshav|joy.?dol|joy.?doul|joydoll|jaydol', t): deity = 'vishnu_joydol'
            elif re.search(r'shiv|siva|shib|sibodol|শিৱ', t): deity = 'shiva'
            monument = site + '_' + deity
            period = 'Later Ahom-period Hindu temple; check monument-specific date before generation'
            note = 'Hindu temple architecture, with Ahom patronage recorded separately. Do not use its shrine tower, deity reliefs or temple plan as a generic Ahom royal/vernacular template.'
        else:
            family, monument = '05_water_and_landscape', site + '_tank_and_setting'
            period = 'Later Ahom-period tank / present-day landscape; specific features need dating'
            note = 'Water and landscape context only. Background temples and modern college/town buildings are not early Ahom architecture evidence.'
    return family, monument, period, note

def gallery(rows):
    cards=[]
    thumbs=CAT/'thumbnails';thumbs.mkdir(exist_ok=True)
    for row in rows:
        thumb=thumbs/(row['reference_id']+'.webp')
        if not thumb.exists():
            with Image.open(ROOT/row['file']) as im:
                preview=ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(300,210))
                preview.save(thumb,'WEBP',quality=65)
        esc=lambda x:html.escape(str(x),quote=True)
        search=esc(' '.join(str(row.get(k,'')) for k in ['title','family','monument','view_type','period_note','source_provider']))
        cards.append(f'<article data-family="{esc(row["family"])}" data-search="{search.lower()}"><a href="{esc(row["file"])}"><img loading="lazy" src="00_catalogue/thumbnails/{row["reference_id"]}.webp" alt="{esc(row["title"])}"></a><h3>{esc(row["title"])}</h3><p>{esc(row["monument"])} · {esc(row["view_type"])}</p><p class="badge">{esc(FAMILIES[row["family"]])}</p><small>{esc(row["period_note"])}</small><p><a href="{esc(row["source_page"])}">Source / licence</a> · <a href="{esc(row["file"])}">Full image</a></p></article>')
    options=''.join(f'<option value="{k}">{html.escape(v)}</option>' for k,v in FAMILIES.items())
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ahom reference library</title><style>body{font:15px system-ui;background:#f4f0e8;color:#202b26;margin:0}header{padding:24px;background:#17372d;color:white;position:sticky;top:0;z-index:2}h1{font-size:25px;margin:0 0 10px}header p{max-width:1000px}input,select{padding:10px;border:0;border-radius:5px;font:inherit;max-width:95%;margin:4px}input{width:420px}main{padding:22px;display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:16px}article{background:white;border-radius:8px;padding:12px;border:1px solid #ddd}img{width:100%;height:200px;object-fit:contain;background:#eee}h3{font-size:15px;overflow-wrap:anywhere}small{color:#61615d}.badge{font-size:12px;color:#285543}article p{font-size:13px}a{color:#245c78}header a{color:#bce8dc}[hidden]{display:none!important}</style><header><h1>Architecture reference library</h1><p>Hindu temple form is separate from Ahom royal/civic architecture. Patronage, religious tradition, building function and period are separate fields. Surviving 18th-century masonry is not a direct template for a 15th-century town. Classifications use source metadata; ambiguous items are labelled for review.</p><input id="search" type="search" placeholder="Search monument, material, interior, date…"><select id="family"><option value="">All usable groups (excludes unrelated)</option>OPTIONS<option value="all">Everything, including excluded</option></select><span id="count"></span><p><a href="IMAGE_CREATION_GUIDE.md">Image creation guide</a> · <a href="00_catalogue/reference-manifest.csv">Reference manifest</a></p></header><main>CARDS</main><script>const search=document.querySelector('#search'),family=document.querySelector('#family'),cards=[...document.querySelectorAll('article')];function filter(){let n=0;const q=search.value.trim().toLowerCase();for(const c of cards){const f=family.value;c.hidden=!(c.dataset.search.includes(q)&&(f==='all'||(f?c.dataset.family===f:c.dataset.family!=='99_excluded_unrelated')));if(!c.hidden)n++}document.querySelector('#count').textContent=n+' references'}search.addEventListener('input',filter);family.addEventListener('change',filter);filter();</script></html>'''
    (ROOT/'index.html').write_text(page.replace('OPTIONS',options).replace('CARDS',''.join(cards)))

def main():
    CAT.mkdir(exist_ok=True)
    legacy=CAT/'download_records';legacy.mkdir(exist_ok=True)
    source_catalog=ROOT/'catalogue.json'
    if not source_catalog.exists():source_catalog=legacy/'catalogue.json'
    source=json.loads(source_catalog.read_text())
    inputs=[]
    for sidecar in ROOT.rglob('*.source.json'):
        if CAT in sidecar.parents:continue
        row=json.loads(sidecar.read_text())
        old=row['file'];image=ROOT/old
        if not image.is_file():raise RuntimeError(f'Missing original image: {image}')
        inputs.append((sidecar,row,hashlib.sha256(image.read_bytes()).hexdigest()))
    if len(inputs)!=850:raise RuntimeError(f'Expected 850 source photos; found {len(inputs)}. Review new files before moving.')
    rows=[];moves=[]
    for sidecar,row,digest in inputs:
        old=row['file'];image=ROOT/old
        original=row.get('original_collection_file',old)
        pageid=image.name.split('_',1)[0]
        source_row=source.get(pageid,{})
        family,monument,period,note=classify(row,source_row)
        view=shot(row['title'])
        reference_id=('commons_'+pageid) if source_row else 'official_'+hashlib.sha1(image.name.encode()).hexdigest()[:12]
        new=Path(family)/monument/view/image.name
        destination=ROOT/new;destination.parent.mkdir(parents=True,exist_ok=True)
        if destination!=image:
            if destination.exists():raise RuntimeError(f'Collision: {destination}')
            shutil.move(str(image),str(destination))
        if hashlib.sha256(destination.read_bytes()).hexdigest()!=digest:raise RuntimeError('Image bytes changed')
        row.update(file=str(new),original_collection_file=original,reference_id=reference_id,family=family,architectural_tradition=FAMILIES[family],monument=monument,view_type=view,period_note=period,classification_note=note,classification_method='source metadata and user reference taxonomy; no full per-image visual audit',source_provider='Wikimedia Commons' if source_row else 'Government of Assam — Sivasagar district',patronage_context='Ahom-period context where identified; patronage does not determine architectural tradition' if family!='99_excluded_unrelated' else 'Unrelated Tripura collection',suitable_as_direct_15th_century_template=False,sha256=digest)
        target_sidecar=destination.with_suffix(destination.suffix+'.source.json')
        target_sidecar.write_text(json.dumps(row,ensure_ascii=False,indent=2))
        if sidecar!=target_sidecar:sidecar.unlink()
        rows.append(row);moves.append(dict(old_file=old,new_file=str(new),sha256=digest))
    rows.sort(key=lambda r:r['file'])
    (CAT/'reference-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    write_csv(CAT/'reference-manifest.csv',rows)
    ledger=CAT/'move-ledger.json'
    previous=json.loads(ledger.read_text()) if ledger.exists() else []
    ledger.write_text(json.dumps(previous+[m for m in moves if m['old_file']!=m['new_file']],ensure_ascii=False,indent=2))
    # Preserve download history; these records intentionally retain the original collection paths.
    for file in list(ROOT.iterdir()):
        if file.is_file() and file.suffix in ['.json','.csv','.log']:
            target=legacy/file.name
            if target.exists():continue
            shutil.move(str(file),str(target))
    for directory in sorted(ROOT.rglob('*'),key=lambda p:len(p.parts),reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):directory.rmdir()
    counts=Counter(r['family'] for r in rows)
    for family,count in counts.items():
        (ROOT/family/'README.md').write_text(f'# {FAMILIES[family]}\n\n{count} reference photographs. See the root IMAGE_CREATION_GUIDE.md before generating images. Each photo retains its source sidecar. Date and function must be checked separately from patronage.\n')
    summary=dict(total_photographs=len(rows),usable_geographic_collection=len(rows)-counts['99_excluded_unrelated'],excluded_unrelated=counts['99_excluded_unrelated'],groups=dict(counts),image_bytes_preserved=True)
    (CAT/'organization-summary.json').write_text(json.dumps(summary,indent=2))
    (ROOT/'.organized-reference-library.json').write_text(json.dumps(dict(manifest='00_catalogue/reference-manifest.json',schema_version=1),indent=2))
    gallery(rows)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
