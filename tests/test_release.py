"""Publication hygiene checks use harmless fake fixtures, never real secrets."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_public import audit_directory, text_findings, metadata_findings


class PublicationAuditTests(unittest.TestCase):
    def test_public_owner_and_github_merge_metadata_are_bounded(self):
        owner='12345+vda93@users.noreply.github.com'
        self.assertEqual(metadata_findings('vda93\n'+owner+'\nvda93\n'+owner+'\npublic commit'),[])
        merge_metadata='vda93\n'+owner+'\nGitHub\nnoreply@github.com\nMerge pull request'
        self.assertEqual(metadata_findings(merge_metadata,merge=True),[])
        self.assertTrue(metadata_findings(merge_metadata,merge=False))
        self.assertTrue(metadata_findings('vda93\n'+owner+'\nUnknown\nother@example.com\ncommit'))
    def test_auditor_source_passes_its_own_generic_content_rules(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(text_findings('scripts/audit_public.py', (root / 'scripts/audit_public.py').read_bytes()), [])

    def make_tree(self, root):
        (root / 'README.md').write_text('An original synthetic demonstration.\n', encoding='utf-8')
        (root / 'release-files.json').write_text(json.dumps(['README.md', 'release-files.json']), encoding='utf-8')

    def test_exact_inventory_and_relative_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            self.assertEqual(audit_directory(root)['status'], 'PASS')
            (root / 'extra.txt').write_text('unexpected')
            self.assertEqual(audit_directory(root)['status'], 'FAIL')

    def test_missing_files_and_broken_links_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            (root / 'README.md').write_text('[missing](missing.md)')
            self.assertEqual(audit_directory(root)['status'], 'FAIL')
            (root / 'README.md').unlink()
            self.assertEqual(audit_directory(root)['status'], 'FAIL')

    def test_unsafe_names_binary_artifacts_and_private_endpoints_fail(self):
        cases = [('escape', ['../outside.md']), ('archive', ['README.md', 'release-files.json', 'sample.zip']),
                 ('endpoint', ['README.md', 'release-files.json'])]
        for case, names in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_tree(root)
                (root / 'release-files.json').write_text(json.dumps(names))
                if case == 'archive':
                    (root / 'sample.zip').write_bytes(b'not-an-archive')
                if case == 'endpoint':
                    (root / 'README.md').write_text('https://' + 'drive.google.com/drive/folders/example')
                self.assertEqual(audit_directory(root)['status'], 'FAIL')

    def test_generated_bytecode_is_not_source_but_unlisted_prose_is(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            cache = root / '__pycache__'
            cache.mkdir()
            (cache / 'example.pyc').write_bytes(b'cache')
            self.assertEqual(audit_directory(root)['status'], 'PASS')
            (root / 'notes.md').write_text('unlisted')
            self.assertEqual(audit_directory(root)['status'], 'FAIL')

    def test_missing_heading_fragment_fails_and_duplicate_slug_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            (root / 'README.md').write_text('# Evidence\n\n[missing](README.md#absent)\n')
            self.assertEqual(audit_directory(root)['status'], 'FAIL')
            (root / 'README.md').write_text('# Evidence\n\n# Evidence\n\n[second](README.md#evidence-1)\n')
            self.assertEqual(audit_directory(root)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
