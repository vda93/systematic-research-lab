"""Independent arithmetic and contract checks for the constructed study."""

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from srl.study import build_fixture, load_protocol, run_study


PROTOCOL = Path(__file__).resolve().parents[1] / "experiments" / "protocol.json"


def small_protocol():
    protocol = load_protocol(PROTOCOL)
    protocol["inference"]["repetitions"] = 39
    protocol["calibration"].update(trials=5, days=32, burn_in=64, repetitions=39)
    return protocol


class StudyTests(unittest.TestCase):
    def test_load_rejects_designs_outside_public_bootstrap_contract(self):
        mutations = [
            lambda p: p["calibration"].update(days=2, block_sizes=[1]),
            lambda p: p["calibration"].update(block_sizes=[17]),
            lambda p: p["inference"].update(block_sizes=[85]),
        ]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "protocol.json"
            for mutate in mutations:
                protocol = small_protocol()
                mutate(protocol)
                path.write_text(json.dumps(protocol), encoding="utf-8")
                with self.subTest(protocol=protocol), self.assertRaises(ValueError):
                    load_protocol(path)

    def test_tiny_calibration_intervals_preserve_coverage_decision_evidence(self):
        protocol = small_protocol()
        protocol["calibration"].update(innovation_scale=1e-12, common_shock_scale=0.0)
        result = run_study(protocol)
        self.assertEqual(result["calibration"]["design"]["innovation_scale"], 1e-12)
        self.assertTrue(any(not trial["covered"] for row in result["calibration"]["by_block"]
                            for trial in row["trials_detail"]))
        for row in result["calibration"]["by_block"]:
            self.assertGreater(row["mean_interval_width"], 0.0)
            for trial in row["trials_detail"]:
                self.assertGreater(trial["width"], 0.0)
                self.assertEqual(trial["covered"], trial["ci_low"] <= 0.0 <= trial["ci_high"])

    def test_fixed_fixture_arithmetic_and_complete_cohort_gate(self):
        protocol = small_protocol()
        fixture = build_fixture(protocol)
        self.assertEqual(len(fixture["control"]), 48)
        self.assertEqual(len(fixture["treatment"]), 48)
        for arm, expected in (("control", -6.0), ("treatment", 6.0)):
            records = fixture[arm]
            self.assertEqual(sum(record.gross - record.cost for record in records), expected)
            self.assertEqual(sum(record.cost for record in records), 6.0)
            self.assertEqual(len({record.opened for record in records}), 24)
            for first, second in zip(records[::2], records[1::2]):
                self.assertEqual(first.opened, second.opened)
                self.assertEqual((date.fromisoformat(first.closed) - date.fromisoformat(first.opened)).days, 2)
                self.assertEqual((date.fromisoformat(second.closed) - date.fromisoformat(second.opened)).days, 4)
        result = run_study(protocol)
        self.assertEqual(result["main"]["control"]["net_total"], -6.0)
        self.assertEqual(result["main"]["treatment"]["net_total"], 6.0)
        self.assertEqual(result["main"]["concentration"]["retained_total"], -22.0)
        self.assertEqual(result["main"]["stop_rule"]["decision"], "REJECT")
        self.assertEqual(result["main"]["event_pairing"]["status"], "PASS")
        self.assertEqual([row["block_size"] for row in result["main"]["bootstrap"]], [7, 14, 28])
        self.assertTrue(all(row["sample_days"] == 168 for row in result["main"]["bootstrap"]))

    def test_reporting_is_seeded_finite_and_keeps_every_calibration_trial(self):
        protocol = small_protocol()
        result = run_study(protocol)
        self.assertEqual(result, run_study(deepcopy(protocol)))
        self.assertEqual(result["evidence_role"], "SYNTHETIC")
        self.assertIs(result["constructed_teaching_example"], True)
        self.assertEqual(len(result["protocol_sha256"]), 64)
        self.assertEqual(len(result["input_sha256"]), 64)
        self.assertEqual(result["calibration"]["known_mean_delta"], 0.0)
        self.assertEqual(result["calibration"]["units"], "synthetic net units per calendar day")
        for row in result["calibration"]["by_block"]:
            self.assertEqual(row["trials"], 5)
            self.assertEqual(len(row["trials_detail"]), 5)
            self.assertEqual(row["covered"], sum(trial["covered"] for trial in row["trials_detail"]))
            self.assertAlmostEqual(row["coverage"], row["covered"] / 5)
            self.assertGreater(row["mean_interval_width"], 0.0)
            self.assertEqual([trial["trial"] for trial in row["trials_detail"]], list(range(5)))
            for trial in row["trials_detail"]:
                self.assertEqual(trial["covered"], trial["ci_low"] <= 0.0 <= trial["ci_high"])
        json.dumps(result, allow_nan=False)

    def test_calendar_and_cohort_labels_follow_protocol(self):
        protocol = small_protocol()
        original = run_study(protocol)
        protocol["cohort_design"]["start_date"] = "2041-03-05"
        changed = run_study(protocol)
        self.assertNotEqual(original["input_sha256"], changed["input_sha256"])
        self.assertNotEqual(original["protocol_sha256"], changed["protocol_sha256"])
        self.assertEqual(changed["main"]["cohorts"][0]["opened"], "2041-03-05")
        self.assertEqual(changed["main"]["cohorts"][-1]["opened"], (date(2041, 3, 5) + timedelta(days=161)).isoformat())
        self.assertEqual(changed["main"]["concentration"]["removed_cohorts"], ["2041-04-02", "2041-07-02"])
        self.assertEqual(changed["design"]["start_date"], "2041-03-05")

    def test_rejects_invalid_manifest_values_before_study(self):
        mutations = [
            lambda p: p.update(evidence_role="EMPIRICAL"),
            lambda p: p.update(constructed_teaching_example=False),
            lambda p: p.update(extra="unexpected"),
            lambda p: p["cohort_design"].update(weeks=True),
            lambda p: p["cohort_design"].update(record_cost=float("nan")),
            lambda p: p["cohort_design"].update(start_date="2040-1-2"),
            lambda p: p["cohort_design"].update(close_offsets_days=[4, 2]),
            lambda p: p["calibration"].update(rho=1.0),
            lambda p: p["calibration"].update(rho=float("inf")),
            lambda p: p["calibration"].update(trials=0),
            lambda p: p["calibration"].update(block_sizes=[]),
            lambda p: p["calibration"].update(block_sizes=[1, True]),
            lambda p: p["inference"].update(block_sizes=[]),
            lambda p: p["inference"].update(repetitions=1.5),
            lambda p: p["stop_rule"].update(remove_cohorts=25),
            lambda p: p["stop_rule"].update(minimum_retained_net=float("inf")),
        ]
        for mutate in mutations:
            protocol = small_protocol()
            mutate(protocol)
            with self.subTest(protocol=protocol), self.assertRaises(ValueError):
                run_study(protocol)

    def test_calibration_reports_known_zero_dgp_without_forcing_coverage(self):
        protocol = small_protocol()
        protocol["calibration"].update(trials=7, rho=0.9, repetitions=19)
        result = run_study(protocol)
        calibration = result["calibration"]
        self.assertEqual(calibration["design"]["rho"], 0.9)
        self.assertEqual([row["block_size"] for row in calibration["by_block"]], [1, 8, 16])
        self.assertTrue(any(row["coverage"] < 1.0 for row in calibration["by_block"]))
        for row in calibration["by_block"]:
            self.assertEqual(len(row["trials_detail"]), 7)
            expected = (row["coverage"] * (1 - row["coverage"]) / 7) ** 0.5
            self.assertAlmostEqual(row["monte_carlo_se"], expected, places=9)


if __name__ == "__main__":
    unittest.main()
