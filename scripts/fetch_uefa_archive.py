"""Read UEFA's public match feed with bounded requests and persistent checkpoints.

No images, current player ages, match commentary or live text are redistributed.
The scorer time.minute is the supplied football minute; the historical second
field can be a sequential placeholder, so it is intentionally never exported.
"""
import concurrent.futures,gzip,json,threading,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/expansion/uefa';P.mkdir(exist_ok=True)
LOCK=threading.Lock();NEXT=0;FAIL=[]
def fetch(url,name):
    global NEXT
    path=P/(name+'.json.gz')
    if path.exists():return json.loads(gzip.decompress(path.read_bytes()))
    with LOCK:
        now=time.monotonic();delay=max(0,NEXT-now);NEXT=max(now,NEXT)+.6
    if delay:time.sleep(delay)
    req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryReplay/1.0 (https://github.com/chanmin6785-hue/1415-)','Accept':'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=30) as r:d=json.load(r)
            path.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False).encode()));return d
        except urllib.error.HTTPError as e:
            if e.code==429:time.sleep(min(30,int(e.headers.get('Retry-After','20'))))
            elif e.code in [401,403,404]:raise
            elif attempt==2:raise
        except Exception:
            if attempt==2:raise
        time.sleep(2+attempt)
def season(task):
    comp,year=task;allrows=[]
    for offset in range(0,1500,100):
        url=f'https://match.uefa.com/v5/matches?competitionId={comp}&seasonYear={year}&limit=100&offset={offset}&order=ASC'
        d=fetch(url,f'list-{comp}-{year}-{offset}')
        if not isinstance(d,list):raise ValueError('Unexpected match feed schema')
        allrows.extend(compact(m) for m in d)
        if len(d)<100:break
    return allrows
def compact(m):
    """Keep factual fields used by importers; avoid retaining image/multilang trees.

    Raw per-page checkpoints are retained separately. This bounds the collector's
    memory while preserving actual minute, phase and stoppage-time values.
    """
    def team(t):
        return {k:t[k] for k in ['id','internationalName','typeIsNational','teamTypeDetail'] if k in t}|{'translations':{'displayOfficialName':{'EN':t.get('translations',{}).get('displayOfficialName',{}).get('EN','')}}}
    def player(p):
        return {k:p[k] for k in ['id','internationalName','birthDate','fieldPosition'] if k in p}|{'translations':{'countryName':{'EN':p.get('translations',{}).get('countryName',{}).get('EN','')}}}
    out={k:m[k] for k in ['id','status','seasonYear','kickOffTime','score','winner','matchDay','group','leg','round'] if k in m}
    out['homeTeam']=team(m.get('homeTeam',{}));out['awayTeam']=team(m.get('awayTeam',{}))
    c=m.get('competition',{});out['competition']={'id':c.get('id'),'metaData':c.get('metaData',{}),'code':c.get('code','')}
    out['stadium']={'translations':{'name':{'EN':m.get('stadium',{}).get('translations',{}).get('name',{}).get('EN','')}}}
    out['playerEvents']={}
    for kind,es in m.get('playerEvents',{}).items():
        out['playerEvents'][kind]=[{k:v for k,v in e.items() if k not in ['player','images','translations']}|{'player':player(e.get('player',{}))} for e in es] if isinstance(es,list) else es
    return out
tasks=[(1,y) for y in range(1955,2028)]+[(19,y) for y in range(1956,1990)]+[(3,y) for y in range(1960,2025,4)]+[(17,y) for y in range(1958,2027,4)]
tasks += [(14,y) for y in range(1971,2028)]+[(9,y) for y in range(1972,2027)]+[(2019,y) for y in range(2021,2028)]+[(2,y) for y in range(1960,2000)]
tasks.sort(key=lambda t:(0 if 1955<=t[1]<=1962 else 1,t[1],t[0]));matches={};n=0
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    fs={pool.submit(season,t):t for t in tasks}
    for f in concurrent.futures.as_completed(fs):
        try:
            for m in f.result():
                date=m.get('kickOffTime',{}).get('date','')
                if m.get('status')=='FINISHED' and '1956-01-01'<=date<='2026-10-31':matches[m['id']]=m
        except Exception as e:FAIL.append({'task':fs[f],'error':str(e)})
        n+=1
        if n%10==0:print('UEFA seasons',n,'/',len(tasks),'matches',len(matches),'unavailable',len(FAIL),flush=True)
(P/'matches.json.gz').write_bytes(gzip.compress(json.dumps(list(matches.values()),ensure_ascii=False).encode()))
print('UEFA match lists finished',len(matches),flush=True)
# First repair early-era player/lineup gaps, then check finals of every era.
lineupTargets=[m for m in matches.values() if m['kickOffTime']['date']<'1963-07-01' or m.get('round',{}).get('metaData',{}).get('type')=='FINAL']
lineupTargets.sort(key=lambda m:m['kickOffTime']['date']);n=0
def lineup(m):return fetch('https://match.uefa.com/v5/matches/'+m['id']+'/lineups','lineup-'+m['id'])
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    fs={pool.submit(lineup,m):m for m in lineupTargets}
    for f in concurrent.futures.as_completed(fs):
        try:f.result()
        except Exception as e:FAIL.append({'matchId':fs[f]['id'],'kind':'lineup','error':str(e)})
        n+=1
        if n%100==0:print('UEFA lineups',n,'/',len(lineupTargets),'unavailable',len(FAIL),flush=True)
(P/'failures.json').write_text(json.dumps(FAIL));print('UEFA collection complete',len(matches),'matches;',len(lineupTargets),'lineup attempts;',len(FAIL),'unavailable',flush=True)
