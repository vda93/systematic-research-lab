"""Bootstrap checks with explicit small reference paths."""

import unittest

from srl.resampling import circular_indices, paired_daily_bootstrap, percentile


DATES = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]


class ResamplingTests(unittest.TestCase):
    def test_circular_blocks_wrap_and_truncate_at_exact_sample_length(self):
        class Starts:
            def __init__(self):
                self.starts = iter([4, 3])

            def randrange(self, n):
                assert n == 5
                return next(self.starts)

        self.assertEqual(circular_indices(5, 3, Starts()), [4, 0, 1, 3, 4])

    def test_linear_percentile_between_order_statistics(self):
        self.assertEqual(percentile([30, 0, 10, 20], .25), 7.5)
        self.assertEqual(percentile([2], .975), 2)
        self.assertEqual(percentile([-1e308, 1e308], .5), 0)
        for values, q in [([], .5), ([1], -1), ([1], float("nan")), ([float("inf")], .5)]:
            with self.assertRaises(ValueError):
                percentile(values, q)

    def test_one_seeded_draw_matches_hand_calculated_mean(self):
        # Random(7) chooses starts 2,1: two length-two blocks yield 2,3,1,2.
        control = dict(zip(DATES, [0, 0, 0, 0]))
        treatment = dict(zip(DATES, [0, 2, 4, 8]))
        result = paired_daily_bootstrap(control, treatment, block_size=2, repetitions=1, seed=7)
        self.assertEqual(result, {
            "observed_mean_delta": 3.5, "ci_low": 4.5, "ci_high": 4.5,
            "positive_fraction": 1, "block_size": 2, "repetitions": 1,
            "seed": 7, "sample_days": 4,
            "method": "paired circular moving-block bootstrap",
        })

    def test_identical_paths_have_zero_pairing_noise(self):
        path = dict(zip(DATES, [100, -3, 7, -54]))
        result = paired_daily_bootstrap(path, dict(reversed(list(path.items()))),
                                        block_size=2, repetitions=29, seed=92)
        self.assertEqual([result[k] for k in ["observed_mean_delta", "ci_low", "ci_high", "positive_fraction"]], [0, 0, 0, 0])

    def test_seeded_interval_interpolates_distinct_replicate_means(self):
        # Seed 7 starts: (2,1),(3,0),(0,0),(2,0); means 4.5,2.5,1,3.5.
        result = paired_daily_bootstrap(dict.fromkeys(DATES, 0), dict(zip(DATES, [0, 2, 4, 8])),
                                        block_size=2, repetitions=4, seed=7)
        self.assertAlmostEqual(result["ci_low"], 1.1125)
        self.assertAlmostEqual(result["ci_high"], 4.425)

    def test_constant_effect_survives_every_resample(self):
        control = dict(zip(DATES, [3, -9, 25, 0]))
        treatment = dict(zip(DATES, [5, -7, 27, 2]))
        result = paired_daily_bootstrap(control, treatment, block_size=1, repetitions=31, seed=6)
        self.assertEqual([result[k] for k in ["observed_mean_delta", "ci_low", "ci_high"]], [2, 2, 2])

    def test_bad_calendars_parameters_and_arithmetic_fail_closed(self):
        good = dict(zip(DATES, [0, 0, 0, 0]))
        bad_paths = [
            {"2024-01-01": 0},
            dict(zip(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-05"], [0] * 4)),
            dict(zip(["20240101", *DATES[1:]], [0] * 4)),
            dict(zip(DATES, [0, 0, float("nan"), 0])),
            dict(zip(DATES, [0, 0, float("inf"), 0])),
        ]
        for bad in bad_paths:
            with self.subTest(path=bad), self.assertRaises(ValueError):
                paired_daily_bootstrap(bad, bad, block_size=1, repetitions=2, seed=1)
        for parameters in [dict(block_size=True), dict(block_size=0), dict(block_size=3),
                           dict(repetitions=False), dict(repetitions=0), dict(seed=True), dict(seed=1.5)]:
            args = dict(block_size=1, repetitions=2, seed=1) | parameters
            with self.subTest(args=args), self.assertRaises(ValueError):
                paired_daily_bootstrap(good, good, **args)
        with self.assertRaises(ValueError):
            paired_daily_bootstrap(good, {d: 0 for d in DATES[1:]}, block_size=1, repetitions=2, seed=1)
        for c, t in [(-1e308, 1e308), (0, 1e308)]:
            with self.assertRaises(ValueError):
                paired_daily_bootstrap(dict.fromkeys(DATES, c), dict.fromkeys(DATES, t), block_size=1, repetitions=2, seed=1)


if __name__ == "__main__":
    unittest.main()
