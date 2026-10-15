"""Read-only preparation of the official 2025 government ITI roster and trade evidence."""
import json
import re
from collections import defaultdict

import pdfplumber
from openpyxl import load_workbook

BOOK='Assam_Colleges_Complete_Directory.xlsx'
PDF='/tmp/assam_iti_2025_counselling.pdf'
OUT='/tmp/assam_iti_roster_reconciled.json'

def key(name):
    name=name.lower().replace('borpeta','barpeta').replace('titabor','titabar')
    name=name.replace('regional industrial training institute','industrial training institute')
    name=re.sub(r'\b(?:govt|government|industrial|training|institute|iti)\b',' ',name)
    name=re.sub(r'\b(?:for)\b',' ',name)
    name=re.sub(r'[^a-z]+',' ',name)
    name=' '.join(name.split())
    if name=='sivasagar':name='gargaon'
    if name=='silchar':name='srikona'
    if name=='lahowal dibrugarh':name='lahowal'
    if name=='dibyang dibrugarh':name='dibyang'
    if name=='south salmara mankachar':name='south salmara'
    return name

def trade(raw):
    raw=raw.replace('\n',' ').strip()
    raw=re.sub(r'\s*[-–]\s*(?:NCVT|SCVT|SIMC|NIMC)(?:\s+under\s+IMC)?\s*$', '',raw,flags=re.I)
    raw=re.sub(r'\s+(?:NCVT|SCVT|SIMC|NIMC)(?:\s+under\s+IMC)?\s*$', '',raw,flags=re.I)
    return raw.strip(' -–')

groups=defaultdict(set)
with pdfplumber.open(PDF) as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                if len(row)>=2 and row[0] and row[1] and ('ITI' in row[0] or 'Industrial Training' in row[0]):
                    groups[key(row[0])].add(trade(row[1]))

assert len(groups)==45,len(groups)
rows=list(load_workbook(BOOK,read_only=True,data_only=True).active.values)[1:]
iti=[(r[0]+1,r[1]) for r in rows if r[2]=='ITI']
found={};excess=[]
for row,name in iti:
    k=key(name)
    if k in groups:
        if k in found:raise ValueError(f'duplicate {k}')
        found[k]={'row':row,'old_name':name,'trades':'; '.join(sorted(groups[k]))}
    else:excess.append({'row':row,'name':name})
assert len(found)==45,(len(found),set(groups)-set(found))
assert len(excess)==10,(len(excess),excess)
out={'matched':found,'excluded':excess}
with open(OUT,'w') as f:json.dump(out,f,indent=2,ensure_ascii=False)
print('matched',len(found),'excluded',len(excess),'trade names',sum(len(x['trades'].split(';')) for x in found.values()))
print('Excluded:')
for x in excess:print(x)
