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
            for view in ['Financials', 'News', 'AI brief']:
                at.radio[1].set_value(view).run()
                self.assertFalse(at.exception)
                if view == 'Financials':
                    at.radio[2].set_value('quarterly').run()
                    self.assertFalse(at.exception)
            next(b for b in at.button if b.label == 'Generate AI brief').click().run()
            self.assertFalse(at.exception)
            self.assertIn('Research packet: AAPL', at.text_area[0].value)
            self.assertIn('Quarterly cashflow', at.text_area[0].value)
            at.radio[0].set_value('Macro').run()
            self.assertFalse(at.exception)

if __name__ == '__main__':
    unittest.main()
