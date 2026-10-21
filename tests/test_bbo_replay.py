"""Original clock/order-side scenarios; no provider observations."""
import importlib
import unittest

from srl.bbo import Quote, QuoteUpdate

T = 300_000_000


def api():
    try:
        module = importlib.import_module('srl.bbo_replay')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'causal BBO replay has not been implemented'
    return module


def quote(time, bid=99.5, ask=100.5, amount=2):
    return QuoteUpdate(time, Quote(time, ask, bid, amount, amount), 'VALID')


def history():
    return [quote(time) for time in range(T-60_000_000, T, 200_000)]


class ReplayTests(unittest.TestCase):
    def test_strict_past_intent_inclusive_targets_and_fixed_quantity(self):
        states = [*history(), quote(T-1, 98, 102), quote(T, 149, 150),
                  quote(T+50_000, 99, 101), quote(T+550_000, 99.5, 100.5, .01)]
        audit = []
        result = api().replay_updates(states, start_us=0, first_intent_us=T, last_intent_us=T, audit=audit.append)
        self.assertEqual(result.report['scheduled_intents'], 1)
        self.assertEqual(result.report['exclusions'], {})
        self.assertEqual(result.report['eligible_intents'], 1)
        group = result.report['groups']['shock/550']
        self.assertEqual(group['paired'], 1)
        self.assertEqual(group['either_depth_fail'], 1)
        self.assertIn('post_outcome_depth_subset', group)
        self.assertEqual(group['post_outcome_depth_subset']['count'], 0)
        self.assertAlmostEqual(group['mean_saving_bps'], 49.525)
        self.assertEqual(result.savings['shock/550'], [49.525])
        self.assertEqual(audit[0]['side'], 1)
        self.assertEqual(audit[0]['quantity'], 1)
        self.assertEqual(audit[0]['intent_midpoint'], 100)
        self.assertEqual(audit[0]['targets']['50']['price'], 101)
        self.assertEqual(audit[0]['targets']['550']['price'], 100.5)

    def test_quote_after_target_cannot_replace_missing_or_stale_target(self):
        states = [*history(), quote(T-1, 98, 102), quote(T+50_001, 89, 90)]
        audit = []
        result = api().replay_updates(states, start_us=0, first_intent_us=T, last_intent_us=T, audit=audit.append)
        self.assertEqual(audit[0]['targets']['50']['price'], 102)
        self.assertIsNone(audit[0]['targets']['550'])
        self.assertEqual(result.report['groups']['shock/550']['paired'], 0)
        self.assertEqual(result.report['groups']['shock/550']['missing_delayed'], 1)

    def test_all_scheduled_intents_reconcile_and_sides_follow_epoch_parity(self):
        result = api().replay_updates([], start_us=0, first_intent_us=T, last_intent_us=T+1_000_000)
        self.assertEqual(result.report['scheduled_intents'], 2)
        self.assertEqual(result.report['exclusions'], {'MISSING_INTENT_STATE': 2})
        states = [*history(), quote(T-1, 98, 102)]
        for time in range(T, T+2_200_000, 200_000):
            states.append(quote(time, 98, 102))
        audit = []
        result = api().replay_updates(states, start_us=0, first_intent_us=T, last_intent_us=T+1_000_000,
                                      audit=audit.append)
        self.assertEqual([row['side'] for row in sorted(audit, key=lambda row: row['intent_us'])], [1, -1])
        self.assertEqual(result.report['scheduled_intents'], result.report['eligible_intents'] +
                         sum(result.report['exclusions'].values()))

    def test_late_source_failure_cannot_return_an_early_scientific_result(self):
        def broken():
            yield from history()
            yield quote(T-1, 98, 102)
            yield quote(T+2_000_000)
            raise ValueError('synthetic corrupt late row')
        with self.assertRaises(ValueError):
            api().replay_updates(broken(), start_us=0, first_intent_us=T, last_intent_us=T)

    def test_excluded_intent_keeps_concurrent_pre_outcome_failure_flags(self):
        audit = []
        result = api().replay_updates([quote(T-1, 98, 102, .001)], start_us=0,
                                      first_intent_us=T, last_intent_us=T, audit=audit.append)
        self.assertEqual(result.report['exclusions'], {'INSUFFICIENT_INTENT_DEPTH': 1})
        self.assertIn('flags', audit[0])
        self.assertIn('INSUFFICIENT_INTENT_DEPTH', audit[0]['flags'])
        self.assertIn('MEDIAN_AMBIGUOUS', audit[0]['flags'])


if __name__ == '__main__':
    unittest.main()
