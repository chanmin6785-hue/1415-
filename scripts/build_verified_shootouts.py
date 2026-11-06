"""Keep verified shoot-out order distinct from football minutes and goal totals."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'dist/replay'
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
rows=read(ROOT/'data/verified-shootouts.json');index=read(P/'match-archive/index.json')
def attach(m):
    for r in rows:
        if r['date']!=m['date'] or not all(any(t.lower() in name.lower() for name in [m['home'],m['away']]) for t in r['teams']):continue
        names={t:next(n for n in [m['home'],m['away']] if t.lower() in n.lower()) for t in r['teams']}
        kicks=[{'team':names[t],'player':p,'outcome':o} for t,p,o in r['kicks']]
        score=[sum(k['team']==n and k['outcome']=='scored' for k in kicks) for n in [m['home'],m['away']]]
        assert score==m.get('pens'),(m['date'],score,m.get('pens'))
        m.update(shootout=kicks,shootoutSource=r['source'],shootoutCorroboration=r['corroboration'],shootoutPrecision='verified kick order; no invented clock times');return True
    return False
for month in {r['date'][:7] for r in rows}:
    file=P/'match-archive'/(month+'.json');d=read(file)
    for m in d['matches']:attach(m)
    dump(file,d);index['months'][month]['bytes']=file.stat().st_size
dump(P/'match-archive/index.json',index)
file=P/'stories.json';d=read(file)
for m in d['features']:attach(m)
dump(file,d)
print('Verified shoot-out sequences:',len(rows))
