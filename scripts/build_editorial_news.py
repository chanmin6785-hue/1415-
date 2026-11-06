"""Compile checked Korean editorial summaries with original publication metadata."""
import csv,datetime as dt,hashlib,json,re
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';OUT=ROOT/'dist/replay/news';OUT.mkdir(exist_ok=True)
source_file=P/'verified-sources.json'
if not source_file.exists():source_file=ROOT/'data/editorial-sources.json'
sources=json.loads(source_file.read_text())
known={s['url'] for s in sources}
sources.extend(s for s in json.loads((ROOT/'data/editorial-extra-sources.json').read_text()) if s['url'] not in known)
def source_for(key):
    rows=[s for s in sources if re.search('/'+re.escape(key)+r'(?:/|$)',s['url'])] if key.isdigit() else [s for s in sources if key in s['url']]
    if not rows:raise ValueError('Missing verified source: '+key)
    rows.sort(key=lambda s:('www.uefa.com' not in s['url'],s['url'].endswith('barcelonaa'),len(s['url'])))
    return rows[0]
def publication(source):
    value=next(iter(source.get('datePublished',[])),'')
    if not value:raise ValueError('Missing publication date: '+source['url'])
    if re.match(r'\d{4}-\d{2}-\d{2}',value):
        date=value[:10];time='';label=''
        if 'T' in value:
            stamp=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
            if 'skysports.com' in source['url']:
                stamp=stamp.astimezone(ZoneInfo('Europe/London'));date=stamp.date().isoformat();label='영국 시각'
            else:label='한국 시각' if stamp.utcoffset()==dt.timedelta(hours=9) else '원문 표준 시각'
            time=stamp.strftime('%H:%M')
        return date,time,label,value
    m=re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})',value)
    if m:return f'{m[3]}-{int(m[1]):02}-{int(m[2]):02}','','',value
    raise ValueError('Unrecognized publication date: '+value)
reports=[];used_sources=[]
with (ROOT/'data/editorial-news.tsv').open() as f:
    for row in csv.DictReader(f,delimiter='|'):
        if None in row:raise ValueError('Unescaped delimiter in editorial row: '+str(row))
        source=source_for(row['key']);date,time,label,stamp=publication(source)
        host=source['url'];publisher=source.get('publisher') or ('Sky Sports' if 'skysports.com' in host else 'UEFA' if 'uefa.com' in host else 'FC Barcelona' if 'fcbarcelona.com' in host else 'Tottenham Hotspur' if 'tottenhamhotspur.com' in host else 'Liverpool FC')
        report={k:row[k] for k in ['category','player','origin','dest','status','fee','title','text','context','reaction','watch'] if row.get(k)}
        report.update(id='e-'+hashlib.sha1(host.encode()).hexdigest()[:14],date=date,publishedAt=stamp,publisher=publisher,source=host,kind=row['category'],priority=3 if row['category']=='충격' else 2 if row['category']=='논란' else 1,originalTitle=source['title'].split(' | Football News')[0],basis='구단 공식 발표' if publisher in ['FC Barcelona','Tottenham Hotspur','Liverpool FC'] else '주최기관 보도' if publisher=='UEFA' else '당시 매체 보도',dateBasis='original-datePublished')
        if source.get('author'):report['author']=source['author']
        report['publicationEvidence']=source.get('dateEvidence') or 'Publisher datePublished metadata'
        report['sourceModifiedAt']=next(iter(source.get('dateModified') or []),'')
        report['editionStatus']='later-update-present' if report['sourceModifiedAt'] and report['sourceModifiedAt'][:10]>date else 'original-edition-not-preserved'
        if time:report.update(publishedTime=time,timezoneLabel=label)
        if row.get('match'):
            report['matches']=[dict(zip(['date','home','away'],m.split('~'))) for m in row['match'].split(';')]
            report['matchDate']=report['matches'][0]['date']
        reports.append(report)
        used_sources.append({k:source.get(k) for k in ['url','title','datePublished','dateModified','publisher','author','dateEvidence']})
assert len({r['id'] for r in reports})==len(reports),'Duplicate editorial source'
reports.sort(key=lambda r:(r['date'],r.get('publishedTime',''),r['id']))
(OUT/'editorial.json').write_text(json.dumps(reports,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/editorial-sources.json').write_text(json.dumps(used_sources,ensure_ascii=False,indent=2)+'\n')
story_file=ROOT/'dist/replay/stories.json';stories=json.loads(story_file.read_text());stories['stories']=reports
stories['newsMeta']={'editorialCount':len(reports),'editionCount':len({r['date'] for r in reports}),'datePolicy':'exact-publication-day','version':2}
story_file.write_text(json.dumps(stories,ensure_ascii=False,separators=(',',':')))
print('Compiled',len(reports),'editorial reports across',stories['newsMeta']['editionCount'],'publication dates')
