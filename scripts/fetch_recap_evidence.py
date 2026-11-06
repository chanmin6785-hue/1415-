"""Checkpoint public CC0 season honors; preserve source entities and omissions."""
import json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/recap';OUT.mkdir(parents=True,exist_ok=True)
leagues='wd:Q9448 wd:Q754839 wd:Q324867 wd:Q15804 wd:Q82595 wd:Q13394 wd:Q167541 wd:Q182994'
extraPath=ROOT/'data/season-extra-leagues.json'
if extraPath.exists():leagues+=' '+' '.join('wd:'+k for k in json.loads(extraPath.read_text()))
queries={
 'honors-winners':'''SELECT ?edition ?editionLabel ?league ?winner ?winnerLabel ?start ?end WHERE { VALUES ?league { '''+leagues+''' } ?edition wdt:P3450 ?league; wdt:P1346 ?winner. OPTIONAL { ?edition wdt:P580 ?start } OPTIONAL { ?edition wdt:P582 ?end } SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ko" } }''',
 'honors-scorers':'''SELECT ?edition ?editionLabel ?league ?scorer ?scorerLabel ?goals WHERE { VALUES ?league { '''+leagues+''' } ?edition wdt:P3450 ?league; p:P12475 ?s. ?s ps:P12475 ?scorer. OPTIONAL { ?s pq:P1351 ?goals } SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ko" } }'''
}
result={'source':'https://www.wikidata.org','license':'CC0-1.0','notice':'Qualified season entities, not proof of a precise championship-clinching or award announcement date.'}
for name,q in queries.items():
 p=OUT/(name+('-all-leagues' if extraPath.exists() else '')+'.json')
 if p.exists():d=json.loads(p.read_text())
 else:
  req=urllib.request.Request('https://query.wikidata.org/sparql?'+urllib.parse.urlencode({'query':q,'format':'json'}),headers={'User-Agent':'FootballHistoryReplay/1.0','Accept':'application/sparql-results+json'})
  with urllib.request.urlopen(req,timeout=60) as r:d=json.load(r)
  p.write_text(json.dumps(d,ensure_ascii=False));time.sleep(1)
 result[name]=[{k:v['value'] for k,v in row.items()} for row in d['results']['bindings']]
 print(name,len(result[name]),flush=True)
(ROOT/'data/season-honors-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
