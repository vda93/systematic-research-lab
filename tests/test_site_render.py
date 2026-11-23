"""Public reading editions must stay short, source-checked and reproducible."""

import json
from pathlib import Path
import re
import unittest

from scripts import render_site
from scripts.site_studies import STUDIES


ROOT = Path(__file__).resolve().parents[1]


class SiteRenderingTests(unittest.TestCase):
    def test_social_metadata_and_linkedin_identity_are_present(self):
        base = 'https://vda93.github.io/systematic-research-lab/'
        linkedin = 'https://www.linkedin.com/in/andrew-vu-4861b9191/'
        for page in ('index', 'orbindex', 'macroimpulse', 'orb-setup-filters'):
            with self.subTest(page=page):
                html = (ROOT / 'docs' / f'{page}.html').read_text(encoding='utf-8')
                expected_url = base if page == 'index' else base + f'{page}.html'
                self.assertIn(f'property="og:url" content="{expected_url}"', html)
                self.assertIn(f'property="og:image" content="{base}social-preview.png"', html)
                self.assertIn('property="og:description"', html)
                self.assertIn('property="og:title"', html)
                self.assertIn('property="og:image:width" content="1200"', html)
                self.assertIn('property="og:image:height" content="630"', html)
                self.assertIn(linkedin, html)
                self.assertIn('Andrew Vu', html)

    def test_numeric_facts_are_bound_to_registered_technical_source(self):
        ledger = json.loads((ROOT / "data/claim-registry.json").read_text(encoding="utf-8"))
        for slug, study in STUDIES.items():
            with self.subTest(study=slug):
                values = render_site.validate_study(ROOT, slug, study, ledger)
                self.assertEqual(set(values), set(study["facts"]))
                for value in values.values():
                    self.assertTrue(any(value in paragraph for paragraph in
                                        (ROOT / study["technical"]).read_text(encoding="utf-8").split("\n\n")))

    def test_unreviewed_numeric_public_copy_is_rejected(self):
        with self.assertRaises(ValueError):
            render_site.public_text("Backtest returned 999.9%", {})
        ledger = json.loads((ROOT / "data/claim-registry.json").read_text(encoding="utf-8"))
        original = STUDIES["orbindex"]["facts"]["a_eur"]["value"]
        try:
            STUDIES["orbindex"]["facts"]["a_eur"]["value"] = "+€999.99"
            with self.assertRaises(ValueError):
                render_site.validate_study(ROOT, "orbindex", STUDIES["orbindex"], ledger)
        finally:
            STUDIES["orbindex"]["facts"]["a_eur"]["value"] = original

    def test_short_website_and_full_technical_record_are_distinct(self):
        orb = (ROOT / "docs/orbindex.html").read_text(encoding="utf-8")
        news = (ROOT / "docs/macroimpulse.html").read_text(encoding="utf-8")
        filters = (ROOT / "docs/orb-setup-filters.html").read_text(encoding="utf-8")
        for html in (orb, news, filters):
            self.assertNotIn("OOS_EXPLORATORY", html)
            self.assertNotIn("POSSIBLE_PRIOR_EXPOSURE", html)
            self.assertIn("Data and verification", html)
            self.assertIn("Complete research record", html)
            self.assertNotIn('class="mark"', html)
            self.assertLess(len(re.sub(r"<[^>]+>", " ", html).split()), 1000)
        self.assertIn("cannot be treated as a completely fresh independent test", orb)
        self.assertIn("None of the frozen portfolios was promoted", orb)
        self.assertIn("News-Release Trading", news)
        self.assertIn("Why I shelved this", news)
        self.assertIn("slippage", news)
        self.assertNotIn("MacroImpulse", news)

    def test_full_orbindex_record_and_verified_figures_remain(self):
        article = (ROOT / "studies/orbindex.md").read_text(encoding="utf-8")
        names = ("search", "jp-uk-heatmaps", "portfolios", "curves",
                 "economics", "forensics")
        for name in names:
            with self.subTest(panel=name):
                path = f"orbindex-{name}.svg"
                self.assertIn(f"../figures/{path}", article)
                self.assertEqual(
                    (ROOT / "figures" / path).read_bytes(),
                    (ROOT / "docs/plots" / path).read_bytes(),
                )
        self.assertEqual(sum(line.startswith("| Portfolio") or line.startswith("| Market")
                             for line in article.splitlines()), 4)
        self.assertIn("OOS_EXPLORATORY / POSSIBLE_PRIOR_EXPOSURE", article)

    def test_public_orbindex_curves_precede_economic_comparison(self):
        page = (ROOT / "docs/orbindex.html").read_text(encoding="utf-8")
        curve = 'src="plots/orbindex-curves.svg"'
        economics = 'src="plots/orbindex-economics.svg"'
        self.assertEqual(page.count(curve), 1)
        self.assertLess(page.index(curve), page.index(economics))
        self.assertIn("Quarter-end cumulative gross price R snapshots", page)
        self.assertIn("not an annualized or broker-net comparison", page)
        self.assertEqual(
            (ROOT / "docs/plots/orbindex-curves.svg").read_bytes(),
            (ROOT / "figures/orbindex-curves.svg").read_bytes(),
        )

    def test_site_outputs_and_offline_figures_are_exact(self):
        outputs = render_site.site_artifacts(ROOT)
        self.assertEqual(
            {name for name in outputs if name.endswith(".html")},
            {"docs/index.html", "docs/orbindex.html", "docs/macroimpulse.html",
             "docs/orb-setup-filters.html"},
        )
        for path, payload in outputs.items():
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), payload)
                if path.startswith("docs/plots/"):
                    self.assertEqual(
                        (ROOT / "figures" / Path(path).name).read_bytes(), payload
                    )

    def test_three_public_studies_and_plain_english_decisions(self):
        landing = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertIn("ORBINDEX", landing)
        self.assertIn("News-Release Trading", landing)
        self.assertIn("ORB Setup and Filters", landing)
        self.assertEqual(landing.count('<article class="card">'), 3)
        self.assertNotIn("MacroImpulse", landing)
        self.assertNotIn("NOWICK", landing)
        self.assertNotIn("Engulfing", landing)
        self.assertIn("Main limitation.", (ROOT / "docs/orbindex.html").read_text())

    def test_each_study_links_its_own_aggregate_data(self):
        expected = {
            "orbindex": "data/orbindex-public.json",
            "macroimpulse": "data/macro-public.json",
            "orb-setup-filters": "data/orb-setup-filters-public.json",
        }
        for slug, data in expected.items():
            with self.subTest(study=slug):
                page = (ROOT / "docs" / f"{slug}.html").read_text(encoding="utf-8")
                self.assertIn(f'{render_site.REPO}/blob/main/{data}', page)
                for other in set(expected.values()) - {data}:
                    self.assertNotIn(f'{render_site.REPO}/blob/main/{other}', page)
        filters = (ROOT / "docs/orb-setup-filters.html").read_text(encoding="utf-8")
        self.assertIn("studies/orb-setup-filters-appendix.md", filters)


if __name__ == "__main__":
    unittest.main()
