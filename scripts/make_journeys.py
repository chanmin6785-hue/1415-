import json
from pathlib import Path
profiles=[]
def player(id,name,country,wiki,stages):
 out=[]
 for year,club,league,aliases,*rest in stages:
  exact=rest[0] if rest else None
  out.append(dict(year=year,date=exact or str(year)+'-12-31',club=club,league=league,aliases=aliases,precision='day' if exact else 'year'))
 profiles.append(dict(id=id,name=name,country=country,source='https://en.wikipedia.org/wiki/'+wiki,stages=out))
player('park','박지성','South Korea','Park_Ji-sung',[(2000,'교토 퍼플 상가','japan',['Kyoto Sanga','Kyoto']),(2003,'PSV 에인트호번','holland',['PSV Eindhoven']),(2005,'맨체스터 유나이티드','england',['Manchester United'],'2005-07-08'),(2012,'퀸스 파크 레인저스','england',['Queens Park Rangers']),(2013,'PSV 에인트호번 · 임대','holland',['PSV Eindhoven'])])
player('son','손흥민','South Korea','Son_Heung-min',[(2010,'함부르크','germany',['Hamburger SV','Hamburg']),(2013,'바이어 레버쿠젠','germany',['Bayer Leverkusen','Bayer 04 Leverkusen']),(2015,'토트넘 홋스퍼','england',['Tottenham Hotspur'],'2015-08-28'),(2025,'LAFC','usa',['Los Angeles FC','Los Angeles'],'2025-08-06')])
player('cruyff','요한 크라위프','Netherlands','Johan_Cruyff',[(1964,'아약스','holland',['AFC Ajax']),(1973,'바르셀로나','spain',['FC Barcelona']),(1979,'로스앤젤레스 아즈텍스','usa',['Los Angeles Aztecs']),(1980,'워싱턴 디플로매츠','usa',['Washington Diplomats']),(1981,'레반테','spain',['Levante UD']),(1981,'워싱턴 디플로매츠','usa',['Washington Diplomats']),(1981,'아약스 복귀','holland',['AFC Ajax']),(1983,'페예노르트','holland',['Feyenoord'])])
player('ronaldo','호나우두','Brazil','Ronaldo_(Brazilian_footballer)',[(1993,'크루제이루','brazil',['Cruzeiro']),(1994,'PSV 에인트호번','holland',['PSV Eindhoven']),(1996,'바르셀로나','spain',['FC Barcelona']),(1997,'인테르','italy',['FC Internazionale']),(2002,'레알 마드리드','spain',['Real Madrid CF']),(2007,'AC 밀란','italy',['AC Milan']),(2009,'코린치앙스','brazil',['Corinthians'])])
player('cristiano','크리스티아누 호날두','Portugal','Cristiano_Ronaldo',[(2002,'스포르팅','portugal',['Sp Lisbon','Sporting CP']),(2003,'맨체스터 유나이티드','england',['Manchester United']),(2009,'레알 마드리드','spain',['Real Madrid CF'],'2009-07-01'),(2018,'유벤투스','italy',['Juventus']),(2021,'맨체스터 유나이티드 복귀','england',['Manchester United']),(2023,'알나스르','saudi',['Al Nassr'])])
player('maradona','디에고 마라도나','Argentina','Diego_Maradona',[(1976,'아르헨티노스 주니어스','argentina',['Argentinos Juniors']),(1981,'보카 주니어스','argentina',['Boca Juniors']),(1982,'바르셀로나','spain',['FC Barcelona']),(1984,'나폴리','italy',['SSC Napoli']),(1992,'세비야','spain',['Sevilla FC']),(1993,'뉴얼스 올드 보이스','argentina',['Newells Old Boys']),(1995,'보카 주니어스 복귀','argentina',['Boca Juniors'])])
player('messi','리오넬 메시','Argentina','Lionel_Messi',[(2000,'바르셀로나 유스','spain',['FC Barcelona']),(2003,'바르셀로나 C','spain',['FC Barcelona C']),(2004,'바르셀로나 B','spain',['FC Barcelona B']),(2004,'바르셀로나 1군','spain',['FC Barcelona']),(2021,'파리 생제르맹','france',['Paris Saint-Germain','Paris SG'],'2021-08-10'),(2023,'인터 마이애미','usa',['Inter Miami'],'2023-07-15')])
player('neymar','네이마르','Brazil','Neymar',[(2009,'산투스','brazil',['Santos']),(2013,'바르셀로나','spain',['FC Barcelona']),(2017,'파리 생제르맹','france',['Paris Saint-Germain','Paris SG'],'2017-08-03'),(2023,'알힐랄','saudi',['Al Hilal']),(2025,'산투스 복귀','brazil',['Santos'])])
player('gullit','뤼트 굴리트','Netherlands','Ruud_Gullit',[(1979,'하를럼','holland',['HFC Haarlem']),(1982,'페예노르트','holland',['Feyenoord']),(1985,'PSV 에인트호번','holland',['PSV Eindhoven']),(1987,'AC 밀란','italy',['AC Milan']),(1993,'삼프도리아 · 임대','italy',['UC Sampdoria']),(1994,'AC 밀란 복귀','italy',['AC Milan']),(1994,'삼프도리아','italy',['UC Sampdoria']),(1995,'첼시','england',['Chelsea'])])
player('eusebio','에우제비우','Portugal','Eus%C3%A9bio',[(1957,'스포르팅 로렌수마르케스','mozambique',['Sporting de Lourenco Marques']),(1961,'벤피카','portugal',['Benfica']),(1975,'보스턴 미닛맨','usa',['Boston Minutemen']),(1975,'몬테레이','mexico',['Monterrey']),(1976,'토론토 메트로스-크로아티아','usa',['Toronto Metros-Croatia']),(1976,'베이라마르','portugal',['Beira Mar']),(1977,'라스베이거스 퀵실버스','usa',['Las Vegas Quicksilvers']),(1977,'우니앙 드 토마르','portugal',['Uniao de Tomar']),(1978,'뉴저지 아메리칸스','usa',['New Jersey Americans'])])
player('pele','펠레','Brazil','Pel%C3%A9',[(1956,'산투스','brazil',['Santos']),(1975,'뉴욕 코스모스','nasl',['New York Cosmos'])])
player('puskas','페렌츠 푸스카스','Hungary','Ferenc_Pusk%C3%A1s',[(1943,'키슈페슈트 / 부다페스트 혼베드','hungary',['Budapest Honved']),(1958,'레알 마드리드','spain',['Real Madrid CF'])])
player('distefano','알프레도 디 스테파노','Spain','Alfredo_Di_St%C3%A9fano',[(1945,'리버 플레이트','argentina',['River Plate']),(1946,'우라칸 · 임대','argentina',['Huracan']),(1947,'리버 플레이트 복귀','argentina',['River Plate']),(1949,'미요나리오스','colombia',['Millonarios']),(1953,'레알 마드리드','spain',['Real Madrid CF']),(1964,'에스파뇰','spain',['RCD Espanyol'])])
player('beckenbauer','프란츠 베켄바워','Germany','Franz_Beckenbauer',[(1964,'바이에른 뮌헨','germany',['Bayern Munich','Bayern München']),(1977,'뉴욕 코스모스','nasl',['New York Cosmos']),(1980,'함부르크','germany',['Hamburger SV','Hamburg']),(1983,'뉴욕 코스모스 복귀','nasl',['New York Cosmos'])])
player('matthews','스탠리 매슈스','England','Stanley_Matthews',[(1932,'스토크 시티','england',['Stoke City']),(1947,'블랙풀','england',['Blackpool']),(1961,'스토크 시티 복귀','england-2',['Stoke City'])])
player('yashin','레프 야신','Soviet Union','Lev_Yashin',[(1950,'디나모 모스크바','soviet',['Dynamo Moscow'])])
player('zidane','지네딘 지단','France','Zinedine_Zidane',[(1989,'칸','france',['AS Cannes']),(1992,'보르도','france',['Girondins de Bordeaux']),(1996,'유벤투스','italy',['Juventus']),(2001,'레알 마드리드','spain',['Real Madrid CF'])])
player('cha','차범근','South Korea','Cha_Bum-kun',[(1978,'다름슈타트 98','germany',['SV Darmstadt 98']),(1979,'아인트라흐트 프랑크푸르트','germany',['Eintracht Frankfurt']),(1983,'바이어 레버쿠젠','germany',['Bayer Leverkusen','Bayer 04 Leverkusen'])])
for item in profiles:
 if item['id'] in ['cha','matthews']:item['partial']=True

# Entries record the first confirmed year at a club, not exact transfer days.
# Year-only entries are conservatively revealed on December 31 to avoid exposing a later-in-year move early.
Path('dist/replay/journeys.json').write_text(json.dumps(dict(players=profiles,note='소속 경력의 연도 기준 요약입니다. 이적일이 확인되지 않은 항목은 해당 연도 말 이후에 공개합니다. 한 해에 여러 소속이 있는 경우 정확한 월·일 순서는 별도 미수록입니다.'),ensure_ascii=False,separators=(',',':')))
print(len(profiles),'player journeys')
