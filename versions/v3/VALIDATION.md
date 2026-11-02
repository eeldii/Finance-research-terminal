# V3 validation — 1 November 2026

Environment: macOS, Python 3.12, Streamlit 1.66.1, pandas 2.3.3, Altair 6.3.0, yfinance 1.7.0. Exact installed versions are recorded in requirements-tested.txt.

## Passed

- 14 automated tests passed (`python -m unittest discover -s tests -v`). Coverage includes all Ticker functions, annual/quarterly switching, brief generation, Macro, empty country/commodity selections, missing-provider behavior, right-rail watchlist actions, SQLite/cache fallback, input validation, RSS/scoring, fiscal labels, negative/zero growth baselines, missing financial periods, scaled currency units, price horizon dates, fixed chart domain and absence of pan/zoom bindings, and the bundled map with no live data.
- Real Streamlit server started on loopback port 8519. Health endpoint returned HTTP 200 / `ok`.
- Live AAPL maximum-history request supplied all seven horizon changes; latest observed date was shown explicitly in the browser.
- All eight sovereign OECD/FRED series returned data. Most latest observations were September 2026; Italy's was August 2026, demonstrating the need for per-country dates. Each row retains retrieval time, source link and failure/stale status.
- Live default commodity requests returned WTI (6,576 observations), gold (6,568) and copper (6,572), ending 30 October 2026. The other five selectable contracts were configured with provider tickers and units but were not live-tested during this release.
- Browser review confirmed top ticker bar, right watchlist, removal of left sidebar, non-blue terminal theme, price horizon table, fixed-range chart and full-width fundamentals. Macro world map, eight-country table and commodity chart sections rendered with real provider data. Link coloring was adjusted to orange after visual review found a default blue link style.
- Bundled Natural Earth geometry contains 177 features and needs no remote map service at runtime.
- Archive integrity checked; runtime database, Python caches and virtual environments excluded.

## Limits

Live checks establish endpoint availability during validation, not data accuracy or future service availability. Financial quarter/growth rules were checked with fixtures; normalized financial figures were not reconciled to original filings. Fiscal quarter naming can be ambiguous around unusual fiscal calendar changes and is explicitly described as inferred. Automated chart checks validate the fixed-domain specification without interactive scale bindings; browser review verified rendering. No live tanker/AIS data is provided. Government yields are monthly observations, not live tradable prices. Commodity histories can contain contract-roll discontinuities. Current source rights and restrictions remain applicable; see README.md.
