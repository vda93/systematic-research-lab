"""Day-level qualification fixture; no restricted market rows or network calls."""
import gzip
import importlib
from pathlib import Path
import tempfile
import unittest


class DayQualificationTests(unittest.TestCase):
    def test_day_summary_counts_unknown_time_without_price_disclosure(self):
        module = importlib.import_module('srl.bbo')
        function = getattr(module, 'qualify_day', None)
        self.assertIsNotNone(function, 'reproducible day qualification is not implemented')
        start = 1672531200000000
        rows = ['exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n']
        for offset in (0, 200000, 400000):
            rows.append(f'binance,BTCUSDT,{start+offset},{start+offset},2,101,100,2\n')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.csv.gz'
            path.write_bytes(gzip.compress(''.join(rows).encode(), mtime=0))
            result = function(path, day='2023-01-01')
        self.assertEqual(result['counts']['rows'], 3)
        self.assertEqual(result['known_duration_us'], 650000)
        self.assertEqual(result['longest_known_run_us'], 650000)
        self.assertEqual(result['scheduled_intents'], 86099)
        self.assertEqual(result['maximum_history_eligible_intents'], 0)
        self.assertEqual(result['status'], 'DEV_FAIL_SUPPORT')
        self.assertFalse(any(key in result for key in ('prices', 'ticks', 'intents', 'costs')))

    def test_corrupt_gzip_or_late_invalid_row_never_returns_partial_summary(self):
        module = importlib.import_module('srl.bbo')
        header = 'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n'
        valid = 'binance,BTCUSDT,1672531200000000,1672531200000000,2,101,100,2\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.csv.gz'
            payload = gzip.compress((header + valid * 3).encode(), mtime=0)
            path.write_bytes(payload[:-4])
            with self.assertRaises((EOFError, OSError)):
                module.qualify_day(path, day='2023-01-01')
            path.write_bytes(gzip.compress((header + valid + valid.replace('binance', 'wrong')).encode(), mtime=0))
            with self.assertRaises(ValueError):
                module.qualify_day(path, day='2023-01-01')


if __name__ == '__main__':
    unittest.main()
