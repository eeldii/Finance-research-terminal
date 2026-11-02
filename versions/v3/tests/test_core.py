import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import core

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(core, 'DB', Path(self.temp.name) / 'test.db')
        self.patch.start()
    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()
    def test_watchlist_persistence_validation(self):
        core.watch(' aapl ')
        core.watch('AAPL')
        self.assertEqual(core.watchlist(), ['AAPL'])
        core.watch('AAPL', False)
        self.assertEqual(core.watchlist(), [])
        with self.assertRaises(ValueError):
            core.watch("'; DROP TABLE watchlist;")
    def test_cache_hit_stale_fallback_and_missing(self):
        first = core.cached('x', 100, lambda: {'value': 42})
        def fail():
            raise RuntimeError('offline')
        self.assertEqual(core.cached('x', 100, fail)[0], first[0])
        stale = core.cached('x', 100, fail, refresh=True)
        self.assertTrue(stale[2])
        self.assertIn('offline', stale[3])
        self.assertIsNone(core.cached('missing', 100, fail)[0])
    def test_sentiment_negation_and_bounds(self):
        self.assertGreater(core.sentiment('profits surge on strong growth'), 0)
        self.assertLess(core.sentiment('not strong'), 0)
        self.assertEqual(core.sentiment('board announces meeting'), 0)
        self.assertEqual(core.sentiment('gains ' * 20), 1)
    def test_news_partial_failure_and_dedup(self):
        xml = b'<rss><channel><item><title>profits rise</title><link>https://example.org/a</link></item><item><title>profits rise</title><link>https://example.org/b</link></item></channel></rss>'
        with patch.object(core, 'fetch', side_effect=[xml, RuntimeError('offline')]):
            data = core.news('AAPL')
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(len(data['feed_errors']), 1)
    def test_labels_units_and_statement_missing_values(self):
        import pandas as pd
        self.assertEqual(core.field_label('trailingPE'), 'Trailing PE')
        self.assertEqual(core.field_label('returnOnEquity'), 'Return On Equity ROE')
        self.assertEqual(core.format_field('returnOnEquity', .25), '25.00%')
        df = pd.DataFrame({pd.Timestamp('2024-12-31'): [1000000, 2.5], pd.Timestamp('2025-12-31'): [2000000, float('nan')]}, index=['TotalRevenue', 'DilutedEPS'])
        rows = core.statement_records(df, 'income')
        self.assertEqual(rows[0]['2025-12-31'], 2000000)
        self.assertIsNone(next(r for r in rows if r['Metric'] == 'Diluted EPS')['2025-12-31'])
        self.assertIsNone(next(r for r in rows if r['Metric'] == 'EBITDA')['2024-12-31'])
        with self.assertRaises(ValueError):
            core.statement_records(pd.DataFrame(), 'income')

    def test_brief_marks_missing_data(self):
        text = core.brief('AAPL', {'News': (None, None, False, 'offline')})
        self.assertIn('offline', text)
        self.assertIn('untrusted', text)
        self.assertIn('https://finance.yahoo.com/quote/AAPL/', text)

if __name__ == '__main__':
    unittest.main()
