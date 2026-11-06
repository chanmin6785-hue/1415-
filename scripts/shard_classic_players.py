"""Keep the source-backed master in git; deliver only one classic profile shard."""
import collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist/replay/players'
master=ROOT/'data/classic-player-profiles.json'
legacy=OUT/'classic.json'
if not master.exists() and legacy.exists():master.write_bytes(legacy.read_bytes())
d=json.loads(master.read_text());parts=collections.defaultdict(dict);index=[]
for p in d['players']:
    shard=int(hashlib.sha256(p['id'].encode()).hexdigest()[:8],16)%32;parts[shard][p['id']]=p
    index.append({**{k:p.get(k,'') for k in ['id','name','alias','birth','birthYear','country','position','first','last']},'shard':shard,'historic':True})
for part,rows in parts.items():(OUT/f'classic-part-{part:02}.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
(OUT/'classic-index.json').write_text(json.dumps({'meta':d['meta'],'players':index},ensure_ascii=False,separators=(',',':')))
legacy.unlink(missing_ok=True)
print('Classic profiles:',len(index),'in',len(parts),'lazy detail shards')
