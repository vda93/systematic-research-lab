"""Transparent arithmetic on published aggregates, without inventing observations."""

import math
from .historical import validate_records


def _finite(value):
    if not math.isfinite(value):
        raise ValueError('derived arithmetic must remain finite')
    return round(value,12)


def derive_diagnostics(data):
    """Return descriptive identities only; no new inference or promotion decisions."""
    validate_records(data)
    records={r['id']:r for r in data['records']}
    rows={k:r['metrics'] for k,r in records.items()}
    m,d,r,a,b,n=[rows[k] for k in ('M3','D2','D7','O2_A','O2_B','N1')]
    if r['requested_risk_pct']<=0 or m['canonical_maxdd_r']<=0 or m['canonical_trades']<=0:
        raise ValueError('ratio denominators must be positive')
    if records['O2_A']['period_end_exclusive']>records['O2_B']['period_start']:
        raise ValueError('do not pool overlapping OOS eligibility windows')
    if any(records[k]['sample_type']!='historical_oos_spent' for k in ('O2_A','O2_B')):
        raise ValueError('OOS descriptive pooling requires explicit spent sample roles')
    if any(records[k].get('return_basis') != 'price_space' for k in ('O2_A','O2_B')):
        raise ValueError('the two OOS records must share explicit price-space accounting')
    result={
        'scope':'DESCRIPTIVE_ARITHMETIC_ON_REPORTED_AGGREGATES',
        'input_precision_note':'Arithmetic uses rounded published inputs. The derived 46.8900R date contribution differs from the source full-precision reported 46.8901R; it is not a trade-exact reconciliation.',
        'momentum':{
            'recent_no_trail_minus_canonical_r':_finite(m['no_trail_total_r']-m['canonical_total_r']),
            'drawdown_multiple':_finite(m['no_trail_maxdd_r']/m['canonical_maxdd_r']),
            'retained_trade_count_pct':_finite(100*m['no_trail_trades']/m['canonical_trades']),
            'era_no_trail_minus_canonical_r':{era:_finite(rows['M4_'+era]['no_trail_total_r']-rows['M4_'+era]['canonical_total_r']) for era in ('EARLY','MID','RECENT')},
            'primary_paired_interval':'NOT_ESTIMABLE_IN_SOURCE',
        },
        'de30':{
            'removed_top10_date_contribution_r':_finite(d['total_r']-d['remove_top10_date_total_r']),
            'risk_fill_pct_of_request':_finite(100*r['after_median_actual_risk_pct']/r['requested_risk_pct']),
        },
        'orb':{
            'pooled_oos_r':_finite(a['total_r']+b['total_r']),
            'standalone_b_total_positive':b['total_r']>0,
            'interpretation':'Descriptive total cannot override the frozen standalone OOS-B failure.',
        },
        'nowick':{'primary_ci_includes_zero':n['ci_low']<=0<=n['ci_high'],
                  'primary_interval_width_pp':_finite(n['ci_high']-n['ci_low'])},
        'limits':'No daily paths, new standard errors, independent replay or deployment conclusions can be recovered from these aggregates.',
    }
    return result
