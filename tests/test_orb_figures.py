"""Preserve complete searched grids, independent decisions and source-driven marks."""
import copy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class ORBFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.u = json.loads((ROOT/'data/orb-ustec-public.json').read_text())
        cls.g = json.loads((ROOT/'data/orb-gold-public.json').read_text())

    def test_complete_grid_and_distinct_invalid_and_empty_states(self):
        from scripts.render_orb import grid_values, validate
        validate(self.u, self.g)
        self.assertEqual(grid_values(self.u, 'LONG_ONLY').shape, (6, 96))
        values = grid_values(self.g, 'LONG_ONLY')
        self.assertEqual(values.shape, (6, 96))
        self.assertEqual(len(self.u['cells']), 1728)
        self.assertEqual(sum(c[8] for c in self.u['cells']), 22)
        self.assertEqual(sum(c[9] for c in self.u['cells']), 18)
        self.assertEqual(sum(c[10] for c in self.u['cells']), 1)
        self.assertEqual(sum(c[4]=='SCIENTIFIC_INVALID' for c in self.g['cells']), 2)
        self.assertEqual(sum(c[4]=='VALID_COMPLETE' and c[5]==0 for c in self.g['cells']), 30)

    def test_missing_duplicate_or_nonfinite_evidence_fails_closed(self):
        from scripts.render_orb import orb_artifacts
        for mutate in [lambda d:d['cells'].pop(),
                       lambda d:d['cells'].__setitem__(1,d['cells'][0]),
                       lambda d:d['cells'][0].__setitem__(6,float('nan')),
                       lambda d:d.update(scope='PUBLIC_REPLAY')]:
            d=copy.deepcopy(self.u); mutate(d)
            with self.assertRaises(ValueError): orb_artifacts(d,self.g)

    def test_oos_curve_and_reported_total_must_reconcile(self):
        from scripts.render_orb import orb_artifacts
        d=copy.deepcopy(self.u);d['oos'][0]['total_r']=25
        with self.assertRaisesRegex(ValueError,'OOS'): orb_artifacts(d,self.g)

    def test_annotations_follow_changed_source_counts_and_diagnostics(self):
        from scripts.render_orb import orb_artifacts
        d=copy.deepcopy(self.u)
        row=next(r for r in d['cells'] if r[8] and not r[9])
        row[8]=False
        d['census']['robust_cells']-=1
        d['concentration']['maximum']['total_r']=99
        rendered=orb_artifacts(d,self.g)
        self.assertTrue(b'Robust outside plateau (3)' in rendered['figures/orb-ustec-qualification.svg'])
        self.assertTrue(b'+99.00R' in rendered['figures/orb-ustec-selection.svg'])

    def test_source_projections_keep_cost_roles_and_oos_separate(self):
        self.assertAlmostEqual(self.u['oos'][0]['total_r'],26.412958684602135)
        self.assertAlmostEqual(self.u['oos'][1]['total_r'],-.5763919629236827)
        self.assertEqual([r['gate'] for r in self.u['oos']],['PASS','FAIL'])
        self.assertEqual(self.g['monetary']['feasible'],0)
        self.assertEqual(sum(r['trades'] for r in self.g['monetary']['rows']),1376)
        self.assertEqual(sum(r['synthetic_exits'] for r in self.g['monetary']['rows']),6)
        for r in self.g['monetary']['rows']:
            self.assertAlmostEqual(r['net_pnl'],r['gross_pnl']+r['swap']+r['commission']+r['fee'])
        for block in self.u['oos']:
            self.assertAlmostEqual(block['exit_month_cumulative_r'][-1][1],block['total_r'])

    def test_control_axes_show_every_paired_observation(self):
        from scripts import render_orb as renderer
        figures=[]; original=renderer._finish
        def capture(fig,*a,**kw):
            result=original(fig,*a,**kw);figures.append(fig);return result
        with patch.object(renderer,'_finish',side_effect=capture):
            renderer._controls(self.u)
        for ax in figures[0].axes:
            lo,hi=ax.get_xlim()
            for x,y in ax.collections[0].get_offsets():
                self.assertGreaterEqual(x-lo,.005)
                self.assertGreaterEqual(hi-x,.005)

    def test_validation_date_labels_do_not_overlap(self):
        from scripts import render_orb as renderer
        figures=[]; original=renderer._finish
        def capture(fig,*a,**kw):
            result=original(fig,*a,**kw);figures.append(fig);return result
        with patch.object(renderer,'_finish',side_effect=capture): renderer._validation(self.u)
        fig=figures[0];fig.canvas.draw()
        for ax in fig.axes:
            boxes=[t.get_window_extent(fig.canvas.get_renderer()) for t in ax.get_xticklabels() if t.get_visible()]
            for left,right in zip(boxes,boxes[1:]): self.assertLess(left.x1,right.x0)

    def test_every_relevant_source_changes_its_figure(self):
        from scripts.render_orb import orb_artifacts
        before=orb_artifacts(self.u,self.g)
        mutations={
            'ustec-surface':('u',lambda d:d['cells'][0].__setitem__(6,.234)),
            'ustec-selection':('u',lambda d:d['concentration']['maximum'].update(total_r=99)),
            'ustec-controls':('u',lambda d:d['placebo_comparisons'][0].update(delta_mean_r=.2)),
            'ustec-validation':('u',lambda d:(d['oos'][0].update(total_r=25),d['oos'][0]['exit_month_cumulative_r'][-1].__setitem__(1,25))),
            'gold-surface':('g',lambda d:d['cells'][0].__setitem__(7,.234)),
            'gold-stress':('g',lambda d:d['stress'][0].update(mean_r=.3)),
            'gold-economics':('g',lambda d:d['monetary']['rows'][0].update(gross_pnl=999)),
        }
        for name,(kind,mutate) in mutations.items():
            u,g=copy.deepcopy(self.u),copy.deepcopy(self.g)
            mutate(u if kind=='u' else g)
            with self.subTest(figure=name):
                self.assertNotEqual(before[f'figures/orb-{name}.svg'],orb_artifacts(u,g)[f'figures/orb-{name}.svg'])

    def test_exact_reproduction_and_vector_output(self):
        from scripts.render_orb import orb_artifacts
        result=orb_artifacts(self.u,self.g)
        self.assertEqual(len(result),9)
        self.assertEqual(result,orb_artifacts(self.u,self.g))
        for name,blob in result.items():
            with self.subTest(name=name):
                self.assertLess(len(blob),600000)
                self.assertNotIn(b'<image',blob)
                svg=ET.fromstring(blob)
                self.assertEqual(svg.attrib.get('role'),'img')
                self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}title'))
                self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}desc'))
                self.assertEqual((ROOT/name).read_bytes(),blob)

    def test_all_visible_labels_fit_canvas(self):
        from matplotlib.text import Text
        from scripts import render_orb as renderer
        figures=[]
        original=renderer._finish
        def capture(fig,*args,**kwargs):
            result=original(fig,*args,**kwargs);figures.append(fig);return result
        with patch.object(renderer,'_finish',side_effect=capture):
            renderer.orb_artifacts(self.u,self.g)
        for fig in figures:
            fig.canvas.draw()
            for label in fig.findobj(Text):
                if label.get_visible() and label.get_text():
                    box=label.get_window_extent(fig.canvas.get_renderer())
                    with self.subTest(label=label.get_text()):
                        self.assertGreaterEqual(box.x0,-1)
                        self.assertLessEqual(box.x1,fig.bbox.width+1)
                        self.assertGreaterEqual(box.y0,-1)
                        self.assertLessEqual(box.y1,fig.bbox.height+1)


if __name__=='__main__': unittest.main()
