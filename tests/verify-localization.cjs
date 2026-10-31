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
