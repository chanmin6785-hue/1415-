"""Reconcile UEFA's official typed scorer/lineup records with the replay archive."""
import collections,datetime,gzip,hashlib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/expansion/uefa';OUT=ROOT/'dist/replay/match-archive'
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
ALIASES={'manunited':'manchesterunited','manutd':'manchesterunited','bayern':'bayernmunchen','bayernmunich':'bayernmunchen','internazionale':'inter','internazionalemilano':'inter','intermilan':'inter','westgermany':'germany','germanyfr':'germany','germandemocraticrepublic':'eastgermany','germanydr':'eastgermany','ussr':'sovietunion','czechrepublic':'czechia','korearepublic':'southkorea','koreasouth':'southkorea','crvenazvezda':'redstarbelgrade','redstar':'redstarbelgrade','psv':'psveindhoven','bayer04leverkusen':'bayerleverkusen','athleticbilbao':'athleticclub','dynamokyiv':'dinamokiev','dynamokiev':'dinamokiev','dinamokyiv':'dinamokiev','sportingcp':'sportinglisbon','sporting':'sportinglisbon','olympiacos':'olympiakos','parisstgermain':'parissaintgermain','psg':'parissaintgermain','anderlecht':'rscanderlecht','mgladbach':'borussiamonchengladbach','monchengladbach':'borussiamonchengladbach'}
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).lower();s=''.join(c for c in s if not unicodedata.combining(c));s=unicodedata.normalize('NFC',s);s=re.sub(r'\b(fc|cf|afc|ac|as|ss|ssc|sc|sv|fk|bk|club|calcio|football|societa|sportiva|sad|spa|srl)\b','',s);s=re.sub(r'[^a-z0-9가-힣]','',s);return ALIASES.get(s,s)
def season(d):return int(d[:4])-(int(d[5:7])<7)
def stamp(e):
    t=e.get('time',{});minute=t.get('minute');extra=t.get('injuryMinute')
    if minute is None or not 0<int(minute)<=120:return None
    return str(minute)+(('+'+str(extra)) if extra else '')
def teamName(t):return t.get('translations',{}).get('displayOfficialName',{}).get('EN') or t.get('internationalName','')
def key(d,h,a):return (d,norm(h),norm(a))
months={};allRecords=[]
for path in sorted(OUT.glob('[12][0-9][0-9][0-9]-[01][0-9].json')):
    d=read(path);months[d['month']]=d['matches'];allRecords.extend(d['matches'])
lookup={key(m['date'],m['home'],m['away']):m for m in allRecords};byDate=collections.defaultdict(list)
for m in allRecords:byDate[m['date']].append(m)
raw=json.loads(gzip.decompress((P/'matches.json.gz').read_bytes()));unavailable=[];matched=0;added=0;goalUpdates=0;aliasProofs=[];sourceProfiles={}
BIG_NATIONS={norm(n) for n in ['England','France','Germany','West Germany','Italy','Spain','Netherlands','Portugal','Hungary','Sweden','Yugoslavia','Soviet Union','Brazil','Argentina','Uruguay','South Korea','Japan']}
for r in raw:
    date=r['kickOffTime']['date'];h=r['homeTeam'];a=r['awayTeam'];home=teamName(h);away=teamName(a);comp=str(r['competition']['id']);score=r.get('score',{}).get('total') or r.get('score',{}).get('regular')
    if not score or not home or not away:continue
    hg,ag=score.get('home'),score.get('away')
    if not isinstance(hg,int) or not isinstance(ag,int):continue
    namesH={norm(home),norm(h.get('internationalName',''))};namesA={norm(away),norm(a.get('internationalName',''))};m=None;reverse=False
    for mh in namesH:
        for ma in namesA:
            for k,rev in [((date,mh,ma),False),((date,ma,mh),True)]:
                candidate=lookup.get(k)
                if candidate and (candidate['hg'],candidate['ag'])==((ag,hg) if rev else (hg,ag)):m=candidate;reverse=rev;break
            if m:break
        if m:break
    if not m:
        # Resolve a spelling difference only with one identified team, matching
        # date/score and exactly one candidate in the same competition family.
        candidates=[]
        for x in byDate[date]:
            if comp=='1' and not x.get('cupId','').startswith('ucl-'):continue
            if comp in ['3','17','19'] and x.get('league'):continue
            if norm(x['home']) in namesH and (x['hg'],x['ag'])==(hg,ag):candidates.append((x,False))
            elif norm(x['away']) in namesH and (x['hg'],x['ag'])==(ag,hg):candidates.append((x,True))
            elif norm(x['away']) in namesA and (x['hg'],x['ag'])==(hg,ag):candidates.append((x,False))
            elif norm(x['home']) in namesA and (x['hg'],x['ag'])==(ag,hg):candidates.append((x,True))
        unique={x['id']:(x,rev) for x,rev in candidates}
        if len(unique)==1:
            m,reverse=next(iter(unique.values()));aliasProofs.append({'date':date,'uefaMatch':r['id'],'uefa':[home,away],'archive':[m['home'],m['away']]})
    if not m:
        if comp=='19' and not (namesH|namesA)&BIG_NATIONS:continue
        competition=r['competition'].get('metaData',{}).get('name') or r['competition'].get('translations',{}).get('name',{}).get('EN','UEFA')
        m={'id':'ma-uefa-'+r['id'],'date':date,'home':home,'away':away,'hg':hg,'ag':ag,'competition':competition,'stage':r.get('round',{}).get('translations',{}).get('name',{}).get('EN',''),'season':season(date),'importance':65 if comp!='19' else 40,'reasons':['UEFA 공식 유럽대회' if comp!='19' else '주요 국가대표 친선경기'],'replayLevel':'result','sources':[]}
        months.setdefault(date[:7],[]).append(m);allRecords.append(m);lookup[key(date,home,away)]=m;byDate[date].append(m);added+=1
    else:matched+=1
    canonical={str(h['id']):m['away'] if reverse else m['home'],str(a['id']):m['home'] if reverse else m['away']}
    url='https://www.uefa.com/uefachampionsleague/match/'+r['id']+'/' if comp=='1' else 'https://match.uefa.com/v5/matches?matchId='+r['id']
    m.setdefault('source',url);m['uefaMatchId']=r['id'];m['uefaCompetitionId']=comp;m['kickoffUtc']=r['kickOffTime'].get('dateTime');m['utcOffsetInHours']=r['kickOffTime'].get('utcOffsetInHours');m['kickoffTimeBasis']='UEFA supplied UTC timestamp and venue offset'
    penaltyScore=r.get('score',{}).get('penalty')
    if penaltyScore and all(isinstance(penaltyScore.get(k),int) for k in ['home','away']):m['pens']=[penaltyScore['away'],penaltyScore['home']] if reverse else [penaltyScore['home'],penaltyScore['away']]
    m['venue']=r.get('stadium',{}).get('translations',{}).get('name',{}).get('EN') or m.get('venue','')
    goals=[];notes=[];valid=True
    for g in r.get('playerEvents',{}).get('scorers',[]):
        time=stamp(g);team=canonical.get(str(g.get('teamId','')))
        if not time or not team:valid=False;break
        goals.append({'minute':time,'team':team,'scorer':g.get('player',{}).get('internationalName') or '득점자 미확인','own':g.get('goalType') in ['OWN','OWN_GOAL'],'penalty':g.get('goalType') in ['PENALTY','PENALTY_GOAL']})
    for e in r.get('playerEvents',{}).get('redCards',[]):
        time=stamp(e);team=canonical.get(str(e.get('teamId','')))
        if time and team:notes.append({'minute':time,'team':team,'kind':'red','player':e.get('player',{}).get('internationalName') or '선수 이름 미수록'})
    regularCounts=(sum(g['team']==m['home'] for g in goals),sum(g['team']==m['away'] for g in goals))
    if valid and regularCounts==(m['hg'],m['ag']) and (goals or notes) and not m.get('featured'):
        m.update(goals=goals,eventNotes=notes,eventPrecision='official-added-time-preserved',replayLevel='events',source=url);goalUpdates+=1
    elif not valid or regularCounts!=(m['hg'],m['ag']):unavailable.append({'matchId':r['id'],'reason':'Incomplete or conflicting source scorer minute/team totals'})
    reason=r.get('winner',{}).get('match',{}).get('reason','')
    if reason=='WIN_BY_FORFEIT':m['administrativeResult']=True
    if 'EXTRA' in reason or any('EXTRA' in g.get('phase','') for g in r.get('playerEvents',{}).get('scorers',[])):m['extraTime']=True;m['duration']=120
    if url not in m['sources']:m['sources'].append(url)
    lp=P/('lineup-'+r['id']+'.json.gz')
    if lp.exists():
        data=json.loads(gzip.decompress(lp.read_bytes()));lineups=[]
        for side,team in [('homeTeam',canonical[str(h['id'])]),('awayTeam',canonical[str(a['id'])])]:
            block=data.get(side,{})
            for kind,role in [('field','starting_lineup'),('bench','substitutes')]:
                for row in block.get(kind,[]):
                    player=row.get('player',{});pname=player.get('internationalName','');pid=player.get('id','')
                    if not pname or not pid:continue
                    item={'name':pname,'team':team,'playerId':'uefa-'+pid,'role':role,'number':str(row.get('jerseyNumber','')),'position':player.get('fieldPosition',''),'captain':row.get('captain',False)};lineups.append(item)
                    birth=player.get('birthDate','')
                    if (birth and birth<'1970-01-01') or date<'1970-01-01':
                        p=sourceProfiles.setdefault(pid,{'id':'historic-uefa-'+pid,'name':pname,'birth':birth if re.fullmatch(r'\d{4}-\d{2}-\d{2}',birth) else '','country':player.get('translations',{}).get('countryName',{}).get('EN',''),'position':player.get('fieldPosition',''),'matches':[]})
                        p['matches'].append({'date':date,'team':team,'starter':role=='starting_lineup','role':role,'source':url,'matchId':r['id']})
        if lineups:m['lineups']=lineups;m['lineupSource']='https://match.uefa.com/v5/matches/'+r['id']+'/lineups'
        m['lineupCoverage']='UEFA published match lineup; no current player age or photograph included'
# Publish normalized monthly records and complete, independently reconciled counts.
oldIndex=read(OUT/'index.json');bySeason=collections.defaultdict(list);days=collections.defaultdict(lambda:[0,0]);mi={};sourceCounts=collections.Counter();lineupGames=0;lineupCount=0;eventCount=0
for month,rs in sorted(months.items()):
    unique={x['id']:x for x in rs};rs=sorted(unique.values(),key=lambda x:(x['date'],-x['importance'],x['id']));path=OUT/(month+'.json');dump(path,{'month':month,'matches':rs});mi[month]={'file':'match-archive/'+path.name,'count':len(rs),'bytes':path.stat().st_size}
    for m in rs:
        bySeason[str(m['season'])].append({k:m[k] for k in ['id','date','home','away','competition','replayLevel','importance','reasons']});days[m['date']][0]+=1;days[m['date']][1]+=m['replayLevel']=='events';eventCount+=m['replayLevel']=='events';lineupGames+=bool(m.get('lineups'));lineupCount+=len(m.get('lineups',[]))
        if m['replayLevel']=='events':sourceCounts[m['source'].split('/')[2]]+=1
seasons={}
for year,rs in sorted(bySeason.items()):
    rs.sort(key=lambda x:(x['date'],-x['importance'],x['id']));p=OUT/f'season-{year}.json';dump(p,{'season':int(year),'matches':rs});n=sum(x['replayLevel']=='events' for x in rs);seasons[year]={'file':'match-archive/'+p.name,'count':len(rs),'events':n,'resultOnly':len(rs)-n,'completeSeason':1956<=int(year)<=2025,'below100Events':n<100}
oldIndex.update(matches=sum(x['count'] for x in mi.values()),eventMatches=eventCount,resultOnlyMatches=sum(x['count'] for x in mi.values())-eventCount,lineupGames=lineupGames,lineupEntries=lineupCount,seasons=seasons,months=mi,days=dict(sorted(days.items())),sourceCounts=dict(sourceCounts),officialUefaMatches=matched+added);dump(OUT/'index.json',oldIndex)
q=read(OUT/'quality.json');q['uefa']={'matched':matched,'added':added,'goalUpdates':goalUpdates,'source':'https://match.uefa.com/v5/matches','excludedScorerRecords':unavailable,'aliasReconciliation':aliasProofs};q['seasonEventGaps']={y:v for y,v in seasons.items() if v['completeSeason'] and v['events']<100};dump(OUT/'quality.json',q)
# Supplement older profiles with confirmed dated match appearances, not guessed
# transfer dates. Deduplicate by complete name and birth date when available.
pp=ROOT/'data/classic-player-profiles.json';data=read(pp);people=data['players'];existing={(norm(p['name']),p.get('birth','')):p for p in people};modern={(norm(p['name']),p.get('birth','')) for p in read(ROOT/'dist/replay/players/index.json')['players']};newProfiles=0
for pid,p in sourceProfiles.items():
    k=(norm(p['name']),p['birth']);profile=existing.get(k)
    if k in modern and not profile:continue
    if not profile:
        profile={'id':p['id'],'name':p['name'],'alias':'','birth':p['birth'],'birthYear':p['birth'][:4],'country':p['country'],'position':{'GOALKEEPER':'Goalkeeper','DEFENDER':'Defender','MIDFIELDER':'Midfield','FORWARD':'Attack'}.get(p['position'],''),'historyPeriods':[],'transfers':[],'appearances':[],'matchRecords':[],'sourceKind':'uefa-history','source':p['matches'][0]['source'],'license':'Factual match lineup metadata; UEFA attribution retained'};people.append(profile);existing[k]=profile;newProfiles+=1
    records=[x for x in profile.get('matchRecords',[]) if 'match.uefa.com' not in x.get('source','') and 'uefachampionsleague/match/' not in x.get('source','')];records.extend(x for x in p['matches'] if x['starter']);profile['benchRecords']=sorted([x for x in p['matches'] if not x['starter']],key=lambda x:x['date']);profile['matchRecords']=sorted({(x['date'],x['team'],x.get('matchId','')):x for x in records}.values(),key=lambda x:(x['date'],x['team']));starts=[x['date'] for x in profile['matchRecords']+profile.get('benchRecords',[])]+[r['visibleFrom'] for r in profile.get('historyPeriods',[])]+[e['date'] for e in profile.get('tournamentEntries',[])];profile['first']=min(starts);profile['last']=max(starts)
data['meta'].update(license='Mixed sources: per-profile and per-component attribution applies',selection='Classic profiles from Wikidata candidate selection, World Cup registrations and dated UEFA lineups',players=len(people),uefaLineupProfileSupplement=sum(p.get('sourceKind')=='uefa-history' for p in people));dump(pp,data)
print('UEFA enriched',matched,'added',added,'verified goal updates',goalUpdates,'new classic profiles',newProfiles,'remaining complete-season event gaps',list(q['seasonEventGaps']),flush=True)
