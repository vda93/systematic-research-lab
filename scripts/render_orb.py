"""Render reported ORB evidence; no strategy execution or private-data dependency."""
from __future__ import annotations

import argparse
from html import escape
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, TwoSlopeNorm
from matplotlib.patches import Patch
import numpy as np

from scripts.render_orbindex import _figure, _finish as _precedent_finish, _ax_style, BLUE, GOLD, TEAL, RED, INK, MUTED

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'EMPIRICAL_REPORTED_PRIVATE_BACKTEST_NOT_PUBLICLY_REPLAYABLE'
DIRECTIONS = ['BOTH', 'LONG_ONLY', 'SHORT_ONLY']
DURATIONS = [5, 10, 15, 30, 45, 60]


def _finish(fig,title,note,**kwargs):
    """Add standalone accessibility without changing any ORBINDEX output."""
    svg=_precedent_finish(fig,title,note,**kwargs).decode('utf-8')
    svg=svg.replace('<svg ','<svg role="img" aria-labelledby="figure-title figure-desc" ',1)
    svg=svg.replace('<title>','<title id="figure-title">',1)
    svg=svg.replace('</title>','</title>\n <desc id="figure-desc">'+escape(note)+'</desc>',1)
    return svg.encode('utf-8')


def _rows(data):
    return [dict(zip(data['columns'], r, strict=True)) for r in data['cells']]


def validate(ustec, gold):
    """Reject an incomplete or ambiguous surface instead of filling absent cells."""
    for data in [ustec, gold]:
        if data.get('scope') != SCOPE or len(data.get('cells', [])) != 1728:
            raise ValueError('expected all 1728 reported historical cells and scope')
        rows = _rows(data)
        clock = 'local_anchor_ny' if 'local_anchor_ny' in data['columns'] else 'anchor_utc'
        expected = {(f'{h:02d}:{m:02d}', t, d) for h in range(24)
                    for m in [0, 15, 30, 45] for t in DURATIONS for d in DIRECTIONS}
        observed = {(r[clock], r['or_duration_minutes'], r['direction_mode']) for r in rows}
        if observed != expected or len({r['cell_id'] for r in rows}) != 1728:
            raise ValueError('missing or duplicate parameter identity')
        for r in rows:
            for key in ['total_r', 'mean_r']:
                value = r[key]
                if value is not None and (isinstance(value, bool) or not math.isfinite(value)):
                    raise ValueError('nonfinite result')
            if r.get('scientific_classification') == 'SCIENTIFIC_INVALID' and r['mean_r'] is not None:
                raise ValueError('invalid cells cannot have scored means')
    if [r['block'] for r in ustec['oos']] != ['A','B']:
        raise ValueError('OOS blocks must remain distinct and ordered')
    for block in ustec['oos']:
        curve=block['exit_month_cumulative_r']
        if (not curve or not math.isfinite(block['total_r'])
                or not all(math.isfinite(r[1]) and isinstance(r[2],int) and r[2]>0 for r in curve)
                or not math.isclose(curve[-1][1],block['total_r'],abs_tol=1e-9)
                or sum(r[2] for r in curve)!=block['trades']
                or [r[0] for r in curve]!=sorted(set(r[0] for r in curve))):
            raise ValueError('OOS month curve, total, counts and chronology must reconcile')


def grid_values(data, direction, field='mean_r'):
    rows = _rows(data)
    clock = 'local_anchor_ny' if 'local_anchor_ny' in data['columns'] else 'anchor_utc'
    lookup = {(r[clock], r['or_duration_minutes']): r[field]
              for r in rows if r['direction_mode'] == direction}
    return np.array([[np.nan if lookup[(f'{i//4:02d}:{15*(i%4):02d}', t)] is None
                      else lookup[(f'{i//4:02d}:{15*(i%4):02d}', t)]
                      for i in range(96)] for t in DURATIONS])


def _heat(data, title, gold=False, qualification=False):
    fig = _figure((13.4, 8.5)); axes = fig.subplots(3, 1)
    if qualification:
        cmap = ListedColormap(['#e7ecf0', '#afcadb', GOLD, TEAL])
        norm = matplotlib.colors.BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], 4)
    else:
        cmap = plt.get_cmap('RdBu').copy(); cmap.set_bad('#e0e5e8')
        norm = TwoSlopeNorm(vmin=-.6, vcenter=0, vmax=.25)
    rows = _rows(data)
    for ax, direction in zip(axes, DIRECTIONS):
        if qualification:
            category = [dict(r, category=3 if r['selected_region'] else 2 if r['robust'] else 1 if r['total_r']>0 else 0) for r in rows]
            q = dict(data, columns=[*data['columns'], 'category'],
                     cells=[[r[c] for c in [*data['columns'], 'category']] for r in category])
            values = grid_values(q, direction, 'category')
        else:
            values = grid_values(data, direction)
        mesh = ax.pcolormesh(np.arange(97)-.5, np.arange(7)-.5, values,
                             cmap=cmap, norm=norm, shading='flat', rasterized=False)
        ax.set_yticks(range(6), [f'OR{t}' for t in DURATIONS])
        ax.set_xticks([0,12,24,36,48,60,72,84,95],
                      ['00:00','03:00','06:00','09:00','12:00','15:00','18:00','21:00','23:45'])
        ax.set_title(direction.replace('_ONLY',' only').title(), loc='left', fontsize=11, color=INK, pad=8)
        ax.tick_params(length=0, labelsize=9, colors=MUTED)
        ax.set_xlim(-.5,95.5); ax.set_ylim(-.5,5.5)
        for spine in ax.spines.values(): spine.set_visible(False)
        if gold:
            for r in rows:
                if r['direction_mode'] != direction or r['mean_r'] is not None: continue
                h,m = map(int,r['anchor_utc'].split(':')); x=h*4+m//15
                invalid=r['scientific_classification']=='SCIENTIFIC_INVALID'
                ax.plot(x,DURATIONS.index(r['or_duration_minutes']),
                        marker='x' if invalid else '.',color=INK,ms=5,ls='')
        elif qualification:
            for r in rows:
                if r['selected_cell'] and r['direction_mode']==direction:
                    h,m=map(int,r['local_anchor_ny'].split(':'))
                    ax.plot(h*4+m//15,DURATIONS.index(r['or_duration_minutes']),marker='*',
                            markerfacecolor='white',markeredgecolor=INK,ms=11,ls='')
    axes[-1].set_xlabel('Opening-range start · '+('UTC' if gold else 'America/New_York local clock'),color=INK)
    if qualification:
        counts=[sum(r['total_r']<=0 for r in rows),
                sum(r['total_r']>0 and not r['robust'] for r in rows),
                sum(r['robust'] and not r['selected_region'] for r in rows),
                sum(r['selected_region'] for r in rows)]
        labels=[f'Nonpositive ({counts[0]:,})',f'Positive, not robust ({counts[1]})',
                f'Robust outside plateau ({counts[2]})',f'Selected plateau ({counts[3]})']
        handles=[Patch(facecolor=c,label=l) for c,l in zip(cmap.colors,
                 labels)]
        fig.legend(handles=handles,loc='center',bbox_to_anchor=(.52,.145),ncol=2,frameon=False,fontsize=9)
        note=('USTEC2 Discovery: 29 Jan 2020–30 Nov 2024 signals; December 2024 burnoff. Star = frozen 10:15 / OR60 LONG medoid.\n'
              'Frozen flags copied from selection records. Neighbouring cells share history and trades; qualification is not independent validation.')
    else:
        cax=fig.add_axes([.31,.145,.39,.018])
        bar=fig.colorbar(mesh,cax=cax,orientation='horizontal',extend='both',ticks=[-.6,-.3,0,.25])
        bar.solids.set_rasterized(False)
        bar.set_label('Mean price-space R per trade · colour clipped to [−0.60, +0.25]',fontsize=9,color=INK)
        bar.ax.tick_params(labelsize=8)
        if gold:
            invalid=sum(r['scientific_classification']=='SCIENTIFIC_INVALID' for r in rows)
            empty=sum(r['scientific_classification']=='VALID_COMPLETE' and r['trade_count']==0 for r in rows)
            positive=sum(r['total_r'] is not None and r['total_r']>0 for r in rows)
            note=(f'XAUUSD2 Discovery: 2019–30 Nov 2023 signal sessions; December burnoff. All {len(rows):,} cells shown: {len(rows)-invalid:,} valid, {invalid} invalid.\n'
                  f'Grey × = scientific invalid; grey dot = {empty} valid zero-trade cells with undefined means. {positive} positive cells. No interpolation or monetary alpha claim.')
        else:
            positive=sum(r['total_r']>0 for r in rows)
            note=(f'USTEC2 Discovery: 29 Jan 2020–30 Nov 2024 signals; December 2024 burnoff; 2020 partial. All {len(rows):,} cells shown; none missing/invalid.\n'
                  f'Executable Bid/Ask price R, not commission/financing-adjusted money. Correlated configurations; {positive} positive cells are not independent confirmations.')
    return _finish(fig,title,note,layout=dict(left=.075,right=.97,bottom=.25,top=.86,hspace=.62))


def _selection(u):
    fig=_figure((12.8,5.8));a,b=fig.subplots(1,2)
    for i,key in enumerate(['maximum','medoid']):
        r=u['concentration'][key]
        a.bar(i-.16,r['total_r'],width=.32,color=BLUE,label='All trades' if i==0 else None)
        a.bar(i+.16,r['total_r_excluding_largest_absolute_r_trade'],width=.32,color=GOLD,label='Largest |R| trade removed' if i==0 else None)
        a.text(i, max(r['total_r'],r['total_r_excluding_largest_absolute_r_trade'])+8,
               f"{r['trade_count']} trades",ha='center',fontsize=9,color=INK)
    a.set_xticks([0,1],['Maximum\n07:30 / OR45 SHORT','Medoid\n10:15 / OR60 LONG'])
    a.axhline(0,color=INK,lw=1);a.set_ylim(-65,160)
    _ax_style(a,ylabel='Discovery total price-space R');a.legend(frameon=False,fontsize=8.5,loc='upper right')
    years=u['medoid_years'];b.bar([str(r['year'])+('*' if r['year']==2020 else '') for r in years],
                                [r['total_r'] for r in years],color=[BLUE if r['total_r']>0 else RED for r in years])
    b.axhline(0,color=INK,lw=1);_ax_style(b,ylabel='Medoid total price-space R by source year')
    mx=u['concentration']['maximum']
    note=('USTEC2 spent Discovery, 2020* partial–2024; last eligible signal session 30 Nov 2024. No trades removed from authoritative evidence.\n'
          f"The maximum contains one {mx['largest_positive_r']:+.2f}R trade; removing its largest |R| observation changes {mx['total_r']:+.2f}R to {mx['total_r_excluding_largest_absolute_r_trade']:+.2f}R. Medoid selection used regional distance.")
    return _finish(fig,'ORB  |  A sharp maximum and a representative answer different questions',note)


def _controls(u):
    fig=_figure((12.8,6.8)); axes=fig.subplots(1,2,sharey=True)
    names=sorted({r['cell_id'] for r in u['placebo_comparisons']})
    extent=max(abs(r['delta_mean_r']) for r in u['placebo_comparisons'])+.02
    for ax,variant,label in zip(axes,['C1_CLOSE_CENTERED_PLACEBO','C2_OPEN_CENTERED_PLACEBO'],['Close-centred placebo','Open-centred placebo']):
        rows={r['cell_id']:r for r in u['placebo_comparisons'] if r['variant']==variant}
        vals=[rows[n]['delta_mean_r'] for n in names]
        ax.scatter(vals,range(18),c=[BLUE if v>0 else RED for v in vals],s=25)
        ax.axvline(0,color=INK,lw=1);ax.axvline(float(np.median(vals)),color=GOLD,lw=1.5,ls='--')
        ax.set_title(f'{label}\n{sum(v>0 for v in vals)}/18 favour actual; median {np.median(vals):+.4f}R',fontsize=11,color=INK)
        _ax_style(ax,xlabel='Actual minus placebo · cell mean R/trade')
        ax.set_xlim(-extent,extent);ax.set_xticks([-.1,0,.1]);ax.grid(axis='x',color='#e6ebef');ax.grid(axis='y',visible=False)
    axes[0].set_yticks(range(18),[n.replace('NY_','').replace('_LONG','').replace('_',' / ') for n in names],fontsize=8)
    axes[0].invert_yaxis()
    note=('USTEC2 posthoc Discovery mechanism study: frozen 18-cell LONG region, Jan 2020–Nov 2024 signals; December burnoff; 2020 partial.\n'
          'Same-width alternative range boundaries. Both comparisons required positive median differences and ≥12/18 favourable cells. Specificity failed.\n'
          'Each dot is a correlated configuration-level paired difference, not a trade pair or independent replication. Dashed gold = median; no invented intervals.')
    return _finish(fig,'ORB  |  Exact opening-range geometry did not pass its control test',note,
                   layout=dict(left=.13,right=.97,bottom=.23,top=.77,wspace=.25))


def _validation(u):
    fig=_figure((12.8,6.2));axes=fig.subplots(1,2,sharey=True)
    for ax,r in zip(axes,u['oos']):
        curve=r['exit_month_cumulative_r']; y=[0]+[v[1] for v in curve]
        ax.step(range(len(y)),y,where='post',color=BLUE if r['gate']=='PASS' else RED,lw=2)
        ax.axhline(0,color=INK,lw=1)
        ax.set_xticks([0,len(y)-1],['Before '+curve[0][0],curve[-1][0]])
        ax.set_title(f"OOS-{r['block']}: {r['gate']} · {r['total_r']:+.3f}R\n{r['trades']} trades; region {r['region_positive']}/18 positive",loc='left',color=INK,fontsize=11)
        _ax_style(ax,xlabel='Actual UTC exit month (including burnoff)',ylabel='Cumulative closed-trade price R')
    note=('Frozen USTEC2 medoid; independently spent blocks. OOS-A: 2025 signals, Jan 2026 burnoff. OOS-B: Feb–Jun 2026 signals, Jul burnoff.\n'
          'Month-end aggregates from verified original exit timestamps and returns; no mark-to-market equity or within-month path is implied.\n'
          'Separate horizontal scales reflect different horizons. The second block failed its standalone primary and region gates; no pooled rescue.')
    return _finish(fig,'ORB  |  First confirmation did not survive a separate second block',note)


def _stress(g):
    fig=_figure((12.8,6.0));axes=fig.subplots(1,2,sharey=True)
    scenarios=['S0','MILD','CORE','SEVERE'];xx=np.arange(4)
    for ax,period,label in zip(axes,['DISCOVERY','OOS'],['Discovery · 2019–Nov 2023','Validation · 2024–Nov 2025']):
        for candidate,color,marker in [('A',BLUE,'o'),('B',GOLD,'s'),('C',TEAL,'^')]:
            rs={r['scenario']:r for r in g['stress'] if r['candidate']==candidate and r['period']==period}
            ax.plot(xx,[rs[s]['mean_r'] for s in scenarios],color=color,marker=marker,lw=1.8,label=candidate)
        ax.set_xticks(xx,['Baseline','Mild','CORE','Severe']);ax.axhline(0,color=INK,lw=1)
        ax.set_title(label,loc='left',fontsize=11,color=INK);_ax_style(ax,ylabel='Mean executable price R / completed trade')
        ax.legend(frameon=False,title='Frozen candidate',ncol=3,fontsize=9)
    note=('Separate XAUUSD2 Phase 8C lineage; December of each segment is burnoff. Mild: 100 ms +0.01R; CORE: 250 ms +0.025R; Severe: 500 ms +0.05R.\n'
          'Normalized shocks, not measured live slippage. A/C passed full CORE gates in each segment; B failed Discovery. All severe Discovery means ≤0.\n'
          'Scenario categories are connected to aid comparison; they are neither a time series nor one continuous cost model. No money-parity inference.')
    return _finish(fig,'ORB Gold  |  Execution robustness remained conditional on stress',note)


def _economics(g):
    fig=_figure((12.8,6.2));a,b=fig.subplots(1,2)
    rows=g['monetary']['rows'];xx=np.arange(4)
    for offset,key,color,label in [(-.18,'gross_pnl',BLUE,'Before swap / fees'),(.18,'net_pnl',GOLD,'After recorded costs')]:
        a.bar(xx+offset,[r[key] for r in rows],width=.34,color=color,label=label)
    a.set_xticks(xx,[r['candidate']+'\n'+('Discovery' if r['period']=='DISCOVERY' else 'Validation') for r in rows])
    a.axhline(0,color=INK,lw=1);_ax_style(a,ylabel='Sum of monetary-parity rows · USD');a.legend(frameon=False,fontsize=9)
    a.set_title('Parity ledger: recorded financing changed the sign',loc='left',fontsize=10,color=INK)
    terminal=g['terminal']['candidates'];b.bar([r['candidate'] for r in terminal],[r['pf_money'] for r in terminal],color=[BLUE,TEAL],width=.45)
    b.axhline(1,color=INK,lw=1,ls='--');b.set_ylim(0,1.2)
    for i,r in enumerate(terminal): b.text(i,r['pf_money']+.035,f"PF {r['pf_money']:.2f}\n{r['trades']} trades",ha='center',color=INK,fontsize=10)
    b.set_title('Spent 2026 terminal holdout',loc='left',fontsize=11,color=INK);_ax_style(b,ylabel='Monetary profit factor (rounded to 2 decimals)',xlabel='Separate frozen gold candidates')
    money=g['monetary'];synthetic=sum(r['synthetic_exits'] for r in money['rows'])
    note=(f"Left: A/C monetary-parity rows, 2019–Nov 2023 Discovery and 2024–Nov 2025 validation; December burnoff. Source position sizes, {money['reconciled_trades']:,} rows;\n"
          f"{synthetic} synthetic scientific exits, {money['mismatches']} unexplained mismatches. Commission/fees are zero here; deductions are recorded swap. Not a combined portfolio.\n"
          f"{money['feasible']}/{money['tested']} frozen deployment policies feasible. Right: Jan–Jun 2026 eligible signals, July burnoff; A negative, C approximately flat. Parity is not profitability.")
    return _finish(fig,'ORB Gold  |  Accounting passed; economic qualification did not',note)


def _summary(u,g):
    """Compact single-column entry point; detailed panels retain full definitions."""
    fig=_figure((5.8,7.8));a,b=fig.subplots(2,1)
    values=[r['total_r'] for r in u['oos']]
    a.barh([1,0],values,color=[BLUE,RED],height=.42)
    a.set_yticks([1,0],['OOS-A\n2025','OOS-B\nFeb–Jun 2026'],fontsize=11)
    a.axvline(0,color=INK,lw=1);a.set_xlim(-5,34)
    for y,r in zip([1,0],u['oos']):
        a.text(max(0,r['total_r'])+.8,y,f"{r['total_r']:+.2f}R\n{r['gate']}",va='center',fontsize=11,color=INK)
    a.set_title('USTEC: the second block failed',loc='left',fontsize=13,fontweight='bold',color=INK,pad=12)
    _ax_style(a,xlabel='Total price-space R');a.tick_params(labelsize=10)
    rows=[r for r in g['monetary']['rows'] if r['period']=='DISCOVERY']
    y=np.array([1,0])
    b.barh(y+.13,[r['gross_pnl'] for r in rows],height=.24,color=BLUE,label='Before swap')
    b.barh(y-.13,[r['net_pnl'] for r in rows],height=.24,color=GOLD,label='After swap')
    b.set_yticks(y,['Gold A','Gold C'],fontsize=11);b.axvline(0,color=INK,lw=1)
    b.set_title('Gold: financing erased Discovery gains',loc='left',fontsize=12,fontweight='bold',color=INK,pad=12)
    _ax_style(b,xlabel='Monetary-parity ledger total · USD');b.tick_params(labelsize=10)
    b.legend(frameon=False,fontsize=10,loc='lower right');b.set_ylim(-.55,1.55)
    b.set_xlim(-1000,2500);b.set_xticks([-1000,0,1000,2000])
    note=('Reported historical evidence; private backtests.\nUSTEC blocks are separate; burnoff included in outcomes.\nGold: 2019–Nov 2023 signals, December burnoff.\nSource sizing; synthetic exits included. No deployment.')
    return _finish(fig,'ORB  |  Why the programs stopped',note,
                   layout=dict(left=.24,right=.95,bottom=.22,top=.85,hspace=.65))


def orb_artifacts(ustec: dict, gold: dict) -> dict[str, bytes]:
    validate(ustec,gold)
    with plt.rc_context({'font.family':'DejaVu Sans','svg.fonttype':'none',
                         'svg.hashsalt':'srl-orb-v002','text.color':INK,'figure.dpi':100}):
        return {
            'figures/orb-summary.svg':_summary(ustec,gold),
            'figures/orb-ustec-surface.svg':_heat(ustec,'ORB USTEC  |  The complete timing search'),
            'figures/orb-ustec-qualification.svg':_heat(ustec,'ORB USTEC  |  Positive cells narrowed to a small frozen plateau',qualification=True),
            'figures/orb-ustec-selection.svg':_selection(ustec),
            'figures/orb-ustec-controls.svg':_controls(ustec),
            'figures/orb-ustec-validation.svg':_validation(ustec),
            'figures/orb-gold-surface.svg':_heat(gold,'ORB Gold  |  A separate discovery surface',gold=True),
            'figures/orb-gold-stress.svg':_stress(gold),
            'figures/orb-gold-economics.svg':_economics(gold),
        }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    u=json.loads((ROOT/'data/orb-ustec-public.json').read_text())
    g=json.loads((ROOT/'data/orb-gold-public.json').read_text())
    bad=[]
    for name,blob in orb_artifacts(u,g).items():
        path=ROOT/name
        if args.write: path.write_bytes(blob)
        elif not path.is_file() or path.read_bytes()!=blob: bad.append(name)
    print('ORB figure mismatches:' if bad else 'ORB figures verified:',bad or 9)
    return int(bool(bad))


if __name__=='__main__': raise SystemExit(main())
