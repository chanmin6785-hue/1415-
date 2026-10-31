"""Download public CC0 dataset mirrors. No account keys required."""
import urllib.request,shutil,concurrent.futures
from pathlib import Path
P=Path('research/tm');P.mkdir(parents=True,exist_ok=True)
files={'players':'kaggle-players','transfers':'kaggle-transfers','appearances':'appearances','clubs':'clubs','competitions':'competitions','national_teams':'national_teams'}
def get(item):
 name,target=item;url='https://www.kaggle.com/api/v1/datasets/download/davidcariboo/player-scores/'+name+'.csv'
 with urllib.request.urlopen(url,timeout=60) as r,open(P/target,'wb') as f:shutil.copyfileobj(r,f)
 print(name,(P/target).stat().st_size,'bytes',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,files.items()))
