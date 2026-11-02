# Research Terminal — V1

A free, local personal research dashboard using Python, Streamlit and SQLite. No API keys, paid data subscription or AI API calls. Internet is required to retrieve fresh data.

## Start here

Install **Python 3.12 or 3.13** (3.12 is the validated version). Extract the archive, open a terminal in the `research-terminal` folder, then run:

### macOS / Linux
```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
If your `python3` is already 3.12/3.13, use it instead of `python3.12`.

### Windows (PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://127.0.0.1:8501 in your browser. Stop with Ctrl+C. Run commands from this project folder so the included local-only server configuration is used. Do not expose this unauthenticated app to the internet. Dependencies may need several minutes to download. Python 3.15 is not a validated target.

## Using the terminal

1. Search a company/ticker in the sidebar, select a result and click **Open selected ticker**. Alternatively type a Yahoo ticker directly (AAPL, MSFT, BRK-B, NOVO-B.CO, ^GSPC).
2. **Company:** choose a history period; inspect the adjusted daily price chart, OHLC/volume table, CSV download and provider fundamentals.
3. **Macro:** select among six FRED series. Each shows its units, native frequency, observation date and source link. CPI is an index level, GDP is an annualized level; neither is a growth rate.
4. **News:** headlines from Google News and Yahoo Finance RSS, deduplicated by normalized headline. Links lead to providers/aggregators, not necessarily the original publisher. Feed order is retained. No paywalls are bypassed or full articles copied.
5. **Watchlist:** Add/Remove saves tickers locally. Select a saved ticker and click Open saved.
6. **AI brief:** click Generate AI brief, then Download Markdown brief. Upload the `.md` file to your normal ChatGPT chat and request analysis. The app does not connect to ChatGPT or generate LLM analysis; the export includes a suggested prompt. Review sharing rights before upload.

The packet includes the last 60 daily observations from the selected period (not full price history), snapshot fundamentals, up to 50 deduplicated feed headlines with links/scores, and all six macro series since 2016. Failed sections remain explicit in the export. Packets can be large because macro observations are included.

## Data, caching and privacy

Only four direct dependencies: Streamlit, pandas, yfinance and certifi (HTTPS trust certificates); SQLite, HTTP, XML parsing and sentiment use Python's standard library. Streamlit supplies the charts, with no separate plotting dependency. Transitive dependencies are installed by pip. `requirements-tested.txt` records the exact validated environment; use it instead of requirements.txt to reproduce those versions on a compatible Python/platform.

`data/terminal.sqlite3` is created on first launch. It stores the watchlist and JSON response cache with UTC retrieval timestamps. Override its location with `TERMINAL_DB` if desired. Prices/news cache for 30 minutes, fundamentals/search for 24 hours, macro for 6 hours. Refresh current view bypasses its cache; refreshing the brief fetches all sections. Provider failures use any older cached payload with an explicit **STALE** warning and original retrieval time. No cache means an unavailable section, not simulated data. Partial RSS failure appears separately; a successful empty feed cannot guarantee comprehensive coverage. Old cache entries are retained; delete the database while stopped to clear all stored data and the watchlist.

No credentials are required. Queries/tickers and network metadata are sent to Yahoo, Google and FRED; data is stored on your computer. The app makes no LLM calls. A Markdown packet is only shared when you upload it elsewhere. Retrieved text is treated as untrusted material in the export prompt; still review AI responses critically.

## Reliability and licensing limits

- **Yahoo/yfinance:** unofficial access, intended for research/education, with Yahoo data subject to Yahoo's terms and personal-use restrictions. Availability, rate limits, exchanges, delays and field units vary. There is no service guarantee. Prices use `auto_adjust=True`, including historical OHLC adjustments for splits/dividends; this is not an executable live quote. No intraday feed, order routing or Bloomberg equivalence.
- **Fundamentals:** a Yahoo snapshot, not a complete SEC filing pipeline. Some instruments have no fundamentals. Fields may mix fiscal periods; retrieval time is not the accounting date. Quote and reporting currencies are displayed separately. Ratios are raw provider fields (P/E/P/B multiples, profit margin/ROE fractions; debt/equity and dividend yield must be checked at source). Missing means unknown, not zero. Verify against company filings before relying on them.
- **FRED:** a small set of public CSV graph downloads, no API key. This endpoint may change, block requests or return errors. Series have publication lags, mixed frequencies and revisions; this app is not a point-in-time backtesting database. Each chart links to the series for original-source attribution, notes and applicable copyright. FRED content is not universally public domain; third-party restrictions can apply. Review current terms and individual series notices, especially before sharing exports.
- **News:** public RSS coverage is incomplete and may fail or change without notice. Ticker-only matching is noisy. Headlines are copyright material; personal access does not grant republication rights. No scraping of article bodies is performed.
- **Sentiment:** intentionally lightweight, deterministic headline lexicon with a short negation window. Range -1 to +1, not probability/confidence. It misses sarcasm, context, entities and many finance words. Zero can mean no words matched. Mean scores are unweighted by time or relevance and are not trading signals.
- No paid-service promises or redistribution rights are included. Verify current provider terms before uploading packets to ChatGPT, publishing, commercializing or sharing data. This is a research aid, not financial advice.

Sources: [yfinance project and usage notice](https://github.com/ranaroussi/yfinance), [FRED download help](https://fred.stlouisfed.org/help/data/downloading/using-the-download-data-link/), [FRED terms](https://fred.stlouisfed.org/legal/), [Streamlit setup](https://docs.streamlit.io/get-started/installation/command-line).

## Checks and troubleshooting

```sh
python -m unittest discover -s tests -v
```

Tests use temporary databases and mocked provider data: cache/stale behavior, validation, persistence, scoring, RSS deduplication/partial failure, brief export and Streamlit page execution. See VALIDATION.md for actual checks and live-source results.

If a provider is unavailable, retry later, use a different ticker or use stale cache with caution. Frequent refreshes can trigger throttling. If port 8501 is occupied, add `--server.port 8502`. If installation fails, confirm Python 3.12/3.13 and upgrade pip (`python -m pip install --upgrade pip`). SQLite write errors usually mean the folder is read-only; move the extracted project to a writable folder. There is no background refresh service: data loads when a workspace is opened.

## Project layout

- `app.py`: Streamlit interface
- `core.py`: SQLite persistence, adapters, sentiment and Markdown export
- `tests/`: offline unit and UI smoke tests
- `.streamlit/config.toml`: loopback-only server and dark theme
- `data/`: runtime database (not included in the download)

Future improvements: SEC filing facts with fiscal-period provenance, configurable feed sources, explicit currency normalization, rate-limit backoff and optional local transformer sentiment. These are not part of V1.
