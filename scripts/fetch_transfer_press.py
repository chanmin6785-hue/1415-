"""Resolve the FTR-18 research bibliography to public article title metadata.

The research dataset supplies historical publication dates. Deleted, blocked,
redirected-to-homepage and conflicting-date articles are excluded, not invented.
No final rumour-veracity labels or later transfers enter the news feed.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,html,json,re,threading,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';CACHE=P/'ftr-title-cache';CACHE.mkdir(exist_ok=True)
LOCK=threading.Lock();NEXT={};RETRY_NETWORK=False
def get_meta(raw,key):
    for tag in re.findall(r'<meta\b[^>]*>',raw,re.I):
        attrs=dict((k.lower(),html.unescape(v)) for k,q,v in re.findall(r'([\w:-]+)\s*=\s*([\"\'])(.*?)\2',tag,re.S))
        if attrs.get('name','').lower()==key or attrs.get('property','').lower()==key:return attrs.get('content','')
    return ''
def fetch(row):
    url=row['url'];id='f-'+hashlib.sha1(url.encode()).hexdigest()[:14];out=CACHE/(id+'.json')
    if out.exists():
        cached=json.loads(out.read_text())
        if not (RETRY_NETWORK and cached.get('status')=='unavailable' and re.search(r'503|502|504|timed out|reset|Remote end',cached.get('error',''))):return cached
    host=urllib.parse.urlsplit(url).netloc.lower()
    with LOCK:
        now=time.monotonic();wait=max(0,NEXT.get(host,0)-now);NEXT[host]=max(now,NEXT.get(host,0))+.7
    if wait:time.sleep(wait)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)'})
        with urllib.request.urlopen(req,timeout=15) as r:
            final=r.geturl();raw=r.read(2000000).decode('utf-8','replace')
        title=get_meta(raw,'og:title') or get_meta(raw,'twitter:title')
        if not title:
            m=re.search(r'<title[^>]*>(.*?)</title>',raw,re.I|re.S);title=html.unescape(re.sub('<[^>]+>','',m[1])).strip() if m else ''
        if not 15<len(title)<350 or re.search(r'access denied|just a moment|page not found|404|subscribe to read|privacy policy|consent|robot|captcha|sign in',title,re.I):raise ValueError('Unavailable article title')
        if len(urllib.parse.urlsplit(final).path.strip('/'))<8:raise ValueError('Redirected to homepage')
        date=dt.datetime.strptime(row['news_article_date'],'%d/%m/%Y').date().isoformat()
        stamps=re.findall(r'"datePublished"\s*:\s*"([^\"]+)"',raw)
        stamp=stamps[0] if stamps else get_meta(raw,'article:published_time')
        if stamp and re.match(r'\d{4}-\d{2}-\d{2}',stamp) and abs((dt.date.fromisoformat(stamp[:10])-dt.date.fromisoformat(date)).days)>1:raise ValueError('Publication date conflict')
        value={'id':id,'date':date,'title':title,'source':url,'publisher':row['news_source'],'language':row['language'],'dateBasis':'FTR-18-publication-date','dataset':'https://github.com/dcaled/FTR-18','type':'transfer-index','rumourGroup':row['id_rumour']}
        result={'status':'ok','record':value}
    except Exception as e:result={'status':'unavailable','url':url,'error':str(e)}
    out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')));return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--retry-network',action='store_true');args=ap.parse_args();RETRY_NETWORK=args.retry_network
    data=json.loads((P/'ftr18/2018_09_26_dataset.json').read_text());rows=[];bad=[];n=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        fs={pool.submit(fetch,r):r for r in data.values()}
        for f in concurrent.futures.as_completed(fs):
            r=f.result();n+=1
            if r['status']=='ok':rows.append(r['record'])
            else:bad.append(r)
            if n%100==0:print('Transfer sources',n,'/',len(data),'resolved',len(rows),'unavailable',len(bad),flush=True)
    rows=list({r['source']:r for r in rows}.values());rows.sort(key=lambda r:(r['date'],r['id']))
    (P/'ftr-records.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    (P/'ftr-fetch-failures.json').write_text(json.dumps(bad))
    print('Resolved dated transfer-press links:',len(rows),flush=True)
