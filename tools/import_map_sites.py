#!/usr/bin/env python3
"""Import the Ahom-era geographic catalogue from an existing local APP entities file."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = '''mongmao pangsau namrup tipam abhoypur habung simaluguri charaideo sivasagar mungkang kamata sadiya nongnyang dimapur dikhowmukh singri karatoya kaliabor garhgaon narayanpur majuli hajo guwahati samdhara biswanath dergaon kajali auniati ghilajharighat jogighopa saraighat alaboi jerenga itakhuli umananda rangpur joysagar maibong jaintiapur kamakhya siva-dol rang-ghar talatal-ghar kareng-ghar manipur jorhat bengmara nazira dibrugarh tinsukia ledo golaghat lakhimpur tezpur nagaon barpeta goalpara dhubri sualkuchi mayong kaziranga kohima imphal silchar cooch-behar bhamo tawang hukawng namdang hayagriva-madhava dakhinpat kamalabari garamur barpeta-satra pandu bordowa mong-yang'''.split()
ALIASES = {
    'mongmao':['Mong Mao'], 'pangsau':['Pangsau','Pangsau Pass'],
    'simaluguri':['Simaluguri','Shimolguri','Simulguri'],
    'sivasagar':['Sivasagar','Sibsagar'], 'mungkang':['Mungkang','Mong Kawng'],
    'nongnyang':['Nongnyang','Nongkyang','Nongnyang Lake'],
    'ghilajharighat':['Ghilajharighat'], 'jerenga':['Jerenga','Jerenga Pathar'],
    'itakhuli':['Itakhuli'], 'joysagar':['Joysagar'], 'rang-ghar':['Rang Ghar','Rangghar'],
    'talatal-ghar':['Talatal Ghar'], 'kareng-ghar':['Kareng Ghar'],
    'siva-dol':['Siva Dol','Shiva Dol','Sivadol'], 'namdang':['Namdang','Namdang Stone Bridge'],
    'bordowa':['Bordowa','Batadrava'],
}


def main():
    src=json.loads(Path(sys.argv[1]).read_text())
    sites=[]
    for key in KEYS:
        value=src[key]
        name=value['name']['en']
        if key=='ghilajharighat': name='Ghilajharighat'
        if key=='itakhuli': name='Itakhuli'
        sites.append({'id':key,'name':name,'as':value['name'].get('as',''),
                      'geo':value['geo'],'aliases':ALIASES.get(key,[name]),
                      'kind':'river reference' if key=='karatoya' else 'region reference' if key in ['kamata','manipur','hukawng'] else 'place'})
    out={'source':'Local APP content/entities.json; locations are catalogue reference points.', 'sites':sites}
    (ROOT/'data/map-sites.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(sites)} geographic reference points imported.')


if __name__=='__main__': main()
