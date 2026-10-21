"""Receive-clock replay of the separately frozen BBO measurement amendment.

No queue/fill or funded portfolio is simulated. Returned samples and the audit
callback are PRIVATE; publish only the reviewed coarse report.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import heapq
import math
from typing import Any, Callable, Iterable

from srl.bbo import DAY_US, Quote, QuoteUpdate
from srl.bbo_accounting import CostDifference, compare_quotes, crossing_price, midpoint, spread
from srl.bbo_history import RollingHistory, classify
from srl.bbo_statistics import distribution_summary

AGE_US = 250_000
TARGETS = (50_000, 300_000, 550_000, 1_050_000)


@dataclass(frozen=True)
class DayReplay:
    report: dict[str, Any]
    savings: dict[str, list[float]]  # Private individual outcomes, never public JSON.


@dataclass
class _Intent:
    time: int
    side: int
    mid: float
    quantity: float
    label: str
    lower: float
    upper: float
    known_us: int
    targets: dict[int, Quote | None] = field(default_factory=dict)
    ages: dict[int, int | None] = field(default_factory=dict)


@dataclass
class _Group:
    eligible: int = 0
    missing_baseline: int = 0
    missing_delayed: int = 0
    both_missing: int = 0
    baseline_depth_fail: int = 0
    delayed_depth_fail: int = 0
    either_depth_fail: int = 0
    sufficient_depth_both: int = 0
    comparisons: list[CostDifference] = field(default_factory=list)
    depth_qualified: list[CostDifference] = field(default_factory=list)

    def add(self, intent: _Intent, offset: int) -> None:
        self.eligible += 1
        base, delayed = intent.targets[50_000], intent.targets[offset]
        self.missing_baseline += base is None
        self.missing_delayed += delayed is None
        self.both_missing += base is None and delayed is None
        base_bad = base is not None and _amount(base, intent.side) < intent.quantity
        delayed_bad = delayed is not None and _amount(delayed, intent.side) < intent.quantity
        self.baseline_depth_fail += base_bad
        self.delayed_depth_fail += delayed_bad
        self.either_depth_fail += base_bad or delayed_bad
        self.sufficient_depth_both += base is not None and delayed is not None and not (base_bad or delayed_bad)
        if base is not None and delayed is not None:
            comparison = compare_quotes(intent.mid, base, delayed, intent.side)
            self.comparisons.append(comparison)
            if not (base_bad or delayed_bad):
                self.depth_qualified.append(comparison)

    def values(self) -> list[float]:
        return [comparison.saving(5., .5) for comparison in self.comparisons]

    def report(self) -> dict[str, Any]:
        result = distribution_summary(self.values())
        n = len(self.comparisons)
        components = {}
        for name in ('price_saving', 'spread_saving', 'mid_drift_saving', 'fee_slope'):
            components[name] = math.fsum(getattr(c, name) for c in self.comparisons) / n if n else None
        grid = {f'{fee:g}/{slippage:g}':
                math.fsum(c.saving(fee, slippage) for c in self.comparisons) / n if n else None
                for fee in (0., 5., 10.) for slippage in (0., .5, 1.)}
        return dict(result, eligible=self.eligible, paired=n, mean_saving_bps=result['mean'],
                    missing_baseline=self.missing_baseline, missing_delayed=self.missing_delayed,
                    both_missing=self.both_missing, baseline_depth_fail=self.baseline_depth_fail,
                    delayed_depth_fail=self.delayed_depth_fail, either_depth_fail=self.either_depth_fail,
                    sufficient_depth_both=self.sufficient_depth_both,
                    mean_components=components, mean_cost_grid_bps=grid,
                    post_outcome_depth_subset=distribution_summary([c.saving(5., .5) for c in self.depth_qualified]))


def _amount(quote: Quote, side: int) -> float:
    return quote.ask_amount if side == 1 else quote.bid_amount


def _available(current: QuoteUpdate | None, target: int) -> Quote | None:
    return current.quote if (current is not None and current.quote is not None
                             and 0 <= target-current.local_us <= AGE_US) else None


def replay_updates(
    updates: Iterable[QuoteUpdate], *, start_us: int,
    first_intent_us: int | None = None, last_intent_us: int | None = None,
    audit: Callable[[dict[str, Any]], None] | None = None,
) -> DayReplay:
    """Merge clocks with intent < same-time update < same-time outcome target.

    Scientific defaults are fixed. Optional intent endpoints permit small original
    fixtures; the study CLI always uses the entire frozen UTC-day schedule.
    Consume the whole input, including after the last target, so late corruption
    cannot return a favorable prefix. Any exception invalidates the entire day.
    """
    if type(start_us) is not int:
        raise ValueError('integer UTC-day start required')
    first = start_us+300_000_000 if first_intent_us is None else first_intent_us
    last = start_us+DAY_US-2_000_000 if last_intent_us is None else last_intent_us
    if (any(type(t) is not int or t % 1_000_000 for t in (first, last))
            or not start_us <= first <= last <= start_us+DAY_US-2_000_000):
        raise ValueError('ordered whole-second intent bounds within the day required')
    iterator = iter(updates)
    next_update = next(iterator, None)
    current: QuoteUpdate | None = None
    history = RollingHistory(start_us=start_us)
    next_intent = first
    queue: list[tuple[int, int, int]] = []
    pending: dict[int, _Intent] = {}
    groups: dict[str, _Group] = {}
    exclusions: Counter[str] = Counter()
    labels: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    bounds_widths: list[float] = []

    def emit(row: dict[str, Any]) -> None:
        if audit is not None:
            audit(row)

    def decide(time: int) -> None:
        side = 1 if (time//1_000_000) % 2 == 0 else -1
        counts['scheduled'] += 1
        counts['buy_scheduled' if side == 1 else 'sell_scheduled'] += 1
        row: dict[str, Any] = {'intent_us': time, 'side': side}
        bounds = history.bounds()
        flags = []
        if not (math.isfinite(bounds.lower) and math.isfinite(bounds.upper) and bounds.lower > 0):
            flags.append('MEDIAN_AMBIGUOUS')
        row.update(known_history_us=bounds.known_us, unknown_history_us=bounds.unknown_us,
                   median_lower=bounds.lower if math.isfinite(bounds.lower) else None,
                   median_upper=bounds.upper if math.isfinite(bounds.upper) else None)
        reason = ''
        if current is None:
            reason = 'MISSING_INTENT_STATE'
        elif current.quote is None:
            reason = 'INVALID_INTENT_STATE'
        elif time-current.local_us > AGE_US:
            reason = 'STALE_INTENT_STATE'
        if reason:
            exclusions[reason] += 1
            emit(dict(row, exclusion=reason, flags=[reason, *flags, 'CURRENT_SPREAD_UNAVAILABLE',
                                                   'INTENT_DEPTH_UNAVAILABLE'],
                      targets='NOT_EVALUATED_INELIGIBLE'))
            return
        assert current is not None and current.quote is not None
        mid = midpoint(current.quote)
        quantity = 100 / mid
        if not math.isfinite(quantity) or quantity <= 0:
            raise ArithmeticError('nonfinite fixed-intent quantity')
        if _amount(current.quote, side) < quantity:
            reason = 'INSUFFICIENT_INTENT_DEPTH'
            flags.append(reason)
        label = classify(spread(current.quote), bounds)
        if label == 'ambiguous' and 'MEDIAN_AMBIGUOUS' not in flags:
            flags.append('MEDIAN_AMBIGUOUS')
        if not reason and label == 'ambiguous':
            reason = 'MEDIAN_AMBIGUOUS'
        row.update(intent_midpoint=mid, quantity=quantity, intent_quote_age_us=time-current.local_us,
                   label=label)
        if reason:
            exclusions[reason] += 1
            emit(dict(row, exclusion=reason, flags=flags, targets='NOT_EVALUATED_INELIGIBLE'))
            return
        labels[label] += 1
        counts['buy_eligible' if side == 1 else 'sell_eligible'] += 1
        bounds_widths.append(bounds.upper-bounds.lower)
        intent = _Intent(time, side, mid, quantity, label, bounds.lower, bounds.upper, bounds.known_us)
        pending[time] = intent
        for target in TARGETS:
            heapq.heappush(queue, (time+target, time, target))

    def finish(intent: _Intent) -> None:
        for offset in TARGETS[1:]:
            for suffix in ('', '/buy' if intent.side == 1 else '/sell'):
                key = f'{intent.label}/{offset//1000}{suffix}'
                groups.setdefault(key, _Group()).add(intent, offset)
        targets: dict[str, Any] = {}
        for offset, quote in intent.targets.items():
            targets[str(offset//1000)] = None if quote is None else {
                'price': crossing_price(quote, intent.side), 'bid': quote.bid, 'ask': quote.ask,
                'bid_amount': quote.bid_amount, 'ask_amount': quote.ask_amount,
                'age_us': intent.ages[offset], 'depth_sufficient': _amount(quote, intent.side) >= intent.quantity}
        flags = []
        if intent.targets[50_000] is None:
            flags.append('MISSING_BASELINE_QUOTE')
        if intent.targets[550_000] is None:
            flags.append('MISSING_DELAYED_QUOTE')
        if any(q is not None and _amount(q, intent.side) < intent.quantity
               for q in (intent.targets[50_000], intent.targets[550_000])):
            flags.append('FUTURE_DEPTH_FAIL')
        emit({'intent_us': intent.time, 'side': intent.side, 'label': intent.label, 'flags': flags,
              'intent_midpoint': intent.mid, 'quantity': intent.quantity,
              'median_lower': intent.lower, 'median_upper': intent.upper,
              'known_history_us': intent.known_us, 'targets': targets})

    previous_update: int | None = None
    while next_update is not None or next_intent <= last or queue:
        clocks = []
        if next_update is not None:
            clocks.append(next_update.local_us)
        if next_intent <= last:
            clocks.append(next_intent)
        if queue:
            clocks.append(queue[0][0])
        timestamp = min(clocks)
        if not start_us <= timestamp < start_us+DAY_US:
            raise ValueError('replay timestamp outside requested day')
        history.advance(timestamp, current)
        if timestamp == next_intent and next_intent <= last:
            decide(timestamp)  # Strict past: same-time message is not installed yet.
            next_intent += 1_000_000
        if next_update is not None and next_update.local_us == timestamp:
            if previous_update is not None and timestamp <= previous_update:
                raise ValueError('updates must have strictly increasing receive times')
            current, previous_update = next_update, timestamp
            next_update = next(iterator, None)
        while queue and queue[0][0] == timestamp:
            _, identifier, offset = heapq.heappop(queue)
            intent = pending[identifier]
            intent.targets[offset] = _available(current, timestamp)
            intent.ages[offset] = None if current is None else timestamp-current.local_us
            if offset == TARGETS[-1]:
                finish(intent)
                del pending[identifier]
    scheduled = counts['scheduled']
    eligible = sum(labels.values())
    if scheduled != eligible + sum(exclusions.values()) or pending:
        raise ValueError('intent reconciliation invariant failed')
    public_groups = {key: group.report() for key, group in sorted(groups.items())}
    primary = public_groups.get('shock/550', {})
    shock_count = labels['shock']
    report = {'scheduled_intents': scheduled, 'eligible_intents': eligible,
              'shock_intents': shock_count, 'normal_intents': labels['normal'],
              'exclusions': dict(sorted(exclusions.items())), 'side_counts': dict(counts),
              'eligible_fraction': eligible/scheduled, 'groups': public_groups,
              'hypothetical_scheduled_notional_usdt': scheduled*100,
              'hypothetical_eligible_notional_usdt': eligible*100,
              'median_bound_width_bps': {'count': len(bounds_widths),
                                         'mean': math.fsum(bounds_widths)/len(bounds_widths) if bounds_widths else None,
                                         'maximum': max(bounds_widths) if bounds_widths else None},
              'support': {'minimum_100_shocks': shock_count >= 100,
                          'intent_coverage_95pct': eligible/scheduled >= .95,
                          'zero_missing_primary_targets': primary.get('paired', 0) == shock_count,
                          'future_depth_99pct': shock_count > 0 and
                          primary.get('sufficient_depth_both', 0)/shock_count >= .99},
              'boundary': 'Conditional historical quote costs, not fills, strategy returns or funded exposure.'}
    return DayReplay(report, {key: group.values() for key, group in groups.items()})
