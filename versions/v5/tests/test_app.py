"""Offline UI smoke tests: no live data or personal database needed."""
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
from streamlit.testing.v1 import AppTest
import core

class AppTests(unittest.TestCase):
    def test_workspaces_and_export(self):
        def fake(key, ttl, loader, refresh=False):
            if key.startswith('prices:'):
                data = [{'Date': '2025-01-02', 'Close': 100, 'Open': 99, 'High': 101, 'Low': 98, 'Volume': 1000}, {'Date': '2025-01-03', 'Close': 102, 'Open': 100, 'High': 103, 'Low': 99, 'Volume': 1200}]
            elif key.startswith('info:'):
                data = {'longName': 'Fixture company', 'currency': 'USD'}
            elif key.startswith('news:'):
                data = {'items': [{'title': 'profits rise', 'link': 'https://example.org', 'source': 'Test', 'published': '2025-01-03', 'score': .67}], 'feed_errors': []}
            elif key.startswith('statement:'):
                data = [{'Metric': 'Revenue', '2025-12-31': 1000000}, {'Metric': 'Diluted EPS', '2025-12-31': 2.5}]
            else:
                data = [{'Date': '2025-01-01', 'Value': 4.2}]
            return data, '2025-01-03T00:00:00+00:00', False, None
        with tempfile.TemporaryDirectory() as tmp, patch.object(core, 'DB', Path(tmp)/'test.db'), patch.object(core, 'cached', side_effect=fake):
            at = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
            self.assertFalse(at.exception)
            self.assertEqual(at.radio[0].label, 'Workspace')
            self.assertTrue(any(e.label == 'Fundamentals' for e in at.expander))
            for view in ['Financials', 'News', 'AI brief']:
                at.radio[1].set_value(view).run()
                self.assertFalse(at.exception)
                if view == 'Financials':
                    at.radio[2].set_value('quarterly').run()
                    self.assertFalse(at.exception)
            next(b for b in at.button if b.label == 'Generate AI brief').click().run()
            self.assertFalse(at.exception)
            self.assertIn('Research document: AAPL', at.session_state['brief_v4'][1])
            self.assertIn('Quarterly — Cash flow', at.session_state['brief_v4'][1])
            at.radio[0].set_value('Macro').run()
            self.assertFalse(at.exception)
            self.assertNotIn('US 10-year Treasury', [c.label for c in at.checkbox])
            self.assertEqual(len(at.checkbox), len(core.ECONOMIC_SERIES))
            yield_table = next(d.value for d in at.dataframe if 'Country' in d.value.columns)
            self.assertEqual(list(yield_table.columns), ['Country','10Y yield (%)','MoM (bp)','Observation'])
            next(w for w in at.selectbox if w.label == 'Indicator country').set_value('Canada').run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.checkbox), 1)
            next(w for w in at.selectbox if w.label == 'Indicator country').set_value('United States').run()
            at.checkbox[0].check().run()
            self.assertFalse(at.exception)
            next(m for m in at.multiselect if m.label == 'Countries / map and yield table').set_value([]).run()
            self.assertFalse(at.exception)
            next(m for m in at.multiselect if m.label == 'Commodity contracts').set_value([]).run()
            self.assertFalse(at.exception)

class FailureUITests(unittest.TestCase):
    def test_missing_sources_and_right_watchlist(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(core, 'DB', Path(tmp)/'test.db'), patch.object(core, 'cached', return_value=(None,None,False,'offline')):
            at = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
            self.assertFalse(at.exception)
            self.assertTrue(at.warning)
            next(b for b in at.button if b.label == '＋ Save ticker').click().run()
            self.assertEqual(core.watchlist(), ['AAPL'])
            next(b for b in at.button if b.label == 'Open saved').click().run()
            self.assertFalse(at.exception)
            at.radio[1].set_value('Financials').run()
            self.assertFalse(at.exception)
            at.radio[2].set_value('quarterly').run()
            self.assertFalse(at.exception)
            at.radio[0].set_value('Macro').run()
            self.assertFalse(at.exception)
            self.assertTrue(at.dataframe)
            at.radio[0].set_value('Ticker').run()
            self.assertEqual(at.text_input[0].value, 'AAPL')
            self.assertFalse(at.exception)

if __name__ == '__main__':
    unittest.main()
