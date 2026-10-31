"""Build source-backed Korean display names, leaving canonical source identities intact."""
import json,csv,re,unicodedata,collections,hashlib
from pathlib import Path
P=Path('research/localization');O=Path('dist/replay')
def norm(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c))
 s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|club|football|calcio|societa|sportiva|spa|sad|srl)\b',' ',s)
 return re.sub(r'[^a-z0-9가-힣]','',s)
manual={}
text='''Barnsley|반즐리
Port Vale|포트 베일
Bristol City|브리스틀 시티
Blackpool|블랙풀
Rotherham United|로더럼 유나이티드
Preston North End|프레스턴 노스 엔드
Sheffield United|셰필드 유나이티드
Huddersfield Town|허더즈필드 타운
Gillingham|질링엄
Reading|레딩
Portsmouth|포츠머스
Bristol Rovers|브리스틀 로버스
Walsall|월솔
Swansea City|스완지 시티
Brentford|브렌트퍼드
Burnley|번리
Cardiff City|카디프 시티
Notts County|노츠 카운티
Millwall|밀월
Plymouth Argyle|플리머스 아가일
Crewe Alexandra|크루 알렉산드라
Bradford City|브래드퍼드 시티
Leyton Orient|레이턴 오리엔트
Northampton Town|노샘프턴 타운
Swindon Town|스윈던 타운
Birmingham City|버밍엄 시티
Sheffield Wednesday|셰필드 웬즈데이
Middlesbrough|미들즈브러
Watford|왓퍼드
AFC Bournemouth|본머스
Bournemouth|본머스
Charlton Athletic|찰턴 애슬레틱
Hull City|헐 시티
Wolverhampton Wanderers|울버햄프턴 원더러스
Wolves|울버햄프턴 원더러스
Fulham|풀럼
Nottingham Forest|노팅엄 포리스트
Nott'm Forest|노팅엄 포리스트
Stoke City|스토크 시티
Bolton Wanderers|볼턴 원더러스
Sunderland|선덜랜드
West Bromwich Albion|웨스트브로미치 앨비언
West Brom|웨스트브로미치 앨비언
Shrewsbury Town|슈루즈버리 타운
Peterborough United|피터버러 유나이티드
Leeds United|리즈 유나이티드
Blackburn Rovers|블랙번 로버스
Blackburn|블랙번 로버스
Rochdale|로치데일
Colchester United|콜체스터 유나이티드
Leicester City|레스터 시티
Leicester|레스터 시티
Crystal Palace|크리스털 팰리스
Norwich City|노리치 시티
Norwich|노리치 시티
Ipswich Town|입스위치 타운
Ipswich|입스위치 타운
West Ham United|웨스트햄 유나이티드
West Ham|웨스트햄 유나이티드
Wigan Athletic|위건 애슬레틱
Wigan|위건 애슬레틱
Southampton|사우샘프턴
Coventry City|코번트리 시티
Derby County|더비 카운티
Derby|더비 카운티
Luton Town|루턴 타운
Oxford United|옥스퍼드 유나이티드
Cambridge United|케임브리지 유나이티드
Lincoln City|링컨 시티
Mansfield Town|맨스필드 타운
Doncaster Rovers|동커스터 로버스
Chesterfield|체스터필드
Exeter City|엑서터 시티
Grimsby Town|그림즈비 타운
Hartlepool United|하틀리풀 유나이티드
Scunthorpe United|스컨소프 유나이티드
Tranmere Rovers|트랜미어 로버스
Stockport County|스톡포트 카운티
Oldham Athletic|올덤 애슬레틱
Carlisle United|칼라일 유나이티드
Bury|베리
Chester City|체스터 시티
York City|요크 시티
Torquay United|토키 유나이티드
Darlington|달링턴
Newport County|뉴포트 카운티
Southend United|사우스엔드 유나이티드
Wrexham|렉섬
Wycombe Wanderers|위컴 원더러스
Cheltenham Town|첼트넘 타운
Crawley Town|크롤리 타운
Fleetwood Town|플리트우드 타운
Accrington Stanley|애크링턴 스탠리
AFC Wimbledon|AFC 윔블던
Wimbledon|윔블던
Yeovil Town|요빌 타운
Dagenham & Redbridge|대거넘 앤드 레드브리지
Stevenage|스티버니지
Burton Albion|버턴 앨비언
Morecambe|모어컴
Forest Green Rovers|포리스트 그린 로버스
Harrogate Town|해러깃 타운
Salford City|솔퍼드 시티
Sutton United|서턴 유나이티드
Barrow|배로
Manchester City|맨체스터 시티
Manchester United|맨체스터 유나이티드
Man City|맨체스터 시티
Man United|맨체스터 유나이티드
Tottenham|토트넘 홋스퍼
Tottenham Hotspur|토트넘 홋스퍼
Chelsea|첼시
Arsenal|아스널
Liverpool|리버풀
Everton|에버턴
Newcastle United|뉴캐슬 유나이티드
Newcastle|뉴캐슬 유나이티드
Aston Villa|애스턴 빌라
Queens Park Rangers|퀸스 파크 레인저스
QPR|퀸스 파크 레인저스
Real Madrid|레알 마드리드
FC Barcelona|바르셀로나
Barcelona|바르셀로나
Espanyol Barcelona|에스파뇰
RCD Espanyol|에스파뇰
Atletico Madrid|아틀레티코 마드리드
Atlético Madrid|아틀레티코 마드리드
Atletico de Madrid|아틀레티코 마드리드
Real Valladolid|레알 바야돌리드
CA Osasuna|오사수나
Racing Santander|라싱 산탄데르
Getafe CF|헤타페
Levante UD|레반테
Malaga CF|말라가
Sporting Gijon|스포르팅 히혼
Sevilla FC|세비야
Villarreal CF|비야레알
Valencia CF|발렌시아
Athletic Bilbao|아틀레틱 빌바오
Athletic Club|아틀레틱 빌바오
Granada CF|그라나다
Rayo Vallecano|라요 바예카노
RCD Mallorca|마요르카
Real Sociedad|레알 소시에다드
Real Betis|레알 베티스
Real Zaragoza|레알 사라고사
Bayern München|바이에른 뮌헨
Bayern Munich|바이에른 뮌헨
Hamburger SV|함부르크
Hamburg|함부르크
Bayer Leverkusen|바이어 레버쿠젠
Bayer 04 Leverkusen|바이어 레버쿠젠
AC Milan|AC 밀란
Inter|인테르
Inter Milan|인테르
FC Internazionale|인테르
FC Internazionale Milano|인테르
Juventus|유벤투스
SSC Napoli|나폴리
AS Roma|AS 로마
SS Lazio|라치오
Lazio Rome|라치오
UC Sampdoria|삼프도리아
Genoa CFC|제노아
ACF Fiorentina|피오렌티나
Palermo|팔레르모
Parma FC|파르마
Parma Calcio 1913|파르마
Bologna FC|볼로냐
Chievo Verona|키에보 베로나
Hellas Verona|엘라스 베로나
US Lecce|레체
US Sassuolo|사수올로
Calcio Catania|카타니아
Novara Calcio|노바라
AC Cesena|체세나
Udinese Calcio|우디네세
AC Siena|시에나
Torino FC|토리노
Cagliari Calcio|칼리아리
Atalanta BC|아탈란타
Paris Saint-Germain|파리 생제르맹
Paris Saint-Germain FC|파리 생제르맹
Paris SG|파리 생제르맹
AJ Auxerre|오세르
AS Nancy|낭시
Stade Reims|스타드 드 랭스
Stade de Reims|스타드 드 랭스
Olympique Lyon|올랭피크 리옹
AS Saint-Etienne|생테티엔
Montpellier Herault|몽펠리에
PSV Eindhoven|PSV 에인트호번
AFC Ajax|아약스
Feyenoord|페예노르트
AZ Alkmaar|AZ 알크마르
Benfica|벤피카
SL Benfica|벤피카
Sporting CP|스포르팅
Sp Lisbon|스포르팅
FC Porto|포르투
Vitoria Guimaraes|비토리아 기마랑이스
Celtic|셀틱
Rangers|레인저스
Heart of Midlothian|하트 오브 미들로디언
Hearts|하트 오브 미들로디언
Hibernian|하이버니언
LAFC|로스앤젤레스 FC
Los Angeles FC|로스앤젤레스 FC
Inter Miami|인터 마이애미
Inter Miami CF|인터 마이애미
Without Club|무소속
Without club|무소속
Retired|은퇴
Career break|활동 중단
Unknown|미상
No club|무소속
End of loan|임대 종료'''
for line in text.splitlines():a,b=line.split('|',1);manual[a]=b
exact=dict(manual);teams={};byId={};countries={};countryCodes={}
for c in json.load(open(P/'countries-static.json')):
 ko=c.get('translations',{}).get('kor',{}).get('common')
 if not ko:continue
 for name in [c['name']['common'],c['name']['official'],*c.get('altSpellings',[])]:
  countries[name]=ko;countryCodes[name]=c['cca2'].lower()
countryExtra={'England':'잉글랜드','Scotland':'스코틀랜드','Wales':'웨일스','Northern Ireland':'북아일랜드','South Korea':'대한민국','Korea Republic':'대한민국','Korea, South':'대한민국','North Korea':'북한','Korea, North':'북한','West Germany':'서독','East Germany':'동독','Soviet Union':'소련','Yugoslavia':'유고슬라비아','Czechoslovakia':'체코슬로바키아','Serbia and Montenegro':'세르비아 몬테네그로','Bohemia':'보헤미아','Saarland':'자를란트','Zaire':'자이르','Burma':'버마','Ceylon':'실론','Swaziland':'스와질란드','Cape Verde':'카보베르데','Congo':'콩고 공화국','DR Congo':'콩고 민주공화국','Congo DR':'콩고 민주공화국','Ivory Coast':'코트디부아르','Cote d’Ivoire':'코트디부아르','Cote d\'Ivoire':'코트디부아르','Bosnia-Herzegovina':'보스니아 헤르체고비나','Chinese Taipei':'대만','USA':'미국','United States':'미국','Netherlands Antilles':'네덜란드령 안틸레스','Western Samoa':'서사모아','East Timor':'동티모르','Northern Cyprus':'북키프로스','Kosovo':'코소보','Eswatini':'에스와티니','Tibet':'티베트','Northern Mariana Islands':'북마리아나 제도','British Guiana':'영국령 기아나','French Guiana':'프랑스령 기아나','Kyrgyz Republic':'키르기스스탄','United Arab Emirates':'아랍에미리트'}
countries.update(countryExtra)
for name,code in {'South Korea':'kr','Korea Republic':'kr','Korea, South':'kr','North Korea':'kp','Korea, North':'kp','USA':'us','United States':'us','Ivory Coast':'ci','DR Congo':'cd','Congo DR':'cd','Congo':'cg','Cote d\'Ivoire':'ci','Cote d’Ivoire':'ci','Cape Verde':'cv','Eswatini':'sz','Bosnia-Herzegovina':'ba','Chinese Taipei':'tw'}.items():countryCodes[name]=code
for row in csv.DictReader(open(P/'korean-teams.json')):
 if row['name_en'] not in exact:exact[row['name_en']]=row['name_ko']
for r in json.load(open(P/'teams.json'))['results']['bindings']:
 id=r['id']['value'];ko=r['ko']['value'];en=r.get('en',{}).get('value','')
 if not re.search('[가-힣]',ko):continue
 byId[id]={'ko':ko,'id':id}
 if en:teams[norm(en)]={'ko':ko,'id':id}
clubs=json.load(open(O/'players/clubs.json'))
for id,c in clubs.items():
 rec=byId.get(id,{});raw=c['name'];ko=exact.get(raw) or next((v for k,v in manual.items() if norm(k)==norm(raw)),None) or rec.get('ko')
 if not ko:continue
 byId[id]={'id':id,'ko':ko};teams[norm(raw)]={'id':id,'ko':ko}
# Apply established display spellings consistently to aliases and IDs.
for en,ko in exact.items():
 k=norm(en);rec=teams.get(k,{})
 teams[k]={**rec,'ko':ko}
 if rec.get('id'):byId[rec['id']]['ko']=ko
for id,rec in byId.items():
 if id in clubs:teams[norm(clubs[id]['name'])]=rec
# Local current crests only. A missing crest is not replaced with another club's crest.
crests=json.load(open(P/'crest-manifest.json'))['crests']
for id,rec in byId.items():
 if id in crests:rec['crest']=crests[id]['file']
for rec in teams.values():
 if rec.get('id') in crests:rec['crest']=crests[rec['id']]['file']
players={}
for p in P.joinpath('batches').glob('*.json'):
 for r in json.load(open(p))['results']['bindings']:
  ko=r['label']['value']
  if re.search('[가-힣]',ko):players[r['id']['value']]=ko
idx=json.load(open(O/'players/index.json'))
for p in idx['players']:
 if p.get('alias'):players[p['id']]=p['alias']
person_labels=collections.defaultdict(set)
for p in idx['players']:
 if p['id'] in players:person_labels[p['name']].add(players[p['id']])
pnames={name:next(iter(labels)) for name,labels in person_labels.items() if len(labels)==1}
compText={'bundesliga':'분데스리가','2-bundesliga':'분데스리가 2부','premier-league':'프리미어리그','serie-a':'세리에 A','laliga':'라리가','ligue-1':'리그 1','eredivisie':'에레디비시','liga-portugal-bwin':'포르투갈 1부','super-lig':'쉬페르리그','scottish-premiership':'스코틀랜드 1부','jupiler-pro-league':'벨기에 1부','super-league-1':'그리스 1부','superligaen':'덴마크 1부','russian-premier-liga':'러시아 프리미어리그','premier-liga':'우크라이나 1부','uefa-champions-league':'UEFA 챔피언스리그','uefa-champions-league-qualifying':'챔피언스리그 예선','europa-league':'UEFA 유로파리그','europa-league-qualifying':'유로파리그 예선','uefa-europa-conference-league':'UEFA 컨퍼런스리그','conference-league':'UEFA 컨퍼런스리그','conference-league-qualifying':'컨퍼런스리그 예선','fa-cup':'FA컵','efl-cup':'리그컵','dfl-supercup':'독일 슈퍼컵','dfb-pokal':'DFB 포칼','copa-del-rey':'코파 델 레이','coppa-italia':'코파 이탈리아','coupe-de-france':'쿠프 드 프랑스','coupe-de-la-ligue':'프랑스 리그컵','fa-community-shield':'커뮤니티 실드','club-world-cup':'FIFA 클럽 월드컵','fifa-club-world-cup':'FIFA 클럽 월드컵','world-cup':'FIFA 월드컵','euros':'UEFA 유로','european-championship':'UEFA 유로','uefa-nations-league':'UEFA 네이션스리그','afc-asian-cup':'AFC 아시안컵','copa-america':'코파 아메리카','africa-cup-of-nations':'아프리카 네이션스컵','international-friendlies':'국가대표 친선경기'}
comps=json.load(open(O/'players/competitions.json'))
for code,c in comps.items():
 if c['name'] in compText:c['ko']=compText[c['name']]
for code,ko in json.load(open('scripts/korean-competition-names.json')).items():
 if code in comps:comps[code]['ko']=ko
# Explicitly known common aliases across season CSVs.
alias={'Man City':'Manchester City','Man United':'Manchester United','West Brom':'West Bromwich Albion','Wolves':'Wolverhampton Wanderers','Nott\'m Forest':'Nottingham Forest','Sp Lisbon':'Sporting CP','Bayern Munich':'Bayern München','Hamburg':'Hamburger SV','RCD Espanyol':'Espanyol Barcelona','Inter Milan':'FC Internazionale Milano','Inter':'FC Internazionale Milano','Paris SG':'Paris Saint-Germain','LAFC':'Los Angeles FC','SL Benfica':'Benfica'}
for en,target in alias.items():
 rec=teams.get(norm(target))
 if rec:teams[norm(en)]={**rec,'ko':exact.get(en,rec['ko'])}
(O/'localization.json').write_text(json.dumps(dict(version=1,exact=exact,teams=teams,teamIds=byId,countries=countries,countryCodes=countryCodes,players=players,playerNames=pnames,competitions=comps,crestPeriod='current',sources=['https://www.wikidata.org/wiki/Property:P2446','https://www.wikidata.org/wiki/Property:P7223','https://github.com/mledoze/countries','https://github.com/dwoony0909-tech/korean-football-team-names','https://tmssl.akamaized.net/images/wappen/head/']),ensure_ascii=False,separators=(',',':')))
print('Korean player names',len(players),'team labels',len(teams),'country labels',len(countries),'current crests',len(crests))
