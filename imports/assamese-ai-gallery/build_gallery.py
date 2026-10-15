"""Rebuild static catalogue JS and thumbnails after deliberate catalogue updates."""
import json,pathlib,hashlib
from PIL import Image,ImageOps
BASE=pathlib.Path(__file__).resolve().parent
data=json.loads((BASE/'catalog.json').read_text())
(BASE/'thumbnails').mkdir(exist_ok=True)
for row in data['images']:
    source=BASE/row['file']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Original checksum mismatch: '+row['file'])
    row['thumbnail']='thumbnails/'+row['id']+'.webp'
    with Image.open(source) as im:
        image=ImageOps.exif_transpose(im).convert('RGB');image.thumbnail((420,280));image.save(BASE/row['thumbnail'],'WEBP',quality=76,method=6)
data['metadata']['count']=len(data['images'])
(BASE/'catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(BASE/'catalog.js').write_text('window.AI_GALLERY_CATALOG='+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n')
for name in ['index.html']:(BASE/name).write_text((BASE/'gallery-template.html').read_text())
print('Built',len(data['images']),'verified originals and thumbnails')
