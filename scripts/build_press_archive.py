"""Build month-sized public news indexes and a separate licensed history layer."""
import collections,hashlib,json,re,sqlite3,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research/news';OUT=ROOT/'dist/replay/news';OUT.mkdir(exist_ok=True)
db=sqlite3.connect(P/'translations.sqlite')
db.execute('CREATE TABLE IF NOT EXISTS titles (key TEXT PRIMARY KEY, original TEXT, language TEXT, korean TEXT)')
translations={r[0]:r[1] for r in db.execute('SELECT key,korean FROM titles')}
reviewed_titles=json.loads((ROOT/'data/headline-reviewed.json').read_text())
reprint_titles=json.loads((ROOT/'data/reprint-title-overrides.json').read_text())
locale=json.loads((ROOT/'dist/replay/localization.json').read_text())
person_names={k:v for k,v in locale['playerNames'].items() if len(k)>5 and ' ' in k}
person_names.update({'Gareth Southgate':'가레스 사우스게이트','Pep Guardiola':'펩 과르디올라','José Mourinho':'조제 모리뉴','Jose Mourinho':'조제 모리뉴','Alex Ferguson':'알렉스 퍼거슨','Arsène Wenger':'아르센 벵거','Arsene Wenger':'아르센 벵거','Jürgen Klopp':'위르겐 클롭','Jurgen Klopp':'위르겐 클롭','Claudio Ranieri':'클라우디오 라니에리','Brendan Rodgers':'브렌던 로저스','Harry Redknapp':'해리 레드냅','Sam Allardyce':'샘 앨러다이스','Roberto Mancini':'로베르토 만치니','Mauricio Pochettino':'마우리시오 포체티노','Thomas Tuchel':'토마스 투헬','Antonio Conte':'안토니오 콘테','Carlo Ancelotti':'카를로 안첼로티','Roy Hodgson':'로이 호지슨','Erik ten Hag':'에릭 텐하흐'})
person_names.update({'Pelé':'펠레','Pele':'펠레','Diego Maradona':'디에고 마라도나','Johan Cruyff':'요한 크라위프','Franz Beckenbauer':'프란츠 베켄바워','Bobby Charlton':'보비 찰턴','Bobby Moore':'보비 무어','George Best':'조지 베스트','Stanley Matthews':'스탠리 매슈스','Alfredo Di Stefano':'알프레도 디 스테파노','Ferenc Puskas':'페렌츠 푸스카스','Lev Yashin':'레프 야신','Gerd Muller':'게르트 뮐러','Gerd Müller':'게르트 뮐러','Michel Platini':'미셸 플라티니','Zinedine Zidane':'지네딘 지단','Roberto Baggio':'로베르토 바조','Paolo Rossi':'파올로 로시','Marco van Basten':'마르코 판바스턴','Ruud Gullit':'뤼트 휠릿','Frank Rijkaard':'프랑크 레이카르트','Gary Lineker':'게리 리네커','Kevin Keegan':'케빈 키건','Kenny Dalglish':'케니 달글리시','Brian Clough':'브라이언 클러프','Bill Shankly':'빌 샹클리','Bob Paisley':'밥 페이즐리','Matt Busby':'맷 버스비','Duncan Edwards':'던컨 에드워즈','Gordon Banks':'고든 뱅크스'})
glossary={**locale['exact'],**person_names}
for ambiguous in ['Reading','Nice']:glossary.pop(ambiguous,None)
name_prefixes=collections.defaultdict(list)
for name in sorted(glossary,key=len,reverse=True):
    first=re.match(r'\w+',name)
    if len(name)>4 and first:name_prefixes[first[0]].append(name)
def replace_known_names(text):
    chunks=[];cursor=0
    for token in re.finditer(r'(?<!\w)\w+',text):
        start=token.start()
        if start<cursor:continue
        for name in name_prefixes.get(token[0],[]):
            end=start+len(name)
            if text.startswith(name,start) and (end==len(text) or not (text[end].isalnum() or text[end]=='_')):
                chunks.extend([text[cursor:start],glossary[name]]);cursor=end;break
    chunks.append(text[cursor:]);return ''.join(chunks)
def translated(text,lang='en'):
    if lang=='ko':return text,False
    key=hashlib.sha256((lang+'\0'+text).encode()).hexdigest();ko=translations.get(key,'')
    if not ko:return '',False
    ko=replace_known_names(ko)
    for wrong,right in [('2루타','멀티골'),('클린 시트','무실점'),('깨끗한 시트','무실점'),('햇트릭','해트트릭')]:ko=ko.replace(wrong,right)
    if re.search(r'\bvictory\b',text,re.I) and not re.search(r'\b(title|champions?|cup|trophy)\b',text,re.I):ko=ko.replace('우승','승리')
    return ko,True
def canonical(url):
    p=urllib.parse.urlsplit(url);query=urllib.parse.parse_qsl(p.query,keep_blank_values=True)
    query=[(k,v) for k,v in query if not k.startswith('utm_') and k not in ['fbclid','CMP','amp']]
    return urllib.parse.urlunsplit(('https',p.netloc.lower().removeprefix('www.'),p.path.rstrip('/'),urllib.parse.urlencode(query),''))
TRANSFER=re.compile(r'\b(?:transfers?|transfer rumours?|rumour mill|signs? for|signing|bid for|loan move|joins? [A-Z]|deal for|release clause|buyout clause|contract talks|contract extension|transfer window)\b',re.I)
CONTROVERSY=re.compile(r'\b(?:racis\w*|scandal|discrimin\w*|banned|guilty|arrest\w*|corrupt\w*|fraud|riots?|stampede|death|dead|crowd crush|liquidation|match.fixing|doping|hooligan\w*|homophob\w*|sexism|protest\w*|abuse|suspend\w*|financial charges|violence|rape|murder\w*|disaster|tragedy)\b',re.I)
def category(row):
    title=row['title'];url=row['source']
    if 'football-transfer-rumours' in url or re.search(r'\brumours?\b|rumour mill',title,re.I):return '이적설·협상',True
    if row.get('type')=='transfer-index' or TRANSFER.search(title):return '이적 보도',True
    if CONTROVERSY.search(title):return '논란',False
    if '/blog/' in url or re.search(r'\b(?:fans|reaction|opinion|talking points|column|letters|analysis|analyses)\b',title,re.I):return '여론·분석',False
    return '현장·반응',False
editorials=json.loads((OUT/'editorial.json').read_text());editorial_sources={canonical(r['source']) for r in editorials}
months=collections.defaultdict(lambda:{'articles':[],'events':[]});days=collections.defaultdict(lambda:[0,0,0,0]);seen=set();issues=[];missing=0;localized=0;named=0;source_counts=collections.Counter();types=collections.Counter();date_counts=collections.Counter();year_counts=collections.defaultdict(collections.Counter)
def add_article(row):
    global missing,localized,named
    # Language editions share a publisher; the language remains a separate field.
    aliases={'Goal Portuguese':'Goal','Goal Spanish':'Goal','ESPN Spanish':'ESPN','ESPN Portuguese':'ESPN'}
    row={**row,'publisher':aliases.get(row['publisher'],row['publisher'])}
    date=row.get('date','');source=row.get('source','');title=row.get('title','')
    try:
        import datetime;datetime.date.fromisoformat(date)
    except (ValueError,TypeError):issues.append(['invalid-date',date,source]);return
    if not '1956-01-01'<=date<='2026-10-31' or not source.startswith(('http://','https://')) or not title.strip():issues.append(['invalid-required-field',date,source]);return
    key=canonical(source)
    if key in seen or key in editorial_sources:return
    seen.add(key);cat,market=category(row);ko,auto=translated(title,row.get('language','en'))
    edited=reprint_titles.get(row['id']) or reviewed_titles.get(title)
    if edited:ko,auto=edited,False
    if ko:localized+=1
    else:missing+=1
    # Only short link-index metadata is distributed for newspaper articles.
    # Long English titles remain linked without being copied into the app.
    name_title=replace_known_names(title) if not ko else title
    names_only=not ko and name_title!=title
    if names_only:named+=1
    display=ko or name_title
    if row['publisher']!='Wikinews' and len(display.split())>25:display=' '.join(display.split()[:24])+'…'
    rec={k:row[k] for k in ['id','date','source','publisher','dateBasis','license','dataset','references','sourcePublicationDate','originalDateEvidence'] if row.get(k)}
    rec.update(title=display,category=cat,market=market,titleTranslation='edited' if edited else 'machine' if auto else 'names' if names_only else 'original',sourceLanguage=row.get('language','en'),kind='archive-index',resultRisk=bool(re.search(r'\b\d{1,2}\s*[–:-]\s*\d{1,2}\b',title)) or not (cat=='이적설·협상' or row.get('type')=='transfer-index'))
    if row.get('summary'):
        summary,summary_auto=translated(row['summary'],row.get('language','en'))
        if summary:rec.update(text=summary,textTranslation='machine' if summary_auto else 'original')
    months[date[:7]]['articles'].append(rec);days[date][0]+=1;days[date][1]+=int(market)
    source_counts[row['publisher']]+=1;types[row.get('type','guardian-index' if row['publisher']=='The Guardian' else 'wikinews')]+=1;date_counts[row.get('dateBasis','unknown')]+=1;year_counts[date[:4]]['articles']+=1
if (P/'reprint-records.json').exists():
    for row in json.loads((P/'reprint-records.json').read_text()):add_article(row)
for file in sorted((P/'guardian-days').glob('*.json')):
    for row in json.loads(file.read_text()).get('articles',[]):add_article(row)
for name in ['wikinews-records.json','ftr-records.json']:
    if (P/name).exists():
        for row in json.loads((P/name).read_text()):add_article(row)
history_seen=set()
history_rows=json.loads((P/'history-records.json').read_text()) if (P/'history-records.json').exists() else []
history_rows+=json.loads((ROOT/'data/historical-landmarks.json').read_text())
if (ROOT/'data/historical-case-records.json').exists():history_rows+=json.loads((ROOT/'data/historical-case-records.json').read_text())
for row in history_rows:
    date=row['date'];key=(date,re.sub(r'\W+','',row['title']).lower())
    if key in history_seen:continue
    history_seen.add(key);ko,auto=translated(row['title'],row.get('language','en'))
    rec={k:row[k] for k in ['id','date','source','publisher','historyKind','dateBasis','license','references'] if row.get(k)}
    name_title=replace_known_names(row['title']) if not ko else row['title']
    rec.update(title=ko or name_title,titleTranslation='edited' if row.get('language')=='ko' else 'machine' if auto else 'names' if name_title!=row['title'] else 'original',sourceLanguage=row.get('language','en'),kind='history-record',priority=3 if row.get('language')=='ko' else 1 if auto else 0)
    months[date[:7]]['events'].append(rec);days[date][2]+=1;year_counts[date[:4]]['events']+=1
for r in editorials:
    days[r['date']][0]+=1;days[r['date']][1]+=int(bool(r.get('player')));days[r['date']][3]+=1;year_counts[r['date'][:4]]['editorials']+=1
month_index={};largest=0;total_bytes=0
for month,data in sorted(months.items()):
    for kind in ['articles','events']:data[kind].sort(key=lambda r:(r['date'],-r.get('priority',0),r['id']))
    output={'month':month,**data};raw=json.dumps(output,ensure_ascii=False,separators=(',',':')).encode();(OUT/(month+'.json')).write_bytes(raw);largest=max(largest,len(raw));total_bytes+=len(raw)
    month_index[month]={'file':'news/'+month+'.json','articles':len(data['articles']),'events':len(data['events']),'bytes':len(raw)}
stats={'editorialReports':len(editorials),'archiveLinks':sum(types.values()),'historicalRecords':len(history_seen),'datedEditions':len([d for d,v in days.items() if v[0]]),'sourceOrganizations':len(set(source_counts)|{r['publisher'] for r in editorials}),'localizedIndexTitles':localized,'originalTitleFallbacks':missing,'nameLocalizedIndexTitles':named,'bySource':dict(source_counts),'byType':dict(types),'dateEvidence':dict(date_counts),'monthlyDataBytes':total_bytes,'largestMonthBytes':largest,'coverageByYear':dict(sorted(year_counts.items()))}
index={'version':2,'cutoff':'2026-10-31','days':dict(sorted(days.items())),'months':month_index,'stats':stats,'datePolicy':'exact-day','historyPolicy':'separate-secondary-history','sourcePolicy':'newspaper-links-only; licensed Wikinews summaries; separately checked editorial reports'}
(OUT/'index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')))
(P/'build-quality-issues.json').write_text(json.dumps(issues,ensure_ascii=False))
print(json.dumps(stats,ensure_ascii=False,indent=2))
