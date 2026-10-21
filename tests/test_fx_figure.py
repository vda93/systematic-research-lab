"""Presentation checks against the frozen empirical result, not new hypotheses."""
from copy import deepcopy
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import numpy as np

from scripts.render_fx import fx_artifacts

ROOT = Path(__file__).resolve().parents[1]


class FxFigureTests(unittest.TestCase):
    def setUp(self):
        self.result = json.loads((ROOT / 'data/ecb-fx-results.json').read_text())

    def test_exact_replay_and_svg_semantic_disclosures(self):
        first = fx_artifacts(self.result)
        self.assertEqual(first, fx_artifacts(deepcopy(self.result)))
        svg = first['figures/fx-reference.svg']
        ET.fromstring(svg)
        for text in (b'NOT_PASS', b'EURUSD', b'USDJPY', b'744', b'0.5', b'not executable'):
            self.assertIn(text, svg)
        self.assertNotIn(b'<dc:date>', svg)

    def test_complete_tables_keep_all_roles_assets_blocks_and_annual_rows(self):
        table = fx_artifacts(self.result)['results/fx-tables.md'].decode()
        for role in ('development', 'validation', 'final'):
            self.assertIn(role, table)
            for block in self.result['roles'][role]['bootstrap']:
                for asset in block['assets']:
                    self.assertIn(f"| {role} | {block['block_length']} | {asset['asset']} |", table)
            for annual in self.result['roles'][role]['annual']:
                self.assertIn(f"| {role} | {annual['year']} |", table)
        self.assertIn('0.9598', table)
        self.assertIn('marginal', table)
        self.assertIn('outcome-dependent', table)
        self.assertIn('NOT_EVALUATED', table)

    def test_mutated_verdict_invalid_probability_and_units_reject(self):
        mutations = [lambda r: r.update(family_verdict='PASS'),
                     lambda r: r['roles']['final']['assets']['EURUSD'].update(primary_p_value=2),
                     lambda r: r.update(executable_profitability='PASS'),
                     lambda r: r['roles']['final']['assets']['USDJPY'].update(ci_low_bps=float('nan'))]
        for mutation in mutations:
            changed = deepcopy(self.result)
            mutation(changed)
            with self.assertRaises(ValueError):
                fx_artifacts(changed)

    def test_independent_final_arithmetic_and_direct_index_bootstrap(self):
        """Separate gathered-index implementation checks frozen primary output."""
        payload = (ROOT / 'data/ecb-fx-reference.csv').read_bytes()
        self.assertEqual(sha256(payload).hexdigest(), self.result['source_csv_sha256'])
        source = list(csv.DictReader(payload.decode().splitlines()))
        prices = [(float(r['USD']), float(r['JPY']) / float(r['USD'])) for r in source]
        differences = []
        for t in range(20, len(source) - 2):
            if not all('2023-01-01' <= source[i]['Date'] < '2026-01-01' for i in (t-20, t, t+1, t+2)):
                continue
            paired = []
            for j in (0, 1):
                momentum = math.log(prices[t][j] / prices[t-20][j])
                sign = (momentum > 0) - (momentum < 0)
                target = math.log(prices[t+2][j] / prices[t+1][j])
                paired.append((sign - 1) * target)
            differences.append(paired)
        values = np.array(differences)
        n = len(values)
        observed = values.mean(axis=0)
        centered = values - observed
        means, null_means = [], []
        rng = np.random.default_rng(20261021)
        for _ in range(9999):
            starts = rng.integers(0, n, size=math.ceil(n / 20))
            indices = ((starts[:, None] + np.arange(20)[None, :]) % n).reshape(-1)[:n]
            means.append(values[indices].mean(axis=0))
            null_means.append(centered[indices].mean(axis=0))
        bounds = np.quantile(means, [.025, .975], axis=0)
        p_values = (1 + (np.array(null_means) >= observed).sum(axis=0)) / 10000
        order = np.argsort(p_values)
        adjusted = np.empty(2)
        adjusted[order[0]] = min(1., 2 * p_values[order[0]])
        adjusted[order[1]] = max(adjusted[order[0]], p_values[order[1]])
        final = self.result['roles']['final']
        self.assertEqual(n, final['sample_size'])
        for j, asset in enumerate(('EURUSD', 'USDJPY')):
            recorded = final['assets'][asset]
            self.assertAlmostEqual(observed[j] * 10000, recorded['mean_difference_bps'], places=9)
            self.assertAlmostEqual(bounds[0, j] * 10000, recorded['ci_low_bps'], places=9)
            self.assertAlmostEqual(bounds[1, j] * 10000, recorded['ci_high_bps'], places=9)
            self.assertAlmostEqual(p_values[j], recorded['primary_p_value'], places=10)
            self.assertAlmostEqual(adjusted[j], recorded['holm_adjusted_p_value'], places=10)


if __name__ == '__main__':
    unittest.main()
