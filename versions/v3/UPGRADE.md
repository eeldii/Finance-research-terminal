# V3 — Mac setup and upgrade

1. Stop V2 with **Control+C** in its Terminal window.
2. Extract `research-terminal-v3.zip` and open Terminal in the extracted `research-terminal-v3` folder. Type `cd `, drag the folder from Finder into Terminal and press Return.
3. Run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. For later launches, enter the same folder, activate `.venv` and run the last command. Python 3.12 is the validated version.

To preserve your watchlist/cache, copy V2's `data` folder into V3 while both apps are stopped. The app continues using SQLite with the same watchlist schema. New price-history cache keys avoid conflicts with V2's selected-period data. Do not copy the old virtual environment. V1/V2 source and archives remain separate.

If updating an existing repository, replace `app.py`, `core.py`, `requirements.txt`, `.streamlit/config.toml` and the test files; also add `charts.py` and the entire `assets` folder. Install requirements in the existing activated environment before restarting. Keep `data` and `.gitignore`; do not commit the database.

See README.md for definitions, limitations and source information; VALIDATION.md for checks performed; COMMIT_MESSAGE.txt for the release commit message.
