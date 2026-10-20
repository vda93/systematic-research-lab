"""Rebuild original historical aggregate figures with pinned Matplotlib."""

from io import BytesIO
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from srl.historical import render_tables, validate_records

BLUE, GOLD, INK = '#315d83', '#bd8939', '#27343f'


def _axes(title, subtitles):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
    fig.suptitle(title, x=.065, ha='left', fontsize=17, fontweight='bold', color=INK)
    for ax, subtitle in zip(axes, subtitles):
        ax.set_title(subtitle, loc='left', fontsize=11, pad=14)
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines[['left', 'bottom']].set_color('#b9c2c9')
        ax.tick_params(colors=INK, labelsize=9)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#e5e9ed', linewidth=.7)
    fig.subplots_adjust(left=.085, right=.97, bottom=.25, top=.77, wspace=.36)
    return fig, axes


def _finish(fig, note, title):
    fig.text(.065, .10, note, fontsize=9, color=INK, va='center', linespacing=1.7)
    out = BytesIO()
    fig.savefig(out, format='svg', metadata={'Date': None, 'Title': title,
                    'Description': note, 'Creator': 'Systematic Research Lab'})
    plt.close(fig)
    return b'\n'.join(line.rstrip() for line in out.getvalue().splitlines()) + b'\n'


def _bars(ax, labels, values, *, ylabel='Total R', digits=2):
    bars = ax.bar(labels, values, width=.55, color=[BLUE, GOLD, GOLD][:len(values)])
    ax.set_ylabel(ylabel, color=INK)
    ax.axhline(0, color=INK, linewidth=.8)
    spread = max(values) - min(0, min(values)) or 1
    ax.set_ylim(min(0, min(values)) - .18*spread, max(0, max(values)) + .25*spread)
    for bar, value in zip(bars, values):
        ax.annotate(f'{value:+.{digits}f}', (bar.get_x()+bar.get_width()/2, value),
                    xytext=(0, 6 if value >= 0 else -7), textcoords='offset points',
                    ha='center', va='bottom' if value >= 0 else 'top', fontsize=11, color=INK)


def _interval(ax, metric, y, color):
    # Percentile intervals may legitimately exclude the original point estimate.
    ax.plot([metric['ci_low'],metric['ci_high']],[y,y],color=color)
    ax.vlines([metric['ci_low'],metric['ci_high']],y-.04,y+.04,color=color)
    ax.plot(metric['estimate'],y,'o',color=color)


def historical_artifacts(data):
    validate_records(data)
    rows = {row['id']: row['metrics'] for row in data['records']}
    result = {'results/historical-tables.md': render_tables(data).encode()}
    style = {'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
             'svg.hashsalt': 'srl-historical-v1', 'axes.labelsize': 10, 'text.color': INK}
    with plt.rc_context(style):
        fig, axes = _axes('Historical research | A better recent backtest did not earn promotion',
                         ['USDJPY mirrored direction · recent sample', 'XAU exit ablation · three observed eras'])
        r = rows['M2']
        _bars(axes[0], [f"Long · n={r['long_trades']}", f"Short · n={r['short_trades']}"], [r['long_total_r'],r['short_total_r']])
        for i, era in enumerate(('EARLY','MID','RECENT')):
            r = rows['M4_'+era]
            axes[1].bar(i-.16,r['canonical_total_r'],width=.3,color=BLUE,label='Canonical' if i==0 else None)
            axes[1].bar(i+.16,r['no_trail_total_r'],width=.3,color=GOLD,label='No trail' if i==0 else None)
        axes[1].set_xticks([0,1,2],['2016–19','2020–24','2025–Jul 26'])
        axes[1].set_ylabel('Total R · complete strategy paths')
        axes[1].axhline(0,color=INK,linewidth=.8)
        axes[1].legend(frameon=False,fontsize=9)
        result['figures/momentum.svg'] = _finish(fig,
            'Historical R-space aggregates · H021/H023A · recent window [2025-01-01, 2026-08-01)\n'
            'Canonical drawdown was lower in every XAU era. Different exits change occupancy and therefore the trade population.',
            'MOMCONT historical direction and exit results')

        fig, axes = _axes('Historical research | Robustness failure and sizing correctness are separate',
                         ['DE30 development concentration stress', 'DE30 known-data engineering replay'])
        r = rows['D2']
        _bars(axes[0],['Full development','Remove top 10 dates'],[r['total_r'],r['remove_top10_date_total_r']])
        r = rows['D7']
        _bars(axes[1],['Original sizing','Corrected sizing'],
              [r['before_median_actual_risk_pct'],r['after_median_actual_risk_pct']],ylabel='Median actual equity risk (%)',digits=5)
        axes[1].axhline(r['requested_risk_pct'],color=INK,linestyle='--',linewidth=1)
        axes[1].text(.98,.98,f"Requested {r['requested_risk_pct']:.2f}%",transform=axes[1].transAxes,ha='right',va='top',fontsize=10)
        result['figures/de30.svg'] = _finish(fig,
            'Development [2020-01-29, 2025-01-01) · H003 NOT SUPPORTED · H005 engineering replay\n'
            '837/837 meaningful paths preserved. The separate spent lockbox did not erase the concentration failure.',
            'DE30 historical concentration and sizing correctness')

        fig, axes = _axes('Historical research | Geometry controls and conflicting OOS blocks',
                         ['USTEC · paired mechanism contrasts across 18 cells', 'USTEC · standalone OOS price-space outcomes'])
        r = rows['O1']
        _bars(axes[0],['Actual − close control','Actual − open control'],
              [r['paired_actual_minus_close_median_r'],r['paired_actual_minus_open_median_r']],ylabel='Median of paired cell deltas (R/trade)',digits=5)
        _bars(axes[1],[f"OOS-A · n={rows['O2_A']['trades']}",f"OOS-B · n={rows['O2_B']['trades']}"],[rows['O2_A']['total_r'],rows['O2_B']['total_r']])
        result['figures/orb.svg'] = _finish(fig,
            'Development 2020–24 · OOS-A signals in 2025 · OOS-B signals Feb–Jun 2026 · later burnoff completes positions\n'
            'Actual geometry beat controls in 6/18 and 9/18 cells. OOS-B failed its own gate; USTEC monetary parity was not certified.',
            'ORB historical mechanism and standalone OOS results')

        fig, axes = _axes('Historical research | An uncertain effect did not justify a reversal',
                         ['NOWICK H004 · continuation probability difference', 'ANTI-NOWICK R001 · net reverse-minus-control'])
        r = rows['N1']
        _interval(axes[0],r,0,BLUE)
        axes[0].set_yticks([0],['H004'])
        axes[0].set_xlabel('Percentage points · day-cluster 95% CI')
        axes[0].set_ylim(-.8,.8)
        for i in range(3):
            r = rows['N2_CELL'+str(i+1)]
            _interval(axes[1],r,i,GOLD)
        axes[1].set_yticks([0,1,2],[f"Cell {i+1} · n={rows['N2_CELL'+str(i+1)]['matched_events']:,}" for i in range(3)])
        axes[1].set_ylim(2.5,-.5)
        axes[1].set_xlabel('ATR units · week-cluster 95% CI')
        for ax in axes:
            ax.spines['left'].set_visible(False)
            ax.grid(False)
            ax.axvline(0,color=INK,linestyle='--',linewidth=1)
        result['figures/nowick.svg'] = _finish(fig,
            f"Historical data through July 2026 · H004 {rows['N1']['matched_events']:,} matched events · R001 discovery-contaminated markouts\n"
            'Different units and estimands: do not compare magnitudes between panels. R001 Holm-adjusted positive-effect p-values all 1.0.',
            'NOWICK historical uncertainty and rejected reversal')
    return result
