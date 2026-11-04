"""Independent arithmetic identities on retained published aggregates."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from srl.diagnostics import derive_diagnostics

ROOT = Path(__file__).resolve().parents[1]


class AggregateDiagnosticTests(unittest.TestCase):
    def source(self):
        return json.loads((ROOT / 'data/historical-results.json').read_text())

    def test_oos_and_nowick_uncertainty_reconcile(self):
        result = derive_diagnostics(self.source())
        self.assertAlmostEqual(result['orb']['pooled_oos_r'], 25.83656672167845, places=9)
        self.assertFalse(result['orb']['standalone_b_total_positive'])
        self.assertTrue(result['nowick']['primary_ci_includes_zero'])
        self.assertAlmostEqual(result['nowick']['primary_interval_width_pp'], 1.170806)

    def test_published_input_mutation_changes_output(self):
        original = derive_diagnostics(self.source())
        changed = deepcopy(self.source())
        next(r for r in changed['records'] if r['id'] == 'O2_A')['metrics']['total_r'] += 1.0
        result = derive_diagnostics(changed)
        self.assertNotEqual(original['orb']['pooled_oos_r'], result['orb']['pooled_oos_r'])
        self.assertEqual(original['nowick'], result['nowick'])

    def test_invalid_oos_period_roles_and_accounting_fail(self):
        for field, value in (
            ('period_start', '2025-06-01'),
            ('sample_type', 'development'),
            ('return_basis', 'money'),
        ):
            changed = deepcopy(self.source())
            next(r for r in changed['records'] if r['id'] == 'O2_B')[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                derive_diagnostics(changed)


if __name__ == '__main__':
    unittest.main()
