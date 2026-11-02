# V2 validation — 1 November 2026

Environment: macOS, Python 3.12, Streamlit 1.66.1, pandas 2.3.3, yfinance 1.7.0. No new dependencies added for V2.

- Seven automated tests passed, including all Ticker functions, Macro, annual/quarterly switching, expanded brief export, label and percent formatting, statement ordering and missing values, plus existing watchlist/cache/news tests.
- Real Streamlit server started on loopback port 8518; health endpoint returned `ok`.
- Live AAPL financial statements: annual income/cashflow/balance returned 4 periods each; quarterly income returned 5 periods, cashflow and balance returned 6 periods each, with some missing fields explicitly retained.
- Browser review confirmed the new theme, two-level navigation and live financial tables, including revenue, EPS and CapEx.
- Archive excludes runtime databases, Python caches and virtual environments.

Provider history depth and completeness vary. Live checks establish availability during validation, not accounting accuracy. No financial statement values were reconciled to SEC filings. Free-data and licensing limitations from V1 remain applicable.
