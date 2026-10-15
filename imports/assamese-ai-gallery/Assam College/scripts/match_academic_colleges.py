"""Explicit, reviewable institution-name reconciliation; no fuzzy auto-merges."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'academic_evidence'
ALIASES={
'1':'Govt. Model Degree College,Baksa','2':'Govt. Model Degree College, Baghbor','3':'Govt. Model College, Chenga','7':'Govt. Model degree College, Chirang','8':"Govt. Model Women's Degree College, Mangaldai",'10':'Govt. Model Degree college, Majar Alga','11':'Govt. Model College, Bilasipara','12':'Govt Model Women College Golakganj, Dhubri','13':'GOVT. MODEL COLLEGE, DIMA HASAO','16':'GOVT. MODEL COLLEGE, KAZIRANGA, GOLAGHAT','17':'Govt. Model College, Hailakandi','18':'PDUAM, KATLICHERRA','19':'KRISHNA KANTA HANDIQUE GOVT. SANSKRIT COLLEGE','24':'Govt. Model Degree College, Majuli','26':'Govt. Model Degree College, Samaguri','28':'Govt. Model Degree College Borsola, Sonitpur','29':'BIR RAGHAB MORAN GOVERNMENT MODEL COLLEGE, DOOMDOOMA, TINSUKIA','31':'Govt. Model Degree College, Hari Singha, Udalguri',
'34':'B. B. KISHAN COLLEGE, JALAH','41':'B H College','42':'BAOSI BANIKANTA KAKATI COLLEGE','45':'Barpeta Bongaigaon College, Langla','46':'Barpeta College, Barpeta','51':'Janapriya College','53':'Madhab Choudhury College, Barpeta','54':'Madhya Kamrup College, Subha','56':'Nabajyoti College, Kalgachia','69':'Mahatma Gandhi College,Chalantapara','74':'Jagannath Singh College','75':'Janata College','76':'MADHAB CHANDRA DAS COLLEGE','77':'MOHENDRA KUMAR DEY COLLEGE','78':'Nehru College','80':'SATYA RANJAN COLLEGE','99':'Mangaldai Commerce College','111':'Paschim Dhemaji College','112':'Purbanchal College, Silapathar','114':'Silapathar Science College P.O. Silapathar','117':'Sissi Borgaon College','119':'B.N. College (Autonomous)','126':'Hatidhura College, Hatidhura','127':'Pramathesh Barua College','138':"Manohari Devi Kanoi Girls' College",'144':'Pithubar College','151':'Dalgoma Anchalik College','159':'Chandra Nath Bezbaruah College, Bokakhat','161':'D K D College (Autonomous)','165':'H.P.B.Girls College. Golaghat','171':'Marangi Mahavidyalaya, Golaghat','172':'Melamora College P.O. Melamora-785625','174':'A.L.Choudhury College','176':'MOINUL HOQUE CHOUDHURY MEMORIAL SCIENCE COLLEGE','178':'SARADA CHARAN DEY COLLEGE, KALINAGAR','179':'S.K. ROY COLLEGE, KALTICHERRA','183':'Lanka Mahavidyalaya','187':'C K B College, Teok','188':'C K B Commerce College','190':"DCB Girls' College",'191':'Dr. N. B. College','192':'Ghana Kanta Borah College, Tamulichiga','197':'Moriani College','200':'Sarbodaya College','213':'LCB College','223':'B. P. Chaliha College, Nagarbera','225':'BINANDI CHANDRA MEDHI COLLEGE, RAMDIA','226':'Jawaharlal Nehru College, Boko','227':'Chhamaria Anchalik College','228':'Chhaygaon College','234':"Manabendra Sarma Girls' College",'242':'S B M S College, Sualkuchi','255':'R K Nagar College','261':'Gossaigaon College, Gossaigaon','265':'Bodofa U. N. Brahma College','283':'Telahi Tuaram Nath College P.O.Lakhimpur','284':'Jengraimukh College, Majuli','298':'Alhaz Sunai Bibi Choudhury College','307':'Kampur College, Nagaon, Assam-782426','322':'Kamrup College, Chamata','324':'Nalbari College, Nalbari','327':'Swahid Smriti Mahavidyalaya, Belsor','329':'Uttar Kampeeth College','331':'Bir Lachit Borphukan College','336':'H.C.D.G. College, Nitaipukhuri','342':'S.P.P.College P.O. Namtichariali--785684','357':'PADMANATH GOHAIN BARUAH GOVT. MODEL COLLEGE, KAKOPATHAR, TINSUKIA','367':'Udalguri College, Udalguri','370':'THONGNOKBE COLLEGE, DOKMOKA',
}
def norm(s): return re.sub('[^a-z0-9]','',re.sub(r'\([^)]*\)','',s.lower()).replace('government','govt'))
def main():
    matrix=json.loads((E/'samarth_seat_matrix.json').read_text()); names={r['college'] for r in matrix}
    lookup={}
    for n in names: lookup.setdefault(norm(n),[]).append(n)
    rows=list(csv.DictReader((ROOT/'general_colleges.csv').open(encoding='utf-8-sig')))
    ALIASES.update({'127':'PRAMATHESH BARUA COLLEGE','103':'Dhemaji City College','83':'SATINDRA MOHAN DEV COLLEGE','95':'Janata College, Serfanguri','210':"K.R.B. Girls' College - ASTU",'328':'TIHU COLLEGE, TIHU'})
    matches={}; missing=[]
    for r in rows:
        opts=lookup.get(norm(r['College / Institute']),[])
        if r['No.'] in ALIASES:
            n=ALIASES[r['No.']]
            if n not in names: print('ALIAS NOT FOUND',r['No.'],n); continue
            opts=[n]
        if len(opts)==1: matches[r['No.']]=opts[0]
        else: missing.append([r['No.'],r['College / Institute'],opts])
    duplicates={n:[i for i,m in matches.items() if m==n] for n in set(matches.values()) if list(matches.values()).count(n)>1}
    (E/'possible_duplicate_colleges.json').write_text(json.dumps(duplicates,indent=2))
    (E/'college_name_matches.json').write_text(json.dumps(matches,indent=2,ensure_ascii=False))
    print('Matched',len(matches),'Unresolved',missing,'Possible duplicates',duplicates)
if __name__=='__main__': main()
