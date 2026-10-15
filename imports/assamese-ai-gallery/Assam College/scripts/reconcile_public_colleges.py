import difflib
import json
import re
import unicodedata

import pdfplumber
from openpyxl import load_workbook

ROOT = '/home/angsuman/extra_spac/Assam College'
BOOK = f'{ROOT}/Assam_Colleges_Complete_Directory.xlsx'
RUSA = '/tmp/assam_rusa_337.pdf'
LIST301 = '/tmp/assam_301_colleges.pdf'


def norm(s):
    s = unicodedata.normalize('NFKD', s).lower().replace('’', "'")
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\b(the|govt|government|degree|model|autonomous|college|mahavidyalaya|pandit|pduam)\b', '', s)
    return ' '.join(s.split())


wb = load_workbook(BOOK, read_only=True)
existing = [r[1] for r in list(wb.active.values)[1:]]
source = {}
with pdfplumber.open(RUSA) as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table[1:]:
                for i in (0, 2, 4):
                    if row[i] and row[i].strip().isdigit() and row[i + 1]:
                        source[int(row[i])] = row[i + 1].replace('\n', ' ').strip()
source.update({44: 'AL Choudhury College', 156: 'Beltola College', 268: 'Gauhati College'})

matched_below_095 = {
    18, 19, 27, 35, 39, 50, 53, 54, 59, 60, 65, 66, 72, 74, 80, 87, 89, 93,
    103, 104, 105, 106, 110, 115, 121, 124, 131, 132, 137, 144, 147, 154,
    158, 159, 163, 164, 167, 168, 178, 189, 198, 201, 205, 226, 227, 237,
    238, 260, 263, 265, 280, 281, 282, 284, 285, 290, 302, 309, 321, 326,
    335, 337, 44, 268,
}
missing = []
for n, name in sorted(source.items()):
    best = max(existing, key=lambda h: difflib.SequenceMatcher(None, norm(name), norm(h)).ratio())
    score = difflib.SequenceMatcher(None, norm(name), norm(best)).ratio()
    if score < .95 and n not in matched_below_095:
        missing.append({'source_id': n, 'name': name, 'best_match': best, 'score': round(score, 2)})

districts = ['Baksa', 'Barpeta', 'Biswanath', 'Bongaigaon', 'Cachar', 'Charaideo', 'Chirang', 'Darrang', 'Dhemaji', 'Dhubri', 'Dibrugarh', 'Dima Hasao', 'Goalpara', 'Golaghat', 'Hailakandi', 'Hojai', 'Jorhat', 'Kamrup (M)', 'Kamrup (R )', 'Karbi Anglong', 'Karimganj', 'Kokrajhar', 'Lakhimpur', 'Majuli', 'Morigaon', 'Nagaon', 'Nalbari', 'Sivasagar', 'Sonitpur', 'South Salmara', 'Tinsukia', 'Udalguri']
old = []
with pdfplumber.open(LIST301) as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                if len(row) >= 3 and row[0] and row[0].strip().isdigit() and row[1] and row[2]:
                    old.append((row[1].replace('\n', ' ').strip(), row[2].replace('\n', ' ').strip()))

for item in missing:
    best_name, best_district = max(old, key=lambda x: difflib.SequenceMatcher(None, norm(item['name']), norm(x[0])).ratio())
    district_score = difflib.SequenceMatcher(None, norm(item['name']), norm(best_name)).ratio()
    item['district'] = best_district if district_score >= .70 else ''
    item['district_match'] = best_name
    item['district_score'] = round(district_score, 2)

print('source', len(source), 'missing candidates', len(missing), 'old district rows', len(old))
for item in missing:
    print(f"{item['source_id']:3} {item['name']:<61} {item['district']:<16} {item['district_score']}")
with open('/tmp/assam_missing_rusa.json', 'w') as f:
    json.dump(missing, f, indent=2)
