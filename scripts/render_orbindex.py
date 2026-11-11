"""Rebuild the public ORBINDEX historical summary figures from reviewed aggregates.

This does not replay private MT5 ticks, orders, broker fills or strategy outcomes.
The input is a carefully scoped public-transcription file, not market data.
"""

from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BLUE, GOLD, TEAL, RED = '#2c6385', '#d09a46', '#318c88', '#b85258'
INK, MUTED, GRID = '#213442', '#657684', '#e6ebef'
PALETTE = {'A': BLUE, 'B': GOLD, 'C': TEAL}


def _figure(figsize=(12.8, 5.8)):
    fig = plt.figure(figsize=figsize, facecolor='white')
    return fig


def _ax_style(ax, *, xlabel=None, ylabel=None):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['bottom', 'left']].set_color('#b5c2c9')
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=GRID, lw=.8)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK, fontsize=10)


def _finish(fig, title, note, *, layout=None):
    fig.text(.065, .955, title, fontsize=17, fontweight='bold', color=INK, ha='left', va='top')
    fig.text(.065, .06, note, fontsize=8.6, color=MUTED, ha='left', va='center', linespacing=1.45)
    fig.subplots_adjust(**(layout or dict(left=.075, right=.96, bottom=.205, top=.81, wspace=.28, hspace=.3)))
    buf = BytesIO()
    fig.savefig(buf, format='svg', metadata={'Date': None, 'Title': title,
                                            'Description': note, 'Creator': 'Systematic Research Lab'})
    plt.close(fig)
    return b'\n'.join(line.rstrip() for line in buf.getvalue().splitlines()) + b'\n'


def _search(data):
    fig = _figure((13.4, 6.05))
    gs = fig.add_gridspec(1, 2, width_ratios=[.76, 1.5])
    ax = fig.add_subplot(gs[0, 0])
    hax = fig.add_subplot(gs[0, 1])
    syms = ['DE30X', 'JP225X', 'UK100X']
    vals = [100 * data['search']['symbols'][s]['positive_price_r'] / data['search']['symbols'][s]['valid'] for s in syms]
    bars = ax.barh(syms[::-1], vals[::-1], color=[RED, GOLD, BLUE], height=.48)
    ax.set_xlim(0, 55)
    ax.set_title('Price-positive cells, not validation', loc='left', fontsize=11, color=INK, pad=12)
    _ax_style(ax, xlabel='% of scientifically valid cells')
    ax.grid(axis='x', color=GRID, lw=.8)
    ax.grid(axis='y', visible=False)
    for bar, s, v in zip(bars, syms[::-1], vals[::-1]):
        c = data['search']['symbols'][s]
        ax.text(v + .8, bar.get_y() + bar.get_height()/2,
                f"{c['positive_price_r']}/{c['valid']} · {v:.1f}%", color=INK, va='center', fontsize=10)
    heat = np.asarray([[
        float('nan') if v is None else v for v in data['search']['de30_long_mean_r_by_15min_anchor'][str(m)]
    ] for m in [5, 15, 30, 60]], dtype=float)
    cmap = plt.get_cmap('RdBu').copy()
    cmap.set_bad('#d5dce2')
    # Vector cells avoid OS-dependent PNG encoding inside the canonical SVG.
    im = hax.pcolormesh(np.arange(97)-.5, np.arange(5)-.5, heat,
                        cmap=cmap, vmin=-.25, vmax=.25, shading='flat', rasterized=False)
    hax.set_xlim(-.5, 95.5)
    hax.set_ylim(-.5, 3.5)
    hax.set_yticks(range(4), ['OR5', 'OR15', 'OR30', 'OR60'])
    hax.set_xticks([i*4 for i in range(24)][::3], [f'{i:02d}:00' for i in range(0,24,3)])
    hax.set_xlabel('DE30X local start, Europe/Berlin · each column = 15 min', fontsize=10, color=INK)
    hax.set_title('DE30 LONG discovery surface · mean R/trade', loc='left', fontsize=11, color=INK, pad=12)
    hax.tick_params(colors=MUTED, labelsize=9)
    for i in range(0, 97, 4):
        hax.axvline(i-.5, color='white', alpha=.25, lw=.45)
    cbar=fig.colorbar(im, ax=hax, fraction=.045, pad=.015)
    cbar.solids.set_rasterized(False)
    cbar.set_label('R/trade, clipped to ±0.25R', color=INK, fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    note=('3 × 96 quarter-hour anchors × 4 durations × 3 directions = 3,456 searched cells · 3,338 valid · 118 invalid.\n'
          'Only DE30 formed supported price-only regions; none survived a hypothetical +0.05R/trade regional stress. Entire surface is discovery.')
    return _finish(fig,'01  |  Search the whole clock, then ask whether any region is stable',note)


def _portfolio(data):
    fig=_figure((13.4,6.6))
    gs=fig.add_gridspec(2,1,height_ratios=[1.45,1],hspace=.5)
    a=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1])
    colors={'LONG':BLUE,'SHORT':RED,'BOTH':TEAL}
    for y,k in zip([2,1,0],'ABC'):
        for row in data['portfolio'][k]['sleeves']:
            hh,mm=map(int,row['time'].split(':'));start=hh+mm/60;duration=row['or']/60
            a.broken_barh([(start,duration)],(y-.25,.5),facecolors=colors[row['side']],alpha=.85)
        a.text(15.42,y,f"{len(data['portfolio'][k]['sleeves'])} sleeves",color=MUTED,fontsize=9,va='center')
    a.set_xlim(7.5,16.3)
    a.set_yticks([2,1,0],['A | core','B | + OR5','C | broad'])
    a.set_ylim(-.5, 3.0)
    a.set_xticks(np.arange(8,16,1),[f'{i:02d}:00' for i in range(8,16)])
    a.set_xlabel('Berlin local opening-range clock; blocks show OR observation, not position lifetime',fontsize=10,color=INK)
    a.set_title('Frozen components, one shared pending-or-position slot within each portfolio',loc='left',fontsize=11,color=INK,pad=12)
    _ax_style(a)
    a.grid(axis='x',color=GRID,lw=.7)
    from matplotlib.patches import Patch
    a.legend(handles=[Patch(facecolor=c,label=n) for n,c in colors.items()],loc='upper left',ncol=3,frameon=False,fontsize=9,bbox_to_anchor=(0,1.02))
    ks=list('ABC');values=[data['portfolio'][k]['discovery']['price_r'] for k in ks];n=[data['portfolio'][k]['discovery']['trades'] for k in ks]
    bars=b.bar(ks,values,color=[PALETTE[k] for k in ks],width=.48)
    _ax_style(b,ylabel='Gross price R, discovery')
    b.set_ylim(0,max(values)*1.27)
    b.set_title('After one-position synchronized replay, not summed independent cells',loc='left',fontsize=11,color=INK,pad=12)
    for bar,k,v,count in zip(bars,ks,values,n):
        b.text(bar.get_x()+bar.get_width()/2,v+7,f'+{v:.1f}R\n{count:,} fills',ha='center',va='bottom',fontsize=10,color=INK)
    note=('Europe/Berlin clocks include DST. A/B/C each run separately; each portfolio shares ONE position/pending-order slot.\n'
          'Discovery 2020–23 was inspected before portfolio selection. B contains a post-selected OR5 SHORT; these bars do not imply net profitability.')
    return _finish(fig,'02  |  Turn a discovery surface into three fixed trading portfolios',note)


def _cumulative(data):
    fig=_figure((13.6,6.5));axes=fig.subplots(1,2)
    for ax,phase in zip(axes,['discovery','oos']):
        qs=[v[0] for v in data['portfolio']['A'][phase]['quarterly_cumulative_r']]
        x=np.arange(len(qs)+1)
        for k in 'ABC':
            series=data['portfolio'][k][phase]['quarterly_cumulative_r'];assert [p[0] for p in series]==qs
            yy=np.array([0.0] + [p[1] for p in series])
            ax.plot(x,yy,marker=['o','s','^'][ord(k)-ord('A')],ms=3.2,lw=2.1,color=PALETTE[k],label=f'Portfolio {k}: {yy[-1]:+.1f}R')
        ax.axhline(0,color=MUTED,lw=.95,ls='--')
        ax.set_xlim(-.35,len(qs)+.35)
        tick=list(range(0,len(qs),max(1,len(qs)//5)));tick.append(len(qs)-1);tick=sorted(set(tick))
        ax.set_xticks([0] + [i+1 for i in tick[1:]],
                      [('Feb 2020' if phase=='discovery' else 'Jan 2024')] +
                      ["'" + qs[i][2:] for i in tick[1:]])
        _ax_style(ax,ylabel='Cumulative gross price R (reset at start)')
        ax.set_title('Discovery | Feb 2020 to Dec 2023' if phase=='discovery' else 'OOS | Jan 2024 to Aug 2026*',loc='left',fontsize=12,color=INK,pad=12)
        ax.legend(loc='upper left',frameon=False,fontsize=9)
        low, high = ax.get_ylim()
        ax.set_ylim(low, high + (high-low)*.30)
        if phase=='oos':
            inds=[i+1 for i,q in enumerate(qs) if q.startswith('2025')]
            ax.axvspan(min(inds)-.45,max(inds)+.45,color=RED,alpha=.07,zorder=-1)
            ax.text((min(inds)+max(inds))/2,ax.get_ylim()[0]+(ax.get_ylim()[1]-ax.get_ylim()[0])*.08,'2025',color=RED,fontsize=9,ha='center')
    note=('Quarter-end snapshots, plus final burnoff totals; straight segments omit intraperiod drawdowns. Each sample starts at zero.\n'
          'Discovery and OOS spans differ, so raw total-R heights are not annualized performance. 2026* has Jul signal cutoff and Aug burnoff only.')
    return _finish(fig,'03  |  Discovery and later-period cumulative gross price R',note)


def _economics(data):
    fig=_figure((13.4,6.4));a,b=fig.subplots(1,2)
    ks=list('ABC');xx=np.arange(3)
    disc=np.array([data['portfolio'][k]['discovery']['eur'] for k in ks]);oos=np.array([data['portfolio'][k]['oos']['eur'] for k in ks])
    a.bar(xx-.18,disc,width=.35,color=BLUE,label='Discovery gross EUR')
    a.bar(xx+.18,oos,width=.35,color=RED,label='OOS gross EUR')
    a.set_xticks(xx,[f'Portfolio {k}' for k in ks]);a.axhline(0,color=INK,lw=1)
    a.set_ylim(min(oos)-65, max(disc)+55)
    a.set_title('Fixed volume gross EUR, before extra charges',loc='left',fontsize=11,color=INK,pad=12)
    _ax_style(a,ylabel='EUR at 0.07 lots')
    a.legend(frameon=False,fontsize=9)
    for i in range(3):
        a.text(i-.18,disc[i]+12,f'{disc[i]:+.0f}',ha='center',fontsize=9,color=INK)
        a.text(i+.18,oos[i]-12,f'{oos[i]:+.0f}',ha='center',va='top',fontsize=9,color=RED)
    width=.24
    for j,(scenario,color) in enumerate([('eur',BLUE),('s1_eur',GOLD),('s2_eur',RED)]):
        vals=[data['portfolio'][k]['oos'][scenario] for k in ks]
        b.bar(xx+(j-1)*width,vals,width=width,color=color,label=['S0 recorded gross','S1 fee proxy','S2 conservative stress'][j])
    b.axhline(0,color=INK,lw=1);b.set_xticks(xx,[f'Portfolio {k}' for k in ks])
    _ax_style(b,ylabel='OOS EUR at 0.07 lots')
    b.set_title('Every frozen OOS economic scenario is negative',loc='left',fontsize=11,color=INK,pad=12)
    b.legend(frameon=False,fontsize=8.8,loc='lower left')
    note=('Same fixed 0.07-lot size; returns are from historical simulation, not verified broker cash postings.\n'
          'S1 uses a current commission proxy; S2 includes financing and adverse-fill stress. Spread is already embedded in source Bid/Ask.')
    return _finish(fig,'04  |  All three portfolios failed later-period fixed-lot economics',note)


def _forensic(data):
    years=data['forensic']['A_exit_year'];ys=[str(v['year'])+('*' if v['year']==2026 else '') for v in years];xx=np.arange(3)
    fig=_figure((13.3,6.4));a,b=fig.subplots(1,2)
    mid=np.array([v['signed_midquote_r'] for v in years]);wedge=np.array([v['embedded_spread_r'] for v in years]);gross=np.array([v['gross_r'] for v in years])
    a.bar(xx-.15,mid,width=.30,color=BLUE,label='Signed midquote R')
    a.bar(xx+.15,-wedge,width=.30,color=RED,label='Embedded Bid/Ask wedge')
    # Explicit vertices avoid platform rounding of a rotated square near zero.
    diamond = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 1)]
    a.plot(xx,gross,ls='',marker=diamond,color=INK,ms=8.5,label='Realized gross R')
    a.set_xticks(xx,ys);a.axhline(0,color=INK,lw=1)
    a.set_title('A: 2025 midquote movement was negative too',loc='left',fontsize=11,color=INK,pad=11)
    _ax_style(a,ylabel='Trade-level aggregate R by exit year')
    a.legend(frameon=False,fontsize=8.8)
    b.plot(xx,[v['mfe05_pct'] for v in years],marker='o',lw=2.25,color=GOLD,label='Ever reached +0.5R')
    b.plot(xx,[v['win_rate_pct'] for v in years],marker='s',lw=2.25,color=BLUE,label='Won at exit')
    b.plot(xx,[v['conversion_pct'] for v in years],marker='^',lw=2.25,color=TEAL,label='Won given +0.5R')
    b.set_xticks(xx,ys);b.set_ylim(20,85)
    b.set_title('A: initial favourable movement converted less often',loc='left',fontsize=11,color=INK,pad=11)
    _ax_style(b,ylabel='Percent (conditional denominator in legend)')
    b.legend(frameon=False,fontsize=8.7,loc='lower left')
    note=('Post-OOS descriptive diagnostics only, conditional on actually executed trades. The spread wedge is an accounting identity.\n'
          'Won given +0.5R uses only trades that reached +0.5R. 2026* includes Jan–Jul origins and Aug burnoff. No causal claim.')
    return _finish(fig,'05  |  Post-OOS observations: spread and price follow-through',note)


def _cross_market(data):
    cross = data['cross_market_discovery']
    fig = _figure((14.2, 8.4))
    axes = fig.subplots(2, 3)
    cmap = plt.get_cmap('RdBu').copy()
    cmap.set_bad('#d5dce2')
    norm = TwoSlopeNorm(vmin=-.70, vcenter=0, vmax=.25)
    markets = ['JP225X', 'UK100X']
    directions = ['BOTH', 'LONG', 'SHORT']
    for row, symbol in enumerate(markets):
        market = cross['markets'][symbol]
        for col, direction in enumerate(directions):
            ax = axes[row, col]
            grid = market['grid'][direction]
            if set(grid) != {'5', '15', '30', '60'} or any(len(v) != 96 for v in grid.values()):
                raise ValueError('cross-market grid must contain all four durations and 96 anchors')
            values = np.array([[np.nan if v is None else v for v in grid[str(m)]]
                               for m in [5, 15, 30, 60]])
            mesh = ax.pcolormesh(np.arange(97)-.5, np.arange(5)-.5, values,
                                 cmap=cmap, norm=norm, shading='flat', rasterized=False)
            ax.set_xlim(-.5, 95.5)
            ax.set_ylim(-.5, 3.5)
            ax.set_yticks(range(4), ['OR5', 'OR15', 'OR30', 'OR60'])
            ax.set_xticks([0, 24, 48, 72, 95], ['00:00', '06:00', '12:00', '18:00', '23:45'])
            ax.tick_params(colors=MUTED, labelsize=9, length=0, pad=5)
            ax.set_title(f'{symbol} | {direction}', loc='left', fontsize=11, color=INK, pad=11)
            ax.set_xlabel(market['timezone'] + ' local start', color=INK, fontsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)
    summary = '  |  '.join(
        f"{s}: {cross['markets'][s]['positive_price_R_cells']}/{cross['markets'][s]['valid']:,} price-positive valid cells; "
        f"{cross['markets'][s]['qualifying_regions']} supported regions" for s in markets)
    fig.text(.065, .89, summary, color=MUTED, fontsize=10, ha='left')
    color_ax = fig.add_axes([.28, .17, .46, .023])
    bar = fig.colorbar(mesh, cax=color_ax, orientation='horizontal', extend='both',
                      ticks=[-.7, -.4, -.2, 0, .1, .25])
    bar.solids.set_rasterized(False)
    bar.ax.tick_params(labelsize=9, colors=MUTED)
    bar.set_label('Mean gross price R/trade; display clipped to [-0.70, +0.25]', fontsize=10, color=INK)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor='#d5dce2', label='Grey = undefined mean; zero is white')],
               loc='center', bbox_to_anchor=(.51, .225), frameon=False, fontsize=9)
    note = ('Spent discovery: Feb 2020-Nov 2023 signal origins; Dec 2023 burnoff. Each panel: 96 local anchors x four OR lengths.\n'
            'Grey includes 95 scientific-invalid cells and two valid JP zero-trade cells. Values are price R, not broker-net money.\n'
            'No passing six-cell neighbourhood on either market; this rejects advancement of the tested ORB mechanism only.')
    return _finish(fig, '06  |  Cross-market falsification: Japan and UK', note,
                   layout=dict(left=.065, right=.97, bottom=.31, top=.81, wspace=.22, hspace=.55))


def orbindex_artifacts(data: dict) -> dict[str, bytes]:
    if data.get('scope') != 'PUBLIC_REPORTED_HISTORICAL_AGGREGATES_PRIVATE_BACKTEST_NOT_REPLAYABLE':
        raise ValueError('missing public data/scope declaration')
    if set(data['portfolio']) != {'A','B','C'}:
        raise ValueError('expected exactly three frozen portfolios')
    rc={'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'srl-orbindex-v1',
        'text.color':INK,'axes.labelcolor':INK, 'axes.titlesize':11,'figure.dpi':100}
    with plt.rc_context(rc):
        return {
          'figures/orbindex-search.svg':_search(data),
          'figures/orbindex-portfolios.svg':_portfolio(data),
          'figures/orbindex-curves.svg':_cumulative(data),
          'figures/orbindex-economics.svg':_economics(data),
          'figures/orbindex-forensics.svg':_forensic(data),
          'figures/orbindex-jp-uk-heatmaps.svg':_cross_market(data),
        }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'data/orbindex-public.json')
    parser.add_argument('--check',action='store_true',help='Compare checked-in rendered SVG bytes')
    parser.add_argument('--write',action='store_true',help='Write canonical SVGs from reviewed aggregate inputs')
    args=parser.parse_args()
    figures=orbindex_artifacts(json.loads(args.input.read_text(encoding='utf-8')))
    bad=[]
    for filename,data in figures.items():
        path=ROOT/filename
        if args.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        elif not path.is_file() or path.read_bytes()!=data:
            bad.append(filename)
    if bad:
        print('ORBINDEX figure mismatch:',bad)
        return 1
    print('ORBINDEX figure render verified:',len(figures))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
