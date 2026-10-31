"""Apply cached title translations without changing a source ID or historical date."""
import hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist/replay/news';DB=ROOT/'research/news/translations.sqlite'
DB.parent.mkdir(parents=True,exist_ok=True)
db=sqlite3.connect(DB);db.execute('CREATE TABLE IF NOT EXISTS titles (key TEXT PRIMARY KEY, original TEXT, language TEXT, korean TEXT)');cache={r[0]:r[1] for r in db.execute('SELECT key,korean FROM titles')};changed=0;localized=0;original=0;total_bytes=0;largest=0
index=json.loads((OUT/'index.json').read_text())
for month,info in index['months'].items():
    file=ROOT/'dist/replay'/info['file'];data=json.loads(file.read_text());touched=False
    for kind in ['articles','events']:
        for r in data[kind]:
            if r.get('titleTranslation') in ['original','names']:
                key=hashlib.sha256((r.get('sourceLanguage','en')+'\0'+r['title']).encode()).hexdigest();ko=cache.get(key)
                if ko and re.search('[가-힣]',ko):r['title']=ko;r['titleTranslation']='machine';changed+=1;touched=True
            if kind=='articles':
                if r['titleTranslation'] in ['machine','edited']:localized+=1
                else:original+=1
    if touched:file.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
    size=file.stat().st_size;info['bytes']=size;total_bytes+=size;largest=max(largest,size)
named=sum(r.get('titleTranslation')=='names' for info in index['months'].values() for r in json.loads((ROOT/'dist/replay'/info['file']).read_text())['articles'])
index['stats'].update(localizedIndexTitles=localized,originalTitleFallbacks=original,nameLocalizedIndexTitles=named,monthlyDataBytes=total_bytes,largestMonthBytes=largest)
(OUT/'index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')))
if (OUT/'quality.json').exists():
    quality=json.loads((OUT/'quality.json').read_text());quality['stats']=index['stats'];(OUT/'quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n')
print('Applied',changed,'title translations; all publication/event dates and IDs retained')
