# V4 — Mac setup and upgrade

1. Stop the previous version with **Control+C** in its Terminal window.
2. Extract `research-terminal-v4.zip`. In Terminal, type `cd `, drag the extracted `research-terminal-v4` folder from Finder into Terminal and press Return.
3. Run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. On later launches, enter the same folder, activate `.venv` and run the last command. Python 3.12 is validated.

To preserve your watchlist/cache, copy the previous version's `data` folder into V4 while both apps are stopped. The SQLite watchlist format is unchanged. A new fundamentals cache key retrieves company descriptions; existing prices and statements can be reused. Do not copy `.venv`.

For an existing repository, replace the source/config/test/documentation files with the V4 archive contents, including the new `report.py`. Keep your existing `data` folder locally and out of Git. No new dependency was added in V4; reinstalling requirements is safe if needed.

## New in V4

- Workspace is the first control, before ticker search. Macro works independently of ticker input.
- Overview, profile, historical changes, price graph, fundamentals, financials and individual statements, news, watchlist, world map, yield table, commodities/individual commodity charts and economic indicators have open/close controls.
- Major section titles are larger and collapsible section bars are visually distinct.
- AI brief now builds a readable instrument research document, downloadable as Markdown and standalone HTML. Open HTML in a browser to read or use Print → Save as PDF.
- Report: timestamp/ticker/sources, provider company description, recent adjusted prices, market-cap snapshot, ratios, up to four recent annual/quarterly financial periods with growth columns, and up to 10 recent headlines with sentiment/source links. Headline catalyst keyword matches are marked as a heuristic, not an assessment of materiality. Historical market caps are not invented.
- US 10Y removed from the economic-series menu; it remains in the sovereign-rate table/map. Economic-series options use a compact two-column checkbox menu.
- Sovereign coverage expanded to 16 countries: added Spain, Netherlands, Switzerland, Sweden, Norway, Finland, New Zealand and South Korea.
- Mean headline score explanation is collapsed by default, with separate meaning, calculation, example and limits sections.

See README.md for definitions/rights and VALIDATION.md for checks performed. COMMIT_MESSAGE.txt contains the release commit message in past tense.
