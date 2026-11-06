"""Join the CC BY-SA Fjelstul World Cup data without confusing squads and starts."""
import collections,csv,datetime,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/expansion/worldcup';OUT=ROOT/'dist/replay/match-archive';SOURCE='https://github.com/jfjelstul/worldcup'
def rows(name):return list(csv.DictReader((P/(name+'.csv')).open()))
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).replace('westgermany','germanyfr')
def name(r):return ' '.join(x for x in [r.get('given_name',''),r.get('family_name','')] if x and x!='not applicable')
def num(x):return int(float(x or 0))
def stamp(r):
    a=num(r['minute_regulation']);b=num(r['minute_stoppage']);return str(a)+(('+'+str(b)) if b else '')
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
matches={r['match_id']:r for r in rows('matches') if "Men's" in r['tournament_name'] and r['match_date']>='1956-01-01'}
goals=collections.defaultdict(list);notes=collections.defaultdict(list);lineups=collections.defaultdict(list);squads=collections.defaultdict(list);apps=collections.defaultdict(list)
for r in rows('goals'):
    if r['match_id'] not in matches:continue
    goals[r['match_id']].append({'minute':stamp(r),'team':r['team_name'],'scorer':name(r),'own':num(r['own_goal'])==1,'penalty':num(r['penalty'])==1})
for r in rows('bookings'):
    if r['match_id'] not in matches:continue
    notes[r['match_id']].append({'minute':stamp(r),'team':r['team_name'],'player':name(r),'kind':'red' if num(r['sending_off']) else 'yellow'})
subs=collections.defaultdict(list)
for r in rows('substitutions'):
    if r['match_id'] not in matches:continue
    subs[(r['match_id'],r['team_name'],stamp(r))].append(r)
for (mid,team,time),rs in subs.items():
    outgoing=[r for r in rs if num(r['going_off'])];incoming=[r for r in rs if num(r['coming_on'])]
    # Two simultaneous substitutions do not establish the individual pairing.
    if len(outgoing)==len(incoming)==1:notes[mid].append({'minute':time,'team':team,'kind':'sub','player':name(outgoing[0]),'incoming':name(incoming[0])})
for r in rows('player_appearances'):
    if r['match_id'] not in matches:continue
    lineups[r['match_id']].append({'playerId':'worldcup-'+r['player_id'],'name':name(r),'team':r['team_name'],'teamId':r['team_id'],'role':'starting_lineup' if num(r['starter']) else 'substitutes','position':r['position_name'],'number':str(num(r['shirt_number']))})
    apps[r['player_id']].append({'date':r['match_date'],'team':r['team_name'],'tournament':r['tournament_name'],'starter':num(r['starter'])==1,'source':SOURCE})
firstTeamDate={}
for r in matches.values():
    for team in [r['home_team_name'],r['away_team_name']]:firstTeamDate[(r['tournament_id'],team)]=min(firstTeamDate.get((r['tournament_id'],team),'9999'),r['match_date'])
for r in rows('squads'):
    k=(r['tournament_id'],r['team_name'])
    if k not in firstTeamDate:continue
    squads[k].append({'playerId':'worldcup-'+r['player_id'],'name':name(r),'team':r['team_name'],'teamId':r['team_id'],'role':'tournament_squad','position':r['position_name'],'number':str(num(r['shirt_number']))})
lookup={(r['match_date'],norm(r['home_team_name']),norm(r['away_team_name'])):r for r in matches.values()};updated=0;lineupGames=0;squadGames=0
for path in OUT.glob('[12][0-9][0-9][0-9]-[01][0-9].json'):
    d=json.loads(path.read_text());changed=False
    for m in d['matches']:
        r=lookup.get((m['date'],norm(m['home']),norm(m['away'])))
        if not r or (m['hg'],m['ag'])!=(num(r['home_team_score']),num(r['away_team_score'])):continue
        mid=r['match_id'];canonical={norm(m['home']):m['home'],norm(m['away']):m['away']}
        gs=[{**g,'team':canonical.get(norm(g['team']),g['team'])} for g in goals[mid]]
        if len(gs)==m['hg']+m['ag'] and not m.get('featured'):
            m['goals']=gs;m['eventNotes']=[{**e,'team':canonical.get(norm(e['team']),e['team'])} for e in notes[mid]];m['eventPrecision']='added-time-preserved';m['extraTime']=num(r['extra_time'])==1;m['duration']=120 if m['extraTime'] else 90;m['replayLevel']='events';m['source']=SOURCE
        m['sourceLicense']='CC-BY-SA-4.0';m['venue']=r['stadium_name'];m['kickoffLocal']=r['match_time'];m['kickoffTimeBasis']='venue local clock; timezone conversion not reconstructed'
        if num(r['penalty_shootout']):m['pens']=[num(r['home_team_score_penalties']),num(r['away_team_score_penalties'])]
        if lineups[mid]:m['lineups']=[{**p,'team':canonical.get(norm(p['team']),p['team'])} for p in lineups[mid]];lineupGames+=1
        else:m['tournamentSquads']=[{**p,'team':canonical.get(norm(p['team']),p['team'])} for t in [r['home_team_name'],r['away_team_name']] for p in squads[(r['tournament_id'],t)]];squadGames+=1
        if SOURCE not in m['sources']:m['sources'].append(SOURCE)
        updated+=1;changed=True
    if changed:dump(path,d)
classic=ROOT/'data/classic-player-profiles.json';profiles=json.loads(classic.read_text());tmIndex=json.loads((ROOT/'dist/replay/players/index.json').read_text())
known={(norm(p['name']),p.get('birth','')) for p in tmIndex['players']+profiles['players']}
wcPlayers={r['player_id']:r for r in rows('players') if num(r['female'])==0 and r['birth_date']<'1970-01-01'};reg=collections.defaultdict(list)
for r in rows('squads'):
    k=(r['tournament_id'],r['team_name'])
    if k in firstTeamDate:reg[r['player_id']].append({'date':firstTeamDate[k],'tournament':r['tournament_name'],'team':r['team_name'],'number':str(num(r['shirt_number'])),'position':r['position_name'],'source':SOURCE})
added=0
for pid,r in wcPlayers.items():
    full=name(r);birth=r['birth_date'];entries=reg[pid]
    if not entries or (norm(full),birth) in known:continue
    position='Goalkeeper' if num(r['goal_keeper']) else 'Defender' if num(r['defender']) else 'Midfield' if num(r['midfielder']) else 'Attack' if num(r['forward']) else ''
    p={'id':'historic-worldcup-'+pid,'name':full,'alias':'','birth':birth,'birthYear':birth[:4],'country':entries[0]['team'],'position':position,'source':r['player_wikipedia_link'] if r['player_wikipedia_link'].startswith('http') else SOURCE,'sourceKind':'worldcup-history','license':'CC-BY-SA-4.0','historyPeriods':[],'tournamentEntries':entries,'matchRecords':apps[pid],'transfers':[],'appearances':[],'first':min(e['date'] for e in entries),'last':max(e['date'] for e in entries)}
    profiles['players'].append(p);known.add((norm(full),birth));added+=1
profiles['meta']['worldCupSupplement']=sum(p.get('sourceKind')=='worldcup-history' for p in profiles['players']);profiles['meta']['worldCupSource']=SOURCE;profiles['meta']['players']=len(profiles['players']);dump(classic,profiles)
dump(OUT/'worldcup-squads.json',{'source':SOURCE,'license':'CC-BY-SA-4.0','dateBasis':'first match of team; actual squad-announcement day not asserted','teams':[{'tournament':k[0],'team':k[1],'visibleFrom':firstTeamDate[k],'players':v} for k,v in squads.items()]})
# Update every derived count after enrichment, using the actual stored records.
index=json.loads((OUT/'index.json').read_text());seasonCounts=collections.defaultdict(lambda:[0,0]);totalEvents=0;allLineups=0;lineupEntries=0;days=collections.defaultdict(lambda:[0,0]);sourceCounts=collections.Counter()
for month,meta in index['months'].items():
    p=ROOT/'dist/replay'/meta['file'];d=json.loads(p.read_text());meta['bytes']=p.stat().st_size
    for m in d['matches']:
        if m['replayLevel']=='events' and not (m.get('goals') or m.get('eventNotes') or m.get('notes')):m['replayLevel']='result'
        seasonCounts[str(m['season'])][0]+=1;seasonCounts[str(m['season'])][1]+=m['replayLevel']=='events';totalEvents+=m['replayLevel']=='events';allLineups+=bool(m.get('lineups'));lineupEntries+=len(m.get('lineups',[]))
        days[m['date']][0]+=1;days[m['date']][1]+=m['replayLevel']=='events'
        if m['replayLevel']=='events':sourceCounts[m['source'].split('/')[2]]+=1
    dump(p,d);meta['bytes']=p.stat().st_size
for year,meta in index['seasons'].items():
    meta['events']=seasonCounts[year][1];meta['resultOnly']=meta['count']-meta['events'];meta['below100Events']=meta['events']<100
    p=ROOT/'dist/replay'/meta['file'];d=json.loads(p.read_text());levels={m['id']:m['replayLevel'] for month,mi in index['months'].items() if int(month[:4]) in [int(year),int(year)+1] for m in json.loads((ROOT/'dist/replay'/mi['file']).read_text())['matches']}
    for m in d['matches']:m['replayLevel']=levels[m['id']]
    dump(p,d)
index.update(eventMatches=totalEvents,resultOnlyMatches=index['matches']-totalEvents,lineupGames=allLineups,lineupEntries=lineupEntries,worldCupSquadGames=squadGames,days=dict(sorted(days.items())),sourceCounts=dict(sourceCounts));dump(OUT/'index.json',index)
quality=json.loads((OUT/'quality.json').read_text());quality['seasonEventGaps']={y:v for y,v in index['seasons'].items() if v['completeSeason'] and v['events']<100};quality['worldCupEnrichment']={'games':updated,'lineupGames':lineupGames,'registeredSquadGames':squadGames,'source':SOURCE,'license':'CC-BY-SA-4.0'};dump(OUT/'quality.json',quality)
print('World Cup games enriched',updated,'lineups',lineupGames,'squads',squadGames,'classic profiles added',added,'all classic profiles',len(profiles['players']))
