import pandas as pd
import streamlit as st
import core

st.set_page_config(page_title='Research Terminal', page_icon='◈', layout='wide')
st.markdown("""<style>
html, body, input, button, [data-testid="stAppViewContainer"] {font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;}
.stApp {background:#050608;color:#e0e3e8;}
.block-container {padding:1rem; max-width:1900px;}
[data-testid="stSidebar"] {background:#101217;border-right:1px solid #4c5360;}
h1,h2,h3 {color:#ffac32!important; text-transform:uppercase; letter-spacing:.04em;}
h2 {font-size:1.25rem!important;} h3 {font-size:1rem!important;}
.terminal-banner {border-top:3px solid #ff9e19;border-bottom:1px solid #677081;background:#181d26;padding:10px 12px;color:#ffae35;font-size:18px;font-weight:bold;}
.terminal-banner span {display:inline-block;margin-left:16px;color:#78c5ff;font-size:12px;padding-top:7px;}
[data-testid="stMetric"] {background:#101721;border:1px solid #3a526c;border-top:2px solid #2798e4;padding:9px;}
[data-testid="stMetricLabel"] {color:#7cc8ff;} [data-testid="stMetricValue"] {color:#ffd277;font-size:1.25rem;}
[data-testid="stVerticalBlock"] {gap:.7rem;}
button, input, [data-baseweb="select"]>div {border-radius:0!important;}
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {border:1px solid #6f7783;}
[data-testid="stCaptionContainer"] {color:#9aaabd;}
[data-testid="stDataFrame"] {border:1px solid #3b4b60;}
[data-testid="stRadio"] {background:#111925;border-top:1px solid #344c68;border-bottom:1px solid #344c68;padding:6px 10px;}
</style>""", unsafe_allow_html=True)
st.caption('YAHOO / FRED / RSS  |  DAILY & DELAYED DATA  |  LOCAL SQLITE  |  NO PAID API')
st.markdown('<div class="terminal-banner">RESEARCH TERMINAL <span>V2 / PERSONAL RESEARCH</span></div>', unsafe_allow_html=True)



def show_status(bundle):
    data, stamp, stale, error = bundle
    if stale:
        st.warning(f'STALE cached data from {stamp}. Refresh failed: {error}')
    elif error:
        st.warning(f'Data unavailable: {error}')
    elif stamp:
        st.caption(f'Retrieved {stamp} · UTC')
    return data

with st.sidebar:
    st.header('Find an instrument')
    with st.form('search'):
        query = st.text_input('Company or ticker', placeholder='Apple or AAPL')
        submitted = st.form_submit_button('Search')
    if submitted and query.strip():
        with st.spinner('Searching Yahoo Finance…'):
            result = core.cached('search:' + query.strip().lower(), 86400, lambda: core.search(query.strip()))
        st.session_state['results'] = result[0] or []
        if result[3]:
            st.warning(result[3])
    results = st.session_state.get('results', [])
    if results:
        choice = st.selectbox('Search results', results, format_func=lambda r: f'{r["symbol"]} · {r["name"]} · {r["exchange"]}')
        if st.button('Open selected ticker'):
            st.session_state['ticker_input'] = choice['symbol']
    ticker_input = st.text_input('Open ticker directly', value='AAPL', key='ticker_input')
    try:
        ticker = core.symbol(ticker_input)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    saved = core.watchlist()
    a, b = st.columns(2)
    if a.button('☆ Add'):
        core.watch(ticker)
        st.rerun()
    if b.button('Remove', disabled=ticker not in saved):
        core.watch(ticker, False)
        st.rerun()
    st.subheader('Watchlist')
    if saved:
        selected = st.selectbox('Saved tickers', saved)
        def open_saved():
            st.session_state['ticker_input'] = selected
        st.button('Open saved', on_click=open_saved)
    else:
        st.caption('Add a ticker to save it locally.')
    period = st.selectbox('Price history', ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    refresh = st.button('Refresh current view', help='Re-fetch current section; brief refreshes all sections.')
    st.caption('Cached: prices/news 30 min, fundamentals 24 h, macro 6 h. Refresh only when needed.')

workspace = st.radio('Workspace', ['Ticker', 'Macro'], horizontal=True)
view = st.radio('Ticker functions', ['Overview', 'Financials', 'News', 'AI brief'], horizontal=True) if workspace == 'Ticker' else 'Macro'

def price_bundle():
    return core.cached(f'prices:{ticker}:{period}', 1800, lambda: core.prices(ticker, period), refresh)

def info_bundle():
    return core.cached('info:v2:' + ticker, 86400, lambda: core.fundamentals(ticker), refresh)

def news_bundle():
    return core.cached('news:' + ticker, 1800, lambda: core.news(ticker), refresh)

def statement_bundle(kind, frequency):
    return core.cached(f'statement:v2:{ticker}:{kind}:{frequency}', 86400, lambda: core.financial_statement(ticker, kind, frequency), refresh)

def macro_bundle(code):
    return core.cached('macro:' + code, 21600, lambda: core.macro(code), refresh)

if view == 'Overview':
    st.header(ticker)
    chart_panel, facts_panel = st.columns([1.6, 1])
    with chart_panel:
        with st.spinner('Loading daily history…'):
            p = price_bundle()
        rows = show_status(p)
        if rows:
            df = pd.DataFrame(rows)
            df['Date'] = pd.to_datetime(df['Date'], utc=True)
            close = df['Close'].dropna()
            c1, c2, c3 = st.columns(3)
            c1.metric('Latest adjusted close', f'{close.iloc[-1]:,.2f}')
            if len(close) > 1 and close.iloc[-2] != 0:
                c2.metric('Last session change', f'{(close.iloc[-1]/close.iloc[-2]-1)*100:+.2f}%')
            c3.metric('Latest trading date', str(df['Date'].iloc[-1].date()))
            st.line_chart(df.set_index('Date')[['Close']], height=320, color='#ffad33')
            st.caption('Yahoo Finance via yfinance. Daily prices adjusted for splits/dividends; not a real-time quote. Currency shown below when available.')
            with st.expander('Daily OHLC and volume'):
                st.dataframe(df, hide_index=True, width='stretch')
            st.download_button('Download price CSV', df.to_csv(index=False), f'{ticker}-prices.csv', 'text/csv')
    with facts_panel:
        st.subheader('Fundamentals & ratios')
        with st.spinner('Loading provider snapshot…'):
            info = show_status(info_bundle())
        if info:
            st.write(info.get('longName') or info.get('shortName') or ticker)
            st.caption(f'Quote currency: {info.get("currency") or "unavailable"} · Financial reporting currency: {info.get("financialCurrency") or "unavailable"}')
            st.dataframe(pd.DataFrame([{'Field': core.field_label(k), 'Value': core.format_field(k, v)} for k, v in info.items()]), hide_index=True, width='stretch')
            st.caption('Margins, ROE and ROA shown as percentages; valuation ratios as multiples. Financial amounts use reporting currency; market capitalization uses quote currency. Debt/equity and dividend yield retain provider units. TTM = trailing twelve months. Snapshot retrieval time is not a fiscal period. Missing fields are not zero.')
        st.link_button('Open Yahoo Finance source', f'https://finance.yahoo.com/quote/{ticker}/')

elif view == 'Financials':
    st.header(f'{ticker} / Financial statements')
    frequency = st.radio('Reporting frequency', ['yearly', 'quarterly'], format_func=lambda f: 'Annual' if f == 'yearly' else 'Quarterly', horizontal=True)
    with st.spinner('Loading reporting currency…'):
        info = show_status(info_bundle())
    currency = (info or {}).get('financialCurrency') or 'Unavailable — verify at source'
    st.caption(f'Reporting currency: {currency} | Amounts in millions; EPS in currency/share; share counts in millions. Columns are fiscal period-end dates, not release dates. Annual and quarterly periods are kept separate.')
    for kind, title in [('income', 'Income statement'), ('cashflow', 'Cash flow'), ('balance', 'Balance sheet')]:
        st.subheader(title)
        with st.spinner(f'Loading {title.lower()}…'):
            rows = show_status(statement_bundle(kind, frequency))
        if rows:
            raw = pd.DataFrame(rows).set_index('Metric')
            formatted = raw.copy().astype(object)
            for metric in raw.index:
                divisor = 1 if metric in {'Basic EPS', 'Diluted EPS'} else 1_000_000
                for col in raw.columns:
                    value = raw.loc[metric, col]
                    formatted.loc[metric, col] = 'Unavailable' if pd.isna(value) else f'{value/divisor:,.2f}'
            st.dataframe(formatted, width='stretch', height=min(460, 38 + 35*len(formatted)))
            st.download_button(f'Download {title.lower()} CSV (raw units)', raw.to_csv(), f'{ticker}-{kind}-{frequency}.csv', 'text/csv')
    st.caption('CapEx retains the provider’s sign (typically negative for cash outflow). Free cash flow is the reported provider field; missing values are not estimated. Balance sheet values are period-end stocks. History depth varies; up to eight periods are shown. Verify against filings.')
    st.link_button('Financial statement source', f'https://finance.yahoo.com/quote/{ticker}/financials/')

elif view == 'Macro':
    st.header('Macro dashboard')
    codes = st.multiselect('FRED series', list(core.MACRO), default=['DGS10', 'UNRATE', 'CPIAUCSL'], format_func=lambda c: f'{c} · {core.MACRO[c][0]}')
    for code in codes:
        name, units = core.MACRO[code]
        st.subheader(name)
        with st.spinner(f'Loading {code}…'):
            rows = show_status(macro_bundle(code))
        if rows:
            df = pd.DataFrame(rows)
            st.metric(f'{code} · {units}', f'{df.Value.iloc[-1]:,.3f}')
            st.caption(f'Latest observation: {df.Date.iloc[-1]}. Observation dates differ from release dates; history may be revised.')
            df['Date'] = pd.to_datetime(df.Date)
            st.line_chart(df.set_index('Date')['Value'], color='#63b5ff')
        st.link_button(f'{code} source, notes and attribution via FRED', f'https://fred.stlouisfed.org/series/{code}')
    st.caption('FRED, Federal Reserve Bank of St. Louis. CPI is an index level, not an inflation rate; GDP is a level, not growth. Series use their native frequencies and units.')

elif view == 'News':
    st.header(f'News · {ticker}')
    with st.spinner('Loading public RSS feeds…'):
        data = show_status(news_bundle())
    st.caption('Headline lexicon sentiment: −1 negative to +1 positive; 0 means no/net-zero matched words. No article text is analyzed. Ticker matching can include unrelated stories. Grouped by feed, not sorted by recency.')
    if data:
        for error in data['feed_errors']:
            st.warning(error)
        items = data['items']
        st.metric('Mean headline score (unweighted)', f'{sum(i["score"] for i in items)/len(items):+.2f}')
        for item in items:
            st.write(item['title'])
            st.caption(f'{item["published"]} · {item["source"]} · sentiment {item["score"]:+.2f}')
            st.link_button('Read source', item['link'])

else:
    st.header('Generate AI brief')
    st.write('Build a Markdown research packet to download and upload to ChatGPT. Includes the selected ticker, last 60 daily observations, fundamentals, annual and quarterly financial statements, headlines with links, all six macro series, retrieval times and data errors.')
    st.caption('No LLM runs in this app. Review the packet and source terms before sharing it. The export is kept in your browser session until downloaded.')
    if st.button('Generate AI brief', type='primary'):
        with st.spinner('Collecting research packet…'):
            bundles = {'Price history': price_bundle(), 'Fundamentals': info_bundle(), 'News': news_bundle()}
            for frequency in ['yearly', 'quarterly']:
                for kind in core.STATEMENT_ROWS:
                    bundles[f'{frequency.title()} {kind} statement (raw reporting currency units; EPS per share)'] = statement_bundle(kind, frequency)
            for code in core.MACRO:
                bundles[f'FRED {code} ({core.MACRO[code][1]})'] = macro_bundle(code)
            st.session_state['brief'] = (ticker, period, core.brief(ticker, bundles))
    packet = st.session_state.get('brief')
    if packet and packet[:2] == (ticker, period):
        st.download_button('Download Markdown brief', packet[2], f'{ticker}-research-brief.md', 'text/markdown')
        st.text_area('Preview', packet[2], height=420)

st.divider()
st.caption('Research aid only. Free data can be delayed, missing or incorrect. Verify important figures against filings and original releases. Personal use does not automatically grant redistribution rights.')
