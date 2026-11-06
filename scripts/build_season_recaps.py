"""Build date-safe season retrospectives from attributable factual components.

Unknown announcement days are never replaced by a claimed exact date. Season
summaries have a conservative availability date and carry explicit precision.
Football goals, provider leaderboards and actual awards remain distinct.
"""
import collections,csv,datetime,gzip,hashlib,json,re,subprocess,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'dist/replay';OUT=P/'season-recaps';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def season(d):return int(d[:4])-(int(d[5:7])<7)
def canonical(s):return s.replace('A.F.C.','AFC').replace('F.C.','FC').replace('S.C.','SC')
manifest=read(P/'manifest.json');curated=read(ROOT/'data/season-recap-curated.json');honors=read(ROOT/'data/season-honors-evidence.json');archive=read(ROOT/'dist/data.json');events=collections.defaultdict(list);seen=set();CUTOFF=manifest['cutoff']
def add(row,year=None):
 if not '1956-01-01'<=row.get('date','')<=CUTOFF:return
 year=season(row['date']) if year is None else int(year)
 if not 1955<=year<=2026:return
 row={**row,'season':year};row['id']=row.get('id') or 'sr-'+hashlib.sha1((str(year)+'|'+row['category']+'|'+row['date']+'|'+row['title']+'|'+row.get('source','')).encode()).hexdigest()[:16]
 if row['id'] in seen:return
 seen.add(row['id']);events[year].append(row)
def finalDate(lid,year):
 s=next((s for s in manifest['leagues'][lid]['seasons'] if s['year']==year),None)
 if not s:return None
 # The current incomplete snapshot is never treated as a final league table.
 if (s.get('calendar') or manifest['leagues'][lid].get('calendar')) and year>=int(CUTOFF[:4]):return None
 if not (s.get('calendar') or manifest['leagues'][lid].get('calendar')) and year>=int(CUTOFF[:4]):return None
 return max(s['end'],f'{year}-12-31' if s.get('calendar',manifest['leagues'][lid].get('calendar',False)) else f'{year+1}-06-30')
L={'Q9448':'england','Q754839':'england','Q324867':'spain','Q15804':'italy','Q82595':'germany','Q13394':'france','Q167541':'holland','Q182994':'portugal'}
extraPath=ROOT/'data/season-extra-leagues.json'
if extraPath.exists():L.update(read(extraPath))
def leagueFor(r,year):
 qid=r['league'].split('/')[-1];lid=L.get(qid)
 if qid=='Q754839' and year is not None and year>=1992:lid='england-2'
 if qid=='Q769744' and year is not None and year>=1992:lid='england-3'
 return lid
def editionYear(r):
 m=re.search(r'(?:^|\s)(\d{4})',r['editionLabel']);return int(m[1]) if m else None
subprocess.run(['node',str(ROOT/'scripts/build_recap_tables.cjs')],cwd=ROOT,check=True)
computed=read(ROOT/'research/recap/computed-tables.json');loc=read(P/'localization.json');rejectedHonors=[];acceptedHonors=[];clubAliases={k:v.lower() for k,v in read(ROOT/'data/season-club-aliases.json').items()}
def clubKey(name,year=None):
 s=unicodedata.normalize('NFKD',canonical(name)).lower();s=''.join(c for c in s if not unicodedata.combining(c));s=unicodedata.normalize('NFC',s);s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|bk|club|football|calcio|societa|sportiva|sad|spa|srl)\b',' ',s);s=re.sub(r'[^a-z0-9가-힣]','',s)
 s=clubAliases.get(s,s)
 korean={'전북':'jeonbukhyundaimotors','울산':'ulsanhyundai','포항':'pohangsteelers','서울':'seoul','수원':'suwonsamsungbluewings','성남':'seongnam','경남':'gyeongnam','대구':'daegu','인천':'incheonunited','부산':'busanipark','전남':'jeonnamdragons','강원':'gangwon','광주':'gwangju','제주':'jejuunited','대전':'daejeonhanacitizen','안양':'anyang','김천':'armyclub','상주':'armyclub','수원fc':'suwon'}
 if s in ['gimcheonsangmu','gimcheonsangmufc','sangjusangmu','김천','상주']:return 'kr:army'
 if s in ['asanmugunghwa','asanmugunghwafc'] or (s=='안산' and year is not None and year<2017) or (s=='아산' and year is not None and year<2020):return 'kr:police'
 for ko,en in korean.items():
  if s==ko or s==en or s==en+'fc':return 'kr:'+en
 rec=loc.get('teams',{}).get(s)
 if rec and rec.get('id'):return 'tm:'+str(rec['id'])
 return {'manunited':'manchesterunited','manutd':'manchesterunited','mancity':'manchestercity','bayernmunchen':'bayernmunich','fcbayernmunich':'bayernmunich','internazionale':'inter','intermilan':'inter','slbenfica':'benfica','afcajax':'ajax','ifknorrkoping':'norrkoping'}.get(s,s)
for row in honors['honors-winners']:
 year=editionYear(row);lid=leagueFor(row,year)
 if not lid or year is None:continue
 proof=computed.get(lid+'|'+str(year))
 if not proof:continue
 candidate=clubKey(row['winnerLabel'],year);participants={clubKey(t,year) for t in proof['teams']};leaders={clubKey(t,year) for t in proof.get('contenders',proof['leaders'])};reason=''
 if candidate not in participants:reason='winner name not reconciled with actual season participants'
 elif lid in ['england','england-2','england-3','england-4','spain','italy','germany','france','holland','portugal'] and candidate not in leaders:reason='winner conflicts with independently reconstructed final standings'
 if (lid,year) in [('france',1992),('holland',2019)]:reason='title vacated or season ended without a champion'
 if reason:rejectedHonors.append({**row,'reason':reason});continue
 row={**row,'_winnerName':next(t for t in proof['teams'] if clubKey(t,year)==candidate)};acceptedHonors.append(row)
winnerKeys=set();scorerKeys=set()
for row in acceptedHonors:
 year=editionYear(row);lid=leagueFor(row,year)
 if lid is None or year is None or year<1955 or (lid=='italy' and year in [2004,2005]):continue
 date=finalDate(lid,year)
 if date and row.get('end'):date=max(date,row['end'][:10])
 if not date or date>CUTOFF:continue
 # Multi-tournament calendar competitions need unambiguous source periods.
 if lid in ['mexico','argentina'] and not row.get('end'):continue
 key=(lid,year)
 if key in winnerKeys:
  e=next(e for e in events[year] if e['category']=='league' and e.get('league')==lid and e.get('leagueSeason')==year)
  variants=e.get('winners',[e['winner']]);variant=canonical(row.get('_winnerName',row['winnerLabel']));e['winners']=variants if clubKey(variant,year) in {clubKey(n,year) for n in variants} else variants+[variant];e['text']='출처의 시즌 우승 기록입니다. 여러 팀은 공동·지역 부문 등 해당 원문의 대회 범위를 함께 확인하세요. 공개 기준일은 우승 확정일과 구분합니다.'
  continue
 winnerKeys.add(key);winner=canonical(row.get('_winnerName',row['winnerLabel']))
 add({'date':date,'category':'league','title':manifest['leagues'][lid]['name']+' '+str(year)+(' 시즌' if manifest['leagues'][lid].get('calendar') else '/'+str(year+1)[-2:])+' 우승','winner':winner,'text':'시즌 우승 기록입니다. 아래 기준일은 보수적인 결산 공개일이며 실제 우승 확정 경기일을 뜻하지 않습니다.','precision':'season','basis':'시즌 우승 기록 · Wikidata','source':row['edition'].replace('http:','https:'),'license':'CC0-1.0','league':lid,'leagueSeason':year,'priority':4},year)
for row in honors['honors-scorers']:
 year=editionYear(row);lid=leagueFor(row,year)
 if lid is None or year is None or year<1955:continue
 date=finalDate(lid,year)
 if not date or date>CUTOFF:continue
 key=(lid,year)
 if key not in scorerKeys:
  scorerKeys.add(key);add({'date':date,'category':'goals','title':manifest['leagues'][lid]['name']+' 득점왕 기록','people':[row['scorerLabel']],'text':'출처에 기록된 시즌 득점 선두. 공동 수상자는 함께 표시합니다. 발표 시각은 확인되지 않았습니다.','precision':'season','basis':'시즌 득점 선두 · Wikidata','source':row['edition'].replace('http:','https:'),'license':'CC0-1.0','league':lid,'priority':3},year)
 else:
  e=next(e for e in events[year] if e['category']=='goals' and e.get('league')==lid);e['people']=sorted(set(e['people']+[row['scorerLabel']]))
for r in curated['administrativeCases']:
 add({**r,'category':'league','precision':'day','basis':'후일 행정 결정 · 원래 시즌과 구분','priority':5},r['season'])
# Official PL Playmaker awards begin in 2017/18; do not back-project the trophy.
assistKeys=set()
for year,name,total in curated['playmakers']:
 date=finalDate('england',year)
 if date:
  assistKeys.add(('england',year));add({'date':date,'category':'assists','title':'프리미어리그 도움왕 · Playmaker','people':[name],'value':total,'unit':'도움','text':'프리미어리그 공식 역대 Playmaker 수상자 표. 다른 제공자의 도움 집계와 구분합니다.','precision':'season','basis':'공식 수상 기록','source':curated['playmakerSource'],'league':'england','priority':4},year)
date=finalDate('england',2011)
if date:
 assistKeys.add(('england',2011));add({'date':date,'category':'assists','title':'프리미어리그 도움 선두 · 2011/12','people':['David Silva'],'value':15,'unit':'도움','text':'다비드 실바는 2011/12 리그 도움 선두를 기록했습니다. 2017/18부터 제정된 Playmaker 트로피의 수상으로 소급하지 않습니다.','precision':'season','basis':'시즌 도움 기록 · 공식상 제정 이전','source':'https://www.mancity.com/news/first-team/first-team-news/2020/january/man-city-decade-david-silva-impact-stats','league':'england','priority':3},2011)
# Last match winners for final replays and two-leg finals are resolved using the
# source aggregate winner, only on the final's final match date.
rawPath=ROOT/'research/expansion/uefa/matches.json.gz';uefa={}
if rawPath.exists():
 for m in json.loads(gzip.decompress(rawPath.read_bytes())):uefa[m['id']]=m
for cid,meta in manifest['cups'].items():
 cup=read(P/meta['file']);finals=[m for m in cup['matches'] if (cid.startswith('super-') or re.fullmatch(r'(?:Finals, )?Final(?: replay)?',m.get('stage',''),re.I))]
 if not finals:continue
 last=max(finals,key=lambda m:(m['date'],m.get('leg',0) or 0));date=last['date'];winner='';r=uefa.get(str(last.get('uefaMatchId','')))
 if not r:
  # Older UCL/country fixtures have different record identifiers. Require both
  # participants and score to agree after normalizing verified common aliases.
  def norm(s):
   s=re.sub(r'[^a-z0-9]','',canonical(s).lower());return {'manutd':'manchesterunitedfc','manchesterunited':'manchesterunitedfc','internazionale':'inter','acmilan':'milan','fcbayernmunchen':'bayernmunchen','bayernmunich':'bayernmunchen'}.get(s,s)
  candidates=[x for x in uefa.values() if x['kickOffTime']['date']==date and {norm(x['homeTeam'].get('internationalName','')),norm(x['awayTeam'].get('internationalName',''))}=={norm(last['home']),norm(last['away'])}]
  if len(candidates)==1:r=candidates[0]
 if r:
  team=(r.get('winner',{}).get('aggregate') or r.get('winner',{}).get('match') or {}).get('team',{})
  winner=team.get('translations',{}).get('displayOfficialName',{}).get('EN') or team.get('internationalName','')
 if not winner and last.get('shootoutWinner'):winner=last['shootoutWinner']
 if not winner and (len(finals)==1 or not any(m.get('leg') for m in finals)):
  score=last.get('pens') or [last['hg'],last['ag']]
  if score[0]!=score[1]:winner=last['home'] if score[0]>score[1] else last['away']
 if not winner and cid.startswith('ucl-'):winner=archive['champions'].get(str(cup['year']+1),'')
 if not winner:continue
 category='worldcup' if cid.startswith('wc-') else 'international' if cid.startswith('euro-') else 'europe'
 add({'date':date,'category':category,'title':cup['name']+' 우승','winner':canonical(winner),'text':f"결승 최종 경기 {canonical(last['home'])} {last['hg']}–{last['ag']} {canonical(last['away'])}"+(' · 승부차기 '+str(last['pens'][0])+'–'+str(last['pens'][1]) if last.get('pens') else '')+'. 두 경기 결승은 최종 합산 승자를 기준으로 합니다.','precision':'day','basis':'실제 대회 결승 기록','source':cup['source'],'cup':cid,'match':{k:last[k] for k in ['date','home','away']},'priority':5,'summer':category in ['worldcup','international'] and date[5:7] in ['07','08']},int(cid.rsplit('-',1)[1]) if category=='europe' else None)
uefa.clear()
for y,people,total in curated['worldCupGoldenBoot']:
 meta=manifest['cups'].get('wc-'+str(y))
 if not meta:continue
 date=meta['end'];source='https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/adidas-golden-boot-race-top-scorer' if y==2026 else curated['worldCupGoldenBootSource']
 add({'date':date,'category':'goals','title':str(y)+' 월드컵 '+('골든부트' if y>=1982 else '최다 득점 기록'),'people':people,'value':total,'unit':'골','text':'역대 대회 최다 득점·수상 기록입니다. 동률일 때 도움·출전 시간에 의한 수상 기준과 단순 공동 득점 선두는 다를 수 있습니다. 1982년 이전은 후대에 정리한 최다 득점 기록입니다.','precision':'day','basis':'월드컵 최다 득점·수상 기록','source':source,'cup':'wc-'+str(y),'priority':4,'summer':date[5:7] in ['07','08']})
# Season statistics from individual source appearances. Only whole-league game
# counts are eligible; these are provider leaderboards, never invented trophies.
compMap={'GB1':'england','ES1':'spain','IT1':'italy','FR1':'france','L1':'germany'};games={};stats=collections.defaultdict(lambda:{'games':set(),'goals':collections.Counter(),'assists':collections.Counter(),'names':{}})
for r in csv.DictReader((ROOT/'research/expansion/games.download').open()):
 if r['competition_id'] in compMap and r['date']<=CUTOFF:games[r['game_id']]=(compMap[r['competition_id']],int(r['season']))
appPath=Path('/workspace/sites/football-atlas/research/tm/appearances')
if not appPath.exists():appPath=ROOT/'research/expansion/appearances.csv'
if appPath.exists():
 for r in csv.DictReader(appPath.open()):
  if r['game_id'] not in games:continue
  key=games[r['game_id']];s=stats[key];s['games'].add(r['game_id']);pid=r['player_id'];s['names'][pid]=r['player_name'];s['goals'][pid]+=int(r['goals']);s['assists'][pid]+=int(r['assists'])
for (lid,year),s in sorted(stats.items()):
 info=next((x for x in manifest['leagues'][lid]['seasons'] if x['year']==year),None);date=finalDate(lid,year)
 if not info or not date or date>CUTOFF or len(s['games'])!=info['count']:continue
 for metric,known,unit in [('goals',scorerKeys,'골'),('assists',assistKeys,'도움')]:
  if (lid,year) in known or not s[metric]:continue
  best=max(s[metric].values())
  if not best:continue
  people=[s['names'][p] for p,total in s[metric].items() if total==best]
  add({'date':date,'category':metric,'title':manifest['leagues'][lid]['name']+(' 득점 선두' if metric=='goals' else '도움 선두')+' · 자료 집계','people':people,'value':best,'unit':unit,'text':f"시즌 {len(s['games'])}경기의 수록 개인 출전 자료에서 집계한 선두입니다. 도움의 정의는 제공자 기준이며 공식 수상 기록과 다를 수 있습니다.",'precision':'season','basis':'개인 출전 자료 집계 · 공식 수상과 구분','source':'https://github.com/dcaribou/transfermarkt-datasets','license':'CC0-1.0','league':lid,'priority':2},year)
# Keep date precision for the original award's calendar year and the ceremony.
for y,winner in archive['awards'].items():
 date=curated['ballonDates'].get(y,y+'-12-31');known=y in curated['ballonDates'];cancel=winner=='시상 취소'
 add({'date':date,'category':'ballon','title':y+' 발롱도르'+(' · 시상 취소' if cancel else ''),'people':[] if cancel else [winner],'text':('평가 대상은 '+str(int(y)-1)+'/'+str(int(y))[-2:]+' 시즌입니다. 2022년부터 시즌 평가로 전환됐으며 실제 발표일에 표시합니다.' if int(y)>=2022 else '수상 대상 연도는 '+y+'년입니다. '+('발표·시상 또는 취소 공지 날짜 기준입니다.' if known else '정확한 발표일이 미확보되어 연말부터 공개하는 연도 단위 기록입니다. 아래 날짜를 실제 시상일로 해석하지 마세요.')),'precision':'day' if known else 'year','awardYear':int(y),'evaluationSeason':int(y)-1 if int(y)>=2022 else None,'basis':'발롱도르 역대 수상 기록','source':curated['ballonSource'],'priority':4},int(y)-1 if int(y)>=2022 else None)
profiles=read(P/'players/index.json');knownNames={p['name']:p['id'] for p in profiles['players']};snapshot=profiles['meta']['snapshot'];localization=read(P/'localization.json');localizedIds=set(localization['players'])|{p['id'] for p in profiles['players'] if p.get('alias')};knownIds={p['id'] for p in profiles['players']};transfers=collections.defaultdict(list)
tp=Path('/workspace/sites/football-atlas/research/tm/kaggle-transfers')
if not tp.exists():tp=ROOT/'research/expansion/transfers.csv'
if tp.exists():
 for r in csv.DictReader(tp.open()):
  date=r['transfer_date']
  if not '1956-01-01'<=date<=min(CUTOFF,snapshot):continue
  if r['to_club_name'].lower()=='retired' and r['player_id'] in localizedIds:
   add({'date':date,'category':'retirement','title':'선수 은퇴 등록 기록','people':[r['player_name']],'text':canonical(r['from_club_name'])+' 소속 이후 은퇴로 등록된 이동 자료입니다. 계약 등록일이며 공식 발표일·마지막 출전일과 같다고 단정하지 않습니다.','player':r['player_id'],'precision':'registration','basis':'원자료 은퇴 등록일','source':'https://github.com/dcaribou/transfermarkt-datasets','priority':2})
  try:fee=float(r['transfer_fee'] or 0)
  except ValueError:continue
  if fee>=10000000:transfers[season(date)].append((fee,r))
for year,rs in transfers.items():
 unique={};
 for fee,r in sorted(rs,key=lambda x:-x[0]):unique.setdefault((r['player_id'],r['transfer_date'],r['to_club_id']),(fee,r))
 for i,(fee,r) in enumerate(unique.values()):
  if i>=10 and fee<50000000:continue
  add({'date':r['transfer_date'],'category':'transfer','title':'주요 이적 · 등록 기록','people':[r['player_name']],'origin':canonical(r['from_club_name']),'dest':canonical(r['to_club_name']),'feeEur':int(fee),'player':r['player_id'] if r['player_id'] in knownIds else '', 'text':'해당 시즌 이적료 상위 10건 또는 5,000만 유로 이상인 등록 기록입니다. 기본 금액의 제공자 집계이며 옵션·환율·계약 발표일과 차이가 날 수 있습니다.','precision':'registration','basis':'소속 이동 등록일 · 금액은 원자료 기준','source':'https://github.com/dcaribou/transfermarkt-datasets','priority':3},year)
for r in archive['transfers']:
 if r['year']>=2012:continue
 add({'date':str(r['year'])+'-12-31','category':'transfer','title':'주요 이적 · 연간 기록','people':[r['name']],'origin':r['origin'],'dest':r['dest'],'text':'연도만 확인된 역사적 이적입니다. 정확한 이적일을 만들지 않고 연말부터 공개합니다.','precision':'year','basis':'선별 연간 이적 자료','source':r['source'],'priority':3})
# Contemporary retirement announcements remain reporting, rather than guessed
# retirement dates. Headlines explicitly distinguish international retirement.
originals={}
for file in (ROOT/'research/news/guardian-days').glob('*.json'):
 for r in read(file).get('articles',[]):originals[r['id']]=r['title']
retirementPattern=re.compile(r'\b(?:retires|announces?(?: his| her)? retirement|hangs? up(?: his| her)? boots|calls? time on (?:his |her )?(?:playing )?career)\b',re.I)
for file in sorted((P/'news').glob('[12][0-9][0-9][0-9]-[01][0-9].json')):
 for r in read(file)['articles']:
  title=originals.get(r['id'],r['title'])
  if not retirementPattern.search(title) or '?' in title:continue
  add({'id':'sr-retirement-'+r['id'],'date':r['date'],'category':'retirement','title':r['title'],'text':'은퇴 발표와 관련된 당시 보도입니다. 국가대표 은퇴와 현역 은퇴, 예고와 이후 복귀는 원문에서 구분하며 발행일을 마지막 경기일로 바꾸지 않습니다.','precision':'day','basis':'은퇴 발표 관련 당시 보도 · '+r['publisher'],'source':r['source'],'priority':2})
# Every licensed history record is available in its own season; retain original
# titles, translation status and retrospective-source labels, not fake reporting.
for file in sorted((P/'news').glob('[12][0-9][0-9][0-9]-[01][0-9].json')):
 for r in read(file)['events']:
  if re.search(r'ballon|발롱',r['title'],re.I):continue
  category='retirement' if re.search(r'\bretire(?:s|d|ment)\b|은퇴',r['title'],re.I) else 'issue'
  add({'id':'sr-'+r['id'],'date':r['date'],'category':category,'title':r['title'],'text':'후대 사건 기록에 근거한 회고 항목입니다. 당시 보도·초판 기사와 구분합니다.','precision':'day','basis':'후대 사건 기록','source':r['source'],'license':r.get('license',''),'titleTranslation':r.get('titleTranslation','original'),'priority':1})
for r in read(P/'news/editorial.json'):
 category='transfer' if r.get('player') else 'retirement' if '은퇴' in r['title'] else 'issue'
 add({'id':'sr-'+r['id'],'date':r['date'],'category':category,'title':r['title'],'text':r['text'],'precision':'day','basis':'당시 발행된 주요 보도 · '+r['publisher'],'source':r['source'],'priority':3})
index={};counts=collections.Counter()
for year in range(1955,2027):
 rs=sorted(events[year],key=lambda r:(r['date'],-r['priority'],r['id']));file=OUT/f'{year}.json';summary={'season':year,'start':max('1956-01-01',f'{year}-07-01'),'nominalEnd':f'{year+1}-06-30','reviewEnd':max([f'{year+1}-06-30']+[e['date'] for e in rs if (e['category'] in ['league','europe','goals','assists'] or e.get('evaluationSeason')==year) and '후일 행정' not in e['basis']]),'cutoff':CUTOFF,'events':rs};dump(file,summary)
 index[str(year)]={'file':'season-recaps/'+file.name,'count':len(rs),'bytes':file.stat().st_size,'start':summary['start'],'nominalEnd':summary['nominalEnd'],'reviewEnd':summary['reviewEnd']};counts.update(r['category'] for r in rs)
meta={'version':1,'cutoff':CUTOFF,'seasons':index,'categories':dict(counts),'policy':'July–June base; optional following July/August international winners. Season/year precision and registration dates are labeled. No visible event after the selected date.'};dump(OUT/'index.json',meta)
dump(OUT/'quality.json',{'checks':['league entity sport and country disambiguation','English division level changes in 1992','winner reconciled to season participants','round-robin source winner must be among maximum-point teams; source honors distinguish tie-breaks','revoked and unawarded title exceptions','ceremony versus award-year separation','registration versus announcement dates','date-closed spoiler guard'],'rejectedHonorStatements':rejectedHonors,'acceptedHonorStatements':len(acceptedHonors),'limitations':['Unresolved or unmatched winner statements are excluded, including possible valid names not yet reconciled.','Not every league or season has scorer, assist, retirement or award evidence.','Provider assist definitions and official awards are displayed separately.']})
print('Season recap events',sum(counts.values()),dict(counts),flush=True)
