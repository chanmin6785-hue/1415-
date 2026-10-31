import json,collections
from pathlib import Path
O=Path('dist/replay');M=json.load(open(O/'manifest.json'))
for league,folder,name in [(1,'kleague','K리그1'),(2,'kleague2','K리그2')]:
 seasons=collections.defaultdict(list);seen=set()
 for p in Path('research',folder).glob('*.json'):
  for r in json.load(open(p)):
   if r.get('leagueId')!=league or r.get('meetSeq')!=league or r.get('endYn')!='Y' or r.get('isSemiPlayOff')=='Y' or r.get('codeName')=='Play Off':continue
   d=r['gameDate'].replace('.','-')
   if d>M['cutoff']:continue
   ident=(r['year'],r['gameId'])
   if ident in seen:continue
   seen.add(ident)
   assert r['homeGoal'] is not None and r['awayGoal'] is not None
   m=dict(date=d,home=r['homeTeamName'],away=r['awayTeamName'],hg=int(r['homeGoal']),ag=int(r['awayGoal']),round=int(r['roundId']),phase=r.get('codeName',''),homeCode=r['homeTeam'],awayCode=r['awayTeam'],venue=r.get('fieldName',''))
   seasons[int(r['year'])].append(m)
 if not seasons:continue
 key='korea' if league==1 else 'korea-2';infos=[]
 for y,ms in sorted(seasons.items()):
  ms.sort(key=lambda m:(m['date'],m['home']));groups=collections.defaultdict(set)
  for m in ms:
   if m['phase'] in ['파이널A','파이널B']:groups[m['phase']].update([m['home'],m['away']])
  splitStart=min((m['date'] for m in ms if m['phase'] in groups),default=None)
  f=f'leagues/{key}-{y}.json';data=dict(id=key,season=y,seasonLabel=str(y),matches=ms,source='https://www.kleague.com/getScheduleList.do',calendar=True,note='공식 일정·결과 기반. 승점 삭감·행정 판정은 별도 반영하지 않은 재계산 순위입니다. 승강 플레이오프는 정규리그와 분리했습니다.',splitGroups={k:sorted(groups[k]) for k in sorted(groups)},splitStart=splitStart)
  (O/f).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));infos.append(dict(year=y,file=f,count=len(ms),start=ms[0]['date'],end=ms[-1]['date'],calendar=True,label=str(y)))
 M['leagues'][key]=dict(country='대한민국 한국',name=name,code='KOR' if league==1 else 'KOR2',region='아시아',calendar=True,seasons=infos,note='2013년 이후 공식 결과 수록. K리그1은 파이널 A·B 구분을 공개 시점 이후 반영합니다. 과거 승점 삭감·행정 처분은 미반영입니다.')
M['totals']['leagueMatches']=sum(x['count'] for l in M['leagues'].values() for x in l['seasons']);M['totals']['leagueCount']=len(M['leagues']);M['totals']['files']=len(list(O.rglob('*.json')))
(O/'manifest.json').write_text(json.dumps(M,ensure_ascii=False,separators=(',',':')))
print('Korea',[(k,len(v['seasons']),sum(x['count'] for x in v['seasons'])) for k,v in M['leagues'].items() if k.startswith('korea')]);print(M['totals'])
