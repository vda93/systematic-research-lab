"""Deterministic presentation of the frozen ECB reference-rate study."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from scripts.render_historical import BLUE, GOLD, INK, _finish, _interval

ASSETS = ('EURUSD', 'USDJPY')
ROLES = ('development', 'validation', 'final')


def _validate(result):
    if (result['study_id'] != 'ECB-FX-MOM20-v001'
            or result['evidence_role'] != 'REAL_MARKET_REFERENCE_OBSERVATIONS'
            or result['executable_profitability'] != 'NOT_EVALUATED'
            or result['prospective_fresh_oos'] is not False
            or result['minimum_effect_bps'] != .5):
        raise ValueError('unexpected empirical study contract')
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('nonfinite presentation input')
        if isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)
    finite(result)
    for role in ROLES:
        period = result['roles'][role]
        if period['status'] != 'QUALIFIED' or set(period['assets']) != set(ASSETS):
            raise ValueError('presentation requires qualified paired periods')
        if sum(row['assets']['EURUSD']['sample_size'] for row in period['annual']) != period['sample_size']:
            raise ValueError('annual counts do not reconcile')
        for asset in ASSETS:
            stats = period['assets'][asset]
            if not (0 <= stats['primary_p_value'] <= 1 and 0 <= stats['holm_adjusted_p_value'] <= 1):
                raise ValueError('invalid probability')
            if stats['ci_low_bps'] > stats['ci_high_bps']:
                raise ValueError('reversed confidence interval')
            if abs(stats['mean_signal_bps'] - stats['mean_always_long_bps'] - stats['mean_difference_bps']) > 1e-8:
                raise ValueError('benchmark comparison does not reconcile')
            if sum(stats['sign_counts'].values()) != stats['sample_size'] or stats['sample_size'] != period['sample_size']:
                raise ValueError('paired sample counts do not reconcile')
    final = result['roles']['final']
    expected = 'PASS' if all(a['verdict'] == 'PASS' for a in final['assets'].values()) else 'NOT_PASS'
    if result['family_verdict'] != expected or final['family_verdict'] != expected:
        raise ValueError('family verdict does not reconcile')


def _number(value, digits=4):
    return f'{value:+.{digits}f}' if value else f'{0:.{digits}f}'


def _table(result):
    lines = ['# ECB-FX-MOM20-v001: complete result tables', '',
             'Generated from `data/ecb-fx-results.json`. Units are basis points of signed logarithmic',
             'reference-rate change per observation. Executable profitability: **NOT_EVALUATED**.',
             'Intervals are marginal 95% percentile block-bootstrap intervals; primary block length 20.',
             'Only the two final-period primary tests form the confirmatory Holm family.', '',
             f"Frozen family verdict: **{result['family_verdict']}**. The 0.5-bp minimum is an arbitrary",
             'statistical relevance screen, not validated trading economics.', '',
             '## Temporal roles and unconditional comparators', '',
             '| Role | Asset | N | Signal | Always long | Always short | Flat | Paired difference | Median difference | Primary 95% CI | Raw p | Holm p | Verdict |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |']
    for role in ROLES:
        for asset in ASSETS:
            a = result['roles'][role]['assets'][asset]
            lines.append(f"| {role} | {asset} | {a['sample_size']} | {_number(a['mean_signal_bps'])} | "
                         f"{_number(a['mean_always_long_bps'])} | {_number(a['mean_always_short_bps'])} | 0.0000 | "
                         f"{_number(a['mean_difference_bps'])} | {_number(a['median_difference_bps'])} | "
                         f"[{_number(a['ci_low_bps'])}, {_number(a['ci_high_bps'])}] | "
                         f"{a['primary_p_value']:.4f} | {a['holm_adjusted_p_value']:.4f} | {a['verdict']} |")
    lines += ['', 'Development and validation p-values are descriptive; their displayed within-period',
              'Holm calculations do not create additional confirmatory claims.', '',
              '## Signal counts and target coverage', '',
              '| Role | Target start | Last target end | N | Asset | Short | Flat | Long |',
              '| --- | --- | --- | ---: | --- | ---: | ---: | ---: |']
    for role in ROLES:
        period = result['roles'][role]
        for asset in ASSETS:
            counts = period['assets'][asset]['sign_counts']
            lines.append(f"| {role} | {period['first_target']} | {period['last_target']} | {period['sample_size']} | "
                         f"{asset} | {counts['-1']} | {counts['0']} | {counts['1']} |")
    lines += ['', 'Zero paired differences occur whenever the signal is long: the signal and benchmark',
              'then match exactly. Unchanged targets can create further zeros. A zero median is not',
              'evidence of missing observations.', '', '## All fixed block-length results', '',
              'These are unadjusted one-sided p-values and marginal intervals. Length 20 is primary;',
              '10 and 60 are sensitivities. Every row uses 9,999 shared-index draws and seed 20261021.', '',
              '| Role | Block length | Asset | Mean difference | 95% CI | Raw p |',
              '| --- | ---: | --- | ---: | --- | ---: |']
    for role in ROLES:
        for block in result['roles'][role]['bootstrap']:
            for a in block['assets']:
                lines.append(f"| {role} | {block['block_length']} | {a['asset']} | {_number(a['mean']*10000)} | "
                             f"[{_number(a['ci_low']*10000)}, {_number(a['ci_high']*10000)}] | {a['p_value']:.4f} |")
    lines += ['', '## Annual differences and equal-weight pooled contributions', '',
              'Annual means are descriptive. Contribution equals the annual pooled sum divided by',
              'the full role sample size, so contributions sum to the full pooled mean.', '',
              '| Role | Year | N | EURUSD mean difference | USDJPY mean difference | Pooled contribution to full mean |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for role in ROLES:
        for row in result['roles'][role]['annual']:
            lines.append(f"| {role} | {row['year']} | {row['assets']['EURUSD']['sample_size']} | "
                         f"{_number(row['assets']['EURUSD']['mean_difference_bps'])} | "
                         f"{_number(row['assets']['USDJPY']['mean_difference_bps'])} | "
                         f"{_number(row['pooled_contribution_to_full_mean_bps'])} |")
    lines += ['', '## Concentration diagnostic', '',
              'Removing the strongest positive calendar contribution is an outcome-dependent descriptive',
              'diagnostic, without an inferential p-value. The pool is descriptive, not another primary test.', '',
              '| Role | Full pooled mean | Removed year | Removed contribution | Retained N | Retained pooled mean |',
              '| --- | ---: | --- | ---: | ---: | ---: |']
    for role in ROLES:
        period = result['roles'][role]
        c = period['concentration']
        retained = _number(c['retained_pooled_mean_bps']) if c['retained_pooled_mean_bps'] is not None else 'undefined'
        lines.append(f"| {role} | {_number(period['pooled_mean_difference_bps'])} | {c['removed_year'] or 'none'} | "
                     f"{_number(c['removed_contribution_to_full_mean_bps'])} | {c['retained_sample_size']} | {retained} |")
    lines += ['', '## Extra-observation delay sensitivity', '',
              'The fixed target becomes log(P[t+3]/P[t+2]); the signal remains unchanged. Means only,',
              'without additional confirmatory inference. These rows cannot rescue the primary result.', '',
              '| Role | Asset | N | Signal | Always long | Always short | Paired difference |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for role in ROLES:
        for asset in ASSETS:
            a = result['extra_delay'][role]['assets'][asset]
            lines.append(f"| {role} | {asset} | {a['sample_size']} | {_number(a['mean_signal_bps'])} | "
                         f"{_number(a['mean_always_long_bps'])} | {_number(a['mean_always_short_bps'])} | {_number(a['mean_difference_bps'])} |")
    lines += ['', f"Source selected-CSV SHA256: `{result['source_csv_sha256']}`.", '',
              'The snapshot is a retrieval vintage. Historical publication latency and executable',
              'bid/ask fills are unverified. No cost, carry, financing or net-return estimate is supplied.', '']
    return '\n'.join(lines).encode('utf-8')


def fx_artifacts(result) -> dict[str, bytes]:
    _validate(result)
    artifacts = {'results/fx-tables.md': _table(result)}
    style = {'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
             'svg.hashsalt': 'srl-fx-reference-v1', 'axes.labelsize': 10, 'text.color': INK}
    with plt.rc_context(style):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
        fig.suptitle(f"ECB reference rates | Frozen momentum comparison: {result['family_verdict']}",
                     x=.065, ha='left', fontsize=16, fontweight='bold', color=INK)
        left, right = axes
        left.set_title('Final historical evaluation · 2023–2025', loc='left', fontsize=11, pad=18)
        final = result['roles']['final']
        for j, (asset, color) in enumerate(zip(ASSETS, (BLUE, GOLD))):
            a = final['assets'][asset]
            _interval(left, {'ci_low': a['ci_low_bps'], 'ci_high': a['ci_high_bps'],
                             'estimate': a['mean_difference_bps']}, j, color)
        left.set_yticks([0, 1], [f"{asset} · n={final['sample_size']}" for asset in ASSETS])
        left.set_ylim(1.7, -.7)
        left.axvline(0, color=INK, linewidth=1)
        left.axvline(.5, color='#818b94', linestyle=':', linewidth=1)
        left.set_xlabel('Mean paired difference · bp per observation\nPoints and marginal 95% intervals · 20-observation blocks')
        left.spines[['top', 'right', 'left']].set_visible(False)
        left.spines['bottom'].set_color('#b9c2c9')
        left.tick_params(colors=INK, labelsize=9)
        right.set_title('All temporal roles · mean difference (bp/observation)', loc='left', fontsize=11, pad=18)
        right.axis('off')
        cells = [[role.capitalize(), str(result['roles'][role]['sample_size']),
                  _number(result['roles'][role]['assets']['EURUSD']['mean_difference_bps'], 3),
                  _number(result['roles'][role]['assets']['USDJPY']['mean_difference_bps'], 3)] for role in ROLES]
        table = right.table(cellText=cells, colLabels=['Role', 'N', 'EURUSD', 'USDJPY'],
                            colWidths=[.36, .14, .25, .25], cellLoc='right', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.8)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('#e5e9ed')
            cell.set_text_props(color=INK, weight='bold' if row == 0 else 'normal')
            if col == 0:
                cell.get_text().set_ha('left')
        p_text = ' / '.join(f"{final['assets'][a]['holm_adjusted_p_value']:.4f}" for a in ASSETS)
        right.text(0, -.02, f"Family: {result['family_verdict']}\nFinal Holm p: {p_text} · no sensitivity rescue",
                   transform=right.transAxes, fontsize=10, color=INK)
        fig.subplots_adjust(left=.13, right=.97, bottom=.32, top=.76, wspace=.4)
        note = ('Real market-derived reference observations · not executable prices or net returns.\n'
                'Dotted line: arbitrary 0.5-bp statistical screen. Historical holdouts; shared-index bootstrap assumes weak dependence.')
        artifacts['figures/fx-reference.svg'] = _finish(fig, note, f"ECB reference momentum: frozen comparison {result['family_verdict']}")
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write figures/tables; default verifies existing bytes')
    args = parser.parse_args()
    result = json.loads((ROOT / 'data/ecb-fx-results.json').read_text(encoding='utf-8'))
    artifacts = fx_artifacts(result)
    if args.write:
        for name, payload in artifacts.items():
            (ROOT / name).write_bytes(payload)
    else:
        mismatches = [name for name, payload in artifacts.items()
                      if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != payload]
        if mismatches:
            print(json.dumps({'status': 'FAIL', 'artifact_mismatch': mismatches}))
            return 1
    print(json.dumps({'status': 'PASS', 'artifacts': sorted(artifacts)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
