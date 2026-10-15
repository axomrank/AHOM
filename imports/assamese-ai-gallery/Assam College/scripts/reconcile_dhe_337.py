import difflib, json, re, unicodedata
import pdfplumber
from openpyxl import load_workbook

BOOK='Assam_Colleges_Complete_Directory.xlsx'
SOURCE='/tmp/assam_337_district_affiliation.pdf'
OUT='/tmp/assam_dhe_337.json'

def norm(s):
    s=unicodedata.normalize('NFKD',s).lower().replace('’',"'")
    s=re.sub(r'[^a-z0-9]+',' ',s)
    s=re.sub(r'\b(the|govt|government|degree|model|autonomous|college|mahavidyalaya|pandit|pduam)\b','',s)
    return ' '.join(s.split())

existing=[r[1] for r in list(load_workbook(BOOK,read_only=True).active.values)[1:]]
rows=[]
with pdfplumber.open(SOURCE) as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                if len(row)>=7 and row[0] and row[0].strip().isdigit():
                    n,name,district,a,s,c,univ=row[:7]
                    name=name.replace('\n',' ').strip()
                    district=district.replace('\n',' ').strip()
                    univ=univ.replace('Dirbugarh','Dibrugarh').strip()
                    streams=[v for v in (a,s,c) if v and v!='0']
                    best=max(existing,key=lambda x:difflib.SequenceMatcher(None,norm(name),norm(x)).ratio())
                    score=difflib.SequenceMatcher(None,norm(name),norm(best)).ratio()
                    rows.append(dict(source_id=int(n),name=name,district=district,streams=streams,university=univ,best_match=best,score=round(score,2)))
assert len(rows)==337
with open(OUT,'w') as f:json.dump(rows,f,indent=2)
missing=[r for r in rows if r['score']<.95]
print('missing candidates',len(missing))
for r in missing:print(f"{r['source_id']:3} {r['name']:<55} {r['district']:<18} {r['score']:.2f} {r['best_match']}")
