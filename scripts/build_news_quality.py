"""Save a small, inspectable quality receipt and unresolved public bibliography."""
import collections,csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';OUT=ROOT/'dist/replay/news'
# A fresh clone carries the published receipt but not the ignored crawl caches.
# Translation-only updates must not turn known failures into an empty bibliography.
if not (P/'ftr18/2018_09_26_dataset.json').exists() and (OUT/'quality.json').exists():
    quality=json.loads((OUT/'quality.json').read_text())
    quality['stats']=json.loads((OUT/'index.json').read_text())['stats']
    quality['dataBytesExcludingQualityReceipt']=sum(p.stat().st_size for p in OUT.glob('*.json') if p.name!='quality.json')
    (OUT/'quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n')
    print('Updated delivery metadata; preserved published collection evidence and unresolved bibliography (raw cache absent).')
    raise SystemExit(0)
def read(name,default):
    p=P/name;return json.loads(p.read_text()) if p.exists() else default
def error_kind(error):
    if '404' in error:return 'not-found'
    if any(x in error for x in ['401','403','402']):return 'access-unavailable'
    if any(x in error for x in ['503','502','504','Remote end','timed out','reset']):return 'network-unavailable'
    if 'date conflict' in error.lower():return 'publication-date-conflict'
    return 'unverified-metadata'
ftr=read('ftr18/2018_09_26_dataset.json',{});failed_ftr=read('ftr-fetch-failures.json',[])
by_url={r['url']:r for r in ftr.values()};recovery=[]
for failure in failed_ftr:
    r=by_url.get(failure['url'],{});date=r.get('news_article_date','');parts=date.split('/')
    if len(parts)==3:date='-'.join(reversed(parts))
    recovery.append({'date':date,'publisher':r.get('news_source',''),'source':failure['url'],'sourceLanguage':r.get('language',''),'reason':error_kind(failure.get('error','')),'dateBasis':'FTR-18-publication-date'})
guardian_failures=read('guardian-fetch-failures.json',[])
for r in guardian_failures:
    date=r['date'];year,month,day=map(int,date.split('-'));m=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'][month-1]
    recovery.append({'date':date,'publisher':'The Guardian','source':f'https://www.theguardian.com/football/{year}/{m}/{day:02}/all','reason':error_kind(r.get('error','')),'kind':'daily-archive-page'})
recovery.sort(key=lambda r:(r['date'],r['source']))
(OUT/'recovery-index.json').write_text(json.dumps({'version':1,'notice':'These are unresolved public source references, not verified articles. They are excluded from displayed news totals.','sources':recovery},ensure_ascii=False,separators=(',',':')))
index=json.loads((OUT/'index.json').read_text());stats=index['stats'];edit=json.loads((OUT/'editorial.json').read_text())
guardian=[]
for p in (P/'guardian-days').glob('*.json'):
    d=json.loads(p.read_text());guardian.append({'date':d['date'],'status':d['status'],'count':len(d.get('articles',[]))})
quality={'snapshot':'2026-10-31','grains':{'editorial':'one checked publication and Korean editorial summary','archive':'one deduplicated article URL and source publication day','history':'one source-described event and exact event day'},'stats':stats,'sourceChecks':{'guardianDaysAttempted':10531,'guardianCachedDays':len(guardian),'guardianDaysUnavailable':len(guardian_failures),'guardianStatusCounts':dict(collections.Counter(r['status'] for r in guardian)),'FTR18BibliographySize':len(ftr),'FTR18ResolvedMetadata':len(read('ftr-records.json',[])),'FTR18UnresolvedReasons':dict(collections.Counter(r['reason'] for r in recovery if r.get('dateBasis')=='FTR-18-publication-date')),'wikinewsDatedArticles':len(read('wikinews-records.json',[])),'originalPrintReprints':len(read('reprint-records.json',[])),'historyPagesUnavailable':len(read('history-fetch-failures.json',[]))},'checks':['unique record IDs and canonical article URLs','valid exact dates and monthly partition integrity','day-count reconciliation against all month files','no resolved rumour veracity or later destination labels','separate publication-day news and secondary-history event dates','match-specific and multi-match result spoiler gates','source attribution and explicit machine/original title labels','month-sized delivery budget and six-month browser cache'],'limitations':[{'severity':'high','issue':'Coverage is not all football history or every publisher. Early newspaper access and non-English coverage are uneven.','remediation':'Add licensed newspaper archives or supplied historical clippings with original publication-date evidence.'},{'severity':'high','issue':'Historical article pages may have been updated after initial publication. The link index is the currently available publisher index, not a preserved as-published snapshot.','remediation':'Keep the index distinct from manually checked editorial reports and attach versioned archival evidence when available.'},{'severity':'medium','issue':'External translation became unavailable; untranslated index titles remain in their original language.','remediation':'Retain original titles and exact source URLs; rerun the resumable translator or import approved translations when access is restored.'},{'severity':'medium','issue':'A source-described historical date is not the same as a contemporary newspaper publication date.','remediation':'Display those records only in the separate historical timeline.'},{'severity':'medium','issue':'Unresolved or blocked source references are not silently treated as empty football days.','remediation':'Publish the recovery bibliography separately and exclude it from news totals.'}],'reproducibleChecks':['node tests/verify-news.cjs','node tests/verify-replay.cjs','node tests/verify-world.cjs','node tests/verify-players.cjs'],'dataBytesExcludingQualityReceipt':sum(p.stat().st_size for p in OUT.glob('*.json') if p.name!='quality.json')}
(OUT/'quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n')
print('Quality receipt saved; unresolved source references:',len(recovery))
