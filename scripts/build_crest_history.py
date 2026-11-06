"""Publish only crest periods with identified original assets and evidence.

Year-only transitions are intentionally left uncovered for the transition year;
an exact January 1 adoption date is never inferred. Club identity crests do not
represent every anniversary, sponsor, kit or monochrome variant.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
def add(team,asset,start,end,period,source,evidence):
    rows.append(dict(teamId=str(team),crest='assets/crests/history/'+asset,fromDate=start,toDate=end,period=period,source=source,evidence=evidence))
add(281,'manchester-city-1997.png','1998-01-01','2016-06-30','1997–2016 독수리형','https://www.mancity.com/news/club-news/club-news/2015/october/badge-consultation','구단 배지 연혁·2016/17 전환; 1997년 도입일 미확인')
add(281,'Manchester-City-v2016.svg','2016-07-01','2026-10-31','2016/17– 원형','https://www.mancity.com/news/club-news/club-news/2016/june/mcfc-new-badge-is-here','구단 공식 2016/17 사용 안내')
add(506,'juventus-2004.png','2005-01-01','2017-06-30','2004–2017 타원형','https://www.juventus.com/en/news/articles/new-logo-new-era','2004 리디자인·2017년 7월 신규 로고 채택; 2004 도입일 미확인')
# Guardian's 2015 repository retained the older Inter art. Visual comparison
# with the club's own history identifies it as the 2007 base crest, not 2014.
add(46,'inter-2014.png','2008-01-01','2013-12-31','2007–2014 기본 클럽 문장','https://www.inter.it/en/news/2021-03-27-history-inter-crest','공식 연혁과 별·원·모노그램 대조. 기념 유니폼 변형 미반영; 전환 연도 제외')
for version,end in [(1996,2001),(2002,2016),(2017,2023),(2024,2026)]:
    add(27,f'FC-Bayern-Munchen-v{version}.svg',f'{version+1}-01-01',f'{end}-12-31' if end<2026 else '2026-10-31',f'{version} 버전','https://fcbayern.com/store/en-zz/i/logo','구단 역사·FCLOGO 버전 메타데이터 대조; 전환 연도 제외')
add(148,'Tottenham-Hotspur-Football-Club-v2006.svg','2006-01-20','2024-11-17','2006–2024 클럽 배지','https://www.tottenhamhotspur.com/news/1031199/club-unveils-new-badge','구단의 2006년 1월 20일 공개와 2024년 11월 18일 리마스터 발표')
add(148,'Tottenham-Hotspur-Football-Club-v2024.svg','2024-11-18','2026-10-31','2024 리마스터','https://www.tottenhamhotspur.com/news/1009867/tottenham-hotspur-unveils-remastered-brand-identity','공식 브랜드 공개일 기준; 유니폼 교체일을 뜻하지 않음')
add(13,'Arsenal-FC-v2002.svg','2003-01-01','2026-10-31','2002– 방패형','https://www.arsenal.com/history/the-arsenal-crest','구단 연혁·FCLOGO 2002 버전. 전환 연도 제외')
for r in rows:
    assert (ROOT/'dist'/r['crest']).stat().st_size>100
p=ROOT/'data/crest-history.json';p.write_text(json.dumps({'periods':rows,'assetSources':['https://github.com/guardian/football-assets/tree/0ca07ae02935f46fdfd934531e49d1e08f09b41c/source/crests','https://github.com/xl2ryan/fclogo'],'policy':'Base club identity, not every shirt variant. Unverified periods retain a current identification crest with an explicit warning.'},ensure_ascii=False,indent=2)+'\n')
p=ROOT/'dist/replay/localization.json';d=json.loads(p.read_text());d['crestHistory']={}
for r in rows:d['crestHistory'].setdefault(r['teamId'],[]).append({**r,'from':r['fromDate'],'to':r['toDate']})
d['crestHistoryMeta']={'periods':len(rows),'clubs':len(d['crestHistory']),'coverage':'Verified periods only; current identification fallback elsewhere'}
p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print('Temporal crests:',len(rows),'periods /',len(d['crestHistory']),'clubs')
