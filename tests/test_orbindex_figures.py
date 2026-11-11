"""ORBINDEX public figures are data-bound illustrations, not market replay."""

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts.render_orbindex import orbindex_artifacts


ROOT = Path(__file__).resolve().parents[1]


class ORBIndexFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data/orbindex-public.json').read_text(encoding='utf-8'))

    def test_source_and_scope_are_not_presented_as_executable_backtests(self):
        d=self.data
        self.assertEqual(d['search']['total_cells'], 3456)
        self.assertEqual(d['search']['valid_cells'] + d['search']['invalid_cells'], 3456)
        self.assertEqual(set(d['portfolio']), set('ABC'))
        self.assertEqual(len(d['source_archives']), 4)
        self.assertTrue(all(len(x['sha256'])==64 for x in d['source_archives']))
        self.assertIn('PRIVATE_BACKTEST_NOT_REPLAYABLE',d['scope'])
        self.assertEqual(d['forensic']['holdout_disclosure'],'OOS_EXPLORATORY_POSSIBLE_PRIOR_EXPOSURE')
        self.assertEqual(d['search']['supported_de30_rectangles_extra_005r'],0)
        self.assertTrue(all(d['portfolio'][k]['oos']['eur'] < 0 for k in 'ABC'))

    def test_all_five_svg_assets_are_source_linked_and_valid(self):
        assets=orbindex_artifacts(self.data)
        self.assertEqual(len(assets),5)
        for name,blob in assets.items():
            with self.subTest(name=name):
                root=ET.fromstring(blob)
                self.assertTrue(root.tag.endswith('svg'))
                self.assertTrue((ROOT / name).is_file())
                self.assertGreater(len(blob), 500)

    def test_figure_output_changes_when_relevant_data_changes(self):
        base=orbindex_artifacts(self.data)
        changed=copy.deepcopy(self.data)
        changed['portfolio']['A']['oos']['eur']=-999.0
        after=orbindex_artifacts(changed)
        self.assertNotEqual(base['figures/orbindex-economics.svg'],after['figures/orbindex-economics.svg'])
        changed=copy.deepcopy(self.data)
        changed['search']['de30_long_mean_r_by_15min_anchor']['30'][23]=.2479
        after=orbindex_artifacts(changed)
        self.assertNotEqual(base['figures/orbindex-search.svg'],after['figures/orbindex-search.svg'])

    def test_figures_are_deterministic_and_each_responds_to_its_source(self):
        base = orbindex_artifacts(self.data)
        self.assertEqual(base, orbindex_artifacts(self.data))
        changes = {
            'search': lambda d: d['search']['symbols']['DE30X'].update(positive_price_r=100),
            'portfolios': lambda d: d['portfolio']['A']['sleeves'][0].update(time='08:00'),
            'curves': lambda d: d['portfolio']['A']['oos']['quarterly_cumulative_r'][-1].__setitem__(1, -25),
            'economics': lambda d: d['portfolio']['A']['oos'].update(s2_eur=-500),
            'forensics': lambda d: d['forensic']['A_exit_year'][1].update(conversion_pct=40),
        }
        for name, mutate in changes.items():
            changed = copy.deepcopy(self.data)
            mutate(changed)
            with self.subTest(figure=name):
                path = f'figures/orbindex-{name}.svg'
                self.assertNotEqual(base[path], orbindex_artifacts(changed)[path])

    def test_plot_labels_fit_and_cumulative_samples_begin_at_zero(self):
        from matplotlib.text import Text
        from scripts import render_orbindex as renderer

        figures = []
        original = renderer._finish

        def capture(fig, title, note):
            payload = original(fig, title, note)
            figures.append(fig)
            return payload

        with patch.object(renderer, '_finish', side_effect=capture):
            orbindex_artifacts(self.data)
        for fig in figures:
            fig.canvas.draw()
            for label in fig.findobj(Text):
                if label.get_visible() and label.get_text():
                    box = label.get_window_extent(fig.canvas.get_renderer())
                    with self.subTest(label=label.get_text()):
                        self.assertGreaterEqual(box.x0, 0)
                        self.assertLessEqual(box.x1, fig.bbox.width)
                        self.assertGreaterEqual(box.y0, 0)
                        self.assertLessEqual(box.y1, fig.bbox.height)
        schedule = figures[1].axes[0]
        legend = schedule.get_legend().get_window_extent(figures[1].canvas.get_renderer())
        self.assertGreater(legend.y0, schedule.transData.transform((8, 2.25))[1])
        for ax in figures[2].axes:
            curves = [line for line in ax.lines if line.get_label().startswith('Portfolio')]
            self.assertEqual(len(curves), 3)
            for curve in curves:
                self.assertEqual(curve.get_ydata()[0], 0)

    def test_portfolio_native_and_oos_arithmetic_at_reported_precision(self):
        d=self.data
        for name in 'ABC':
            s=d['portfolio'][name]
            self.assertEqual(s['oos']['trades'],sum(x['trades'] for x in s['oos']['annual']))
            self.assertAlmostEqual(s['oos']['price_r'],sum(x['gross_r'] for x in s['oos']['annual']),delta=.001)
            self.assertAlmostEqual(s['oos']['price_r'],s['oos']['quarterly_cumulative_r'][-1][1],delta=.002)
            self.assertAlmostEqual(s['discovery']['price_r'],s['discovery']['quarterly_cumulative_r'][-1][1],delta=.002)


if __name__=='__main__':
    unittest.main()
