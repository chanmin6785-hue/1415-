"""Build a dated major-match archive; never invent an event or its minute.

Sources remain separate until team, date and score reconciliation succeeds.
Shoot-out kicks are excluded from the playing score. Missing event coverage
produces a result record, never a synthetic minute-by-minute commentary.
"""
import collections,csv,datetime,hashlib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist/replay/match-archive';OUT.mkdir(exist_ok=True)
RAW=ROOT/'research/expansion';LEGACY=ROOT/'../..'/'sites/football-atlas/research';CUTOFF='2026-10-31'
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
locale=read(ROOT/'dist/replay/localization.json')
ALIASES={'manutd':'manchesterunited','manunited':'manchesterunited','manchestercityfc':'manchestercity','qpr':'queensparkrangers','bayer04leverkusen':'bayerleverkusen','internazionale':'inter','intermilan':'inter','internazionalemilano':'inter','psg':'parissaintgermain','parisstgermain':'parissaintgermain','acmilan':'milan','athleticbilbao':'athleticclub','espanyolbarcelona':'espanyol','deportivolacoruna':'deportivolacoruna','bayernmunich':'bayernmunchen','realsociedadsansebastian':'realsociedad','borussiamonchengladbach':'borussiamonchengladbach','westgermany':'germanyfr','sovietunion':'ussr','korearepublic':'southkorea','koreasouth':'southkorea','cotedivoire':'ivorycoast'}
def norm(name):
    s=unicodedata.normalize('NFKD',str(name)).lower();s=''.join(c for c in s if not unicodedata.combining(c));s=unicodedata.normalize('NFC',s);s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|bk|club|calcio|football|societa|sportiva|sad|spa|srl)\b','',s);s=re.sub(r'[^a-z0-9가-힣]','',s);return ALIASES.get(s,s)
def key(date,home,away):return (date,norm(home),norm(away))
def season(date):return int(date[:4])-(int(date[5:7])<7)
def minute(s):
    if not re.fullmatch(r'(?:[1-9]\d?|1[01]\d|120)(?:\+\d{1,2})?',str(s)):return None
    a=str(s).split('+');return int(a[0])+(int(a[1])*.01 if len(a)>1 else 0)
records={};conflicts=[];counts=collections.Counter();sources=collections.Counter()
def add(m,origin,league=''):
    if not '1956-01-01'<=m.get('date','')<=CUTOFF or not m.get('home') or not m.get('away'):return None
    k=key(m['date'],m['home'],m['away'])
    if k in records:
        old=records[k]
        if (old['hg'],old['ag'])!=(m['hg'],m['ag']):conflicts.append({'kind':'score-conflict','date':m['date'],'home':m['home'],'away':m['away'],'origin':origin});return old
        for field in ['stage','competition','venue','pens','shootoutWinner','cupId']:
            if m.get(field) and not old.get(field):old[field]=m[field]
        if league:old['league']=league
        return old
    rec={**m,'origin':origin,'sources':[origin]}
    if league:rec['league']=league
    records[k]=rec;return rec
manifest=read(ROOT/'dist/replay/manifest.json')
for lid,info in manifest['leagues'].items():
    for s in info['seasons']:
        data=read(ROOT/'dist/replay'/s['file'])
        for m in data['matches']:add({**m,'competition':info['name'],'leagueSeason':data['season']},data.get('source') or info.get('source') or 'https://www.football-data.co.uk/data.php',lid)
for cid,info in manifest['cups'].items():
    d=read(ROOT/'dist/replay'/info['file'])
    for m in d['matches']:add({**m,'competition':d['name'],'cupId':cid},d.get('source') or 'https://github.com/openfootball')
for p in sorted((ROOT/'dist/replay/international').glob('*.json')):
    for m in read(p)['matches']:add(m,'https://github.com/martj42/international_results')
print('Match registry',len(records),flush=True)
def complete(m,goals):
    return len(goals)==m['hg']+m['ag'] and all(minute(g.get('minute')) is not None for g in goals) and sum(g['team']==m['home'] for g in goals)==m['hg'] and sum(g['team']==m['away'] for g in goals)==m['ag']
def attach(m,goals,source,precision='minute'):
    if not m or not complete(m,goals):return False
    if m.get('verifiedGoals') and m.get('eventPrecision')=='added-time-preserved' and precision!='added-time-preserved':return True
    m['goals']=sorted(goals,key=lambda g:minute(g['minute']));m['verifiedGoals']=True;m['source']=source;m['eventPrecision']=precision
    if source not in m['sources']:m['sources'].append(source)
    return True
# Broaden international coverage beyond just the World Cup and Euros.
gpath=RAW/'international-goals.csv'
if not gpath.exists():gpath=LEGACY/'goalscorers.csv'
if gpath.exists():
    grouped=collections.defaultdict(list)
    for r in csv.DictReader(gpath.open()):
        grouped[key(r['date'],r['home_team'],r['away_team'])].append(r)
    for k,rs in grouped.items():
        m=records.get(k)
        if not m:continue
        goals=[{'minute':r['minute'],'team':m['home'] if norm(r['team'])==norm(m['home']) else m['away'],'scorer':r['scorer'],'own':r['own_goal']=='TRUE','penalty':r['penalty']=='TRUE'} for r in rs]
        if attach(m,goals,'https://github.com/martj42/international_results','source-minute'):counts['internationalGoalGames']+=1
# Published goal logs have running score columns, allowing own goals and
# duplicate rows to be checked without guessing which team benefited.
leagueMap={'eng-premier-league':'england','bundesliga':'germany','fra-ligue-1':'france','esp-primera-division':'spain','ita-serie-a':'italy','por-primeira-liga':'portugal','ned-eredivisie':'holland','sco-premiership':'scotland','bel-pro-league':'belgium','tur-sueperlig':'turkey','gre-super-league':'greece','aut-bundesliga':'austria','nor-eliteserien':'norway','pol-ekstraklasa':'poland','sui-super-league':'switzerland'}
for path in sorted((RAW/'schochastics').glob('*.csv')):
    grouped=collections.defaultdict(list)
    for r in csv.DictReader(path.open()):grouped[(r['date'],r['game'])].append(r)
    for (date,label),rs in grouped.items():
        match=re.fullmatch(r'(.*?) vs\. (.*?) (\d+):(\d+)(?:\s.*)?',label)
        if not match:counts['unparsedGoalLabels']+=1;continue
        home,away=match[1],match[2];m=records.get(key(date,home,away))
        if not m:m=add({'date':date,'home':home,'away':away,'hg':int(match[3]),'ag':int(match[4]),'competition':path.stem},'https://github.com/schochastics/football-data',leagueMap.get(path.stem,''))
        if not m:continue
        if not m.get('league') and path.stem in leagueMap:m['league']=leagueMap[path.stem]
        unique={(r['scoring_player'],r['time'],r['GH'],r['GA']):r for r in rs}
        try:ordered=sorted(unique.values(),key=lambda r:(int(r['GH'])+int(r['GA']),int(r['GH'])))
        except ValueError:continue
        goals=[];last=(0,0);valid=True
        for r in ordered:
            now=(int(r['GH']),int(r['GA']));delta=(now[0]-last[0],now[1]-last[1]);last=now
            if delta not in [(1,0),(0,1)] or minute(r['time']) is None:valid=False;break
            goals.append({'minute':r['time'],'team':m['home'] if delta[0] else m['away'],'scorer':r['scoring_player'],'own':bool(re.search(r'own|o\.g\.',r['scoring_player'],re.I)),'penalty':bool(re.search(r'penalty|\(pen\)',r['scoring_player'],re.I))})
        if valid and attach(m,goals,'https://github.com/schochastics/football-data/blob/master/data/goals_time/'+path.name,'added-time-preserved'):counts['historicalGoalGames']+=1
    print('Goal source',path.stem,flush=True)
# The Transfermarkt mirror includes shoot-out goals in game totals. Reconcile
# against existing match scores or subtract explicitly recorded scored kicks.
tm={};tmMap={};clubData=read(ROOT/'dist/replay/players/clubs.json');compData=read(ROOT/'dist/replay/players/competitions.json')
for r in csv.DictReader((RAW/'games.download').open()):
    date=r['date'][:10]
    if not '1956-01-01'<=date<=CUTOFF:continue
    tm[r['game_id']]=r
events=collections.defaultdict(list)
for r in csv.DictReader((RAW/'game_events.download').open()):
    if r['game_id'] in tm:events[r['game_id']].append(r)
players={}
playerInput=RAW/'player-names.csv'
if not playerInput.exists():playerInput=LEGACY/'tm/kaggle-players'
for r in csv.DictReader(playerInput.open()):players[r['player_id']]=r['name']
for gid,r in tm.items():
    home=r['home_club_name'] or clubData.get(r['home_club_id'],{}).get('name','');away=r['away_club_name'] or clubData.get(r['away_club_id'],{}).get('name','')
    if not home or not away:continue
    penalties=[sum(e['type']=='Shootout' and e['club_id']==cid and 'scored' in e['description'].lower() for e in events[gid]) for cid in [r['home_club_id'],r['away_club_id']]]
    shootout=any(e['type']=='Shootout' for e in events[gid]);hg=int(r['home_club_goals']);ag=int(r['away_club_goals'])
    m=records.get(key(r['date'],home,away))
    if not m:
        hg-=penalties[0];ag-=penalties[1]
        if min(hg,ag)<0:counts['invalidShootoutTotals']+=1;continue
        m=add({'date':r['date'],'home':home,'away':away,'hg':hg,'ag':ag,'competition':compData.get(r['competition_id'],{}).get('name',r['competition_id']),'stage':r['round']},r['url'])
    if not m:continue
    m['gameId']=gid;m['homeId']=r['home_club_id'];m['awayId']=r['away_club_id'];m['venue']=r['stadium']
    m['managers']=[r['home_club_manager_name'],r['away_club_manager_name']]
    if shootout and not m.get('pens'):m['pens']=penalties
    goalRows=[e for e in events[gid] if e['type']=='Goals'];goals=[]
    for e in goalRows:
        if e['club_id'] not in [r['home_club_id'],r['away_club_id']]:continue
        goals.append({'minute':e['minute'],'team':m['home'] if e['club_id']==r['home_club_id'] else m['away'],'scorer':players.get(e['player_id'],'선수 이름 미수록'),'playerId':e['player_id'],'own':'own-goal' in e['description'].lower(),'penalty':'penalty' in e['description'].lower()})
    if attach(m,goals,r['url'],'source-minute-without-added-time-separator'):
        notes=[]
        for e in events[gid]:
            if minute(e['minute']) is None:continue
            team=m['home'] if e['club_id']==r['home_club_id'] else m['away'];name=players.get(e['player_id'],'선수 이름 미수록');desc=e['description'].lower()
            if e['type']=='Cards':
                kind='red' if 'red' in desc or 'second yellow' in desc or '2. yellow' in desc else 'yellow' if 'yellow' in desc else 'card'
                notes.append({'minute':e['minute'],'kind':kind,'team':team,'player':name,'playerId':e['player_id']})
            if e['type']=='Substitutions' and e['player_in_id']:
                notes.append({'minute':e['minute'],'kind':'sub','team':team,'player':name,'incoming':players.get(e['player_in_id'],'선수 이름 미수록'),'playerId':e['player_id'],'incomingId':e['player_in_id']})
        m['eventNotes']=notes;counts['transfermarktEventGames']+=1
    else:counts['rejectedTransfermarktEventGames']+=1
    tmMap[gid]=m
print('Reconciled source events',dict(counts),flush=True)
events.clear();tm.clear();tmMap.clear()
# Hand-checked detailed games retain their original exact added-time markers.
for f in read(ROOT/'dist/replay/stories.json')['features']:
    m=records.get(key(f['date'],f['home'],f['away'])) or add(f,f['source'])
    if m:m.update(f,verifiedGoals=True,eventPrecision='hand-checked-added-time',featured=True)
BIG={norm(s) for s in ['Manchester United','Manchester City','Liverpool','Arsenal','Chelsea','Tottenham Hotspur','Everton','Newcastle United','Real Madrid','Barcelona','Atletico Madrid','Athletic Bilbao','Valencia','Sevilla','AC Milan','Inter','Juventus','Napoli','Roma','Lazio','Fiorentina','Bayern Munich','Borussia Dortmund','Hamburger SV','Werder Bremen','Schalke 04','Borussia Monchengladbach','Saint-Etienne','Olympique Marseille','Olympique Lyon','Paris Saint-Germain','Girondins Bordeaux','Monaco','Benfica','FC Porto','Sporting CP','Ajax','PSV Eindhoven','Feyenoord','Celtic','Rangers']}
MAJOR_INTL=re.compile(r'World Cup|UEFA Euro|Copa Am[eé]rica|Asian Cup|Africa Cup|African Cup|Gold Cup|Nations League|Confederations Cup',re.I)
endDates={}
for m in records.values():
    if m.get('league'):endDates[(m['league'],m.get('leagueSeason',season(m['date'])))]=max(endDates.get((m['league'],m.get('leagueSeason',season(m['date']))),''),m['date'])
selected=[]
for m in records.values():
    reasons=[];score=0;h=norm(m['home']);a=norm(m['away']);comp=m.get('competition','');stage=m.get('stage','')
    if m.get('featured'):reasons.append('별도 검증 역사 경기');score+=100
    if m.get('cupId','').startswith(('wc-','euro-','ucl-')):reasons.append('월드컵·유로·유럽 클럽 대회');score+=60
    if re.search(r'final|quarter|semi|round of 16|last 16',stage,re.I) and not re.search('qualif',comp,re.I):reasons.append('컵 토너먼트');score+=70
    if MAJOR_INTL.search(comp) and not m.get('league'):reasons.append('주요 국가대표 대회');score+=60
    if (h=='southkorea' or a=='southkorea') and not m.get('league'):reasons.append('대한민국 국가대표');score+=70
    if m.get('league') and (h in BIG or a in BIG):reasons.append('주요 구단 경기');score+=35
    if m.get('league') in ['england','spain','italy','germany','france']:
        end=endDates.get((m['league'],m.get('leagueSeason',season(m['date']))))
        if end and (datetime.date.fromisoformat(end)-datetime.date.fromisoformat(m['date'])).days<=42:reasons.append('시즌 막판 리그 경기');score+=40
    if h in BIG and a in BIG:reasons.append('주요 구단 맞대결');score+=40
    if not reasons:continue
    rec={k:v for k,v in m.items() if k not in ['origin','verifiedGoals']}
    rec['id']='ma-'+hashlib.sha1('|'.join(key(m['date'],m['home'],m['away'])).encode()).hexdigest()[:16];rec['reasons']=reasons;rec['importance']=score
    rec['replayLevel']='events' if m.get('verifiedGoals') and (m.get('goals') or m.get('eventNotes') or m.get('notes')) else 'result';rec['source']=m.get('source') or m['sources'][0]
    if rec['replayLevel']=='result':rec.pop('goals',None);rec.pop('eventNotes',None)
    else:sources[rec['source'].split('/')[2]]+=1
    selected.append(rec)
selectedIds={r.get('gameId'):r for r in selected if r.get('gameId')};lineups=collections.defaultdict(list)
for r in csv.DictReader((RAW/'game_lineups.download').open()):
    if r['game_id'] not in selectedIds or r['type'] not in ['starting_lineup','substitutes']:continue
    lineups[r['game_id']].append({'playerId':r['player_id'],'name':r['player_name'],'teamId':r['club_id'],'role':r['type'],'position':r['position'],'number':r['number'],'captain':r['team_captain']=='1'})
for r in selected:
    if lineups.get(r.get('gameId')):
        ls=list({(p['teamId'],p['playerId'],p['role']):p for p in lineups[r['gameId']]}.values());r['lineups']=ls
byMonth=collections.defaultdict(list);bySeason=collections.defaultdict(list);days=collections.defaultdict(lambda:[0,0]);quality=collections.Counter()
for r in selected:
    r['season']=season(r['date']);byMonth[r['date'][:7]].append(r)
    brief={k:r[k] for k in ['id','date','home','away','competition','replayLevel','importance','reasons']};bySeason[r['season']].append(brief)
    days[r['date']][0]+=1;days[r['date']][1]+=r['replayLevel']=='events';quality[r['replayLevel']]+=1
months={};seasons={}
for month,rs in sorted(byMonth.items()):
    rs.sort(key=lambda r:(r['date'],-r['importance'],r['id']));p=OUT/(month+'.json');dump(p,{'month':month,'matches':rs});months[month]={'file':'match-archive/'+p.name,'count':len(rs),'bytes':p.stat().st_size}
for year,rs in sorted(bySeason.items()):
    rs.sort(key=lambda r:(r['date'],-r['importance'],r['id']));p=OUT/f'season-{year}.json';dump(p,{'season':year,'matches':rs});n=sum(r['replayLevel']=='events' for r in rs);seasons[str(year)]={'file':'match-archive/'+p.name,'count':len(rs),'events':n,'resultOnly':len(rs)-n,'completeSeason':1956<=year<=2025,'below100Events':n<100}
meta={'cutoff':CUTOFF,'matches':len(selected),'eventMatches':quality['events'],'resultOnlyMatches':quality['result'],'lineupGames':len(lineups),'lineupEntries':sum(len(r.get('lineups',[])) for r in selected),'seasons':seasons,'months':months,'days':dict(sorted(days.items())),'sourceCounts':dict(sources),'notes':['Season means July through June; 1955/56 and 2026/27 are partial.','All qualifying major matches are included; no quota padding or invented incidents.','Result-only records are explicitly not minute commentary.','Some source minute columns omit the added-time separator; original reported minute retained.','A shoot-out is excluded from the playing score.']}
dump(OUT/'index.json',meta);dump(OUT/'quality.json',{'counts':dict(counts),'conflictCount':len(conflicts),'conflicts':conflicts[:100],'seasonEventGaps':{y:v for y,v in seasons.items() if v['completeSeason'] and v['events']<100},'checks':['score and goal-team reconciliation','positive source minutes','shoot-out separation','no synthetic events','original source attribution','lineup roles retained']})
print(json.dumps({k:v for k,v in meta.items() if k not in ['seasons','months','days','notes']},ensure_ascii=False),flush=True)
