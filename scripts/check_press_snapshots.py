"""Look up publicly indexed same-publication-day captures; no article scraping."""
import json,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/expansion/press-snapshots';P.mkdir(exist_ok=True);reports=json.loads((ROOT/'dist/replay/news/editorial.json').read_text());result={};fail=[]
for i,r in enumerate(reports):
    cache=P/(r['id']+'.json');row=None
    if cache.exists():row=json.loads(cache.read_text())
    else:
        u='https://archive.org/wayback/available?'+urllib.parse.urlencode({'url':r['source'],'timestamp':r['date'].replace('-','')+'235959'})
        try:
            with urllib.request.urlopen(u,timeout=15) as response:d=json.load(response)
            candidate=d.get('archived_snapshots',{}).get('closest',{});stamp=candidate.get('timestamp','')
            row={'publicationDate':r['date'],'url':r['source'],'sameDayCapture':candidate.get('url') if stamp[:8]==r['date'].replace('-','') and candidate.get('status')=='200' else None,'captureTimestamp':stamp or None,'datePolicy':'only same-publication-day snapshots qualify; a later capture is not an original edition'}
            cache.write_text(json.dumps(row));time.sleep(.6)
        except urllib.error.HTTPError as e:
            fail.append({'source':r['source'],'error':str(e)})
            if e.code in [401,403,429]:break
        except Exception as e:fail.append({'source':r['source'],'error':str(e)})
    if row:result[r['id']]=row
    if i%20==0:print('Press snapshot checks',i+1,'/',len(reports),flush=True)
(ROOT/'dist/replay/news/edition-evidence.json').write_text(json.dumps({'reports':result,'failures':fail,'notice':'A capture on publication day is evidence of that dated version, not proof of the earliest revision or publication time.'},ensure_ascii=False,separators=(',',':')))
print('Same-day snapshots',sum(bool(r['sameDayCapture']) for r in result.values()),'checked',len(result),'unavailable',len(fail),flush=True)
