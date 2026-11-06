(function(root){
 'use strict';
 const seasonFor=date=>Number(date.slice(0,4))-(Number(date.slice(5,7))<7);
 function visible(data,summer,{date,closed=[],includeSummer=true}){
  const rows=[...(data?.events||[]),...(includeSummer?(summer?.events||[]).filter(e=>e.summer&&e.date>=`${data.season+1}-07-01`&&e.date<=`${data.season+1}-08-31`):[])];
  return [...new Map(rows.filter(e=>e.date<date||(e.date===date&&closed.includes(date))).map(e=>[e.id,e])).values()].sort((a,b)=>a.date.localeCompare(b.date)||(b.priority||0)-(a.priority||0)||a.id.localeCompare(b.id));
 }
 const api={seasonFor,visible};if(typeof module==='object'&&module.exports)module.exports=api;else root.SeasonRecapEngine=api;
})(typeof globalThis==='object'?globalThis:this);
