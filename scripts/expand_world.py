"""Expand an existing replay build. Only known source countries are accepted."""
import csv,json,datetime,collections
from pathlib import Path
P=Path('research');O=Path('dist/replay');M=json.load(open(O/'manifest.json'));cut=M['cutoff']
def dump(f,v):p=O/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':')))
def add(key,label,code,region,rows,source,calendar=False,note='',tier=1):
 seasons=collections.defaultdict(list);season_labels={}
 for r in rows:
  try:
   if 'Country' in r:
    d=datetime.datetime.strptime(r['Date'],'%d/%m/%Y').date().isoformat();y=int(r['Season'][:4]);h,a,hg,ag=r['Home'],r['Away'],r['HG'],r['AG'];sl=r['Season']
   else:
    if r.get('tier')!=str(tier) or r.get('round','league') not in ['league','NA']:continue
    d=r['Date'];y=int(r['Season']);h,a,hg,ag=r['home'],r['visitor'],r['hgoal'],r['vgoal'];sl=str(y) if calendar else str(y)+'/'+str(y+1)[2:]
   if y<1955 or d>cut or not hg.isdigit() or not ag.isdigit():continue
   if h==a:raise ValueError('same team')
   seasons[y].append(dict(date=d,home=h,away=a,hg=int(hg),ag=int(ag)));season_labels[y]=sl
  except (ValueError,KeyError):continue
 # Recent European seasons share the same source keys but a different CSV schema.
 for recent in ['2526','2627']:
  rf=P/f'{key}-{recent}.csv'
  if not rf.exists():continue
  for r in csv.DictReader(open(rf,encoding='utf-8-sig')):
   try:
    dt=r['Date'];d=datetime.datetime.strptime(dt,'%d/%m/%Y' if len(dt)==10 else '%d/%m/%y').date().isoformat();y=2000+int(recent[:2])
    if d>cut or not r['FTHG'].isdigit() or not r['FTAG'].isdigit():continue
    seasons[y].append(dict(date=d,home=r['HomeTeam'],away=r['AwayTeam'],hg=int(r['FTHG']),ag=int(r['FTAG'])));season_labels[y]=str(y)+'/'+str(y+1)[2:]
   except (ValueError,KeyError):continue
 infos=[]
 for y,ms in sorted(seasons.items()):
  ms.sort(key=lambda m:(m['date'],m['home']));seen=set();unique=[]
  for m in ms:
   id=(m['date'],m['home'],m['away'])
   if id in seen:continue
   seen.add(id);unique.append(m)
  ms=unique;f=f'leagues/{key}-{y}.json';sl=season_labels[y];cal='/' not in sl
  dump(f,dict(id=key,season=y,seasonLabel=sl,matches=ms,source=(source if y<2025 or 'football-data' in source else 'https://www.football-data.co.uk/data.php'),note=note));infos.append(dict(year=y,file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date'],label=sl,calendar=cal))
 if infos:M['leagues'][key]=dict(name=label,code=code,region=region,seasons=infos,calendar=calendar,note=note)
for k,info in M['leagues'].items():
 info.setdefault('region','유럽');info.setdefault('calendar',False)
 for s in info['seasons']:s.setdefault('label',str(s['year'])+'/'+str(s['year']+1)[2:]);s.setdefault('calendar',False)
history={'holland':('에레디비시','NED'),'portugal':('포르투갈 1부','POR'),'scotland':('스코틀랜드 1부','SCO'),'belgium':('벨기에 1부','BEL'),'greece':('그리스 1부','GRE'),'turkey':('튀르키예 1부','TUR')}
for key,(name,code) in history.items():
 p=P/(key+'.csv')
 if p.exists():add(key,name,code,'유럽',list(csv.DictReader(open(p))),'https://github.com/jalapic/engsoccerdata',note='스플릿·플레이오프·승점 이월 및 삭감은 별도 복원하지 않은 기본 합산 순위입니다.')
for key,base,tier,label,code in [('england-2','england',2,'잉글랜드 2부','ENG2'),('england-3','england',3,'잉글랜드 3부','ENG3'),('england-4','england',4,'잉글랜드 4부','ENG4'),('germany-2','germany',2,'독일 2부','GER2')]:
 rows=list(csv.DictReader(open(P/(base+'.csv'))))
 # English third tier was regional until 1957/58. Do not combine north/south into one table.
 if key=='england-3':rows=[r for r in rows if int(r['Season'])>=1958]
 add(key,label,code,'유럽',rows,'https://github.com/jalapic/engsoccerdata',tier=tier)
world={'japan':('J1리그','JPN','아시아','Japan',True),'brazil':('브라질 세리 A','BRA','남미','Brazil',True),'argentina':('아르헨티나 1부','ARG','남미','Argentina',True),'usa':('미국 MLS','USA','북중미','USA',True),'mexico':('멕시코 리가 MX','MEX','북중미','Mexico',False),'norway':('노르웨이 1부','NOR','유럽','Norway',True),'sweden':('스웨덴 1부','SWE','유럽','Sweden',True),'denmark':('덴마크 1부','DEN','유럽','Denmark',False),'finland':('핀란드 1부','FIN','유럽','Finland',True),'ireland':('아일랜드 1부','IRL','유럽','Ireland',True),'china':('중국 슈퍼리그','CHN','아시아','China',True),'austria':('오스트리아 1부','AUT','유럽','Austria',False),'switzerland':('스위스 1부','SUI','유럽','Switzerland',False)}
for key,(label,code,region,country,calendar) in world.items():
 p=P/(key+'-world.csv')
 if not p.exists():continue
 rows=list(csv.DictReader(open(p,encoding='utf-8-sig')));countries={r.get('Country','').strip() for r in rows}
 if countries!={country}:raise ValueError('Wrong country feed: '+key+str(countries))
 add(key,label,code,region,rows,'https://www.football-data.co.uk/all_new_data.php',calendar,'스플릿·컨퍼런스·전후기·플레이오프·승점 이월을 구분하지 않은 기본 합산 순위입니다. 시즌별 완전성은 보장하지 않습니다.')
# Every country's dated match history, loaded only when selected.
nations=collections.defaultdict(list)
for inf in M['internationals'].values():
 for m in json.load(open(O/inf['file']))['matches']:
  nations[m['home']].append(m);nations[m['away']].append(m)
M['nations']={}
for i,(name,ms) in enumerate(sorted(nations.items())):
 ms.sort(key=lambda m:(m['date'],m['home']));f=f'nations/nation-{i:03}.json';dump(f,dict(name=name,matches=ms,source='https://github.com/martj42/international_results'));M['nations'][name]=dict(file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date'])
countries={'england':'잉글랜드','spain':'스페인','italy':'이탈리아','germany':'독일','france':'프랑스','holland':'네덜란드','portugal':'포르투갈','scotland':'스코틀랜드','belgium':'벨기에','greece':'그리스','turkey':'튀르키예','japan':'일본','brazil':'브라질','argentina':'아르헨티나','usa':'미국','mexico':'멕시코','norway':'노르웨이','sweden':'스웨덴','denmark':'덴마크','finland':'핀란드','ireland':'아일랜드','china':'중국','austria':'오스트리아','switzerland':'스위스','korea':'대한민국 한국'}
for key,info in M['leagues'].items():info['country']=countries.get(key.split('-')[0],'')
M['totals']['leagueMatches']=sum(s['count'] for l in M['leagues'].values() for s in l['seasons']);M['totals']['leagueCount']=len(M['leagues']);M['totals']['nationCount']=len(M['nations']);M['totals']['files']=len(list(O.rglob('*.json')));dump('manifest.json',M)
print(M['totals']);print('NEW LEAGUES',[(k,v['seasons'][0]['year'],v['seasons'][-1]['year']) for k,v in M['leagues'].items() if k not in ['england','spain','italy','germany','france']])
