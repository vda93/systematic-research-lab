"""Hand-calculated cashflow and cohort examples."""

import unittest

from srl.accounting import Record, concentration, summarize


class AccountingTests(unittest.TestCase):
    def test_close_order_controls_drawdown_and_costs_reduce_every_record(self):
        rows = [
            Record("z", "2024-01-01", "2024-01-03", 8, 1),
            Record("b", "2024-01-01", "2024-01-02", -2, 1),
            Record("a", "2024-01-01", "2024-01-02", 5, 1),
        ]
        self.assertEqual(summarize(iter(rows)), {
            "n": 3, "gross_total": 11, "cost_total": 3,
            "net_total": 8, "mean_net": 8 / 3,
            "profit_factor": 11 / 3, "max_drawdown": 3,
            "ordering": "closed_then_key",
        })
        self.assertEqual(summarize(reversed(rows)), summarize(rows))

    def test_initial_loss_counts_as_drawdown(self):
        result = summarize([Record("a", "2024-01-01", "2024-01-01", -4, 1)])
        self.assertEqual(result["max_drawdown"], 5)
        self.assertEqual(result["profit_factor"], 0)

    def test_empty_and_no_losses_have_no_profit_factor(self):
        self.assertEqual(summarize([])["net_total"], 0)
        self.assertIsNone(summarize([])["profit_factor"])
        self.assertIsNone(summarize([Record("a", "2024-01-01", "2024-01-01", 1, 0)])["profit_factor"])

    def test_sums_retain_small_residuals(self):
        rows = [Record(str(i), "2024-01-01", "2024-01-01", v, 0)
                for i, v in enumerate([1e16, 1, -1e16])]
        self.assertEqual(summarize(rows)["net_total"], 1)

    def test_whole_opened_cohort_removed_and_equal_totals_use_date(self):
        rows = [
            Record("a", "2024-01-01", "2024-01-05", 8, 1),
            Record("b", "2024-01-01", "2024-01-02", -2, 0),
            Record("c", "2024-01-02", "2024-01-02", 5, 0),
            Record("d", "2024-01-03", "2024-01-03", -3, 0),
        ]
        self.assertEqual(concentration(reversed(rows), 1), {
            "removed_cohorts": ["2024-01-01"], "removed_total": 5,
            "retained_total": 2, "original_total": 7, "cohort_count": 3,
        })
        self.assertEqual(concentration(rows, 0)["retained_total"], 7)
        self.assertEqual(concentration(rows, 3)["retained_total"], 0)
        for bad in [-1, 4, True, 1.0]:
            with self.subTest(remove=bad), self.assertRaises(ValueError):
                concentration(rows, bad)

    def test_invalid_records_fail_before_aggregation(self):
        bad_rows = [
            Record("", "2024-01-01", "2024-01-02", 1, 0),
            Record("a", "20240101", "2024-01-02", 1, 0),
            Record("a", "2024-02-30", "2024-03-01", 1, 0),
            Record("a", "2024-01-03", "2024-01-02", 1, 0),
            Record("a", "2024-01-01", "2024-01-02", float("nan"), 0),
            Record("a", "2024-01-01", "2024-01-02", 1, float("inf")),
            Record("a", "2024-01-01", "2024-01-02", 1, -1),
            Record("a", "2024-01-01", "2024-01-02", -1e308, 1e308),
        ]
        for row in bad_rows:
            with self.subTest(row=row), self.assertRaises(ValueError):
                summarize([row])
        duplicate = Record("a", "2024-01-01", "2024-01-02", 1, 0)
        with self.assertRaises(ValueError):
            summarize([duplicate, duplicate])

    def test_overflow_in_aggregates_is_rejected(self):
        rows = [Record(k, "2024-01-01", "2024-01-01", 1e308, 0) for k in ["a", "b"]]
        for action in [lambda: summarize(rows), lambda: concentration(rows, 1)]:
            with self.assertRaises(ValueError):
                action()

    def test_profit_factor_and_drawdown_cannot_emit_infinity(self):
        for values in [[1e308, -1e-308], [1e308, -1e308, -1e308]]:
            rows = [Record(str(i), "2024-01-01", "2024-01-01", v, 0)
                    for i, v in enumerate(values)]
            with self.subTest(values=values), self.assertRaises(ValueError):
                summarize(rows)


if __name__ == "__main__":
    unittest.main()
