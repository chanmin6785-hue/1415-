"""Collect licensed football reporting from the English Wikinews category tree."""
import threading
import concurrent.futures,datetime as dt,gzip,hashlib,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,'/tmp/football-news-deps')
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';CACHE=P/'wikinews-pages';CACHE.mkdir(exist_ok=True)
BASE='https://en.wikinews.org'
LOCK=threading.Lock();NEXT=0
def page(url):
    global NEXT
    p=CACHE/(hashlib.sha1(url.encode()).hexdigest()+'.gz')
    if p.exists():raw=gzip.decompress(p.read_bytes()).decode()
    else:
        with LOCK:
            now=time.monotonic();wait=max(0,NEXT-now);NEXT=max(now,NEXT)+1.25
        if wait:time.sleep(wait)
        req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)'})
        for attempt in range(4):
            try:
                raw=urllib.request.urlopen(req,timeout=20).read().decode('utf-8','replace');p.write_bytes(gzip.compress(raw.encode()));break
            except urllib.error.HTTPError as e:
                if e.code!=429 or attempt==3:raise
                with LOCK:NEXT=max(NEXT,time.monotonic()+30*(attempt+1))
                time.sleep(30*(attempt+1))
    return BeautifulSoup(raw,'lxml')
def category(url):
    articles=set();cats=set();visited=set()
    while url and url not in visited:
        visited.add(url);s=page(url)
        for a in s.select('#mw-pages .mw-category-group a[href]'):
            href=a['href'];name=a.get_text(' ',strip=True)
            if not href.startswith('/wiki/') or ':' in urllib.parse.unquote(href[6:]):continue
            if name.startswith('Football results'):continue
            articles.add(urllib.parse.urljoin(BASE,href))
        for a in s.select('#mw-subcategories .mw-category-group a[href]'):
            href=a['href']
            if '/wiki/Category:' in urllib.parse.urljoin(BASE,href) and not any(x in href for x in ['club_logos','Wikinews','WikiFootball']):cats.add(urllib.parse.urljoin(BASE,href))
        nxt=next((a.get('href') for a in s.select('#mw-pages a[href]') if a.get_text(strip=True)=='next page'),None)
        url=urllib.parse.urljoin(BASE,nxt) if nxt else None
    return articles,cats
def article(url):
    s=page(url);date_node=s.select_one('.published')
    if not date_node:raise ValueError('No published dateline')
    raw=date_node.get_text(' ',strip=True);date=None
    for fmt in ['%A, %B %d, %Y','%B %d, %Y','%A, %d %B %Y']:
        try:date=dt.datetime.strptime(raw,fmt).date().isoformat();break
        except ValueError:pass
    if not date or not '1956-01-01'<=date<='2026-10-31':raise ValueError('Date outside range: '+raw)
    title=s.select_one('h1').get_text(' ',strip=True)
    ps=s.select('.mw-parser-output > p');summary=''
    for p in ps:
        txt=p.get_text(' ',strip=True)
        if len(txt)>70 and not p.select_one('.published') and not txt.startswith(('"','“','This article','This is an archive')):
            summary=txt[:1000];break
    links=[a['href'] for a in s.select('.sourceTemplate a.external[href]') if a['href'].startswith('http')]
    license='CC-BY-4.0' if date>='2024-12-16' else 'CC-BY-2.5' if date>='2005-09-25' else 'public-domain'
    return {'id':'w-'+hashlib.sha1(url.encode()).hexdigest()[:14],'date':date,'title':title,'summary':summary,'source':url,'publisher':'Wikinews','language':'en','dateBasis':'published-dateline','license':license,'references':links[:4]}
if __name__=='__main__':
    seen=set();frontier={BASE+'/wiki/Category:Football_(soccer)'};articles=set();bad=[]
    for depth in range(5):
        todo=frontier-seen
        if not todo:break
        seen.update(todo);frontier=set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            fs={pool.submit(category,u):u for u in todo}
            for f in concurrent.futures.as_completed(fs):
                try:a,c=f.result();articles.update(a);frontier.update(c)
                except Exception as e:bad.append({'url':fs[f],'error':str(e)})
        print('Wikinews categories',len(seen),'article URLs',len(articles),'depth',depth,flush=True)
    rows=[];n=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fs={pool.submit(article,u):u for u in sorted(articles)}
        for f in concurrent.futures.as_completed(fs):
            try:rows.append(f.result())
            except Exception as e:bad.append({'url':fs[f],'error':str(e)})
            n+=1
            if n%100==0:print('Wikinews articles',n,'/',len(articles),'dated',len(rows),flush=True)
    rows.sort(key=lambda r:(r['date'],r['id']))
    (P/'wikinews-records.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    (P/'wikinews-fetch-failures.json').write_text(json.dumps(bad))
    print('Wikinews dated articles:',len(rows),'unavailable',len(bad),flush=True)
