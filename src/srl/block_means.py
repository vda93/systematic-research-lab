"""Exact circular block sums with one float rounding per replicate mean.

This is an optional sampling kernel. It does not change frozen study outputs,
align dates, select a block length, or establish the validity of an inference.
"""

from fractions import Fraction
import math
import random
from typing import Sequence


def _ratios(values: Sequence[float]) -> list[tuple[int, int]]:
    ratios = []
    for value in values:
        if type(value) not in (int, float):
            raise ValueError('values must be finite built-in ints or floats, excluding bool')
        try:
            converted = float(value)
        except OverflowError as exc:
            raise ValueError('input cannot be represented as a finite float') from exc
        if not math.isfinite(converted):
            raise ValueError('values must be finite')
        ratios.append(converted.as_integer_ratio())
    return ratios


def _block_totals(prefix: Sequence[int], length: int) -> tuple[int, ...]:
    n = len(prefix) - 1
    return tuple(prefix[start + length] - prefix[start] if start + length <= n
                 else prefix[n] - prefix[start] + prefix[start + length - n]
                 for start in range(n))


def circular_block_means(
    values: Sequence[float], *, block_size: int, repetitions: int, seed: int,
) -> tuple[float, ...]:
    """Sample means from ordered observations using circular moving blocks.

    At least four finite observations; 1 <= block_size <= n//2. Each draw has
    exactly n observations, with one uniform start per block, wraparound and a
    truncated final block. RNG consumption matches resampling.circular_indices.
    The returned tuple keeps draw order and never mutates the input.

    Built-in ints are converted to float first (possibly losing integer precision).
    Each resulting binary float x_i has exact representation a_i / D for a common
    power-of-two D. Prefix sums, block totals and sampled totals are Python ints.
    Fraction(total, n*D) is converted once to float; cancellation and intermediate
    floating overflow cannot corrupt block aggregation. A tiny mean can round to
    zero. The kernel estimates uncertainty in supplied values, not market fills.
    """
    n = len(values)
    if n < 4:
        raise ValueError('at least four ordered observations are required')
    if type(block_size) is not int or not 1 <= block_size <= n // 2:
        raise ValueError('block size must be an integer in [1, n//2]')
    if type(repetitions) is not int or repetitions < 1 or type(seed) is not int:
        raise ValueError('repetitions must be positive integer and seed an integer')
    ratios = _ratios(values)
    scale = max(denominator for _, denominator in ratios)
    prefix = [0]
    for numerator, denominator in ratios:
        prefix.append(prefix[-1] + numerator * (scale // denominator))
    full = _block_totals(prefix, block_size)
    count, remainder = divmod(n, block_size)
    tail = _block_totals(prefix, remainder) if remainder else ()
    rng = random.Random(seed)
    means = []
    for _ in range(repetitions):
        total = sum(full[rng.randrange(n)] for _ in range(count))
        if remainder:
            total += tail[rng.randrange(n)]
        means.append(float(Fraction(total, n * scale)))
    return tuple(means)
