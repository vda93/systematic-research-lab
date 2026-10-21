"""Adversarial evidence governance and portable deterministic closeout checks."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

from srl.evidence import load_manifest, pack, verify_manifest, verify_pack


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'input.txt').write_bytes(b'fixture only\n')
        self.manifest = {'version': 1, 'evidence': [{
            'id': 'fixture', 'path': 'input.txt',
            'sha256': hashlib.sha256(b'fixture only\n').hexdigest(), 'bytes': 13,
            'source': 'unit-test fixture', 'license': 'MIT', 'redistribution': 'permitted',
            'disclosure': 'Public synthetic fixture', 'disclosure_approved': True,
            'owner': 'test author', 'kind': 'synthetic', 'study_id': 'study-a',
            'sample_space': 'fixture-series', 'period_start': '2020-01-01',
            'period_end_exclusive': '2021-01-01', 'sample_role': 'illustration',
            'consumed': True}], 'claims': [{
            'id': 'claim', 'kind': 'engineering', 'text': 'Fixture bytes verify.',
            'evidence_ids': ['fixture'], 'disclosure_approved': True}]}

    def reject(self, change):
        candidate = copy.deepcopy(self.manifest)
        change(candidate)
        with self.assertRaises(ValueError):
            verify_manifest(self.root, candidate)

    def test_real_bytes_are_verified_and_mutation_rejected(self):
        result = verify_manifest(self.root, self.manifest)
        self.assertEqual(result.evidence[0].id, 'fixture')
        (self.root / 'input.txt').write_bytes(b'changed bytes')
        with self.assertRaises(ValueError):
            verify_manifest(self.root, self.manifest)

    def test_required_metadata_identity_schema_and_roles(self):
        for field in ['source', 'license', 'redistribution', 'disclosure', 'owner', 'study_id', 'sample_space']:
            self.reject(lambda m, f=field: m['evidence'][0].pop(f))
            self.reject(lambda m, f=field: m['evidence'][0].update({f: ' '}))
        for patch in [{'id': '../bad'}, {'bytes': True}, {'bytes': 99}, {'sha256': 'a' * 64},
                      {'sample_role': 'unseen'}, {'period_start': '2021-01-01'},
                      {'period_start': '2020-1-1'}, {'consumed': 'false'},
                      {'redistribution': 'unknown'}, {'source': 3}, {'id': True}, {'extra': 'undeclared'}]:
            self.reject(lambda m, p=patch: m['evidence'][0].update(p))
        self.reject(lambda m: m['evidence'].append(copy.deepcopy(m['evidence'][0])))
        self.reject(lambda m: m.update(version=True))

    def test_paths_reject_escape_absolute_windows_and_symlinks(self):
        for name in ['../input.txt', '/input.txt', 'C:/input.txt', 'a\\input.txt',
                     'a/../input.txt', './input.txt', 'a//input.txt', 'input.txt:stream', 'a./x']:
            self.reject(lambda m, n=name: m['evidence'][0].update(path=n))
        try:
            (self.root / 'link').symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest('OS does not permit symlink creation')
        self.reject(lambda m: m['evidence'][0].update(path='link/input.txt'))

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        path = self.root / 'manifest.json'
        for payload in ['{"version":1,"version":1}', '{"value":NaN}', '[1]']:
            path.write_text(payload, encoding='utf-8')
            with self.assertRaises(ValueError):
                load_manifest(path)

    def test_spent_invalid_consumed_cannot_reappear_as_test_by_alias(self):
        for role, consumed in [('spent', False), ('invalid', False), ('development', True)]:
            previous = copy.deepcopy(self.manifest)
            previous['evidence'][0].update(sample_role=role, consumed=consumed)
            current = copy.deepcopy(self.manifest)
            current['evidence'][0].update(id='alias', kind='historical', sample_role='test', consumed=False)
            current['claims'][0]['evidence_ids'] = ['alias']
            with self.assertRaises(ValueError):
                verify_manifest(self.root, current, previous=previous)
        self.reject(lambda m: m['evidence'][0].update(sample_role='test'))
        previous = copy.deepcopy(self.manifest)
        previous['evidence'][0]['sha256'] = 'a' * 64
        with self.assertRaises(ValueError):
            verify_manifest(self.root, self.manifest, previous=previous)

    def test_history_cannot_be_laundered_through_an_intermediate_role(self):
        for role, consumed in [('invalid', False), ('spent', False), ('illustration', True),
                               ('development', False), ('validation', False)]:
            previous = copy.deepcopy(self.manifest)
            previous['evidence'][0].update(sample_role=role, consumed=consumed)
            current = copy.deepcopy(self.manifest)
            current['evidence'][0].update(sample_role='engineering', consumed=False)
            with self.assertRaises(ValueError):
                verify_manifest(self.root, current, previous=previous)

    def test_external_archive_hash_detects_rewritten_self_consistent_archive(self):
        target = self.root / 'bound.zip'
        pack(self.root, self.manifest, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        verify_pack(target, expected_sha256=digest)
        revised = copy.deepcopy(self.manifest)
        revised['claims'][0]['text'] = 'A different declaration with internally consistent hashes.'
        rewritten = self.root / 'rewritten.zip'
        pack(self.root, revised, rewritten)
        verify_pack(rewritten)
        with self.assertRaises(ValueError):
            verify_pack(rewritten, expected_sha256=digest)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows junction behavior')
    def test_windows_junction_is_rejected_without_symlink_privileges(self):
        import _winapi
        _winapi.CreateJunction(str(self.root), str(self.root / 'junction'))
        self.reject(lambda m: m['evidence'][0].update(path='junction/input.txt'))

    def test_archive_symlink_entry_is_rejected_without_extraction(self):
        target = self.root / 'link.zip'
        with zipfile.ZipFile(target, 'w') as archive:
            info = zipfile.ZipInfo('link')
            info.create_system, info.external_attr = 3, 0o120777 << 16
            archive.writestr(info, '../outside')
        with self.assertRaises(ValueError):
            verify_pack(target)

    def test_closeout_carries_and_verifies_trusted_previous_ledger(self):
        target = self.root / 'history.zip'
        pack(self.root, self.manifest, target, previous=self.manifest)
        verify_pack(target)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(json.loads(archive.read('history.json')), self.manifest)

    def test_zip_crc_corruption_is_rejected(self):
        target = self.root / 'crc.zip'
        pack(self.root, self.manifest, target)
        payload = target.read_bytes()
        self.assertIn(b'fixture only\n', payload)
        target.write_bytes(payload.replace(b'fixture only\n', b'fixture evil\n', 1))
        with self.assertRaises(ValueError):
            verify_pack(target)

    def pair(self, role='test', study='study-a', start='2020-12-31'):
        m = copy.deepcopy(self.manifest)
        m['evidence'][0].update(sample_role='development', kind='historical', consumed=False)
        other = copy.deepcopy(m['evidence'][0])
        (self.root / 'second.txt').write_bytes(b'other')
        other.update(id='second', path='second.txt', bytes=5,
                     sha256=hashlib.sha256(b'other').hexdigest(), sample_role=role, study_id=study, period_start=start,
                     period_end_exclusive='2022-01-01')
        m['evidence'].append(other)
        return m

    def test_overlap_is_scoped_by_study_space_and_half_open_periods(self):
        with self.assertRaises(ValueError):
            verify_manifest(self.root, self.pair())
        verify_manifest(self.root, self.pair(study='independent-study'))
        verify_manifest(self.root, self.pair(start='2021-01-01'))
        verify_manifest(self.root, self.pair(role='development'))
        separate_space = self.pair()
        separate_space['evidence'][1]['sample_space'] = 'another-instrument'
        verify_manifest(self.root, separate_space)

    def test_claim_references_disclosure_and_scientific_scope_fail_closed(self):
        for patch in [{'evidence_ids': ['missing']}, {'evidence_ids': []},
                      {'evidence_ids': ['fixture', 'fixture']}, {'disclosure_approved': False},
                      {'kind': 'historical_alpha'}, {'kind': 'clean_oos_economic'}]:
            self.reject(lambda m, p=patch: m['claims'][0].update(p))
        self.reject(lambda m: m['evidence'][0].update(disclosure_approved=False))
        for kind, role in [('historical', 'invalid'), ('reported_aggregate', 'test'),
                           ('engineering', 'test'), ('historical', 'validation')]:
            m = copy.deepcopy(self.manifest)
            m['evidence'][0].update(kind=kind, sample_role=role, consumed=False)
            m['claims'][0]['kind'] = 'clean_oos_economic'
            with self.assertRaises(ValueError):
                verify_manifest(self.root, m)
        m['evidence'][0].update(kind='historical', sample_role='test')
        verify_manifest(self.root, m)

    def test_deterministic_pack_has_internal_hashes_and_no_overwrite(self):
        first, second = self.root / 'first.zip', self.root / 'second.zip'
        pack(self.root, self.manifest, first)
        pack(self.root, self.manifest, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        verified = verify_pack(first)
        self.assertEqual(verified.evidence[0].id, 'fixture')
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))
            self.assertIn('hashes.json', archive.namelist())
            self.assertIn('manifest.json', archive.namelist())
        with self.assertRaises(FileExistsError):
            pack(self.root, self.manifest, first)

    def test_pack_tampering_duplicates_escapes_and_extra_members_rejected(self):
        original = self.root / 'ok.zip'
        pack(self.root, self.manifest, original)
        with zipfile.ZipFile(original) as archive:
            members = [(name, archive.read(name)) for name in archive.namelist()]
        variants = [members + [('manifest.json', b'{}')], members + [('../escape', b'x')],
                    members + [('extra', b'x')],
                    [(n, b'changed' if n == 'evidence/input.txt' else b) for n, b in members],
                    [(n, b'{}' if n == 'hashes.json' else b) for n, b in members]]
        for index, entries in enumerate(variants):
            target = self.root / f'bad-{index}.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                with zipfile.ZipFile(target, 'w') as archive:
                    for name, payload in entries:
                        archive.writestr(name, payload)
            with self.assertRaises(ValueError):
                verify_pack(target)

    def test_checked_in_example_validates_actual_public_asset_and_cli(self):
        root = Path(__file__).resolve().parents[1]
        example = root / 'experiments/evidence-example.json'
        manifest = load_manifest(example)
        verified = verify_manifest(root, manifest)
        self.assertIn('data/historical-results.json', [e.path for e in verified.evidence])
        command = [sys.executable, str(root / 'scripts/research_os.py')]
        for args in [['verify', str(example)], ['pack', str(example), str(self.root / 'cli.zip')],
                     ['verify-pack', str(self.root / 'cli.zip')]]:
            run = subprocess.run(command + args, cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
