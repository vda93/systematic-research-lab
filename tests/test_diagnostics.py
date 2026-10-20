"""Independent arithmetic identities on real published aggregates."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from srl.diagnostics import derive_diagnostics

ROOT=Path(__file__).resolve().parents[1]


class AggregateDiagnosticTests(unittest.TestCase):
    def source(self):
        return json.loads((ROOT/'data/historical-results.json').read_text())

    def test_concentration_risk_and_oos_reconcile_by_independent_arithmetic(self):
        result=derive_diagnostics(self.source())
        self.assertAlmostEqual(result['de30']['removed_top10_date_contribution_r'],46.8900,places=6)
        self.assertAlmostEqual(result['de30']['risk_fill_pct_of_request'],99.21,places=6)
        self.assertAlmostEqual(result['orb']['pooled_oos_r'],25.83656672167845,places=9)
        self.assertEqual(result['orb']['standalone_b_total_positive'],False)
        self.assertEqual(result['nowick']['primary_ci_includes_zero'],True)

    def test_source_changes_flow_to_comparison_without_relabeling_uncertainty(self):
        data=self.source()
        original=derive_diagnostics(data)
        changed=deepcopy(data)
        next(r for r in changed['records'] if r['id']=='M3')['metrics']['no_trail_total_r']=50.0
        result=derive_diagnostics(changed)
        self.assertAlmostEqual(result['momentum']['recent_no_trail_minus_canonical_r'],1.2808,places=6)
        self.assertNotEqual(original['momentum'],result['momentum'])

    def test_invalid_arithmetic_and_unaligned_oos_fail(self):
        data=self.source()
        next(r for r in data['records'] if r['id']=='D7')['metrics']['requested_risk_pct']=0
        with self.assertRaises(ValueError):
            derive_diagnostics(data)
        data=self.source()
        next(r for r in data['records'] if r['id']=='O2_B')['period_start']='2025-06-01'
        with self.assertRaises(ValueError):
            derive_diagnostics(data)


if __name__=='__main__':
    unittest.main()
