"""Published pages must stay bound to the reviewed Markdown and figure inputs."""

from pathlib import Path
import unittest

from scripts import render_site

ROOT = Path(__file__).resolve().parents[1]


class SiteRenderingTests(unittest.TestCase):
    def test_checked_pages_and_offline_figures_match_their_sources(self):
        outputs = render_site.site_artifacts(ROOT)
        self.assertEqual(
            {path for path in outputs if path.endswith('.html')},
            {f'docs/{slug}.html' for slug in ('index', 'orb', 'ebp', 'orbindex', 'macroimpulse')},
        )
        for name, payload in outputs.items():
            with self.subTest(path=name):
                self.assertEqual((ROOT / name).read_bytes(), payload)
                if name.startswith('docs/plots/'):
                    self.assertEqual((ROOT / 'figures' / Path(name).name).read_bytes(), payload)

    def test_excerpt_selector_rejects_missing_or_ambiguous_paragraphs(self):
        for paragraphs in (['Another study.'], ['Gold fell.', 'Gold rose.']):
            with self.subTest(paragraphs=paragraphs), self.assertRaises(ValueError):
                render_site.select_paragraph(paragraphs, 'Gold')

    def test_quantitative_excerpt_requires_a_registered_digest_and_source(self):
        block = 'The comparison used 17 sessions.'
        for records in ([], [{'sha256': 'x', 'source_ids': ['A'], 'kind': 'historical_report'}]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                render_site.check_excerpt(block, records, ('A',), {'A'})

    def test_summary_drift_cannot_change_a_reviewed_finding(self):
        with self.assertRaises(ValueError):
            render_site.check_summary('The order stayed open.', ['The order was cancelled.'])

    def test_inline_citation_preserves_the_following_qualification(self):
        block = 'See [the rule](../docs/limitations.md). **Costs still apply.** [A](../docs/evidence.md#a)'
        html = render_site.display_prose(block, 'studies/example.md')
        self.assertIn('<strong>Costs still apply.</strong>', html)
        self.assertIn('/blob/main/docs/limitations.md', html)
