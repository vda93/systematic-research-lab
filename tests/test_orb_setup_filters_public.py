"""Checks for the released ORB setup and filter study aggregates and figures."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.render_orb_setup_filters import (
    SELECTED_LABELS, build, comparison_values, factorial_index, later_index,
    ema_pair_summary, primary_fixed_trade_costs,
    render_comparison, render_factorial, render_oos,
)


ROOT = Path(__file__).resolve().parents[1]


class PublicOrbSetupFilterStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((ROOT / "data/orb-setup-filters-public.json").read_text(encoding="utf-8"))

    def test_full_design_retains_every_factorial_combination(self) -> None:
        rows = factorial_index(self.data)
        self.assertEqual(len(rows), 48)
        self.assertEqual(sum(row["closed_trades"] for row in rows.values()), 10895)
        self.assertEqual(sum(row["ema200_enabled"] for row in rows.values()), 24)

    def test_factorial_rejects_missing_duplicate_and_mislabelled_cells(self) -> None:
        for change in ("missing", "duplicate", "metadata"):
            with self.subTest(change=change):
                data = deepcopy(self.data)
                rows = data["factorial_cells"]
                if change == "missing":
                    rows.pop()
                elif change == "duplicate":
                    rows[-1] = deepcopy(rows[0])
                else:
                    rows[0]["ema200_enabled"] = not rows[0]["ema200_enabled"]
                with self.assertRaises(ValueError):
                    render_factorial(data)

    def test_later_results_preserve_closes_censors_and_unknown_drawdowns(self) -> None:
        rows = list(later_index(self.data).values())
        self.assertEqual(sum(row["entries"] for row in rows), 366)
        self.assertEqual(sum(row["natural_closes"] for row in rows), 364)
        self.assertEqual(sum(row["right_censored_entries"] for row in rows), 2)
        self.assertEqual(
            {(row["id"], row["cohort"]) for row in rows if row["right_censored_entries"]},
            {("US500_OR05_L_A0_E0", "A"), ("US500_OR15_L_A0_E0", "A")},
        )
        for row in rows:
            if row["right_censored_entries"]:
                self.assertIsNone(row["quote_MTM_drawdown_R"])
            else:
                self.assertIsNotNone(row["quote_MTM_drawdown_R"])
            self.assertLessEqual(row["closed_trade_published_commission_scenario_R"], row["closed_trade_gross_R"])

    def test_no_ema_oos_performance_is_invented(self) -> None:
        discovery = factorial_index(self.data)
        for id_, _ in later_index(self.data):
            self.assertFalse(discovery[id_]["ema200_enabled"])
        self.assertEqual(self.data["later_ustec"]["status"], "NOT_RUN_SOURCE_BLOCKED")

    def test_later_identity_and_denominators_fail_closed(self) -> None:
        for change in ("duplicate", "cohort", "entries", "no_closes"):
            with self.subTest(change=change):
                data = deepcopy(self.data)
                rows = data["later_us500"]["results"]
                if change == "duplicate":
                    rows[-1] = deepcopy(rows[0])
                elif change == "cohort":
                    rows[0]["cohort"] = "C"
                elif change == "entries":
                    rows[0]["entries"] += 1
                else:
                    rows[0]["natural_closes"] = 0
                with self.assertRaises(ValueError):
                    render_oos(data)

    def test_comparison_uses_same_configurations_and_gross_close_denominators(self) -> None:
        comparisons = comparison_values(self.data)
        self.assertEqual(set(comparisons), set(SELECTED_LABELS))
        primary = comparisons["US500_OR15_LS_A1_E0"]
        self.assertEqual([count for _, count in primary], [377, 74, 40])
        self.assertAlmostEqual(primary[0][0], 70.5471 / 377)
        self.assertAlmostEqual(primary[1][0], 4.693 / 74)
        self.assertAlmostEqual(primary[2][0], 2.223 / 40)
        censored = comparisons["US500_OR15_L_A0_E0"][1]
        self.assertEqual(censored[1], 65)
        self.assertAlmostEqual(censored[0], -7.126 / 65)

    def test_all_checked_in_figures_reproduce_byte_for_byte(self) -> None:
        artifacts = build(self.data)
        self.assertEqual(set(artifacts), {
            "orb-setup-filters-factorial.svg", "orb-setup-filters-oos.svg",
            "orb-setup-filters-comparison.svg",
        })
        for name, svg in artifacts.items():
            with self.subTest(name=name):
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertEqual((ROOT / "figures" / name).read_bytes(), svg.encode("utf-8"))

    def test_comparison_and_oos_figures_follow_changed_source_values(self) -> None:
        data = deepcopy(self.data)
        for row in data["later_us500"]["results"]:
            if row["id"] == "US500_OR15_LS_A1_E0" and row["cohort"] == "B":
                row["closed_trade_gross_R"] = -8.0
                row["closed_trade_published_commission_scenario_R"] = -9.0
        self.assertIn("-0.200R | n=40", render_comparison(data))
        self.assertIn("-9.000R", render_oos(data))
        self.assertNotEqual(render_comparison(data), render_comparison(self.data))
        self.assertNotEqual(render_oos(data), render_oos(self.data))

    def test_ema_summary_covers_all_pairs_and_retains_mixed_results(self) -> None:
        summary = ema_pair_summary(self.data)
        self.assertEqual(self.data["study_design"]["ema_matched_summary"]["markets"], summary)
        expected = {
            "US500": {
                "gross_profit_factor": (5, 6, 1),
                "commission_scenario_R_per_common_day": (2, 10, 0),
                "realized_drawdown_R": (0, 12, 0),
                "closed_trades": (0, 12, 0),
                "gross_price_R": (0, 12, 0),
            },
            "USTEC": {
                "gross_profit_factor": (11, 1, 0),
                "commission_scenario_R_per_common_day": (6, 6, 0),
                "realized_drawdown_R": (3, 8, 1),
                "closed_trades": (0, 12, 0),
                "gross_price_R": (5, 7, 0),
            },
        }
        for market, metrics in expected.items():
            self.assertEqual(summary[market]["matched_pairs"], 12)
            for metric, counts in metrics.items():
                actual = summary[market]["metrics"][metric]
                self.assertEqual(tuple(actual.values()), counts, (market, metric))
                self.assertEqual(sum(actual.values()), 12)

    def test_cost_sensitivity_uses_two_sides_per_natural_close(self) -> None:
        result = primary_fixed_trade_costs(self.data)
        released = self.data["later_us500"]["primary_fixed_trade_cost_sensitivity"]
        for key, value in result.items():
            self.assertEqual(released[key], value)
        self.assertEqual(result["natural_closes"], 114)
        self.assertEqual(result["combined_published_commission_scenario_R"], 5.319)
        self.assertEqual([row["extra_round_trip_cost_R"] for row in result["scenarios"]], [0, 5.7, 11.4])
        self.assertEqual([row["closed_trade_scenario_R_after_extra_cost"] for row in result["scenarios"]],
                         [5.319, -0.381, -6.081])

    def test_figures_follow_period_coverage_and_source_metadata(self) -> None:
        data = deepcopy(self.data)
        data["study_design"]["factorial_periods"]["US500"] = "2019-01-01 through 2024-02-29"
        a = data["later_us500"]["score_periods"]["A"]
        a.update(start="2024-02-01", end_exclusive="2025-01-01", eligible_NYSE_days=230,
                 incomplete_confirmation_sessions=["2024-03-01", "2024-04-01"])
        data["later_us500"]["score_periods"]["B"]["eligible_NYSE_days"] = 123
        data["source_evidence"]["factorial"]["source_id"] = "TEST_DISCOVERY"
        data["source_evidence"]["later_us500"]["source_id"] = "TEST_LATER"
        comparison, oos = render_comparison(data), render_oos(data)
        self.assertIn("Jan 2019 to Feb 2024", comparison)
        for svg in (comparison, oos):
            self.assertIn("Feb to Dec 2024", svg)
            self.assertIn("2 incomplete confirmation", svg)
            self.assertIn("TEST_LATER", svg)
        self.assertIn("230 eligible sessions", oos)
        self.assertIn("123 eligible sessions", oos)
        self.assertIn("TEST_DISCOVERY", comparison)
        self.assertIn("TEST_DISCOVERY", render_factorial(data))


if __name__ == "__main__":
    unittest.main()
