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
POLICY_ARMS = {
    'CELL_A': ('PENDING_GTC_BLOCK', 'BE_COMPLETED_H4_POST_ENTRY'),
    'CELL_B': ('PENDING_REPLACE_ON_NEW_SIGNAL', 'BE_COMPLETED_H4_POST_ENTRY'),
    'CELL_C': ('PENDING_GTC_BLOCK', 'BE_INTRABAR_H4_EXTREME_POST_ENTRY'),
    'CELL_D': ('PENDING_REPLACE_ON_NEW_SIGNAL', 'BE_INTRABAR_H4_EXTREME_POST_ENTRY'),
}


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
    lo, hi = data['small_candle']['interval_95']
    estimate = data['small_candle']['estimate_price_r']
    if not all(math.isfinite(x) for x in (lo, hi, estimate)) or not lo <= estimate <= hi:
        raise ValueError('Registered aggregate interval must bracket its estimate')


def _style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#b5c2c9')
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, lw=.8)


def _finish(fig, title, subtitle, note, *, layout):
    fig.text(.065, .962, title, ha='left', va='top', color=INK, fontsize=18, fontweight='bold')
    fig.text(.065, .905, subtitle, ha='left', va='top', color=MUTED, fontsize=10.5)
    fig.text(.065, .045, note, ha='left', va='bottom', color=MUTED, fontsize=9, linespacing=1.5)
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
        detail.plot(v, y, 'o', ms=6, color=c)
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
        summary.plot(value, y, 'o', color=SYMBOL_COLORS[row['symbol']], ms=7)
        summary.text(value, y+.16, f"{row['symbol']}  {value:+.3f}R", ha='center', color=INK, fontsize=10)
        summary.text(-.59, y-.20, f"{row['negative_years']}/4 negative years · point estimate", color=MUTED, fontsize=8.7)
    estimate = s['estimate_price_r']
    lo, hi = s['interval_95']
    summary.errorbar(estimate, -.05, xerr=[[estimate-lo], [hi-estimate]], fmt='D',
                     color=INK, capsize=5, markersize=7, lw=2)
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
    title = '03  |  Smaller candles were associated with worse original outcomes'
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
    categories = {'M15': (RUST, 'v'), 'H4': (BLUE, 'D'), 'other': ('#8796a1', 'o')}
    for row in cells:
        group = row['timeframe'] if row['timeframe'] in ('M15', 'H4') else 'other'
        color, marker = categories[group]
        mark = support.scatter(row['closed_trades'], row['mean_price_r'],
                               s=33 if group == 'other' else 48, c=color, marker=marker,
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
    handles = [Line2D([], [], color=c, marker=m, ls='', markersize=6, label=f'{label} · {n} cells')
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
    fig, ax = plt.subplots(figsize=(13.4, 6.5), facecolor='white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    positions = [.025, .365, .705]
    width, height = .27, .23
    for y, color, heading, boxes in [
        (.62, BLUE, 'GTC · a persistent pending order occupies the slot',
         ['Signal A arrives\nPlace pending A\nSlot: A',
          'Signal B arrives\nSKIPPED_PENDING_ORDER\nSlot: still A',
          'Signal C arrives\nSKIPPED_PENDING_ORDER\nSlot: still A']),
        (.13, GOLD, 'Cancel / replace · later eligible signals change the opportunity',
         ['Signal A arrives\nPlace pending A\nSlot: A',
          'Signal B arrives\nCancel A → place B\nSlot: B',
          'Signal C arrives\nCancel B → place C\nSlot: C']),
    ]:
        ax.text(.025, y+height+.065, heading, color=INK, fontsize=12, fontweight='bold', va='bottom')
        for i, (x, label) in enumerate(zip(positions, boxes)):
            patch = FancyBboxPatch((x, y), width, height, boxstyle='round,pad=0.012,rounding_size=0.015',
                                   facecolor=color, edgecolor=color, alpha=.12, linewidth=1.2)
            ax.add_patch(patch)
            ax.text(x+width/2, y+height/2, label, ha='center', va='center', color=INK,
                    fontsize=10.5 if 'SKIPPED' in label else 11, linespacing=1.65)
            if i < 2:
                ax.annotate('', xy=(positions[i+1]-.018, y+height/2),
                            xytext=(x+width+.018, y+height/2),
                            arrowprops={'arrowstyle': '->', 'color': color, 'lw': 1.8})
    title = '05  |  A pending order can occupy the entry slot'
    subtitle = 'CONCEPTUAL_SCHEMATIC · Fictional order-state example · source-defined EBP-PY-H002 policies'
    note = ('The invented A/B/C signal sequence assumes orders remain unfilled and replacement is eligible. It contains no prices, returns or historical timestamps.\n'
            'A live position without BE_APPLIED blocks replacement; both pending policies have no time expiry. Source B21 defines these contracts.\n'
            'No historical price path or contemporaneous counterfactual sequence is shown. H002 arms were separate engine contracts; all four were PARKED.')
    result = _finish(fig, title, subtitle, note,
                     layout=dict(left=.065, right=.965, top=.79, bottom=.25))
    # Bind the conceptual explanation to the complete reviewed policy text as well.
    contract_description = ' '.join(contracts[k] for k in ('PENDING_GTC_BLOCK', 'PENDING_REPLACE_ON_NEW_SIGNAL'))
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
