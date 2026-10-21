"""Original synthetic BBO fixtures; no provider rows or financial evidence."""
from datetime import datetime, timezone
import csv
import importlib
import io
import unittest

START = int(datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp()) * 1_000_000
HEADER = 'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n'


def api():
    try:
        module = importlib.import_module('srl.bbo')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'frozen BBO qualification contract is not implemented'
    return module


def row(offset, *, ask='101', bid='100', amount='2', exchange='binance', symbol='BTCUSDT'):
    return f'{exchange},{symbol},{START+offset},{START+offset},{amount},{ask},{bid},{amount}\n'


class BBOParsingTests(unittest.TestCase):
    def read(self, rows):
        module = api()
        counts = module.QuoteCounts()
        updates = list(module.iter_updates(io.StringIO(HEADER + rows), day='2023-01-01', counts=counts))
        return updates, counts

    def test_schema_and_one_valid_original_fixture(self):
        updates, counts = self.read(row(1) + row(2))
        self.assertEqual([x.local_us for x in updates], [START + 1, START + 2])
        self.assertEqual((updates[0].quote.ask, updates[0].quote.bid), (101, 100))
        self.assertEqual(counts.rows, 2)
        self.assertEqual(counts.valid_states, 2)

    def test_duplicate_collapses_but_different_state_at_same_time_is_unknown(self):
        updates, counts = self.read(row(1) * 2 + row(2) + row(2, ask='102') + row(3))
        self.assertEqual(len(updates), 3)
        self.assertEqual(counts.duplicate_rows, 1)
        self.assertEqual(counts.conflicting_timestamps, 1)
        self.assertIsNone(updates[1].quote)
        self.assertEqual(updates[1].reason, 'AMBIGUOUS_TIMESTAMP')
        self.assertIsNotNone(updates[2].quote)

    def test_nonfinite_nonpositive_locked_crossed_and_malformed_prices_invalidate_state(self):
        for changed in [dict(ask='nan'), dict(amount='0'), dict(bid='101'), dict(bid='102'),
                        dict(ask='inf'), dict(bid='not-a-number')]:
            with self.subTest(changed=changed):
                updates, counts = self.read(row(1) + row(2, **changed) + row(3))
                self.assertIsNone(updates[1].quote)
                self.assertIsNotNone(updates[2].quote)
                self.assertEqual(counts.invalid_rows, 1)

    def test_file_errors_are_not_reordered_or_silently_dropped(self):
        module = api()
        bad = [HEADER.replace('ask_amount', 'ask_size') + row(1),
               HEADER + row(2) + row(1), HEADER + row(-1),
               HEADER + row(86_400_000_000), HEADER + row(1, exchange='other'),
               HEADER + row(1, symbol='ETHUSDT'), HEADER + row(1).rstrip() + ',extra\n',
               HEADER + row(1).replace(str(START+1), str(START+1)+'.0', 1)]
        for text in bad:
            with self.subTest(text=text), self.assertRaises(ValueError):
                list(module.iter_updates(io.StringIO(text), day='2023-01-01', counts=module.QuoteCounts()))
        for day in ['20230101', 'bad']:
            with self.subTest(day=day), self.assertRaises(ValueError):
                list(module.iter_updates(io.StringIO(HEADER), day=day, counts=module.QuoteCounts()))

    def test_invalid_and_valid_at_one_timestamp_remain_ambiguous(self):
        updates, counts = self.read(row(1, ask='nan') + row(1) + row(2))
        self.assertIsNone(updates[0].quote)
        self.assertEqual(updates[0].reason, 'AMBIGUOUS_TIMESTAMP')
        self.assertEqual(counts.conflicting_timestamps, 1)

    def test_same_bbo_with_different_exchange_clock_is_not_false_conflict(self):
        second = row(1).replace(str(START + 1), str(START), 1)
        updates, counts = self.read(row(1) + second)
        self.assertEqual(len(updates), 1)
        self.assertIsNotNone(updates[0].quote)
        self.assertEqual(counts.duplicate_rows, 0)
        self.assertEqual(counts.conflicting_timestamps, 0)

    def test_malformed_csv_header_is_a_file_qualification_error(self):
        module = api()
        try:
            with self.assertRaises(ValueError):
                list(module.iter_updates(io.StringIO('"unclosed'), day='2023-01-01', counts=module.QuoteCounts()))
        except csv.Error:
            self.fail('header parsing must expose ValueError consistently with other file failures')


class HistoryCoverageTests(unittest.TestCase):
    def test_unknown_states_and_expiry_break_continuous_history(self):
        module = api()
        function = getattr(module, 'known_runs', None)
        self.assertIsNotNone(function, 'continuous-history qualification has not been implemented')
        quote = module.Quote(0, 101, 100, 2, 2)
        states = [module.QuoteUpdate(t, quote if valid else None, 'fixture') for t, valid in
                  [(0, True), (200_000, True), (400_000, False), (500_000, True), (800_000, True)]]
        self.assertEqual(list(function(states, end_us=1_000_000)),
                         [(0, 400_000), (500_000, 750_000), (800_000, 1_000_000)])

    def test_grid_counter_includes_exact_history_and_expiry_boundaries(self):
        module = api()
        function = getattr(module, 'history_grid_count', None)
        self.assertIsNotNone(function, 'history grid support counter has not been implemented')
        runs = [(0, 62_000_000), (63_500_000, 124_000_000)]
        # First run: intents60,61,62. Second:124 (window begins64).
        self.assertEqual(function(runs, first_intent_us=0, last_intent_us=130_000_000), 4)
        self.assertEqual(function(runs, first_intent_us=61_000_000, last_intent_us=61_000_000), 1)

    def test_continuous_history_matches_independent_microsecond_grid(self):
        module = api()
        function = getattr(module, 'known_runs', None)
        self.assertIsNotNone(function, 'continuous-history qualification has not been implemented')
        quote = module.Quote(0, 101, 100, 2, 2)
        states = [module.QuoteUpdate(t, quote if valid else None, 'fixture') for t, valid in
                  [(0, True), (3, True), (7, False), (8, True), (14, True)]]
        actual = list(function(states, end_us=20, max_age_us=4))
        # Check each unit interval independently: most recent received state and its age.
        expected = set()
        for tick in range(20):
            earlier = [s for s in states if s.local_us <= tick]
            if earlier and earlier[-1].quote is not None and tick < earlier[-1].local_us + 4:
                expected.add(tick)
        covered = {tick for start, end in actual for tick in range(start, end)}
        self.assertEqual(covered, expected)

    def test_touching_runs_form_one_continuous_history(self):
        module = api()
        self.assertEqual(module.history_grid_count([(0, 60_000_000), (60_000_000, 120_000_000)],
                                                  first_intent_us=60_000_000,
                                                  last_intent_us=120_000_000), 61)

    def test_bad_state_clocks_and_grid_intervals_fail_instead_of_salvaging_prefix(self):
        module = api()
        quote = module.Quote(0, 101, 100, 2, 2)
        for times in ([0, 0], [2, 1], [0, 10]):
            with self.subTest(times=times), self.assertRaises(ValueError):
                list(module.known_runs([module.QuoteUpdate(t, quote, 'fixture') for t in times], end_us=10))
        for args in (dict(end_us=10, max_age_us=0), dict(end_us=10, max_age_us=True), dict(end_us=1.5)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                list(module.known_runs([], **args))
        self.assertEqual(list(module.known_runs([], end_us=10)), [])
        self.assertEqual(list(module.known_runs([module.QuoteUpdate(0, None, 'unknown')], end_us=10)), [])
        for runs in ([(2, 1)], [(0, 0)], [(0, 9), (8, 10)], [(True, 10)]):
            with self.subTest(runs=runs), self.assertRaises(ValueError):
                module.history_grid_count(runs, first_intent_us=0, last_intent_us=1_000_000)
        for bounds in ((1, 1_000_000), (1_000_000, 0), (True, 1_000_000)):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                module.history_grid_count([], first_intent_us=bounds[0], last_intent_us=bounds[1])
        self.assertEqual(module.history_grid_count([], first_intent_us=0, last_intent_us=0), 0)


if __name__ == '__main__':
    unittest.main()
