import json,re,hashlib,concurrent.futures,urllib.request,urllib.parse,collections
from pathlib import Path
import unicodedata
def norm(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c))
 s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|club|football|calcio|societa|sportiva|spa|sad|srl)\b',' ',s)
 return re.sub(r'[^a-z0-9가-힣]','',s)
P=Path('research/localization');O=Path('dist/replay');L=json.load(open(O/'localization.json'));M=json.load(open(O/'manifest.json'))
# Only unique, exact normalized-name matches, within the league's country when known.
paths=[x['path'] for x in json.load(open(P/'team-logos-tree.json'))['tree'] if x['path'].endswith('.svg') and x['path'].startswith('logos/')]
idx=collections.defaultdict(list)
for p in paths:idx[norm(Path(p).stem.replace('_',' '))].append(p)
country={'england':'england','spain':'spain','germany':'germany','france':'france','italy':'italy','holland':'netherlands','portugal':'portugal','scotland':'scotland','belgium':'belgium','greece':'greece','turkey':'turkey','korea':'south-korea','japan':'japan','brazil':'brazil','argentina':'argentina','usa':'usa','mexico':'mexico','sweden':'sweden','norway':'norway','denmark':'denmark','finland':'finland','ireland':'ireland','china':'china','austria':'austria','switzerland':'switzerland'}
requests={};targets=collections.defaultdict(set)
for key,league in M['leagues'].items():
 folder=country.get(key.split('-')[0]);names=set()
 for s in league['seasons']:
  for m in json.load(open(O/s['file']))['matches']:names.update([m['home'],m['away']])
 for name in names:
  k=norm(name);rec=L['teams'].get(k,{})
  if rec.get('crest'):continue
  ps=idx.get(k,[]);local=[p for p in ps if p.split('/')[1]==folder];candidates=local or ps
  if len(candidates)==1:
   path=candidates[0];requests[path]='https://raw.githubusercontent.com/JoseArroyave/football-logos/main/'+urllib.parse.quote(path,safe='/');targets[path].add(k)
# Explicit official Korean short-name aliases from the official fixture source.
kr={'강원':'Gangwon_FC','광주':'Gwangju_FC','김천':'Gimcheon_Sangmu_FC','상주':'Gimcheon_Sangmu_FC','대구':'Daegu_FC','대전':'Daejeon_Hana_Citizen','부산':'Busan_IPark','서울':'FC_Seoul','성남':'Seongnam_FC','수원':'Suwon_Samsung_Bluewings','수원FC':'Suwon_FC','울산':'Ulsan_HD_FC','인천':'Incheon_United','전남':'Jeonnam_Dragons','전북':'Jeonbuk','제주':'Jeju_SK_FC','포항':'Pohang_Steelers','경남':'Gyeongnam_FC','안산':'Ansan_Greeners_FC','안양':'FC_Anyang','부천':'Bucheon_FC_1995','서울E':'Seoul_E-Land_FC','충남아산':'Chungnam_Asan_FC','천안':'Cheonan_City_FC','충북청주':'Chungbuk_Cheongju_FC','김포':'Gimpo_FC','화성':'Hwaseong_FC','용인':'Yongin_FC','파주':'Paju_Frontier_FC','김해':'Gimhae_FC_2008'}
for name,stem in kr.items():
 path='logos/south-korea/'+stem+'.svg'
 if path not in paths:continue
 requests[path]='https://raw.githubusercontent.com/JoseArroyave/football-logos/main/'+path;targets[path].add(norm(name))
# Include K League competition identification emblems.
for stem in ['K_League_1','K_League_2']:
 path='logos/south-korea/'+stem+'.svg';requests[path]='https://raw.githubusercontent.com/JoseArroyave/football-logos/main/'+path;targets[path].add(norm('K리그1' if stem.endswith('1') else 'K리그2'))
results={};bad=[]
def get(it):
 path,url=it;f='repo-'+hashlib.sha1(path.encode()).hexdigest()[:12]+'.svg';p=Path('dist/assets/crests')/f
 if not p.exists():
  b=urllib.request.urlopen(url,timeout=20).read()
  if b'<svg' not in b[:1000] or b'<script' in b.lower():raise ValueError('unsafe/non-svg')
  p.write_bytes(b)
 return path,'assets/crests/'+f
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 pending={pool.submit(get,t):t[0] for t in requests.items()}
 for f in concurrent.futures.as_completed(pending):
  try:k,v=f.result();results[k]=v
  except Exception as e:bad.append([pending[f],str(e)])
for path,file in results.items():
 for key in targets[path]:L['teams'].setdefault(key,dict(ko=next((n for n in kr if norm(n)==key),'')))['crest']=file
# Resolve aliases that share a unique Korean label to the same known ID and asset.
groups=collections.defaultdict(list)
for rec in L['teams'].values():
 if rec.get('ko'):groups[rec['ko']].append(rec)
for ko,recs in groups.items():
 ids={r['id'] for r in recs if r.get('id')};assets={r['crest'] for r in recs if r.get('crest')}
 if len(ids)==1:
  id=next(iter(ids));base=L['teamIds'].get(id,{})
  for r in recs:r.setdefault('id',id);r.update({k:v for k,v in base.items() if k=='crest'})
 elif len(assets)==1:
  for r in recs:r.setdefault('crest',next(iter(assets)))
# Flag fallback is explicitly a national flag, not a football federation badge.
flags={};needed={L['countryCodes'][name] for name in M['nations'] if name in L['countryCodes'] and not L['teams'].get(norm(name),{}).get('crest')}
def flag(code):
 p=Path('dist/assets/crests')/('flag-'+code+'.svg')
 if not p.exists():
  b=urllib.request.urlopen('https://flagcdn.com/'+code+'.svg',timeout=15).read()
  if b'<svg' not in b[:1000]:raise ValueError('not SVG flag')
  p.write_bytes(b)
 return code,'assets/crests/flag-'+code+'.svg'
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 pending={pool.submit(flag,c):c for c in needed}
 for f in concurrent.futures.as_completed(pending):
  try:k,v=f.result();flags[k]=v
  except Exception:pass
L['flags']=flags;L['crestNotice']='현재 식별용 엠블럼입니다. 선택한 과거 연도의 디자인과 다를 수 있습니다. 엠블럼이 없으면 국기 또는 이니셜을 구분해 표시합니다.'
L['sources'].extend(['https://github.com/JoseArroyave/football-logos','https://flagcdn.com/'])
(O/'localization.json').write_text(json.dumps(L,ensure_ascii=False,separators=(',',':')))
(P/'extra-assets.json').write_text(json.dumps(dict(files=results,targets={k:list(v) for k,v in targets.items()},flags=flags,failed=bad),ensure_ascii=False))
print('Additional crest assets',len(results),'national flags',len(flags),'failed',len(bad))
