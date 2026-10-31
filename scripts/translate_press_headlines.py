"""Translate public link-index titles; never sends user/account data.

Translations are cached by the exact source text. Unavailable translations
remain explicitly untranslated. A changed or missing line is never assigned
to a different headline.
"""
import argparse,concurrent.futures,hashlib,json,sqlite3,threading,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news'
P.mkdir(parents=True,exist_ok=True)
DB=P/'translations.sqlite';LOCK=threading.Lock();NEXT=0;INTERVAL=.8
def key(text,lang='en'):return hashlib.sha256((lang+'\0'+text).encode()).hexdigest()
def request(text,lang):
    global NEXT
    with LOCK:
        now=time.monotonic();wait=max(0,NEXT-now);NEXT=max(now,NEXT)+INTERVAL
    if wait:time.sleep(wait)
    url='https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode({'client':'gtx','sl':lang,'tl':'ko','dt':'t','q':text})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=25) as r:d=json.load(r)
            return ''.join(piece[0] or '' for piece in d[0] if isinstance(piece,list) and piece)
        except urllib.error.HTTPError as e:
            if e.code in [401,403]:raise
            if e.code==429:time.sleep(min(45,int(e.headers.get('Retry-After','20'))))
            elif attempt==2:raise
        except Exception:
            if attempt==2:raise
        time.sleep(2+attempt)
def translate_batch(batch):
    import re
    lang=batch[0]['language'];text='\n'.join(r['title'] for r in batch)
    translated=request(text,lang);lines=[s.strip() for s in translated.splitlines() if s.strip()]
    if len(lines)!=len(batch):
        if len(batch)==1:raise ValueError('Translation returned multiple lines for one title')
        middle=len(batch)//2;return translate_batch(batch[:middle])+translate_batch(batch[middle:])
    result=[]
    for row,ko in zip(batch,lines):
        if not re.search('[가-힣]',ko):ko=''  # Preserve an explicit original-name fallback.
        # Exact score pairs must survive translation; monetary units may change legitimately.
        scores=re.findall(r'\b(\d{1,2})[–:-](\d{1,2})\b',row['title'])
        translated_scores=re.findall(r'\b(\d{1,2})[–:-](\d{1,2})\b',ko)
        if scores and scores!=translated_scores:
            ko=request(row['title'],lang).strip()
            if scores!=re.findall(r'\b(\d{1,2})[–:-](\d{1,2})\b',ko):
                ko=''  # Explicit original-title fallback; never invent a corrected score.
        result.append((key(row['title'],lang),row['title'],lang,ko))
    return result
def source_rows():
    raw_ids=set()
    for p in (P/'guardian-days').glob('*.json'):
        try:
            for r in json.loads(p.read_text()).get('articles',[]):
                raw_ids.add(r['id']);yield {**r,'language':'en'}
        except (ValueError,OSError):continue
    for name in ['wikinews-records.json','history-records.json','ftr-records.json']:
        p=P/name
        if p.exists():
            for r in json.loads(p.read_text()):
                raw_ids.add(r['id'])
                yield r
                if r.get('summary'):yield {**r,'title':r['summary']}
    # A cloned published app can resume untranslated titles without raw crawl caches.
    for file in (ROOT/'dist/replay/news').glob('[12][0-9][0-9][0-9]-[01][0-9].json'):
        data=json.loads(file.read_text())
        for r in data.get('articles',[])+data.get('events',[]):
            if r.get('titleTranslation') in ['original','names'] and r['id'] not in raw_ids:
                yield {'title':r['title'],'language':r.get('sourceLanguage','en'),'id':r['id']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');ap.add_argument('--minutes',type=int,default=70);ap.add_argument('--workers',type=int,default=2);ap.add_argument('--interval',type=float,default=.8);args=ap.parse_args();INTERVAL=max(.5,args.interval)
    db=sqlite3.connect(DB);db.execute('CREATE TABLE IF NOT EXISTS titles (key TEXT PRIMARY KEY, original TEXT, language TEXT, korean TEXT)');db.commit()
    done={r[0] for r in db.execute('SELECT key FROM titles')};failed=set();started=time.time();total=0;errors=0
    while True:
        pending={}
        for row in source_rows():
            k=key(row['title'],row.get('language','en'))
            if k not in done and k not in failed and row.get('language')!='ko':pending[k]=row
        batches=[];current=[];size=0;language=None
        for row in sorted(pending.values(),key=lambda r:r.get('language','en')):
            lang=row.get('language','en')
            if current and (size+len(row['title'])>4300 or lang!=language):batches.append(current);current=[];size=0
            language=lang;current.append(row);size+=len(row['title'])+1
        if current:batches.append(current)
        consecutive=0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(3,args.workers))) as pool:
            fs={pool.submit(translate_batch,b):b for b in batches}
            for future in concurrent.futures.as_completed(fs):
                try:
                    rows=future.result();db.executemany('INSERT OR REPLACE INTO titles VALUES (?,?,?,?)',rows);db.commit()
                    done.update(r[0] for r in rows);total+=len(rows);consecutive=0
                except Exception as e:
                    errors+=1;consecutive+=1;failed.update(key(r['title'],r.get('language','en')) for r in fs[future]);print('Translation unavailable:',str(e),flush=True)
                if consecutive>=5:
                    for task in fs:task.cancel()
                    print('Translation service unavailable; stopped this pass and retained original titles.',flush=True)
                    break
                if total%500<60:print(json.dumps({'translatedThisRun':total,'cached':len(done),'errors':errors,'seconds':round(time.time()-started)}),flush=True)
        (P/'translation-progress.json').write_text(json.dumps({'cached':len(done),'failedTitles':len(failed),'finishedScan':True}))
        if not args.watch or time.time()-started>args.minutes*60:break
        if (P/'guardian-fetch-complete.json').exists() and not pending:break
        time.sleep(15)
