# V4 validation — 2 November 2026

Environment: macOS, Python 3.12, Streamlit 1.66.1, pandas 2.3.3, Altair 6.3.0, yfinance 1.7.0. V4 adds no dependencies.

## Passed

- 18 automated tests passed. Existing price, financial growth, fiscal calendar, cache, persistence, missing-data and map checks remain covered.
- Updated UI smoke tests executed all workspaces, confirmed Workspace is the first radio control, found the new section controls, generated the readable document, switched financial frequencies, exercised economic checkboxes and empty selections, and checked missing-provider behavior.
- New report tests checked business description, ticker/date/source information, scaled market cap, recent prices, financial values and growth columns, publication-time news ordering, sentiment summaries, explicit missing/stale data, and HTML escaping without external scripts/assets.
- Economic menu checks confirmed DGS10 is absent, the US remains in sovereign coverage, and 16 countries are configured.
- The real server started on 127.0.0.1:8520 and its health endpoint returned HTTP 200 / `ok`.
- Live requests succeeded for all eight added country series: Spain, Netherlands, Switzerland, Sweden, Norway, Finland, New Zealand and South Korea. Netherlands' latest returned month was August 2026; the other added series returned September 2026. Per-country observation dates remain visible.
- Live AAPL fundamentals returned a business description and market-cap snapshot. In-browser generation produced the new report preview with readable sections and Markdown/HTML export controls.
- Browser inspection confirmed Workspace above the ticker bar, larger headings, nested collapsible sections and successful visual collapse of the Financials panel.
- Archive integrity checked; runtime databases, caches and virtual environments are excluded.

## Scope and limitations

The app assembles research documents without an LLM. Headline keyword flags do not establish financial materiality. Market cap is a snapshot, not a historical series. Normalized financials were not reconciled against filings. HTML generation/sanitization and Streamlit export controls were checked; browser download completion and PDF print pagination were not confirmed. Closing a panel changes visibility and may not skip its network request. Live source availability can change, and provider terms/third-party rights still apply. See README.md.
