# Football Time Machine · 풋볼 타임머신

1956년부터 하루 단위로 축구를 다시 보는 한국어 웹앱입니다. 실제 결과를 바꾸는 시뮬레이션이 아니라, 미래 결과를 감추고 날짜에 맞춰 기록을 공개하는 역사 리플레이입니다.

## 실행

```sh
python -m http.server 4173 --directory dist
# http://localhost:4173
node tests/verify-replay.cjs
node tests/verify-world.cjs
node tests/verify-news.cjs
node tests/verify-expansion.cjs
node tests/verify-season-recaps.cjs
```

런타임 의존성, API 키, 서버 데이터베이스가 없습니다. GitHub Pages의 프로젝트 하위 경로에서도 상대 경로로 작동합니다.

## 기능

- 날짜 선택, 하루 전/후, 다음 경기일, 자동 진행. 중요한 경기 날짜에서 자동 정지.
- 리그·국가·지역 선택과 수록 기간 표시. K리그1·2, J1, 남미·북중미, 유럽 11개국 및 잉글랜드/독일 하부 리그.
- 한국 등 국가·대표팀별 전체 경기 이력 및 연도 선택.
- 박지성·손흥민·크라위프·호나우두 등 18명의 주요 성장 경로에서 해당 클럽의 경기·순위와 대표팀 이력으로 이동. 정확한 날짜 없는 경력은 연도 말에 보수적으로 공개.
- 실제 경기 결과를 이용한 일일 리그 순위. 승리 2점/3점 시대 구분과 잉글랜드의 과거 골 평균 적용.
- 유러피언컵/챔피언스리그, 월드컵, 유로 실제 대진. 미래 진출 팀과 스코어 숨김.
- 중요한 경기의 득점·퇴장 등에 맞춘 문자 리플레이. 일시정지, 다음 주요 장면, 속도 조절.
- 2012-05-13 맨체스터 두 경기의 득점 시점에 따른 실시간 우승 레이스.
- 날짜가 있는 실제 기사 요약과 이적 보도. 이적설·구단 입장·공식 발표를 분리. 선수 소식 추적.
- 기존 선수/클래식 팀 아카이브는 `archive.html`에 보존.

## 수록 데이터

| 종류 | 수록량 |
|---|---:|
| 30개 리그·디비전 실제 결과 | 372,746경기 |
| 남자 국가대표 A매치 | 45,740경기 |
| 유럽 클럽 대회 | 26,681경기 / 223개 대회 시즌 |
| 월드컵 | 18개 본선 (1958–2026) |
| 유로 | 17개 본선 (1960–2024, 1968 재경기 포함) |
| 별도 연출 역사적 경기 | 8경기 |
| 한국어로 정리한 주요 보도 | 148건 / 113개 날짜 |
| 시즌별 주요 경기 아카이브 | 143,674경기 |
| 실제 사건 기록 재생 | 89,644경기 / 완결 70시즌 모두 100경기 초과 |
| 확인된 경기별 선발·벤치 | 17,760경기 / 666,134개 명단 항목 |
| 고전 선수 추가 프로필 | 9,309개 / 소속·대회 등록·실제 출전 구분 |
| 발행일별 원문 보도 색인 | 210,583건 |
| 별도 사건·논란 연표 | 5,222건 / 1956–2026년 |

월드컵/유로 경기는 A매치 자료에도 포함되므로 위 숫자를 단순 합산하면 중복입니다. 유럽 대회는 수록 범위 내 예선도 포함하되 2016/17 이후 원본 TXT는 본선 기준입니다. 본선 조 편성·단계는 수록되지만 과거의 모든 조 추첨 발표 시점은 없습니다. 최종 수집 기준: 2026-10-31. 2026/27 챔피언스리그·유로파리그는 수집일 이전 완료 경기까지 추가했습니다. 슈퍼컵의 1–2월 경기는 이전 시즌 대회에 묶어 달력 연도와 대회 연도를 구분합니다.

경기·선수 자료는 시즌/대회/선수별로, 보도 자료는 696개 월별 JSON으로 분할했습니다. 보도 월별 파일은 최대 약 631KiB이며 브라우저는 최대 6개월만 캐시합니다. 보도 월별 데이터 약 90MiB, 전체 배포 파일 약 549MiB로 정적 배포에 수록했습니다. 원문 CSV나 신문 기사 전문은 배포하지 않습니다.

## 정확도와 연출

- 리그 순위는 **경기 결과 재계산 순위**입니다. 승점 삭감, 몰수·행정 처분, 모든 국가/대회의 상대전적·플레이오프 규정은 완전히 반영하지 않아 공식 일일 발표 순위와 다를 수 있습니다.
- 조별 동률은 기본 승점→골득실→다득점 정렬이며, 모든 대회의 당시 순위 규정을 완전히 재현하지 않습니다.
- 날짜는 경기의 현지 날짜이며, 하루는 00:00에 시작합니다. 당일 결과는 직접 중계를 마치거나 하루를 마감/다음 날로 넘길 때 공개됩니다.
- 대진의 미래 참가 팀 공개는 이전 단계 경기 완료 기준입니다. 실제 조 추첨 발표 시각의 완전한 재현은 아닙니다.
- 한국어 중계 문장은 재구성입니다. 기록에 없는 슈팅, 팬 발언, 관중 수치, 협상 확률, 여론 비율은 창작하지 않았습니다.
- 기자의 기사 전체를 복제하지 않았습니다. 선별 기사 날짜·매체·짧은 요약·원문 링크만 제공합니다. 각 기사에만 나타난 반응을 전체 여론으로 일반화하지 않습니다.
- 보도와 이적시장은 **선택한 날 발행된 기사만** 표시합니다. 카카·호날두·토레스·베일·손흥민·네이마르·메시·음바페·케인 등 여러 협상과 안정환/페루자 사건을 날짜별 주요 보도로 정리했습니다. 링크 색인에도 이적/이적설 필터가 있지만 제목 기반 분류이므로 오분류가 있을 수 있습니다. 모든 매체의 모든 이적설을 제공하지 않습니다.
- 경기 결과가 들어갈 수 있는 보도는 해당 경기 관람 또는 하루 마감 후 공개합니다. 당일 기사의 실제 발행 시각까지 재현하는 기능은 아닙니다.
- 당시 보도와 후대의 사건 정리를 분리합니다. 사건 연표는 별도 탭이며 하루 마감 후 공개합니다. 후대 자료에는 이후 밝혀진 정보가 포함될 수 있다는 안내를 표시합니다.
- 약 20만 건의 색인은 기사 전문이나 모두 검토한 한국어 요약이 아닙니다. 번역된 색인 제목 119,290건, 나머지 원문 제목 91,293건 중 54,387건은 확인된 선수/팀 이름을 한국어로 표기했습니다. 각 카드에서 자동 번역·이름 표기·원문을 구분합니다. 자동 번역 오류가 있을 수 있습니다.
- 기존 식별용 엠블럼과 국기에 더해 6개 구단의 검증된 11개 버전을 날짜별로 전환합니다. 정확한 전환일이 없는 연도는 미확인으로 남깁니다. 기념 유니폼 등 모든 변형은 아니며 나머지는 현재 식별용이라고 표시합니다. 모든 시즌 전체 스쿼드가 아닌 실제 경기별 선발·벤치와 별도 대회 등록 자료입니다.

## 출처

- [James P. Curley / engsoccerdata](https://github.com/jalapic/engsoccerdata), GPL (>=2): 유럽 5대 리그 역사 결과.
- [Football-Data.co.uk](https://www.football-data.co.uk/data.php): 최근 2시즌 경기 결과. 원저작자 출처와 별도 이용 조건을 유지합니다.
- [Mart Jürisoo / international_results](https://github.com/martj42/international_results), CC0: 남자 국가대표 결과, 득점, 승부차기.
- [OpenFootball / worldcup.json](https://github.com/openfootball/worldcup.json), CC0: 월드컵 단계와 조, 득점.
- [FootballCSV / europe-champions-league](https://github.com/footballcsv/europe-champions-league): 1955/56–2015/16 유럽 클럽 대회.
- [OpenFootball / champions-league](https://github.com/openfootball/champions-league), CC0: 2016/17–2025/26 유럽 클럽 대회.
- 개별 문자중계/보도 출처: `dist/replay/stories.json` 및 앱의 데이터 안내.
- 대량 보도 색인: Guardian 일별 축구 아카이브, Wikinews 487건, FTR-18에서 원문 메타데이터를 확인하고 중복을 제거한 이적 보도 1,229건. 옛 신문 재수록 17건은 원래 지면 발행일과 웹 재게시일을 구분합니다.
- 출처별·연도별 수록량과 미확인 자료: `dist/replay/news/index.json`, `quality.json`, `recovery-index.json`. 자세한 범위와 대안은 [DATA_COVERAGE.md](DATA_COVERAGE.md)를 참조하세요.
- 경기장 분위기 사진: Unsplash `photo-1522778119026-d647f0596c20`. 특정 역사 경기의 현장 사진으로 표시하지 않습니다.

코드 라이선스: GPL-2.0-or-later. 각 원본 데이터·사진·기사의 이용 조건은 별도로 적용됩니다. GPL/CC0 고지는 `licenses/`를 참조하세요.

## 데이터 재생성

프로젝트 루트에서 실행합니다. 기존 경기 빌더는 Python 표준 라이브러리를 사용하며, 새 보도 수집기는 `beautifulsoup4`, `lxml`이 필요합니다.

```sh
python scripts/fetch_data.py
python scripts/build_replay.py
python scripts/enrich_ucl.py
python scripts/make_stories.py
python scripts/make_journeys.py
python scripts/expand_world.py
python scripts/fetch_kleague.py
python scripts/fetch_kleague2.py
python scripts/build_kleague.py
node tests/verify-replay.cjs
node tests/verify-world.cjs
```

소스 저장소의 미래 변경에 따라 스키마/결과가 달라질 수 있으므로 갱신 후 검증이 필요합니다. 원본 파일은 `research/`에만 보관하고 Git에 추가하지 않습니다. 스냅샷 종료 날짜는 현재 빌더에서 `2026-10-31`로 고정했습니다.

### 보도 자료 수집·검증

```sh
python -m pip install --target /tmp/football-news-deps beautifulsoup4 lxml
python scripts/fetch_press_archive.py
python scripts/fetch_wikinews_football.py
python scripts/fetch_transfer_press.py
python scripts/fetch_football_history.py
python scripts/fetch_historical_reprints.py
python scripts/verify_historical_cases.py
python scripts/build_editorial_news.py
python scripts/build_press_archive.py
python scripts/build_news_quality.py
node tests/verify-news.cjs
```

각 수집기는 `research/news/`의 체크포인트를 사용합니다. 원문 접근이 실패한 항목은 성공 건수에 포함하지 않습니다. Guardian 일별 페이지의 접근 실패 209건을 모두 복구했습니다. FTR-18 미확인 참고 링크 2,760건은 재시도 목록으로 분리했습니다. 외부 연결이 503 또는 연결 종료 오류로 중단되어 일부 원문 확인과 번역을 완료하지 못했으며, 원문과 출처를 유지했습니다.

번역은 선택 작업입니다. 새 복제본에서도 배포된 원문 제목을 읽어 재개할 수 있습니다. 외부 번역에 보내는 내용은 공개 기사 제목과 언어뿐입니다. 이후 번역 캐시를 적용하고 정합성을 다시 검사합니다.

```sh
python scripts/translate_press_headlines.py
python scripts/apply_news_translations.py
python scripts/build_news_quality.py
node tests/verify-news.cjs
```

이 명령들은 번역 서비스의 가용성과 이용 조건에 따라 실패할 수 있습니다. 월별 JSON을 수동 편집하기보다 출처·검증 자료와 빌더를 변경하고 재생성하세요. 최초 전체 수집에는 많은 네트워크 요청과 시간이 필요합니다.

## GitHub Pages

배포 주소: https://chanmin6785-hue.github.io/1415-/

`main` 브랜치는 앱 소스와 데이터를 보관합니다. `gh-pages` 브랜치는 `dist/`의 정적 파일을 루트에 배치합니다. 저장소 Settings → Pages에서 `gh-pages` / `(root)`를 선택해 배포합니다. GitHub Actions 워크플로 수정 권한이 없어도 이 방식으로 배포할 수 있습니다. `.nojekyll`로 정적 파일을 그대로 게시합니다.

## 확장 리그와 선수 경로의 한계

- 네덜란드 1956년부터, 포르투갈·스코틀랜드·그리스·튀르키예 1994년부터, 벨기에 1995년부터. 추가 국가의 최신 유럽 자료는 2026/27 시즌까지 수집했습니다.
- 잉글랜드 2부 1955/56부터, 잉글랜드 3·4부는 지역 리그를 잘못 합치지 않도록 1958/59부터, 독일 2부는 1974/75부터 수록합니다.
- J1, 브라질·아르헨티나·미국·멕시코·북유럽·오스트리아·스위스 등은 대부분 2012년부터, 중국은 2014년부터입니다.
- 한국은 공식 K리그 JSON 일정·결과를 조회하여 K리그1·2를 2013년부터 수록했습니다. 1983–2012 조회가 빈 응답인 것을 완전한 경기 이력으로 오인하지 않았습니다. 정규리그와 파이널 A/B를 포함하며 승강/준플레이오프는 기본 리그와 분리했습니다.
- K리그1은 파이널 개시일 이후 실제 그룹을 구분하고 이전 정규라운드 승점을 포함해 재계산합니다. 2016년 전북의 9점 삭감과 일부 유럽 리그의 징계·항소 17개 결정을 발표일 마감 후 반영합니다. 모든 처분을 수록한 것은 아닙니다.
- MLS 컨퍼런스, 전후기 대회, 유럽 일부 리그 스플릿의 공식 최종 순위를 완전히 구현하지는 못했습니다. 리그별 주의 문구를 표시합니다.
- 국가 데이터의 334개 명칭에는 역사적 국가, 비FIFA 대표팀 표기가 포함됩니다. 현대 FIFA 회원국 수를 뜻하지 않습니다.
- 선수 경로는 개인 경기 출전·능력치 데이터가 아닙니다. 클럽 경기만 있는 시기는 그 사실을 표시합니다. 유소년·리저브 클럽을 1군 경기로 대체하지 않습니다.

한국 공식 출처: https://www.kleague.com/getScheduleList.do (공개 일정 JSON, 읽기 전용 POST). 빌더는 요청 연도·경기 연도·대회 코드와 정규리그 여부를 검증합니다. 다른 국가 자료에서 잘못된 국가 피드가 내려오는 경우 국가 필드를 검사해 수록을 중단합니다.

## 선수 페이지 대량 검색

- 선수 프로필 **50,149명** 중 날짜가 있는 커리어 자료는 **39,218명**입니다.
- 소속 이동·등록 174,645건과 실제 개인 출전 1,894,348건을 512개 조각으로 나눴습니다. 선수 검색을 열 때 목록을 받고, 상세에서는 해당 조각만 가져옵니다.
- 한국어 주요 선수 이름, 원문 영문 이름, 악센트를 생략한 검색을 지원합니다. 국적·포지션 필터, 페이지 이동, 선수 저장, 선수/날짜별 공유 링크를 제공합니다.
- `?player=91845&date=2015-08-27`처럼 선수와 날짜를 URL에 지정할 수 있습니다.
- 소속 이동과 개인 출전·득점·도움은 선택 날짜 이하의 자료로만 표시합니다. 연도별 집계는 달력 연도·클럽·대회별이며 전체 통산 기록이 아닙니다.
- 프로필의 최신 소속, 최신 총 대표팀 출전·득점, 시장가치는 과거 화면에 사용하지 않습니다. 국적·포지션은 자료 시점의 참고 정보로 표시합니다.
- 원본에는 미래 임대 복귀 예정일 등이 있어 자료 스냅샷 이후 기록 520건을 제외했습니다. 실제 이전 날짜의 같은 날짜 이동들은 순서를 임의로 정하지 않습니다.
- 자료 갱신 중단 기준 **2026-07-06**, 출전 기록 마지막 날짜 **2026-06-28**. 그 이후 날짜에서는 갱신 중단 안내를 표시합니다.
- 대량 데이터는 현대 선수 중심입니다. 펠레·푸스카스·디 스테파노·베켄바워·야신·지단·매슈스·차범근 등은 별도로 선별한 주요 소속 경로로 보완했으며, 모든 고전 선수의 완전한 경력을 보장하지 않습니다.
- 출처: https://github.com/dcaribou/transfermarkt-datasets (CC0), 배포 사본 https://www.kaggle.com/datasets/davidcariboo/player-scores . `scripts/fetch_players.py`와 `scripts/build_players.py`로 재생성합니다.

검증: `node tests/verify-players.cjs` — 512개 파일의 정합성, 날짜 경계, 미래 이적 제외, 최신 스냅샷 통계 미포함 확인.

## 한국어 이름과 엠블럼

- 선수 한국어 이름 9,997명을 추가하고, 팀·국가·65개 대회 이름을 한국어로 표시합니다. 확인된 한국어 표기가 없으면 원문을 유지합니다. 영문 원래 이름 검색도 지원합니다.
- 경기 카드, 리그 순위표, 대진표, 문자중계, 선수의 소속 이동·출전 기록에서 로컬 엠블럼을 사용합니다. 현재 디자인임을 표시하며 당시 디자인으로 오인하지 않게 안내합니다.
- 이름 번역은 화면 표시 계층에만 적용합니다. 원본 선수/클럽 ID, 경기 매칭, 날짜별 결과 공개와 미래 이적 숨김 규칙은 유지합니다.
- 한국어 표기: Wikidata (P2446/P7223, CC0), mledoze/countries, korean-football-team-names. 엠블럼: Transfermarkt CDN 및 JoseArroyave/football-logos. 국기: FlagCDN. 개별 출처와 권리는 `licenses/NOTICE.md` 참고.
- 선수 이름 수집: `python scripts/fetch_korean_players.py`. `research/localization/`의 원본 팀·국가 자료와 crest manifest를 확보한 뒤 `build_localization.py` → `extend_crest_assets.py` → `apply_korean_overrides.py` 순으로 실행합니다. 검증은 `node tests/verify-localization.cjs`입니다.

## 시즌별 중계와 1–6 보강

‘시즌 주요 경기’에서 시즌·팀·대회·기록 종류를 고릅니다. 1956/57–2025/26 완결 70시즌의 실제 사건 재생 수는 118–2,884경기입니다. 100경기로 자르거나 빈 장면으로 채우지 않았습니다. 1955/56과 2026/27은 일부 기간입니다. 사건 시각이 없는 54,030경기는 종료 결과 열람으로 구분합니다.

득점 스코어, 자책골 귀속, 승부차기 분리를 검증하고 추가시간 원문을 보존합니다. 일부 원문은 추가시간 구분 기호가 없어 그 한계를 표시합니다. 2005 챔피언스리그·2022 월드컵 결승은 출처로 대조한 승부차기를 한 킥씩 공개하며 임의의 킥 시각은 없습니다.

일일 순위에는 확인된 징계의 당시 결정과 이후 항소 변경을 구분해 적용합니다. 잉글랜드 골 평균, 일부 리그 상대전적, 프랑스 과거 보너스 승점을 보강하고 근거로 가르지 못한 동률은 공동 순위로 남깁니다. 기사 상세에는 원문 발행 시각·시간대와 수정 메타데이터를 표시합니다. 발행 당시 초판 전체가 확보된 것은 아닙니다.

고전 프로필은 검색 색인과 32개 상세 조각으로 나눴습니다. 확인된 실제 출전과 벤치·대회 등록을 구분하며 연도만 알려진 소속을 정확한 이적일로 바꾸지 않습니다. 선수별 이적 보도 흐름은 1,378개 선수 묶음, 중복 선수 언급을 제외한 기사 5,708개이며 현재 날짜 이후의 보도와 진위 판정은 숨깁니다. 당일 신문과 별도입니다.

추가 원본을 다시 수집하려면 다음 순서를 사용합니다. 원문 CSV·API 체크포인트는 git에서 제외되며 공개 API의 접근과 현재 스키마에 따라 결과가 달라질 수 있습니다. 데이터 원문·이용 조건과 로컬 입력 해시는 `data/match-inputs.json`, `data/match-input-receipt.json`에 있습니다.

```sh
python scripts/fetch_match_inputs.py
python scripts/fetch_classic_careers.py
python scripts/fetch_uefa_archive.py
python scripts/build_match_archive.py
python scripts/enrich_worldcup_archive.py
python scripts/enrich_uefa_archive.py
python scripts/build_uefa_cups.py
python scripts/build_verified_shootouts.py
python scripts/shard_classic_players.py
python scripts/build_crest_history.py
python scripts/add_korean_editorials.py
python scripts/build_editorial_news.py
python scripts/build_press_archive.py
python scripts/build_news_quality.py
python scripts/build_transfer_threads.py
node tests/verify-expansion.cjs
node tests/verify-season-recaps.cjs
```

초기 시대 신문 초판, 모든 나라의 제재 결정과 엠블럼은 아직 공백이 있습니다. 무엇을 구현했고 무엇이 미확보인지 [DATA_COVERAGE.md](DATA_COVERAGE.md)에 명시했습니다. 수록량을 전체 역사 완성이나 원문 초판 확보로 해석하지 않습니다.

## 시즌 회고 타임라인

새 ‘시즌 회고’ 탭과 ‘그날의 축구’의 회고 바로가기를 추가했습니다. 72개 기간에 7,142개 출처 연결 항목을 모았습니다. 리그·유럽대항전·월드컵·유로 우승, 주요 이적과 은퇴 관련 보도, 득점·도움 선두, 발롱도르, 사건을 날짜순으로 필터·검색하고 한 번에 모두 펼치거나 인쇄할 수 있습니다.

기본은 7월~다음 해 6월이며 이어지는 여름 월드컵·유로도 선택적으로 포함합니다. 순연된 2019/20 챔피언스리그의 2020년 8월 결승은 원래 시즌에 남깁니다. ‘회고 마지막 기록까지 날짜 이동’은 선택한 회고를 유지하며 종료 이후로 이동합니다. 선택한 날짜 이후 사건·우승 팀·수상자는 화면과 집계에서 숨깁니다.

리그 우승은 원자료의 시즌·국가·시대별 리그 단계를 확인하고 실제 참가 팀과 대조했습니다. 정규리그는 최다 승점 팀 집합과도 대조합니다. 영국 First/Second Division은 1992년 전후의 소속 단계가 바뀌는 것을 반영합니다. 북키프로스의 동명 리그, 실제 참가하지 않은 팀, 상충하는 우승 주장 등은 제외하고 `dist/replay/season-recaps/quality.json`에 남겼습니다. 미해결 이름이어서 빠진 유효 기록도 있을 수 있습니다.

당시 참가 팀 이름을 표시하고 현재 구단명으로 덮어쓰지 않습니다. 공식 Playmaker 수상과 제공자 도움 집계는 구분합니다. 발롱도르는 평가 연도와 실제 시상 날짜를 구분하며, 연도만 확보한 기록에 정확한 날짜를 만들지 않습니다. 은퇴·이적 등록일, 당시 발표 보도, 후대 사건 정리도 각각 표시합니다.

한글 정규화 과정의 팀 이름 충돌을 수정했습니다. 전북·서울 등 서로 다른 팀의 식별자가 보존되며, 전북의 2016년 9점 삭감은 전북에만 적용됩니다. 엠블럼 미수록 한국 팀에 무관한 구단 문장이 붙지 않도록 빈 키를 제거했습니다.

```sh
python scripts/repair_korean_identities.py
python scripts/fetch_recap_evidence.py
python scripts/build_season_recaps.py
node tests/verify-season-recaps.cjs
```

회고는 시즌별 조각만 불러옵니다. 가장 큰 시즌도 약 183KiB이며 전체 원본이나 모든 시즌을 한 번에 로드하지 않습니다. 모든 나라·시대의 개인상·은퇴 기록이 완전한 것은 아니므로 미확보 항목은 추정으로 채우지 않습니다.

2022년부터 시즌 평가로 바뀐 발롱도르는 해당 평가 시즌에 연결하되 실제 발표일을 유지합니다. 예를 들어 2022년 벤제마 수상은 2021/22 회고에 2022-10-17 기록으로, 2026년 케인 수상은 2025/26 회고에 2026-10-26 기록으로 표시합니다. 이 날짜 전에는 수상자와 해당 집계를 숨깁니다.

선택 브라우저 검증은 Playwright와 Chromium이 있는 개발 환경에서 `tests/browser-core-flows.cjs`, `tests/browser-season-recap.cjs`로 실행할 수 있습니다. `FOOTBALL_QA_BASE_URL`은 로컬 서버 주소, `CHROMIUM_PATH`는 설치된 브라우저 경로입니다. 앱 실행에는 이 도구들이 필요하지 않습니다.
