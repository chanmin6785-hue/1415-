'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),N=require('../dist/news-engine.js'),E=require('../dist/engine.js');
const base=path.resolve(__dirname,'../dist/replay'),read=f=>JSON.parse(fs.readFileSync(path.join(base,f))),story=read('stories.json'),catalogue=read('news/index.json');
const ids=new Set(),sources=new Set(),dayCounts=new Map(),addDay=(d,i)=>{if(!dayCounts.has(d))dayCounts.set(d,[0,0,0,0]);dayCounts.get(d)[i]++};
const checkDate=d=>{assert.match(d,/^\d{4}-\d{2}-\d{2}$/);assert(d>='1956-01-01'&&d<=catalogue.cutoff,d);assert.equal(new Date(d+'T00:00:00Z').toISOString().slice(0,10),d)};
for(const r of story.stories){checkDate(r.date);assert(!ids.has(r.id));ids.add(r.id);assert(r.text&&r.context&&r.watch&&r.source&&r.publisher);assert.equal(r.dateBasis,'original-datePublished');addDay(r.date,0);addDay(r.date,3);if(r.player)addDay(r.date,1)}
let articleCount=0,eventCount=0,largest=0,localized=0,original=0,named=0,monthlyBytes=0;
for(const [month,entry] of Object.entries(catalogue.months)){
 const data=read(entry.file);assert.equal(data.month,month);assert.equal(data.articles.length,entry.articles);assert.equal(data.events.length,entry.events);const bytes=fs.statSync(path.join(base,entry.file)).size;assert.equal(bytes,entry.bytes);monthlyBytes+=bytes;largest=Math.max(largest,bytes);
 for(const kind of ['articles','events'])for(const r of data[kind]){
  checkDate(r.date);assert(r.date.startsWith(month));assert(r.title&&r.publisher);assert.match(r.source,/^https?:\/\//);assert(!ids.has(r.id),'Repeated record ID '+r.id);ids.add(r.id);
  assert(['machine','edited','names','original'].includes(r.titleTranslation),'Unknown title language label');
  if(kind==='articles'){if(['machine','edited'].includes(r.titleTranslation))localized++;else original++;if(r.titleTranslation==='names')named++;if(/\b\d{1,2}\s*[–:-]\s*\d{1,2}\b/.test(r.title))assert(r.resultRisk,'A scored headline escaped the result gate');}
  assert(!('veracity' in r||'finalDestination' in r||'evidence_date' in r),'Future rumour resolution leaked');
  if(kind==='articles'){assert.equal(r.kind,'archive-index');assert(!sources.has(r.source),'Repeated news URL');sources.add(r.source);addDay(r.date,0);if(r.market)addDay(r.date,1);articleCount++;assert(['publisher-daily-archive','published-dateline','FTR-18-publication-date','original-print-date-in-publisher-reprint'].includes(r.dateBasis));}
  else{assert.equal(r.kind,'history-record');addDay(r.date,2);eventCount++;}
 }
}
assert.equal(articleCount,catalogue.stats.archiveLinks);assert.equal(eventCount,catalogue.stats.historicalRecords);assert.equal(story.stories.length,catalogue.stats.editorialReports);assert(largest<5*1024*1024,'Month shard exceeds delivery budget');
assert.equal(localized,catalogue.stats.localizedIndexTitles);assert.equal(original,catalogue.stats.originalTitleFallbacks);assert.equal(named,catalogue.stats.nameLocalizedIndexTitles);assert.equal(monthlyBytes,catalogue.stats.monthlyDataBytes);assert.equal(largest,catalogue.stats.largestMonthBytes);
assert.deepEqual(Object.fromEntries([...dayCounts].sort(([a],[b])=>a.localeCompare(b))),catalogue.days);
const city=story.features.find(f=>f.id==='title-day'),options={date:'2012-05-13',closed:[],isMatchComplete:m=>E.completed(m,'2012-05-13',[],[])};
assert.equal(N.visible(story.stories,options).length,0,'Result articles shown before match');
let watched=[E.key(city)];let revealed=N.visible(story.stories,{...options,isMatchComplete:m=>E.completed(m,options.date,[],watched)});assert.equal(revealed.length,4);assert(revealed.every(r=>r.date===options.date));
assert.equal(N.visible(story.stories,{...options,isMatchComplete:m=>E.completed(m,options.date,[],['1999-05-26|Manchester United FC|FC Bayern München'])}).length,0,'Unrelated watched match unlocked the news');
const neymar=N.visible(story.stories,{date:'2017-07-26',closed:[],isMatchComplete:()=>false});assert(neymar.some(r=>r.title.includes('피케')));assert(neymar.every(r=>r.date==='2017-07-26'));assert(!neymar.some(r=>r.category==='공식 발표'));
const korea=story.stories.find(r=>r.source.includes('12757087'));assert.equal(N.unlocked(korea,{date:korea.date,isMatchComplete:m=>m.home==='South Korea'}),false,'One match unlocked a two-match outcome');
assert.equal(N.visible(story.stories,{date:'1956-01-01'}).length,0,'Past reports filled an empty issue');
const recommendation=N.visible(story.stories,{date:'2024-02-15'});assert(recommendation.some(r=>r.source.includes('AEN20240215008253315')));assert(!recommendation.some(r=>r.source.includes('AEN20240216005152315')),'Final dismissal leaked into recommendation day');
const asianGold=story.stories.find(r=>r.source.includes('AEN20180901001800315'));assert(asianGold);assert(!N.unlocked(asianGold,{date:'2018-09-01'}),'Asian Games final result shown before day close');assert(N.unlocked(asianGold,{date:'2018-09-01',closed:['2018-09-01']}));
assert(!sources.has('javascript:alert(1)'));assert(catalogue.days['1956-12-18'][2]>0);assert(catalogue.days['1970-06-21'][2]>0);
console.log(`PASS: ${story.stories.length} edited reports, ${articleCount.toLocaleString()} dated news links, ${eventCount.toLocaleString()} separate historical records; daily counts, source/date integrity, multi-match spoiler gates and month delivery budget (${Math.ceil(largest/1024)} KB max).`);
