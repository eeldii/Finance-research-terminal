"""Fixed-domain charts: deliberately no pan/zoom bindings or .interactive()."""
import json
from datetime import timedelta
from pathlib import Path
import altair as alt
import pandas as pd

ORANGE = '#ff9d23'

def price_chart(df, title='Adjusted close', height=350):
    if df.empty:
        return None
    start, end = pd.Timestamp(df.Date.min()), pd.Timestamp(df.Date.max())
    if start == end:
        start, end = start.to_pydatetime()-timedelta(days=1), end.to_pydatetime()+timedelta(days=1)
    base = alt.Chart(df).encode(
        x=alt.X('Date:T', scale=alt.Scale(domain=[start.isoformat(), end.isoformat()], nice=False), title=None),
        y=alt.Y('Close:Q', scale=alt.Scale(zero=False), title=title),
        tooltip=[alt.Tooltip('Date:T', title='Trading date', format='%Y-%m-%d'), alt.Tooltip('Close:Q', title=title, format=',.4f')])
    return style((base.mark_line(color=ORANGE, clip=True, strokeWidth=1.6) +
                  base.mark_circle(color=ORANGE, opacity=0, size=60)).properties(height=height))

def style(chart):
    return chart.configure(background='#111111').configure_view(stroke='#363636').configure_axis(
        labelColor='#bababa', titleColor='#d7d7d7', gridColor='#282828', domainColor='#555555',
        tickColor='#555555', labelFont='monospace', titleFont='monospace').configure_legend(
        labelColor='#dedede', titleColor='#ff9d23')

def world_chart(rows):
    geo = json.loads((Path(__file__).parent/'assets/world.geojson').read_text())
    land = alt.Chart(alt.Data(values=geo['features'])).mark_geoshape(fill='#242424', stroke='#69604f', strokeWidth=.4)
    layers = [land]
    data = pd.DataFrame(rows)
    if not data.empty:
        data = data.dropna(subset=['10Y yield (%)'])
        if not data.empty:
            points = alt.Chart(data).mark_circle(stroke='#ffd59c', strokeWidth=1).encode(
                size=alt.Size('10Y yield (%):Q', scale=alt.Scale(range=[60, 240]), legend=None),
                color=alt.Color('10Y yield (%):Q', scale=alt.Scale(range=['#79440c', '#ffd09a']), legend=alt.Legend(orient='bottom', title='10Y yield (%)')),
                longitude='longitude:Q', latitude='latitude:Q',
                tooltip=['Country:N', alt.Tooltip('10Y yield (%):Q', format='.3f'), 'Observation:N', 'Status:N'])
            layers.append(points)
    return style(alt.layer(*layers).project(type='equalEarth').properties(height=360))
