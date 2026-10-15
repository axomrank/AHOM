import json,re,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1]/'academic_evidence'
for ident in sys.argv[1:]:
    p=E/f'college_{ident}.json'
    if not p.exists(): continue
    c=json.loads(p.read_text()); print('\n###',ident,c['college'])
    for ref in c['pages']:
        d=json.loads((E/ref['cache']).read_text()); t=d.get('text','')
        if not t: continue
        hits=[]
        for m in re.finditer(r'(?i)(?:post.?graduate|masters? (?:of|programme)|M\s*\.\s*(?:Sc|Com|A)\.?\s+(?:in|course)|PG (?:admission|course|programme)|programmes? offered)',t):
            s=re.sub(r'\s+',' ',t[max(0,m.start()-100):m.end()+380])
            if s not in hits:hits.append(s)
        if hits: print(ref['url'],'\n'+'\n'.join(hits[:8]))
