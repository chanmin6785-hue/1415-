"""Read public CC0 Wikidata memberships with date precision preserved."""
import calendar,concurrent.futures,datetime,json,re,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/expansion';CACHE=P/'classic-careers';CACHE.mkdir(parents=True,exist_ok=True)
def query(q):
    u='https://query.wikidata.org/sparql?'+urllib.parse.urlencode({'query':q,'format':'json'})
    req=urllib.request.Request(u,headers={'User-Agent':'FootballHistoryReplay/1.0 (https://github.com/chanmin6785-hue/1415-)','Accept':'application/sparql-results+json'})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)['results']['bindings']
def v(r,k,default=''):return r.get(k,{}).get('value',default)
def observed_at(date,precision):
    y,m,d=map(int,date[:10].split('-'));precision=int(precision or 9)
    if precision<10:return f'{y:04}-12-31'
    if precision<11:return f'{y:04}-{m:02}-{calendar.monthrange(y,m)[1]}'
    return date[:10]
if not (P/'classic-wikidata-index.json').exists():
    initial=query('''SELECT ?player ?playerLabel ?birth WHERE { ?player wdt:P106/wdt:P279* wd:Q937857; wdt:P569 ?birth; wikibase:sitelinks ?n . FILTER(?birth < "1970-01-01T00:00:00Z"^^xsd:dateTime && ?n >= 10) SERVICE wikibase:label { bd:serviceParam wikibase:language "ko,en". } } LIMIT 2000''')
    (P/'classic-wikidata-index.json').write_text(json.dumps({'results':{'bindings':initial}},ensure_ascii=False))
base=json.loads((P/'classic-wikidata-index.json').read_text())['results']['bindings'];people={r['player']['value'].rsplit('/',1)[-1]:r for r in base}
allrows=[];fail=[]
ids=sorted(people)
for offset in range(0,len(ids),40):
    batch=ids[offset:offset+40];path=CACHE/f'{offset:04}.json'
    if path.exists():rows=json.loads(path.read_text())
    else:
        values=' '.join('wd:'+qid for qid in batch)
        q='''SELECT ?player ?english ?countryEnglish ?club ?clubLabel ?clubEnglish ?start ?sp ?end ?ep ?bp WHERE {
        VALUES ?player { '''+values+''' }
        OPTIONAL { ?player rdfs:label ?english FILTER(LANG(?english)="en") }
        OPTIONAL { ?player wdt:P27 ?country . ?country rdfs:label ?countryEnglish FILTER(LANG(?countryEnglish)="en") }
        OPTIONAL { ?player p:P569/psv:P569 ?bv . ?bv wikibase:timePrecision ?bp }
        OPTIONAL { ?player p:P54 ?statement . ?statement ps:P54 ?club .
          OPTIONAL { ?club rdfs:label ?clubEnglish FILTER(LANG(?clubEnglish)="en") }
          OPTIONAL { ?statement pqv:P580 ?sv . ?sv wikibase:timeValue ?start; wikibase:timePrecision ?sp }
          OPTIONAL { ?statement pqv:P582 ?ev . ?ev wikibase:timeValue ?end; wikibase:timePrecision ?ep }
        }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "ko,en". }
        }'''
        try:rows=query(q);path.write_text(json.dumps(rows,ensure_ascii=False))
        except Exception as e:
            fail.append({'ids':batch,'error':str(e)});print('Classic membership batch unavailable',offset,str(e),flush=True)
            if len(fail)>=3:break
            continue
        time.sleep(1)
    allrows.extend(rows)
    if offset%200==0:print('Classic memberships',offset+len(batch),'/',len(ids),flush=True)
result={}
for r in allrows:
    qid=v(r,'player').rsplit('/',1)[-1];base=people[qid];birth=v(base,'birth')[:10];label=v(base,'playerLabel');english=v(r,'english',label)
    p=result.setdefault(qid,{'id':'historic-'+qid,'qid':qid,'name':english,'alias':label if label!=english else '', 'birth':birth if int(v(r,'bp','9'))>=11 else '', 'birthYear':birth[:4],'country':v(r,'countryEnglish'),'position':'','historyPeriods':[],'source':'https://www.wikidata.org/wiki/'+qid,'sourceKind':'wikidata-history','license':'CC0-1.0','transfers':[],'appearances':[]})
    if v(r,'club') and v(r,'start'):
        start=v(r,'start');end=v(r,'end');precision=int(v(r,'sp','9'));ep=int(v(r,'ep','9'))
        if not re.match(r'^\d{4}-',start):continue
        item={'club':v(r,'clubEnglish',v(r,'clubLabel')),'clubKo':v(r,'clubLabel'),'clubId':v(r,'club').rsplit('/',1)[-1],'start':start[:10],'startPrecision':precision,'visibleFrom':observed_at(start,precision),'source':p['source']}
        if end and re.match(r'^\d{4}-',end):item.update(end=end[:10],endPrecision=ep,endVisibleFrom=observed_at(end,ep))
        if item not in p['historyPeriods']:p['historyPeriods'].append(item)
for p in result.values():
    p['historyPeriods'].sort(key=lambda r:(r['visibleFrom'],r['club']));p['first']=min([r['visibleFrom'] for r in p['historyPeriods']],default='');p['last']=max([r['visibleFrom'] for r in p['historyPeriods']],default='')
out=ROOT/'data/classic-player-profiles.json';out.write_text(json.dumps({'meta':{'source':'https://www.wikidata.org','license':'CC0-1.0','players':len(result),'indexCandidates':len(people),'failedBatches':len(fail),'selection':'football occupation; born before 1970; at least ten language sitelinks','precisionPolicy':'Year-only starts become visible at year end; no invented transfer day.'},'players':list(result.values())},ensure_ascii=False,separators=(',',':')))
(P/'classic-career-failures.json').write_text(json.dumps(fail));print('Compiled classic profiles',len(result),flush=True)
