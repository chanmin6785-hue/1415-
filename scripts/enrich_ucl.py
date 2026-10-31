import json,csv,re,datetime,collections
from pathlib import Path
P=Path('research');O=Path('dist/replay');manifest=json.load(open(O/'manifest.json'))
def clean(s):return re.sub(r'\s*\([A-Z]{3}\)\s*','',s.split('›')[0]).strip()
def stage(s):
 if 'Semi' in s or 'semi' in s:return 'Semi-finals'
 if 'Quarter' in s or 'quarter' in s:return 'Quarter-finals'
 if '16' in s:return 'Round of 16'
 if s.lower().strip()=='final' or s.startswith('Final |'):return 'Final'
 return s.split('|')[0].strip()
def score(s):
 m=re.search(r'(\d+)-(\d+)',s or '');return list(map(int,m.groups())) if m else None
for p in sorted(P.glob('ucl-*.csv')):
 y=int(p.stem[-4:]);ms=[]
 for r in csv.DictReader(open(p)):
  dm=re.search(r'(\d{1,2} [A-Za-z]+ \d{4})',r.get('Date',''));sc=score(r.get('ET')) or score(r.get('FT'))
  if not dm or not sc:continue
  d=datetime.datetime.strptime(dm[1],'%d %b %Y').date().isoformat()
  if d>'2026-10-31':continue
  s=stage(r.get('Round',''));g=r.get('Group','');m=dict(date=d,home=clean(r['Team 1']),away=clean(r['Team 2']),hg=sc[0],ag=sc[1],stage=s,group=g)
  pen=score(r.get('P'));agg=score(r.get('∑FT'))
  if pen:m['pens']=pen
  if agg:m['aggregate']=agg
  if 'Leg 1' in r['Round']:m['leg']=1
  elif 'Leg 2' in r['Round']:m['leg']=2
  ms.append(m)
 name='유러피언컵' if y<1992 else '챔피언스리그';f=f'cups/ucl-{y}.json';data=dict(name=f'{name} {y}/{str(y+1)[2:]}',year=y,matches=sorted(ms,key=lambda m:m['date']),source='https://github.com/footballcsv/europe-champions-league',winPoints=3 if y>=1995 else 2)
 (O/f).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));manifest['cups'][f'ucl-{y}']=dict(name=data['name'],file=f,count=len(ms),start=min(m['date'] for m in ms),end=max(m['date'] for m in ms))
for p in sorted(P.glob('ucl-*.txt')):
 y=int(p.stem[-4:]);ms=[];s='';group='';d=''
 for line in p.read_text().splitlines():
  if line.startswith('▪'):
   raw=line[1:].strip();s=stage(raw);group=raw if raw.startswith('Group ') else '';continue
  dm=re.match(r'\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Za-z]+)\s+(\d{1,2})(?:\s+(\d{4}))?',line)
  if dm:
   mon=datetime.datetime.strptime(dm[1][:3],'%b').month;yr=int(dm[3]) if dm[3] else y+(mon<7 or (mon<=8 and s in ['Final','Semi-finals','Quarter-finals','Round of 16']))
   d=f'{yr}-{mon:02}-{int(dm[2]):02}';continue
  mm=re.match(r'\s*(?:\d{1,2}:\d{2}\s+)?(.+?)\s+v\s+(.+?)\s+(\d+)-(\d+)(.*)$',line)
  if not mm or not d or d>'2026-10-31':continue
  h,a,hg,ag,extra=mm.groups();m=dict(date=d,home=clean(h),away=clean(a),hg=int(hg),ag=int(ag),stage=s,group=group)
  pen=re.search(r'(\d+)-(\d+)\s+pen',extra)
  if pen:m['pens']=list(map(int,pen.groups()))
  # assign legs within the same stage and pair chronologically
  ms.append(m)
 for m in ms:
  pair=[x for x in ms if x['stage']==m['stage'] and {x['home'],x['away']}=={m['home'],m['away']}]
  if len(pair)==2 and not m['group']:m['leg']=sorted(pair,key=lambda x:x['date']).index(m)+1
 if not ms:continue
 f=f'cups/ucl-{y}.json';name=f'챔피언스리그 {y}/{str(y+1)[2:]}';(O/f).write_text(json.dumps(dict(name=name,year=y,matches=sorted(ms,key=lambda m:m['date']),source='https://github.com/openfootball/champions-league',winPoints=3),ensure_ascii=False,separators=(',',':')));manifest['cups'][f'ucl-{y}']=dict(name=name,file=f,count=len(ms),start=min(m['date'] for m in ms),end=max(m['date'] for m in ms))
manifest['totals']['europeanMatches']=sum(x['count'] for k,x in manifest['cups'].items() if k.startswith('ucl-'));manifest['totals']['cupEditions']=len(manifest['cups']);manifest['totals']['files']=len(list(O.rglob('*.json')));(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
print(manifest['totals']);print('recent:',[(y,manifest['cups'].get('ucl-'+str(y),{}).get('count')) for y in range(2016,2026)])
