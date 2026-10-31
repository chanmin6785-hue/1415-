# Third-party data and assets

Application code is GPL-2.0-or-later; see GPL-2.0.txt for the license text. Source code and the data transformations are provided in this repository, without warranty.

- Historical league results: James P. Curley, engsoccerdata, GPL >= 2. https://github.com/jalapic/engsoccerdata . Normalized extracts are in `dist/replay/leagues/` for seasons before 2025. The extraction/filtering code is in `scripts/build_replay.py`.
- Recent league results (2025/26 and 2026/27): Football-Data.co.uk, https://www.football-data.co.uk/data.php . Attribution and any original usage conditions remain applicable. These files are not relicensed as application code.
- International results and goal events: Mart Jürisoo and contributors, CC0. https://github.com/martj42/international_results . See international-results-CC0.txt.
- World Cup data: OpenFootball and contributors, CC0. https://github.com/openfootball/worldcup.json . See openfootball-worldcup-CC0.txt.
- European club competition CSV: FootballCSV and contributors, CC0. https://github.com/footballcsv/europe-champions-league . See footballcsv-CC0.md.
- Recent European club competition TXT: OpenFootball and contributors, CC0. https://github.com/openfootball/champions-league .
- Editorial reports: brief original Korean summaries with source URLs in `dist/replay/stories.json`; original reporting remains the property of its respective publisher. Headlines in the app are written summaries, not purported verbatim quotations. Articles are not included in full.
- Stadium photograph: Unsplash photo identifier `photo-1522778119026-d647f0596c20`, used under the Unsplash license, https://unsplash.com/license . This is atmosphere imagery, not a photograph of any specified historical fixture.
- Web fonts: DM Sans and Noto Sans KR via Google Fonts. Font licenses are supplied by their respective upstream distributors. System fallback fonts work if remote font loading is unavailable.

Original factual data may contain errors. This application displays date-limited reconstructions and explicitly identifies limitations of standings, historical naming, and editorial coverage.

- K League 1/2 (2013 onward): Korean Professional Football League, public official schedule/result JSON at https://www.kleague.com/getScheduleList.do . Attribution retained; no private API credentials, full articles, copyrighted player photos or official crest assets redistributed.
- Curated factual career year/date summaries: individual source links in `dist/replay/journeys.json`. They do not claim individual match appearances.

- Player profiles, dated transfers and appearances: D. Caribou and transfermarkt-datasets contributors, CC0-1.0, https://github.com/dcaribou/transfermarkt-datasets ; public Kaggle mirror https://www.kaggle.com/datasets/davidcariboo/player-scores . Snapshot 2026-07-06, appearances through 2026-06-28. Selected, normalized extracts exclude profile-current clubs, current caps, valuations and player images. Player photos are not redistributed. See transfermarkt-datasets-CC0.txt.
