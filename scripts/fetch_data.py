"""Fetch the public sources used by the checked-in 2026-10-31 snapshot.
Run from the repository root. Raw downloads stay in ignored research/.
"""
import concurrent.futures,json,urllib.request
from pathlib import Path
P=Path('research');P.mkdir(exist_ok=True)
URLS={}
for k in ['england','spain','italy','germany','france','holland','portugal','scotland','belgium','greece','turkey']:
 URLS[k+'.csv']='https://raw.githubusercontent.com/jalapic/engsoccerdata/master/data-raw/'+k+'.csv'
for k,f in [('intl','results'),('shootouts','shootouts'),('goalscorers','goalscorers')]:URLS[k+'.csv']='https://raw.githubusercontent.com/martj42/international_results/master/'+f+'.csv'
for k,code in [('england','E0'),('spain','SP1'),('italy','I1'),('germany','D1'),('france','F1'),('holland','N1'),('portugal','P1'),('scotland','SC0'),('belgium','B1'),('greece','G1'),('turkey','T1'),('england-2','E1'),('england-3','E2'),('england-4','E3'),('germany-2','D2')]:
 for season in ['2526','2627']:URLS[f'{k}-{season}.csv']=f'https://www.football-data.co.uk/mmz4281/{season}/{code}.csv'
for y in range(1958,2027,4):URLS[f'wc{y}.json']=f'https://raw.githubusercontent.com/openfootball/worldcup.json/master/{y}/worldcup.json'
for y in range(1955,2016):URLS[f'ucl-{y}.csv']=f'https://raw.githubusercontent.com/footballcsv/europe-champions-league/master/{y}-{str(y+1)[2:]}/champs.csv'
for y in range(2016,2026):URLS[f'ucl-{y}.txt']=f'https://raw.githubusercontent.com/openfootball/champions-league/master/{y}-{str(y+1)[2:]}/cl.txt'
for k,c in [('japan','JPN'),('brazil','BRA'),('argentina','ARG'),('usa','USA'),('mexico','MEX'),('norway','NOR'),('sweden','SWE'),('denmark','DNK'),('finland','FIN'),('ireland','IRL'),('china','CHN'),('austria','AUT'),('switzerland','SWZ')]:URLS[k+'-world.csv']='https://www.football-data.co.uk/new/'+c+'.csv'
def download(item):
 name,url=item
 req=urllib.request.Request(url,headers={'User-Agent':'Football-Time-Machine-data-builder/2.0'})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read()
 (P/name).write_bytes(b)
 return name,len(b)
failures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 pending={pool.submit(download,item):item for item in URLS.items()}
 for future in concurrent.futures.as_completed(pending):
  name,url=pending[future]
  try:_,size=future.result();print(name,size)
  except Exception as e:failures.append((name,str(e)));print('FAILED',name,str(e))
if failures:raise SystemExit('Incomplete source download: '+repr(failures))
print('Downloaded',len(URLS),'sources. Build using scripts/build_replay.py, enrich_ucl.py, make_stories.py.')
