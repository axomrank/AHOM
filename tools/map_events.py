"""Bind catalogue stories to geographic mentions, named rivers and explicit event connections."""
import json
import re


def build_map_events(root,scenes,basemap):
    sites=json.loads((root/'data/map-sites.json').read_text())['sites']
    explicit=json.loads((root/'data/map-stories.json').read_text())['events']
    known={p['id'] for p in sites}
    patterns={p['id']:re.compile(r'(?<!\w)(?:'+ '|'.join(re.escape(a) for a in sorted(p['aliases'],key=len,reverse=True))+r')(?!\w)',re.I) for p in sites}
    river_aliases={'dihing':['Dihing','Dehing'],'dhansiri-south':['Dhansiri','Doyang'],'puthimari':['Puthimari','Bornadi','Barnadi'],'bharali':['Bharali','Jia Bharali'],'dikhou':['Dikhou','Dikhow']}
    river_patterns={rid:re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(a) for a in river_aliases.get(rid,[r['name']]))+r')(?!\w)',re.I) for rid,r in basemap['rivers'].items()}
    aliases={a:s['id'] for s in scenes for a in [s['id'],*s.get('alias',[])]}
    for key,value in explicit.items():
        if key not in aliases: raise ValueError(f'Unknown map event {key}')
        for pid in value.get('sites',[])+value.get('route',[]):
            if pid not in known: raise ValueError(f'Unknown map place {pid} in {key}')
        for rid in value.get('rivers',[]):
            if rid not in basemap['rivers']: raise ValueError(f'Unknown map river {rid}')
    events={}
    for s in scenes:
        text=s['title']+' '+s['summary']
        matched=sorted((p['id'] for p in sites if patterns[p['id']].search(text)),key=lambda pid:patterns[pid].search(text).start())
        rivers=[rid for rid,pattern in river_patterns.items() if pattern.search(text)]
        override=next((explicit[a] for a in [s['id'],*s.get('alias',[])] if a in explicit),{})
        events[s['id']]={'sites':override.get('sites',matched),'rivers':override.get('rivers',rivers),
                         'route':override.get('route',[]),'mode':override.get('mode','connection'),
                         'caption':override.get('caption','')}
    for p in sites:
        p['scenes']=[sid for sid,event in events.items() if p['id'] in event['sites']]
    return {'sites':sites,'events':events}
