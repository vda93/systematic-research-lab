"""Rebuild MacroImpulse visuals from reviewed public historical aggregates.

No strategy engine, calendar acquisition, raw trades or market replay is used.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.patches import Patch, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BLUE, GOLD, TEAL, RED = '#2c6385', '#d09a46', '#318c88', '#b85258'
INK, MUTED, GRID = '#213442', '#657684', '#e6ebef'
SYMBOLS = ('AUDUSD2', 'EURUSD2', 'GBPUSD2', 'USDCAD2', 'USDJPY2')
UNIVERSES = ('FIVE_PAIR_ORIGINAL', 'FOUR_PAIR_EXCLUDE_USDCAD2')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _same(actual, expected, message, tolerance=.000001):
    _require(isinstance(actual, (int, float)) and not isinstance(actual, bool)
             and math.isfinite(actual) and abs(actual-expected) <= tolerance, message)


def _count(value):
    _require(type(value) is int and value >= 0, 'Counts must be nonnegative integers')


def _identities(rows, fields, expected):
    keys = [tuple(r[k] for k in fields) for r in rows]
    _require(len(keys) == len(set(keys)) and set(keys) == set(expected),
             f'Duplicate, missing or unexpected identity: {fields}')


def _validate(data):
    """Fail closed before allocating figures; redundant source summaries must agree.

    Fixed narrative verdicts are contracts, not conclusions recalculated from an
    arbitrary replacement dataset. Consistent numerical transcription changes
    may update marks/labels only while preserving those reviewed contracts.
    """
    def finite(value):
        if isinstance(value, dict):
            for child in value.values(): finite(child)
        elif isinstance(value, list):
            for child in value: finite(child)
        elif isinstance(value, (float, int)):
            _require(math.isfinite(value), 'Nonfinite numeric input')
    try:
        finite(data)
        mechanics=data['mechanics']
        _require(mechanics['classification']=='CONCEPTUAL_SCHEMATIC'
                 and mechanics['historical_price_path'] is False and mechanics['observed_latency'] is False,
                 'Mechanics schematic must remain explicitly nonempirical')
        b=data['baseline']; cells=b['cells']
        _identities(cells, ('year','symbol'), [(y,s) for y in (2023,2024) for s in SYMBOLS])
        for row in cells:
            _require(row['cell_id'] == f"MIEB_{row['year']}_{row['symbol']}", 'Baseline cell ID mismatch')
            _count(row['trades'])
            _require(row['spread_only_usd']>0 and row['gross_profit_usd']>=0 and row['gross_loss_usd']>0,
                     'Baseline positive-cell narrative no longer supported')
            _same(row['spread_only_usd'], row['gross_profit_usd']-row['gross_loss_usd'], 'Baseline cell accounting mismatch')
            _same(row['pf_as_reported'], round(row['gross_profit_usd']/row['gross_loss_usd'],6), 'Baseline cell PF mismatch')
        _count(b['trades']); _same(b['trades'],sum(r['trades'] for r in cells),'Baseline trade summary mismatch')
        _same(b['spread_only_usd'],sum(r['spread_only_usd'] for r in cells),'Baseline P&L summary mismatch')
        _same(b['aggregate_pf_as_reported'],round(sum(r['gross_profit_usd'] for r in cells)/sum(r['gross_loss_usd'] for r in cells),4),'Baseline aggregate PF mismatch')
        _require(b['cost_model']=='SPREAD_ONLY_COMMISSION_NOT_YET_APPLIED','Baseline cost contract changed')

        s=data['spread_filter']; pairs=s['pairs']
        _identities(pairs,('symbol',),[(p,) for p in SYMBOLS])
        for row in pairs:
            _same(row['delta_usd'],row['treatment_usd']-row['control_usd'],'Filter pair delta mismatch')
            _require(row['delta_usd']<=0,'No-pair-improved narrative no longer supported')
        for key in ('control_usd','treatment_usd','delta_usd'):
            _same(s[key],sum(r[key] for r in pairs),'Filter aggregate mismatch')
        _same(s['delta_usd'],s['treatment_usd']-s['control_usd'],'Filter treatment delta mismatch')
        for key in ('control_trades','treatment_trades','removed_completed_trades','removed_completed_trades_profitable'): _count(s[key])
        _same(s['control_trades']-s['treatment_trades'],s['removed_completed_trades'],'Removed-trade count mismatch')
        _same(s['removed_completed_trades'],s['removed_completed_trades_profitable'],'Removed-winner narrative mismatch')
        _require(s['decision']=='REJECT_NO_RETUNING' and s['delta_usd']<0,'Frozen filter decision contract changed')
        _require(s['cost_model']=='SPREAD_ONLY_COMMISSION_NOT_YET_APPLIED','Filter cost contract changed')

        seq=data['sequential']
        for key in ('groups','positions','sequential_groups'): _count(seq[key])
        _same(seq['positions'],2*seq['groups'],'Sequential position count mismatch')
        _same(seq['sequential_groups'],seq['groups'],'Sequential group count mismatch')
        _same(seq['combined_usd'],seq['first_leg_usd']+seq['reversal_leg_usd'],'Sequential leg accounting mismatch')
        _require(seq['independent_equity_paths'] is False and seq['first_leg_usd']<0 and seq['reversal_leg_usd']>0,
                 'Dependent reversal-component contract changed')
        _require(seq['decision']=='REJECT_BLANKET_OPPOSITE_ORDER_SUPPRESSION'
                 and seq['cost_model']=='SPREAD_ONLY_COMMISSION_NOT_APPLIED','Sequential adjudication contract changed')

        m=data['medium']; years=m['years']; pairs=m['pairs']; totals=m['totals']
        _identities(years,('universe','year'),[(u,y) for u in UNIVERSES for y in range(2021,2025)])
        _identities(pairs,('universe','symbol'),[(u,s) for u in UNIVERSES for s in SYMBOLS if u==UNIVERSES[0] or s!='USDCAD2'])
        _identities(totals,('universe',),[(u,) for u in UNIVERSES])
        for row in years+pairs+totals:
            _count(row['trades']); _require(row['commission_usd']>=0,'Negative commission')
            _same(row['adjusted_usd'],row['spread_only_usd']-row['commission_usd'],'Medium commission arithmetic mismatch')
        for total in totals:
            _require(total['adjusted_usd']>0 and total['spread_only_usd']>0,'Positive medium aggregate narrative no longer supported')
            for collection in (years,pairs):
                chosen=[r for r in collection if r['universe']==total['universe']]
                for key in ('trades','spread_only_usd','commission_usd','adjusted_usd'):
                    _same(total[key],sum(r[key] for r in chosen),'Medium annual/pair aggregate mismatch')
            _require(total['pf_as_reported']>0,'Invalid reported medium PF')
        four=[r for r in years if r['universe']==UNIVERSES[1]]
        _require(sum(r['adjusted_usd']>0 for r in four)==3 and next(r for r in four if r['year']==2021)['adjusted_usd']<0,
                 'Annual stability narrative no longer supported')
        _require(m['cost_validation']=='DOCUMENTATION_ONLY' and m['same_account_deal_export_available'] is False
                 and m['decision']=='PARK_FAILED_EVERY_YEAR_POSITIVE_GATE','Medium qualification contract changed')

        c=data['calendar']; monthly=c['monthly']; fs=c['forensic_scope']; earlier=c['earlier_scope']
        expected=[f'{2020+i//12:04d}-{i%12+1:02d}' for i in range(78)]
        _require([r['month'] for r in monthly]==expected,'Calendar requires 78 unique consecutive ordered months')
        for row in monthly:
            for key in ('high','medium','low','unclassified','all'): _count(row[key])
            _same(row['all'],sum(row[k] for k in ('high','medium','low','unclassified')),'Calendar impact-count mismatch')
        for prefix,subset,n in [('earlier',monthly[:60],60),('later',monthly[60:],18)]:
            _count(fs[prefix+'_months']); _count(fs[prefix+'_rows'])
            _same(fs[prefix+'_months'],n,'Forensic month scope mismatch')
            _same(fs[prefix+'_rows'],sum(r['medium'] for r in subset),'Forensic count mismatch')
            _same(fs[prefix+'_rate_as_reported'],round(fs[prefix+'_rows']/n,2),'Forensic rate mismatch')
        _require(fs['earlier_rows']>0,'Earlier rate denominator must be positive')
        _same(earlier['reported_total'],earlier['2020_reported']+earlier['2021_2024_reported'],'Earlier extraction scope mismatch')
        _require(c['scope_reconciled'] is False and c['later_result_classification']=='INVALID_DATA_UNIVERSE',
                 'Calendar adjudication contract changed')
    except (KeyError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f'Missing or invalid Macro aggregate input: {exc}') from exc


def _style(ax, ylabel=None, xlabel=None):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['bottom', 'left']].set_color('#b5c2c9')
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=GRID, lw=.8)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK, fontsize=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK, fontsize=10)


def _start(title, subtitle, size=(12.8, 5.9)):
    fig = plt.figure(figsize=size, facecolor='white')
    fig.text(.065, .95, title, fontsize=17, fontweight='bold', color=INK, va='top')
    fig.text(.065, .885, subtitle, fontsize=10.4, color=MUTED, va='top')
    return fig


def _finish(fig, note, title, *, left=.075, right=.96, bottom=.22, top=.78, wspace=.4):
    fig.text(.065, .075, note, color=MUTED, fontsize=9, va='center', linespacing=1.5)
    fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top, wspace=wspace)
    buf = BytesIO()
    fig.savefig(buf, format='svg', metadata={'Date': None, 'Title': title,
        'Description': note, 'Creator': 'Systematic Research Lab'})
    plt.close(fig)
    svg=b'\n'.join(line.rstrip() for line in buf.getvalue().splitlines()) + b'\n'
    # Native SVG accessible name/description, independent of RDF metadata.
    text=svg.decode('utf-8'); start=text.index('<svg '); end=text.index('>',start)
    text=text[:end]+' role="img" aria-labelledby="macro-title macro-desc"'+text[end:]
    end=text.index('>',start)+1
    text=text[:end]+f'\n <title id="macro-title">{escape(title)}</title>\n <desc id="macro-desc">{escape(note)}</desc>'+text[end:]
    return text.encode('utf-8')


def _money(value, decimals=2):
    return f'{value:+,.{decimals}f}'


def _signed_usd(value):
    return f"{'+' if value>=0 else '−'}${abs(value):,.2f}"


def _mechanics(d):
    title='00  |  How a two-sided news-event order plan can unfold'
    fig=_start(title,'CONCEPTUAL_SCHEMATIC · Fictional state example · Symbolic levels and possible states; no price path or measured timing',size=(13.2,6.2))
    ax=fig.add_subplot(111);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    def line(y,text,color):
        ax.plot([.02,.29],[y,y],color=color,lw=2)
        ax.text(.155,y+.035,text,ha='center',va='bottom',color=INK,fontsize=10.5)
    line(.76,'Upper BUY STOP level',BLUE)
    line(.24,'Lower SELL STOP level',GOLD)
    ax.plot([.06,.25],[.52,.52],color=BLUE,lw=1.3)
    ax.plot([.06,.25],[.46,.46],color=GOLD,lw=1.3)
    ax.text(.155,.59,'Ask / Bid · spread',ha='center',color=INK,fontsize=10.5)
    ax.text(.155,.04,'Ask-based buy entry\nBid-based sell entry',ha='center',va='bottom',color=MUTED,fontsize=10,linespacing=1.5)
    ax.text(.155,.96,'Before the announcement',ha='center',color=INK,fontsize=11,fontweight='bold')
    ax.plot([.365,.365],[.2,.83],color=MUTED,lw=1.2,linestyle='--')
    ax.text(.365,.96,'Scheduled\nrelease',ha='center',va='top',color=INK,fontsize=11,fontweight='bold',linespacing=1.3)
    def box(x,y,w,h,text,color=BLUE):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.013',facecolor='#f4f7f9',edgecolor=color,lw=1.3))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',color=INK,fontsize=10.5,linespacing=1.5)
    def arrow(start,end):
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':MUTED,'lw':1.4,'shrinkA':4,'shrinkB':5})
    box(.45,.64,.19,.2,'One side\ntriggers')
    box(.75,.64,.22,.2,'Protective stop /\ntrailing-managed exit',TEAL)
    box(.75,.21,.22,.2,'If the first\nposition stops',GOLD)
    box(.45,.21,.22,.2,'Opposite pending\nmay trigger later',GOLD)
    arrow((.30,.76),(.45,.74));arrow((.65,.74),(.75,.74))
    arrow((.86,.63),(.86,.42));arrow((.74,.31),(.68,.31))
    ax.text(.71,.02,'Only if still eligible; scheduled deletion\ncan cancel unfilled news orders.',ha='center',va='bottom',color=MUTED,fontsize=10,linespacing=1.5)
    return _finish(fig,'Generic two-sided event-order schematic; exact contracts vary. Spread affects entry/stop geometry.\nArrows are possible state transitions, not historical trades or independent paths. Source: frozen behavioral specification plus sequential adjudication.',title,top=.76,bottom=.23)


def _baseline(d):
    baseline=d['baseline']
    title = '01  |  Ten positive baseline cells, with commission still excluded'
    fig = _start(title, 'High-impact historical bridge · Exness custom symbols · 2023–2024 · Spread-only USD')
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1])
    ax = fig.add_subplot(gs[0]); info = fig.add_subplot(gs[1]); info.axis('off')
    symbols = ['AUDUSD2', 'EURUSD2', 'GBPUSD2', 'USDCAD2', 'USDJPY2']
    cells = {(c['year'], c['symbol']): c for c in d['baseline']['cells']}
    values = np.array([[cells[y,s]['spread_only_usd'] for y in [2023,2024]] for s in symbols])
    ax.pcolormesh(np.arange(3)-.5, np.arange(6)-.5, values,
                  cmap='Blues', vmin=0, vmax=1000, edgecolors='white', linewidth=3)
    ax.set_ylim(4.5, -.5)
    ax.set_xticks([0,1], ['2023','2024']); ax.set_yticks(range(5), symbols)
    ax.tick_params(length=0, labelsize=10, colors=INK, pad=8)
    for spine in ax.spines.values(): spine.set_visible(False)
    for i,s in enumerate(symbols):
        for j,y in enumerate([2023,2024]):
            c=cells[y,s]
            ax.text(j,i,f"${c['spread_only_usd']:,.2f}\nn = {c['trades']}", ha='center', va='center', fontsize=11,
                    color='white' if values[i,j]>600 else INK, linespacing=1.6)
    info.text(0,.93,f"+${baseline['spread_only_usd']:,.2f}",fontsize=27,fontweight='bold',color=BLUE,transform=info.transAxes)
    info.text(0,.78,f"{baseline['trades']:,} recorded trades",fontsize=14,color=INK,transform=info.transAxes)
    info.text(0,.64,f"Aggregate spread-only PF {baseline['aggregate_pf_as_reported']:.4f}",fontsize=12,color=INK,transform=info.transAxes)
    positive=sum(c['spread_only_usd']>0 for c in baseline['cells'])
    info.text(0,.44,f"{positive} / {len(baseline['cells'])} positive pair-year cells",fontsize=12,color=INK,transform=info.transAxes)
    info.text(0,.12,'Historical baseline bridge\nAlready opened evidence\nCommission and live economics unresolved',fontsize=11,color=MUTED,linespacing=1.8,transform=info.transAxes)
    return _finish(fig,'Cell labels: recorded spread-only USD and completed trades. Color begins at $0.\nSource: original BASELINE_CELL_SUMMARY.csv. This is reported historical evidence, not a net investable-return claim.',title,left=.13)


def _spread(d):
    s=d['spread_filter']; title='02  |  The frozen spread filter removed winners and reduced P&L'
    fig=_start(title,'Separate 2021–2022 frozen validation · SPREAD3 control versus SPREAD1 treatment · Spread-only USD')
    gs=fig.add_gridspec(1,2,width_ratios=[1,1.1]); a=fig.add_subplot(gs[0]); b=fig.add_subplot(gs[1])
    vals=[s['control_usd'],s['treatment_usd']]
    bars=a.bar([f"SPREAD3\n{s['control_trades']} trades",f"SPREAD1\n{s['treatment_trades']} trades"],vals,color=[BLUE,GOLD],width=.55)
    a.set_ylim(0,3300);_style(a,ylabel='Spread-only USD')
    for bar,v in zip(bars,vals):a.text(bar.get_x()+bar.get_width()/2,v+80,f'${v:,.2f}',ha='center',color=INK,fontsize=11)
    pairs=sorted(s['pairs'],key=lambda p:p['symbol'])
    b.barh(range(5),[p['delta_usd'] for p in pairs],color=GOLD,height=.48)
    b.set_yticks(range(5),[p['symbol'] for p in pairs]);b.invert_yaxis();b.set_xlim(-4.7,.4)
    _style(b,xlabel='Treatment minus control, USD');b.grid(axis='y',visible=False);b.grid(axis='x',color=GRID,lw=.8)
    b.axvline(0,color=INK,lw=1)
    for i,p in enumerate(pairs):b.text(p['delta_usd']-.12,i,_money(p['delta_usd']),ha='right',va='center',fontsize=10,color=INK)
    b.set_title(f"No pair improved · total delta −${abs(s['delta_usd']):.2f}",loc='left',fontsize=11,color=INK,pad=15)
    note=(f"{s['removed_completed_trades']} completed trades removed; all {s['removed_completed_trades_profitable']} were profitable. "
          f"Double-trigger P&L was unchanged at +${s['double_trigger_usd_both_arms']:.2f} in both arms.\n"
          'Integrity passed; the frozen intervention was REJECTED without retuning. No confidence interval is inferred from these totals.')
    return _finish(fig,note,title,wspace=.52)


def _sequential(d):
    s=d['sequential'];title='03  |  The reversal leg recovered part of the first-leg loss'
    fig=_start(title,f"{s['groups']} sequential double-trigger groups · {s['positions']} positions · Exness 2021–2024 development · Spread-only USD")
    ax=fig.add_subplot(111)
    vals=[s['first_leg_usd'],s['reversal_leg_usd'],s['combined_usd']]
    bars=ax.bar(['First leg\nalready stopped','Later opposite leg\nrecovery',f"Combined\nsame {s['groups']} groups"],vals,
                color=[RED,TEAL,'white'],edgecolor=[RED,TEAL,INK],linewidth=1.4,width=.48)
    bars[2].set_hatch('///')
    for bar,v in zip(bars,vals):
        ax.text(bar.get_x()+bar.get_width()/2,v+(12 if v>0 else -12),'$'+_money(v),ha='center',va='bottom' if v>0 else 'top',fontsize=13,color=INK)
    _style(ax,ylabel='Spread-only USD, dependent leg aggregates');ax.axhline(0,color=INK,lw=1)
    ax.set_ylim(-360,260)
    return _finish(fig,f"All {s['groups']} groups were stop-then-opposite-trigger sequences. Components belong to the same groups; these are not independent equity paths.\nSource: canonical adjudication as reported. Blanket opposite-order suppression was REJECTED; commission and group-level uncertainty are unavailable.",title)


def _costs(d):
    m=d['medium']; title='04  |  Positive medium-impact totals still failed annual stability'
    fig=_start(title,'Clean medium-only discovery · 2021–2024 · USD · Commission validation: DOCUMENTATION_ONLY',size=(13.2,6.2))
    gs=fig.add_gridspec(1,2,width_ratios=[1,1.45]);a=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1])
    totals=sorted(m['totals'],key=lambda r:UNIVERSES.index(r['universe']))
    x=np.arange(2);width=.32
    for offset,key,color,label in [(-width/2,'spread_only_usd',BLUE,'Spread-only'),(width/2,'adjusted_usd',GOLD,'After modeled commission')]:
        vals=[r[key] for r in totals];bars=a.bar(x+offset,vals,width,color=color,label=label)
        for bar,v in zip(bars,vals):a.text(bar.get_x()+bar.get_width()/2,v+25,f'{v:,.2f}',ha='center',fontsize=9.5,color=INK)
    a.set_xticks(x,[f"Five pairs\nn = {totals[0]['trades']}",f"Four pairs\nn = {totals[1]['trades']}"]);a.set_ylim(0,max(1320,max(r['spread_only_usd'] for r in totals)*1.2))
    _style(a,ylabel='Aggregate USD');a.set_title('Original and preregistered exclusion',loc='left',fontsize=11,color=INK,pad=15)
    years=sorted([r for r in m['years'] if r['universe']=='FOUR_PAIR_EXCLUDE_USDCAD2'],key=lambda r:r['year']);x=np.arange(4)
    for offset,key,color in [(-width/2,'spread_only_usd',BLUE),(width/2,'adjusted_usd',GOLD)]:
        bars=b.bar(x+offset,[r[key] for r in years],width,color=color)
        for bar,r in zip(bars,years):
            v=r[key];b.text(bar.get_x()+bar.get_width()/2,v+(13 if v>=0 else -15),_money(v),ha='center',va='bottom' if v>=0 else 'top',fontsize=9.5,color=INK)
    b.set_xticks(x,[f"{r['year']}\nn = {r['trades']}" for r in years]);b.set_ylim(-90,680)
    b.axhline(0,color=INK,lw=1);_style(b,ylabel='Four-pair annual USD')
    first=years[0]
    b.set_title(f"Four-pair {first['year']}: {_signed_usd(first['spread_only_usd'])} → {_signed_usd(first['adjusted_usd'])}",loc='left',fontsize=11,color=INK,pad=15)
    fig.legend(handles=[Patch(facecolor=BLUE,label='Spread-only'),Patch(facecolor=GOLD,label='After modeled commission')],loc='upper center',bbox_to_anchor=(.5,.835),ncol=2,frameon=False,fontsize=10)
    return _finish(fig,'Four-pair candidate excludes USDCAD2. Modeled commission: USD 3.50 per actual lot per side on entry and exit.\nNo same-account deal export: live net economics unvalidated. Four-pair candidate remained PARK: only 3/4 positive years at modeled commission.',title,top=.72,wspace=.32)


def _calendar(d):
    c=d['calendar'];title='05  |  The calendar lost coverage before the later evaluation'
    fig=_start(title,'Original calendar audit · January 2020–June 2026 · Recorded source rows, not estimates of real announcements')
    gs=fig.add_gridspec(1,2,width_ratios=[2.1,1]);a=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1])
    monthly=c['monthly'];x=np.arange(len(monthly))
    a.plot(x,[r['medium'] for r in monthly],color=BLUE,lw=2,label='MEDIUM')
    a.plot(x,[r['high'] for r in monthly],color=GOLD,lw=1.7,linestyle='--',label='HIGH')
    a.axvspan(56,57,color='#d9dfe4',alpha=.8)
    a.axvspan(60,77,color='#f3f5f7',zorder=0)
    a.text(54,370,'Sep–Oct 2024\ncoverage break',ha='right',va='top',fontsize=10,color=INK)
    a.annotate('',xy=(56.5,155),xytext=(54.5,315),arrowprops={'arrowstyle':'->','color':MUTED})
    a.set_xlim(0,77);a.set_ylim(0,410)
    a.set_xticks([0,12,24,36,48,60,77],['Jan 2020','2021','2022','2023','2024','2025','Jun 2026'])
    _style(a,ylabel='Recorded rows per month');a.legend(loc='upper left',frameon=False,fontsize=10,ncol=2)
    scope=c['forensic_scope'];counts=[scope['earlier_rows'],scope['later_rows']]
    rates=[scope['earlier_rows']/scope['earlier_months'],scope['later_rows']/scope['later_months']]
    bars=b.bar([f"2020–2024\n{scope['earlier_months']} months",f"2025–Jun 2026\n{scope['later_months']} months"],rates,color=[BLUE,GOLD],width=.55)
    _style(b,ylabel='MEDIUM rows per month');b.set_ylim(0,410)
    for bar,rate,n in zip(bars,rates,counts):b.text(bar.get_x()+bar.get_width()/2,rate+10,f'{rate:.2f}\n{n:,} rows',ha='center',fontsize=10,color=INK,linespacing=1.5)
    b.text(.5,.87,f'{100*rates[1]/rates[0]:.1f}% of earlier rate',transform=b.transAxes,ha='center',fontsize=11,fontweight='bold',color=INK)
    note=('INVALID_DATA_UNIVERSE superseded the provisional clean strategy-failure verdict. Surviving rows still parsed successfully.\n'
          f"Forensic scope: {counts[0]:,} earlier MEDIUM rows. Earlier strategy-input counts sum to {c['earlier_scope']['reported_total']:,}; scopes remain unreconciled. No repaired result is implied.")
    return _finish(fig,note,title,wspace=.32)


def build_figures(data):
    _validate(data)
    with matplotlib.rc_context({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'macro-public-v002',
                                 'axes.unicode_minus':True,'font.size':10}):
        return {f'macro-{name}.svg':builder(data) for name,builder in [
            ('mechanics',_mechanics),('baseline',_baseline),('spread-filter',_spread),('sequential',_sequential),('costs',_costs),('calendar',_calendar)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check committed SVG bytes without writing.')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'figures')
    args=parser.parse_args()
    data=json.loads((ROOT/'data/macro-public.json').read_text(encoding='utf-8'))
    figures=build_figures(data)
    if args.check:
        changed=[n for n,b in figures.items() if not (args.output_dir/n).is_file() or (args.output_dir/n).read_bytes()!=b]
        if changed:raise SystemExit('Figure mismatch: '+', '.join(changed))
        print(f'{len(figures)} MacroImpulse SVGs match reviewed aggregates.')
    else:
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for name,content in figures.items():(args.output_dir/name).write_bytes(content)
        print(f'Wrote {len(figures)} MacroImpulse SVGs.')


if __name__=='__main__':
    main()
