<img width="1098" height="751" alt="image" src="https://github.com/user-attachments/assets/019635a8-b527-4a80-9473-99324e5ce608" /># AI Research Terminal

A free, local research terminal for exploring market prices, company financials, macroeconomic data and news.

Built with **Python, Streamlit and SQLite**, with a terminal-style interface inspired by Godel and Bloomberg. Designed for personal research without paid data subscriptions or AI API calls.

<img width="1137" height="893" alt="image" src="https://github.com/user-attachments/assets/1813b7f4-a4af-491e-aeb3-ebaf7d0188d1" />

<img width="1273" height="906" alt="image" src="https://github.com/user-attachments/assets/9851450f-3815-419d-9de1-11cfefffeac3" />

## Features

### Instrument research

- Search by company name or ticker.
- View daily adjusted price history with fixed chart ranges.
- Compare cumulative price changes over **1M, 3M, 6M, 1Y, 3Y, 5Y and 10Y**.
- Explore fundamentals, valuation ratios, margins and growth metrics.
- Save instruments to a persistent local watchlist.
- Download price data as CSV.

### Financial statements

View annual and quarterly:

- **Income statements:** revenue, gross profit, operating income, earnings, EBITDA and EPS.
- **Cash flow statements:** operating cash flow, CapEx, free cash flow, dividends and share repurchases.
- **Balance sheets:** cash, assets, liabilities, equity and debt.

Tables include fiscal-quarter labels, YoY and QoQ percentage changes, selectable monetary scales and CSV exports.

<img width="1098" height="751" alt="image" src="https://github.com/user-attachments/assets/106d42b7-d7c1-4ecc-a57d-39f2b4343570" />

### Global macro

- World map displaying available government bond yields.
- Monthly 10-year government benchmark yields for the United States, Canada, Germany, France, the United Kingdom, Italy, Japan and Australia.
- Commodity futures charts covering oil, precious metals, copper, natural gas, corn and wheat.
- FRED economic indicators, including interest rates, unemployment, CPI and real GDP.

### News and sentiment

- Public RSS headlines from Google News and Yahoo Finance.
- Headline deduplication and source links.
- Lightweight local sentiment scoring with an explanation of how scores are calculated.

<img width="1198" height="724" alt="image" src="https://github.com/user-attachments/assets/43d8771d-8a96-4645-a131-b790977ff332" />

### AI research packets

Generate a Markdown research packet containing prices, historical changes, fundamentals, financial statements, headlines and core macroeconomic data.

Upload the packet manually to ChatGPT for further analysis. The app does not call an AI API or require an AI subscription to run.

## Quick start

### Requirements

- **Python 3.12** — the validated version.
- Internet access to retrieve fresh data.
- A writable local project folder.

### macOS / Linux

Open a terminal in the project folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If your `python3` command already uses Python 3.12, you can use it instead of `python3.12`.

### Windows

Open PowerShell in the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://127.0.0.1:8501** in your browser.

Stop the app with **Control+C** in the terminal.

### Starting again

On macOS / Linux, enter the project folder and run:

```sh
source .venv/bin/activate
python -m streamlit run app.py
```

On Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Using the app

1. Enter a ticker in the top bar, or search for a company and open a matching result.
2. Use **Ticker → Overview** to inspect prices, historical changes and fundamentals.
3. Open **Financials** for annual or quarterly statements and growth comparisons.
4. Open **News** for headlines and sentiment scores.
5. Save instruments using the watchlist on the right.
6. Switch to **Macro** for government yields, the world map, commodities and economic indicators.
7. Use **AI brief** to generate and download a Markdown research packet.

Yahoo ticker conventions apply. Examples include `AAPL`, `MSFT`, `BRK-B`, `NOVO-B.CO` and `^GSPC`.

## Data sources

| Data | Source |
|---|---|
| Instrument search and prices | Yahoo Finance via yfinance |
| Fundamentals and financial statements | Yahoo Finance via yfinance |
| Economic indicators | FRED |
| International government yields | OECD series accessed through FRED |
| Commodity futures histories | Yahoo Finance via yfinance |
| News headlines | Google News RSS and Yahoo Finance RSS |
| World map geometry | Natural Earth |

No API keys are required for the current implementation.

## Understanding the data

### Prices and historical changes

Historical prices use provider split/dividend adjustments. Percentage changes are cumulative adjusted-close changes, not annualized returns.

Each horizon uses a baseline trading close on or before its target calendar date. Insufficient history or a missing nearby baseline produces an unavailable result.

Charts have fixed time ranges. Change the range using the selector beside
