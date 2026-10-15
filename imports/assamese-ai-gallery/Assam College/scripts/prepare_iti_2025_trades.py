import json,re
from collections import defaultdict
import pdfplumber

PDF='/tmp/assam_iti_2025_counselling.pdf'
TARGETS={502:'Dhansiri',503:'Dudhnoi',504:'Pathsala',505:'Sootea',506:'Dibyang',
         507:'Boko',508:'Kajalgaon',509:'Lahowal',510:'Bokajan',511:'For Women, Nalbari',
         512:'Kazigaon',513:'Ballamguri',514:'Salakati'}
group=defaultdict(set)
with pdfplumber.open(PDF) as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                if len(row)>=4 and row[0] and row[1] and row[0]!='Institute':
                    group[row[0].replace('\n',' ').strip()].add(row[1].replace('\n',' ').strip())

out={}
for row,token in TARGETS.items():
    candidates=[(k,v) for k,v in group.items() if token.lower() in k.lower()]
    assert len(candidates)==1,(row,candidates)
    trades=set()
    for raw in candidates[0][1]:
        raw=re.sub(r'\s*[-–]\s*NCVT\s+Under\s+IMC\s*$', '', raw, flags=re.I)
        clean=re.sub(r'\s*[-–]\s*(?:N?SCVT|SIMC)(?:\s+under\s+IMC)?\s*$', '',raw,flags=re.I)
        clean=re.sub(r'\s+(?:N?SCVT|SIMC)\s+under\s+IMC\s*$', '',clean,flags=re.I)
        trades.add(clean.strip())
    out[row]='; '.join(sorted(trades))
with open('/tmp/assam_iti_2025_trades.json','w') as f:json.dump(out,f,indent=2)
print('rows',len(out),'trades',sum(len(v.split(';')) for v in out.values()))
