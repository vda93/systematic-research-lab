"""Validate and present reported historical aggregates; never invent trade paths."""

from datetime import date
import math
import re


SAMPLE_TYPES = {'development', 'historical_oos_spent', 'engineering_replay',
                'historical_simulation', 'retrospective_event_study', 'discovery_reversal'}


def validate_records(data: dict) -> None:
    if not isinstance(data, dict) or data.get('scope') != 'HISTORICAL_REPORTED_AGGREGATES':
        raise ValueError('historical aggregate scope must be explicit')
    records = data.get('records')
    if not isinstance(records, list) or not records:
        raise ValueError('nonempty historical records required')
    seen = set()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError('record must be a mapping')
        for field in ('id', 'program', 'source_record', 'limitations'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('record identity and source context required')
        if not re.fullmatch(r'[A-Z0-9_]+', row['id']) or row['id'] in seen:
            raise ValueError('record IDs must be safe and unique')
        seen.add(row['id'])
        if row.get('sample_type') not in SAMPLE_TYPES:
            raise ValueError('unsupported sample classification')
        try:
            start, end = [date.fromisoformat(row[field]) for field in
                          ('period_start', 'period_end_exclusive')]
            if start >= end or start.isoformat() != row['period_start'] or end.isoformat() != row['period_end_exclusive']:
                raise ValueError('invalid historical period')
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('canonical bounded sample dates required') from exc
        metrics = row.get('metrics')
        if not isinstance(metrics, dict) or not metrics:
            raise ValueError('reported metrics required')
        for key, value in metrics.items():
            if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9_]+', key):
                raise ValueError('safe metric names required')
            try:
                finite = type(value) in (int, float) and math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError('all metrics must be finite numeric values')
            if key in {'trades', 'events', 'controls_per_event', 'paths', 'block_days'} or key.endswith(('_trades', '_events', '_cells', '_opportunities', '_repetitions')):
                if type(value) is not int or value < 0:
                    raise ValueError('counts must be nonnegative integers')
            if key.endswith('_p') and not 0 <= value <= 1:
                raise ValueError('reported p-values must be in [0, 1]')
            if key.endswith('_risk_pct') or key.endswith(('_pass_pct', '_breach_pct')):
                if not 0 <= value <= 100:
                    raise ValueError('reported risk and path percentages must be in [0, 100]')
            if key.endswith(('pf_r', 'pf_money', 'maxdd_r', 'abs_tolerance')) and value < 0:
                raise ValueError('profit factors, drawdown magnitudes and tolerances must be nonnegative')
        if any(key in metrics for key in ('ci_low', 'ci_high')):
            if not all(key in metrics for key in ('estimate', 'ci_low', 'ci_high')):
                raise ValueError('estimate and both interval bounds required')
            if metrics['ci_low'] > metrics['ci_high']:
                raise ValueError('inconsistent interval bounds')


def render_tables(data: dict) -> str:
    validate_records(data)
    lines = ['# Published historical aggregate tables', '',
             'Generated from [historical-results.json](../data/historical-results.json). '
             'These are reported private-study aggregates, not a public backtest replay. '
             'R means normalized initial planned risk; price-space R and account returns are distinct.', '']
    for row in data['records']:
        lines += [f"## {row['id']}", '', f"**{row['program']}** · {row['source_record']}", '',
                  f"Sample: `{row['sample_type']}`, [{row['period_start']}, {row['period_end_exclusive']}).", '',
                  '| Metric | Reported value |', '| --- | ---: |']
        lines.extend(f'| {key} | {value} |' for key, value in row['metrics'].items())
        lines += ['', row['limitations'], '']
    return '\n'.join(lines).rstrip() + '\n'
