# Research Terminal — V5

Free local personal research with Python, Streamlit, SQLite, yfinance and public FRED/RSS data. No paid API keys or AI calls. Internet is required for fresh data. See [UPGRADE.md](UPGRADE.md) for a short Mac walkthrough and preserving an existing watchlist.

## Start on Mac / Linux

Install Python 3.12, extract the archive, open Terminal in the `research-terminal-v5` folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Visit http://127.0.0.1:8501. Stop with Control+C. Launch from the project folder so its local-only configuration is loaded. The app has no authentication; do not publish it to the internet. If the port is occupied, stop the other copy or add `--server.port 8502`.

## Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## V5 workspace

Workspace is the first control on the page. Major sections retain open/close controls. Headings use sentence case, and duplicate labels and heavy terminal decorations have been removed. V5 consolidates the minimal interface, dark mode and toolbar alignment updates: charcoal backgrounds, soft white text, quiet section headers and a muted warm accent. Charts, tables and maps share the dark theme, with readable green/red changes. Prior terminal styling is retained in earlier version snapshots.

- **Top bar:** enter a ticker, or search a company and click Open match. Refresh view re-fetches that section's sources.
- **Top-right Watchlist:** save, open and remove instruments on either workspace. Opening a saved instrument switches to Ticker. Watchlists persist in SQLite.
- **Ticker → Overview:** adjusted daily close, last-session change, volume, trading date and cumulative changes for 1M, 3M, 6M, 1Y, 3Y, 5Y and 10Y. Graph history sits directly above the chart. The time domain is fixed and no pan/zoom scale bindings are used. Fundamentals occupy the full content width below the chart.
- **Ticker → Financials:** annual and quarterly income statements, cash flow and balance sheets. Select billions or millions; every monetary row names its reporting currency and scale. EPS remains currency/share and share counts remain millions. Fiscal quarter labels and YoY/QoQ changes are explained below. Download display CSVs with changes or raw-unit CSVs.
- **Ticker → News:** public Google News/Yahoo RSS headlines with source links, simple lexicon scores, and an explanation of the equal-weighted mean.
- **Ticker → AI brief:** readable instrument research document, exported as Markdown or standalone HTML. Includes generation date/ticker/sources, provider company description, recent prices and seven horizon changes, current market-cap snapshot, key fundamentals, up to four recent annual/quarterly statement periods with growth columns, and up to 10 recent headlines with sentiment/source links. Upload Markdown manually to ChatGPT or read/print HTML in a browser. Macro/commodities are separate monitors and are not included in this instrument report. The report does not run an AI model.
- **Macro:** bundled world map with yield markers, 16-country yield table, commodity futures charts and a compact checkbox menu for economic indicators. US 10Y is removed from the economic menu and retained in the sovereign monitor. Country selection controls map and table. Major macro sections and individual charts can be closed. Empty selections work without errors.

## Price changes and chart behavior

A horizon is measured back from the latest available trading date, using calendar-month offsets (1Y = 12 months). Baseline is the last close on or before that target. A baseline more than seven calendar days early, absent history, or a nonpositive denominator yields Unavailable. Actual baseline/latest dates are visible under the explanatory expander. Short-history instruments therefore do not get invented 10-year returns.

Prices use yfinance `auto_adjust=True`: historical OHLC reflects provider split/dividend adjustments. Changes are cumulative adjusted-close changes, not annualized returns or guarantees of realized investor returns. Chart windows also anchor to the latest trading date, not the computer's clock. One cached maximum-history request supports all ranges and the full-history CSV. Initial loads may take longer than V2. Charts draw only the selected window; wheel scrolling scrolls the page and cannot move the time domain. Very illiquid/delisted instruments can have old last dates: always read the date.

## Financial periods, quarter names and growth

Statements keep their provider period-end dates; these are not filing/release dates. Quarterly labels represent **fiscal** quarters. They are inferred by matching the quarter end to actual annual income-statement year ends, allowing up to 40 days around expected three-month intervals for 52/53-week calendars. This supports September year ends such as Apple's (December is Q1). If no annual reference is available, the label says Q unavailable. Fiscal year-end changes and unusual reporting calendars can still require manual verification; no period values are synthesized.

Annual tables show YoY changes. Quarterly tables show YoY plus QoQ, matching available date intervals around one year/one quarter. Missing matching periods and zero denominators show a dash. Formula is `(current − prior) / abs(prior) × 100`; a negative prior loss can therefore show positive improvement. This is explicitly different from conventional growth with a positive base. CapEx retains its provider cash-outflow sign, typically negative; larger expenditure can produce a negative change. Balance-sheet changes compare stocks, not revenue growth. Tables scroll horizontally; raw and display CSV downloads are separate. Some providers return trailing empty cells or insufficient history for YoY; missing values remain unknown.

Snapshot amounts scale automatically to billions or millions with a currency. Market capitalization uses quote currency; statement amounts and other financial snapshots use reporting currency. Margins/ROE/ROA and growth snapshot fractions are displayed as percentages, and P/E/P/B as multiples. Debt/equity and dividend yield retain provider-defined units and must be checked at source. Retrieval time is not the accounting date. Snapshot and statement periods can differ.

## World map and government yields

Countries: United States, Canada, Germany, France, United Kingdom, Italy, Japan, Australia, Spain, Netherlands, Switzerland, Sweden, Norway, Finland, New Zealand and South Korea. All use **monthly OECD 10-year main/benchmark government yields via FRED**, percent, not seasonally adjusted (`IRLTLT01{country code}M156N`). These are not live quotes, not a full maturity curve, and not individual bond prices. Latest observation dates can differ by country. MoM basis-point change requires the preceding calendar month (100 bp = 1 percentage point); gaps are not interpolated.

Orange marker shade and size encode yields; markers show country reference points and expose yield/date/cache status on hover. Countries with unavailable data have no marker and an unavailable table row. Cached fallback status/errors are retained. The map outline is bundled Natural Earth public-domain geometry and works offline. See assets/NOTICE.md. Boundaries are generalized and illustrative.

No tanker/AIS positions are provided. V5's map visualizes available sovereign data rather than simulated vessel movements.

FRED series contain source links/notes, including OECD copyright and attribution requirements. OECD data should be cited as OECD, Main Economic Indicators, accessed via FRED, with series ID and retrieval date; read current per-series notices before sharing exports. Publicly accessible does not mean unrestricted redistribution.

## Commodity futures

WTI crude (CL=F), Brent crude (BZ=F), gold (GC=F), silver (SI=F), copper (HG=F), natural gas (NG=F), corn (ZC=F) and wheat (ZW=F). Select which charts to load; defaults are WTI, gold and copper. Prices are Yahoo front-contract futures histories, not spot prices. USD/barrel, USD/troy ounce, USD/lb, USD/MMBtu or **US cents/bushel** is explicitly shown. Contracts roll; price discontinuities and changing contract metadata make this unsuitable as a futures strategy backtest. No roll-adjustment guarantee, live market feed or order execution is included.

## News sentiment definition

Only headlines are analyzed. The built-in dictionary counts positive words minus negative words, with a three-word negation window, divides by three and caps scores at −1/+1. The mean is the arithmetic average across displayed deduplicated headlines, equally weighted without recency/relevance adjustment. Zero can mean no words matched or balanced words. It is not the fraction of positive articles, model confidence or predicted price change. Ticker ambiguity, repeated stories, sarcasm and lack of article context can distort it. Feed order is retained; no article body is scraped and no paywall is bypassed.

## Local storage and dependencies

Five direct dependencies: Streamlit, pandas, yfinance, certifi and Altair (already a Streamlit dependency, now explicitly declared for fixed-range charts). All other persistence, HTTP/XML and scoring code uses Python's standard library. `requirements-tested.txt` records the exact validated environment; Python 3.12 is the validated target. No model downloads or API keys. V5 adds no dependencies.

`data/terminal.sqlite3` stores watchlist and JSON response cache with UTC timestamps. Override path using `TERMINAL_DB`. Prices/news: 30 minutes; fundamentals/statements/search: 24 hours; FRED: 6 hours. Refresh bypasses current-view cache. Provider failure returns stale cached payload with its original time/status/error, or unavailable with no cache. Individual statements/series are independently cached. Delete the database while stopped to clear cache and watchlist. There is no background scheduler or automatic streaming.

Search/ticker requests and network metadata go to Yahoo/Google/FRED. Data stays locally unless you download/share/upload it. The app never sends packets to an LLM. Retrieved text is untrusted source material in the brief prompt; verify AI output.

## Free-source reliability and rights

Yahoo/yfinance is unofficial and can throttle, change fields, block requests or stop working. Its project states research/educational intent and Yahoo personal-use restrictions. Prices can be delayed; fundamentals and normalized statements are not independently reconciled to SEC filings. Some instruments have no fundamentals/statements. Verify important figures with original filings/releases.

FRED public CSV graph downloads require no API key but can change/fail, have release lags and revised history. This is not a point-in-time backtesting database. Some series, especially OECD content, have third-party copyright restrictions. News headlines are also copyright material. Personal access does not automatically permit redistribution, public hosting or upload to another service: check current source terms and notices before sharing. This app is a research aid, not investment advice.

## Checks

```sh
python -m unittest discover -s tests -v
```

Tests cover persistence, input validation, cache/stale behavior, RSS handling, scoring, export, all workspaces, empty selections, missing providers, watchlist actions, date baselines, fixed chart specifications, fiscal quarter naming, growth calculations and currency scaling. See VALIDATION.md for actual results.

## Source links

- [yfinance usage notice](https://github.com/ranaroussi/yfinance)
- [FRED terms](https://fred.stlouisfed.org/legal/) and per-series links in the app
- [OECD Germany 10-year series](https://fred.stlouisfed.org/series/IRLTLT01DEM156N) / [Canada series](https://fred.stlouisfed.org/series/IRLTLT01CAM156N)
- [Yahoo commodity quote universe](https://finance.yahoo.com/markets/commodities/)
- [Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/)
- The terminal-inspired themes in V2–V4 are retained in their separate release snapshots; V5 uses a simplified dark design.

## Files

`app.py` interface; `core.py` providers/SQLite/analytics/export; `charts.py` fixed chart and map specifications; `report.py` readable Markdown and script-free HTML export; `assets/world.geojson` bundled geometry; `tests/` offline checks; `.streamlit/config.toml` theme/local server; `COMMIT_MESSAGE.txt` release commit text. Runtime database and virtual environments are excluded from the archive.

## Research document details

The document is assembled deterministically, not written by an LLM. Company descriptions are provider text. News is sorted by parseable publication timestamp, not verified financial materiality. Potential catalyst terms such as earnings, merger or guidance are highlighted as keyword matches only. The mean news score in the report refers to its included headlines, which may differ from the full News screen.

Market capitalization is a current snapshot with a retrieval timestamp. Historical market-cap series are not supplied, and the report does not estimate them from current shares. Recent price history uses the last 10 trading sessions, plus a one-month range and horizon changes. Price dates and retrieval times are distinct. Financial tables use named scale/currency units, fiscal labels and growth columns; missing/stale sources and errors remain explicit.

The HTML document embeds styling only and loads no external scripts or assets. It can contain links to provider/news pages, which are visited only when clicked. Review it before sharing. Macro sources are not fetched for the instrument report. Collapsing a section changes visibility; it does not guarantee its data request is skipped.

## Consolidated V5 update

This release combines the earlier minimal interface, dark-mode work, toolbar alignment and the latest layout changes into one V5 update. The Watchlist opens from the top-right corner on both pages. Search results render below the toolbar so inputs and action buttons stay aligned. Main content now uses the full available width.

The country yield table and its CSV contain only Country, 10Y yield (%), MoM (bp) and Observation. Retrieval timestamps, source links and errors are available under Sources and data notes instead of table columns. An explicit warning appears if selected countries have unavailable or stale fallback data.

Economic indicators includes a country selector. United States retains its five existing indicator options (no US 10Y). Canada, Germany, France, United Kingdom, Japan, Italy, Spain and Finland each add monthly seasonally adjusted unemployment-rate data from OECD via FRED (`LRHUTTTT{country code}M156S`). These eight added countries currently offer unemployment only, not a complete suite of GDP/inflation indicators. Native reporting lags and observation dates are shown; the series are not live estimates. Read each series' FRED source notes for attribution and usage rights.
