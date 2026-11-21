"""Checks for the released Trading Steady ORB aggregate-only research figures."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.render_tradingsteady_orb import build, render_factorial, render_oos


ROOT = Path(__file__).resolve().parents[1]


class PublicTradingSteadyStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((ROOT / "data/trading-steady-orb-public.json").read_text(encoding="utf-8"))

    def test_full_design_retains_all_48_distinct_variants(self) -> None:
        rows = self.data["factorial_cells"]
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({row["id"] for row in rows}), 48)
        self.assertEqual({row["market"] for row in rows}, {"US500", "USTEC"})
        self.assertEqual({row["opening_range_minutes"] for row in rows}, {5, 15, 30})
        self.assertEqual(sum(x["closed_trades"] for x in rows), 10895)

    def test_later_results_retain_all_eight_cells_and_censors(self) -> None:
        rows = self.data["later_us500"]["results"]
        self.assertEqual(len(rows), 8)
        self.assertEqual({r["cohort"] for r in rows}, {"A", "B"})
        self.assertEqual(sum(r["entries"] for r in rows), 366)
        self.assertEqual(sum(r["natural_closes"] for r in rows), 364)
        self.assertEqual(sum(r["right_censored_entries"] for r in rows), 2)
        primary = [r for r in rows if r["id"] == "US500_OR15_LS_A1_E0"]
        self.assertAlmostEqual(sum(r["closed_trade_published_commission_scenario_R"] for r in primary), 5.319, places=2)

    def test_renderers_use_aggregate_cells_without_private_data(self) -> None:
        artifacts = build(self.data)
        self.assertEqual(set(artifacts), {"trading-steady-orb-factorial.svg", "trading-steady-orb-oos.svg"})
        for svg in artifacts.values():
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)
            self.assertNotIn("PRIVATE KEY", svg)
        self.assertIn("0.814", render_factorial(self.data))
        self.assertIn("+3.539R", render_oos(self.data))
        self.assertIn("-13.708R", render_oos(self.data))

    def test_public_study_does_not_claim_full_oos_inference(self) -> None:
        text = (ROOT / "studies/trading-steady-orb.md").read_text(encoding="utf-8")
        for phrase in (
            "full preregistered primary statistic remains unestimable",
            "historical all-in net performance is unknown",
            "USTEC source-blocked",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
