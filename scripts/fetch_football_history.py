"""Collect licensed, dated historical records. These are NOT contemporary news.

Sources: annual football event lists, English season diaries and Wikipedia's
monthly current-events portals. Events without an exact day are excluded.
"""
import concurrent.futures,datetime as dt,gzip,hashlib,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,'/tmp/football-news-deps')
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';CACHE=P/'wiki-pages';CACHE.mkdir(exist_ok=True)
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']
TERM=re.compile(r'\b(?:association football|soccer|FIFA|UEFA|CONMEBOL|CONCACAF|AFC Asian Cup|CAF Champions|Premier League|La Liga|Bundesliga|Serie A|Ligue 1|Champions League|Europa League|Ballon d.Or|World Cup|football club|footballer|football team|football match|football league|football manager|football stadium|football fans|football coach|football federation)\b',re.I)
NOT_SOCCER=re.compile(r'\b(?:cricket|rugby|NFL|Super Bowl|American football|Australian rules|basketball|ice hockey)\b',re.I)
def fetch_page(title):
    url='https://en.wikipedia.org/wiki/'+urllib.parse.quote(title.replace(' ','_'),safe=':()_')
    file=CACHE/(hashlib.sha1(url.encode()).hexdigest()+'.gz')
    if file.exists():raw=gzip.decompress(file.read_bytes()).decode()
    else:
        req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)'})
        raw=urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace');file.write_bytes(gzip.compress(raw.encode()))
    return url,BeautifulSoup(raw,'lxml')
def clean(node):
    node=BeautifulSoup(str(node),'lxml')
    for x in node.select('sup,.mw-editsection,.reference,.flagicon,.sortkey,.noprint'):x.decompose()
    return re.sub(r'\s+',' ',node.get_text(' ',strip=True)).strip()
def record(date,text,url,kind,links=()):
    return {'id':'h-'+hashlib.sha1((date+'|'+text).encode()).hexdigest()[:16],'date':date,'title':text,'source':url,'publisher':'위키백과 기여자','language':'en','type':'history','historyKind':kind,'dateBasis':'event-date-in-secondary-history','license':'CC-BY-SA-4.0','references':list(links)[:4]}
def portals(year,month):
    title=f'Portal:Current_events/{MONTHS[month-1]}_{year}';url,s=fetch_page(title);rows=[]
    for container in s.select('.current-events-main.vevent'):
        date_node=container.select_one('.dtstart');date=date_node.get_text(strip=True) if date_node else ''
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date) or date>'2026-10-31':continue
        body=container.select_one('.current-events-content') or container
        for li in body.find_all('li'):
            # Keep a precise leaf statement, not a whole nested sports roundup.
            if li.find('li'):continue
            text=clean(li)
            ancestors=' '.join(clean(x).split(' (')[0][:200] for x in list(li.parents)[:3] if x.name=='li')
            scope=text+' '+ancestors
            if NOT_SOCCER.search(scope) and not re.search('FIFA|UEFA|association football|soccer',scope,re.I):continue
            if not TERM.search(scope):continue
            if not 25<len(text)<1600:continue
            # World Cup without an identifiable football context is ambiguous.
            if re.search('World Cup',scope,re.I) and not re.search('FIFA|football|soccer|UEFA|[12][09][0-9]{2} FIFA',scope,re.I):continue
            refs=[a['href'] for a in li.select('a.external[href]') if a['href'].startswith('http')]
            rows.append(record(date,text,url+'#'+container.get('id',''), '월별 시사 기록',refs))
    return rows
def annual(year,season=False):
    title=f'{year}–{str(year+1)[2:]} in English football' if season else f'{year} in association football'
    url,s=fetch_page(title);ids=['Diary_of_the_season','Events'];rows=[]
    for id in ids:
        h=s.find(id=id)
        if not h:continue
        section=h.find_parent('section')
        if not section:continue
        nodes=section.find_all(['li','p'])
        for node in nodes:
            if node.find(['li','p']):continue
            text=clean(node)
            if len(text)<30:continue
            m=re.match(r'^(\d{1,2})\s+('+'|'.join(MONTHS)+r')(?:\s+(\d{4}))?\s*[:–—−-]\s*(.+)$',text,re.I)
            rev=False
            if not m:
                m=re.match(r'^('+'|'.join(MONTHS)+r')\s+(\d{1,2})(?:,?\s+(\d{4}))?\s*[:–—−-]\s*(.+)$',text,re.I);rev=True
            if not m:continue
            day=int(m[2] if rev else m[1]);month=MONTHS.index((m[1] if rev else m[2]).capitalize())+1
            y=int(m[3]) if m[3] else year+(1 if season and month<7 else 0)
            try:date=dt.date(y,month,day).isoformat()
            except ValueError:continue
            if not '1956-01-01'<=date<='2026-10-31':continue
            refs=[a['href'] for a in node.select('a.external[href]') if a['href'].startswith('http')]
            rows.append(record(date,m[4],url+'#'+id,'시즌 일지' if season else '연도별 사건 기록',refs))
    return rows
if __name__=='__main__':
    tasks=[('year',y,False) for y in range(1956,2027)]+[('year',y,True) for y in range(1956,2026)]
    tasks += [('month',y,m) for y in range(2000,2027) for m in range(1,13) if (y,m)<=(2026,10)]
    rows=[];bad=[];n=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        fs={pool.submit(annual,a,b) if typ=='year' else pool.submit(portals,a,b): (typ,a,b) for typ,a,b in tasks}
        for f in concurrent.futures.as_completed(fs):
            try:rows.extend(f.result())
            except Exception as e:bad.append([fs[f],str(e)])
            n+=1
            if n%25==0:print('History pages',n,'/',len(tasks),'records',len(rows),'unavailable',len(bad),flush=True)
    rows=list({r['id']:r for r in rows}.values());rows.sort(key=lambda r:(r['date'],r['id']))
    (P/'history-records.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    (P/'history-fetch-failures.json').write_text(json.dumps(bad))
    print('Historical event records:',len(rows),flush=True)
