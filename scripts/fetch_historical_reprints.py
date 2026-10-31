"""Keep original newspaper dates only when the publisher explicitly identifies them."""
import concurrent.futures,datetime as dt,hashlib,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,'/tmp/football-news-deps')
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';BASE='https://www.theguardian.com';MONTHS=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
def date_text(text):
    for m in re.finditer(r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',text,re.I):
        try:return dt.datetime.strptime(m[0],'%d %B %Y').date().isoformat()
        except ValueError:pass
def url_date(url):
    m=re.search(r'/(\d{4})/([a-z]{3})/(\d{2})/',url)
    return f'{m[1]}-{MONTHS.index(m[2])+1:02}-{m[3]}' if m and m[2] in MONTHS else ''
def html(url):
    req=urllib.request.Request(url,headers={'User-Agent':'FootballHistoryArchive/1.0 (https://github.com/chanmin6785-hue/1415-)'})
    return BeautifulSoup(urllib.request.urlopen(req,timeout=20).read(),'lxml')
def original(row):
    text=row['caption'];title=row['title'];date=None;basis=''
    match=re.search(r'from the archive[, :]\s*\d{1,2}\s+\w+\s+\d{4}',title,re.I)
    if match:date=date_text(match[0]);basis='explicit-original-date-in-reprint-title'
    match=re.search(r'Originally published.{0,180}',text,re.I)
    if not date and match:date=date_text(match[0]);basis='explicit-original-publication-note'
    if not date:
        page=html(row['source']);text=page.get_text(' ',strip=True)
        match=re.search(r'(?:Originally|First) published (?:in|by).{0,160}',text,re.I)
        if match:date=date_text(match[0]);basis='explicit-original-publication-note'
        if not date:
            headline=page.find('h1');heading=headline.get_text(' ',strip=True) if headline else ''
            if re.search('from the archive',heading,re.I):date=date_text(heading);basis='explicit-original-date-in-reprint-title'
    if not date or not '1956-01-01'<=date<=row['sourcePublicationDate']:raise ValueError('Original publication day not explicit')
    return {'id':'r-'+hashlib.sha1(row['source'].encode()).hexdigest()[:14],'date':date,'title':title,'source':row['source'],'publisher':'The Observer' if re.search(r'published in the Observer',text,re.I) else 'The Guardian','language':'en','type':'historical-reprint','dateBasis':'original-print-date-in-publisher-reprint','sourcePublicationDate':row['sourcePublicationDate'],'originalDateEvidence':basis}
if __name__=='__main__':
    candidates={};bad=[]
    for number in range(1,5):
        url=BASE+'/football+theguardian/series/from-the-archive'+('' if number==1 else '?page='+str(number))
        try:
            s=html(url)
            for h in s.select('h3.card-headline,h3.fc-item__title'):
                card=h
                for _ in range(8):
                    if card.find('a',href=True):break
                    card=card.parent
                links=card.find_all('a',href=True)
                source=next((urllib.parse.urljoin(BASE,a['href']) for a in links if url_date(a['href'])),None)
                if not source:continue
                candidates[source]={'title':h.get_text(' ',strip=True),'source':source,'caption':card.get_text(' ',strip=True),'sourcePublicationDate':url_date(source)}
        except Exception as e:bad.append({'url':url,'error':str(e)})
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fs={pool.submit(original,r):r for r in candidates.values()}
        for f in concurrent.futures.as_completed(fs):
            try:rows.append(f.result())
            except Exception as e:bad.append({'url':fs[f]['source'],'error':str(e)})
    (P/'reprint-records.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    (P/'reprint-fetch-failures.json').write_text(json.dumps(bad,ensure_ascii=False,indent=2))
    print('Original-day newspaper reprints:',len(rows),'of',len(candidates),'candidates; excluded/unavailable',len(bad))
