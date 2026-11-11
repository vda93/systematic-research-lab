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

    def test_annotations_follow_coherent_robust_count_change(self):
        from scripts.render_orb import orb_artifacts
        d=copy.deepcopy(self.u)
        row=next(r for r in d['cells'] if r[8] and not r[9])
        row[8]=False
        d['census']['robust_cells']-=1
        rendered=orb_artifacts(d,self.g)
        self.assertIn(b'Robust outside plateau (3)',rendered['figures/orb-ustec-qualification.svg'])

    def test_contradictory_projections_fail_before_rendering(self):
        # Removing any binding guard admits a scientifically contradictory figure.
        from scripts.render_orb import orb_artifacts
        changes = [
            ('u','mean',lambda d:d['cells'][0].__setitem__(6,.234)),
            ('u','count domain',lambda d:d['cells'][0].__setitem__(4,True)),
            ('u','fractional count',lambda d:d['cells'][0].__setitem__(4,1.5)),
            ('u','cell identity',lambda d:d['cells'][0].__setitem__(0,'NY_0000_OR5_SHORT_WRONG')),
            ('u','duplicate columns',lambda d:d['columns'].__setitem__(7,'mean_r')),
            ('u','positive census',lambda d:d['census'].update(positive_r_cells=139)),
            ('u','robust census',lambda d:d['census'].update(robust_cells=21)),
            ('u','robust hierarchy',lambda d:d['cells'][0].__setitem__(8,True)),
            ('u','region hierarchy',lambda d:d['cells'][0].__setitem__(9,True)),
            ('u','medoid identity',lambda d:d['cells'][0].__setitem__(10,True)),
            ('u','control delta',lambda d:d['placebo_comparisons'][0].update(delta_mean_r=.2)),
            ('u','control reference',lambda d:d['placebo_comparisons'][0].update(actual_mean_r=.2,delta_mean_r=.2-d['placebo_comparisons'][0]['control_mean_r'])),
            ('u','duplicate control',lambda d:d['placebo_comparisons'].__setitem__(1,copy.deepcopy(d['placebo_comparisons'][0]))),
            ('u','missing control',lambda d:d['placebo_comparisons'].pop()),
            ('u','concentration total',lambda d:d['concentration']['maximum'].update(total_r=99)),
            ('u','concentration removal',lambda d:d['concentration']['maximum'].update(total_r_excluding_largest_absolute_r_trade=99)),
            ('u','contribution fraction',lambda d:d['concentration']['maximum'].update(top_5_trade_contribution_fraction=99)),
            ('u','OOS sample',lambda d:d['oos'][0].update(signal_sessions='2024 historical')),
            ('u','OOS month outside sample',lambda d:d['oos'][0]['exit_month_cumulative_r'][0].__setitem__(0,'2024-12')),
            ('u','missing field',lambda d:d.pop('concentration')),
            ('u','surface sample',lambda d:d['sample'].update(timezone='UTC')),
            ('u','annual mean',lambda d:d['medoid_years'][1].update(mean_r=.9)),
            ('u','annual leave out',lambda d:d['concentration']['medoid']['leave_one_full_year_out_total_r'].update({'2021':99})),
            ('u','duplicate annual',lambda d:d['medoid_years'].__setitem__(1,copy.deepcopy(d['medoid_years'][0]))),
            ('g','mean',lambda d:d['cells'][0].__setitem__(7,.234)),
            ('g','empty mean',lambda d:next(r for r in d['cells'] if r[4]=='VALID_COMPLETE' and r[5]==0).__setitem__(7,0)),
            ('g','invalid scored total',lambda d:next(r for r in d['cells'] if r[4]=='SCIENTIFIC_INVALID').__setitem__(6,0)),
            ('g','census',lambda d:d['census'].update(valid_zero_trades=29)),
            ('g','stress mean',lambda d:d['stress'][0].update(mean_r=.3)),
            ('g','stress duplicate',lambda d:d['stress'].__setitem__(1,copy.deepcopy(d['stress'][0]))),
            ('g','stress missing',lambda d:d['stress'].pop()),
            ('g','stress identity',lambda d:d['stress'][0].update(cell_id='UTC_1330_OR45_LONG')),
            ('g','stress sample',lambda d:d['stress_dates']['DISCOVERY'].update(eligible_start='2018-01-01')),
            ('g','stress cost identity',lambda d:d['stress'][1].update(additional_cost_r=.5)),
            ('g','monetary sum',lambda d:d['monetary']['rows'][0].update(gross_pnl=999)),
            ('g','monetary duplicate',lambda d:d['monetary']['rows'].__setitem__(1,copy.deepcopy(d['monetary']['rows'][0]))),
            ('g','monetary count',lambda d:d['monetary'].update(reconciled_trades=1375)),
            ('g','synthetic exits',lambda d:d['monetary']['rows'][0].update(synthetic_exits=1)),
            ('g','boolean feasibility',lambda d:d['monetary'].update(feasible=False)),
            ('g','terminal classification',lambda d:d['terminal']['candidates'][1].update(pf_money=2)),
            ('g','monetary scope',lambda d:d['monetary']['rows'][0].update(commission=-1,net_pnl=d['monetary']['rows'][0]['net_pnl']-1)),
        ]
        for kind,label,mutate in changes:
            u,g=copy.deepcopy(self.u),copy.deepcopy(self.g)
            mutate(u if kind=='u' else g)
            with self.subTest(label=label):
                with patch('scripts.render_orb._summary',side_effect=AssertionError('rendering reached')):
                    with self.assertRaises(ValueError):orb_artifacts(u,g)

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

    def test_coherent_sources_move_geometry_and_update_annotations(self):
        from scripts import render_orb as renderer
        # Real figures are captured after saving, retaining their plotted objects.
        def capture_call(u,g):
            figures=[];finish=renderer._finish
            def capture(fig,*args,**kwargs):
                result=finish(fig,*args,**kwargs);figures.append(fig);return result
            with patch.object(renderer,'_finish',side_effect=capture):outputs=renderer.orb_artifacts(u,g)
            return outputs,figures
        before,old=capture_call(self.u,self.g)
        u,g=copy.deepcopy(self.u),copy.deepcopy(self.g)
        u['cells'][0][5]-=1;u['cells'][0][6]=u['cells'][0][5]/u['cells'][0][4]
        maximum=u['concentration']['maximum'];maximum['total_r']+=1
        maximum['total_r_excluding_largest_absolute_r_trade']+=1
        maximum['total_r_excluding_5_largest_absolute_r_trades']+=1
        for year in maximum['leave_one_full_year_out_total_r']:
            maximum['leave_one_full_year_out_total_r'][year]+=1
        for stem in ['top_1_trade','top_5_trade','top_1_percent_positive','bottom_1_percent_negative']:
            maximum[stem+'_contribution_fraction']=maximum[stem+'_contribution_r']/maximum['total_r']
        cell=next(r for r in u['cells'] if r[0]==maximum['cell_id'])
        cell[5]=maximum['total_r'];cell[6]=cell[5]/cell[4]
        control=u['placebo_comparisons'][0];control['control_mean_r']-=.001
        control['delta_mean_r']=control['actual_mean_r']-control['control_mean_r']
        u['oos'][0]['total_r']=25;u['oos'][0]['exit_month_cumulative_r'][-1][1]=25
        g['cells'][0][6]-=1;g['cells'][0][7]=g['cells'][0][6]/g['cells'][0][5]
        # Shift a whole candidate's Discovery stress family and its public S0 reference.
        cell=next(r for r in g['cells'] if r[0]=='UTC_1315_OR60_LONG')
        cell[6]+=.01;cell[7]=cell[6]/cell[5]
        for row in g['stress']:
            if row['candidate']=='A' and row['period']=='DISCOVERY':
                row['total_r']+=.01;row['mean_r']=row['total_r']/row['trades']
        money=g['monetary']['rows'][0];money['gross_pnl']+=10;money['net_pnl']+=10
        after,new=capture_call(u,g)
        self.assertNotEqual(old[1].axes[0].collections[0].get_array()[0,0],new[1].axes[0].collections[0].get_array()[0,0])
        self.assertNotEqual(old[4].axes[0].collections[0].get_offsets()[0,0],new[4].axes[0].collections[0].get_offsets()[0,0])
        self.assertEqual(new[3].axes[0].patches[0].get_height(),121.36775815081688)
        self.assertIn(b'+121.37R',after['figures/orb-ustec-selection.svg'])
        self.assertEqual(new[5].axes[0].lines[0].get_ydata()[-1],25)
        self.assertIn(b'+25.000R',after['figures/orb-ustec-validation.svg'])
        self.assertNotEqual(old[6].axes[0].collections[0].get_array()[0,0],new[6].axes[0].collections[0].get_array()[0,0])
        self.assertNotEqual(old[7].axes[0].lines[0].get_ydata()[0],new[7].axes[0].lines[0].get_ydata()[0])
        self.assertEqual(new[8].axes[0].patches[0].get_height(),1600.72)
        self.assertNotEqual(before['figures/orb-gold-economics.svg'],after['figures/orb-gold-economics.svg'])

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
