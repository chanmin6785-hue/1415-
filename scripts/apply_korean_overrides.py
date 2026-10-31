import json,collections,re,unicodedata
from pathlib import Path
p=Path('dist/replay/localization.json');L=json.load(open(p))
def norm(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c));s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|club|football|calcio|societa|sportiva|spa|sad|srl)\b',' ',s);return re.sub(r'[^a-z0-9가-힣]','',s)
rows='''Chester|체스터 시티
Lazio Roma|라치오
Bor. Monchengladbach|보루시아 묀헨글라트바흐
Stade Rennes|스타드 렌
Stade Rennais FC|스타드 렌
FC Sochaux|소쇼
FC Sochaux-Montbeliard|소쇼
RC Strasbourg|스트라스부르
RC Strasbourg Alsace|스트라스부르
Aldershot|올더숏
Aldershot Town|올더숏 타운
Hereford United|헤리퍼드 유나이티드
Vitesse|피테서
Vitesse Arnhem|피테서
MVV|MVV 마스트리흐트
Cheltenham|첼트넘 타운
Sp Braga|브라가
SC Braga|브라가
Guimaraes|비토리아 기마랑이스
Vitoria SC|비토리아 기마랑이스
Gent|헨트
KAA Gent|헨트
Standard|스탕다르 리에주
Standard Liege|스탕다르 리에주
Olympiakos|올림피아코스
Olympiacos|올림피아코스
Barnet|바닛
Charleroi|샤를루아
RSC Charleroi|샤를루아
Milton Keynes Dons|밀턴킨스 던스
MK Dons|밀턴킨스 던스
Maritimo|마리티무
AEK|AEK 아테네
AEK Athens|AEK 아테네
Stuttgarter Kickers|슈투트가르터 키커스
Genclerbirligi|겐츨레르비를리이
Southport|사우스포트
St Truiden|신트트라위던
Sint-Truiden|신트트라위던
Sint-Truidense VV|신트트라위던
SG Wattenscheid 09|바텐샤이트 09
Accrington|애크링턴 스탠리
Workington|워킹턴
US Valenciennes-Anzin|발랑시엔
Valenciennes FC|발랑시엔
Aris|아리스
Aris Thessaloniki|아리스
OFI|OFI 크레타
OFI Crete|OFI 크레타
SBV Excelsior|엑셀시오르
Excelsior|엑셀시오르
Xanthi|크산티
Hansa Rostock|한자 로스토크
Belenenses|벨레넨스
Ankaragucu|앙카라귀쥐
Rot-Weiss Oberhausen|로트바이스 오버하우젠
Panionios|파니오니오스
Macclesfield|매클즈필드 타운
Macclesfield Town|매클즈필드 타운
Mechelen|메헬렌
KV Mechelen|메헬렌
Kickers Offenbach|키커스 오펜바흐
Setubal|비토리아 세투발
Vitoria Setubal|비토리아 세투발
Westerlo|베스테를로
Lokeren|로케런
Yeovil|요빌 타운
Espanyol Barcelona|에스파뇰
RCD Espanyol Barcelona|에스파뇰
AS Nancy-Lorraine|낭시
1. FC Kaiserslautern|카이저슬라우테른
Anderlecht|안더레흐트
RSC Anderlecht|안더레흐트
Genk|헹크
KRC Genk|헹크
Almere City|알메러 시티
FC Volendam|폴렌담
FC Emmen|에먼
RKC Waalwijk|RKC 발베이크
Willem II|빌럼 II
De Graafschap|더 흐라프스합
VVV Venlo|VVV 펜로
VVV-Venlo|VVV 펜로
NEC Nijmegen|NEC 네이메헌
PEC Zwolle|PEC 즈볼러
Go Ahead Eagles|고 어헤드 이글스
Fortuna Sittard|포르튀나 시타르트
Roda JC|로다 JC
Sparta Rotterdam|스파르타 로테르담
FC Twente|트벤터
FC Utrecht|위트레흐트
FC Groningen|흐로닝언
SC Heerenveen|헤이렌베인
SC Cambuur|캄뷔르
Cambuur Leeuwarden|캄뷔르
NEC|NEC 네이메헌
NAC Breda|NAC 브레다
Beerschot|베이르스홋
Beerschot VA|베이르스홋
Lierse|리르서
Eupen|외펜
Waasland-Beveren|바슬란트 베베런
Cercle Brugge|세르클러 브뤼허
Club Brugge|클뤼프 브뤼허
Club Brugge KV|클뤼프 브뤼허
Antwerp|로열 앤트워프
Royal Antwerp|로열 앤트워프
Oostende|오스텐더
Mouscron|무스크롱
Dender|덴더
Kortrijk|코르트레이크
Waregem|바레험
Zulte-Waregem|쥘터 바레험
Farense|파렌스
Estoril|에스토릴
Pacos Ferreira|파수스 드 페헤이라
Paços de Ferreira|파수스 드 페헤이라
Gil Vicente|질 비센트
Boavista|보아비스타
Rio Ave|히우 아브
Nacional|나시오날
Nacional Funchal|나시오날
Moreirense|모레이렌스
Arouca|아로카
Portimonense|포르티모넨스
Santa Clara|산타 클라라
Famalicao|파말리캉
Tondela|톤델라
Chaves|샤브스
Leixoes|레이숑이스
Naval|나발
Penafiel|페나피엘
Feirense|페이렌스
Uniao Leiria|우니앙 레이리아
Academica|아카데미카
Ergotelis|에르고텔리스
Levadeiakos|레바디아코스
Panetolikos|파네톨리코스
Asteras Tripolis|아스테라스 트리폴리스
Atromitos|아트로미토스
PAS Giannina|PAS 야니나
Larisa|라리사
AE Larisa|라리사
Panthrakikos|판트라키코스
Apollon|아폴론
Ionikos|이오니코스
PAOK|PAOK
Iraklis|이라클리스
Kallithea|칼리테아
OFI Crete FC|OFI 크레타
Dunfermline|던펌린
Dundee|던디
Dundee United|던디 유나이티드
Kilmarnock|킬마녹
St Mirren|세인트 미렌
St Johnstone|세인트 존스턴
Motherwell|머더웰
Hamilton|해밀턴
Partick|파틱 시슬
Partick Thistle|파틱 시슬
Falkirk|폴커크
Ross County|로스 카운티
Inverness C|인버네스
Inverness CT|인버네스
Livingston|리빙스턴
Gretna|그레트나
Dumbarton|덤바턴
Cape Town|케이프타운
Santos|산투스
Cruzeiro|크루제이루
Corinthians|코린치앙스
Flamengo|플라멩구
Fluminense|플루미넨시
Botafogo|보타포구
Vasco da Gama|바스쿠 다 가마
Sao Paulo|상파울루
Palmeiras|파우메이라스
Gremio|그레미우
Internacional|인테르나시오나우
Athletico-PR|아틀레치쿠 파라나엔시
Atletico-MG|아틀레치쿠 미네이루
Boca Juniors|보카 주니어스
River Plate|리버 플레이트
Racing Club|라싱 클루브
Independiente|인데펜디엔테
San Lorenzo|산로렌소
Newells Old Boys|뉴얼스 올드 보이스
Velez Sarsfield|벨레스 사르스필드
Estudiantes|에스투디안테스
Argentinos Juniors|아르헨티노스 주니어스
Bayer 04 Leverkusen|바이어 레버쿠젠
Bayer Leverkusen|바이어 레버쿠젠
Tottenham Hotspur|토트넘 홋스퍼
Tottenham|토트넘 홋스퍼
Gamba Osaka|감바 오사카
Vissel Kobe|비셀 고베
Kyoto Sanga|교토 상가
Urawa Reds|우라와 레즈
Yokohama F. Marinos|요코하마 F. 마리노스
Yokohama Marinos|요코하마 F. 마리노스
Kashima Antlers|가시마 앤틀러스
Kashiwa Reysol|가시와 레이솔
Shimizu S-Pulse|시미즈 S펄스
Kawasaki Frontale|가와사키 프론탈레
Sanfrecce Hiroshima|산프레체 히로시마
Sapporo|콘사돌레 삿포로
Cerezo Osaka|세레소 오사카
Nagoya Grampus|나고야 그램퍼스
Avispa Fukuoka|아비스파 후쿠오카
Vegalta Sendai|베갈타 센다이
Albirex Niigata|알비렉스 니가타
Jubilo Iwata|주빌로 이와타
Sagan Tosu|사간 도스
Omiya Ardija|오미야 아르디자
Tokyo|FC 도쿄
FC Tokyo|FC 도쿄
Shonan Bellmare|쇼난 벨마레
Ventforet Kofu|방포레 고후'''
overrides={}
for row in rows.splitlines():en,ko=row.split('|',1);overrides[en]=ko;L['exact'][en]=ko;key=norm(en);L['teams'].setdefault(key,{})['ko']=ko
# Standardize IDs and all aliases with the same Korean display name only when the ID is unambiguous.
groups=collections.defaultdict(list)
for key,r in L['teams'].items():
 if r.get('ko'):groups[r['ko']].append(r)
for ko,rs in groups.items():
 ids={r['id'] for r in rs if r.get('id')};assets={r['crest'] for r in rs if r.get('crest')}
 if len(ids)==1:
  id=next(iter(ids));base=L['teamIds'].get(id,{})
  if base:base['ko']=ko
  for r in rs:r.setdefault('id',id);r.update({k:v for k,v in base.items() if k=='crest'})
 elif len(assets)==1:
  for r in rs:r.setdefault('crest',next(iter(assets)))
L['stats']={'koreanPlayerNames':len(L['players']),'crestAssets':len(list(Path('dist/assets/crests').glob('*'))),'koreanTeamSpellings':len(L['teams'])}
p.write_text(json.dumps(L,ensure_ascii=False,separators=(',',':')))
Path('dist/replay/korean-name-overrides.json').write_text(json.dumps(overrides,ensure_ascii=False,separators=(',',':')))
print('Additional Korean spellings:',len(overrides))
