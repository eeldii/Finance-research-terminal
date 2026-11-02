# V2 — what changed and how to upgrade

- Dense terminal appearance: black background, amber headings and price line, blue information accents, monospace type, square controls, compact spacing and bordered panels.
- Two top-level workspaces: **Ticker** and **Macro**. Ticker contains **Overview**, **Financials**, **News** and **AI brief**. Overview places the price chart beside the fundamental snapshot.
- Clear labels including **Trailing PE**, **Return On Equity ROE**, **Revenue (TTM)** and **Trailing EPS (TTM)**. Percent ratios are displayed as percentages and valuation multiples as `x`.
- Expanded snapshot metrics: revenue, net income, EBITDA, EPS, cash flow, cash, debt, margins and growth where available.
- New **Financials** function: annual/quarterly income statement, cash flow and balance sheet, with fiscal period-end columns. Includes revenue, basic/diluted EPS, earnings/net income, EBITDA, CapEx, free cash flow, debt, assets and equity.
- Statement display amounts and share counts use millions; EPS remains per share. CSV exports and AI packets use raw provider units. CapEx signs are preserved. Missing figures are explicitly unavailable. No estimates are substituted for missing statements.
- AI brief now includes both annual and quarterly statements. Each statement has independent caching/error reporting; one missing statement does not prevent the others from loading. Financial statements cache for 24 hours.

## Run on Mac

Extract this V2 archive and open Terminal in the extracted `research-terminal-v2` folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. Stop a running V1 first with Control+C in its Terminal window. To keep the V1 watchlist/cache, copy its `data` folder into the extracted V2 folder while both apps are stopped. V2 uses new keys for expanded fundamentals and statements. Do not copy `.venv`; create the new environment above.

Alternatively, replace `app.py`, `core.py`, `requirements.txt` and `.streamlit/config.toml` in your existing installation with V2's copies while stopped, run `python -m pip install -r requirements.txt` in its activated environment and restart. Keep the existing `data` folder.

## Data notes

Yahoo statements are normalized provider data, not independently validated company filings. Frequency, depth and field availability differ by ticker; funds/indices may have no statements. Quarterly cash flow and balance-sheet histories may contain missing periods. No TTM statement is computed by summing potentially incomplete quarters. Snapshot and statement periods can differ. Current source checks: [income statement API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.get_income_stmt.html), [cash flow API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.get_cashflow.html).

See README.md for source/licensing limitations and full setup instructions. V1 is retained separately.
