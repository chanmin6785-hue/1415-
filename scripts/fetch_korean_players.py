import urllib.request,urllib.parse,json,concurrent.futures,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/localization/batches';P.mkdir(parents=True,exist_ok=True)
players=json.load(open(ROOT/'dist/replay/players/index.json'))['players'];ids=[p['id'] for p in players]
def run(it):
 i,batch=it;p=P/f'{i:03}.json'
 if p.exists():return i,len(json.load(open(p))['results']['bindings'])
 vals=' '.join('"'+x+'"' for x in batch);q='SELECT ?id ?label WHERE { VALUES ?id { '+vals+' } ?p wdt:P2446 ?id; rdfs:label ?label. FILTER(LANG(?label)="ko") }'
 # SELECT query only; POST avoids oversized query URLs.
 req=urllib.request.Request('https://query.wikidata.org/sparql',data=urllib.parse.urlencode({'query':q,'format':'json'}).encode(),headers={'User-Agent':'FootballTimeMachine/1.0 (https://github.com/chanmin6785-hue/1415-)','Accept':'application/sparql-results+json'})
 with urllib.request.urlopen(req,timeout=25) as r:data=json.load(r)
 p.write_text(json.dumps(data,ensure_ascii=False));return i,len(data['results']['bindings'])
tasks=[(i,ids[a:a+500]) for i,a in enumerate(range(0,len(ids),500))];count=0;bad=[];n=0
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 pending={pool.submit(run,t):t[0] for t in tasks}
 for f in concurrent.futures.as_completed(pending):
  try:i,m=f.result();count+=m
  except Exception as e:bad.append((pending[f],str(e)))
  n+=1
  if n%20==0:print('Batches',n,'/',len(tasks),'Korean labels',count,'errors',len(bad),flush=True)
print('Complete labels',count,'failed',bad[:6],flush=True)
