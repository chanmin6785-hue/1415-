'use strict';
const fs=require('node:fs'),path=require('node:path'),E=require('../dist/engine.js'),root=path.resolve(__dirname,'..'),base=path.join(root,'dist/replay');
const read=f=>JSON.parse(fs.readFileSync(path.join(base,f))),m=read('manifest.json');E.configureRules(read('standings-rules.json'));const out={};
for(const [lid,league] of Object.entries(m.leagues))for(const s of league.seasons){const data=read(s.file),rows=E.table(data.matches,{league:lid,season:s.year,date:'9999',closed:[],watched:[]});out[lid+'|'+s.year]={teams:rows.map(r=>r.name),leaders:rows.filter(r=>r.rank===1).map(r=>r.name),contenders:rows.filter(r=>r.pts===rows[0]?.pts).map(r=>r.name),end:s.end};}
fs.mkdirSync(path.join(root,'research/recap'),{recursive:true});fs.writeFileSync(path.join(root,'research/recap/computed-tables.json'),JSON.stringify(out));
