"""Original synthetic order-side paths; no provider prices or execution evidence."""
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
import importlib
import math
import random
import unittest

from srl.bbo import Quote


def api():
    try:
        module = importlib.import_module('srl.bbo_accounting')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'the frozen quote-accounting kernel is not implemented'
    return module


def quote(bid=99.0, ask=101.0, amount=2.0):
    return Quote(0, ask, bid, amount, amount)


def decimal_oracle(intent_midpoint, baseline, delayed, side, fee=5.0, slippage=0.5):
    """Independent dollar-cost calculation with quantity fixed at intent."""
    with localcontext() as context:
        context.prec = 100
        d = lambda value: Decimal.from_float(float(value))
        notional = Decimal(100)
        quantity = notional / d(intent_midpoint)
        prices = [d(q.ask if side == 1 else q.bid) for q in (baseline, delayed)]
        costs = [Decimal(side) * quantity * (p - d(intent_midpoint))
                 + d(fee) / Decimal(10_000) * quantity * p for p in prices]
        return float((costs[0] - costs[1]) / notional * Decimal(10_000) - d(slippage))


class QuoteAccountingTests(unittest.TestCase):
    def test_frozen_midpoint_spread_order_and_crossing_sides(self):
        module = api()
        q = quote(99.0, 101.0)
        self.assertEqual(module.midpoint(q), 100.0)
        self.assertEqual(module.spread(q), 200.0)
        self.assertEqual(module.crossing_price(q, 1), 101.0)
        self.assertEqual(module.crossing_price(q, -1), 99.0)
        for bid, ask in [(0.1, 0.10000000000000003), (1.0, math.nextafter(1.0, math.inf)),
                         (1e300, math.nextafter(1e300, math.inf))]:
            q = quote(bid, ask)
            mid = bid + (ask - bid) / 2
            self.assertEqual(module.midpoint(q), mid)
            self.assertEqual(module.spread(q), (ask - bid) / mid * 10_000)

    def test_hand_computed_buy_sell_decomposition_and_fee_notional(self):
        module = api()
        baseline, delayed = quote(99.0, 101.0), quote(101.0, 103.0)
        buy = module.compare_quotes(100.0, baseline, delayed, 1)
        sell = module.compare_quotes(100.0, baseline, delayed, -1)
        self.assertEqual(buy.price_saving, -200.0)
        self.assertEqual(sell.price_saving, 200.0)
        self.assertEqual(buy.spread_saving, 0.0)
        self.assertEqual(buy.mid_drift_saving, -200.0)
        self.assertEqual(sell.mid_drift_saving, 200.0)
        self.assertAlmostEqual(buy.fee_slope, -0.02)
        self.assertAlmostEqual(sell.fee_slope, -0.02)
        self.assertAlmostEqual(buy.saving(5.0, 0.5), -200.6)
        self.assertAlmostEqual(sell.saving(5.0, 0.5), 199.4)
        with self.assertRaises(FrozenInstanceError):
            buy.price_saving = 0.0

    def test_spread_saving_survives_with_zero_midpoint_drift(self):
        module = api()
        for side in [-1, 1]:
            result = module.compare_quotes(100.0, quote(98.0, 102.0), quote(99.0, 101.0), side)
            self.assertEqual(result.price_saving, 100.0)
            self.assertEqual(result.spread_saving, 100.0)
            self.assertEqual(result.mid_drift_saving, 0.0)
            self.assertAlmostEqual(result.saving(5.0, 0.5),
                                   decimal_oracle(100.0, quote(98.0, 102.0), quote(99.0, 101.0), side))

    def test_quantity_fixed_at_intent_and_small_future_depth_not_filtered(self):
        module = api()
        baseline, delayed = quote(99.0, 101.0, 1e-12), quote(101.0, 103.0, 1e-15)
        first = module.compare_quotes(100.0, baseline, delayed, 1)
        second = module.compare_quotes(200.0, baseline, delayed, 1)
        self.assertEqual(first.price_saving, 2 * second.price_saving)
        self.assertEqual(first.fee_slope, 2 * second.fee_slope)
        self.assertAlmostEqual(second.saving(10.0, 1.0), decimal_oracle(200.0, baseline, delayed, 1, 10.0, 1.0))

    def test_identical_quotes_only_pay_extra_delayed_slippage(self):
        module = api()
        for side in [-1, 1]:
            result = module.compare_quotes(100.0, quote(), quote(), side)
            self.assertEqual(result.price_saving, 0.0)
            self.assertEqual(result.fee_slope, 0.0)
            for fee in [0.0, 5.0, 10.0]:
                for stress in [0.0, 0.5, 1.0]:
                    self.assertEqual(result.saving(fee, stress), -stress)

    def test_independent_decimal_oracle_for_original_random_paths(self):
        module = api()
        rng = random.Random(20261021)
        for _ in range(150):
            intent = rng.uniform(10.0, 10_000.0)
            bid_b = intent * rng.uniform(0.99, 1.01)
            bid_d = intent * rng.uniform(0.99, 1.01)
            baseline = quote(bid_b, bid_b + intent * rng.uniform(0.000001, 0.005))
            delayed = quote(bid_d, bid_d + intent * rng.uniform(0.000001, 0.005))
            for side in [-1, 1]:
                result = module.compare_quotes(intent, baseline, delayed, side)
                self.assertAlmostEqual(result.price_saving,
                                       math.fsum([result.spread_saving, result.mid_drift_saving]), delta=1e-8)
                for fee, stress in [(0.0, 0.0), (5.0, 0.5), (10.0, 1.0)]:
                    self.assertAlmostEqual(result.saving(fee, stress),
                                           decimal_oracle(intent, baseline, delayed, side, fee, stress), delta=1e-8)

    def test_invalid_quotes_intent_side_and_cost_parameters_fail(self):
        module = api()
        invalid = [quote(ask=math.nan), quote(bid=math.inf), quote(bid=0.0),
                   quote(ask=-1.0), quote(bid=101.0), quote(bid=102.0),
                   quote(amount=0.0), quote(amount=math.nan)]
        for q in invalid:
            with self.subTest(q=q):
                for function in [module.midpoint, module.spread]:
                    with self.assertRaises(ValueError):
                        function(q)
                with self.assertRaises(ValueError):
                    module.crossing_price(q, 1)
                with self.assertRaises(ValueError):
                    module.compare_quotes(100.0, quote(), q, 1)
        for side in [True, False, 0, 2, -2, 1.0, -1.0]:
            with self.subTest(side=side), self.assertRaises(ValueError):
                module.compare_quotes(100.0, quote(), quote(), side)
            with self.subTest(side=side), self.assertRaises(ValueError):
                module.crossing_price(quote(), side)
        for intent in [0.0, -1.0, math.nan, math.inf, True]:
            with self.subTest(intent=intent), self.assertRaises(ValueError):
                module.compare_quotes(intent, quote(), quote(), 1)
        result = module.compare_quotes(100.0, quote(), quote(), 1)
        for value in [-1.0, math.nan, math.inf, True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                result.saving(value, 0.0)
            with self.subTest(value=value), self.assertRaises(ValueError):
                result.saving(0.0, value)

    def test_nonfinite_arithmetic_fails_instead_of_skipping_an_intent(self):
        module = api()
        with self.assertRaises(ArithmeticError):
            module.compare_quotes(1e-300, quote(1e300, 1.1e300), quote(1e300, 1.2e300), 1)
        result = module.CostDifference(1.0, 1.0, 0.0, 1e300)
        with self.assertRaises(ArithmeticError):
            result.saving(1e300, 0.0)

    def test_finite_but_inconsistent_arithmetic_fails_both_invariant_checks(self):
        module = api()
        first_ask = math.nextafter(1.0, math.inf)
        second_ask = math.nextafter(first_ask, math.inf)
        # Extreme synthetic scale ratios amplify a rounding discrepancy beyond
        # the protocol's fixed tolerance. Neither failure may become a dropped row.
        with self.assertRaisesRegex(ArithmeticError, 'decomposition'):
            module.compare_quotes(1e-8, quote(1.0, first_ask), quote(1.0, second_ask), 1)
        with self.assertRaisesRegex(ArithmeticError, 'direct primary-cost'):
            module.compare_quotes(3e-10, quote(99.0, 101.0), quote(101.0, 103.0), 1)


if __name__ == '__main__':
    unittest.main()
