"""Conditional uncertainty for aligned daily paths using circular blocks.

The inference unit is a calendar day. Pairing is preserved by resampling one
vector of treatment-minus-control differences with common block indices.
"""

from datetime import date
import math
import random
from typing import Mapping, Sequence


def _finite(value: object) -> float:
    if type(value) not in (int, float):
        raise ValueError("daily values must be finite numbers")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError("value exceeds finite float range") from exc
    if not math.isfinite(value):
        raise ValueError("daily values and arithmetic must be finite")
    return value


def _total(values) -> float:
    try:
        value = math.fsum(values)
    except (OverflowError, ValueError) as exc:
        raise ValueError("bootstrap aggregate must be finite") from exc
    return _finite(value)


def circular_indices(n: int, block_size: int, rng: random.Random) -> list[int]:
    """Draw block starts uniformly, wrapping each block and truncating at n.

    This low-level helper accepts any block length 1..n. The public bootstrap
    applies the stricter n//2 limit to avoid a single full-sample block.
    """
    if type(n) is not int or type(block_size) is not int or not 1 <= block_size <= n:
        raise ValueError("n and block size must be positive integers with block size <= n")
    indices = []
    while len(indices) < n:
        start = rng.randrange(n)
        length = min(block_size, n - len(indices))
        indices.extend((start + offset) % n for offset in range(length))
    return indices


def percentile(values: Sequence[float], q: float) -> float:
    """Linear interpolation at rank (m-1)*q, with finite endpoint arithmetic."""
    q = _finite(q)
    ordered = sorted(_finite(value) for value in values)
    if not ordered or not 0 <= q <= 1:
        raise ValueError("percentile needs observations and q in [0, 1]")
    return _ordered_percentile(ordered, q)


def _ordered_percentile(ordered: Sequence[float], q: float) -> float:
    rank = (len(ordered) - 1) * q
    lower = math.floor(rank)
    upper = math.ceil(rank)
    weight = rank - lower
    return _total(((1 - weight) * ordered[lower], weight * ordered[upper]))


def _calendar(path: Mapping[str, float]) -> list[str]:
    days = []
    for key in path:
        if not isinstance(key, str):
            raise ValueError("daily keys must be canonical YYYY-MM-DD dates")
        try:
            parsed = date.fromisoformat(key)
        except ValueError as exc:
            raise ValueError("daily keys must be canonical YYYY-MM-DD dates") from exc
        if parsed.isoformat() != key:
            raise ValueError("daily keys must be canonical YYYY-MM-DD dates")
        days.append(parsed)
    days.sort()
    if len(days) < 4 or any((right - left).days != 1 for left, right in zip(days, days[1:])):
        raise ValueError("at least four contiguous calendar days are required")
    return [day.isoformat() for day in days]


def paired_daily_bootstrap(
    control: Mapping[str, float], treatment: Mapping[str, float], *,
    block_size: int, repetitions: int, seed: int,
) -> dict:
    """Return a percentile interval for the paired daily mean difference.

    The circular moving-block model assumes the supplied daily path is a useful
    stationary approximation. The output does not qualify unseen market data.
    Positive fraction counts strictly positive replicate means.
    """
    days = _calendar(control)
    if days != _calendar(treatment):
        raise ValueError("control and treatment must have identical calendars")
    n = len(days)
    if type(block_size) is not int or not 1 <= block_size <= n // 2:
        raise ValueError("block size must be an integer in [1, sample_days//2]")
    if type(repetitions) is not int or repetitions < 1 or type(seed) is not int:
        raise ValueError("repetitions must be a positive integer and seed an integer")
    deltas = [_total((_finite(treatment[day]), -_finite(control[day]))) for day in days]
    observed = _total(deltas) / n
    rng = random.Random(seed)
    means = []
    for _ in range(repetitions):
        indices = circular_indices(n, block_size, rng)
        means.append(_total(deltas[index] for index in indices) / n)
    means.sort()
    return {
        "observed_mean_delta": observed,
        "ci_low": _ordered_percentile(means, .025),
        "ci_high": _ordered_percentile(means, .975),
        "positive_fraction": sum(value > 0 for value in means) / repetitions,
        "block_size": block_size, "repetitions": repetitions, "seed": seed,
        "sample_days": n, "method": "paired circular moving-block bootstrap",
    }
