"""Completion-robust rolling history; no missing quote is imputed."""
from __future__ import annotations

from bisect import bisect_left, insort
from collections import deque
from dataclasses import dataclass
import math
from typing import Iterable

from srl.bbo import QuoteUpdate


@dataclass(frozen=True)
class MedianBounds:
    lower: float
    upper: float
    known_us: int
    unknown_us: int


def _bounds(keys: Iterable[float], weights: dict[float, int], known_us: int, total: int) -> MedianBounds:
    unknown = total - known_us
    lower, upper = -math.inf, math.inf
    cumulative = 0
    lower_found = unknown * 2 >= total
    for value in keys:
        cumulative += weights[value]
        if not lower_found and cumulative * 2 >= total - unknown * 2:
            lower, lower_found = value, True
        if cumulative * 2 >= total:
            upper = value
            break
    return MedianBounds(lower, upper, known_us, unknown)


def median_bounds(known: Iterable[tuple[float, int]], *, total_us: int) -> MedianBounds:
    """Outer lower-median bounds over arbitrary real-valued missing mass."""
    if type(total_us) is not int or total_us <= 0:
        raise ValueError('positive integer window duration required')
    weights: dict[float, int] = {}
    for spread, duration in known:
        if (type(spread) not in (float, int) or not math.isfinite(spread)
                or type(duration) is not int or duration <= 0):
            raise ValueError('finite numerical spread and positive integer duration required')
        weights[float(spread)] = weights.get(float(spread), 0) + duration
    known_us = sum(weights.values())
    if known_us > total_us:
        raise ValueError('known duration exceeds the window')
    return _bounds(sorted(weights), weights, known_us, total_us)


def classify(current_spread: float, bounds: MedianBounds) -> str:
    """Classify numerical indicators by exact-ratio three-times comparisons."""
    if type(current_spread) not in (int, float) or not math.isfinite(current_spread) or current_spread <= 0:
        raise ValueError('finite positive current spread required')
    if not (math.isfinite(bounds.lower) and math.isfinite(bounds.upper)
            and 0 < bounds.lower <= bounds.upper):
        return 'ambiguous'
    numerator, denominator = float(current_spread).as_integer_ratio()
    upper_n, upper_d = bounds.upper.as_integer_ratio()
    if numerator * upper_d >= 3 * upper_n * denominator:
        return 'shock'
    lower_n, lower_d = bounds.lower.as_integer_ratio()
    return 'normal' if numerator * lower_d < 3 * lower_n * denominator else 'ambiguous'


class RollingHistory:
    """Duration-weighted known observations and explicit unknown intervals.

    State is bounded by one window plus distinct spread weights. Sorted-key
    insertion/eviction is linear in distinct keys; quantile queries scan keys.
    Timestamps advance monotonically. The caller installs a new quote only
    after advancing to its receipt time, so future quotes cannot seed history.
    """
    def __init__(self, *, window_us: int = 60_000_000, max_age_us: int = 250_000,
                 start_us: int = 0) -> None:
        if any(type(x) is not int or x <= 0 for x in (window_us, max_age_us)) or type(start_us) is not int:
            raise ValueError('integer clock and positive integer window/age required')
        self.window, self.max_age, self.end = window_us, max_age_us, start_us
        self.segments: deque[tuple[int, int, float | None]] = deque()
        self.weights: dict[float, int] = {}
        self.keys: list[float] = []
        self.known = 0

    def _weight(self, value: float | None, duration: int) -> None:
        if value is None:
            return
        old = self.weights.get(value, 0)
        updated = old + duration
        if updated < 0:
            raise ValueError('history duration accounting underflow')
        self.known += duration
        if updated == 0:
            del self.weights[value]
            del self.keys[bisect_left(self.keys, value)]
        else:
            if old == 0:
                insort(self.keys, value)
            self.weights[value] = updated

    def _append(self, low: int, high: int, value: float | None) -> None:
        if high <= low:
            return
        if self.segments and self.segments[-1][1] == low and self.segments[-1][2] == value:
            previous = self.segments.pop()
            self.segments.append((previous[0], high, value))
        else:
            self.segments.append((low, high, value))
        self._weight(value, high-low)

    def advance(self, timestamp_us: int, current: QuoteUpdate | None) -> None:
        if type(timestamp_us) is not int or timestamp_us < self.end:
            raise ValueError('history clock must advance monotonically in integer microseconds')
        if current is not None and current.local_us > self.end:
            raise ValueError('future state cannot seed prior history')
        low = self.end
        if current is not None and current.quote is not None:
            valid_end = min(timestamp_us, current.local_us + self.max_age)
            if valid_end > low:
                quote = current.quote
                midpoint = quote.bid + (quote.ask-quote.bid)/2
                spread_value = (quote.ask-quote.bid)/midpoint * 10000
                if not math.isfinite(spread_value) or spread_value <= 0:
                    raise ValueError('nonfinite or nonpositive numerical history spread')
                self._append(low, valid_end, spread_value)
                low = valid_end
        self._append(low, timestamp_us, None)
        self.end = timestamp_us
        cutoff = timestamp_us - self.window
        while self.segments and self.segments[0][0] < cutoff:
            start, end, value = self.segments.popleft()
            removed = min(end, cutoff)-start
            self._weight(value, -removed)
            if end > cutoff:
                self.segments.appendleft((cutoff, end, value))
        if not 0 <= self.known <= self.window:
            raise ValueError('history window duration invariant failed')

    def bounds(self) -> MedianBounds:
        return _bounds(self.keys, self.weights, self.known, self.window)
