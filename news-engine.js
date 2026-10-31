'use strict';
(function(root){
  const dayReports=(reports,date)=>reports.filter(r=>r.date===date);
  function unlocked(report,{date,closed=[],isMatchComplete=()=>false}){
    if(report.date!==date)return false;
    if(!report.matchDate&&!report.matches?.length)return true;
    if(closed.includes(report.matchDate||report.date))return true;
    return !!report.matches?.length&&report.matches.every(isMatchComplete);
  }
  function visible(reports,options){return dayReports(reports,options.date).filter(r=>unlocked(r,options)).sort((a,b)=>(b.priority||0)-(a.priority||0)||(a.publishedAt||a.date).localeCompare(b.publishedAt||b.date));}
  function editionDate(reports,date,direction,market=false){return [...new Set(reports.filter(r=>!market||r.player).map(r=>r.date))].filter(d=>direction>0?d>date:d<date).sort((a,b)=>direction>0?a.localeCompare(b):b.localeCompare(a))[0]||null;}
  const api={dayReports,unlocked,visible,editionDate};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.NewsEngine=api;
})(typeof globalThis==='object'?globalThis:this);
