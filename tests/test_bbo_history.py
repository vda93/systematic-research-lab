"""Partial-identification fixtures and an independent completion oracle."""
from fractions import Fraction
import importlib
import itertools
import math
import unittest

from srl.bbo import Quote, QuoteUpdate


def api():
    try:
        module = importlib.import_module('srl.bbo_history')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'completion-robust history feature is not implemented'
    return module


class HistoryTests(unittest.TestCase):
    def test_bounds_cover_all_small_numeric_completions_including_half_ties(self):
        module = api()
        for observed in ([], [2], [2, 4], [2, 4, 4], [2, 2, 4, 6]):
            for total in range(max(1, len(observed)), 6):
                bounds = module.median_bounds([(x, 1) for x in observed], total_us=total)
                for missing in itertools.product((-100, 1, 3, 100), repeat=total-len(observed)):
                    complete = sorted([*observed, *missing])
                    median = complete[(total-1)//2]
                    self.assertLessEqual(bounds.lower, median)
                    self.assertGreaterEqual(bounds.upper, median)
                    for current in (1., 6., 12., 30.):
                        label = module.classify(current, bounds)
                        if label == 'shock':
                            self.assertGreaterEqual(Fraction(current), 3*Fraction(median))
                        elif label == 'normal':
                            self.assertLess(Fraction(current), 3*Fraction(median))
        half = module.median_bounds([(2., 1), (4., 1)], total_us=4)
        self.assertEqual((half.lower, half.upper), (-math.inf, 4.))

    def test_exact_ratio_threshold_does_not_round_a_near_tie_into_a_shock(self):
        module = api()
        bound = math.nextafter(1/3, math.inf)
        self.assertEqual(3*bound, 1.)
        self.assertLess(Fraction(1.), 3*Fraction(bound))
        bounds = module.median_bounds([(bound, 60)], total_us=60)
        self.assertEqual(module.classify(1., bounds), 'normal')
        self.assertEqual(module.classify(3., module.median_bounds([(1., 60)], total_us=60)), 'shock')

    def test_expiry_unknown_time_and_rolling_eviction_are_not_imputed(self):
        module = api()
        history = module.RollingHistory(window_us=60, max_age_us=20)
        first = QuoteUpdate(0, Quote(0, 101, 99, 2, 2), 'VALID')
        second = QuoteUpdate(30, Quote(30, 102, 98, 2, 2), 'VALID')
        history.advance(20, first)
        history.advance(30, first)
        history.advance(60, second)
        bounds = history.bounds()
        self.assertEqual((bounds.known_us, bounds.unknown_us), (40, 20))
        self.assertEqual((bounds.lower, bounds.upper), (200., 400.))
        self.assertEqual(module.classify(1300., bounds), 'shock')
        self.assertEqual(module.classify(500., bounds), 'normal')
        self.assertEqual(module.classify(1000., bounds), 'ambiguous')
        history.advance(100, QuoteUpdate(60, None, 'AMBIGUOUS_TIMESTAMP'))
        later = history.bounds()
        self.assertEqual((later.known_us, later.unknown_us), (10, 50))
        self.assertEqual((bounds.known_us, bounds.unknown_us), (40, 20))

    def test_bad_durations_clocks_and_numerical_inputs_fail_closed(self):
        module = api()
        for known, total in [([(1., 0)], 60), ([(1., True)], 60), ([(math.nan, 1)], 60),
                             ([(1., 61)], 60), ([(1., 1)], 0), ([(1., 1)], True)]:
            with self.subTest(known=known, total=total), self.assertRaises(ValueError):
                module.median_bounds(known, total_us=total)
        for kwargs in (dict(window_us=0), dict(max_age_us=False)):
            with self.assertRaises(ValueError):
                module.RollingHistory(**kwargs)
        history = module.RollingHistory()
        history.advance(10, None)
        with self.assertRaises(ValueError):
            history.advance(9, None)
        with self.assertRaises(ValueError):
            history.advance(20, QuoteUpdate(15, Quote(15, 101, 99, 1, 1), 'future'))
        for value in (0, -1, True, math.nan, math.inf):
            with self.assertRaises(ValueError):
                module.classify(value, module.median_bounds([(1., 60)], total_us=60))


if __name__ == '__main__':
    unittest.main()
