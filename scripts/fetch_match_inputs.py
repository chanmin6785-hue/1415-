"""Download public factual inputs; checkpoint files and stop on access refusal.

No paid accounts, credentials or publisher article bodies. Raw inputs remain
ignored by git. Large downloads stream to disk instead of occupying RAM.
"""
import hashlib,json,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/expansion';OUT.mkdir(parents=True,exist_ok=True)
rows=json.loads((ROOT/'data/match-inputs.json').read_text())['files'];receipt=[]
for r in rows:
    p=OUT/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        req=urllib.request.Request(r['url'],headers={'User-Agent':'FootballHistoryReplay/1.0'})
        temp=p.with_suffix(p.suffix+'.partial')
        try:
            with urllib.request.urlopen(req,timeout=60) as response,temp.open('wb') as f:
                while chunk:=response.read(1024*1024):f.write(chunk)
            temp.replace(p)
        except Exception:
            temp.unlink(missing_ok=True);raise
        time.sleep(.7)
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    receipt.append({**r,'bytes':p.stat().st_size,'localSha256':h.hexdigest(),'hashBasis':'Local input bytes; converted World Cup CSV can differ in serialization from publisher CSV' });print(r['path'],p.stat().st_size,flush=True)
(OUT/'input-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
