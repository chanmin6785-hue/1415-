"""Collect dated public football archive links, not newspaper article bodies.

The publisher's daily archive is the date evidence. A link index is distinct
from the separately checked and written editorial reports.
"""
import argparse, concurrent.futures, datetime as dt, hashlib, html, json, re, time, urllib.error, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news/guardian-days'
MONTHS=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
P.mkdir(parents=True,exist_ok=True)
def extract(raw,date):
    found={}
    for card in re.findall(r'<h3\b[^>]*class="fc-item__title"[^>]*>(.*?)</h3>',raw,re.S):
        m=re.search(r'<a\b[^>]*href="([^"]+)"',card)
        if not m:continue
        url=html.unescape(m.group(1));d=re.search(r'/(\d{4})/([a-z]{3})/(\d{2})/',url)
        if not d or d.group(2) not in MONTHS:continue
        source_date=f'{d[1]}-{MONTHS.index(d[2])+1:02}-{d[3]}'
        if source_date!=date:continue
        title=html.unescape(re.sub('<[^>]+>',' ',card));title=re.sub(r'\s+',' ',title).strip()
        if not title or len(title)>350:continue
        found[url]={'id':'g-'+hashlib.sha1(url.encode()).hexdigest()[:14], 'date':date,'title':title,'source':url,'publisher':'The Guardian','archiveSource':archive_url(date),'dateBasis':'publisher-daily-archive'}
    return list(found.values())
def archive_url(date):
    y,m,d=map(int,date.split('-'));return f'https://www.theguardian.com/football/{y}/{MONTHS[m-1]}/{d:02}/all'
def fetch(date):
    out=P/(date+'.json')
    if out.exists():
        cached=json.loads(out.read_text())
        if cached.get('status') in ['ok','empty','not-found']:return cached
    url=archive_url(date)
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)','Accept-Encoding':'gzip'})
            with urllib.request.urlopen(req,timeout=20) as response:
                data=response.read()
                if response.headers.get('Content-Encoding')=='gzip':
                    import gzip;data=gzip.decompress(data)
            raw=data.decode('utf-8','replace');rows=extract(raw,date)
            if not rows and 'fc-item__title' not in raw and 'Sorry' not in raw and 'No articles' not in raw and 'Sorry, no articles' not in raw:
                raise ValueError('Unrecognized daily archive structure')
            result={'date':date,'source':url,'status':'ok' if rows else 'empty','articles':rows}
            out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')));time.sleep(.15);return result
        except urllib.error.HTTPError as e:
            if e.code==404:
                result={'date':date,'source':url,'status':'not-found','articles':[]};out.write_text(json.dumps(result));return result
            if e.code in [401,403]:return {'date':date,'status':'blocked','error':str(e),'articles':[]}
            if e.code==429:time.sleep(min(30,int(e.headers.get('Retry-After','15'))))
        except Exception as e:
            if attempt==2:return {'date':date,'status':'failed','error':str(e),'articles':[]}
        time.sleep(1+attempt)
    return {'date':date,'status':'failed','articles':[]}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',default='1998-01-01');ap.add_argument('--end',default='2026-10-31');ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
    first=dt.date.fromisoformat(args.start);last=dt.date.fromisoformat(args.end)
    dates=[(first+dt.timedelta(days=i)).isoformat() for i in range((last-first).days+1)]
    # Spread collection across eras so a partial network failure cannot erase an era silently.
    priority=['2012','2017','2021','2002','2005','2006','2018','2022','2023','2025']
    dates.sort(key=lambda d:(priority.index(d[:4]) if d[:4] in priority else 99,d))
    count=0;reports=0;bad=[];started=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending={pool.submit(fetch,d):d for d in dates}
        for f in concurrent.futures.as_completed(pending):
            row=f.result();count+=1;reports+=len(row['articles'])
            if row['status'] in ['failed','blocked']:bad.append(row)
            if count%50==0:print(json.dumps({'days':count,'totalDays':len(dates),'links':reports,'failed':len(bad),'seconds':round(time.time()-started)}),flush=True)
            if len(bad)>20 and all(x['status']=='blocked' for x in bad[-20:]):
                for task in pending:task.cancel()
                raise RuntimeError('Publisher denied access; stopped instead of bypassing restriction')
    (P.parent/'guardian-fetch-failures.json').write_text(json.dumps(bad,ensure_ascii=False))
    (P.parent/'guardian-fetch-complete.json').write_text(json.dumps({'days':count,'links':reports,'failed':len(bad)}))
    print(json.dumps({'finished':True,'days':count,'links':reports,'failed':len(bad)}),flush=True)
