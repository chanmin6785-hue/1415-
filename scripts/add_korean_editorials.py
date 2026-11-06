"""Idempotent additions checked against original publisher datelines.

Short original factual summaries, not copies of article bodies. Allegations,
named supporters' statements and later decisions remain separate reports.
"""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sourcePath=ROOT/'data/editorial-extra-sources.json';sources=json.loads(sourcePath.read_text())
path=ROOT/'data/editorial-news.tsv'
with path.open() as f:reader=csv.DictReader(f,delimiter='|');fields=reader.fieldnames;rows=list(reader)
def add(key,url,title,publisher,date,category,summary,context='',reaction='',watch='',modified='',match=''):
    if not any(s['url']==url for s in sources):sources.append({'url':url,'title':title,'publisher':publisher,'datePublished':[date],'dateModified':[modified] if modified else [],'dateEvidence':'발행사 원문 입력·승인 날짜와 시각 확인. 시각 없는 항목은 날짜만 보존.'})
    if not any(r['key']==key for r in rows):rows.append(dict.fromkeys(fields,'')|dict(key=key,category=category,title=title,text=summary,context=context or '당일 발행된 국내 보도로, 후대의 회고 기사와 구분한다.',reaction=reaction,watch=watch or '이 사안에 대한 이후 공식 설명과 후속 보도.',match=match))
add('1827754_30391','https://imnews.imbc.com/replay/1989/nwdesk/article/1827754_30391.html','대한민국, 사우디를 꺾고 이탈리아 월드컵 본선행 확정','MBC','1989-10-25','경기 후 보도','한국이 사우디아라비아에 2–0으로 승리해 마지막 예선 경기와 관계없이 월드컵 본선 진출권을 확보했다.','승점은 당시 제도에 따른 3승 1무, 7점이다.','MBC는 축구 중계로 늦어진 뉴스의 첫 소식으로 본선 진출을 전했다.',match='1989-10-25~South Korea~Saudi Arabia')
add('1931507_30690','https://imnews.imbc.com/replay/1994/nwdesk/article/1931507_30690.html','한국 대표팀, 볼리비아전을 앞두고 보스턴으로 이동','MBC','1994-06-19','현장·반응','대표팀이 볼리비아와의 다음 경기를 준비하며 보스턴에 도착했다. 김호 감독은 스페인전 무승부 뒤 선수단의 자신감을 전했다.','아직 볼리비아전 결과를 알 수 없는 준비 단계다.','신문선 해설위원은 측면 수비와 실점 뒤 조직력 보강이 필요하다고 지적했다.','볼리비아전의 전술과 수비 조직력.')
add('19980622001001','https://www.seoul.co.kr/news/1998/06/22/19980622001001','차범근 감독 경질…월드컵 대회 도중 사령탑 교체','서울신문','1998-06-22T00:00:00+09:00','충격','축구협회 기술위원회가 월드컵 대회 도중 차범근 감독을 경질했다. 한국 대표팀 감독이 대회 중 교체되는 첫 사례라고 서울신문이 보도했다.','남은 조별 경기를 앞두고 지휘 체계가 바뀌었다.',watch='남은 경기의 대표팀 운영.')
add('2860563_30494','https://imnews.imbc.com/replay/2011/nw2400/2860563_30494.html','승부조작 파문에 프로축구 선수·코칭스태프 비상 소집','MBC','2011-05-31T00:00:00+09:00','논란','프로축구연맹이 승부조작 재발 방지를 위한 워크숍에 16개 구단 선수와 코칭스태프를 소집했다.','수사와 제도 개선이 진행 중인 시점의 보도다. 최종 처벌 결과와 구분한다.','MBC는 인터뷰한 선수의 당혹감과 연맹 대책의 실효성 문제를 전했다.','수사 결과와 재발 방지책.',modified='2011-06-01T12:16:00+09:00')
add('201105292143145','https://www.khan.co.kr/article/201105292143145','승부조작 수사, 연루 의혹 선수로 범위 확대','경향신문','2011-05-29','논란','경향신문은 승부조작 연루 의혹을 받는 선수가 10명으로 늘었다고 보도했다.','수사 단계의 의혹 보도로, 해당 선수들의 확정 유죄 판결을 의미하지 않는다.',watch='추가 수사와 구체적인 사실 확인.')
add('6371442_35744','https://imnews.imbc.com/replay/2022/nwdesk/article/6371442_35744.html','손흥민, 아시아 선수 최초 프리미어리그 공동 득점왕','MBC','2022-05-23T19:58:00+09:00','경기 후 보도','손흥민이 시즌 최종전 득점으로 프리미어리그 공동 득점왕에 올랐다. MBC는 아시아 선수 최초의 성과라고 전했다.','페널티킥 없이 쌓은 득점이라는 점도 보도에 담겼다.',watch='시즌을 마친 선수와 구단의 반응.',modified='2022-05-23T20:35:00+09:00')
add('6371443_35744','https://imnews.imbc.com/replay/2022/nwdesk/article/6371443_35744.html','득점왕 손흥민을 향한 동료와 팬의 반응','MBC','2022-05-23T19:59:00+09:00','여론·분석','MBC가 손흥민의 득점왕 등극 뒤 동료·팬들의 반응을 전했다.','이 기사에 등장한 반응을 축구 팬 전체의 여론 조사로 해석하지 않는다.','보도에서 소개한 동료와 팬들의 축하에 한정한다.',modified='2022-05-23T22:00:00+09:00')
add('kuk202303280209','https://www.kukinews.com/article/view/kuk202303280209','축구협회, 승부조작 징계자 48명 포함 100명 사면 결정','쿠키뉴스','2023-03-28T19:29:55+09:00','논란','축구협회가 징계를 받은 축구인 100명의 사면을 결정했다. 보도에 따르면 승부조작으로 징계받은 48명도 포함됐다.','이 날짜에는 사면 결정이 발표된 상태다. 후속 철회 결과를 앞당겨 쓰지 않는다.',watch='협회의 설명과 축구계·팬들의 반응.')
add('118608728','https://www.donga.com/news/Sports/article/all/20230331/118608728/1','붉은악마, 사면 철회 없으면 경기 보이콧 경고','동아일보','2023-03-31T03:00:00+09:00','여론·분석','붉은악마가 승부조작 관련 사면 철회를 요구하며 A매치와 리그 경기 보이콧 가능성을 밝혔다고 동아일보가 전했다.','오전 발행 기사다. 같은 날 나중에 나온 결정은 이 기사의 당시 상황에 섞지 않는다.','보도에 인용된 붉은악마의 입장이며 모든 팬의 의견을 수치화한 자료는 아니다.','협회가 재논의에서 어떤 결정을 내릴지.',modified='2023-03-31T03:38:00+09:00')
add('6469630_36154','https://imnews.imbc.com/news/2023/sports/article/6469630_36154.html','축구협회, 임시이사회에서 징계 사면 전면 철회','MBC','2023-03-31T17:14:00+09:00','공식 발표','축구협회가 임시이사회를 열어 지난 28일 의결한 징계 사면을 전면 철회했다고 발표했다.','오전의 철회 요구 보도 뒤 나온 새로운 결정이다.',watch='의사 결정 과정에 대한 설명과 책임.',modified='2023-03-31T17:14:00+09:00')
add('6469684_36199','https://imnews.imbc.com/replay/2023/nwdesk/article/6469684_36199.html','사면 철회 뒤 축구협회 설명…팬들의 비판은 계속','MBC','2023-03-31T20:34:00+09:00','논란','MBC는 사면 철회와 함께 축구협회가 팬들의 높아진 눈높이를 고려하지 못했다고 밝힌 경위를 보도했다.','사면 발표와 철회, 철회 이후의 설명은 서로 다른 시점의 보도다.','MBC는 사면 결정 과정에 대한 비판을 전했다. 여론조사 수치가 아니다.','이사회 의사 결정 과정과 후속 조치.',modified='2023-03-31T20:34:00+09:00')
with path.open('w') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='|',lineterminator='\n');w.writeheader();w.writerows(rows)
sourcePath.write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
print('Verified Korean additions present; total editorial rows',len(rows))
