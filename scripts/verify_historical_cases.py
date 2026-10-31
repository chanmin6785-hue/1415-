"""Verify manual case dates occur in their cited historical pages before import."""
import concurrent.futures,csv,datetime as dt,gzip,hashlib,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,'/tmp/football-news-deps')
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';CACHE=P/'case-pages';CACHE.mkdir(exist_ok=True)
known={r['id']:r for r in json.loads((ROOT/'data/historical-case-verification.json').read_text())}
def verify(row):
    url='https://en.wikipedia.org/wiki/'+urllib.parse.quote(row['page'].replace(' ','_'),safe='()_')
    out=CACHE/(hashlib.sha1(url.encode()).hexdigest()+'.gz')
    if row['id'] in known and known[row['id']]['date']==row['date'] and known[row['id']]['source']==url:
        raw='Exact date previously verified in cited source: '+row['date']
    elif out.exists():raw=gzip.decompress(out.read_bytes()).decode()
    else:
        req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)'})
        raw=urllib.request.urlopen(req,timeout=20).read().decode('utf-8','replace');out.write_bytes(gzip.compress(raw.encode()));time.sleep(.5)
    text=BeautifulSoup(raw,'lxml').get_text(' ',strip=True);day=dt.date.fromisoformat(row['date'])
    candidates=[day.isoformat(),f'{day.day} {day:%B} {day.year}',f'{day:%B} {day.day}, {day.year}']
    if not any(v in text for v in candidates):raise ValueError('Exact date absent in cited article: '+row['date'])
    return {'id':'h-case-'+row['id'],'date':row['date'],'title':row['title']+' — '+row['text'],'language':'ko','source':url,'publisher':'위키백과 기여자·한국어 편집','type':'history','historyKind':'사건·사회·축구계 논란','dateBasis':'event-date-checked-in-secondary-history','license':'CC-BY-SA-4.0'}
rows=list(csv.DictReader((ROOT/'data/historical-cases.tsv').open(),delimiter='|'));good=[];bad=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    fs={pool.submit(verify,r):r for r in rows}
    for f in concurrent.futures.as_completed(fs):
        try:good.append(f.result())
        except Exception as e:bad.append({'id':fs[f]['id'],'error':str(e)})
(ROOT/'data/historical-case-records.json').write_text(json.dumps(sorted(good,key=lambda r:r['date']),ensure_ascii=False,indent=2)+'\n')
(P/'case-verification-failures.json').write_text(json.dumps(bad,ensure_ascii=False,indent=2))
print('Verified case dates:',len(good),'unavailable/unsupported:',bad)
