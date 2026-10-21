"""Mutation checks for the reviewed claim and figure-input boundary."""

import json
from pathlib import Path
import tempfile
import unittest

from srl.claims import audit_acquisition, audit_claims, digest, quantitative_blocks


class ClaimChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'data').mkdir()
        (self.root / 'figures').mkdir()
        (self.root / 'README.md').write_text('Reported 12 events.\n')
        (self.root / 'docs/evidence.md').write_text('## Q1\n\nRetained report.\n')
        (self.root / 'data/input.json').write_text('{}')
        (self.root / 'figures/test.svg').write_text('<svg/>')
        (self.root / 'renderer.py').write_text('# test')
        self.ledger = {
            'sources': [{'id': 'Q1', 'kind': 'retained_private_report', 'disclosure': 'approved'}],
            'documents': {
                'README.md': [{'sha256': digest(b'Reported 12 events.'),
                               'kind': 'historical_report', 'source_ids': ['Q1']}],
                'docs/evidence.md': [{'sha256': digest(b'## Q1'),
                                      'kind': 'documentation', 'source_ids': []}]},
            'figures': [{'path': 'figures/test.svg', 'renderer': 'renderer.py',
                         'inputs': {'data/input.json': digest(b'{}')}, 'source_ids': ['Q1']}]}

    def check(self):
        (self.root / 'data/claim-registry.json').write_text(json.dumps(self.ledger))
        return audit_claims(self.root)['status']

    def test_valid_then_changed_quantity(self):
        self.assertEqual(self.check(), 'PASS')
        (self.root / 'README.md').write_text('Reported 120 events.\n')
        self.assertEqual(self.check(), 'FAIL')

    def test_new_claim_document_requires_review(self):
        (self.root / 'new.md').write_text('100% success')
        self.assertEqual(self.check(), 'FAIL')

    def test_source_removal_and_disclosure(self):
        self.ledger['sources'][0]['disclosure'] = 'pending'
        self.assertEqual(self.check(), 'FAIL')
        self.ledger['sources'] = []
        self.assertEqual(self.check(), 'FAIL')

    def test_private_report_cannot_be_public_replay(self):
        self.ledger['documents']['README.md'][0]['kind'] = 'public_replay'
        self.assertEqual(self.check(), 'FAIL')

    def test_input_mutation_and_undeclared_figure(self):
        (self.root / 'data/input.json').write_text('{"changed":true}')
        self.assertEqual(self.check(), 'FAIL')

    def test_figures_cannot_drop_inputs_or_use_external_paths(self):
        for field, value in (('inputs', {}), ('renderer', str(self.root / 'renderer.py')),
                             ('renderer', '../renderer.py'), ('path', '/external.svg')):
            original = self.ledger['figures'][0][field]
            self.ledger['figures'][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(self.check(), 'FAIL')
            self.ledger['figures'][0][field] = original

    def test_figures_reject_external_input_bad_hash_and_duplicates(self):
        original = self.ledger['figures'][0]['inputs']
        for inputs in ({str(self.root / 'data/input.json'): digest(b'{}')},
                       {'../outside.json': digest(b'{}')}, {'data/input.json': 'bad-hash'}):
            self.ledger['figures'][0]['inputs'] = inputs
            self.assertEqual(self.check(), 'FAIL')
        self.ledger['figures'][0]['inputs'] = original
        self.ledger['figures'].append(dict(self.ledger['figures'][0]))
        self.assertEqual(self.check(), 'FAIL')
        (self.root / 'figures/extra.svg').write_text('<svg/>')
        self.assertEqual(self.check(), 'FAIL')

    def test_numeric_detection_includes_tables_excludes_code_and_urls(self):
        text = 'Text [reference](https://example.org/2026).\n\n```sh\nrun 100\n```\n\n| n |\n| 12 |'
        self.assertEqual(quantitative_blocks(text), ['| n |\n| 12 |'])

    def acquisition(self):
        from srl.fx_study import SOURCE_URL

        snapshot = b'Date,USD,JPY\n2016-06-01,1.1,110\n2016-06-02,1.2,120\n'
        (self.root / 'data/ecb-fx-reference.csv').write_bytes(snapshot)
        files = ('src/srl/fx_study.py', 'scripts/fx_study.py', 'tests/test_fx_study.py',
                 'experiments/ecb-fx-mom20-protocol.md', 'DATA_LICENSE.md')
        for name in files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixture')
        return {'source_url': SOURCE_URL, 'rights_reviewed': True,
                'archive_notice_check': 'PASS_SINGLE_CSV_NO_EXTRA_NOTICE',
                'canonical_csv_sha256': digest(snapshot), 'selected_rows': 2,
                'protocol_commit': 'a' * 40,
                'frozen_file_sha256': {name: digest(b'fixture') for name in files}}

    def save_acquisition(self, receipt):
        (self.root / 'data/ecb-acquisition.json').write_text(json.dumps(receipt))

    def test_acquisition_receipt_binds_snapshot_and_preaccess_methods(self):
        receipt = self.acquisition()
        self.save_acquisition(receipt)
        audit_acquisition(self.root)
        (self.root / 'src/srl/fx_study.py').write_bytes(b'amended')
        with self.assertRaisesRegex(ValueError, 'method changed'):
            audit_acquisition(self.root)

    def test_acquisition_rejects_rights_source_identity_and_incomplete_freeze(self):
        receipt = self.acquisition()
        for field, value in (('rights_reviewed', False), ('source_url', 'https://example.org'),
                             ('archive_notice_check', 'PENDING'), ('canonical_csv_sha256', 'b' * 64),
                             ('selected_rows', 3), ('protocol_commit', 'not-a-commit')):
            changed = dict(receipt, **{field: value})
            self.save_acquisition(changed)
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit_acquisition(self.root)
        receipt['frozen_file_sha256'].pop('DATA_LICENSE.md')
        self.save_acquisition(receipt)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            audit_acquisition(self.root)
