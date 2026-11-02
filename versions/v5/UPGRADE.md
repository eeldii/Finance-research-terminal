# V5 — Consolidated minimal dark interface

This V5 release merges the minimal redesign, dark theme, toolbar alignment and latest layout/indicator changes into one version.

## Run on Mac

Stop the previous app with Control+C. Extract the new ZIP and open Terminal in its `research-terminal-v5` folder. Run each command separately; do not type a standalone `sh` or the Markdown backticks.

```sh
python3.12 -m venv .venv
```

```sh
source .venv/bin/activate
```

```sh
python -m pip install -r requirements.txt
```

Wait for installation to finish, then run:

```sh
python -m streamlit run app.py
```

Keep Terminal open and visit http://127.0.0.1:8501. To launch later, activate the environment in this folder and run the final command again.

To retain your watchlist, copy the previous installation's `data` folder into this folder while both apps are stopped. Do not copy its virtual environment. The release ZIP contains no saved usage data. The database schema and dependency requirements are unchanged.

## Changes

- Minimal dark layout, sans-serif typography, clearer spacing and sentence-case headings.
- Matching dark charts, tables and world map, with muted warm accents.
- Aligned ticker/search/action controls, with search results below the toolbar.
- Watchlist menu in the top-right corner of both workspaces; main research content uses full width.
- Country yield table limited to country, yield, monthly change and observation date. Source/error/cache details are separate; data-quality warnings remain visible.
- Country-specific economic indicators added for Canada, Germany, France, UK, Japan, Italy, Spain and Finland (monthly unemployment).
- Existing calculations, collapsible sections, fixed chart ranges and research-document exports retained. HTML research documents remain light and print-friendly.

See README.md for data definitions/rights and VALIDATION.md for checks.
