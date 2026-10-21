"""Independent synthetic CDF and bootstrap checks; no market observations."""
from fractions import Fraction
import importlib
import math
import random
import sys
import unittest


def api():
    try:
        module = importlib.import_module('srl.bbo_statistics')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'pure BBO statistical helpers are not implemented'
    return module


def weighted_oracle(days):
    """Aggregate a small exact probability table, independently of merge/LCM."""
    contributing = [day for day in days if day]
    masses = {}
    for day in contributing:
        weight = Fraction(1, len(contributing) * len(day))
        for saving in day:
            penalty = -float(saving)
            masses[penalty] = masses.get(penalty, Fraction()) + weight
    result = {}
    for p in (50, 90, 95, 99):
        cumulative = Fraction()
        result[str(p)] = None
        for value in sorted(masses):
            cumulative += masses[value]
            if cumulative >= Fraction(p, 100):
                result[str(p)] = value
                break
    return result


def direct_bootstrap(values, block):
    """Expand every sampled index and sum rationals; no production helpers."""
    rng = random.Random(20261021)
    n = len(values)
    means = []
    for _ in range(20000):
        selected = []
        while len(selected) < n:
            start = rng.randrange(n)
            selected.extend(values[(start + offset) % n]
                            for offset in range(min(block, n-len(selected))))
        means.append(float(sum((Fraction(x) for x in selected), Fraction()) / n))
    ordered = sorted(means)
    endpoints = []
    for q in (.025, .975):
        rank = (len(ordered)-1)*q
        lo, hi = math.floor(rank), math.ceil(rank)
        weight = rank-lo
        endpoints.append(math.fsum(((1-weight)*ordered[lo], weight*ordered[hi])))
    return endpoints


class ImportContractTests(unittest.TestCase):
    def test_helpers_exist(self):
        module = api()
        self.assertTrue(all(callable(getattr(module, name)) for name in
                            ('distribution_summary', 'equal_day_inference', 'weighted_penalty_quantiles')))


class StatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.subject = api()
        except AssertionError:
            raise unittest.SkipTest('import contract supplies the implementation failure')

    def test_distribution_lower_cdf_and_penalty_sign_are_hand_calculated(self):
        result = self.subject.distribution_summary([-3., 1., 2., 4.])
        self.assertEqual(result['count'], 4)
        self.assertEqual(result['mean'], 1.)
        self.assertEqual(result['sample_sd'], math.sqrt(Fraction(26, 3)))
        self.assertEqual(result['median_saving'], 1.)
        self.assertEqual(result['penalty_quantiles'], {'50': -2., '90': 3., '95': 3., '99': 3.})
        self.assertEqual(result['worst_penalty'], 3.)
        self.assertEqual(self.subject.distribution_summary([2., 2.])['worst_penalty'], -2.)

    def test_empty_and_singleton_descriptions_are_explicit(self):
        empty = self.subject.distribution_summary([])
        self.assertEqual(empty['count'], 0)
        for key in ('mean', 'sample_sd', 'median_saving', 'worst_penalty'):
            self.assertIsNone(empty[key])
        self.assertEqual(empty['penalty_quantiles'], dict.fromkeys(('50', '90', '95', '99')))
        one = self.subject.distribution_summary([-5.])
        self.assertEqual(one['mean'], -5.)
        self.assertIsNone(one['sample_sd'])
        self.assertEqual(one['penalty_quantiles'], dict.fromkeys(('50', '90', '95', '99'), 5.))

    def test_finite_validation_excludes_boolean_text_overflow_and_nonfinite(self):
        for invalid in (True, '1', float('nan'), float('inf'), -float('inf'), 10**1000):
            with self.subTest(invalid=invalid):
                for function in (self.subject.distribution_summary, self.subject.equal_day_inference):
                    with self.assertRaises(ValueError):
                        function([0., invalid])
                with self.assertRaises(ValueError):
                    self.subject.weighted_penalty_quantiles([[0.], [invalid]])

    def test_extreme_finite_mean_avoids_sum_overflow(self):
        maximum = sys.float_info.max
        result = self.subject.distribution_summary([maximum]*4)
        self.assertEqual(result['mean'], maximum)
        self.assertEqual(result['sample_sd'], 0.)
        self.assertEqual(self.subject.distribution_summary([math.ulp(0.)]*4)['mean'], math.ulp(0.))
        with self.assertRaises(ValueError):
            self.subject.distribution_summary([maximum, -maximum])

    def test_fewer_than_four_days_never_gets_a_bootstrap_interval(self):
        for values in ([], [1.], [1., -1.], [-1., 0., 2.]):
            result = self.subject.equal_day_inference(values)
            self.assertEqual(result['count'], len(values))
            self.assertIsNone(result['ci95'])
            self.assertIsNone(result['sensitivity_ci95'])
            self.assertEqual(result['status'], 'DESCRIPTIVE_FEWER_THAN_FOUR_DAYS')
        described = self.subject.equal_day_inference([-1., 0., 2.])
        self.assertEqual(described['sign_counts'], {'negative': 1, 'zero': 1, 'positive': 1})
        self.assertEqual(described['leave_one_day_out'], [1., .5, -.5])
        self.assertEqual(self.subject.equal_day_inference([7.])['leave_one_day_out'], [None])
        self.assertEqual(self.subject.equal_day_inference([])['leave_one_day_out'], [])

    def test_constant_days_have_degenerate_primary_and_sensitivity_intervals(self):
        for value in (-3., 0., 2.):
            result = self.subject.equal_day_inference([value]*4)
            self.assertEqual(result['ci95'], [value, value])
            self.assertEqual(result['sensitivity_ci95'], [value, value])
            self.assertEqual(result['leave_one_day_out'], [value]*4)
            self.assertNotIn('p_value', result)
            self.assertNotIn('positive_fraction', result)

    def test_primary_and_wrapped_truncated_sensitivity_match_direct_rational_draws(self):
        values = [-2., .5, 0., 3., 1.]
        original = values.copy()
        result = self.subject.equal_day_inference(values)
        self.assertEqual(result['ci95'], direct_bootstrap(values, 1))
        self.assertEqual(result['sensitivity_ci95'], direct_bootstrap(values, 2))
        self.assertEqual(result['bootstrap_repetitions'], 20000)
        self.assertEqual(result['seed'], 20261021)
        self.assertEqual(values, original)

    def test_equal_day_weights_differ_from_pooling_and_keep_empty_counts(self):
        result = self.subject.weighted_penalty_quantiles([[-10.], [0.]*9, []])
        self.assertEqual(result['quantiles'], {'50': 0., '90': 10., '95': 10., '99': 10.})
        self.assertEqual(result['contributing_days'], 2)
        self.assertEqual(result['planned_days'], 3)
        self.assertEqual(result['empty_days'], 1)
        self.assertEqual(result['intent_count'], 10)
        self.assertEqual(self.subject.weighted_penalty_quantiles([[], []])['quantiles'],
                         dict.fromkeys(('50', '90', '95', '99')))

    def test_weighted_ties_and_unequal_prime_counts_match_exact_fraction_cdf(self):
        rng = random.Random(1541)
        for _ in range(70):
            days = [[rng.choice([-3., -.5, 0., 1., 7.]) for _ in range(rng.choice([0, 2, 3, 5, 7, 11]))]
                    for _ in range(rng.randrange(1, 8))]
            original = [day.copy() for day in days]
            self.assertEqual(self.subject.weighted_penalty_quantiles(days)['quantiles'], weighted_oracle(days))
            self.assertEqual(days, original)
        # Exact half-mass equality must select the lower penalty, without epsilon.
        result = self.subject.weighted_penalty_quantiles([[5.]*3, [-5.]*7])
        self.assertEqual(result['quantiles']['50'], -5.)


if __name__ == '__main__':
    unittest.main()
