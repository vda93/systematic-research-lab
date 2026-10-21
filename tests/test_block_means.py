"""A rational oracle checks exact block aggregation independently of prefixes."""
from fractions import Fraction
from decimal import Decimal, localcontext
import importlib
import math
import random
import struct
import sys
import unittest


def subject():
    try:
        module = importlib.import_module('srl.block_means')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'exact circular block mean sampler has not been implemented'
    return module.circular_block_means


def rational_oracle(values, block_size, repetitions, seed):
    """Enumerate every selected observation; no shared production helper."""
    rng = random.Random(seed)
    output = []
    for _ in range(repetitions):
        picked = []
        while len(picked) < len(values):
            start = rng.randrange(len(values))
            for offset in range(min(block_size, len(values) - len(picked))):
                picked.append(Fraction(float(values[(start + offset) % len(values)])))
        output.append(float(sum(picked, Fraction()) / len(values)))
    return tuple(output)


class BlockMeansTests(unittest.TestCase):
    def test_released_index_helper_selects_the_same_observations(self):
        from srl.resampling import circular_indices
        values = [1., -.5, 0., 3., 11., -7., .125]
        for block in range(1, len(values) // 2 + 1):
            rng = random.Random(931)
            expected = tuple(float(sum((Fraction(values[i]) for i in
                                       circular_indices(len(values), block, rng)), Fraction()) / len(values))
                             for _ in range(31))
            self.assertEqual(subject()(values, block_size=block, repetitions=31, seed=931), expected)

    def test_decimal_oracle_for_random_bit_patterns_and_rounding_boundary(self):
        generator = random.Random(281)
        with localcontext() as context:
            context.prec = 2500
            for _ in range(16):
                values = []
                while len(values) < 8:
                    value = struct.unpack('!d', generator.getrandbits(64).to_bytes(8, 'big'))[0]
                    if math.isfinite(value):
                        values.append(value)
                rng = random.Random(49)
                expected = []
                for _ in range(13):
                    selected = []
                    while len(selected) < len(values):
                        start = rng.randrange(len(values))
                        selected.extend(values[(start + offset) % len(values)]
                                        for offset in range(min(3, len(values) - len(selected))))
                    expected.append(float(sum(map(Decimal.from_float, selected), Decimal()) / len(values)))
                self.assertEqual(subject()(values, block_size=3, repetitions=13, seed=49), tuple(expected))
        # The documented input contract converts integers before exact aggregation.
        values = [2 ** 53 + 1, -2 ** 53, 0, 0]
        self.assertEqual(subject()(values, block_size=2, repetitions=19, seed=5),
                         rational_oracle(list(map(float, values)), 2, 19, 5))
        self.assertTrue(all(math.copysign(1., x) == 1 for x in
                            subject()([-0.] * 4, block_size=2, repetitions=3, seed=0)))

    def test_hand_draw_and_exact_length(self):
        sample = subject()([0, 2, 4, 8], block_size=2, repetitions=4, seed=7)
        self.assertEqual(sample, (4.5, 2.5, 1.0, 3.5))

    def test_every_block_length_matches_independent_rational_oracle(self):
        sampler = subject()
        for values in ([0, 0, 0, 0], [3, -2, 7, 0, 11],
                       [1e16, 1, -1e16, 3, -.25, .1, -1e-100],
                       [sys.float_info.max, -sys.float_info.max, .25, -.5],
                       [math.ulp(0.), 0., -math.ulp(0.), 2 * math.ulp(0.)]):
            for block in range(1, len(values) // 2 + 1):
                with self.subTest(values=values, block=block):
                    self.assertEqual(sampler(values, block_size=block, repetitions=41, seed=94),
                                     rational_oracle(values, block, 41, 94))

    def test_seed_prefix_and_input_are_preserved(self):
        sampler = subject()
        values = [1., -.3, 0., 9., -2.]
        original = values.copy()
        args = dict(block_size=2, seed=-91)
        short = sampler(values, repetitions=3, **args)
        self.assertEqual(short, sampler(values, repetitions=31, **args)[:3])
        self.assertEqual(values, original)

    def test_large_constant_mean_does_not_overflow_intermediate_sum(self):
        value = sys.float_info.max
        self.assertEqual(subject()([value] * 4, block_size=2, repetitions=5, seed=0), (value,) * 5)

    def test_parameters_and_nonfinite_or_non_numeric_values_fail_closed(self):
        sampler = subject()
        for values in ([], [1, 2, 3], [True, 0, 0, 0], ['1', 0, 0, 0],
                       [float('nan'), 0, 0, 0], [float('inf'), 0, 0, 0],
                       [10 ** 1000, 0, 0, 0]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                sampler(values, block_size=1, repetitions=2, seed=0)
        for changed in (dict(block_size=0), dict(block_size=True), dict(block_size=3),
                        dict(repetitions=0), dict(repetitions=True), dict(seed=False), dict(seed=.5)):
            args = dict(block_size=1, repetitions=2, seed=0) | changed
            with self.subTest(args=args), self.assertRaises(ValueError):
                sampler([0, 1, 2, 3], **args)


if __name__ == '__main__':
    unittest.main()
