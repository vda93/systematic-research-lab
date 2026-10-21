"""All-planned-day aggregation of completed BBO quote-cost replay reports.

Inputs are caller-verified full-day reports and PRIVATE sample vectors. This
module verifies their numerical/count consistency; it neither replays clocks nor
certifies publication, rights, implementation freezes or source integrity.
"""
from __future__ import annotations

import math
from typing import Any, Mapping, Sequence, cast

from srl.bbo_statistics import distribution_summary, equal_day_inference, weighted_penalty_quantiles

_GROUPS = tuple(f'{label}/{delay}{side}' for label in ('shock','normal')
                for delay in (300,550,1050) for side in ('','/buy','/sell'))
_COUNTS = ('eligible','paired','missing_baseline','missing_delayed','both_missing',
           'baseline_depth_fail','delayed_depth_fail','either_depth_fail','sufficient_depth_both')
_COMPONENTS = ('price_saving','spread_saving','mid_drift_saving','fee_slope')
_GRID = tuple(f'{fee:g}/{slip:g}' for fee in (0.,5.,10.) for slip in (0.,.5,1.))
_YEARS = {'development':2023,'validation':2024,'final':2025}
_TOLERANCE = 1e-8


def _count(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError('counts must be nonnegative built-in integers, excluding bool')
    return value


def _finite(value: Any) -> float:
    if type(value) not in (int,float):
        raise ValueError('finite numeric statistics required, excluding bool')
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError('statistic exceeds finite float range') from exc
    if not math.isfinite(result):
        raise ValueError('nonfinite statistic')
    return result


def _sum(values: Sequence[float]) -> float:
    try:
        return _finite(math.fsum(values))
    except OverflowError as exc:
        raise ValueError('arithmetic exceeds finite float range') from exc


def _same(actual: Any, expected: float | None) -> None:
    if expected is None:
        if actual is not None:
            raise ValueError('empty statistic must be None')
    elif not math.isclose(_finite(actual),expected,rel_tol=0.,abs_tol=_TOLERANCE):
        raise ValueError('coarse statistics disagree with samples or accounting')


def _average(values: Sequence[float]) -> float | None:
    result = distribution_summary(values)['mean']
    return None if result is None else _finite(result)


def _empty_group() -> dict[str,Any]:
    return dict(distribution_summary([]), **dict.fromkeys(_COUNTS,0),
                mean_saving_bps=None,mean_components=dict.fromkeys(_COMPONENTS),
                mean_cost_grid_bps=dict.fromkeys(_GRID),post_outcome_depth_subset=distribution_summary([]))


def _group(report: Mapping[str,Any], samples: Sequence[float]) -> dict[str,Any]:
    summary = distribution_summary(samples)
    counts = {name:_count(report[name]) for name in _COUNTS}
    eligible,paired = counts['eligible'],counts['paired']
    if _count(report['count']) != paired or paired != len(samples):
        raise ValueError('paired counts and private samples disagree')
    baseline,delayed,both = (counts[name] for name in ('missing_baseline','missing_delayed','both_missing'))
    if both>min(baseline,delayed) or paired != eligible-baseline-delayed+both or not 0<=paired<=eligible:
        raise ValueError('missing-target union does not reconcile')
    bad_base,bad_delay,bad_either,sufficient = (counts[name] for name in
        ('baseline_depth_fail','delayed_depth_fail','either_depth_fail','sufficient_depth_both'))
    if (bad_base>eligible-baseline or bad_delay>eligible-delayed
        or not max(bad_base,bad_delay)<=bad_either<=bad_base+bad_delay
        or sufficient>paired or not 0<=bad_either-(paired-sufficient)<=eligible-paired-both):
        raise ValueError('displayed-depth counts do not reconcile')
    mean = None if summary['mean'] is None else _finite(summary['mean'])
    for name in ('mean','mean_saving_bps'):
        _same(report[name],mean)
    for name in ('sample_sd','median_saving','worst_penalty'):
        value = summary[name]
        _same(report[name],None if value is None else _finite(value))
    if set(report['penalty_quantiles']) != {'50','90','95','99'}:
        raise ValueError('all four penalty quantiles required')
    for name,value in cast(Mapping[str,float|None],summary['penalty_quantiles']).items():
        _same(report['penalty_quantiles'][name],value)
    if set(report['mean_components']) != set(_COMPONENTS) or set(report['mean_cost_grid_bps']) != set(_GRID):
        raise ValueError('all decomposition components and nine grid cells required')
    components = {name:None if mean is None else _finite(report['mean_components'][name]) for name in _COMPONENTS}
    grid: dict[str,float|None] = {}
    for name in _COMPONENTS:
        _same(report['mean_components'][name],components[name])
    for key in _GRID:
        if mean is None:
            expected = None
        else:
            fee,slip = map(float,key.split('/'))
            expected = _sum([_finite(components['price_saving']),fee*_finite(components['fee_slope']),-slip])
        _same(report['mean_cost_grid_bps'][key],expected)
        grid[key] = expected
    if mean is not None:
        _same(components['price_saving'],_sum([_finite(components['spread_saving']),_finite(components['mid_drift_saving'])]))
        _same(grid['5/0.5'],mean)
    subset = report['post_outcome_depth_subset']
    if _count(subset['count']) != sufficient:
        raise ValueError('depth-conditioned subset count differs from sufficient-depth count')
    safe_subset: dict[str,Any] = {'count':sufficient}
    for name in ('mean','sample_sd','median_saving','worst_penalty'):
        required = sufficient>0 and (name!='sample_sd' or sufficient>1)
        value = _finite(subset[name]) if required else None
        _same(subset[name],value)
        if name=='sample_sd' and value is not None and value<0:
            raise ValueError('sample SD cannot be negative')
        safe_subset[name] = value
    return dict(summary,**counts,mean_saving_bps=mean,mean_components=components,
                mean_cost_grid_bps=grid,post_outcome_depth_subset=safe_subset)


def _day(day: str, report: Mapping[str,Any], samples: Mapping[str,Sequence[float]]) -> dict[str,Any]:
    if report.get('status','COMPLETE')!='COMPLETE' or report.get('day',day)!=day:
        raise ValueError('only completed matching-day coarse reports may be aggregated')
    scheduled,eligible,shock,normal = (_count(report[name]) for name in
        ('scheduled_intents','eligible_intents','shock_intents','normal_intents'))
    exclusions = {str(reason):_count(value) for reason,value in report['exclusions'].items()}
    if scheduled!=eligible+sum(exclusions.values()) or eligible!=shock+normal:
        raise ValueError('scheduled/eligible/label/exclusion counts do not reconcile')
    coverage = eligible/scheduled if scheduled else 0.
    _same(report['eligible_fraction'],coverage)
    sides = {name:_count(report['side_counts'].get(name,0)) for name in
             ('scheduled','buy_scheduled','sell_scheduled','buy_eligible','sell_eligible')}
    if (sides['scheduled']!=scheduled or sides['buy_scheduled']+sides['sell_scheduled']!=scheduled
        or sides['buy_eligible']+sides['sell_eligible']!=eligible
        or any(sides[f'{side}_eligible']>sides[f'{side}_scheduled'] for side in ('buy','sell'))):
        raise ValueError('side totals do not reconcile')
    if set(report['groups'])-set(_GROUPS) or set(samples)-set(_GROUPS):
        raise ValueError('unexpected group; fixed label/latency/side groups only')
    groups = {}
    for key in _GROUPS:
        raw = report['groups'].get(key)
        vector = samples.get(key,())
        if raw is None:
            if len(vector):
                raise ValueError('samples lack a matching group report')
            groups[key] = _empty_group()
        else:
            groups[key] = _group(raw,vector)
    for delay in (300,550,1050):
        for label,label_count in (('shock',shock),('normal',normal)):
            key = f'{label}/{delay}'
            pooled,buy,sell = (groups[key+suffix] for suffix in ('','/buy','/sell'))
            if pooled['eligible']!=label_count:
                raise ValueError('label/latency group omitted eligible intents')
            for name in _COUNTS:
                if pooled[name]!=buy[name]+sell[name]:
                    raise ValueError('pooled and side group counts disagree')
            if pooled['paired']:
                weighted = _sum([g['paired']*_finite(g['mean_saving_bps']) for g in (buy,sell) if g['paired']])/pooled['paired']
                _same(pooled['mean_saving_bps'],weighted)
        for side in ('buy','sell'):
            if sum(groups[f'{label}/{delay}/{side}']['eligible'] for label in ('shock','normal'))!=sides[f'{side}_eligible']:
                raise ValueError('group-side eligibility disagrees with day totals')
    primary = groups['shock/550']
    support = dict(minimum_100_shocks=shock>=100,intent_coverage_95pct=100*eligible>=95*scheduled,
                   zero_missing_primary_targets=primary['paired']==shock,
                   future_depth_99pct=shock>0 and 100*primary['sufficient_depth_both']>=99*shock)
    return dict(day=day,status='COMPLETE',scheduled_intents=scheduled,eligible_intents=eligible,
                shock_intents=shock,normal_intents=normal,exclusions=exclusions,side_counts=sides,
                eligible_fraction=coverage,paired_shocks=primary['paired'],mean_saving_bps=primary['mean_saving_bps'],
                support=support,groups=groups)


def _aggregate_group(key: str, planned: Sequence[str], completed: Mapping[str,dict[str,Any]],
                     samples: Mapping[str,Mapping[str,Sequence[float]]]) -> dict[str,Any]:
    daily = [{'day':day,**completed[day]['groups'][key]} for day in planned if day in completed]
    contributing = [row for row in daily if row['paired']]
    vectors = [samples.get(day,{}).get(key,()) if day in completed else () for day in planned]
    means = [_finite(row['mean_saving_bps']) for row in contributing]
    components = {name:_average([_finite(row['mean_components'][name]) for row in contributing]) for name in _COMPONENTS}
    components['fee_saving_bps'] = 5*_finite(components['fee_slope']) if contributing else None
    components['slippage_saving_bps'] = -.5 if contributing else None
    subset = [row for row in daily if row['post_outcome_depth_subset']['count']]
    worst_day = min(contributing,key=lambda row:(row['mean_saving_bps'],row['day'])) if contributing else None
    return dict(paired_intents=sum(row['paired'] for row in daily),contributing_days=len(contributing),
                daily=[dict(day=row['day'],paired=row['paired'],mean=row['mean_saving_bps'],
                            median_saving=row['median_saving'],worst_penalty=row['worst_penalty']) for row in daily],
                equal_day_summary=distribution_summary(means),
                equal_day_penalty_quantiles=weighted_penalty_quantiles(vectors),
                worst_day=None if worst_day is None else dict(day=worst_day['day'],mean=worst_day['mean_saving_bps']),
                worst_observed_penalty=max((_finite(row['worst_penalty']) for row in contributing),default=None),
                mean_cost_grid_bps={cell:_average([_finite(row['mean_cost_grid_bps'][cell]) for row in contributing]) for cell in _GRID},
                mean_components=components,
                post_outcome_depth_subset=dict(
                    status='DESCRIPTIVE_POST_OUTCOME_CONDITIONED',
                    count=sum(row['post_outcome_depth_subset']['count'] for row in daily),
                    contributing_days=len(subset),
                    equal_day_summary=distribution_summary([_finite(row['post_outcome_depth_subset']['mean']) for row in subset]),
                    daily=[dict(day=row['day'],**row['post_outcome_depth_subset']) for row in daily],
                    pooled_penalty_quantiles=None,
                    quantile_reason='PRIVATE_SUBSET_SAMPLES_NOT_RETAINED_CDF_NOT_RECONSTRUCTED'))


def aggregate_stage(planned_days: Sequence[str], reports: Mapping[str,Mapping[str,Any]],
                    private_samples: Mapping[str,Mapping[str,Sequence[float]]], *, stage: str,
                    missing_reasons: Mapping[str,str] | None = None,
                    external_gates_passed: bool = False) -> dict[str,Any]:
    """Aggregate the fixed twelve planned days, retaining every missing day.

    Full-day replay completeness and integrity are caller prerequisites; this API
    independently checks supplied counts, finite numbers, private sample summaries
    and accounting. `external_gates_passed` is an explicit caller assertion of the
    separate rights/integrity/stage/publication gates, never inferred here. The
    returned coarse candidate still requires non-reconstructibility review before
    publication. Private vectors and arbitrary input fields are never forwarded.
    """
    if stage not in _YEARS or type(external_gates_passed) is not bool:
        raise ValueError('known stage and explicit boolean external gate required')
    planned = [f'{_YEARS[stage]}-{month:02d}-01' for month in range(1,13)]
    if list(planned_days)!=planned:
        raise ValueError('exact chronological twelve frozen monthly first days required')
    missing_reasons = {} if missing_reasons is None else missing_reasons
    if any(set(mapping)-set(planned) for mapping in (reports,private_samples,missing_reasons)):
        raise ValueError('unplanned day in inputs')
    if set(private_samples)-set(reports):
        raise ValueError('private samples require a completed day report')
    if any(not isinstance(reason,str) or not reason for reason in missing_reasons.values()):
        raise ValueError('missing reasons must be nonempty strings')
    completed = {day:_day(day,reports[day],private_samples.get(day,{})) for day in planned if day in reports}
    groups = {key:_aggregate_group(key,planned,completed,private_samples) for key in _GROUPS}
    primary = groups['shock/550']
    primary['inference'] = equal_day_inference([_finite(completed[day]['groups']['shock/550']['mean_saving_bps'])
                                               for day in planned if day in completed and completed[day]['paired_shocks']])
    contributors = [row for row in completed.values() if row['paired_shocks']]
    support = dict(days_with_100_shocks=sum(row['shock_intents']>=100 for row in completed.values()),
                   at_least_ten_qualified_days=len(completed)>=10,
                   every_contributor_95pct=all(row['support']['intent_coverage_95pct'] for row in contributors),
                   every_contributor_99pct_depth=all(row['support']['future_depth_99pct'] for row in contributors),
                   zero_missing_primary_targets=all(row['support']['zero_missing_primary_targets'] for row in completed.values()),
                   numeric_contributing_days=len(contributors))
    support['pass'] = bool(support['days_with_100_shocks']>=10 and support['at_least_ten_qualified_days']
                           and contributors and support['every_contributor_95pct']
                           and support['every_contributor_99pct_depth'] and support['zero_missing_primary_targets'])
    inference = primary['inference']
    contradictions = dict(block_two=False,leave_one_day_out=False)
    if inference['sensitivity_ci95'] is not None:
        contradictions['block_two'] = inference['sensitivity_ci95'][0]<=0
    if inference['ci95'] is not None and inference['leave_one_day_out']:
        contradictions['leave_one_day_out'] = any(value is None or value<.1 for value in inference['leave_one_day_out'])
    if stage!='final':
        status = 'DESCRIPTIVE_'+stage.upper()
    elif not support['pass']:
        status = 'FAIL_SUPPORT'
    elif not external_gates_passed:
        status = 'NOT_RUN_EXTERNAL_GATES'
    elif inference['mean']<=0:
        status = 'NEGATIVE'
    elif inference['ci95'] is None or inference['ci95'][0]<=0 or inference['mean']<.1:
        status = 'INCONCLUSIVE'
    elif any(contradictions.values()):
        status = 'SENSITIVITY_DEPENDENT'
    else:
        status = 'HISTORICAL_QUOTE_COST_SCREEN_PASS'
    day_rows = []
    for day in planned:
        if day in completed:
            day_rows.append(completed[day])
        else:
            day_rows.append(dict(day=day,status='MISSING',reason=missing_reasons.get(day,'MISSING_REPORT'),
                                 paired_shocks=None,mean_saving_bps=None))
    return dict(stage=stage,status=status,days=day_rows,groups=groups,primary=primary,support=support,
                external_gates_passed=external_gates_passed,sensitivity_contradictions=contradictions,
                boundary='Historical selected-day quote costs only; no fills, returns or deployment authority.')
