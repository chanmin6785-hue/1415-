"""Preserve Hangul syllables and attach explicit, source-identified short aliases."""
import collections,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'dist/replay/localization.json';d=json.loads(P.read_text())
def key(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c));s=unicodedata.normalize('NFC',s)
 return re.sub(r'[^a-z0-9가-힣]','',s)
for field in ['teams','exact']:d[field].pop('',None)
grouped=collections.defaultdict(list)
for ident,r in d['teamIds'].items():
 if r.get('ko'):grouped[key(r['ko'])].append(r)
for k,rs in grouped.items():
 if len({r['id'] for r in rs})==1:d['teams'][k]=rs[0]
aliases={'전북':'6502','울산':'3535','포항':'311','서울':'6500','수원':'3301','수원FC':'31622','성남':'3610','인천':'2996','김천':'6505','상주':'6505','서울이랜드':'46292'}
for name,ident in aliases.items():
 if ident in d['teamIds']:d['teams'][key(name)]={**d['teamIds'][ident],'ko':name}
d['identityKeyPolicy']='Latin accent folding followed by NFC composition; distinct Hangul club names stay distinct. Short Korean display aliases do not replace historical names with current names.'
P.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print('Korean club identity keys repaired:',len(aliases),'short aliases')
