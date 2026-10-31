"""Read public article metadata for editorial date checking; raw pages stay ignored."""
import concurrent.futures, hashlib, html, json, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'research/news';P.mkdir(parents=True,exist_ok=True)
def fetch(row):
    out=P/(hashlib.sha256(row['url'].encode()).hexdigest()[:16]+'.json')
    if out.exists(): return json.loads(out.read_text())
    req=urllib.request.Request(row['url'],headers={'User-Agent':'Mozilla/5.0 FootballHistoryResearch/1.0'})
    raw=urllib.request.urlopen(req,timeout=15).read().decode('utf-8','replace')
    dates={k:re.findall(r'"'+k+r'"\s*:\s*"([^\"]+)"',raw) for k in ['datePublished','dateModified']}
    desc=re.search(r'<meta\s+name="description"\s+content="([^"]*)"',raw)
    body=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',raw,flags=re.S)
    body=html.unescape(re.sub('<[^>]+>',' ',body));body=re.sub(r'\s+',' ',body)
    row={**row,**dates,'description':html.unescape(desc.group(1)) if desc else '', 'body':body}
    out.write_text(json.dumps(row,ensure_ascii=False));return row
if __name__=='__main__':
    rows=json.loads((P/'source-search.json').read_text())
    rows=[r for r in rows if any(d in r['url'] for d in ['skysports.com/football/news/','skysports.com/transfer/news/','uefa.com/','tottenhamhotspur.com/news/','fcbarcelona.com/en/football/','liverpoolfc.com/news/'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        fs={pool.submit(fetch,r):r for r in rows};ok=[];bad=[]
        for f in concurrent.futures.as_completed(fs):
            try:ok.append(f.result())
            except Exception as e:bad.append({'url':fs[f]['url'],'error':str(e)})
    (P/'verified-sources.json').write_text(json.dumps(ok,ensure_ascii=False))
    (P/'failed-sources.json').write_text(json.dumps(bad,ensure_ascii=False))
    print('Fetched',len(ok),'sources;',len(bad),'unavailable')
