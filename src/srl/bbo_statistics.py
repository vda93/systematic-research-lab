"""Descriptive saving distributions and fixed equal-day uncertainty helpers.

Inputs are already qualified savings, not prices or simulated fills. Callers keep
all planned-day support failures and supply daily means in chronological order.
These functions do not decide rights, support, promotion, or sample freshness.
"""
from __future__ import annotations

import heapq
from importlib import import_module
from itertools import repeat
import math
import statistics
from typing import Callable, Iterator, Sequence

from srl.block_means import circular_block_means
# The released resampling module has legacy untyped helpers. Keep a narrow typed
# callable boundary without editing that frozen benchmark source or relaxing mypy.
_percentile: Callable[[Sequence[float], float], float] = import_module('srl.resampling').percentile

_PERCENTILES = (50, 90, 95, 99)
_REPETITIONS = 20_000
_SEED = 20261021


def _finite(value: float) -> float:
    if type(value) not in (int, float):
        raise ValueError('savings must be finite built-in numbers, excluding bool')
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError('saving exceeds finite float range') from exc
    if not math.isfinite(result):
        raise ValueError('savings must be finite')
    return result


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    # statistics.mean accumulates the binary input ratios exactly before division;
    # fsum(values)/n could overflow for a representable average.
    result = float(statistics.mean(values))
    if not math.isfinite(result):
        raise ValueError('mean cannot be represented as a finite float')
    return result


def _sd(values: Sequence[float]) -> float | None:
    if len(values) < 2:
        return None
    try:
        result = float(statistics.stdev(values))
    except OverflowError as exc:
        raise ValueError('sample standard deviation exceeds finite float range') from exc
    if not math.isfinite(result):
        raise ValueError('sample standard deviation exceeds finite float range')
    return result


def _lower_quantile(ordered: Sequence[float], percent: int) -> float | None:
    if not ordered:
        return None
    # Inverse empirical CDF: first x with count(<=x)/n >= percent/100.
    return ordered[(percent * len(ordered) + 99) // 100 - 1]


def distribution_summary(savings: Sequence[float]) -> dict[str, object]:
    """Describe equally weighted intents, with penalty = -saving (no zero clamp).

    Quantiles and median use the smallest observed x with F(x)>=p, including
    half-mass ties. Empty statistics are None. Integers are first converted to
    binary floats; decimal/integer precision lost before that step is not restored.
    """
    values = [_finite(value) for value in savings]
    ordered = sorted(values)
    penalties = [-value for value in reversed(ordered)]
    return {'count': len(values), 'mean': _mean(values), 'sample_sd': _sd(values),
            'median_saving': _lower_quantile(ordered, 50),
            'penalty_quantiles': {str(p): _lower_quantile(penalties, p) for p in _PERCENTILES},
            'worst_penalty': penalties[-1] if penalties else None}


def _interval(values: Sequence[float], block: int) -> list[float]:
    means = circular_block_means(values, block_size=block, repetitions=_REPETITIONS, seed=_SEED)
    return [_percentile(means, .025), _percentile(means, .975)]


def equal_day_inference(daily_means: Sequence[float]) -> dict[str, object]:
    """Equal weight per observed day; fixed 20,000-draw 95% percentile intervals.

    One-day circular blocks are primary; two-day blocks are descriptive sensitivity.
    The caller must supply chronological selected-day order and report omitted
    days separately. Monthly gaps are not reconstructed as contiguous calendar
    observations. Sparse selected days and circular endpoint adjacency limit the
    interpretation of this bootstrap; arithmetic correctness does not qualify it.
    Intended periods have at most twelve selected days. Leave-one-out costs O(D^2)
    day visits; the two bootstrap vectors each store only 20,000 means, not a
    draw-by-intent matrix. Fewer than four days gets descriptions only.
    No positive fraction is a p-value.
    """
    values = [_finite(value) for value in daily_means]
    count = len(values)
    result: dict[str, object] = {
        'count': count, 'mean': _mean(values), 'sample_sd': _sd(values),
        'sign_counts': {'negative': sum(value < 0 for value in values),
                        'zero': sum(value == 0 for value in values),
                        'positive': sum(value > 0 for value in values)},
        'leave_one_day_out': [_mean(values[:i] + values[i+1:]) for i in range(count)],
        'ci95': None, 'sensitivity_ci95': None,
        'primary_block_size': 1, 'sensitivity_block_size': 2,
        'bootstrap_repetitions': _REPETITIONS, 'seed': _SEED,
        'status': 'DESCRIPTIVE_FEWER_THAN_FOUR_DAYS',
    }
    if count >= 4:
        result.update(ci95=_interval(values, 1), sensitivity_ci95=_interval(values, 2),
                      status='BOOTSTRAP_AVAILABLE_SUPPORT_NOT_ASSESSED')
    return result


def weighted_penalty_quantiles(day_savings: Sequence[Sequence[float]]) -> dict[str, object]:
    """Equal-day mixture CDF: every intent in day d has mass 1/(D*n_d).

    Empty days contribute no empirical mass and are explicitly counted. Their
    exclusion here grants no support approval. Exact integer weights are L/n_d
    where L=lcm(n_d); thresholds compare 100*cumulative with p*D*L. No epsilon or
    rounded floating weights enter ties. Each day is sorted once; a lazy merge
    avoids materializing a weighted pair per intent or any bootstrap-by-intent
    matrix. Memory is O(N+D) values/iterators, plus integer bit costs; L can grow
    with unequal day counts. All values are validated before any quantile returns.
    """
    counts = [len(day) for day in day_savings if len(day)]
    contributing = len(counts)
    quantiles: dict[str, float | None] = dict.fromkeys(str(p) for p in _PERCENTILES)
    result: dict[str, object] = {
        'quantiles': quantiles, 'planned_days': len(day_savings),
        'contributing_days': contributing, 'empty_days': len(day_savings)-contributing,
        'intent_count': sum(counts),
    }
    if not counts:
        return result
    scale = math.lcm(*counts)
    streams: list[Iterator[tuple[float, int]]] = []
    for day in day_savings:
        if day:
            penalties = sorted(-_finite(value) for value in day)
            streams.append(zip(penalties, repeat(scale // len(day))))
    total_weight = contributing * scale
    cumulative = 0
    index = 0
    for penalty, weight in heapq.merge(*streams):
        cumulative += weight
        while index < len(_PERCENTILES) and 100 * cumulative >= _PERCENTILES[index] * total_weight:
            quantiles[str(_PERCENTILES[index])] = penalty
            index += 1
        if index == len(_PERCENTILES):
            break
    return result
