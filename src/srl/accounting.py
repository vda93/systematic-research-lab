"""Cost-explicit record accounting, without position-sizing assumptions.

Equity starts at zero and realizes each net amount at its close date. Equal
close dates are ordered by key, so drawdown is a property of that declared
ordering. Concentration removes whole opening-date cohorts by net contribution.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
import math
from typing import Iterable


@dataclass(frozen=True)
class Record:
    key: str
    opened: str
    closed: str
    gross: float
    cost: float


def _number(value: object, label: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} is outside finite float range") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _sum(values: Iterable[float]) -> float:
    try:
        result = math.fsum(values)
    except (OverflowError, ValueError) as exc:
        raise ValueError("accounting aggregate is not finite") from exc
    if not math.isfinite(result):
        raise ValueError("accounting aggregate is not finite")
    return result


def _day(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("record dates must be canonical YYYY-MM-DD strings")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("record dates must be canonical YYYY-MM-DD strings") from exc
    if result.isoformat() != value:
        raise ValueError("record dates must be canonical YYYY-MM-DD strings")
    return result


def _checked(records: Iterable[Record]) -> list[tuple[Record, float, float, float]]:
    checked = []
    keys = set()
    for row in records:
        if not isinstance(row, Record):
            raise ValueError("accounting requires Record instances")
        if not isinstance(row.key, str) or not row.key.strip() or row.key in keys:
            raise ValueError("record keys must be nonblank and unique")
        keys.add(row.key)
        if _day(row.opened) > _day(row.closed):
            raise ValueError("record opens after its close")
        gross, cost = _number(row.gross, "gross"), _number(row.cost, "cost")
        if cost < 0:
            raise ValueError("record cost must be nonnegative")
        net = _sum((gross, -cost))
        checked.append((row, gross, cost, net))
    return checked


def summarize(records: Iterable[Record]) -> dict:
    """Return realized net totals, net profit factor and absolute drawdown.

    Empty inputs have zero totals and no profit factor. Profit factor divides
    positive net contributions by the absolute sum of negative contributions;
    it is None when no negative contribution exists. Prefix equity is summed
    independently with fsum (quadratic work, appropriate for small ledgers).
    """
    rows = sorted(_checked(records), key=lambda item: (item[0].closed, item[0].key))
    nets = [item[3] for item in rows]
    gross_total = _sum(item[1] for item in rows)
    cost_total = _sum(item[2] for item in rows)
    net_total = _sum(nets)
    wins = _sum(value for value in nets if value > 0)
    losses = _sum(-value for value in nets if value < 0)
    profit_factor = None if losses == 0 else _number(wins / losses, "profit factor")
    peak = 0.0
    max_drawdown = 0.0
    for position in range(1, len(nets) + 1):
        equity = _sum(nets[:position])
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, _sum((peak, -equity)))
    return {
        "n": len(rows), "gross_total": gross_total, "cost_total": cost_total,
        "net_total": net_total, "mean_net": net_total / len(rows) if rows else 0.0,
        "profit_factor": profit_factor, "max_drawdown": max_drawdown,
        "ordering": "closed_then_key",
    }


def concentration(records: Iterable[Record], remove: int) -> dict:
    """Remove the largest net opening-date cohorts; ties use ascending date.

    The retained total is summed from retained records rather than obtained by
    subtracting two rounded totals. A removal count can include loss cohorts.
    """
    rows = _checked(records)
    cohorts = defaultdict(list)
    for row, _, _, net in rows:
        cohorts[row.opened].append(net)
    if type(remove) is not int or not 0 <= remove <= len(cohorts):
        raise ValueError("remove must be an integer from zero to cohort count")
    totals = {day: _sum(nets) for day, nets in cohorts.items()}
    ordered = sorted(totals, key=lambda day: (-totals[day], day))
    removed = ordered[:remove]
    removed_set = set(removed)
    return {
        "removed_cohorts": removed,
        "removed_total": _sum(net for row, _, _, net in rows if row.opened in removed_set),
        "retained_total": _sum(net for row, _, _, net in rows if row.opened not in removed_set),
        "original_total": _sum(item[3] for item in rows),
        "cohort_count": len(cohorts),
    }
