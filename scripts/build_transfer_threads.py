"""Link dated reporting by identified player; no future outcome labels."""
import collections,hashlib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'dist/replay/news'
locale=json.loads((ROOT/'dist/replay/localization.json').read_text());profiles=json.loads((ROOT/'dist/replay/players/index.json').read_text())['players'];aliases={};names={}
for p in profiles:
    ko=locale['players'].get(p['id']) or p.get('alias') or locale['playerNames'].get(p['name'])
    if not ko:continue
    key='player-'+p['id'];names[key]=ko
    for text in [p['name'],ko]:
        if len(text)>=4:aliases[text]=key
manual={'Messi':'Lionel Messi','Neymar':'Neymar','Mbappé':'Kylian Mbappé','Mbappe':'Kylian Mbappé','메시':'Lionel Messi','네이마르':'Neymar','음바페':'Kylian Mbappé','손흥민':'Heung-min Son','Son Heung-min':'Heung-min Son','박지성':'Ji-sung Park','Harry Kane':'Harry Kane'}
byName={p['name']:p['id'] for p in profiles}
for alias,full in manual.items():
    if full in byName:aliases[alias]='player-'+byName[full]
prefixes=collections.defaultdict(list)
for alias in sorted(aliases,key=len,reverse=True):
    head=re.match(r'\w+',alias)
    if head:prefixes[head[0].casefold()].append(alias)
def entities(text):
    result=set();fold=text.casefold()
    for m in re.finditer(r'(?<!\w)\w+',text):
        for alias in prefixes.get(m[0].casefold(),[]):
            end=m.start()+len(alias)
            if fold.startswith(alias.casefold(),m.start()) and (end==len(text) or not text[end].isalnum()):result.add(aliases[alias])
    return result
threads=collections.defaultdict(list);articleMap={};originals={}
for path in (ROOT/'research/news/guardian-days').glob('*.json'):
    for r in json.loads(path.read_text()).get('articles',[]):originals[r['id']]=r['title']
for name in ['ftr-records.json','wikinews-records.json']:
    path=ROOT/'research/news'/name
    if path.exists():
        for r in json.loads(path.read_text()):originals[r['id']]=r['title']
for path in sorted(P.glob('[12][0-9][0-9][0-9]-[01][0-9].json')):
    for r in json.loads(path.read_text())['articles']:
        if not r['market']:continue
        for person in entities(r['title']+' '+originals.get(r['id'],'')):
            row={k:r[k] for k in ['id','date','title','publisher','source','category']};row['kind']='index';threads[person].append(row);articleMap.setdefault(r['id'],[]).append(person)
for r in json.loads((P/'editorial.json').read_text()):
    if not r.get('player'):continue
    es=entities(r['player']) or entities(r.get('originalTitle',''))
    for person in es:
        threads[person].append({**{k:r[k] for k in ['id','date','title','publisher','source','category']},'kind':'editorial'});articleMap.setdefault(r['id'],[]).append(person)
out=ROOT/'dist/replay/transfer-threads';out.mkdir(exist_ok=True);index=[];parts=collections.defaultdict(dict)
for person,rs in sorted(threads.items()):
    rs=list({r['source']:r for r in rs}.values());rs.sort(key=lambda r:(r['date'],r['id']));part=int(person.split('-')[-1])%64;parts[part][person]=rs;index.append({'id':person,'name':names.get(person,person),'first':rs[0]['date'],'last':rs[-1]['date'],'shard':part})
for part,data in parts.items():(out/f'part-{part:02}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(out/'index.json').write_text(json.dumps({'players':index,'articlePlayers':articleMap,'policy':'Display dated reports at or before the selected day. Player grouping is not a confirmed transfer or a rumour truth label.','reportCount':sum(len(rs) for rs in threads.values()),'uniqueReports':len(articleMap)},ensure_ascii=False,separators=(',',':')))
print('Player reporting threads',len(index),'linked reports',sum(len(rs) for rs in threads.values()))
