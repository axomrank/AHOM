import difflib, json, re, unicodedata

RUSA=json.load(open('/tmp/assam_missing_rusa.json'))
DHE=json.load(open('/tmp/assam_dhe_337.json'))
BY_ID={r['source_id']:r for r in DHE}
DHE_URL='https://highereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/higheredu_medhassu_in_oid_3/do_u_want_2_know/337_stream_wise_colleges_0.pdf'
RUSA_URL='https://rusa.assam.gov.in/sites/default/files/swf_utility_folder/departments/rusa_medhassu_in_oid_7/menu/document/latest_list_of_all_provincialised_colleges.pdf'

def norm(s):
    s=unicodedata.normalize('NFKD',s).lower().replace('’',"'")
    return re.sub(r'[^a-z0-9]','',s.replace('degree','').replace('college','').replace('mahavidyalaya',''))

manual={3:318, 41:133, 48:153, 49:154, 55:144, 75:205, 81:246,
        101:266, 119:37, 128:52, 138:95, 160:171, 187:214, 194:275,
        213:322, 215:105, 222:53, 235:63, 256:122, 275:193, 299:253,
        315:314, 316:265, 317:190, 320:128, 325:335, 331:155}

canonical={55:'Chandra Kamal Bezbaruah College (C.K.B. College)',
           81:'Nagaon G.N.D.G. Commerce College',
           119:'Rajiv Gandhi Memorial College, Lengtisinga',
           138:'D.D.R. College',
           187:'Panigaon O.P.D. College',
           194:'Hem Chandra Dev Goswami College',
           213:'Bodofa U.N. Brahma College',
           256:'Dergaon Kamal Dowerah College',
           315:'Swami Yogananda Giri College',
           325:'Padmanath Gohain Baruah Government Model College, Kakopather'}

district_override={9:'Kamrup Rural',31:'Dhubri',75:'Karimganj',94:'Cachar',
                   99:'Sivasagar',118:'Karimganj',119:'Bongaigaon',
                   304:'Nagaon',314:'Chirang',323:'Nagaon'}
university_override={315:'Bodoland University',325:'Dibrugarh University'}

additions=[]
for x in RUSA:
    sid=x['source_id']
    if sid in manual:
        d=BY_ID[manual[sid]]
    else:
        d=max(DHE,key=lambda y:difflib.SequenceMatcher(None,norm(x['name']),norm(y['name'])).ratio())
        score=difflib.SequenceMatcher(None,norm(x['name']),norm(d['name'])).ratio()
        if score<.88:d=None
    district=district_override.get(sid,(d['district'] if d else x['district']))
    university=university_override.get(sid,d['university'] if d else '')
    streams=d['streams'] if d else []
    # The roster predates Madhabdev University's affiliation changes.
    if district in ('Lakhimpur','Biswanath') and university=='Gauhati University':
        university=''
    additions.append({'name':canonical.get(sid,x['name']),
                      'district':district,'university':university,'streams':streams,
                      'type':'Provincialised State College',
                      'source':DHE_URL if d else RUSA_URL,
                      'note':f"Public/provincialised college confirmed in RUSA roster (entry {sid}); departments not yet verified"})

notice2025='https://directorateofhighereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/dhe_medhassu_in_oid_4/menu/document/public_notice_english_and_assamese.pdf'
notice2023='https://directorateofhighereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/dhe_medhassu_in_oid_4/menu/document/notice_regarding_admission_in_newly_established_govt._model_colleges_in_assam_and_govt._model_women_colleges.pdf'
models=[
('Government Model Women’s College, Hailakandi','Hailakandi','Assam University',notice2025),
('Hari Singha Government Model Women’s College, Udalguri','Udalguri','Bodoland University',notice2025),
('Government Model College, Borsola','Sonitpur','Gauhati University',notice2025),
('Government Model Women’s College, Mangaldai','Darrang','Gauhati University',notice2025),
('Government Model Women’s College, Golakganj','Dhubri','Gauhati University',notice2025),
('Government Model College, Majar Alga','Dhubri','Gauhati University',notice2025),
('Government Model College, Lahorighat','Morigaon','Gauhati University',notice2025),
('Government Model College, Samaguri','Nagaon','Gauhati University',notice2025),
('Government Model College, Diblong','Dima Hasao','Assam University',notice2023),
('Government Model College, Baghbor','Barpeta','Gauhati University',notice2023),
('Government Model Women’s College, Chenga','Barpeta','Gauhati University',notice2023),
('Government Model Women’s College, Bilasipara','Dhubri','Gauhati University',notice2023),
]
for name,district,university,source in models:
    additions.append({'name':name,'district':district,'university':university,
                      'streams':[],'type':'State Government Model College','source':source,
                      'note':'Government model college in DHE admission notice; departments not yet verified'})
additions.append({'name':'Pragjyotishpur Medical College and Hospital','district':'Kamrup Metropolitan',
                  'university':'Srimanta Sankaradeva University of Health Sciences','streams':[],
                  'type':'State Government Medical College',
                  'source':'https://dme.assam.gov.in/frontimpotentdata/websites-of-medical-colleges',
                  'website':'https://pragjyotishpur-mch.assam.gov.in/',
                  'note':'Government medical college in Directorate of Medical Education list; departments not yet verified'})

assert len(additions)==121,len(additions)
assert len({norm(a['name']) for a in additions})==len(additions)
with open('/tmp/assam_public_additions.json','w') as f:json.dump(additions,f,indent=2,ensure_ascii=False)
print('prepared',len(additions),'public institutions')
print('missing district',sum(not a['district'] for a in additions))
print('missing university',sum(not a['university'] for a in additions))
