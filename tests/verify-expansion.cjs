'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'../dist'),read=f=>JSON.parse(fs.readFileSync(path.join(root,'replay',f))),E=require('../dist/engine.js');
E.configureRules(read('standings-rules.json'));
const adjustments=(date,closed=[])=>E.adjustmentsFor('england',2023,date,closed).filter(r=>r.team==='Everton').reduce((s,r)=>s+r.points,0);
assert.equal(adjustments('2023-11-17'),0);assert.equal(adjustments('2023-11-17',['2023-11-17']),-10);
assert.equal(adjustments('2024-02-27'),-6);assert.equal(adjustments('2024-04-09'),-8,'Independent sanction must add to revised first case');
assert.equal(E.adjustmentsFor('italy',2022,'2023-04-21').filter(r=>r.team==='Juventus').reduce((s,r)=>s+r.points,0),0);
assert.equal(E.adjustmentsFor('italy',2022,'2023-05-23').filter(r=>r.team==='Juventus').reduce((s,r)=>s+r.points,0),-10);
const game=(date,home,away,hg,ag)=>({date,home,away,hg,ag});
const kr=E.table([game('2016-09-29','서울','전북',0,1),game('2016-09-29','울산','전남',2,1)],{league:'korea',season:2016,date:'2016-10-01'});assert.equal(kr.find(r=>r.name==='전북').adjustment,-9);assert(kr.filter(r=>r.name!=='전북').every(r=>r.adjustment===0),'Jeonbuk sanction applied to a different Hangul team');
let rows=E.table([game('1973-08-01','A','B',3,3)],{league:'france',season:1973});assert(rows.every(r=>r.pts===2),'Three-goal bonus applied to both teams');
rows=E.table([game('1974-08-01','A','B',3,2)],{league:'france',season:1974});assert.equal(rows.find(r=>r.name==='A').pts,2,'1974 bonus requires three-goal winning margin');
rows=E.table([game('1974-08-01','A','B',3,0)],{league:'france',season:1974});assert.equal(rows.find(r=>r.name==='A').pts,3);
rows=E.table([game('2024-01-01','A','B',0,0)]);assert(rows.every(r=>r.rank===1&&r.tieUnresolved));
rows=E.table([game('2024-01-01','A','B',1,0),game('2024-02-01','B','A',2,0)],{league:'spain',season:2023,date:'2024-01-15'});assert(rows.every(r=>!r.headToHeadReady));
const index=read('match-archive/index.json'),ids=new Set(),days={},seasons={},sources={};let count=0,events=0,lineupGames=0,lineupEntries=0;
for(const [month,meta] of Object.entries(index.months)){
 const file=path.join(root,'replay',meta.file),data=JSON.parse(fs.readFileSync(file));assert.equal(fs.statSync(file).size,meta.bytes);assert.equal(data.matches.length,meta.count);assert.equal(data.month,month);
 for(const m of data.matches){
  assert(!ids.has(m.id),'Duplicate archive ID '+m.id);ids.add(m.id);assert.equal(m.date.slice(0,7),month);assert(m.date>='1956-01-01'&&m.date<=index.cutoff);assert(m.home&&m.away);assert(Number.isInteger(m.hg)&&Number.isInteger(m.ag));
  (days[m.date]??=[0,0])[0]++;const year=String(+m.date.slice(0,4)-(+m.date.slice(5,7)<7));assert.equal(String(m.season),year);(seasons[year]??=[0,0])[0]++;
  if(m.replayLevel==='events'){
   events++;days[m.date][1]++;seasons[year][1]++;assert.match(m.source,/^https?:\/\//);
   assert.equal((m.goals||[]).filter(g=>g.team===m.home).length,m.hg,m.id+' home score');assert.equal((m.goals||[]).filter(g=>g.team===m.away).length,m.ag,m.id+' away score');
   assert((m.goals||[]).length||(m.eventNotes||[]).length||(m.notes||[]).length,'An empty synthetic replay');
   for(const g of [...(m.goals||[]),...(m.eventNotes||[])]){assert.match(String(g.minute),/^(?:[1-9]\d?|1[01]\d|120)(?:\+\d{1,2})?$/);assert([m.home,m.away].includes(g.team));assert(!('second' in g),'Historical placeholder seconds must never be exported');}
  }else assert.equal(m.replayLevel,'result');
  if(m.lineups?.length){lineupGames++;lineupEntries+=m.lineups.length;for(const p of m.lineups){assert(['starting_lineup','substitutes'].includes(p.role));assert([m.home,m.away].includes(p.team)||(p.teamId!==undefined&&[m.homeId,m.awayId].map(String).includes(String(p.teamId))));}}
  if(m.shootout){assert.deepEqual([m.home,m.away].map(team=>m.shootout.filter(k=>k.team===team&&k.outcome==='scored').length),m.pens);for(const k of m.shootout){assert(!('minute' in k));assert(['scored','saved','missed'].includes(k.outcome));}}
  count++;
 }
}
assert.equal(count,index.matches);assert.equal(events,index.eventMatches);assert.equal(count-events,index.resultOnlyMatches);assert.equal(lineupGames,index.lineupGames);assert.equal(lineupEntries,index.lineupEntries);assert.deepEqual(days,index.days);
for(const [year,meta] of Object.entries(index.seasons)){assert.deepEqual(seasons[year],[meta.count,meta.events]);assert.equal(meta.count-meta.events,meta.resultOnly);const brief=read(meta.file);assert.equal(brief.matches.length,meta.count);for(const m of brief.matches)assert(!('hg' in m||'ag' in m||'goals' in m),'Season catalogue contains results');if(meta.completeSeason)assert(meta.events>100,year+' needs more than 100 actual-event games');}
const final=read('match-archive/2022-12.json').matches.find(m=>m.date==='2022-12-18'&&/Argentina/.test(m.home)&&/France/.test(m.away));assert(final);assert.equal(final.hg,3);assert.equal(final.ag,3);assert.equal(final.goals.length,6,'Shootout successes counted as football goals');
const early=read('match-archive/1956-06.json').matches.find(m=>m.date==='1956-06-13'&&/Madrid/.test(m.home));assert(early);assert(early.lineups.length>=22);assert.deepEqual(early.goals.map(g=>String(g.minute)).sort((a,b)=>+a-+b),['6','10','14','30','62','67','79']);
const classics=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../data/classic-player-profiles.json')));const ci=read('players/classic-index.json');assert.equal(ci.players.length,classics.players.length);const classicParts=Array.from({length:32},(_,i)=>read('players/classic-part-'+String(i).padStart(2,'0')+'.json'));for(const p of ci.players){assert(!('historyPeriods' in p||'matchRecords' in p));assert(classicParts[p.shard][p.id]);}assert.equal(classics.meta.players,classics.players.length);assert.equal(new Set(classics.players.map(p=>p.id)).size,classics.players.length);
for(const p of classics.players){for(const r of p.historyPeriods||[]){if(r.startPrecision===9)assert(r.visibleFrom.endsWith('-12-31'));assert(r.visibleFrom>=r.start);}for(const r of p.matchRecords||[])if(/uefa.com/.test(r.source||'')){assert.equal(r.starter,true,'UEFA bench registered as an appearance');assert.equal(r.role,'starting_lineup');}for(const r of p.benchRecords||[])assert.equal(r.starter,false);}
const sandbox=vm.createContext({state:{date:'1960-01-01',playerWatch:[]},esc:s=>String(s),koreanPlayer:p=>p.name,playerAge:()=>20,playerCountryName:s=>s,n:s=>s,teamLabel:s=>s});vm.runInContext(fs.readFileSync(path.join(root,'historic-players.js'),'utf8'),sandbox);
const html=vm.runInContext(`historicPlayerProfileHTML({id:'test',name:'Test',birth:'1940-01-01',country:'Testland',source:'https://example.org',historyPeriods:[{club:'PAST',visibleFrom:'1959-12-31',start:'1959-01-01',startPrecision:9},{club:'FUTURE',visibleFrom:'1961-12-31',start:'1961-01-01',startPrecision:9}],matchRecords:[{date:'1962-01-01',team:'FUTURE CLUB',starter:true}],benchRecords:[]})`,sandbox);assert(html.includes('PAST'));assert(!html.includes('FUTURE'));
const ti=read('transfer-threads/index.json');let links=0;for(let part=0;part<64;part++){const f=path.join(root,'replay/transfer-threads/part-'+String(part).padStart(2,'0')+'.json');if(!fs.existsSync(f))continue;for(const [person,rs] of Object.entries(JSON.parse(fs.readFileSync(f)))){const p=ti.players.find(p=>p.id===person);assert(p);assert.equal(p.shard,part);assert.equal(p.first,rs[0].date);for(const r of rs){assert(!('veracity' in r||'finalDestination' in r));assert(r.date<=index.cutoff);links++;}}}assert.equal(links,ti.reportCount);
console.log(`PASS: ${count.toLocaleString()} archive games; ${events.toLocaleString()} verified event replays; all 70 complete seasons >100; shootout separation; early UEFA minutes and XI; dated sanctions, bonus points, unresolved ranks; ${classics.players.length} classic profiles; ${ti.players.length} reporting threads.`);
