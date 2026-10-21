"""Synthetic software checks; these fixtures are not market evidence."""
from dataclasses import replace
from datetime import date, timedelta
import io
import math
from pathlib import Path
import unittest
import zipfile
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

from srl.fx_study import (Rate, bootstrap, canonical_csv, classify, holm,
                          parse_csv, result_bytes, rows_for_role, run_study, selected_archive)
from scripts import fx_study as cli


def fixture(start=date(2016, 6, 1), n=180):
    result = []
    day = start
    while len(result) < n:
        if day.weekday() < 5:
            k = len(result)
            result.append(Rate(day, str(1 + k / 1000), str(100 + k / 10)))
        day += timedelta(days=1)
    return result


class FxStudyTests(unittest.TestCase):
    def test_exact_schema_and_canonical_serialization(self):
        records = fixture(n=30)
        payload = canonical_csv(list(reversed(records)))
        self.assertEqual(parse_csv(payload), records)
        self.assertTrue(payload.startswith(b'Date,USD,JPY\n'))
        self.assertNotIn(b'\r', payload)
        for invalid in (b'Date,USD,JPY,other\n', b'USD,Date,JPY\n'):
            with self.assertRaises(ValueError):
                parse_csv(invalid)

    def test_duplicate_nonpositive_invalid_and_gap_reject(self):
        records = fixture(n=30)
        mutations = [records + [records[0]],
                     [replace(records[0], usd='0')] + records[1:],
                     [replace(records[0], jpy='NaN')] + records[1:],
                     [replace(records[0], usd='Infinity')] + records[1:],
                     records[:1] + records[10:]]
        for bad in mutations:
            with self.subTest(bad=bad[:1]), self.assertRaises(ValueError):
                canonical_csv(bad)

    def test_delayed_target_and_future_mutation_do_not_change_signal(self):
        records = fixture()
        rows = rows_for_role(records, 'development')
        row = rows[0]
        t = next(i for i, item in enumerate(records) if item.day.isoformat() == row['signal_date'])
        expected = math.log(float(records[t + 2].usd) / float(records[t + 1].usd))
        self.assertAlmostEqual(row['target'][0], expected)
        changed = records[:]
        changed[t + 2] = replace(changed[t + 2], usd='9.0')
        mutant = rows_for_role(changed, 'development')[0]
        self.assertEqual(row['sign'], mutant['sign'])
        self.assertNotEqual(row['target'], mutant['target'])

    def test_role_purge_and_delay_sensitivity(self):
        records = fixture(date(2019, 11, 1), 160)
        for delay in (1, 2):
            rows = rows_for_role(records, 'validation', delay=delay)
            self.assertTrue(rows)
            for row in rows:
                self.assertGreaterEqual(row['feature_start'], '2020-01-01')
                self.assertGreaterEqual(row['target_start'], '2020-01-01')
                self.assertLess(row['target_end'], '2023-01-01')
        self.assertEqual(len(rows_for_role(records, 'validation', delay=1)),
                         len(rows_for_role(records, 'validation', delay=2)) + 1)

    def test_archive_selects_only_frozen_columns_dates_and_rejects_notices(self):
        def archive(notice=None):
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w') as z:
                z.writestr('eurofxref-hist.csv',
                           'Date,USD,JPY,GBP,\n2016-06-02,1.2,120,0.8,\n'
                           '2016-06-01,1.1,110,0.7,\n2026-01-01,2,200,1,\n')
                if notice is not None:
                    z.writestr('LICENSE.txt', notice)
            return out.getvalue()
        selected, metadata = selected_archive(archive())
        self.assertEqual(len(parse_csv(selected)), 2)
        self.assertEqual(metadata['member'], 'eurofxref-hist.csv')
        with self.assertRaises(ValueError):
            selected_archive(archive('Redistribution prohibited'))

    def test_holm_exact_and_invalid_inputs(self):
        self.assertEqual(holm([0.04, 0.01]), [0.04, 0.02])
        self.assertEqual(holm([0.03, 0.04]), [0.06, 0.06])
        for bad in ([float('nan'), .2], [-.1, .2], [1.1, .2]):
            with self.assertRaises(ValueError):
                holm(bad)

    def test_bootstrap_preserves_asset_pairing_and_seed(self):
        x = np.linspace(-.002, .003, 80)
        values = np.column_stack([x, x * 3])
        first = bootstrap(values, block_length=10, repetitions=99)
        self.assertEqual(first, bootstrap(values, block_length=10, repetitions=99))
        self.assertAlmostEqual(first['assets'][1]['ci_low'], first['assets'][0]['ci_low'] * 3)
        self.assertAlmostEqual(first['assets'][1]['ci_high'], first['assets'][0]['ci_high'] * 3)
        self.assertEqual(first['assets'][0]['p_value'], first['assets'][1]['p_value'])

    def test_bootstrap_matches_independent_direct_index_reference(self):
        values = np.column_stack([np.arange(12) / 1000, -np.arange(12) / 2000])
        actual = bootstrap(values, block_length=5, repetitions=29)
        rng = np.random.default_rng(20261021)
        means = []
        for _ in range(29):
            starts = rng.integers(0, 12, size=3)
            indices = [(int(start) + j) % 12 for start in starts for j in range(5)][:12]
            means.append(values[indices].mean(axis=0))
        expected = np.quantile(np.array(means), [.025, .975], axis=0)
        for i in range(2):
            self.assertAlmostEqual(actual['assets'][i]['ci_low'], expected[0, i])
            self.assertAlmostEqual(actual['assets'][i]['ci_high'], expected[1, i])

    def test_pass_needs_all_three_screens(self):
        self.assertEqual(classify(.00006, .00001, .04), 'PASS')
        for mean, low, p in ((.00004, .00001, .04), (.00006, 0, .04), (.00006, .00001, .06)):
            self.assertNotEqual(classify(mean, low, p), 'PASS')
        self.assertEqual(classify(-.0001, -.0002, .9), 'NEGATIVE_COMPARISON')

    def test_zero_difference_null_and_bootstrap_validation(self):
        output = bootstrap(np.zeros((80, 2)), repetitions=19)
        self.assertTrue(all(a['p_value'] == 1 and a['ci_low'] == 0 for a in output['assets']))
        for values, block, repeats in (([[1, 2]], 1, 19), ([[float('nan'), 0]] * 5, 1, 19),
                                       ([[1, 2]] * 5, 3, 19), ([[1, 2]] * 5, 1, 0)):
            with self.assertRaises(ValueError):
                bootstrap(values, block_length=block, repetitions=repeats)

    def test_complete_synthetic_replay_reports_every_role_and_no_trading_claim(self):
        records = fixture(n=2600)
        records = [replace(r, usd=f'{math.exp(.03 * math.sin(i / 33)):.17g}',
                           jpy=f'{120 * math.exp(.02 * math.cos(i / 27)):.17g}')
                   for i, r in enumerate(records) if r.day < date(2026, 1, 1)]
        payload = canonical_csv(records)
        first = run_study(payload, repetitions=29)
        self.assertEqual(result_bytes(first), result_bytes(run_study(payload, repetitions=29)))
        self.assertEqual(first['executable_profitability'], 'NOT_EVALUATED')
        self.assertFalse(first['prospective_fresh_oos'])
        self.assertEqual(set(first['roles']), {'development', 'validation', 'final'})
        for role in first['roles'].values():
            self.assertEqual(role['status'], 'QUALIFIED')
            self.assertEqual([b['block_length'] for b in role['bootstrap']], [10, 20, 60])
            self.assertEqual(set(role['assets']), {'EURUSD', 'USDJPY'})
        expected = 'PASS' if all(a['verdict'] == 'PASS' for a in first['roles']['final']['assets'].values()) else 'NOT_PASS'
        self.assertEqual(first['family_verdict'], expected)
        self.assertIn('concentration', first['roles']['final'])
        self.assertTrue(first['extra_delay']['final']['assets'])

    def test_support_fails_closed_without_changing_window(self):
        output = run_study(canonical_csv(fixture()), repetitions=19)
        self.assertEqual(output['family_verdict'], 'FAIL_SUPPORT')
        self.assertEqual(output['roles']['final']['status'], 'FAIL_SUPPORT')

    def test_missing_development_blocks_family_despite_qualified_final(self):
        records = [r for r in fixture(date(2023, 1, 2), 700)]
        output = run_study(canonical_csv(records), repetitions=19)
        self.assertEqual(output['roles']['final']['status'], 'QUALIFIED')
        self.assertEqual(output['family_verdict'], 'FAIL_SUPPORT')

    def test_cli_default_never_downloads_and_freeze_rejects_before_network(self):
        with TemporaryDirectory() as directory, patch.object(cli, 'urlopen') as network:
            absent = Path(directory) / 'missing.csv'
            with self.assertRaises(ValueError):
                cli.main(['--snapshot', str(absent)])
            with self.assertRaises(ValueError):
                cli.acquire(Path(directory) / 'raw.zip', absent, '', False)
            network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
