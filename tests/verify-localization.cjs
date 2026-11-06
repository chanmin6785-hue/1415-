'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../dist'),data=JSON.parse(fs.readFileSync(path.join(root,'replay/localization.json')));
const sandbox=vm.createContext({document:{addEventListener(){}},esc:s=>String(s),names:{}});
vm.runInContext(fs.readFileSync(path.join(root,'locale.js'),'utf8'),sandbox);
vm.runInContext('LocaleData='+JSON.stringify(data),sandbox);
const evaluate=s=>vm.runInContext(s,sandbox);
assert.equal(evaluate('koreanName("Manchester City")'),'맨체스터 시티');
assert.equal(evaluate('koreanName("South Korea")'),'대한민국');
assert.equal(evaluate('koreanPlayer({id:"91845",name:"Heung-min Son"})'),'손흥민');
assert.equal(evaluate('koreanName("Unverified Club 123")'),'Unverified Club 123');
assert.equal(evaluate('crestRecord("Unverified Club 123").crest'),undefined);
assert.equal(evaluate('koreanCompetition("L1")'),'분데스리가');
assert(evaluate('crestHTML("Manchester City")').includes('현재 엠블럼'));
assert.equal(data.crestPeriod,'current');
for(const c of Object.keys(JSON.parse(fs.readFileSync(path.join(root,'replay/players/competitions.json')))))assert.match(data.competitions[c].ko,/[가-힣]/,c);
const assets=new Set([...Object.values(data.teams),...Object.values(data.teamIds)].map(r=>r.crest).filter(Boolean).concat(Object.values(data.flags)));
for(const asset of assets){assert(asset.startsWith('assets/crests/'),asset);assert(fs.statSync(path.join(root,asset)).size>100,asset);}
const catalogue=JSON.parse(fs.readFileSync(path.join(root,'replay/players/index.json')));
const grouped=new Map();
for(const p of catalogue.players)if(data.players[p.id]){if(!grouped.has(p.name))grouped.set(p.name,new Set());grouped.get(p.name).add(data.players[p.id]);}
for(const [name,labels] of grouped)if(labels.size>1)assert.equal(data.playerNames[name],undefined,'Ambiguous scorer name: '+name);
console.log(`PASS: Korean identity aliases, unknown-name fallback, current-crest labels, ${Object.keys(data.competitions).length} competitions and ${assets.size} referenced local assets.`);

const periods=Object.values(data.crestHistory).flat();assert.equal(periods.length,11);for(const p of periods){assert(fs.statSync(path.join(root,p.crest)).size>100);assert(p.from<=p.to);assert(p.source.startsWith('https://'));}
evaluate('globalThis.state={date:"2012-05-13"}');assert(evaluate('crestHTML("Manchester City")').includes('manchester-city-1997.png'));assert(evaluate('crestHTML("Manchester City")').includes('당시 엠블럼'));evaluate('state.date="1956-06-13"');assert(evaluate('crestHTML("Manchester City")').includes('현재 엠블럼'));
console.log('PASS: 11 temporal crest periods and explicit unverified-period fallback.');

assert.notEqual(evaluate('localeKey("전북")'),evaluate('localeKey("서울")'));assert.equal(evaluate('localeKey("전북")'),'전북');assert.equal(evaluate('koreanName("미수록한국팀")'),'미수록한국팀');assert.equal(evaluate('koreanName("")'),'');assert(evaluate('crestHTML("전북")').includes('6502.png'));assert(!evaluate('crestHTML("전북")').includes('932.png'));console.log('PASS: distinct Hangul team identity, correct Jeonbuk crest and unknown Korean fallback.');
