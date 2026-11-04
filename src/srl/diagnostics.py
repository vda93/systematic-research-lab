"""Transparent arithmetic on retained ORB and NOWICK published aggregates."""

import math
from .historical import validate_records


def _finite(value):
    if not math.isfinite(value):
        raise ValueError('derived arithmetic must remain finite')
    return round(value, 12)


def derive_diagnostics(data):
    """Only descriptive identities from retained records; no new inference."""
    validate_records(data)
    records = {row['id']: row for row in data['records']}
    a, b, n = [records[key]['metrics'] for key in ('O2_A', 'O2_B', 'N1')]
    if records['O2_A']['period_end_exclusive'] > records['O2_B']['period_start']:
        raise ValueError('do not pool overlapping OOS eligibility windows')
    if any(records[key]['sample_type'] != 'historical_oos_spent' for key in ('O2_A', 'O2_B')):
        raise ValueError('OOS descriptive pooling requires explicitly spent roles')
    if any(records[key].get('return_basis') != 'price_space' for key in ('O2_A', 'O2_B')):
        raise ValueError('pooled ORB outcomes must share price-space accounting')
    return {
        'scope': 'DESCRIPTIVE_ARITHMETIC_ON_REPORTED_AGGREGATES',
        'orb': {
            'pooled_oos_r': _finite(a['total_r'] + b['total_r']),
            'standalone_b_total_positive': b['total_r'] > 0,
            'interpretation': 'Descriptive total cannot override the frozen standalone OOS-B failure.',
        },
        'nowick': {
            'primary_ci_includes_zero': n['ci_low'] <= 0 <= n['ci_high'],
            'primary_interval_width_pp': _finite(n['ci_high'] - n['ci_low']),
        },
        'limits': 'No daily paths, new standard errors, independent replay or deployment conclusions can be recovered from these aggregates.',
    }
