import pandas as pd
import streamlit as st
import core

st.set_page_config(page_title='Research Terminal', page_icon='◈', layout='wide')
st.title('◈ Research Terminal')
st.caption('Personal research • free sources • local storage • no paid AI calls')


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

view = st.radio('Workspace', ['Company', 'Macro', 'News', 'AI brief'], horizontal=True, label_visibility='collapsed')

def price_bundle():
    return core.cached(f'prices:{ticker}:{period}', 1800, lambda: core.prices(ticker, period), refresh)

def info_bundle():
    return core.cached('info:' + ticker, 86400, lambda: core.fundamentals(ticker), refresh)

def news_bundle():
    return core.cached('news:' + ticker, 1800, lambda: core.news(ticker), refresh)

def macro_bundle(code):
    return core.cached('macro:' + code, 21600, lambda: core.macro(code), refresh)

if view == 'Company':
    st.header(ticker)
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
        st.line_chart(df.set_index('Date')[['Close']], height=360)
        st.caption('Yahoo Finance via yfinance. Daily prices adjusted for splits/dividends; not a real-time quote. Currency shown below when available.')
        with st.expander('Daily OHLC and volume'):
            st.dataframe(df, hide_index=True, width='stretch')
        st.download_button('Download price CSV', df.to_csv(index=False), f'{ticker}-prices.csv', 'text/csv')
    st.subheader('Fundamentals & ratios')
    with st.spinner('Loading provider snapshot…'):
        info = show_status(info_bundle())
    if info:
        st.write(info.get('longName') or info.get('shortName') or ticker)
        st.caption(f'Quote currency: {info.get("currency") or "unavailable"} · Financial reporting currency: {info.get("financialCurrency") or "unavailable"}')
        st.dataframe(pd.DataFrame([{'Field': k, 'Value': 'Unavailable' if v is None else str(v)} for k, v in info.items()]), hide_index=True, width='stretch')
        st.caption('Raw Yahoo fields. P/E and P/B are multiples; profitMargins and returnOnEquity are fractions; debtToEquity is provider-defined. Dividend yield units can vary by provider version: verify at source. Snapshot retrieval time is not a fiscal period. Missing fields are not zero.')
    st.link_button('Open Yahoo Finance source', f'https://finance.yahoo.com/quote/{ticker}/')

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
            st.line_chart(df.set_index('Date')['Value'])
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
    st.write('Build a Markdown research packet to download and upload to ChatGPT. Includes the selected ticker, last 60 daily observations, fundamentals, headlines with links, all six macro series, retrieval times and data errors.')
    st.caption('No LLM runs in this app. Review the packet and source terms before sharing it. The export is kept in your browser session until downloaded.')
    if st.button('Generate AI brief', type='primary'):
        with st.spinner('Collecting research packet…'):
            bundles = {'Price history': price_bundle(), 'Fundamentals': info_bundle(), 'News': news_bundle()}
            for code in core.MACRO:
                bundles[f'FRED {code} ({core.MACRO[code][1]})'] = macro_bundle(code)
            st.session_state['brief'] = (ticker, period, core.brief(ticker, bundles))
    packet = st.session_state.get('brief')
    if packet and packet[:2] == (ticker, period):
        st.download_button('Download Markdown brief', packet[2], f'{ticker}-research-brief.md', 'text/markdown')
        st.text_area('Preview', packet[2], height=420)

st.divider()
st.caption('Research aid only. Free data can be delayed, missing or incorrect. Verify important figures against filings and original releases. Personal use does not automatically grant redistribution rights.')
