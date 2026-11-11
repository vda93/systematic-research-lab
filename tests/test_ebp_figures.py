"""Public aggregate/figure checks; these do not replay a private strategy."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import unittest

ROOT = Path(__file__).resolve().parents[1]


def data():
    return json.loads((ROOT / 'data/ebp-public.json').read_text(encoding='utf-8'))


def renderer():
    source = ROOT / 'scripts/render_ebp.py'
    assert source.is_file(), 'EBP deterministic renderer has not been implemented'
    spec = importlib.util.spec_from_file_location('render_ebp', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synchronize_native_summary(d):
    """Keep synthetic mutation fixtures internally consistent with their cells."""
    m = d['native_matrix']
    for summary in m['timeframe_summary']:
        rows = [r for r in m['cells'] if r['timeframe'] == summary['timeframe']]
        summary['closed_trades'] = sum(r['closed_trades'] for r in rows)
        summary['positive_cells'] = sum(r['total_price_r'] > 0 for r in rows)
        summary['cells'] = len(rows)
        summary['total_price_r'] = math.fsum(r['total_price_r'] for r in rows)
        summary['pooled_mean_price_r'] = summary['total_price_r']/summary['closed_trades']


def synchronize_small_summary(d):
    """Synthetic geometry fixture only; never recompute the archived interval."""
    s = d['small_candle']
    for row in s['strata']:
        row['delta_q1_minus_q4_price_r'] = row['q1_mean_price_r']-row['q4_mean_price_r']
    for summary in s['symbol_effects']:
        rows = [r for r in s['strata'] if r['symbol'] == summary['symbol']]
        summary['equal_year_delta_price_r'] = math.fsum(r['delta_q1_minus_q4_price_r'] for r in rows)/4
        summary['negative_years'] = sum(r['delta_q1_minus_q4_price_r'] < 0 for r in rows)
    s['estimate_price_r'] = math.fsum(r['delta_q1_minus_q4_price_r'] for r in s['strata'])/12


def test_native_matrix_is_actual_complete_native_clock_surface():
    d = data()['native_matrix']
    cells = d['cells']
    assert d['timeframes'] == ['M15', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'H12']
    assert len(cells) == len({(r['symbol'], r['timeframe']) for r in cells}) == 88
    assert {(r['symbol'], r['timeframe']) for r in cells} == {(s, t) for s in d['symbols'] for t in d['timeframes']}
    assert sum(r['closed_trades'] for r in cells) == 152753
    assert sum(r['positive_price_r'] for r in cells) == 25
    assert all(r['native_clock_status'] == 'PASS_NATIVE_TF' for r in cells)
    assert all(math.isclose(r['mean_price_r'], r['total_price_r']/r['closed_trades'], abs_tol=1e-13) for r in cells)
    assert all(not r['positive_price_r'] for r in cells if r['timeframe'] == 'M15')
    # Independently retained closeout values keep symbol/clock orientation auditable.
    usd = next(r for r in cells if (r['symbol'], r['timeframe']) == ('USDJPY2', 'H4'))
    gbp = next(r for r in cells if (r['symbol'], r['timeframe']) == ('GBPUSD2', 'H4'))
    assert (usd['closed_trades'], usd['total_price_r']) == (591, 82.6512)
    assert (gbp['closed_trades'], gbp['total_price_r']) == (688, 5.4172)
    h4 = next(r for r in d['timeframe_summary'] if r['timeframe'] == 'H4')
    assert h4['positive_cells'] == 7
    assert math.isclose(h4['pooled_mean_price_r'], 0.006330873049346267, abs_tol=1e-13)


def test_policy_contracts_keep_exposure_and_interpretations_separate():
    p = data()['policy_matrix']
    arms = p['arms']
    assert [r['cell_id'] for r in arms] == ['CELL_A', 'CELL_B', 'CELL_C', 'CELL_D']
    assert [r['closed_trades'] for r in arms] == [3, 1257, 3, 1297]
    assert [r['accepted_signals'] for r in arms] == [4, 1492, 4, 1541]
    assert all(math.isclose(r['total_price_r'], v, abs_tol=1e-12) for r, v in zip(arms, [0.9765822398206974, -119.41040465275606, 0.9765822398206974, -94.90285507376487]))
    assert all(r['signals'] == 1718 and r['decision'] == 'PARK' for r in arms)
    assert arms[0]['skipped_pending'] == arms[2]['skipped_pending'] == 1714
    assert set(p['pending_contract']) == {'PENDING_GTC_BLOCK', 'PENDING_REPLACE_ON_NEW_SIGNAL'}


def test_small_candle_interval_is_registered_aggregate_only():
    s = data()['small_candle']
    assert (s['placed_opportunities'], s['fills']) == (28097, 21917)
    assert len(s['strata']) == 12
    assert sum(r['delta_q1_minus_q4_price_r'] < 0 for r in s['strata']) == 9
    assert abs(s['estimate_price_r'] + 0.27178390561993154) < 1e-14
    assert abs(s['estimate_price_r'] - sum(r['delta_q1_minus_q4_price_r'] for r in s['strata'])/12) < 1e-12
    assert all(abs(v-w)<1e-14 for v,w in zip(s['interval_95'], [-0.330415012574377, -0.21279312685784468]))
    assert s['bootstrap_replicates'] == 20000
    assert all(r['interval'] is None for r in s['symbol_effects'])
    assert [r['negative_years'] for r in s['symbol_effects']] == [4, 4, 1]


def test_every_native_cell_binds_to_actual_archive_member_bytes():
    d = data()
    source = d['sources']['B22_TF001R2']
    assert source['archive']['sha256'] == '45849b254cb4b7e07fffe719dfa3e718371c4bbc44472b4209365f2c56d9fc9d'
    members = {r['member']: r for r in source['members']}
    for cell in d['native_matrix']['cells']:
        assert cell['source_sha256'] == members[cell['source_member']]['sha256']
    for source in d['sources'].values():
        assert source['archive']['bytes'] > 0
        assert re.fullmatch('[a-f0-9]{64}', source['archive']['sha256'])
        for member in source['members']:
            assert re.fullmatch('[a-f0-9]{64}', member['sha256'])
    raw = (ROOT/'data/ebp-public.json').read_text(encoding='utf-8')
    assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]|drive\.google|docs\.google|order_ticket|entry_price', raw)


def test_renderer_is_deterministic_accessible_and_matches_retained_svgs():
    m = renderer()
    first = m.render_all(data())
    assert set(first) == {'ebp-native-timeframe.svg', 'ebp-order-policy.svg', 'ebp-small-candle.svg',
                          'ebp-cell-distribution.svg', 'ebp-pending-lifecycle.svg'}
    assert first == m.render_all(data())
    for name, content in first.items():
        root = ET.fromstring(content)
        assert root.attrib['role'] == 'img'
        assert root.attrib['aria-labelledby'] == 'figure-title figure-desc'
        assert root.find('{http://www.w3.org/2000/svg}title').text
        assert root.find('{http://www.w3.org/2000/svg}desc').text
        assert root.findall('.//{http://www.w3.org/2000/svg}text')
        assert not root.findall('.//{http://www.w3.org/2000/svg}image')
        assert not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]|drive\.google|docs\.google', content)
        retained=(ROOT/'figures'/name).read_bytes()
        if retained != content:
            from difflib import unified_diff
            diff=unified_diff(retained.decode('utf-8').splitlines(),content.decode('utf-8').splitlines(),n=2)
            excerpt='\n'.join(line[:200] for line in list(diff)[:35])
            raise AssertionError(f'Exact EBP SVG mismatch: {name}\n{excerpt}')


def test_diamond_markers_have_exact_axis_vertices():
    from unittest.mock import patch
    from matplotlib.markers import MarkerStyle
    import numpy as np
    m=renderer();d=data();figures=[];original=m._finish
    def capture(fig,*args,**kwargs):
        result=original(fig,*args,**kwargs);figures.append(fig);return result
    original_cos=math.cos
    def platform_cos(angle):
        value=original_cos(angle)
        return math.nextafter(value,math.inf) if abs(angle-math.pi/4)<1e-14 else value
    # Emulate the libm last-bit difference observed in hosted Linux SVG paths.
    with patch('matplotlib.transforms.math.cos',side_effect=platform_cos), patch.object(m,'_finish',side_effect=capture):
        m._small(d);m._distribution(d)
        summary=figures[0].axes[1]
        line=next(line for line in summary.lines if len(line.get_xdata())==1
                  and line.get_xdata()[0]==d['small_candle']['estimate_price_r']
                  and line.get_ydata()[0]==-.05)
        marker=MarkerStyle(line.get_marker())
        paths=[marker.get_path().transformed(marker.get_transform())]
    h4=next(c for c in d['native_matrix']['cells'] if c['timeframe']=='H4')
    collection=next(c for c in figures[1].axes[1].collections if c.get_gid()=='support-'+h4['cell_id'])
    paths.extend(collection.get_paths())
    for path in paths:
        values=np.abs(path.vertices)
        assert not np.any((values>0)&(values<1e-12)), 'Rotated near-zero vertices vary by platform'


def test_renderer_rejects_an_incomplete_surface_and_invalid_interval():
    m = renderer()
    incomplete = deepcopy(data())
    incomplete['native_matrix']['cells'].pop()
    with unittest.TestCase().assertRaisesRegex(ValueError, '88|complete'):
        m.render_all(incomplete)
    invalid = deepcopy(data())
    invalid['small_candle']['interval_95'].reverse()
    with unittest.TestCase().assertRaisesRegex(ValueError, 'interval'):
        m.render_all(invalid)


def test_case_study_exposes_all_empirical_figures_and_their_limits():
    study = (ROOT/'studies/engulfing-and-support.md').read_text(encoding='utf-8')
    note = (ROOT/'docs/ebp-visual-evidence.md').read_text(encoding='utf-8')
    for name in ['ebp-native-timeframe.svg', 'ebp-order-policy.svg', 'ebp-small-candle.svg',
                 'ebp-cell-distribution.svg', 'ebp-pending-lifecycle.svg']:
        assert f'../figures/{name}' in study
        assert f'[Full-resolution SVG](../figures/{name})' in study
        assert f'../figures/{name}' in note
    assert study.index('ebp-native-timeframe.svg') < study.index('## From engulfing candle')
    assert 'APPROVED AS REPORTED' in note and 'BLOCKED' in note
    assert 'CONCEPTUAL_SCHEMATIC' in note and 'SCHEMATIC ONLY' in note
    assert 'Symbol/year intervals were not supplied and are not drawn' in note
    assert 'H002_ARCHIVE_SHA' not in note
    for content in (study, note):
        assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]|drive\.google|docs\.google', content)


def test_distribution_uses_each_original_mean_and_completed_trade_count():
    m = renderer()
    d = data()
    figure = m.render_all(d)
    assert 'ebp-cell-distribution.svg' in figure, 'Full cell distribution/support figure is missing'
    original = figure['ebp-cell-distribution.svg']
    tree = ET.fromstring(original)
    for cell in d['native_matrix']['cells']:
        point = tree.find(f".//*[@id='support-{cell['cell_id']}']")
        assert point is not None, 'Every original cell needs its own support mark'
    # One source count changes only that point's horizontal coordinate.
    cell = d['native_matrix']['cells'][0]
    point_id = f"support-{cell['cell_id']}"
    before = tree.find(f".//*[@id='{point_id}']//{{http://www.w3.org/2000/svg}}use")
    changed = deepcopy(d)
    changed['native_matrix']['cells'][0]['closed_trades'] += 1000
    row = changed['native_matrix']['cells'][0]
    row['total_price_r'] = row['closed_trades'] * row['mean_price_r']
    synchronize_native_summary(changed)
    after_tree = ET.fromstring(m.render_all(changed)['ebp-cell-distribution.svg'])
    after = after_tree.find(f".//*[@id='{point_id}']//{{http://www.w3.org/2000/svg}}use")
    assert before.attrib['x'] != after.attrib['x']
    assert before.attrib['y'] == after.attrib['y']
    # A mean crossing bins must alter histogram geometry, not just a label.
    changed = deepcopy(d)
    changed['native_matrix']['cells'][0]['mean_price_r'] = .149
    row = changed['native_matrix']['cells'][0]
    row['total_price_r'] = row['closed_trades'] * row['mean_price_r']
    row['positive_price_r'] = True
    synchronize_native_summary(changed)
    after_tree = ET.fromstring(m.render_all(changed)['ebp-cell-distribution.svg'])
    before_bins = [ET.tostring(n) for n in tree.findall(".//*[@id]") if n.attrib['id'].startswith('mean-bin-')]
    after_bins = [ET.tostring(n) for n in after_tree.findall(".//*[@id]") if n.attrib['id'].startswith('mean-bin-')]
    assert len(before_bins) == len(after_bins) == 12
    assert before_bins != after_bins


def test_lifecycle_is_explicitly_fictional_and_requires_both_source_policies():
    m = renderer()
    d = data()
    figures = m.render_all(d)
    assert 'ebp-pending-lifecycle.svg' in figures, 'Pending lifecycle schematic is missing'
    svg = figures['ebp-pending-lifecycle.svg'].decode('utf-8')
    assert 'CONCEPTUAL_SCHEMATIC' in svg
    assert 'Fictional order-state example' in svg
    assert 'No historical price path or contemporaneous counterfactual sequence' in svg
    assert 'BE_APPLIED' in svg and 'SKIPPED_PENDING_ORDER' in svg
    changed = deepcopy(d)
    del changed['policy_matrix']['pending_contract']['PENDING_REPLACE_ON_NEW_SIGNAL']
    with unittest.TestCase().assertRaisesRegex(ValueError, 'policy|contract'):
        m.render_all(changed)


def test_review_policy_identity_is_order_invariant_and_rejects_ambiguity():
    m = renderer()
    d = data()
    changed = deepcopy(d)
    changed['policy_matrix']['arms'].reverse()
    assert m.render_all(d) == m.render_all(changed), 'Reordering source arms must not relabel their plotted values'
    for mutation in ('duplicate', 'missing', 'wrong_contract'):
        changed = deepcopy(d)
        if mutation == 'duplicate':
            changed['policy_matrix']['arms'][3] = deepcopy(changed['policy_matrix']['arms'][0])
        elif mutation == 'missing':
            changed['policy_matrix']['arms'].pop()
        else:
            changed['policy_matrix']['arms'][0]['be_mode'] = 'BE_INTRABAR_H4_EXTREME_POST_ENTRY'
        with unittest.TestCase().assertRaisesRegex(ValueError, 'arm|contract|CELL'):
            m.render_all(changed)


def test_review_native_inconsistent_counts_means_flags_and_summaries_fail_closed():
    m = renderer()
    for mutation in ('count', 'mean', 'flag', 'summary', 'summary_duplicate'):
        changed = deepcopy(data())
        if mutation == 'count':
            changed['native_matrix']['cells'][0]['closed_trades'] += 1
        elif mutation == 'mean':
            changed['native_matrix']['cells'][0]['mean_price_r'] += .01
        elif mutation == 'flag':
            changed['native_matrix']['cells'][0]['positive_price_r'] = True
        elif mutation == 'summary':
            changed['native_matrix']['timeframe_summary'][0]['positive_cells'] += 1
        else:
            changed['native_matrix']['timeframe_summary'][1] = deepcopy(changed['native_matrix']['timeframe_summary'][0])
        with unittest.TestCase().assertRaisesRegex(ValueError, 'inconsistent|summary|total|mean|positive'):
            m.render_all(changed)


def test_review_native_and_distribution_annotations_follow_consistent_source_changes():
    m = renderer()
    changed = deepcopy(data())
    row = changed['native_matrix']['cells'][0]
    row['closed_trades'] += 1000
    row['mean_price_r'] = .149
    row['total_price_r'] = row['closed_trades'] * row['mean_price_r']
    row['positive_price_r'] = True
    h4row = next(r for r in changed['native_matrix']['cells'] if r['symbol'] == 'XAUUSD2' and r['timeframe'] == 'H4')
    h4row['mean_price_r'] = .1
    h4row['total_price_r'] = h4row['closed_trades'] * .1
    h4row['positive_price_r'] = True
    synchronize_native_summary(changed)
    figures = m.render_all(changed)
    native = ' '.join(ET.fromstring(figures['ebp-native-timeframe.svg']).itertext())
    distribution = ' '.join(ET.fromstring(figures['ebp-cell-distribution.svg']).itertext())
    assert '27 of 88 cells positive' in native
    assert '153,753 closed trades' in native
    assert 'M15: 1/11 positive' in native and 'H4: 8/11 positive' in native
    h4 = next(r for r in changed['native_matrix']['timeframe_summary'] if r['timeframe'] == 'H4')
    assert f"{h4['pooled_mean_price_r']:+.5f}" in native
    assert '27 positive / 61 negative' in distribution
    assert '153,753 overlapping trade records' in distribution


def test_review_stat001_interval_is_explicitly_post_selection_exploratory():
    m = renderer()
    d = data()
    s = d['small_candle']
    for text in (s['interval_method'], ' '.join(s['limitations']),
                 (ROOT/'studies/engulfing-and-support.md').read_text(encoding='utf-8'),
                 (ROOT/'docs/ebp-visual-evidence.md').read_text(encoding='utf-8'),
                 m.render_all(d)['ebp-small-candle.svg'].decode('utf-8')):
        assert 'post-selection exploratory' in text.lower()
        assert 'not selection-adjusted' in text.lower()


def test_final_review_small_candle_rejects_contradictory_components_and_summaries():
    m = renderer()
    for mutation in ('stratum_delta', 'symbol_mean', 'negative_years', 'aggregate_mean'):
        changed = deepcopy(data())
        s = changed['small_candle']
        if mutation == 'stratum_delta':
            s['strata'][0]['delta_q1_minus_q4_price_r'] += .02
        elif mutation == 'symbol_mean':
            s['symbol_effects'][0]['equal_year_delta_price_r'] += .02
        elif mutation == 'negative_years':
            s['symbol_effects'][0]['negative_years'] = 1
        else:
            s['estimate_price_r'] += .02
        with unittest.TestCase().assertRaisesRegex(ValueError, 'STAT001|small-candle|strat|symbol|aggregate'):
            m.render_all(changed)


def test_final_review_small_candle_rejects_incomplete_invalid_and_duplicate_rows():
    m = renderer()
    for mutation in ('missing', 'duplicate', 'year', 'symbol', 'nonfinite', 'count', 'summary_missing', 'summary_duplicate'):
        changed = deepcopy(data())
        s = changed['small_candle']
        if mutation == 'missing':
            s['strata'].pop()
        elif mutation == 'duplicate':
            s['strata'][1] = deepcopy(s['strata'][0])
        elif mutation == 'year':
            s['strata'][0]['signal_year'] = 2024
        elif mutation == 'symbol':
            s['strata'][0]['symbol'] = 'XAUUSD2'
        elif mutation == 'nonfinite':
            s['strata'][0]['q1_mean_price_r'] = float('nan')
        elif mutation == 'count':
            s['strata'][0]['q1_filled'] = 0
        elif mutation == 'summary_missing':
            s['symbol_effects'].pop()
        else:
            s['symbol_effects'][1] = deepcopy(s['symbol_effects'][0])
        with unittest.TestCase().assertRaisesRegex(ValueError, 'STAT001|small-candle|strat|symbol'):
            m.render_all(changed)


def test_final_review_small_candle_rejects_changed_identity_scope_or_archived_interval():
    m = renderer()
    for mutation in ('source_id', 'source_hash', 'run', 'missing_source', 'role', 'window', 'units',
                     'method', 'replicates', 'replicate_type', 'bounds', 'missing_field'):
        changed = deepcopy(data())
        s = changed['small_candle']
        if mutation == 'source_id':
            s['source_id'] = 'B22_TF001R2'
        elif mutation == 'source_hash':
            changed['sources']['B23_STAT001']['archive']['sha256'] = '0'*64
        elif mutation == 'run':
            changed['sources']['B23_STAT001']['run_identity'] = 'UNQUALIFIED'
        elif mutation == 'missing_source':
            del changed['sources']['B23_STAT001']
        elif mutation == 'role':
            s['role'] = 'Independent OOS'
        elif mutation == 'window':
            s['window_end_exclusive'] = '2025-01-01T00:00:00Z'
        elif mutation == 'units':
            s['units'] = 'Net account currency'
        elif mutation == 'method':
            s['interval_method'] = 'Selection-adjusted OOS confidence interval'
        elif mutation == 'replicates':
            s['bootstrap_replicates'] = 19999
        elif mutation == 'replicate_type':
            s['bootstrap_replicates'] = 20000.0
        elif mutation == 'bounds':
            s['interval_95'][0] -= .02
        else:
            del s['strata'][0]['q4_mean_price_r']
        with unittest.TestCase().assertRaisesRegex(ValueError, 'STAT001|small-candle|scope|source|interval'):
            m.render_all(changed)


def test_final_review_coherent_small_candle_fixture_moves_points_without_manufacturing_interval():
    from unittest.mock import patch
    m = renderer()
    original = data()
    changed = deepcopy(original)
    for row in changed['small_candle']['strata']:
        row['q1_mean_price_r'] -= .07
    synchronize_small_summary(changed)
    assert changed['small_candle']['interval_95'] == original['small_candle']['interval_95']
    assert changed['small_candle']['estimate_price_r'] < changed['small_candle']['interval_95'][0]
    captured = []
    finish = m._finish
    def capture(fig, title, *args, **kwargs):
        result = finish(fig, title, *args, **kwargs)
        if 'Smaller candles' in title:
            captured.append(fig)
        return result
    with patch.object(m, '_finish', side_effect=capture):
        m.render_all(original)
        try:
            changed_svg = m.render_all(changed)['ebp-small-candle.svg']
        except ValueError as exc:
            raise AssertionError('Coherent component/summary fixture must not require percentile bounds to bracket the point') from exc
    before, after = captured
    for gid, expected in [('small-aggregate', changed['small_candle']['estimate_price_r']),
                          ('small-symbol-DE30X', next(r['equal_year_delta_price_r'] for r in changed['small_candle']['symbol_effects'] if r['symbol']=='DE30X'))]:
        first = next(line for line in before.axes[1].lines if line.get_gid()==gid)
        second = next(line for line in after.axes[1].lines if line.get_gid()==gid)
        assert first.get_xdata()[0] != second.get_xdata()[0]
        assert second.get_xdata()[0] == expected
    first_interval = next(c for c in before.axes[1].collections if c.get_gid()=='small-interval95')
    second_interval = next(c for c in after.axes[1].collections if c.get_gid()=='small-interval95')
    assert first_interval.get_segments()[0].tolist() == second_interval.get_segments()[0].tolist()
    assert f"{changed['small_candle']['estimate_price_r']:+.3f}R" in changed_svg.decode('utf-8')
    assert '4/4 negative years' in changed_svg.decode('utf-8')


def test_final_review_figure_order_and_lifecycle_mobile_reading():
    from unittest.mock import patch
    m = renderer()
    captured = []
    finish = m._finish
    def capture(fig, title, *args, **kwargs):
        result = finish(fig, title, *args, **kwargs)
        captured.append((title, fig))
        return result
    with patch.object(m, '_finish', side_effect=capture):
        figures = m.render_all(data())
    lifecycles = [(title, fig) for title, fig in captured if 'Pending orders' in title]
    assert lifecycles, 'Renumbered stacked lifecycle figure is not implemented'
    lifecycle = lifecycles[0]
    small = next(title for title, fig in captured if 'Smaller candles' in title)
    assert lifecycle[0].startswith('03') and small.startswith('05')
    assert lifecycle[1].get_figheight() > lifecycle[1].get_figwidth()
    states = [t for t in lifecycle[1].axes[0].texts if t.get_gid() and t.get_gid().startswith('lifecycle-state-')]
    assert len(states) == 6 and all(t.get_fontsize() >= 14 for t in states)
    assert all('SKIPPED_PENDING_ORDER' not in t.get_text() for t in states)
    assert all(p.get_path().vertices[:, 1].min() >= 0 for p in lifecycle[1].axes[0].patches), 'State boxes must remain inside the figure axes'
    assert b'BE_APPLIED' in figures['ebp-pending-lifecycle.svg']


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(f) for name, f in sorted(globals().items()) if name.startswith('test_') and callable(f))


if __name__ == '__main__':
    unittest.main()
