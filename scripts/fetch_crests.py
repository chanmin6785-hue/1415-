"""Cache current identification crests; no claim of historical period accuracy."""
import urllib.request,json,concurrent.futures,time,hashlib,struct
from pathlib import Path
O=Path('dist/assets/crests');O.mkdir(parents=True,exist_ok=True)
clubs=json.load(open('dist/replay/players/clubs.json'));success={};failed=[]
def get(item):
 id,club=item;p=O/(id+'.png');url=f'https://tmssl.akamaized.net/images/wappen/head/{id}.png'
 if p.exists():b=p.read_bytes()
 else:
  b=urllib.request.urlopen(url,timeout=15).read()
 if not b.startswith(b'\x89PNG\r\n\x1a\n') or len(b)<180:raise ValueError('not PNG')
 width,height=struct.unpack('>II',b[16:24])
 if width<15 or height<15:raise ValueError('tiny placeholder')
 p.write_bytes(b);return id,dict(file='assets/crests/'+id+'.png',source=url,period='current',name=club['name'],sha=hashlib.sha256(b).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 pending={pool.submit(get,t):t[0] for t in clubs.items()};n=0
 for f in concurrent.futures.as_completed(pending):
  id=pending[f]
  try:k,m=f.result();success[k]=m
  except Exception as e:failed.append([id,str(e)])
  n+=1
  if n%200==0:print('Crests',n,'/',len(clubs),'cached',len(success),flush=True)
Path('research/localization/crest-manifest.json').write_text(json.dumps(dict(crests=success,failed=failed),ensure_ascii=False))
print('Done',len(success),'crests;',len(failed),'unavailable',flush=True)
