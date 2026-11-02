import pandas as pd
import streamlit as st
import core
import charts

st.set_page_config(page_title='Research Terminal V3', page_icon='◈', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
html, body, input, button, [data-testid="stAppViewContainer"] {font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace;}
.stApp {background:#111111;color:#e8e8e8;}
[data-testid="stHeader"] {display:none;}
.block-container {padding:1rem 1.1rem;max-width:2100px;}
[data-testid="stVerticalBlock"] {gap:.55rem;}
h1,h2,h3 {color:#ff9d23!important;text-transform:uppercase;letter-spacing:.025em;}
h2 {font-size:1.2rem!important;} h3 {font-size:.95rem!important;}
.terminal-banner {border:1px solid #444;border-top:2px solid #ff9d23;background:#191919;padding:8px 12px;color:#ff9d23;font-weight:bold;}
.terminal-banner span {color:#bcbcbc;font-size:11px;margin-left:20px;}
[data-testid="stMetric"] {background:#181818;border:1px solid #393939;padding:7px;}
[data-testid="stMetricLabel"] {color:#bababa;font-size:11px;}
[data-testid="stMetricValue"] {color:#e8e8e8;font-size:1.3rem;}
button,input,[data-baseweb="select"]>div {border-radius:0!important;}
button {border-color:#555!important;}
[data-testid="stCaptionContainer"] {color:#b0b0b0;}
[data-testid="stDataFrame"] {border:1px solid #444;}
[data-testid="stRadio"] {background:#1b1b1b;border-top:1px solid #4b4030;border-bottom:1px solid #4b4030;padding:5px 8px;}
[data-testid="stLinkButton"] a {color:#ffb450;}
[data-testid="stSidebar"] {display:none;}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="terminal-banner">◈ RESEARCH TERMINAL <span>V3 / YAHOO · FRED · RSS / DAILY & DELAYED</span></div>', unsafe_allow_html=True)


def show_status(bundle):
    data, stamp, stale, error = bundle
    if stale:
        st.warning(f'STALE cache from {stamp} UTC. Refresh failed: {error}')
    elif error:
        st.warning(f'Data unavailable: {error}')
    elif stamp:
        st.caption(f'Retrieved {stamp} · UTC')
    return data


def open_ticker(value):
    st.session_state['ticker_input'] = value

# Every ticker control is in the top bar. No left sidebar is used.
with st.container(border=True):
    command, lookup, action = st.columns([1.2, 2.6, 1])
    with command:
        if 'ticker_input' not in st.session_state:
            st.session_state['ticker_input'] = 'AAPL'
        ticker_input = st.text_input('INSTRUMENT / TICKER', key='ticker_input')
    with lookup:
        with st.form('search'):
            search_text, search_action = st.columns([4, 1])
            query = search_text.text_input('COMPANY LOOKUP', placeholder='Company name or ticker')
            submitted = search_action.form_submit_button('Search')
        if submitted and query.strip():
            result = core.cached('search:'+query.strip().lower(), 86400, lambda: core.search(query.strip()))
            st.session_state['results'] = show_status(result) or []
        results = st.session_state.get('results', [])
        if results:
            choice = st.selectbox('Matches', results, format_func=lambda r: f'{r["symbol"]} / {r["name"]} / {r["exchange"]}')
            st.button('Open match', on_click=open_ticker, args=(choice['symbol'],))
    refresh = action.button('Refresh view', help='Bypass cache for this view. Brief collection refreshes all packet sources.')
try:
    ticker = core.symbol(ticker_input)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

main, lists = st.columns([5, 1.15], gap='small')
with lists:
    with st.container(border=True):
        st.subheader('LISTS / WATCHLIST')
        st.caption(f'Active: {ticker}')
        if st.button('＋ Save ticker', width='stretch'):
            core.watch(ticker)
            st.rerun()
        saved = core.watchlist()
        if saved:
            selected = st.selectbox('Saved instruments', saved)
            st.button('Open saved', on_click=open_ticker, args=(selected,), width='stretch')
            if st.button('Remove saved', width='stretch'):
                core.watch(selected, False)
                st.rerun()
            st.dataframe(pd.DataFrame({'Ticker': saved}), hide_index=True, width='stretch')
        else:
            st.caption('Save an instrument to build your list.')
        st.caption('Stored locally in SQLite. Prices/news: 30m cache. Fundamentals/statements: 24h. FRED: 6h.')


def price_bundle(instrument=ticker):
    # One history source supports all return horizons and chart ranges.
    return core.cached(f'prices:v3:{instrument}:max', 1800, lambda: core.prices(instrument, 'max'), refresh)


def info_bundle():
    return core.cached('info:v2:'+ticker, 86400, lambda: core.fundamentals(ticker), refresh)


def statement_bundle(kind, frequency):
    return core.cached(f'statement:v2:{ticker}:{kind}:{frequency}', 86400, lambda: core.financial_statement(ticker, kind, frequency), refresh)


def macro_bundle(code):
    return core.cached('macro:'+code, 21600, lambda: core.macro(code), refresh)


def news_bundle():
    return core.cached('news:'+ticker, 1800, lambda: core.news(ticker), refresh)


def paint_chart(df, title, key):
    chart = charts.price_chart(df, title)
    if chart is not None:
        st.altair_chart(chart, width='stretch', key=key, theme=None)
        st.caption('Range locked: wheel scrolling and dragging cannot move the time axis. Use the range selector above.')
    else:
        st.info('No observations in the selected range.')


def styled_change(value):
    try:
        number = float(str(value).replace('%','').replace(',',''))
        return 'color: #55b878' if number > 0 else ('color: #e35b5b' if number < 0 else '')
    except (ValueError, TypeError):
        return ''

with main:
    workspace = st.radio('Workspace', ['Ticker', 'Macro'], horizontal=True)
    view = st.radio('Ticker functions', ['Overview', 'Financials', 'News', 'AI brief'], horizontal=True) if workspace == 'Ticker' else 'Macro'

    if view == 'Overview':
        st.header(f'{ticker} / Price monitor')
        with st.spinner('Loading instrument snapshot…'):
            info = show_status(info_bundle()) or {}
        st.write(info.get('longName') or info.get('shortName') or ticker)
        currency = info.get('currency') or 'quote currency unavailable'
        with st.spinner('Loading price history…'):
            rows = show_status(price_bundle())
        if rows:
            df = core.price_frame(rows)
            if not df.empty:
                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df)>1 else None
                metrics = st.columns(4)
                metrics[0].metric(f'Adjusted close / {currency}', f'{latest.Close:,.2f}')
                change = core.pct_change(latest.Close, previous.Close) if previous is not None else None
                metrics[1].metric('Last session', 'Unavailable' if change is None else f'{change:+.2f}%')
                metrics[2].metric('Volume / shares or contracts', 'Unavailable' if pd.isna(latest.get('Volume')) else f'{latest.get("Volume"):,.0f}')
                metrics[3].metric('Trading date', str(latest.Date.date()))
                st.subheader('Historical change / adjusted close')
                returns = core.horizon_changes(rows)
                summary = pd.DataFrame([{r['Horizon']: 'Unavailable' if r['Change (%)'] is None else f'{r["Change (%)"]:+.2f}%' for r in returns}])
                st.dataframe(summary.style.map(styled_change), hide_index=True, width='stretch')
                with st.expander('How these changes are calculated / baseline dates'):
                    st.write('Change from the last trading close on or before each calendar horizon to the latest available trading close. A baseline more than seven days before the target, or insufficient history, is unavailable. Adjusted prices reflect provider split/dividend adjustments. These are cumulative changes, not annualized returns; latest data may be delayed.')
                    st.dataframe(pd.DataFrame(returns), hide_index=True, width='stretch')
                label, control = st.columns([2, 1])
                label.subheader('PRICE HISTORY / FIXED RANGE')
                horizon = control.selectbox('Graph history', list(core.HORIZONS), index=3)
                paint_chart(core.chart_window(rows, core.HORIZONS[horizon]), f'Adjusted close ({currency})', 'instrument-chart')
                st.caption('Daily adjusted OHLC from Yahoo via yfinance; not an executable live quote. Volume is provider reported. ETFs, indices, futures and crypto have different quote/volume conventions.')
                with st.expander('Daily OHLC / volume'):
                    st.dataframe(df, hide_index=True, width='stretch')
                st.download_button('Download price CSV', df.to_csv(index=False), f'{ticker}-prices.csv', 'text/csv')
        st.subheader('Fundamentals / full-width snapshot')
        if info:
            st.dataframe(pd.DataFrame([{'Field': core.field_label(k), 'Value / units': core.scaled_field(k,v,info)} for k,v in info.items()]), hide_index=True, width='stretch', height=600)
        st.caption('Amounts identify their scale and currency. EPS uses currency/share; margins, ROE and ROA are percentages, valuation ratios are multiples. Debt/equity and dividend yield retain provider units. Retrieval time is not the fiscal reporting period. TTM = trailing twelve months. Missing is not zero.')
        st.link_button('Yahoo instrument source', f'https://finance.yahoo.com/quote/{ticker}/')

    elif view == 'Financials':
        st.header(f'{ticker} / Financial statements')
        freq_col, unit_col = st.columns(2)
        frequency = freq_col.radio('Reporting frequency', ['yearly','quarterly'], format_func=lambda f: 'Annual' if f=='yearly' else 'Quarterly', horizontal=True)
        scale_name = unit_col.selectbox('Statement amount scale', ['Billions','Millions'])
        scale = 1e9 if scale_name=='Billions' else 1e6
        info = show_status(info_bundle()) or {}
        currency = info.get('financialCurrency') or 'currency unknown'
        annual = statement_bundle('income','yearly')
        annual_dates = [k for k in (annual[0] or [{}])[0] if k!='Metric']
        if frequency=='quarterly' and (annual[3] or annual[2]):
            st.warning('Fiscal quarter naming uses annual statement dates. Annual reference status: '+str(annual[3] or 'stale cache'))
        st.caption(f'{scale_name}, {currency} / EPS: {currency} per share / Shares: millions. Quarter labels are fiscal quarters inferred from annual year ends (52/53-week tolerance); unavailable if the annual reference is missing. Dates are period ends, not publication dates.')
        for kind, title in [('income','Income statement'),('cashflow','Cash flow'),('balance','Balance sheet')]:
            st.subheader(title)
            bundle = annual if kind=='income' and frequency=='yearly' else statement_bundle(kind,frequency)
            rows = show_status(bundle)
            if rows:
                table = core.statement_display(rows, frequency, annual_dates, currency, scale)
                change_columns = [c for c in table if c.endswith(' %')]
                styled = table.style.map(styled_change, subset=change_columns)
                st.dataframe(styled, width='stretch', height=min(470, 40+35*len(table)))
                st.download_button(f'Download {title.lower()} CSV (with changes)', table.to_csv(), f'{ticker}-{kind}-{frequency}-display.csv', 'text/csv')
                raw = pd.DataFrame(rows).set_index('Metric')
                st.download_button(f'Download {title.lower()} CSV (raw units)', raw.to_csv(), f'{ticker}-{kind}-{frequency}-raw.csv', 'text/csv')
        st.info('YoY compares with the same fiscal period about one year earlier. Quarterly tables also show QoQ versus the preceding quarter. Change = (current − prior) ÷ |prior| × 100. A dash means a missing/zero baseline or missing matching period. With negative earnings this measures improvement/deterioration, not conventional positive-base growth. CapEx keeps its cash-outflow sign; changes in balance-sheet stocks are not revenue growth. Scroll tables horizontally for older periods.')
        st.link_button('Yahoo financial statement source', f'https://finance.yahoo.com/quote/{ticker}/financials/')

    elif view == 'News':
        st.header(f'{ticker} / News & headline tone')
        data = show_status(news_bundle())
        st.info('Mean headline score = the sum of the displayed headline scores divided by the number of headlines, with equal weight per headline. Each score counts positive minus negative dictionary words (with basic negation), divides by 3 and caps the result at −1 / +1. Positive = more favorable matched language; negative = more unfavorable language. Zero can mean no matched words or a balance. It is not the percentage of positive articles, a confidence score or a return forecast. Only headlines are read; repeated themes, ticker ambiguity and missing context can distort the result.')
        if data:
            for error in data['feed_errors']:
                st.warning(error)
            items = data['items']
            mean = sum(i['score'] for i in items)/len(items) if items else None
            st.metric('Mean headline score / equal weighted', 'Unavailable' if mean is None else f'{mean:+.2f}')
            st.caption(f'{len(items)} deduplicated headlines. Example: scores +0.67 and −0.33 average to +0.17. Feed order is retained; no recency or publisher weighting.')
            for item in items:
                st.write(item['title'])
                st.caption(f'{item["published"]} / {item["source"]} / tone {item["score"]:+.2f}')
                st.link_button('Read source', item['link'])

    elif view == 'AI brief':
        st.header('Generate AI brief')
        st.write('Export a Markdown packet for ChatGPT: latest price history, horizon changes, fundamentals, annual/quarterly statements, headlines and core FRED series. Statement values are raw units; growth rates and fiscal labels are available in Financials CSV exports. No AI API call runs here.')
        if st.button('Generate AI brief', type='primary'):
            with st.spinner('Collecting sources…'):
                price = price_bundle()
                bundles = {'Price history': price, 'Historical adjusted-close changes': (core.horizon_changes(price[0]) if price[0] else None, price[1], price[2], price[3]), 'Fundamentals': info_bundle(), 'News': news_bundle()}
                for frequency in ['yearly','quarterly']:
                    for kind in core.STATEMENT_ROWS:
                        bundles[f'{frequency.title()} {kind} statement (raw reporting currency units; EPS per share)'] = statement_bundle(kind,frequency)
                for code in core.MACRO:
                    bundles[f'FRED {code} ({core.MACRO[code][1]})'] = macro_bundle(code)
                st.session_state['brief'] = (ticker, core.brief(ticker,bundles))
        packet = st.session_state.get('brief')
        if packet and packet[0]==ticker:
            st.download_button('Download Markdown brief', packet[1], f'{ticker}-research-brief.md', 'text/markdown')
            st.text_area('Preview', packet[1], height=420)

    else:
        st.header('Global macro / sovereign rates')
        st.caption('OECD Main Economic Indicators via FRED / monthly 10-year government benchmark yields, percent, not seasonally adjusted. These are monthly observations, not live government bond quotes. Countries may have different latest observation months.')
        countries = st.multiselect('Countries / map and yield table', list(core.SOVEREIGNS), default=list(core.SOVEREIGNS))
        sovereigns = []
        with st.spinner('Loading sovereign yields…'):
            for country in countries:
                code = core.SOVEREIGNS[country][0]
                sovereigns.append(core.sovereign_row(country, macro_bundle(f'IRLTLT01{code}M156N')))
        st.subheader('WORLD / 10Y GOVERNMENT YIELD MONITOR')
        st.altair_chart(charts.world_chart(sovereigns), width='stretch', theme=None)
        st.caption('Marker size and orange shade encode yield. Hover for yield, observation month and cache status. Markers are country reference points, not exchange or vessel locations. Base map: Natural Earth, public domain; boundaries are illustrative. No live tanker/AIS tracking is included.')
        if sovereigns:
            columns = ['Country','10Y yield (%)','MoM (bp)','Observation','Status','Retrieved UTC','Source','Error']
            table = pd.DataFrame(sovereigns)[columns]
            st.dataframe(table, hide_index=True, width='stretch', column_config={'Source':st.column_config.LinkColumn('FRED source / notes'), '10Y yield (%)':st.column_config.NumberColumn(format='%.3f'), 'MoM (bp)':st.column_config.NumberColumn(format='%+.1f')})
            st.download_button('Download sovereign yield CSV', table.to_csv(index=False), 'sovereign-yields.csv', 'text/csv')
        st.caption('MoM = latest yield minus the preceding calendar-month observation, in basis points (100 bp = 1 percentage point). Missing months are not interpolated. OECD series can carry copyright restrictions: use each source link for notes and attribution before sharing.')

        st.subheader('COMMODITIES / FUTURES MONITOR')
        commodity_choices = st.multiselect('Commodity contracts', list(core.COMMODITIES), default=['WTI crude oil','Gold','Copper'])
        commodity_range = st.selectbox('Commodity graph history', ['1M','3M','6M','1Y','3Y','5Y','10Y'], index=3)
        st.caption('Yahoo front-contract futures histories, not spot prices. Contract rolls can create discontinuities; performance is not the return of a continuously investable strategy. Units are shown per contract below. No live quotes or roll-adjustment guarantee.')
        for name in commodity_choices:
            instrument, units = core.COMMODITIES[name]
            st.subheader(f'{name} / {instrument} / {units}')
            rows = show_status(price_bundle(instrument))
            if rows:
                df = core.price_frame(rows)
                if not df.empty:
                    last = df.iloc[-1]
                    prev = df.iloc[-2] if len(df)>1 else None
                    delta = core.pct_change(last.Close,prev.Close) if prev is not None else None
                    st.metric(f'Latest daily close ({units})',f'{last.Close:,.3f}',delta=None if delta is None else f'{delta:+.2f}%')
                    st.caption(f'Trading date: {last.Date.date()}')
                    paint_chart(core.chart_window(rows,core.HORIZONS[commodity_range]),f'Close ({units})',f'commodity-{instrument}')
            st.link_button(f'{name} quote source',f'https://finance.yahoo.com/quote/{instrument}/')

        st.subheader('ECONOMIC SERIES / FRED')
        codes = st.multiselect('FRED dashboard series',list(core.MACRO),default=['DGS10','UNRATE','CPIAUCSL'],format_func=lambda c:f'{c} / {core.MACRO[c][0]}')
        for code in codes:
            name, units = core.MACRO[code]
            st.subheader(name)
            rows = show_status(macro_bundle(code))
            if rows:
                df = pd.DataFrame(rows)
                st.metric(f'{code} / {units}',f'{df.Value.iloc[-1]:,.3f}')
                st.caption(f'Observation date: {df.Date.iloc[-1]}. Dates are not release dates; historical observations may be revised.')
                plot = df.rename(columns={'Value':'Close'})
                plot['Date'] = pd.to_datetime(plot.Date)
                paint_chart(plot,units,f'fred-{code}')
            st.link_button(f'{code} source and notes',f'https://fred.stlouisfed.org/series/{code}')
        st.caption('CPI is an index level, not inflation; real GDP is a level, not growth. Each series retains its own native frequency and units.')

st.divider()
st.caption('PERSONAL RESEARCH / FREE DATA MAY BE DELAYED, INCOMPLETE OR INCORRECT / VERIFY AGAINST FILINGS & ORIGINAL RELEASES / CHECK SOURCE RIGHTS BEFORE SHARING')
