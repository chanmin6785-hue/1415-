"""Read-only public K League schedule snapshot. Month cache; no live credentials."""
import urllib.request,json,concurrent.futures,time
from pathlib import Path
P=Path('research/kleague');P.mkdir(parents=True,exist_ok=True)
YEARS=range(1983,2027)
def get(t):
 y,m=t;p=P/f'{y}-{m:02}.json'
 if p.exists():return y,m,len(json.load(open(p)))
 body=json.dumps({'year':str(y),'month':f'{m:02}','leagueId':1}).encode()
 req=urllib.request.Request('https://www.kleague.com/getScheduleList.do',data=body,headers={'Content-Type':'application/json','Accept':'application/json','User-Agent':'Football-Time-Machine/2.0'})
 with urllib.request.urlopen(req,timeout=20) as r:a=json.load(r)
 if str(a.get('resultCode'))!='200':raise ValueError(a.get('resultMsg'))
 ms=a.get('data',{}).get('scheduleList',[])
 for x in ms:
  if int(x['year'])!=y or x['gameDate'][:4]!=str(y):raise ValueError('wrong year')
 p.write_text(json.dumps(ms,ensure_ascii=False));return y,m,len(ms)
tasks=[(y,m) for y in YEARS for m in range(1,13) if y<2026 or m<=10];n=0;count=0;bad=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 pending={pool.submit(get,t):t for t in tasks}
 for f in concurrent.futures.as_completed(pending):
  try:r=f.result();count+=r[2]
  except Exception as e:bad.append((pending[f],str(e)))
  n+=1
  if n%60==0:print('Months',n,'/',len(tasks),'records',count,flush=True)
print('Completed',n,'months; records',count,'failed',len(bad),bad[:10],flush=True)
