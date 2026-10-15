"""Prepare evidence-linked academic review data for the CSV and HTML.

Portal records describe published 2026–27 admissions; a portal listing alone is
not proof that a college's own prospectus agrees. A missing record is unknown.
"""
import csv, json, re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'academic_evidence'
UG_SOURCE='https://assamadmission.samarth.ac.in/index.php/site/vacancy-list'
PG_SOURCE='https://assamadmission.samarth.ac.in/pg/index.php/site/merit-list'
DATE='2026-10-03'
POSSIBLE_DUPLICATE={'83':'81','95':'262','265':'257','331':'332'}
NAV_DEPARTMENT_ADDITIONS={
    '163':['Banking and Insurance','Human Resource Management','Commercial Law'],
    '190':['Hindi','Computer Science'],
    '336':['Assamese','Economics','Education','English','Political Science','History','Computer Science'],
}
COLLEGE_UG_OVERRIDES={
    '25':('2025–26',['B.A.'],['Arts'],'https://directorateofhighereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/dhe_medhassu_in_oid_4/menu/document/public_notice_english_and_assamese.pdf'),
    '70':('2026–27',['B.A.'],['Arts'],'https://manikpuranchalikcollege.ac.in/'),
}
IDENTITY_NOTES={
    '66':'Constituent science college of Bongaigaon University since 13 March 2026; still named as a college by the university.',
    '83':'Likely same Satindra Mohan Dev College as row 81; linked prospectus resolves to the same college.',
    '95':'Likely same Janata College, Serfanguri as row 262; linked official site resolves to the same college.',
    '103':'Official source calls this Dhemaji City College, formerly Dhemaji Girls College.',
    '265':'Likely same Bodofa U. N. Brahma College as row 257; both linked to bodofaunbc.ac.in.',
    '331':'B.L.B. expands to Bir Lachit Borphukan College; row 332 has the same official site.',
}

# College-controlled material read individually. Values are specific regular
# degree awards; study centres, plans, PG diplomas and staff qualifications are omitted.
# "date" is the academic session when printed; standing pages have no session.
COLLEGE_MASTERS={
 '19':('2026–27',['M.A. Sanskrit Vedanta','M.A. Sanskrit Mimamsa','M.A. Sanskrit Dharmasastra','M.A. Assamese','M.A. Yoga Vigyan'],'https://kkhgsc.org/Prospectus_2026_27.pdf'),
 '35':('standing page',['M.A. Bodo'],'https://www.baramacollegebarama.edu.in/bodo_department.php'),
 '41':('2024–25',['M.Com','M.A. Assamese','M.A. Education'],'https://bhcollege.ac.in/upload/prospectus/1715577158.pdf'),
 '42':('2025–26',['M.A. Assamese'],'https://bbkcollege.co.in/upload/prospectus/Prospectus%202025-26.pdf'),
 '53':('2026–27',['M.A. Assamese','M.Sc Botany'],'https://mccollege.edu.in/upload/notice/1787672178.pdf'),
 '98':('2026–27',['M.A. Assamese','M.A. Political Science','M.A. Philosophy','M.A. Education','M.A. Geography','M.Voc Food Processing Technology','M.Sc Computer Science','M.Sc Geography','M.Sc Microbiology','M.Sc Zoology','M.Sc Physics','M.Sc Chemistry','M.Sc Botany'],'http://mangaldaicollege.org/pdf/PG-Admission26.pdf'),
 '100':('2026–27',['M.A. Assamese','M.A. English'],'https://sipajharcollege.ac.in/upload/prospectus/PROSPECTUS%202026-27.pdf'),
 '133':('standing page',['M.Com'],'https://dhskcommercecollege.edu.in/CoursesOffer.php'),
 '173':('2024–25',['M.A. Assamese'],'https://sarupatharcollege.ac.in/static/upload/prospectus-2024-25.pdf'),
 '150':('2026–27',['M.A. Assamese','M.A. Geography'],'https://bikalicollege.org/pg-admission-notice-assamese-geography-2026-27/'),
 '138':('standing page',['M.A. Assamese'],'https://mdkgcollege.edu.in/?home'),
 '190':('standing page',['M.A. Assamese'],'https://www.dcbgirlscollegejorhat.org/assamese.php'),
 '208':('standing page',['M.Sc Botany','M.Sc Chemistry','M.Sc Zoology','M.A. Assamese','M.A. Economics','M.A. English','M.A. Philosophy','M.A. Political Science'],'https://www.hgcollege.edu.in/'),
 '216':('2026–27',['M.Sc Zoology'],'https://panducollege.ac.in/'),
 '218':('2024–25',['M.T.M. Tourism and Management','M.A. Assamese','M.A. Economics','M.Sc Economics','M.Sc Zoology','M.Sc Geology','M.A. Geography','M.Sc Geography','M.A. Education'],'https://webbackend.pragjyotishcollege.ac.in/src/uploads/COLLEGE_DOWNLOADS_GALLERY/PROSPECTUS%20FINAL%2010052024_TopgeuxdgP.pdf'),
 '226':('standing page',['M.A. Assamese','M.A. Mathematics','M.Sc Mathematics'],'https://jncollegeboko.ac.in/pg.php'),
 '228':('2026–27',['M.A. Assamese'],'https://chhaygaoncollege.in/notice.php'),
 '238':('standing page',['M.Sc Biophysics','M.Sc Physics','M.Sc Computer Science','M.Sc Zoology','M.Voc Food Processing & Quality Management'],'https://pubkamrupcollege.co.in/pg.php'),
 '258':('standing page',['M.Com'],'https://commercecollege.ac.in/courses'),
 '261':('2025–26',['M.A. Assamese','M.A. Bodo','M.A. Education','M.A. Geography'],'https://gossaigaoncollege.org/2025/07/09/admission-notice-for-admission-into-pg-assamese-bodo-education-geography-for-the-session-2025-26/'),
 '262':('2026–27',['M.A. Bodo'],'https://www.janatacollege.co.in/'),
 '263':('2026–27',['M.Sc Botany','M.Sc Zoology','M.Sc Chemistry'],'http://sciencecollege.ac.in/Prospectus/sck/Prospectus/Prospectus_2026_2027_Final_Version.pdf'),
 '299':('standing page',['M.A. Assamese'],'https://adpcollege.ac.in/postgraduate.php'),
 '309':('2026–27',['M.A. Assamese'],'https://www.khagarijancollege.ac.in/Khagarijan College Prospectus, 2026-2027.pdf'),
 '311':('standing page',['M.Com'],'https://ngndgccollege.edu.in/academic.php'),
 '314':('2026–27',['M.A. Assamese','M.A. Geography','M.Sc Geography'],'https://nowgonggirlscollege.edu.in/upload/notice/1785226658.pdf'),
 '324':('standing page',['M.A. Assamese','M.A. English'],'https://nalbaricollege.ac.in/PG.pdf'),
 '332':('2025–26',['M.A. Assamese','M.A. Political Science','M.A. Sociology','M.A. Education'],'https://blbcollege.org.in/PROSPECTUS BLB 25-26.pdf'),
 '341':('2026–27',['M.A. Assamese','M.A. Political Science'],'https://sibsagargirlscollege.org.in/Prospectus%202026-27.pdf'),
 '359':('2026–27',['M.Com','M.Sc Mathematics','M.Sc Chemistry','M.Sc Computer Science'],'https://tinsukiacollege.in/uploads/Propectus_2026-27.pdf'),
 '367':('standing page',['M.A. Bodo'],'https://udalguricollegeedu.in/academics/'),
}

def normalized(s):
    return re.sub('[^a-z0-9]','',re.sub(r'\([^)]*\)','',s.lower()).replace('government','govt'))

def subject_key(s):
    return re.sub('[^a-z]','',re.sub(r'\([^)]*\)','',s.lower()))

def ug_label(programme):
    s=programme.strip(); low=s.lower()
    if low.startswith('bachelor of arts'):
        if 'mass communication' in low or 'journalism' in low:return 'B.A. (Mass Communication)'
        return 'B.A.'
    if low.startswith('bachelor of science') or low.startswith('b.sc'):
        for term,label in [('information technology','Information Technology'),('biotechnology','Biotechnology'),('applied science','Applied Science'),('interior design','Interior Design'),('microbiology','Microbiology'),('data science','Data Science')]:
            if term in low:return f'B.Sc ({label})'
        return 'B.Sc'
    if low.startswith('bachelor of commerce'):
        return 'B.Com (Business Analytics)' if 'business analytics' in low else 'B.Com'
    if low.startswith('bachelor of business administration'):return 'B.B.A.'
    if low.startswith('bachelor of computer applications'):return 'B.C.A.'
    if low.startswith('bachelor of vocation'):
        inside=re.search(r'\((.*)\)',s)
        subject=inside.group(1).strip() if inside else ''
        subject=re.sub(r'\s+(?:GU|DBU|BBC|BNC|CDC|DBC|DKC|DKD|DRC|GCC|GPC|MDC|MGC|NLC|RPC|RTU|SDC|SPC)\s*$','',subject).strip()
        return f'B.Voc ({subject})' if subject else 'B.Voc'
    if low.startswith('bachelor of law'):return 'LL.B.'
    if low.startswith('bachelor of social work'):return 'B.S.W.'
    if low.startswith('bachelor of performing arts'):return 'B.P.A.'
    if low.startswith('bachelor of music'):return 'B.Mus.'
    if low.startswith('bachelor of physical education'):return 'B.P.Ed.'
    if low.startswith('bachelor of physiotherapy'):return 'B.P.T.'
    if low.startswith('bachelor of tourism management'):return 'B.T.M.'
    if low.startswith('five year') or low.startswith('integrated'):return s
    return s

def area(label):
    if label.startswith('B.A.'):return 'Arts'
    if label.startswith('B.Sc'):return 'Science'
    if label.startswith('B.Com'):return 'Commerce'
    if label.startswith('B.B.A.'):return 'Management'
    if label.startswith('B.C.A.'):return 'Computer Applications'
    if label.startswith('B.Voc'):return 'Vocational'
    if label.startswith('LL.B.'):return 'Law'
    if label.startswith(('B.P.A.','B.Mus.')):return 'Performing Arts'
    if label.startswith('B.P.Ed.'):return 'Physical Education'
    if label.startswith('B.P.T.'):return 'Health Sciences'
    if label.startswith('B.S.W.'):return 'Social Work'
    return 'Other / integrated'

def masters_area(label):
    x=label.lower()
    if 'm.b.a.' in x:return 'Management'
    if 'm.c.a.' in x:return 'Computer Applications'
    if 'm.s.w.' in x:return 'Social Work'
    if 'll.m.' in x:return 'Law'
    if 'm.f.tech' in x:return 'Design'
    if 'm.t.t.m.' in x:return 'Management'
    if 'm.lib' in x:return 'Library Science'
    if re.search(r'\bm\.a\.|master of arts',x):return 'Arts'
    if re.search(r'\bm\.sc|master of science',x):return 'Science'
    if re.search(r'\bm\.com|master of commerce',x):return 'Commerce'
    if 'voc' in x:return 'Vocational'
    if 'tourism' in x or 'mba' in x:return 'Management'
    return 'Other / postgraduate'

def pg_label(raw):
    raw=raw.split(':',1)[-1].strip()
    awards=[('Master of Arts','M.A.'),('Master of Science','M.Sc'),('Master of Commerce','M.Com'),
            ('Master of Business Administration','M.B.A.'),('Master of Computer Application','M.C.A.'),
            ('Master of Social Work','M.S.W.'),('Master of Life Science','M.Sc Life Science'),
            ('Master of Travel and Tourism Management','M.T.T.M.'),('Master of Fashion Technology','M.F.Tech'),
            ('Master of Library & Information Sciences','M.Lib.I.Sc.'),('Master of Laws','LL.M.')]
    for prefix,award in awards:
        if not raw.lower().startswith(prefix.lower()):continue
        tail=raw[len(prefix):].strip()
        if tail.startswith('(') and tail.endswith(')'):tail=tail[1:-1].strip()
        tail=re.sub(r'(?:[- ](?:AWU|BBC|BNC|DBC|DHSK|DKC|DNC|DRC|GC|GNC|GUS|HPB|KBC|KBVSAS|MDC|MGC|NC|NLC|RPC))$','',tail,flags=re.I).strip(' -')
        tail=re.sub(r'-Sc-?\s*$','',tail,flags=re.I).strip()
        tail=tail.replace('Assamesse','Assamese')
        if tail.isupper():tail=tail.title()
        if tail.lower()==award.lower().replace('m.com','commerce'):tail=''
        if award=='M.Sc Life Science' and tail:return f'{award} ({tail.title()})'
        return f'{award} {tail}'.strip()
    return raw

def main():
    rows=list(csv.DictReader((ROOT/'general_colleges.csv').open(encoding='utf-8-sig')))
    matrix=json.loads((E/'samarth_seat_matrix.json').read_text())
    match=json.loads((E/'college_name_matches.json').read_text())
    by_college=defaultdict(list)
    for x in matrix:
        try: seats=int(x['seats'])
        except ValueError:continue
        if seats>0:by_college[x['college']].append(x)
    pg=json.loads((E/'samarth_pg_metadata.json').read_text())
    index={normalized(r['College / Institute']):r['No.'] for r in rows}
    portal_pg=defaultdict(list)
    for x in pg:
        name=x['college'].split(':')[-1].strip()
        ident=index.get(normalized(name))
        if not ident:
            ident={'B.N. College (Autonomous)':'119','H.P.B.Girls College. Golaghat':'165'}.get(name)
        if ident and 'master' in x['programme'].lower():
            label=pg_label(x['programme'])
            portal_pg[ident].append({'programme':label,'source':x['source_url']})
    academic=[]; offer_rows=[]
    for r in rows:
        ident=r['No.']; name=match.get(ident,''); seat=by_college.get(name,[])
        awards=sorted({ug_label(x['programme']) for x in seat})
        areas=sorted({area(x) for x in awards})
        disciplines=sorted({x['discipline'].strip() for x in seat if x['discipline'].strip()})
        master_portal=portal_pg.get(ident,[])
        master_college=COLLEGE_MASTERS.get(ident)
        # A current college notice gives the precise award title where the
        # portal's programme label is abbreviated or misclassified.
        prefer_college=master_college and master_college[0]=='2026–27'
        master_labels=(master_college[1] if prefer_college else sorted({x['programme'] for x in master_portal}) if master_portal else (master_college[1] if master_college else []))
        master_source=(master_college[2] if prefer_college else PG_SOURCE if master_portal else (master_college[2] if master_college else ''))
        master_date='2026–27' if master_portal or prefer_college else (master_college[0] if master_college else '')
        master_status='Documented regular master’s' if master_labels else 'Not established from reviewed evidence'
        legacy_courses=[{'BA':'B.A.','BSc':'B.Sc','BCom':'B.Com'}.get(x.strip(),x.strip()) for x in (r['Courses / Streams'].split('/',1)[1] if '/' in r['Courses / Streams'] else '').split(',') if x.strip()]
        override=COLLEGE_UG_OVERRIDES.get(ident)
        ug_review_awards=awards if awards else (override[1] if override else legacy_courses)
        ug_review_areas=areas if areas else (override[2] if override else [x.strip() for x in r['Courses / Streams'].split('/',1)[0].replace('&',',').split(',') if x.strip()])
        reviewed_courses=ug_review_awards+master_labels
        reviewed_streams=sorted(set(ug_review_areas+[masters_area(x) for x in master_labels]))
        dept_source=r['Department Source URL'].strip()
        dept_note=r['Department Verification'].lower()
        dept_subject_only=('teaching subjects listed in the dhe' in dept_note or 'disciplines in gauhati university' in dept_note or 'subjects listed' in dept_note)
        dept_secondary=('nearme.3o9.in' in dept_source or 'study-india.org' in dept_source or 'aishe-derived' in dept_note)
        dept_names=[] if not dept_source or dept_subject_only or dept_secondary else [x.strip() for x in r['Departments / ITI Trades'].split(';') if x.strip()]
        for dept_name in NAV_DEPARTMENT_ADDITIONS.get(ident,[]):
            if dept_name.lower() not in {x.lower() for x in dept_names}:dept_names.append(dept_name)
        department_keys={subject_key(x) for x in dept_names}
        unmapped_disciplines=[x for x in disciplines if subject_key(x) not in department_keys and subject_key(x) not in {'notset',''}]
        degree_review=('2026–27 UG portal listing; college programme completeness unverified' if awards else
                       f'{override[0]} college/government UG evidence; no matching 2026–27 portal listing' if override else
                       'Legacy UG entry; no matching 2026–27 portal listing')
        if master_labels:degree_review+=f'; regular master’s documented ({master_date})'
        department_review=('Source-linked department names; college-wide completeness unverified' if dept_names else 'Department list not established; source gives subjects or no verified roster')
        if dept_names and unmapped_disciplines:department_review+=f'; {len(unmapped_disciplines)} portal disciplines require department mapping'
        if ident in POSSIBLE_DUPLICATE: match_status='Possible duplicate of row '+POSSIBLE_DUPLICATE[ident]
        elif name and seat: match_status='2026–27 portal programmes found'
        elif name: match_status='Portal name matched; no positive-seat records found'
        else: match_status='No matching current portal listing found'
        # Only literal department headings in recent college material can support
        # a complete department ranking; existing legacy lists have mixed semantics.
        dv=r['Department Verification'].lower()
        if re.search(r'2026|2025',dv) and re.search(r'\b(explicit|all|\d+ department|department headings|current official index)\b',dv):dept_status='Recent official list; review completeness'
        else:dept_status='Completeness unverified'
        record={
            'No.':ident,'College / Institute':r['College / Institute'],
            'Academic Review Date':DATE,'Institution Match Status':match_status,
            'Institution Identity Note':IDENTITY_NOTES.get(ident,''),
            '2026 Portal College Name':name,
            '2026 Portal UG Programmes':'; '.join(awards),
            '2026 Portal UG Programme Areas':'; '.join(areas),
            '2026 Portal UG Disciplines':'; '.join(disciplines),
            '2026 Portal UG Programme Count':str(len(awards)) if seat else '',
            '2026 Portal UG Source':UG_SOURCE if seat else '',
            'Regular Masters Status':master_status,
            'Documented Regular Masters':'; '.join(master_labels),
            'Masters Evidence Session':master_date,
            'Masters Evidence URL':master_source,
            'Department Count Review':dept_status,
            'Streams':'; '.join(reviewed_streams),
            'Courses':'; '.join(dict.fromkeys(reviewed_courses)),
            'Departments':'; '.join(dept_names),
            'Course and Stream Evidence':degree_review,
            'Department Evidence':department_review,
            'Reviewed Department Source URL':r['Website URL'] if ident in NAV_DEPARTMENT_ADDITIONS else dept_source if dept_names else '',
            'Course and Stream Source URL':UG_SOURCE if awards else override[3] if override else '',
            'Portal Disciplines Needing Department Mapping':'; '.join(unmapped_disciplines),
        }
        academic.append(record)
        for x in seat:
            offer_rows.append({'No.':ident,'College / Institute':r['College / Institute'],'Level':'UG','Degree Programme':ug_label(x['programme']),'Portal Programme':x['programme'],'Discipline':x['discipline'],'Seats':x['seats'],'Source':x['source_url'],'Review':'Official 2026–27 portal listing; college corroboration pending'})
        for x in master_labels:
            offer_rows.append({'No.':ident,'College / Institute':r['College / Institute'],'Level':'Masters','Degree Programme':x,'Portal Programme':'','Discipline':'','Seats':'','Source':master_source,'Review':master_date+' official evidence'})
    (E/'academic_review.json').write_text(json.dumps(academic,ensure_ascii=False,indent=2))
    (E/'programme_evidence.json').write_text(json.dumps(offer_rows,ensure_ascii=False,indent=2))
    print(json.dumps({'directory_rows':len(rows),'portal_match':sum(bool(x['2026 Portal College Name']) for x in academic),'positive_seats':sum(bool(x['2026 Portal UG Programmes']) for x in academic),'regular_masters_documented':sum(bool(x['Documented Regular Masters']) and x['No.'] not in POSSIBLE_DUPLICATE for x in academic),'masters_2026':sum(bool(x['Documented Regular Masters']) and x['Masters Evidence Session']=='2026–27' and x['No.'] not in POSSIBLE_DUPLICATE for x in academic),'possible_duplicate_rows':len(POSSIBLE_DUPLICATE),'offer_rows':len(offer_rows)}))

if __name__=='__main__':main()
