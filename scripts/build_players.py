"""Compact public player catalogue and dated history. Never publish snapshot-current clubs or caps."""
import csv,json,collections,datetime,unicodedata
from pathlib import Path
P=Path('research/tm');O=Path('dist/replay/players');O.mkdir(parents=True,exist_ok=True)
SNAPSHOT='2026-07-06';SHARDS=512
players={};hist=collections.defaultdict(lambda:{'transfers':[],'appearances':[]});clubRows=list(csv.DictReader(open(P/'clubs')));clubs={r['club_id']:{'name':r['name'],'competition':r['domestic_competition_id']} for r in clubRows}
for r in csv.DictReader(open(P/'national_teams')):clubs[r['national_team_id']]={'name':r['name'],'competition':'INTERNATIONAL'}
comps={r['competition_id']:{'name':r['name'],'type':r['type'],'country':r['country_name']} for r in csv.DictReader(open(P/'competitions'))}
for r in csv.DictReader(open(P/'kaggle-players')):
 players[r['player_id']]={'id':r['player_id'],'name':r['name'],'country':r['country_of_citizenship'],'birth':r['date_of_birth'][:10],'position':r['position'],'detailPosition':r['sub_position'],'source':r['url']}
seen=set();discarded=0;transfers=0
for r in csv.DictReader(open(P/'kaggle-transfers')):
 date=r['transfer_date'][:10];pid=r['player_id']
 if not date or date>SNAPSHOT or date<'1956-01-01':discarded+=1;continue
 key=(pid,date,r['from_club_id'],r['to_club_id'])
 if key in seen:continue
 seen.add(key)
 if pid not in players:continue
 # transfer_fee=0 can encode missing/free/loan returns; no fee displayed without reliable transfer type.
 hist[pid]['transfers'].append([date,r['from_club_name'],r['to_club_name'],r['from_club_id'],r['to_club_id']]);transfers+=1
seen=set();appCount=0;maxApp='';bad=0
for r in csv.DictReader(open(P/'appearances')):
 pid=r['player_id'];date=r['date'][:10]
 if pid not in players or date>SNAPSHOT or date<'1956-01-01':continue
 if r['appearance_id'] in seen:continue
 seen.add(r['appearance_id'])
 try:vals=[int(float(r.get(k) or 0)) for k in ['minutes_played','goals','assists','yellow_cards','red_cards']]
 except ValueError:bad+=1;continue
 hist[pid]['appearances'].append([date,r['player_club_id'],r['competition_id'],*vals]);appCount+=1;maxApp=max(maxApp,date)
# Common Korean search aliases; raw source names remain visible.
aliasNames={'Ji-sung Park':'박지성','Heung-min Son':'손흥민','Min-jae Kim':'김민재','Kang-in Lee':'이강인','Hee-chan Hwang':'황희찬','Jae-sung Lee':'이재성','In-beom Hwang':'황인범','Sung-yong Ki':'기성용','Chung-yong Lee':'이청용','Young-pyo Lee':'이영표','Du-ri Cha':'차두리','Jung-hwan Ahn':'안정환','Jun-ho Bae':'배준호','Hyeon-seok Hong':'홍현석','Hyun-jun Yang':'양현준','Min-hyeok Yang':'양민혁','Woo-yeong Jeong':'정우영','Gue-sung Cho':'조규성','Seung-ho Paik':'백승호','Chang-hoon Kwon':'권창훈','Young-woo Seol':'설영우','Hyeon-gyu Oh':'오현규','Ui-jo Hwang':'황의조','Dong-gook Lee':'이동국','Dong-won Ji':'지동원','Chu-young Park':'박주영','Shinji Kagawa':'가가와 신지','Keisuke Honda':'혼다 게이스케','Takefusa Kubo':'구보 다케후사','Kaoru Mitoma':'미토마 가오루','Hidetoshi Nakata':'나카타 히데토시','Takumi Minamino':'미나미노 다쿠미','Cristiano Ronaldo':'크리스티아누 호날두','Lionel Messi':'리오넬 메시','Neymar':'네이마르','Kylian Mbappé':'킬리안 음바페','Erling Haaland':'엘링 홀란','Kevin De Bruyne':'케빈 더브라위너','Mohamed Salah':'모하메드 살라','Harry Kane':'해리 케인','Karim Benzema':'카림 벤제마','Luka Modrić':'루카 모드리치','Andrés Iniesta':'안드레스 이니에스타','Xavi':'차비','Zlatan Ibrahimović':'즐라탄 이브라히모비치','Wayne Rooney':'웨인 루니','Thierry Henry':'티에리 앙리','Luis Suárez':'루이스 수아레스','Robert Lewandowski':'로베르트 레반도프스키','Sergio Ramos':'세르히오 라모스','Manuel Neuer':'마누엘 노이어','Gareth Bale':'가레스 베일','Eden Hazard':'에덴 아자르','David Silva':'다비드 실바','Fernando Torres':'페르난도 토레스','Steven Gerrard':'스티븐 제라드','Frank Lampard':'프랭크 램퍼드','Miroslav Klose':'미로슬라프 클로제','Mesut Özil':'메수트 외질','Thomas Müller':'토마스 뮐러','Toni Kroos':'토니 크로스','Sergio Agüero':'세르히오 아구에로','Didier Drogba':'디디에 드로그바','Samuel Eto’o':'사무엘 에토','Ronaldinho':'호나우지뉴','David Beckham':'데이비드 베컴','Paul Scholes':'폴 스콜스','Ryan Giggs':'라이언 긱스','Gianluigi Buffon':'잔루이지 부폰','Francesco Totti':'프란체스코 토티','Andrea Pirlo':'안드레아 피를로'}
shards=collections.defaultdict(dict);index=[];withHistory=0;withTransfers=0;withApps=0
for pid,p in players.items():
 h=hist[pid];h['transfers'].sort(key=lambda x:(x[0],x[1],x[2]));h['appearances'].sort(key=lambda x:(x[0],x[1],x[2]));dates=[x[0] for x in h['transfers']]+[x[0] for x in h['appearances']];first=min(dates) if dates else '';last=max(dates) if dates else ''
 if dates:withHistory+=1
 if h['transfers']:withTransfers+=1
 if h['appearances']:withApps+=1
 p['alias']=aliasNames.get(p['name'],'');p['first']=first;p['last']=last;p['shard']=int(pid)%SHARDS
 shards[p['shard']][pid]=dict(**p,**h);index.append({k:p[k] for k in ['id','name','alias','country','position','birth','first','last','shard']})
for shard,data in shards.items():(O/f'part-{shard:03}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
index.sort(key=lambda x:x['name'].casefold())
meta={'snapshot':SNAPSHOT,'appearanceThrough':maxApp,'playerCount':len(index),'withHistory':withHistory,'withTransfers':withTransfers,'withAppearances':withApps,'transferCount':transfers,'appearanceCount':appCount,'excludedFutureTransfers':discarded,'source':'https://github.com/dcaribou/transfermarkt-datasets','downloadSource':'https://www.kaggle.com/datasets/davidcariboo/player-scores','license':'CC0-1.0','shards':SHARDS,'note':'주로 2012년 이후 경기 출전과 1993년 이후 이적 기록의 현대 축구 자료입니다. 모든 시대·국가·선수의 전체 커리어를 보장하지 않습니다. 최신 소속·총 국가대표 출전·최고 시장가치 등의 스냅샷 값은 과거 화면에 사용하지 않습니다. 이적료 0은 무료 계약과 미상 등을 구분하지 못해 표시하지 않습니다.'}
(O/'index.json').write_text(json.dumps({'meta':meta,'players':index},ensure_ascii=False,separators=(',',':')))
(O/'competitions.json').write_text(json.dumps(comps,ensure_ascii=False,separators=(',',':')))
(O/'clubs.json').write_text(json.dumps(clubs,ensure_ascii=False,separators=(',',':')))
(O/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')))
print(json.dumps(meta,ensure_ascii=False));print('Normalized MB',round(sum(p.stat().st_size for p in O.glob('*.json'))/1e6,1))
