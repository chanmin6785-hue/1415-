import csv,json,collections,re,hashlib,datetime
from pathlib import Path
P=Path('research');O=Path('dist/replay');O.mkdir(exist_ok=True)
CUTOFF='2026-10-31';manifest={'version':2,'cutoff':CUTOFF,'leagues':{},'internationals':{},'cups':{},'sources':[]}
def write(path,data):
 p=O/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
def match(d,h,a,hg,ag,**kw):return dict(date=d,home=h,away=a,hg=int(hg),ag=int(ag),**kw)
leagues={'england':('잉글랜드 1부','ENG'),'spain':('라리가','ESP'),'italy':('세리에 A','ITA'),'germany':('분데스리가','GER'),'france':('프랑스 1부','FRA')}
for k,(label,code) in leagues.items():
 seasons=collections.defaultdict(list)
 for r in csv.DictReader(open(P/(k+'.csv'))):
  if r.get('tier')!='1' or r.get('round','league') not in ['league','NA']:continue
  y=int(r['Season']);d=r['Date']
  if y<1955 or d>CUTOFF:continue
  try:seasons[y].append(match(d,r['home'],r['visitor'],r['hgoal'],r['vgoal']))
  except:pass
 for s in ['2526','2627']:
  p=P/f'{k}-{s}.csv'
  if not p.exists():continue
  for r in csv.DictReader(open(p,encoding='utf-8-sig')):
   try:
    dt=r['Date'];d=datetime.datetime.strptime(dt,'%d/%m/%Y' if len(dt)==10 else '%d/%m/%y').date().isoformat()
    if d>CUTOFF:continue
    seasons[2000+int(s[:2])].append(match(d,r['HomeTeam'],r['AwayTeam'],r['FTHG'],r['FTAG']))
   except:pass
 info=[]
 for y,ms in sorted(seasons.items()):
  ms.sort(key=lambda m:(m['date'],m['home']));ids=[(m['date'],m['home'],m['away']) for m in ms];assert len(ids)==len(set(ids)),(k,y,'duplicate')
  f=f'leagues/{k}-{y}.json';write(f,{'id':k,'season':y,'matches':ms,'source':'https://github.com/jalapic/engsoccerdata' if y<2025 else 'https://www.football-data.co.uk/data.php'});info.append(dict(year=y,file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date']))
 manifest['leagues'][k]=dict(name=label,code=code,seasons=info)
# All senior men's international matches, including qualifiers and friendlies.
intl=collections.defaultdict(list)
shoot={(r['date'],r['home_team'],r['away_team']):r['winner'] for r in csv.DictReader(open(P/'shootouts.csv'))}
goals=collections.defaultdict(list)
for r in csv.DictReader(open(P/'goalscorers.csv')):
 if r['date']<'1956-01-01' or r['date']>CUTOFF or not r['minute']:continue
 goals[(r['date'],r['home_team'],r['away_team'])].append(dict(minute=r['minute'],team=r['team'],scorer=r['scorer'],own=r['own_goal']=='TRUE',penalty=r['penalty']=='TRUE'))
for r in csv.DictReader(open(P/'intl.csv')):
 d=r['date']
 if d<'1956-01-01' or d>CUTOFF:continue
 try:m=match(d,r['home_team'],r['away_team'],r['home_score'],r['away_score'],competition=r['tournament'],venue=r['city']+', '+r['country'])
 except:continue
 key=(d,m['home'],m['away'])
 if key in shoot:m['shootoutWinner']=shoot[key]
 if r['tournament'] in ['FIFA World Cup','UEFA Euro'] and key in goals:m['goals']=goals[key]
 intl[d[:4]].append(m)
for y,ms in sorted(intl.items()):
 f=f'international/{y}.json';write(f,{'matches':ms,'source':'https://github.com/martj42/international_results'});manifest['internationals'][y]=dict(file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date'])
# World Cup structured stages and group identities from openfootball.
for p in sorted(P.glob('wc[0-9][0-9][0-9][0-9].json')):
 y=p.stem[2:];raw=json.load(open(p));ms=[]
 for r in raw['matches']:
  sc=r.get('score');d=r.get('date','')
  if not sc or not d or d>CUTOFF or 'winner' in str(r['team1']).lower():continue
  final=(sc.get('et') or sc.get('ft')) if isinstance(sc,dict) else sc
  if not final or None in final:continue
  m=match(d,r['team1'],r['team2'],*final,stage=r.get('round',''),group=r.get('group',''),venue=r.get('ground',''))
  if isinstance(sc,dict) and sc.get('p'):m['pens']=sc['p']
  key=(d,m['home'],m['away']);m['goals']=[]
  for side in [1,2]:
   for g in r.get('goals'+str(side),[]):m['goals'].append(dict(minute=str(g['minute']),team=m['home'] if side==1 else m['away'],scorer=g['name'],penalty=g.get('penalty',False),own=g.get('owngoal',False)))
  if not m['goals']:m['goals']=goals.get(key,[])
  if key in shoot:m['shootoutWinner']=shoot[key]
  ms.append(m)
 if ms:
  f=f'cups/wc-{y}.json';write(f,{'name':'FIFA 월드컵 '+y,'year':int(y),'matches':sorted(ms,key=lambda m:m['date']),'source':'https://github.com/openfootball/worldcup.json','winPoints':2 if int(y)<1994 else 3});manifest['cups']['wc-'+y]=dict(name='월드컵 '+y,file=f,count=len(ms),start=min(m['date'] for m in ms),end=max(m['date'] for m in ms))
# Euro stages: historical format changes, group components obtained from group fixtures.
for y,allms in sorted(intl.items()):
 ms=[dict(m) for m in allms if m['competition']=='UEFA Euro']
 if not ms:continue
 iy=int(y);ms.sort(key=lambda m:m['date']);n=len(ms);gcount=0 if iy<=1976 else (12 if iy<=1992 else 24 if iy<=2012 else 36)
 expected=5 if iy==1968 else 4 if iy<=1976 else 14 if iy==1980 else 15 if iy<=1992 else 31 if iy<=2012 else 51
 if n!=expected:print('Euro incomplete',y,n,expected)
 groupms=ms[:gcount];groups=[]
 for m in groupms:
  found=[g for g in groups if m['home'] in g or m['away'] in g]
  if not found:groups.append({m['home'],m['away']})
  else:
   g=found[0];g.update([m['home'],m['away']])
   for x in found[1:]:g.update(x);groups.remove(x)
 for i,m in enumerate(ms):
  m['group']='';m['stage']=''
  if i<gcount:
   m['group']='Group '+chr(65+next(j for j,g in enumerate(groups) if m['home'] in g));m['stage']='Group stage'
  else:
   remaining=n-i
   if iy==1968:m['stage']='Semi-finals' if i<2 else 'Third place' if i==2 else 'Final'
   elif remaining==1:m['stage']='Final'
   elif (iy<=1980 and remaining==2):m['stage']='Third place'
   elif remaining<=3 or (iy<=1976 and remaining<=4):m['stage']='Semi-finals'
   elif remaining<=7:m['stage']='Quarter-finals'
   else:m['stage']='Round of 16'
 f=f'cups/euro-{y}.json';write(f,{'name':'UEFA EURO '+('2020 (2021 개최)' if y=='2021' else y),'year':iy,'matches':ms,'source':'https://github.com/martj42/international_results','winPoints':2 if iy<1996 else 3});manifest['cups']['euro-'+y]=dict(name='유로 '+('2020 (2021)' if y=='2021' else y),file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date'])
manifest['totals']={'leagueMatches':sum(s['count'] for l in manifest['leagues'].values() for s in l['seasons']),'internationalMatches':sum(s['count'] for s in manifest['internationals'].values()),'cupEditions':len(manifest['cups']),'files':len(list(O.rglob('*.json')))}
write('manifest.json',manifest);print(json.dumps(manifest['totals']));print('MB',sum(p.stat().st_size for p in O.rglob('*') if p.is_file())/1e6)
