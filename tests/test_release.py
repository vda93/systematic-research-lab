"""Publication hygiene checks use harmless fake fixtures, never real secrets."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_public import audit_directory, text_findings, metadata_findings


class PublicationAuditTests(unittest.TestCase):
    def test_csv_exception_is_specific_to_the_reviewed_provider_snapshot(self):
        from scripts.audit_public import text_findings

        self.assertEqual(text_findings('data/ecb-fx-reference.csv', b'Date,USD,JPY\n'), [])
        self.assertTrue(text_findings('data/vendor.csv', b'Date,USD,JPY\n'))

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


    def test_public_research_site_is_bounded(self):
        page = b'<!doctype html><html><main><h1>Research</h1><div id="research"></div><a href="#research">Studies</a></main></html>'
        self.assertEqual(text_findings('docs/index.html', page), [])
        self.assertTrue(text_findings('docs/other.html', page))
        self.assertTrue(text_findings('docs/index.html', page.replace(b'#research', b'#missing')))
        self.assertTrue(text_findings('docs/index.html', page.replace(b'#research', b'https://example.com')))
        self.assertTrue(text_findings('docs/index.html', page + b'<script src="https://example.com"></script>'))

    def test_site_accepts_only_static_markup_and_local_resources(self):
        page = '<html><main><h1>Library</h1>{}</main></html>'
        approved = [
            '<a href="orb.html#results">Study</a>',
            '<img src="plots/orb-summary.svg" alt="Validation results">',
            '<link rel="stylesheet" href="site.css">',
        ]
        for item in approved:
            with self.subTest(item=item):
                self.assertEqual(text_findings('docs/ebp.html', page.format(item).encode()), [])
        rejected = [
            '<h2 onload="">Finding</h2>', "<p onerror=''>Finding</p>",
            '<script></script>', '<p style="color: blue">Finding</p>',
            '<a href="javascript:">Study</a>', '<a href="//example.com/">Study</a>',
            '<link rel="stylesheet" href="https://example.com/theme.css">',
            '<img src="https://github.com/vda93/systematic-research-lab" alt="Remote">',
            '<a href="/orb.html">Study</a>', '<meta http-equiv="refresh" content="0">',
        ]
        for item in rejected:
            with self.subTest(item=item):
                self.assertTrue(text_findings('docs/index.html', page.format(item).encode()))
        self.assertTrue(text_findings('docs/test.js', b''))
        self.assertTrue(text_findings('docs/plots/unreviewed.svg', b'<svg/>'))
        self.assertTrue(text_findings('docs/site.css', b'@import "https://example.com/theme.css";'))
        self.assertEqual(text_findings('docs/.nojekyll', b''), [])
        self.assertTrue(text_findings('docs/.nojekyll', b'unexpected'))

    def test_site_links_require_a_real_page_and_fragment_in_the_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / 'docs'
            docs.mkdir()
            paths = ['docs/index.html', 'docs/orb.html', 'docs/evidence.md', 'release-files.json']
            (root / 'release-files.json').write_text(json.dumps(paths))
            (docs / 'evidence.md').write_text('## O1\n')
            base = '<html><main><h1>Question</h1>{}</main></html>'
            (docs / 'orb.html').write_text(base.format('<h2 id="results">Results</h2>'))
            evidence = 'https://github.com/vda93/systematic-research-lab/blob/main/docs/evidence.md'
            for target, status in [('orb.html#results', 'PASS'), (evidence+'#o1', 'PASS'),
                                   ('orb.html#absent', 'FAIL'), ('ebp.html', 'FAIL'),
                                   (evidence+'#missing', 'FAIL'), (evidence+'x', 'FAIL')]:
                with self.subTest(target=target):
                    (docs / 'index.html').write_text(base.format(f'<a href="{target}">Read</a>'))
                    self.assertEqual(audit_directory(root)['status'], status)

    def test_figure_copy_requires_the_registered_original_bytes(self):
        source = Path(__file__).resolve().parents[1] / 'figures/orb-summary.svg'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ['figures', 'docs/plots', 'data']:
                (root / directory).mkdir(parents=True)
            names = ['figures/orb-summary.svg', 'docs/plots/orb-summary.svg',
                     'data/claim-registry.json', 'release-files.json']
            original, copy, registry, inventory = [root / name for name in names]
            inventory.write_text(json.dumps(names))
            original.write_bytes(source.read_bytes())
            copy.write_bytes(original.read_bytes())
            registry.write_text(json.dumps({'figures': [{'path': names[0]}]}))
            self.assertEqual(audit_directory(root)['status'], 'PASS')
            copy.write_bytes(b'<svg/>')
            self.assertEqual(audit_directory(root)['status'], 'FAIL')
            copy.write_bytes(original.read_bytes())
            registry.write_text(json.dumps({'figures': []}))
            self.assertEqual(audit_directory(root)['status'], 'FAIL')

    def test_legacy_landing_page_allowance_ends_at_its_original_merge(self):
        from scripts.audit_public import is_archived_landing_page as archived

        page = 'docs/index.html'
        blob = '35b280c49072484b6f6379707bf87ef0f374b874'
        introduction = '24d794f5efcc0ba8b3911c5452f47e6d23223de8'
        merge = '4e787e90db81cc29336c163088c806b23bc6225c'
        self.assertTrue(archived(page, blob, introduction))
        self.assertTrue(archived(page, blob, merge))
        self.assertFalse(archived(page, blob, 'f' * 40))
        self.assertFalse(archived('docs/orb.html', blob, introduction))
        self.assertFalse(archived(page, '0' * 40, introduction))

if __name__ == '__main__':
    unittest.main()
