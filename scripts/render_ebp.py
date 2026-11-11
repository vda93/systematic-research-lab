"""Render reviewed EBP aggregate SVGs and an explicit conceptual policy schematic.

Run from the public checkout: python scripts/render_ebp.py [--check].
The public input is data/ebp-public.json; original evidence remains private.
"""
from __future__ import annotations

import argparse
from html import escape
from io import BytesIO
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, GRID = '#213442', '#657684', '#e6ebef'
BLUE, GOLD, RUST = '#2c6385', '#d09a46', '#a96235'
SYMBOL_COLORS = {'JP225X': BLUE, 'USDCAD2': RUST, 'DE30X': '#71816b'}
# Explicit axis vertices avoid libm rotation roundoff and signed-zero SVG IDs.
DIAMOND = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 1)]
POLICY_ARMS = {
    'CELL_A': ('PENDING_GTC_BLOCK', 'BE_COMPLETED_H4_POST_ENTRY'),
    'CELL_B': ('PENDING_REPLACE_ON_NEW_SIGNAL', 'BE_COMPLETED_H4_POST_ENTRY'),
    'CELL_C': ('PENDING_GTC_BLOCK', 'BE_INTRABAR_H4_EXTREME_POST_ENTRY'),
    'CELL_D': ('PENDING_REPLACE_ON_NEW_SIGNAL', 'BE_INTRABAR_H4_EXTREME_POST_ENTRY'),
}
STAT001_INTERVAL_95 = (-0.330415012574377, -0.21279312685784468)
STAT001_SCOPE = {
    'source_id': 'B23_STAT001',
    'role': 'Retrospective observational diagnosis on spent Discovery, 2020–2023',
    'window_start_inclusive': '2020-01-30T00:00:00Z',
    'window_end_exclusive': '2024-01-01T00:00:00Z',
    'timeframe': 'M15',
    'placed_opportunities': 28097,
    'fills': 21917,
    'bootstrap_replicates': 20000,
    'units': 'Difference in original price R per filled trade; smaller minus larger relative-range quartile.',
    'contrast': 'Rank all placed opportunities within each symbol-year by engulf range / causal ATR. Contrast filled Q1 mean original r_result minus filled Q4 mean; average the 12 strata equally.',
    'interval_method': 'Post-selection exploratory; not selection-adjusted. 20,000 stratified signal-calendar-month block-bootstrap valid replicates; percentile 2.5/97.5; seed 20261011; frozen quartiles retained.',
}
STAT001_MEMBERS = {
    'STAT001_ANALYSIS_PLAN.json': 'b32b511634501cf07692d32597dfdea7775f6e6429e04da1a740e68eed650313',
    'STAT001_RESULTS_MANIFEST.json': 'c6c1dbaafaa91fa1aa2007f44ad327ceb1f1d68e594368ca6cfa7fd93cae7f1a',
    'BOOTSTRAP_SUMMARY.json': '5d331e047899e685991fc38145b06d0c69f67a9ccab1f7e78c4e9a2b4f542d37',
    'PRIMARY_12_STRATA.csv': '86e513424402db479928e28d5ff9edce357fb726a84390bfa4260d22546a173f',
    'SYMBOL_LEVEL_EFFECTS.csv': 'eb2d52bf7f8626e0e29d746ffd1550b498249778068ac19b94bd3139acb86b30',
    'STAT001_VERDICT_REPORT.md': 'd98f0bd68f97ada8392eaf0705b22b5b1089baf3fa8aa27d13da8a32edaf078d',
    'EBP_H001_Q3_Phase2_Frozen_Analysis_Contract_20261011.md': 'bfbc8bfcb73f959242aa9aa35eea8cf067b2b310d70f4d9d6ac6fca5c2154178',
}


def _finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _validate_small_candle(data):
    """Validate STAT001's disclosed arithmetic and frozen statistical contract.

    Bounds remain the archived percentiles. A percentile interval need not
    contain a point estimate; neither validation nor rendering invents bounds.
    """
    try:
        s = data['small_candle']
        if any(type(s[k]) is not int for k in ('placed_opportunities', 'fills', 'bootstrap_replicates')):
            raise ValueError('STAT001 scope populations and bootstrap replicates require integer counts')
        if any(s[k] != value for k, value in STAT001_SCOPE.items()):
            raise ValueError('STAT001 small-candle frozen scope or interval method changed')
        source = data['sources']['B23_STAT001']
        archive = source['archive']
        if (source['experiment_id'] != 'EBP-M15-REV-H001-Q3-STAT001' or
            source['run_identity'] != 'EBP_M15_REV_H001_Q3_STAT001_20261011_213401' or
            archive['basename'] != 'EBP_M15_REV_H001_Q3_STAT001_20261011_213401_REVIEW.zip' or
            archive['sha256'] != '1e52bf69309b678ca49f8df88ea8d78394cb2a0f947f28dd7df550669c8534c3'):
            raise ValueError('STAT001 source identity conflicts with the frozen archive')
        members = source['members']
        if len(members) != len(STAT001_MEMBERS) or {r['member']: r['sha256'] for r in members} != STAT001_MEMBERS:
            raise ValueError('STAT001 source member identities are incomplete or inconsistent')
        rows = s['strata']
        expected = {(symbol, year) for symbol in SYMBOL_COLORS for year in range(2020, 2024)}
        keys = [(r['symbol'], r['signal_year']) for r in rows]
        if len(rows) != 12 or len(set(keys)) != 12 or set(keys) != expected:
            raise ValueError('STAT001 requires twelve unique, complete symbol-year strata')
        for row in rows:
            if (type(row['signal_year']) is not int or
                any(type(row[k]) is not int or row[k] <= 0 for k in ('q1_filled', 'q4_filled')) or
                any(not _finite_number(row[k]) for k in ('q1_mean_price_r', 'q4_mean_price_r', 'delta_q1_minus_q4_price_r'))):
                raise ValueError('STAT001 stratum requires finite outcomes and positive integer fill counts')
            if not math.isclose(row['delta_q1_minus_q4_price_r'], row['q1_mean_price_r']-row['q4_mean_price_r'], rel_tol=1e-12, abs_tol=2e-12):
                raise ValueError('STAT001 stratum contrast conflicts with its Q1 and Q4 component means')
        if sum(r['q1_filled']+r['q4_filled'] for r in rows) > s['fills']:
            raise ValueError('STAT001 stratum quartile counts exceed the frozen fill population')
        effects = s['symbol_effects']
        symbols = [r['symbol'] for r in effects]
        if len(effects) != 3 or len(set(symbols)) != 3 or set(symbols) != set(SYMBOL_COLORS):
            raise ValueError('STAT001 symbol summaries must be unique and complete')
        for effect in effects:
            subset = [r for r in rows if r['symbol'] == effect['symbol']]
            calculated = math.fsum(r['delta_q1_minus_q4_price_r'] for r in subset)/4
            negatives = sum(r['delta_q1_minus_q4_price_r'] < 0 for r in subset)
            if (type(effect['years']) is not int or effect['years'] != 4 or
                type(effect['negative_years']) is not int or effect['negative_years'] != negatives or
                effect['interval'] is not None or not _finite_number(effect['equal_year_delta_price_r']) or
                not math.isclose(effect['equal_year_delta_price_r'], calculated, rel_tol=1e-12, abs_tol=2e-12)):
                raise ValueError('STAT001 symbol summary conflicts with its four annual strata')
        estimate = s['estimate_price_r']
        calculated = math.fsum(r['delta_q1_minus_q4_price_r'] for r in rows)/12
        if not _finite_number(estimate) or not math.isclose(estimate, calculated, rel_tol=1e-12, abs_tol=2e-12):
            raise ValueError('STAT001 aggregate mean conflicts with the twelve equal-weight strata')
        bounds = s['interval_95']
        if len(bounds) != 2 or not all(_finite_number(x) for x in bounds) or tuple(bounds) != STAT001_INTERVAL_95:
            raise ValueError('STAT001 interval must retain the original archived 95% percentile bounds')
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError('STAT001 small-candle source or statistical fields are missing or malformed') from exc


def _policy_arms(data):
    """Bind the frozen contracts by unique identity, independently of input order."""
    rows = data['policy_matrix']['arms']
    identities = [r['cell_id'] for r in rows]
    if len(rows) != 4 or len(set(identities)) != 4 or set(identities) != set(POLICY_ARMS):
        raise ValueError('Policy arms require unique, complete CELL_A through CELL_D identities')
    keyed = {r['cell_id']: r for r in rows}
    arms = [keyed[k] for k in POLICY_ARMS]
    for row in arms:
        if (row['pending_policy'], row['be_mode']) != POLICY_ARMS[row['cell_id']]:
            raise ValueError('Policy arm contract conflicts with its frozen CELL identity')
        if type(row['closed_trades']) is not int or row['closed_trades'] <= 0:
            raise ValueError('Policy arm requires positive integer closed-trade count')
        if not math.isclose(row['mean_price_r'], row['total_price_r']/row['closed_trades'], rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError('Policy arm mean/total/count are inconsistent')
    if len({r['signals'] for r in arms}) != 1:
        raise ValueError('Policy arms must share the frozen signal stream count')
    return arms


def _native_summaries(matrix):
    summaries = []
    for tf in matrix['timeframes']:
        rows = [r for r in matrix['cells'] if r['timeframe'] == tf]
        count = sum(r['closed_trades'] for r in rows)
        total = math.fsum(r['total_price_r'] for r in rows)
        summaries.append({'timeframe': tf, 'cells': len(rows), 'closed_trades': count,
                          'positive_cells': sum(r['total_price_r'] > 0 for r in rows),
                          'total_price_r': total, 'pooled_mean_price_r': total/count})
    return summaries


def _validate(data):
    m = data['native_matrix']
    cells = m['cells']
    pairs = {(r['symbol'], r['timeframe']) for r in cells}
    expected = {(s, t) for s in m['symbols'] for t in m['timeframes']}
    if len(cells) != 88 or len(pairs) != 88 or pairs != expected:
        raise ValueError('Native matrix must contain exactly 88 complete, unique cells')
    if any(not math.isfinite(r['mean_price_r']) or not math.isfinite(r['total_price_r']) or
           type(r['closed_trades']) is not int or r['closed_trades'] <= 0 for r in cells):
        raise ValueError('Every native cell needs a finite mean and positive count')
    for row in cells:
        if not math.isclose(row['mean_price_r'], row['total_price_r']/row['closed_trades'], rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError('Native mean/total/count are inconsistent')
        if type(row['positive_price_r']) is not bool or row['positive_price_r'] != (row['total_price_r'] > 0):
            raise ValueError('Native positive flag is inconsistent with total price R')
    if any(r['native_clock_status'] != 'PASS_NATIVE_TF' for r in cells):
        raise ValueError('Native-clock qualification is required for every cell')
    supplied = m['timeframe_summary']
    keys = [r['timeframe'] for r in supplied]
    if len(keys) != len(set(keys)) or set(keys) != set(m['timeframes']):
        raise ValueError('Native summary identities must be unique and complete')
    by_tf = {r['timeframe']: r for r in supplied}
    for calculated in _native_summaries(m):
        reported = by_tf[calculated['timeframe']]
        if any(reported.get(k) != calculated[k] for k in ('cells', 'closed_trades', 'positive_cells')):
            raise ValueError('Native timeframe summary counts are inconsistent with cells')
        if any(not math.isclose(reported[k], calculated[k], rel_tol=1e-12, abs_tol=1e-12)
               for k in ('total_price_r', 'pooled_mean_price_r')):
            raise ValueError('Native timeframe summary total/mean are inconsistent with cells')
    _policy_arms(data)
    _validate_small_candle(data)


def _style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#b5c2c9')
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, lw=.8)


def _finish(fig, title, subtitle, note, *, layout, title_size=18, subtitle_size=10.5, note_size=9):
    fig.text(.065, .962, title, ha='left', va='top', color=INK, fontsize=title_size, fontweight='bold')
    fig.text(.065, .905, subtitle, ha='left', va='top', color=MUTED, fontsize=subtitle_size)
    fig.text(.065, .045, note, ha='left', va='bottom', color=MUTED, fontsize=note_size, linespacing=1.5)
    fig.subplots_adjust(**layout)
    buf = BytesIO()
    description = subtitle + ' ' + note.replace('\n', ' ')
    fig.savefig(buf, format='svg', metadata={'Date': None, 'Title': title,
                                           'Description': description, 'Creator': 'Systematic Research Lab'})
    plt.close(fig)
    svg = buf.getvalue().decode('utf-8')
    start = svg.index('<svg')
    svg = svg[:start] + svg[start:].replace('<svg ', '<svg role="img" aria-labelledby="figure-title figure-desc" ', 1)
    end = svg.index('>', start) + 1
    svg = svg[:end] + ('\n <title id="figure-title">' + escape(title) + '</title>\n'
                      ' <desc id="figure-desc">' + escape(description) + '</desc>') + svg[end:]
    return ('\n'.join(line.rstrip() for line in svg.splitlines()) + '\n').encode('utf-8')


def _native(data):
    m = data['native_matrix']
    summaries = _native_summaries(m)
    lookup = {(r['symbol'], r['timeframe']): r for r in m['cells']}
    heat = np.array([[lookup[s, t]['mean_price_r'] for t in m['timeframes']] for s in m['symbols']])
    fig, ax = plt.subplots(figsize=(13.4, 8.5), facecolor='white')
    cmap = LinearSegmentedColormap.from_list('ebp-signed', [RUST, '#fafbfc', BLUE])
    im = ax.pcolormesh(np.arange(9), np.arange(12), heat, cmap=cmap,
                       vmin=-.45, vmax=.45, edgecolors='white', linewidth=.9, rasterized=False)
    ax.set_ylim(11, 0)
    ax.set_xlim(0, 8)
    ax.set_xticks(np.arange(8)+.5, m['timeframes'])
    ax.set_yticks(np.arange(11)+.5, m['symbols'])
    ax.tick_params(length=0, colors=INK, labelsize=11, pad=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i, s in enumerate(m['symbols']):
        for j, t in enumerate(m['timeframes']):
            value = lookup[s, t]['mean_price_r']
            ax.text(j+.5, i+.5, f'{value:+.3f}', ha='center', va='center',
                    color='white' if value < -.30 else INK, fontsize=10.5,
                    fontweight='bold' if value > 0 else 'normal')
    for j, row in enumerate(summaries):
        ax.text(j+.5, 1.025, f"{row['positive_cells']}/{row['cells']}", transform=ax.get_xaxis_transform(),
                ha='center', color=BLUE if row['positive_cells'] else RUST, fontsize=10, fontweight='bold')
    ax.text(-.02, 1.025, 'Positive cells', transform=ax.transAxes, ha='right', fontsize=9.5, color=MUTED)
    cbar = fig.colorbar(im, ax=ax, fraction=.035, pad=.035, ticks=[-.45, -.30, -.15, 0, .15, .30, .45])
    cbar.solids.set_rasterized(False)
    cbar.ax.tick_params(labelsize=9, colors=MUTED)
    cbar.set_label('Mean price R / closed trade', color=INK, fontsize=10, labelpad=10)
    positive = sum(r['positive_price_r'] for r in m['cells'])
    trades = sum(r['closed_trades'] for r in m['cells'])
    clocks = {r['timeframe']: r for r in summaries}
    m15, h4 = clocks['M15'], clocks['H4']
    title = '01  |  The repaired clock exposes a mostly negative surface'
    subtitle = (f"TF001R2 · {len(m['symbols'])} instruments × {len(m['timeframes'])} native timeframes · "
                f"2020–2023 Discovery · {positive} of {len(m['cells'])} cells positive")
    note = (f'Each number is a cell mean from its original archived telemetry; all {trades:,} closed trades are retained. Color scale is symmetric, ±0.45R.\n'
            f"M15: {m15['positive_cells']}/{m15['cells']} positive. H4: {h4['positive_cells']}/{h4['cells']} positive, but pooled mean only {h4['pooled_mean_price_r']:+.5f} price R/trade. Overlapping jobs are not a portfolio.\n"
            'Price R does not establish net account economics; 74 invalid-risk denominators recorded zero R. No new OOS or best-cell promotion. Source B22.')
    return _finish(fig, title, subtitle, note,
                   layout=dict(left=.15, right=.93, top=.79, bottom=.20))


def _policy(data):
    arms = _policy_arms(data)
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 6.1), facecolor='white',
                             gridspec_kw={'width_ratios': [1.1, 1]})
    labels = [f"{r['cell_id'][-1]} · " + ('GTC' if r['pending_policy'] == 'PENDING_GTC_BLOCK' else 'Replace') +
              ' / ' + ('completed H4' if r['be_mode'] == 'BE_COMPLETED_H4_POST_ENTRY' else 'intrabar') for r in arms]
    ys = np.arange(4)
    colors = [BLUE, GOLD, BLUE, GOLD]
    count_ax, r_ax = axes
    count_ax.barh(ys, [r['closed_trades'] for r in arms], color=colors, height=.48)
    count_ax.set_yticks(ys, labels)
    count_ax.set_xlim(0, 1490)
    count_ax.set_xticks([0, 500, 1000, 1400])
    count_ax.set_xlabel('Closed trades', color=INK, fontsize=11)
    count_ax.set_title(f"The same {arms[0]['signals']:,} signals reach very different exposure", loc='left', fontsize=11, color=INK, pad=16)
    for y, row in zip(ys, arms):
        count_ax.plot(row['closed_trades'], y, 'o', ms=4.5, color=colors[y], clip_on=False)
        count_ax.text(row['closed_trades']+26, y, f"{row['closed_trades']:,}", va='center', fontsize=11, color=INK)
    values = [r['total_price_r'] for r in arms]
    r_ax.barh(ys, values, color=colors, height=.48)
    r_ax.set_yticks(ys, [])
    r_ax.set_xlim(-150, 48)
    r_ax.set_xticks([-150, -100, -50, 0])
    r_ax.set_xlabel('Total price R', color=INK, fontsize=11)
    gtc_counts = ' / '.join(f"{r['closed_trades']:,}" for r in arms if r['pending_policy'] == 'PENDING_GTC_BLOCK')
    r_ax.set_title(f'GTC arms: {gtc_counts} closed trades', loc='left', fontsize=11, color=INK, pad=16)
    r_ax.axvline(0, color=MUTED, lw=1)
    for y, value in zip(ys, values):
        r_ax.plot(value, y, 'o', ms=4.5, color=colors[y])
        r_ax.text(value-3 if value < 0 else value+3, y, f'{value:+.2f}R',
                  va='center', ha='right' if value < 0 else 'left', color=INK, fontsize=10.5)
    for ax in axes:
        _style(ax)
        ax.set_ylim(3.65, -.65)
        ax.axhline(1.5, color=GRID, lw=1)
    title = '02  |  Order lifetime changes the trade population'
    subtitle = 'EBP-PY-H002 · XAUUSD2 H4 · 2020-01-01 to 2026-08-01 exclusive · historical revalidation'
    note = ('GTC keeps one pending order until filled or cancelled; replacement supersedes it only when active-position eligibility permits. Neither has a time expiry.\n'
            'The second ambiguity is post-entry break-even confirmation: completed H4 versus intrabar extreme. Common execution corrections apply to all arms.\n'
            'All four arms PARK; overall AMBIGUITY_SENSITIVE. Executable-side price R is not fully cost-qualified net profit. No winner selected. Source B21.')
    return _finish(fig, title, subtitle, note,
                   layout=dict(left=.21, right=.96, top=.75, bottom=.25, wspace=.28))


def _small(data):
    s = data['small_candle']
    fig, (detail, summary) = plt.subplots(1, 2, figsize=(13.4, 7.1), facecolor='white',
                                         gridspec_kw={'width_ratios': [1.1, 1]})
    ordered = sorted(s['strata'], key=lambda r: (list(SYMBOL_COLORS).index(r['symbol']), r['signal_year']))
    labels = [f"{r['symbol']}  {r['signal_year']}" for r in ordered]
    for y, row in enumerate(ordered):
        v = row['delta_q1_minus_q4_price_r']
        c = SYMBOL_COLORS[row['symbol']]
        detail.hlines(y, min(v, 0), max(v, 0), color=c, lw=1.2, alpha=.5)
        detail.plot(v, y, 'o', ms=6, color=c)[0].set_gid(f"small-stratum-{row['symbol']}-{row['signal_year']}")
        detail.text(v-.014 if v < 0 else v+.014, y, f'{v:+.3f}',
                    ha='right' if v < 0 else 'left', va='center', color=INK, fontsize=9)
    detail.set_yticks(range(12), labels)
    detail.set_ylim(11.8, -.8)
    detail.set_title('Twelve observed symbol-year contrasts', loc='left', fontsize=11, color=INK, pad=15)
    for y in [3.5, 7.5]:
        detail.axhline(y, color=GRID, lw=1)
    means = [r['equal_year_delta_price_r'] for r in s['symbol_effects']]
    ys = [3.0, 2.0, 1.0]
    for y, row, value in zip(ys, s['symbol_effects'], means):
        summary.plot(value, y, 'o', color=SYMBOL_COLORS[row['symbol']], ms=7)[0].set_gid('small-symbol-'+row['symbol'])
        summary.text(value, y+.16, f"{row['symbol']}  {value:+.3f}R", ha='center', color=INK, fontsize=10)
        summary.text(-.59, y-.20, f"{row['negative_years']}/4 negative years · point estimate", color=MUTED, fontsize=8.7)
    estimate = s['estimate_price_r']
    lo, hi = s['interval_95']
    summary.hlines(-.05, lo, hi, color=INK, lw=2).set_gid('small-interval95')
    summary.vlines([lo, hi], -.105, .005, color=INK, lw=1.3)
    summary.plot(estimate, -.05, ls='', marker=DIAMOND, color=INK,
                 markersize=7*math.sqrt(2))[0].set_gid('small-aggregate')
    summary.text(estimate, .25, f'Equal-stratum mean  {estimate:+.3f}R', ha='center', color=INK, fontsize=11, fontweight='bold')
    summary.text(estimate, -.45, f'Post-selection exploratory 95% interval\n[{lo:+.3f}, {hi:+.3f}] · not selection-adjusted',
                 ha='center', va='center', color=INK, fontsize=9.2, linespacing=1.5)
    summary.set_ylim(-.8, 3.65)
    summary.set_yticks([])
    summary.set_title('The aggregate has an interval; symbol means do not', loc='left', fontsize=11, color=INK, pad=15)
    for ax in (detail, summary):
        _style(ax)
        ax.axvline(0, color=MUTED, lw=1, ls='--')
        ax.set_xlim(-.62, .12)
        ax.set_xticks([-.6, -.4, -.2, 0])
        ax.set_xlabel('Smaller − larger relative-range quartile · price R', color=INK, fontsize=10)
    title = '05  |  Smaller candles were associated with worse original outcomes'
    subtitle = 'STAT001 · M15 · 2020–2023 spent Discovery · post-selection exploratory · 28,097 placed / 21,917 fills'
    note = ('Quartiles rank engulf range / causal ATR among all placed orders within symbol-year; outcomes use fills. The primary estimate weights 12 strata equally.\n'
            'Post-selection exploratory interval, not selection-adjusted: 20,000 stratified signal-month block-bootstrap replicates. Symbol intervals unavailable.\n'
            'Observational, price-R evidence; XAU excluded for unresolved history identity. Anti-EBP PARKED; stop intervention and reversal economics unrun. Source B23.')
    return _finish(fig, title, subtitle, note,
                   layout=dict(left=.15, right=.96, top=.79, bottom=.23, wspace=.32))


def _distribution(data):
    cells = data['native_matrix']['cells']
    means = np.asarray([r['mean_price_r'] for r in cells])
    fig, (hist, support) = plt.subplots(1, 2, figsize=(13.4, 6.5), facecolor='white')
    # Fixed .05R bins contain every reviewed mean, including both endpoints.
    bins = np.linspace(-.45, .15, 13)
    if np.any(means < bins[0]) or np.any(means > bins[-1]):
        raise ValueError('Reviewed mean lies outside the disclosed distribution bins')
    counts, _, patches = hist.hist(means, bins=bins, color=BLUE, edgecolor='white', linewidth=1.1)
    if int(counts.sum()) != len(cells):
        raise ValueError('Distribution must retain every native cell')
    for i, (count, patch) in enumerate(zip(counts, patches)):
        patch.set_gid(f'mean-bin-{i:02d}')
        if count:
            hist.text(patch.get_x()+patch.get_width()/2, count+.45, str(int(count)),
                      ha='center', va='bottom', fontsize=10, color=INK)
    hist.set_xlim(-.46, .16)
    hist.set_ylim(0, max(counts)*1.20)
    hist.set_xlabel('Cell mean price R / closed trade', fontsize=10.5, color=INK)
    hist.set_ylabel('Native-timeframe cells', fontsize=10.5, color=INK)
    hist.set_title(f'All {len(cells)} cell means · equal weight per cell', loc='left', fontsize=11, color=INK, pad=17)
    hist.axvline(0, color=MUTED, lw=1, ls='--')
    categories = {'M15': (RUST, 'v'), 'H4': (BLUE, DIAMOND), 'other': ('#8796a1', 'o')}
    for row in cells:
        group = row['timeframe'] if row['timeframe'] in ('M15', 'H4') else 'other'
        color, marker = categories[group]
        mark = support.scatter(row['closed_trades'], row['mean_price_r'],
                               s=33 if group == 'other' else 96 if group == 'H4' else 48, c=color, marker=marker,
                               edgecolors='white', linewidth=.55, alpha=.88, zorder=3)
        mark.set_gid('support-'+row['cell_id'])
    support.set_xlim(0, max(r['closed_trades'] for r in cells)*1.06)
    support.set_ylim(-.48, .18)
    support.set_xticks([0, 3000, 6000, 9000, 12000], ['0', '3,000', '6,000', '9,000', '12,000'])
    support.set_xlabel('Completed trades in each original cell', fontsize=10.5, color=INK)
    support.set_ylabel('Mean price R / closed trade', fontsize=10.5, color=INK)
    support.set_title('One point per cell · trade support stays visible', loc='left', fontsize=11, color=INK, pad=17)
    support.axhline(0, color=MUTED, lw=1, ls='--')
    group_counts = [sum(r['timeframe'] == 'M15' for r in cells), sum(r['timeframe'] == 'H4' for r in cells),
                    sum(r['timeframe'] not in ('M15', 'H4') for r in cells)]
    handles = [Line2D([], [], color=c, marker=m, ls='', markersize=6*math.sqrt(2) if label=='H4' else 6, label=f'{label} · {n} cells')
               for (c, m), label, n in zip(categories.values(), ['M15', 'H4', 'Other'], group_counts)]
    support.legend(handles=handles, loc='lower right', frameon=False, fontsize=9)
    for ax in (hist, support):
        _style(ax)
    hist.grid(axis='x', visible=False)
    hist.grid(axis='y', color=GRID, lw=.8)
    title = '04  |  The full cell distribution keeps trade support visible'
    positives = sum(r['total_price_r'] > 0 for r in cells)
    negatives = sum(r['total_price_r'] < 0 for r in cells)
    zeroes = len(cells) - positives - negatives
    trades = sum(r['closed_trades'] for r in cells)
    subtitle = (f'TF001R2 · same {len(cells)} original cells · 2020–2023 spent Discovery · {positives} positive / {negatives} negative'
                + (f' / {zeroes} zero' if zeroes else ''))
    note = (f'Histogram: fixed 0.05R bins, one observation per native cell. Scatter: all {len(cells)} means paired with their own completed-trade count.\n'
            f'Cells share instruments and dates and are correlated; {len(cells)} cells are not {len(cells)} independent tests. Counts sum to {trades:,} overlapping trade records.\n'
            'Arithmetic price-R means retain original tails and zero-R telemetry. Support is descriptive, not a confidence interval or net-profit qualification. Source B22.')
    return _finish(fig, title, subtitle, note,
                   layout=dict(left=.085, right=.96, top=.77, bottom=.25, wspace=.28))


def _lifecycle(data):
    policy = data['policy_matrix']
    contracts = policy.get('pending_contract', {})
    if not all(contracts.get(k) for k in ('PENDING_GTC_BLOCK', 'PENDING_REPLACE_ON_NEW_SIGNAL')):
        raise ValueError('Lifecycle requires both frozen H002 pending policy contracts')
    fig, ax = plt.subplots(figsize=(6.4, 12.4), facecolor='white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    width, height, x = .86, .105, .07
    policies = [
        (BLUE, 'GTC: keep the pending order', .96, [.86, .72, .58],
         ['A arrives → place pending A\nSlot holds A',
          'B arrives → skip this signal\nSlot still holds A',
          'C arrives → skip this signal\nSlot still holds A']),
        (GOLD, 'Replace: change an eligible order', .455, [.355, .215, .075],
         ['A arrives → place pending A\nSlot holds A',
          'B arrives → cancel A, place B\nSlot now holds B',
          'C arrives → cancel B, place C\nSlot now holds C']),
    ]
    for policy_index, (color, heading, heading_y, centers, boxes) in enumerate(policies):
        ax.text(.07, heading_y, heading, color=INK, fontsize=16, fontweight='bold', va='bottom')
        for i, (center, label) in enumerate(zip(centers, boxes)):
            patch = FancyBboxPatch((x, center-height/2), width, height,
                                   boxstyle='round,pad=0.012,rounding_size=0.015',
                                   facecolor=color, edgecolor=color, alpha=.12, linewidth=1.2)
            ax.add_patch(patch)
            text = ax.text(x+width/2, center, label, ha='center', va='center', color=INK,
                           fontsize=15, linespacing=1.5)
            text.set_gid(f'lifecycle-state-{policy_index}-{i}')
            if i < 2:
                ax.annotate('', xy=(.5, centers[i+1]+height/2+.012),
                            xytext=(.5, center-height/2-.012),
                            arrowprops={'arrowstyle': '->', 'color': color, 'lw': 1.8})
    title = '03  |  Pending orders occupy the slot'
    subtitle = ('CONCEPTUAL_SCHEMATIC · Fictional order-state example\n'
                'Source-defined H002 policies; no historical path')
    note = ('Fictional A/B/C signals; orders stay unfilled.\n'
            'Replacement assumes active-position eligibility.\n'
            'Without applied break-even (BE_APPLIED), a live\n'
            'position blocks replacement. Neither policy expires.\n'
            'No historical price path or contemporaneous\n'
            'counterfactual sequence is shown. Separate H002\n'
            'contracts; all four PARKED. Source B21.')
    result = _finish(fig, title, subtitle, note,
                     layout=dict(left=.065, right=.935, top=.82, bottom=.23),
                     subtitle_size=11.5, note_size=11.5)
    contract_description = ' '.join(contracts[k] for k in ('PENDING_GTC_BLOCK', 'PENDING_REPLACE_ON_NEW_SIGNAL'))
    contract_description += ' Skipped new signals correspond to source state SKIPPED_PENDING_ORDER.'
    return result.replace(b'</desc>', (' Source contract: '+escape(contract_description)+'</desc>').encode('utf-8'), 1)


def render_all(data):
    """Return deterministic vector SVG bytes from disclosed, validated aggregates."""
    _validate(data)
    with plt.rc_context({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                         'svg.hashsalt': 'ebp-public-v002', 'axes.unicode_minus': False}):
        return {'ebp-native-timeframe.svg': _native(data),
                'ebp-order-policy.svg': _policy(data),
                'ebp-small-candle.svg': _small(data),
                'ebp-cell-distribution.svg': _distribution(data),
                'ebp-pending-lifecycle.svg': _lifecycle(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'data/ebp-public.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'figures')
    parser.add_argument('--check', action='store_true', help='Compare generated bytes with retained SVGs without writing')
    args = parser.parse_args()
    rendered = render_all(json.loads(args.input.read_text(encoding='utf-8')))
    if args.check:
        mismatches = [n for n, b in rendered.items() if not (args.output_dir/n).is_file() or (args.output_dir/n).read_bytes() != b]
        if mismatches:
            raise SystemExit('EBP figure mismatch: ' + ', '.join(mismatches))
        print(f'EBP: all {len(rendered)} SVGs match deterministic aggregate/schematic rendering')
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in rendered.items():
            (args.output_dir/name).write_bytes(content)
        print(f'EBP: wrote {len(rendered)} aggregate/schematic figures')


if __name__ == '__main__':
    main()
