"""Create a local, checksum-verified snapshot. Never commits the ZIP to Git."""
import json,pathlib,hashlib,zipfile,datetime
BASE=pathlib.Path(__file__).resolve().parent
catalog=json.loads((BASE/'catalog.json').read_text())
for row in catalog['images']:
    if hashlib.sha256((BASE/row['file']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Checksum mismatch: '+row['file'])
dest=BASE/'backups';dest.mkdir(exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
target=dest/f'Assamese-AI-gallery-{stamp}.zip'
paths=[p for p in BASE.rglob('*') if p.is_file() and not any(part in {'.git','backups','node_modules','output','.playwright-cli'} for part in p.relative_to(BASE).parts)]
with zipfile.ZipFile(target.with_suffix('.partial'),'w',compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
    for p in paths:archive.write(p,p.relative_to(BASE))
with zipfile.ZipFile(target.with_suffix('.partial')) as archive:
    if archive.testzip() is not None:raise ValueError('Backup CRC check failed')
    for row in catalog['images']:
        if hashlib.sha256(archive.read(row['file'])).hexdigest()!=row['sha256']:raise ValueError('Backup image checksum mismatch')
target.with_suffix('.partial').replace(target)
target.with_suffix('.sha256').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name+'\n')
print('Verified backup:',target)
