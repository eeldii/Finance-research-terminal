import pandas as pd
import streamlit as st
import core
import charts
import report

st.set_page_config(page_title='Research Terminal V5', page_icon='◈', layout='wide', initial_sidebar_state='collapsed')
st.markdown("""<style>
.stApp {background:#151515;color:#ecebe8;}
[data-testid="stHeader"] {display:none;}
.block-container {padding:1.8rem 2rem 3rem;max-width:1500px;}
[data-testid="stVerticalBlock"] {gap:.9rem;}
h1,h2,h3 {color:#f0efec!important;letter-spacing:-.02em;font-weight:600!important;}
h1 {font-size:2rem!important;} h2 {font-size:1.65rem!important;margin-top:.7rem!important;}
h3 {font-size:1.15rem!important;margin-top:.5rem!important;}
.app-title {font-size:1.7rem;font-weight:600;letter-spacing:-.035em;margin:10px 0 20px;}
.app-title span {display:block;color:#b7b4ad;font-size:.85rem;font-weight:400;letter-spacing:0;margin-top:4px;}
[data-testid="stExpander"] {background:#1c1c1b;border:1px solid #373632;border-radius:10px;margin-bottom:.65rem;}
[data-testid="stExpander"] summary {padding:12px 14px;}
[data-testid="stExpander"] summary p {font-size:1rem!important;font-weight:600;color:#e4e1db;}
[data-testid="stMetric"] {padding:12px 0;border:0;background:transparent;}
[data-testid="stMetricLabel"] {color:#b7b4ad;font-size:.8rem;}
[data-testid="stMetricValue"] {color:#ecebe8;font-size:1.65rem;font-weight:500;font-variant-numeric:tabular-nums;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:#b7b4ad!important;font-size:.8rem;}
[data-testid="stDataFrame"] {border:1px solid #373632;border-radius:7px;}
[data-testid="stRadio"] {padding:2px 0;}
[data-testid="stRadio"] label {font-size:.95rem;}
button,input,[data-baseweb="select"]>div {border-radius:7px!important;}
button {border-color:#4b4842!important;}
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondaryFormSubmit"] {min-height:40px;}

[data-testid="stSidebar"] {display:none;}
@media(max-width:800px){.block-container{padding:1rem;}}
</style>""", unsafe_allow_html=True)
workspace_col, watchlist_col = st.columns([5, 1.4], vertical_alignment='bottom')
with workspace_col:
    workspace = st.radio('Workspace', ['Ticker', 'Macro'], horizontal=True, key='workspace')
watchlist_slot = watchlist_col.container()
st.markdown('<div class="app-title">Research Terminal<span>Prices, company research and the global economy · V5</span></div>', unsafe_allow_html=True)


def show_status(bundle):
    data, stamp, stale, error = bundle
    if stale:
        st.warning(f'STALE cache from {stamp} UTC. Refresh failed: {error}')
    elif error:
        st.warning(f'Data unavailable: {error}')
    elif stamp:
        st.caption(f'Updated {pd.Timestamp(stamp).strftime("%d %b %Y · %H:%M UTC")}')
    return data


def open_ticker(value):
    st.session_state['ticker_input'] = value
    st.session_state['active_ticker'] = value
    st.session_state['workspace'] = 'Ticker'

if workspace == 'Ticker':
    # Every ticker control is in the top bar. No left sidebar is used.
    with st.container(border=False):
        command, lookup, action = st.columns([1.2, 2.6, 1], vertical_alignment="bottom")
        with command:
            if 'ticker_input' not in st.session_state:
                st.session_state['ticker_input'] = st.session_state.get('active_ticker', 'AAPL')
            ticker_input = st.text_input('Ticker', key='ticker_input')
        with lookup:
            with st.form('search', border=False):
                search_text, search_action = st.columns([4, 1], vertical_alignment="bottom")
                query = search_text.text_input('Search companies', placeholder='Company name or ticker')
                submitted = search_action.form_submit_button('Search')
        refresh = action.button('Refresh view', help='Bypass cache for this view. Brief collection refreshes all packet sources.')
    if submitted and query.strip():
        result = core.cached('search:'+query.strip().lower(), 86400, lambda: core.search(query.strip()))
        st.session_state['results'] = show_status(result) or []
    results = st.session_state.get('results', [])
    if results:
        choice = st.selectbox('Matches', results, format_func=lambda r: f'{r["symbol"]} / {r["name"]} / {r["exchange"]}')
        st.button('Open match', on_click=open_ticker, args=(choice['symbol'],))
    try:
        ticker = core.symbol(ticker_input)
        st.session_state['active_ticker'] = ticker
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

else:
    try:
        ticker = core.symbol(st.session_state.get('active_ticker', 'AAPL'))
    except ValueError:
        ticker = 'AAPL'
    refresh = st.button('Refresh view', help='Refresh selected macro sources.')

main = st.container()
with watchlist_slot:
    with st.popover('Watchlist', width='stretch'):
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
        with st.expander('Data refresh', expanded=False):
            st.caption('Saved on this computer. Prices/news refresh after 30 minutes; financials after 24 hours; FRED after 6 hours. Use Refresh view to update sooner.')


def price_bundle(instrument=ticker):
    # One history source supports all return horizons and chart ranges.
    return core.cached(f'prices:v3:{instrument}:max', 1800, lambda: core.prices(instrument, 'max'), refresh)


def info_bundle():
    return core.cached('info:v4:'+ticker, 86400, lambda: core.fundamentals(ticker), refresh)


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

    else:
        st.info('No observations in the selected range.')


def styled_change(value):
    try:
        number = float(str(value).replace('%','').replace(',',''))
        return 'color: #77c49b' if number > 0 else ('color: #ed9797' if number < 0 else '')
    except (ValueError, TypeError):
        return ''

with main:
    view = st.radio('Research view', ['Overview', 'Financials', 'News', 'AI brief'], horizontal=True) if workspace == 'Ticker' else 'Macro'

    if view == 'Overview':
        with st.expander('Overview', expanded=True):
            with st.spinner('Loading instrument snapshot…'):
                info = show_status(info_bundle()) or {}
            st.subheader(info.get('longName') or info.get('shortName') or ticker)
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
                    with st.expander('Price changes', expanded=True):
                        returns = core.horizon_changes(rows)
                        summary = pd.DataFrame([{r['Horizon']: 'Unavailable' if r['Change (%)'] is None else f'{r["Change (%)"]:+.2f}%' for r in returns}])
                        st.dataframe(summary.style.map(styled_change), hide_index=True, width='stretch')
                        with st.expander('How these changes are calculated / baseline dates'):
                            st.write('Change from the last trading close on or before each calendar horizon to the latest available trading close. A baseline more than seven days before the target, or insufficient history, is unavailable. Adjusted prices reflect provider split/dividend adjustments. These are cumulative changes, not annualized returns; latest data may be delayed.')
                            st.dataframe(pd.DataFrame(returns), hide_index=True, width='stretch')
                    with st.expander('Price history', expanded=True):
                        label, control = st.columns([2, 1])
                        label.caption('Daily adjusted close · fixed time range')
                        horizon = control.selectbox('Graph history', list(core.HORIZONS), index=3)
                        paint_chart(core.chart_window(rows, core.HORIZONS[horizon]), f'Adjusted close ({currency})', 'instrument-chart')
                        st.caption('Daily adjusted OHLC from Yahoo via yfinance; not an executable live quote. Volume is provider reported. ETFs, indices, futures and crypto have different quote/volume conventions.')
                        with st.expander('Daily OHLC / volume'):
                            st.dataframe(df, hide_index=True, width='stretch')
                        st.download_button('Download price CSV', df.to_csv(index=False), f'{ticker}-prices.csv', 'text/csv')
            with st.expander('About the company', expanded=False):
                st.write(info.get('longBusinessSummary') or 'Business description unavailable for this instrument.')
            with st.expander('Fundamentals', expanded=True):
                if info:
                    st.dataframe(pd.DataFrame([{'Field': core.field_label(k), 'Value / units': core.scaled_field(k,v,info)} for k,v in info.items() if k != 'longBusinessSummary']), hide_index=True, width='stretch', height=600)
                st.caption('Amounts identify their scale and currency. EPS uses currency/share; margins, ROE and ROA are percentages, valuation ratios are multiples. Debt/equity and dividend yield retain provider units. Retrieval time is not the fiscal reporting period. TTM = trailing twelve months. Missing is not zero.')
                st.link_button('Yahoo instrument source', f'https://finance.yahoo.com/quote/{ticker}/')

    elif view == 'Financials':
        with st.expander('Financials', expanded=True):
            st.header(f'{ticker} financials')
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
                with st.expander(title, expanded=True):
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
        st.header(f'{ticker} news')
        data = show_status(news_bundle())
        with st.expander('How to read the headline score', expanded=False):
            st.markdown("""### What the number means
- **+1:** strongest positive dictionary score; **−1:** strongest negative score.
- **0:** balanced matched language, or no matched words.

### How it is calculated
1. Count positive minus negative words in each headline, with basic negation handling.
2. Divide by 3 and cap each score between −1 and +1.
3. Average all displayed headline scores, giving each headline equal weight.

### Example
Scores **+0.67** and **−0.33** average to **+0.17**.

### Limits
Only headlines are read. The score is **not** the percentage of positive stories, confidence or a price forecast. Missing context, ticker ambiguity and repeated themes can distort it. There is no recency or publisher weighting.
""")
        with st.expander('Headlines and sentiment', expanded=True):
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
        st.header('Instrument research document')
        st.write('Create a readable company report: business description, dated price and market-cap snapshot, recent prices, key fundamentals, annual/quarterly financials, recent news and sentiment, and source links. Download Markdown for ChatGPT or HTML to read/print in a browser. No AI model or paid API runs here.')
        st.caption('Headlines are sorted by publication time; their importance is not independently assessed. Market cap is a current provider snapshot, not a historical series.')
        if st.button('Generate AI brief', type='primary'):
            with st.spinner('Collecting essential instrument data…'):
                bundles = {'Price history': price_bundle(), 'Fundamentals': info_bundle(), 'News': news_bundle()}
                for frequency in ['yearly','quarterly']:
                    for kind in core.STATEMENT_ROWS:
                        bundles[f'{frequency}:{kind}'] = statement_bundle(kind,frequency)
                st.session_state['brief_v4'] = (ticker, report.instrument_report(ticker,bundles))
        packet = st.session_state.get('brief_v4')
        if packet and packet[0]==ticker:
            markdown = packet[1]
            st.download_button('Download research document / Markdown', markdown, f'{ticker}-research-document.md', 'text/markdown')
            st.download_button('Download research document / HTML', report.html_document(markdown), f'{ticker}-research-document.html', 'text/html')
            st.caption('HTML is a standalone, script-free document: open it in a browser, then Print → Save as PDF if wanted.')
            with st.expander('Document preview', expanded=True):
                st.markdown(markdown)

    else:
        st.header('Global economy')
        st.caption('OECD Main Economic Indicators via FRED / monthly 10-year government benchmark yields, percent, not seasonally adjusted. These are monthly observations, not live government bond quotes. Countries may have different latest observation months.')
        with st.expander('Government bond yields', expanded=True):
            countries = st.multiselect('Countries / map and yield table', list(core.SOVEREIGNS), default=list(core.SOVEREIGNS))
            sovereigns = []
            with st.spinner('Loading sovereign yields…'):
                for country in countries:
                    code = core.SOVEREIGNS[country][0]
                    sovereigns.append(core.sovereign_row(country, macro_bundle(f'IRLTLT01{code}M156N')))
            with st.expander('World map', expanded=True):
                st.altair_chart(charts.world_chart(sovereigns), width='stretch', theme=None)
                st.caption('Marker size and shading show the yield. Hover for yield, observation month and cache status. Markers are country reference points, not exchange or vessel locations. Base map: Natural Earth, public domain; boundaries are illustrative. No live tanker/AIS tracking is included.')
            with st.expander('Yield table', expanded=True):
                if sovereigns:
                    columns = ['Country','10Y yield (%)','MoM (bp)','Observation']
                    table = pd.DataFrame(sovereigns)[columns]
                    st.dataframe(table, hide_index=True, width='stretch', column_config={'10Y yield (%)':st.column_config.NumberColumn(format='%.3f'), 'MoM (bp)':st.column_config.NumberColumn(format='%+.1f')})
                    st.download_button('Download sovereign yield CSV', table.to_csv(index=False), 'sovereign-yields.csv', 'text/csv')
                issues = [r['Country'] for r in sovereigns if r['Error'] or r['Status'] == 'STALE fallback']
                if issues:
                    st.warning('Some yields are unavailable or use stale cached data: '+', '.join(issues)+'. See data notes below.')
                with st.expander('Sources and data notes', expanded=False):
                    for row in sovereigns:
                        st.markdown(f"**{row['Country']}** · [FRED source and notes]({row['Source']})")
                        st.caption(f"Updated {row['Retrieved UTC']} · {row['Status']}")
                        if row['Error']:
                            st.caption(row['Error'])
                st.caption('MoM = latest yield minus the preceding calendar-month observation, in basis points (100 bp = 1 percentage point). Missing months are not interpolated. OECD series can carry copyright restrictions: use each source link for notes and attribution before sharing.')

        with st.expander('Commodities', expanded=True):
            commodity_choices = st.multiselect('Commodity contracts', list(core.COMMODITIES), default=['WTI crude oil','Gold','Copper'])
            commodity_range = st.selectbox('Commodity graph history', ['1M','3M','6M','1Y','3Y','5Y','10Y'], index=3)
            st.caption('Yahoo front-contract futures histories, not spot prices. Contract rolls can create discontinuities; performance is not the return of a continuously investable strategy. Units are shown per contract below. No live quotes or roll-adjustment guarantee.')
            for name in commodity_choices:
                instrument, units = core.COMMODITIES[name]
                with st.expander(name, expanded=True):
                    st.caption(f'{instrument} · {units}')
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

        with st.expander('Economic indicators', expanded=True):
            indicator_country = st.selectbox('Indicator country', list(core.ECONOMIC_COUNTRIES))
            country_series = core.ECONOMIC_COUNTRIES[indicator_country]
            with st.expander('Choose indicators', expanded=False):
                options = st.columns(2)
                codes = [code for index, (code, (name, _)) in enumerate(country_series.items())
                         if options[index % 2].checkbox(name, value=code in {'UNRATE','CPIAUCSL'} or indicator_country != 'United States', key=f'economic-{code}')]
            for code in codes:
                with st.expander(f'{country_series[code][0]}', expanded=True):
                    name, units = country_series[code]
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
st.caption('For personal research. Data may be delayed or incomplete. Verify important figures and check source terms before sharing.')
