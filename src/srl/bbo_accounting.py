"""Order-side quote costs for the frozen BBO-delay study; these are not fills.

Quantity is fixed from the intent's 100-USDT notional. Future displayed depth
is reported by replay, never used here to drop an adverse price comparison.
Invalid inputs raise ValueError; nonfinite or inconsistent arithmetic raises
ArithmeticError so the caller fails the file rather than skipping an intent.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from srl.bbo import Quote

_TOLERANCE_BPS = 1e-8


def _finite_input(value: float, name: str) -> None:
    try:
        finite = not isinstance(value, bool) and math.isfinite(value)
    except (TypeError, OverflowError) as exc:
        raise ValueError(f'{name} must be a finite number') from exc
    if not finite:
        raise ValueError(f'{name} must be a finite number')


def _positive(value: float, name: str) -> None:
    _finite_input(value, name)
    if value <= 0:
        raise ValueError(f'{name} must be positive')


def _nonnegative(value: float, name: str) -> None:
    _finite_input(value, name)
    if value < 0:
        raise ValueError(f'{name} must be nonnegative')


def _validate_quote(quote: Quote) -> None:
    for name, value in (('ask', quote.ask), ('bid', quote.bid),
                        ('ask_amount', quote.ask_amount), ('bid_amount', quote.bid_amount)):
        _positive(value, name)
    if quote.bid >= quote.ask:
        raise ValueError('bid must be strictly below ask')


def _side(side: int) -> None:
    if type(side) is not int or side not in (-1, 1):
        raise ValueError('side must be exactly integer -1 or +1')


def _result(value: float) -> float:
    if not math.isfinite(value):
        raise ArithmeticError('nonfinite quote-cost arithmetic')
    return value


def _sum(values: list[float]) -> float:
    try:
        return _result(math.fsum(values))
    except (ValueError, OverflowError) as exc:
        raise ArithmeticError('invalid or overflowing quote-cost sum') from exc


def midpoint(quote: Quote) -> float:
    """Return the protocol's finite-float midpoint in its frozen operation order."""
    _validate_quote(quote)
    return _result(quote.bid + (quote.ask - quote.bid) / 2)


def spread(quote: Quote) -> float:
    """Return quoted relative spread in bps, preserving frozen operation order."""
    mid = midpoint(quote)
    return _result((quote.ask - quote.bid) / mid * 10_000)


def crossing_price(quote: Quote, side: int) -> float:
    """Ask for a buy, bid for a sell; displayed quotes do not establish execution."""
    _side(side)
    _validate_quote(quote)
    return quote.ask if side == 1 else quote.bid


@dataclass(frozen=True)
class CostDifference:
    """Baseline-minus-delayed costs in bps of original intent notional.

    fee_slope is the difference in target quote notionals divided by the
    original 100 USDT, so a common fee rate need not cancel exactly.
    """

    price_saving: float
    spread_saving: float
    mid_drift_saving: float
    fee_slope: float

    def __post_init__(self) -> None:
        for name, value in (('price_saving', self.price_saving),
                            ('spread_saving', self.spread_saving),
                            ('mid_drift_saving', self.mid_drift_saving),
                            ('fee_slope', self.fee_slope)):
            _finite_input(value, name)

    def saving(self, fee_bps: float, extra_slippage_bps: float) -> float:
        """Positive means delaying costs less, under the supplied cost assumptions."""
        _nonnegative(fee_bps, 'fee_bps')
        _nonnegative(extra_slippage_bps, 'extra_slippage_bps')
        return _sum([self.price_saving, fee_bps * self.fee_slope, -extra_slippage_bps])


def compare_quotes(
    intent_midpoint: float, baseline: Quote, delayed: Quote, side: int,
) -> CostDifference:
    """Compare one fixed-quantity intent at two quoted marketable prices.

    Q=100/intent_midpoint is represented algebraically by dividing prices by
    intent_midpoint. This preserves the original-notional denominator without
    independently re-sizing at either policy quote. Depth sufficiency belongs
    to the caller's ledger and never filters this comparison.
    """
    _positive(intent_midpoint, 'intent_midpoint')
    _side(side)
    price_b = crossing_price(baseline, side)
    price_d = crossing_price(delayed, side)
    mid_b, mid_d = midpoint(baseline), midpoint(delayed)
    half_b = (baseline.ask - baseline.bid) / 2
    half_d = (delayed.ask - delayed.bid) / 2
    fee_slope = _result((price_b - price_d) / intent_midpoint)
    price_saving = _result(10_000 * side * fee_slope)
    spread_saving = _result((half_b - half_d) / intent_midpoint * 10_000)
    drift_saving = _result(side * (mid_b - mid_d) / intent_midpoint * 10_000)
    if abs(_sum([spread_saving, drift_saving, -price_saving])) > _TOLERANCE_BPS:
        raise ArithmeticError('spread/midpoint decomposition exceeds 1e-8 bps')
    result = CostDifference(price_saving, spread_saving, drift_saving, fee_slope)

    # Independent arithmetic path: compute each policy's original-notional
    # cost first, rather than deriving it from price difference/decomposition.
    cost_b = _result(side * (price_b - intent_midpoint) / intent_midpoint * 10_000)
    cost_d = _result(side * (price_d - intent_midpoint) / intent_midpoint * 10_000)
    fee_b = _result(5.0 * (price_b / intent_midpoint))
    fee_d = _result(5.0 * (price_d / intent_midpoint))
    direct_primary = _sum([cost_b, fee_b, -cost_d, -fee_d, -0.5])
    if abs(_sum([result.saving(5.0, 0.5), -direct_primary])) > _TOLERANCE_BPS:
        raise ArithmeticError('direct primary-cost check exceeds 1e-8 bps')
    return result
