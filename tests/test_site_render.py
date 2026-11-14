"""The reading edition must preserve the reviewed article, including its figure order."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

from markdown_it import MarkdownIt

from scripts import render_site


ROOT = Path(__file__).resolve().parents[1]


class ArticleReader(HTMLParser):
    """Read article text and images in document order, excluding the table of contents."""

    def __init__(self, html, inside=False):
        super().__init__()
        self.inside = inside
        self.in_nav = False
        self.text = []
        self.images = []
        self.tables = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.inside = True
        if tag == 'nav':
            self.in_nav = True
        if self.inside and not self.in_nav:
            if tag == 'img':
                self.images.append(dict(attrs)['src'])
            if tag == 'table':
                self.tables += 1

    def handle_endtag(self, tag):
        if tag == 'article':
            self.inside = False
        if tag == 'nav':
            self.in_nav = False

    def handle_data(self, data):
        if self.inside and not self.in_nav:
            self.text.append(data)

    def words(self):
        return re.sub(r'\s+', '', ''.join(self.text))


class SiteRenderingTests(unittest.TestCase):
    def test_reading_editions_include_every_canonical_paragraph_and_table_in_order(self):
        markdown = MarkdownIt('commonmark').enable('table')
        for slug, source in (('orbindex', 'orbindex'), ('macroimpulse', 'news-research')):
            with self.subTest(study=slug):
                canonical = (ROOT / f'studies/{source}.md').read_text(encoding='utf-8')
                expected = ArticleReader(markdown.render(canonical), inside=True)
                actual = ArticleReader((ROOT / f'docs/{slug}.html').read_text(encoding='utf-8'))
                self.assertEqual(expected.words(), actual.words())
                self.assertEqual(expected.tables, actual.tables)
                self.assertEqual([Path(x).name for x in expected.images],
                                 [Path(x).name for x in actual.images])

    def test_original_orbindex_panels_keep_their_source_order_and_captions(self):
        page = ArticleReader((ROOT / 'docs/orbindex.html').read_text(encoding='utf-8'))
        self.assertEqual(page.images, [f'plots/orbindex-{panel}.svg' for panel in
                         ('search', 'jp-uk-heatmaps', 'portfolios', 'curves', 'economics', 'forensics')])
        self.assertIn('Figure 6 uses one zero-centred colour scale', ''.join(page.text))
        self.assertEqual(page.tables, 4)

    def test_outputs_are_current_and_all_offline_plots_match_their_sources(self):
        outputs = render_site.site_artifacts(ROOT)
        self.assertEqual({name for name in outputs if name.endswith('.html')},
                         {'docs/index.html', 'docs/orbindex.html', 'docs/macroimpulse.html'})
        for name, payload in outputs.items():
            with self.subTest(path=name):
                self.assertEqual((ROOT / name).read_bytes(), payload)
                if name.startswith('docs/plots/'):
                    self.assertEqual((ROOT / 'figures' / Path(name).name).read_bytes(), payload)

    def test_numeric_source_mutation_cannot_be_rendered_using_old_review(self):
        ledger = json.loads((ROOT / 'data/claim-registry.json').read_bytes())
        path = 'studies/orbindex.md'
        original = (ROOT / path).read_text(encoding='utf-8')
        with self.assertRaises(ValueError):
            render_site.reviewed_markdown(path, original.replace('3,456', '3,455', 1), ledger)
