import unittest
import report
import core

class ReportTests(unittest.TestCase):
    def fixture(self):
        def b(data): return (data,'2026-11-02T12:00:00+00:00',False,None)
        return {'Fundamentals':b({'longName':'Example Company','longBusinessSummary':'Builds useful things.','currency':'USD','financialCurrency':'USD','marketCap':2e9,'trailingPE':20}),
                'Price history':b([{'Date':'2026-10-01','Close':100},{'Date':'2026-11-02','Close':110}]),
                'News':b({'items':[{'title':'Older earnings','published':'Thu, 01 Oct 2026 12:00:00 GMT','score':.33,'link':'https://example.org/older','source':'Test'}, {'title':'Latest earnings beat','published':'Mon, 02 Nov 2026 12:00:00 GMT','score':.67,'link':'https://example.org/new','source':'Test'}], 'feed_errors':[]}),
                'yearly:income':b([{'Metric':'Revenue','2026-09-30':2e9,'2025-09-30':1e9}])}
    def test_readable_report_has_essentials_and_dates(self):
        text=report.instrument_report('TEST',self.fixture())
        for value in ['Research document: TEST','Builds useful things.','2.00 (billions, USD)','110.0000 USD','Annual — Income statement','2026-09-30','+100.00%','Sources & data quality','Mean score']:
            self.assertIn(value,text)
        self.assertLess(text.index('Latest earnings beat'),text.index('Older earnings'))
        self.assertNotIn('```json',text)
        self.assertIn('Historical market-cap observations are not supplied',text)
    def test_missing_and_stale_sections_remain_explicit(self):
        text=report.instrument_report('TEST',{'Fundamentals':(None,None,False,'offline'),'Price history':(None,'old',True,'offline')})
        self.assertIn('Price history unavailable',text)
        self.assertIn('STALE fallback',text)
        self.assertIn('offline',text)
    def test_html_escapes_provider_content_and_has_no_remote_assets(self):
        bundles=self.fixture()
        bundles['Fundamentals'][0]['longBusinessSummary']='<script>alert(1)</script> [bad](javascript:alert(1))'
        text=report.instrument_report('TEST',bundles)
        document=report.html_document(text)
        self.assertNotIn('<script>',document)
        self.assertNotIn('href="javascript:',document)
        self.assertIn('<table>',document)
        self.assertIn('https://example.org/new',document)
        self.assertNotIn('<img',document)
    def test_economic_menu_and_expanded_countries(self):
        self.assertNotIn('DGS10',core.ECONOMIC_SERIES)
        self.assertIn('United States',core.SOVEREIGNS)
        self.assertEqual(len(core.SOVEREIGNS),16)

if __name__=='__main__': unittest.main()
