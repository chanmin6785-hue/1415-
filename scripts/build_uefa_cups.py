"""Add primary UEFA cup schedules without exposing subsequent aggregate scores.

UEFA seasonYear conventions vary by competition and era. Infer the displayed
season from the most frequent July/June match season inside each official
edition, rather than assuming seasonYear is always the starting year.
"""
import collections,gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'dist/replay';raw=ROOT/'research/expansion/uefa/matches.json.gz'
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def name(t):return t.get('translations',{}).get('displayOfficialName',{}).get('EN') or t.get('internationalName','')
manifest=read(P/'manifest.json');editions=collections.defaultdict(list)
# Old Super Cups can span January/February of the following year. The
# match feed indexes some of these by calendar year. Re-group July–June.
for cid in list(manifest['cups']):
    if cid.startswith('super-') and manifest['cups'][cid].get('officialUefa'):
        old=manifest['cups'].pop(cid);(P/old['file']).unlink(missing_ok=True)
for r in json.loads(gzip.decompress(raw.read_bytes())):
    c=str(r['competition']['id'])
    if c not in ['1','14','2','9','2019']:continue
    edition=str(int(r['kickOffTime']['date'][:4])-(int(r['kickOffTime']['date'][5:7])<7)) if c=='9' else str(r['seasonYear'])
    editions[(c,edition)].append(r)
added=0
for (comp,feedYear),rs in sorted(editions.items()):
    years=collections.Counter(int(r['kickOffTime']['date'][:4])-(int(r['kickOffTime']['date'][5:7])<7) for r in rs)
    year=years.most_common(1)[0][0]
    if comp=='9':year=int(feedYear)
    prefix={'1':'ucl','14':'uel','2':'cwc','9':'super','2019':'conference'}[comp];cid=f'{prefix}-{year}'
    # Preserve independently checked UCL editions; add the current partial one.
    if cid in manifest['cups'] and prefix=='ucl':continue
    label={'1':'챔피언스리그','14':'UEFA컵' if year<2009 else '유로파리그','2':'컵위너스컵','9':'UEFA 슈퍼컵','2019':'컨퍼런스리그'}[comp]
    title=label+' '+(str(year) if prefix=='super' else f'{year}/{str(year+1)[-2:]}');matches=[]
    for r in rs:
        score=r.get('score',{}).get('total') or r.get('score',{}).get('regular') or {};h,a=score.get('home'),score.get('away')
        if not isinstance(h,int) or not isinstance(a,int):continue
        rd=r.get('round') or {};stage=rd.get('translations',{}).get('name',{}).get('EN') or rd.get('metaData',{}).get('name','');g=r.get('group') or {};group=g.get('translations',{}).get('name',{}).get('EN') or g.get('metaData',{}).get('name','')
        m={'date':r['kickOffTime']['date'],'home':name(r['homeTeam']),'away':name(r['awayTeam']),'hg':h,'ag':a,'stage':stage,'group':group if rd.get('mode') in ['GROUP','LEAGUE'] else '','uefaMatchId':r['id'],'roundOrder':rd.get('orderInCompetition',0)}
        if r.get('leg',{}):m['leg']=r['leg'].get('number')
        if r.get('score',{}).get('penalty'):m['pens']=[r['score']['penalty']['home'],r['score']['penalty']['away']]
        # Primary feeds include eventual two-leg aggregate even on first-leg
        # rows; never export it to a historical fixture's day-one snapshot.
        matches.append(m)
    if not matches:continue
    matches.sort(key=lambda m:(m['roundOrder'],m['date'],m['uefaMatchId']));file='cups/'+cid+'.json';source='https://match.uefa.com/v5/matches?competitionId='+comp+('' if comp=='9' else '&seasonYear='+feedYear)
    dump(P/file,{'name':title,'year':year,'matches':matches,'source':source,'winPoints':2 if year<1995 else 3,'coverage':'Finished UEFA source fixtures through cutoff; future scheduled fixtures after the collection cutoff are not included.','officialSeasonYear':feedYear})
    manifest['cups'][cid]={'name':title,'file':file,'count':len(matches),'start':min(m['date'] for m in matches),'end':max(m['date'] for m in matches),'officialUefa':True};added+=1
manifest['totals']['cupEditions']=len(manifest['cups']);manifest['totals']['europeanMatches']=sum(v['count'] for k,v in manifest['cups'].items() if k.split('-')[0] in ['ucl','uel','cwc','super','conference']);manifest['totals']['files']=sum(1 for _ in P.rglob('*.json'));dump(P/'manifest.json',manifest)
print('Added/updated UEFA cup editions',added,'total editions',len(manifest['cups']))
