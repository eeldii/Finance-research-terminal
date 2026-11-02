import unittest
import pandas as pd
import core
import charts

class V3Tests(unittest.TestCase):
    def test_horizons_use_calendar_baselines_and_require_coverage(self):
        rows = [{'Date':'2024-01-01', 'Close':50}, {'Date':'2024-10-31', 'Close':80}, {'Date':'2024-12-02','Close':90}, {'Date':'2025-01-02','Close':100}]
        changes = {r['Horizon']:r for r in core.horizon_changes(rows)}
        self.assertAlmostEqual(changes['1M']['Change (%)'], (100/90-1)*100)
        self.assertEqual(changes['1M']['Baseline date'],'2024-12-02')
        self.assertEqual(changes['1Y']['Change (%)'],100)
        self.assertIsNone(changes['3M']['Change (%)'])  # No close near target.
        self.assertIsNone(changes['10Y']['Change (%)'])
    def test_chart_window_and_no_pan_or_zoom(self):
        rows=[{'Date':'2020-01-01','Close':1},{'Date':'2024-12-02','Close':2},{'Date':'2025-01-02','Close':3}]
        df=core.chart_window(rows,1)
        self.assertEqual(len(df),2)
        spec=charts.price_chart(df).to_dict()
        self.assertNotIn('params',spec)
        domain=spec['encoding']['x']['scale']['domain'] if 'encoding' in spec else spec['layer'][0]['encoding']['x']['scale']['domain']
        self.assertEqual(domain,['2024-12-02T00:00:00','2025-01-02T00:00:00'])
        self.assertNotIn('bind',str(spec))
    def test_fiscal_quarters_non_december_year_end(self):
        self.assertEqual(core.fiscal_quarter('2025-12-27',['2025-09-27']),1)
        self.assertEqual(core.fiscal_quarter('2025-03-29',['2025-09-27']),2)
        self.assertEqual(core.fiscal_quarter('2025-06-28',['2025-09-27']),3)
        self.assertEqual(core.fiscal_quarter('2025-09-27',['2025-09-27']),4)
        self.assertIsNone(core.fiscal_quarter('2025-12-31',[]))
    def test_growth_negative_zero_and_missing_periods(self):
        self.assertEqual(core.pct_change(-50,-100),50)
        self.assertIsNone(core.pct_change(10,0))
        rows=[{'Metric':'Revenue','2025-12-31':2e9,'2025-09-30':1e9,'2024-12-31':1e9}, {'Metric':'Diluted EPS','2025-12-31':2,'2025-09-30':1,'2024-12-31':0}]
        table=core.statement_display(rows,'quarterly',['2025-12-31'],'USD')
        self.assertEqual(table.loc['Revenue (billions, USD)','2025-12-31 (Q4) YoY %'],'+100.00%')
        self.assertEqual(table.loc['Revenue (billions, USD)','2025-12-31 (Q4) QoQ %'],'+100.00%')
        self.assertEqual(table.loc['Diluted EPS (USD/share)','2025-12-31 (Q4)'],'2.00')
        self.assertEqual(table.loc['Diluted EPS (USD/share)','2025-12-31 (Q4) YoY %'],'—')
        self.assertEqual(table.loc['Revenue (billions, USD)','2024-12-31 (Q4) QoQ %'],'—')
    def test_scaled_currency_and_sovereign_missing_month(self):
        self.assertEqual(core.scaled_field('marketCap',2e9,{'currency':'EUR'}),'2.00 (billions, EUR)')
        self.assertEqual(core.scaled_field('totalRevenue',5e6,{'financialCurrency':'USD'}),'5.00 (millions, USD)')
        bundle=([{'Date':'2025-01-01','Value':3},{'Date':'2025-02-01','Value':3.2}], 'stamp',True,'offline')
        row=core.sovereign_row('Canada',bundle)
        self.assertAlmostEqual(row['MoM (bp)'],20)
        self.assertEqual(row['Status'],'STALE fallback')
        bundle[0][1]['Date']='2025-03-01'
        self.assertIsNone(core.sovereign_row('Canada',bundle)['MoM (bp)'])
        self.assertEqual(core.sovereign_row('Canada',(None,None,False,'offline'))['Observation'],'Unavailable')
    def test_bundled_map_without_data(self):
        spec=charts.world_chart([]).to_dict()
        self.assertEqual(spec['projection']['type'],'equalEarth')
        self.assertNotIn('url',str(spec))

if __name__=='__main__':
    unittest.main()
