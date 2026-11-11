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

    def test_cross_market_grid_preserves_states_and_frozen_examples(self):
        cross = self.data['cross_market_discovery']
        self.assertEqual(cross['source']['archive_sha256'],
                         self.data['source_archives'][0]['sha256'])
        self.assertEqual(cross['source']['member_sha256'],
                         'fcfeb019e2a0a772a4d87adac9075df198f36571fed3f86e9f4d71b1ae640946')
        total = missing = 0
        for symbol, expected in [('JP225X', (1089, 63, 20, 65)),
                                 ('UK100X', (1120, 32, 1, 32))]:
            market = cross['markets'][symbol]
            self.assertEqual((market['valid'], market['scientific_invalid'],
                              market['positive_price_R_cells']), expected[:3])
            self.assertEqual(market['qualifying_regions'], 0)
            self.assertEqual(market['qualifying_rectangles'], 0)
            self.assertEqual(set(market['grid']), {'BOTH', 'LONG', 'SHORT'})
            count = 0
            for grid in market['grid'].values():
                self.assertEqual(set(grid), {'5', '15', '30', '60'})
                for values in grid.values():
                    self.assertEqual(len(values), 96)
                    total += len(values)
                    count += sum(v is None for v in values)
            self.assertEqual(count, expected[3])
            missing += count
        self.assertEqual(total, 2304)
        self.assertEqual(missing, 97)
        valid_missing = [v for v in cross['missing_mean_cells'] if v['state']=='VALID_COMPLETE']
        self.assertEqual(len(valid_missing), 2)
        self.assertTrue(all(v['filled_trades']==v['closed_trades']==0 for v in valid_missing))
        uk = cross['examples']['UK100X_LOCAL2215_OR15_SHORT']
        self.assertEqual(uk['filled_trades'], 8)
        self.assertAlmostEqual(uk['price_total_R'], .1704990623201852)
        self.assertEqual((uk['opening_ranges'], uk['eligible_anchor_sessions']), (16, 967))

    def test_cross_market_figure_uses_each_grid_and_a_shared_zero_centred_scale(self):
        from scripts import render_orbindex as renderer
        captured = []
        original = renderer._finish

        def capture(fig, title, note, **kwargs):
            result = original(fig, title, note, **kwargs)
            if title.startswith('06'):
                captured.append(fig)
            return result

        with patch.object(renderer, '_finish', side_effect=capture):
            base = orbindex_artifacts(self.data)
        fig = captured[0]
        for ax in fig.axes[:6]:
            mesh = ax.collections[0]
            self.assertEqual((mesh.norm.vmin, mesh.norm.vcenter, mesh.norm.vmax), (-.7, 0, .25))
            self.assertEqual(mesh.get_array().size, 384)
        self.assertEqual(sum(int(ax.collections[0].get_array().mask.sum()) for ax in fig.axes[:6]), 97)
        self.assertLess(len(base['figures/orbindex-jp-uk-heatmaps.svg']), 600000)
        for symbol in ['JP225X', 'UK100X']:
            for side in ['BOTH', 'LONG', 'SHORT']:
                changed = copy.deepcopy(self.data)
                changed['cross_market_discovery']['markets'][symbol]['grid'][side]['30'][48] = .123456
                with self.subTest(symbol=symbol, side=side):
                    after = orbindex_artifacts(changed)
                    self.assertNotEqual(base['figures/orbindex-jp-uk-heatmaps.svg'],
                                        after['figures/orbindex-jp-uk-heatmaps.svg'])
                    for name in base.keys() - {'figures/orbindex-jp-uk-heatmaps.svg'}:
                        self.assertEqual(base[name], after[name])

    def test_figures_use_vector_marks_instead_of_platform_encoded_pngs(self):
        for name, blob in orbindex_artifacts(self.data).items():
            with self.subTest(figure=name):
                if b'<image' in blob:
                    self.fail(f'Unexpected platform-encoded raster image in {name}')

    def test_checked_in_figures_match_exact_rendered_bytes(self):
        from difflib import unified_diff

        for name, rendered in orbindex_artifacts(self.data).items():
            with self.subTest(figure=name):
                expected = (ROOT / name).read_bytes()
                if expected != rendered:
                    diff = unified_diff(expected.decode().splitlines(),
                                        rendered.decode().splitlines(),
                                        fromfile='checked-in', tofile='rendered', n=2)
                    excerpt = '\n'.join(line[:240] for line in list(diff)[:35])
                    self.fail(f'Exact SVG reproduction mismatch: {name}\n{excerpt}')

    def test_all_six_svg_assets_are_source_linked_and_valid(self):
        assets=orbindex_artifacts(self.data)
        self.assertEqual(len(assets),6)
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

        def capture(fig, title, note, **kwargs):
            payload = original(fig, title, note, **kwargs)
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
