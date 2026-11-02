# Validation — 1 November 2026

Environment: macOS, Python 3.12, Streamlit 1.66.1, pandas 2.3.3, yfinance 1.7.0. Exact installed versions are in requirements-tested.txt.

## Passed

- Installed dependencies in a clean virtual environment.
- Six automated tests passed (`python -m unittest discover -s tests -v`). They cover SQLite watchlist persistence and input validation; cache hits, stale fallback and missing data; headline scoring/negation; RSS partial failure and deduplication; missing-data labels in the Markdown packet; all four Streamlit workspaces and brief generation with offline fixtures.
- Started the real server bound to `127.0.0.1:8517`; HTTP `/_stcore/health` returned `200` / `ok`.
- Live Yahoo search for Apple returned five results.
- Live AAPL one-month daily price request returned 23 observations.
- Live AAPL fundamentals request returned a 17-field snapshot.
- Live FRED DGS10 CSV request returned 2,707 observations since 2016.
- Live combined AAPL RSS request returned headlines; individual feed status checked separately below.

Python's system certificate store initially rejected RSS/FRED HTTPS connections. Fixed by explicitly using certifi's CA bundle, retaining certificate verification. All offline tests passed again after that change.

## Scope of verification

UI smoke tests execute actual Streamlit code with provider fixtures; they are not browser-based visual checks. Live adapters were checked separately. Provider responses can differ on another network or day. The server health response alone does not verify all data providers. No historical accuracy, provider licensing compliance for redistribution, or investment performance is claimed. No live market data, watchlist database or installed virtual environment is included in the archive.

RSS check detail: {'Google News RSS': 25, 'Yahoo Finance RSS': 16}. Feed errors: []
