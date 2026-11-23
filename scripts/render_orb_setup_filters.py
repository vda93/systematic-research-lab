"""Rebuild the ORB setup and filter study charts from reviewed aggregates.

No private market data, EA, MT5 terminal or account access required.
The charts visualize reported scenario aggregates, not historical broker-net P&L.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from html import escape
from math import ceil, floor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "orb-setup-filters-public.json"

SELECTED_LABELS = {
    "US500_OR15_LS_A1_E0": "15m Both + ATR",
    "US500_OR15_L_A0_E0": "15m Long",
    "US500_OR15_L_A1_E0": "15m Long + ATR",
    "US500_OR05_L_A0_E0": "5m Long",
}


def factorial_index(data: dict) -> dict[str, dict]:
    rows = data["factorial_cells"]
    expected = {
        f"{market}_OR{duration:02d}_{side}_A{atr}_E{ema}"
        for market in ("US500", "USTEC")
        for duration in (5, 15, 30)
        for side in ("L", "LS")
        for atr in (0, 1)
        for ema in (0, 1)
    }
    by_id = {row["id"]: row for row in rows}
    if len(rows) != len(expected) or set(by_id) != expected:
        raise ValueError("Expected the complete 48-cell native factorial design")
    for id_, row in by_id.items():
        side = {"LONG_ONLY": "L", "BIDIRECTIONAL": "LS"}[row["direction"]]
        metadata_id = (f'{row["market"]}_OR{row["opening_range_minutes"]:02d}_{side}'
                       f'_A{int(row["atr_enabled"])}_E{int(row["ema200_enabled"])}')
        if metadata_id != id_ or row["closed_trades"] <= 0:
            raise ValueError("Factorial identity or closed-trade denominator is invalid")
    return by_id


def later_index(data: dict) -> dict[tuple[str, str], dict]:
    rows = data["later_us500"]["results"]
    expected = {(id_, cohort) for id_ in SELECTED_LABELS for cohort in ("A", "B")}
    by_id = {(row["id"], row["cohort"]): row for row in rows}
    if len(rows) != len(expected) or set(by_id) != expected:
        raise ValueError("Expected four selected US500 configurations in both cohorts")
    for row in rows:
        if (row["natural_closes"] <= 0 or row["right_censored_entries"] < 0
                or row["entries"] != row["natural_closes"] + row["right_censored_entries"]):
            raise ValueError("Later entries must reconcile to natural closes and censors")
    return by_id


def ema_pair_summary(data: dict) -> dict[str, dict]:
    """Count every matched EMA comparison at the released source precision.

    Direction counts describe this finite discovery surface. They are not
    independent trials or a replacement for the published paired inference.
    """
    rows = factorial_index(data)
    metrics = ("gross_profit_factor", "commission_scenario_R_per_common_day",
               "realized_drawdown_R", "closed_trades", "gross_price_R")
    result = {}
    for market in ("US500", "USTEC"):
        pairs = [(row, rows[id_[:-1] + "1"])
                 for id_, row in rows.items()
                 if row["market"] == market and not row["ema200_enabled"]]
        counts = {}
        for metric in metrics:
            counts[metric] = {
                "higher": sum(on[metric] > off[metric] for off, on in pairs),
                "lower": sum(on[metric] < off[metric] for off, on in pairs),
                "tied_at_reported_precision": sum(on[metric] == off[metric] for off, on in pairs),
            }
        result[market] = {"matched_pairs": len(pairs), "metrics": counts}
    return result


def primary_fixed_trade_costs(data: dict) -> dict:
    """Apply hypothetical extra entry/exit costs to the same observed closes.

    Use Decimal to preserve the published three-decimal aggregate precision.
    This does not reconstruct unrounded source totals, financing or fills.
    """
    rows = later_index(data)
    id_ = data["later_us500"]["primary_candidate_id"]
    primary = [rows[(id_, cohort)] for cohort in ("A", "B")]
    closes = sum(row["natural_closes"] for row in primary)
    base = sum((Decimal(str(row["closed_trade_published_commission_scenario_R"]))
                for row in primary), Decimal(0))
    return {
        "id": id_,
        "natural_closes": closes,
        "combined_published_commission_scenario_R": float(base),
        "scenarios": [
            {"extra_R_per_fill_side": float(cost),
             "extra_round_trip_cost_R": float(2 * closes * cost),
             "closed_trade_scenario_R_after_extra_cost": float(base - 2 * closes * cost)}
            for cost in (Decimal("0"), Decimal("0.025"), Decimal("0.05"))
        ],
    }


def ema_pair_deltas(data: dict) -> dict[str, list[dict]]:
    """Every EMA-on minus EMA-off contrast, on the same common-day basis.

    Decimal subtraction preserves the five-decimal released precision, including
    a small positive effect that would disappear at three decimal places.
    These overlapping configurations are descriptive, not independent trials.
    """
    rows = factorial_index(data)
    result: dict[str, list[dict]] = {}
    metric = "commission_scenario_R_per_common_day"
    for market in ("US500", "USTEC"):
        result[market] = []
        for duration in (5, 15, 30):
            for side in ("L", "LS"):
                for atr in (0, 1):
                    off_id = f"{market}_OR{duration:02d}_{side}_A{atr}_E0"
                    on_id = off_id[:-1] + "1"
                    off, on = (Decimal(str(rows[id_][metric])) for id_ in (off_id, on_id))
                    if not off.is_finite() or not on.is_finite():
                        raise ValueError("EMA effects require finite common-day outcomes")
                    result[market].append({
                        "off_id": off_id, "on_id": on_id, "range_minutes": duration,
                        "direction": "Long" if side == "L" else "Both",
                        "atr_enabled": bool(atr), "delta": float(on - off),
                    })
    return result


def primary_cost_curve(data: dict) -> dict:
    """Fixed observed trades, a hypothetical extra cost per entry and exit.

    The exact break-even coordinate uses the released rounded total, not a
    rounded cost label. No financing, changed fills, or trade reselection occurs.
    """
    summary = primary_fixed_trade_costs(data)
    base = Decimal(str(summary["combined_published_commission_scenario_R"]))
    sides = Decimal(2 * summary["natural_closes"])
    if not base.is_finite():
        raise ValueError("Cost sensitivity requires a finite released total")
    return {
        "id": summary["id"], "natural_closes": summary["natural_closes"],
        "base_R": float(base), "fill_sides": int(sides),
        "break_even_R_per_fill_side": float(base / sides),
        "points": [(float(cost), float(base - sides * cost))
                   for cost in (Decimal(i) / 200 for i in range(11))],
    }


def signal_admission_counts(data: dict) -> list[tuple[str, str, int]]:
    """Reconcile mutually exclusive recorded final statuses, not diagnostics."""
    admission = data["study_design"]["primary_signal_admission"]
    labels = {
        "PRICE_OFF_GRID": "Price grid",
        "ATR_FILTER": "ATR filter",
        "FILLED": "Filled",
        "SESSION_ALREADY_OPEN": "Session occupied",
        "CALENDAR_UNKNOWN_OR_CLOSED": "Calendar",
        "MISSING_PRIOR_BAR": "Missing prior bar",
        "STALE_NEXT_QUOTE": "Stale next quote",
        "STALE_PRIOR_BAR": "Stale prior bar",
    }
    counts = admission["status_counts"]
    total = admission["total_direction_permitted_signals"]
    if (set(counts) != set(labels) or type(total) is not int or total <= 0
            or any(type(count) is not int or count < 0 for count in counts.values())
            or sum(counts.values()) != total):
        raise ValueError("Final signal statuses must be nonnegative and reconcile exactly")
    if admission["id"] not in factorial_index(data):
        raise ValueError("Signal admission must identify a released discovery setup")
    return [(key, label, counts[key]) for key, label in labels.items()]


def period_label(start: str, end_inclusive: str) -> str:
    first, last = date.fromisoformat(start), date.fromisoformat(end_inclusive)
    if last < first:
        raise ValueError("A chart period must end on or after it starts")
    first_label = first.strftime("%b") if first.year == last.year else first.strftime("%b %Y")
    return f"{first_label} to {last.strftime('%b %Y')}"


def discovery_period_label(data: dict, market: str) -> str:
    start, end = data["study_design"]["factorial_periods"][market].split(" through ")
    return period_label(start, end)


def cohort_period_label(data: dict, cohort: str) -> str:
    period = data["later_us500"]["score_periods"][cohort]
    last = date.fromisoformat(period["end_exclusive"]) - timedelta(days=1)
    return period_label(period["start"], last.isoformat())


def rect(x: float, y: float, w: float, h: float, color: str, radius: int = 0) -> str:
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'rx="{radius}" fill="{color}"/>')


def text(x: float, y: float, content: str, size: int = 14,
         color: str = "#243444", align: str = "start", weight: int = 400) -> str:
    return (f'<text x="{x:g}" y="{y:g}" font-family="Arial,sans-serif" '
            f'font-size="{size}" fill="{color}" text-anchor="{align}" '
            f'font-weight="{weight}">{escape(str(content), quote=True)}</text>')


def pf_color(pf: float) -> str:
    if pf < 0.9:
        return "#F4D0C3"
    if pf < 1.0:
        return "#FBE8DF"
    if pf < 1.15:
        return "#E7F0EB"
    if pf < 1.3:
        return "#BDE0D0"
    if pf < 1.5:
        return "#8CCDB4"
    return "#58B08E"


def render_factorial(data: dict) -> str:
    by_id = factorial_index(data)
    source = data["source_evidence"]["factorial"]["source_id"]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="500" '
        'viewBox="0 0 1040 500" role="img" '
        'aria-label="Gross profit factors for 48 fixed opening-range breakout '
        'configurations on US500 and USTEC">',
        rect(0, 0, 1040, 500, "#FBFCFD"),
        text(28, 42, "48 fixed opening-range breakout configurations", 27, "#182D3A", weight=700),
        text(28, 68, "MT5 real-tick gross profit factor | Historical exploration | NOT verified net returns", 15, "#576A76"),
    ]
    labels = [
        ("L", False, False, "Long only"),
        ("L", True, False, "Long + ATR"),
        ("L", False, True, "Long + EMA"),
        ("L", True, True, "Long + both"),
        ("LS", False, False, "Both directions"),
        ("LS", True, False, "Both + ATR"),
        ("LS", False, True, "Both + EMA"),
        ("LS", True, True, "Both + ATR+EMA"),
    ]
    for mi, market in enumerate(("US500", "USTEC")):
        x0 = 195 if mi == 0 else 640
        out.append(text(x0 + 140, 103, market, 20, "#183745", "middle", 700))
        for j, duration in enumerate((5, 15, 30)):
            out.append(text(x0 + j * 91 + 41, 125, f"OR{duration}", 13, "#4E6675", "middle", 600))
        for i, (side, atr, ema, label) in enumerate(labels):
            y = 137 + 36 * i
            if mi == 0:
                out.append(text(24, y + 20, label, 13, "#364C59"))
            for j, duration in enumerate((5, 15, 30)):
                id_ = f"{market}_OR{duration:02d}_{side}_A{int(atr)}_E{int(ema)}"
                pf = float(by_id[id_]["gross_profit_factor"])
                out.append(rect(x0 + j * 91, y, 83, 29, pf_color(pf), 5))
                out.append(text(x0 + j * 91 + 41.5, y + 20, f"{pf:.3f}", 13, "#16323A", "middle", 700))
    out.extend((
        text(25, 461, "PF = gross winning price R / absolute gross losing price R; values do not include commission or financing.", 13, "#526976"),
        text(25, 484, f"Source: {source} | {len(by_id)} overlapping models on privately held US500 / USTEC Exness Bid/Ask quotes.", 12, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def render_oos(data: dict) -> str:
    keyed = later_index(data)
    periods = data["later_us500"]["score_periods"]
    incomplete_a = len(periods["A"]["incomplete_confirmation_sessions"])
    day_label = "day" if incomplete_a == 1 else "days"
    censors_a = sum(row["right_censored_entries"] for (id_, cohort), row in keyed.items() if cohort == "A")
    source = data["source_evidence"]["later_us500"]["source_id"]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="427" '
        'viewBox="0 0 1020 427" role="img" '
        'aria-label="US500 out-of-sample commission-scenario R for four fixed strategy '
        'configurations in two historical cohorts">',
        rect(0, 0, 1020, 427, "#FBFCFD"),
        text(28, 43, "US500: later historical performance, four frozen variants", 26, "#182D3A", weight=700),
        text(28, 68, "Published-commission-scenario R, verified natural closes only. Coverage and censors are noted below.", 14, "#576A76"),
    ]
    groups = tuple((cohort, f"{cohort} | {cohort_period_label(data, cohort)}", axis)
                   for cohort, axis in (("A", 435), ("B", 820)))
    for cohort, name, axis in groups:
        out.append(text(axis - 70, 111, name, 16, "#273F4E", "middle", 700))
        out.append(f'<line x1="{axis}" y1="128" x2="{axis}" y2="334" stroke="#4B6573" stroke-width="1.6"/>')
        out.append(text(axis, 355, "0R", 12, "#5A6F78", "middle"))
    for i, (id_, label) in enumerate(SELECTED_LABELS.items()):
        y = 145 + 51 * i
        out.append(text(24, y + 16, label, 14, "#233D4B"))
        for cohort, _, axis in groups:
            value = float(keyed[(id_, cohort)]["closed_trade_published_commission_scenario_R"])
            width = abs(value) * 13.8
            left = axis - width if value < 0 else axis
            out.append(rect(left, y, width, 26, "#197B66" if value >= 0 else "#B45C43", 4))
            out.append(text(left - 8 if value < 0 else left + width + 8, y + 18,
                            f"{value:+.3f}R", 13, "#243A45",
                            "end" if value < 0 else "start", 700))
    out.extend((
        text(28, 382, f'A: {periods["A"]["eligible_NYSE_days"]} eligible sessions; {incomplete_a} incomplete confirmation {day_label}; '
             f'{censors_a} cutoff-censored entries across variants.', 12, "#5B6D79"),
        text(28, 404, f'B: {periods["B"]["eligible_NYSE_days"]} eligible sessions. Not broker-net returns, continuous equity or absolute-return tests. '
             f'Source: {source}.', 12, "#5B6D79"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def comparison_values(data: dict) -> dict[str, list[tuple[float, int]]]:
    """Match unchanged rules and a gross price-R basis across the three periods.

    Means are derived from reported gross totals and natural-close counts.
    This is a descriptive closed-trade comparison, not complete daily inference.
    """
    discovery = factorial_index(data)
    later = later_index(data)
    result = {}
    for id_ in SELECTED_LABELS:
        row = discovery[id_]
        values = [(row["gross_price_R"] / row["closed_trades"], row["closed_trades"])]
        for cohort in ("A", "B"):
            row = later[(id_, cohort)]
            values.append((row["closed_trade_gross_R"] / row["natural_closes"], row["natural_closes"]))
        result[id_] = values
    return result


def render_comparison(data: dict) -> str:
    comparisons = comparison_values(data)
    periods = data["later_us500"]["score_periods"]
    incomplete_a = len(periods["A"]["incomplete_confirmation_sessions"])
    day_label = "day" if incomplete_a == 1 else "days"
    censors_a = sum(row["right_censored_entries"] for row in data["later_us500"]["results"] if row["cohort"] == "A")
    sources = ", ".join(data["source_evidence"][key]["source_id"] for key in ("factorial", "later_us500"))
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="630" '
        'viewBox="0 0 1120 630" role="img" '
        'aria-label="Same-configuration US500 gross mean R per closed trade in '
        'discovery and two later historical cohorts, with sample counts">',
        rect(0, 0, 1120, 630, "#FBFCFD"),
        text(28, 42, "US500: in-sample discovery vs later historical periods", 26, "#182D3A", weight=700),
        text(28, 69, "Same four configurations, gross mean R per closed trade. EMA is off in every later-tested variant.", 15, "#576A76"),
    ]
    groups = (("In-sample discovery", discovery_period_label(data, "US500"), 365),
              ("Later cohort A", cohort_period_label(data, "A"), 650),
              ("Later cohort B", cohort_period_label(data, "B"), 935))
    scale = 400
    for title, dates, axis in groups:
        out.append(text(axis, 106, title, 17, "#273F4E", "middle", 700))
        out.append(text(axis, 127, dates, 13, "#576A76", "middle"))
        for tick in (-0.2, -0.1, 0.0, 0.1, 0.2):
            x = axis + tick * scale
            out.append(f'<line x1="{x:g}" y1="145" x2="{x:g}" y2="505" '
                       f'stroke="{"#67808C" if tick == 0 else "#DCE5EA"}" '
                       f'stroke-width="{1.5 if tick == 0 else 1}"/>')
            out.append(text(x, 527, "0" if tick == 0 else f"{tick:+.1f}", 12, "#5A6F78", "middle"))
    for i, (id_, label) in enumerate(SELECTED_LABELS.items()):
        y = 158 + i * 91
        out.append(text(28, y + 21, label, 17, "#233D4B", weight=700))
        for index, (value, count) in enumerate(comparisons[id_]):
            axis = groups[index][2]
            width = abs(value) * scale
            left = axis - width if value < 0 else axis
            color = "#416C96" if index == 0 else ("#197B66" if value >= 0 else "#B45C43")
            out.append(rect(left, y, width, 28, color, 3))
            out.append(text(axis, y + 53, f"{value:+.3f}R | n={count}", 14, "#243A45", "middle", 700))
    out.extend((
        text(28, 563, "Price R includes quoted spread, excludes commissions and financing. Sample counts are verified closes.", 13, "#526976"),
        text(28, 586, f'A has {incomplete_a} incomplete confirmation {day_label}; its {censors_a} censored entries are excluded from closed-trade means.', 13, "#526976"),
        text(28, 609, f"Unequal periods and observation coverage: descriptive comparison, not a test of a structural break. Sources: {sources}.", 13, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def line(x1: float, y1: float, x2: float, y2: float, color: str = "#DCE5EA",
         width: float = 1, dash: bool = False) -> str:
    dashed = ' stroke-dasharray="6 5"' if dash else ""
    return (f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
            f'stroke="{color}" stroke-width="{width:g}"{dashed}/>')


def dot(x: float, y: float, color: str, radius: float = 5) -> str:
    return f'<circle cx="{x:g}" cy="{y:g}" r="{radius:g}" fill="{color}"/>'


def chart_start(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="description">{escape(description)}</desc>',
        rect(0, 0, width, height, "#FBFCFD"),
        text(28, 42, title, 26, "#182D3A", weight=700),
    ]


def render_setup(data: dict) -> str:
    """A parameter-bound rule schematic, never a fabricated historical trade."""
    design = data["study_design"]
    candidate = factorial_index(data)[data["later_us500"]["primary_candidate_id"]]
    duration = candidate["opening_range_minutes"]
    anchor = design["opening_range_anchor"].split()[0]
    end = (datetime.strptime(anchor, "%H:%M") + timedelta(minutes=duration)).strftime("%H:%M")
    confirmation = design["first_eligible_confirmation_NY"][f"OR{duration:02d}"]
    target = float(design["take_profit_R"])
    atr, ema = design["atr"], design["ema"]
    source = data["source_evidence"]["factorial"]["source_id"]
    # Abstract geometry. Only the stop/entry/target distances encode a ratio.
    stop_y, entry_y = 460, 370
    target_y = entry_y - target * (stop_y - entry_y)
    out = chart_start(1120, 760, "The opening-range breakout setup", (
        "Illustrative long-entry rule schematic, not historical prices. The prior completed close "
        "is inside the opening range, the signal close is above it, and entry uses the next eligible "
        "Ask quote. Stop and target levels are shown without any post-entry price outcome."))
    out.extend((
        text(28, 71, f"Long example | {duration}-minute range | New York time | Illustrative geometry, not historical prices", 16, "#576A76"),
        rect(100, 396, 220, 64, "#E1EBF2", 4),
        text(130, 435, "Opening range", 17, "#416C96", weight=700),
        line(100, 396, 895, 396, "#8BA5B7", 1.5, True),
        line(100, stop_y, 895, stop_y, "#B45C43", 2),
        line(650, entry_y, 895, entry_y, "#416C96", 2),
        line(650, target_y, 895, target_y, "#197B66", 2, True),
        text(916, target_y + 6, f"{target:g}R target", 19, "#197B66", weight=700),
        text(916, entry_y + 5, "Entry at Ask", 18, "#416C96", weight=700),
        text(916, 417, "Range high", 15, "#576A76"),
        text(916, stop_y + 5, "Stop: range low", 18, "#B45C43", weight=700),
        line(850, target_y, 850, entry_y, "#197B66", 1.5),
        line(842, target_y, 858, target_y, "#197B66", 1.5),
        line(842, entry_y, 858, entry_y, "#197B66", 1.5),
        text(865, (target_y + entry_y) / 2 + 5, f"{target:g}R", 16, "#197B66", weight=700),
        line(850, entry_y, 850, stop_y, "#B45C43", 1.5),
        line(842, stop_y, 858, stop_y, "#B45C43", 1.5),
        text(865, (entry_y + stop_y) / 2 + 6, "1R", 16, "#B45C43", weight=700),
        dot(320, 426, "#416C96", 7),
        dot(490, 382, "#416C96", 7),
        dot(650, entry_y, "#182D3A", 7),
        text(105, 275, "Previous completed", 17, "#243444", weight=700),
        text(105, 300, "M15 close inside", 17, "#243444"),
        line(264, 312, 314, 416, "#8BA5B7", 1.5),
        text(395, 155, "Completed M15 close", 17, "#243444", weight=700),
        text(395, 180, "above the range", 17, "#243444"),
        line(492, 193, 492, 369, "#8BA5B7", 1.5),
        text(602, 303, "Next eligible quote", 17, "#243444", weight=700),
        line(651, 316, 651, 357, "#8BA5B7", 1.5),
        line(100, 500, 795, 500, "#8096A3", 1.5),
    ))
    for x, label in ((100, anchor), (320, end), (490, confirmation), (650, "Next quote")):
        out.extend((line(x, 494, x, 506, "#8096A3", 1.5),
                    text(x, 531, label, 17, "#243444", "middle", 700)))
    out.extend((
        rect(28, 564, 515, 118, "#EDF3F7", 8),
        rect(562, 564, 530, 118, "#EDF3F7", 8),
        text(48, 596, "Optional volatility filter", 19, "#243444", weight=700),
        text(48, 624, f'Range width / ATR({atr["period"]}): {atr["or_width_over_atr_min"]:g} to {atr["or_width_over_atr_max"]:g}', 17, "#416C96"),
        text(48, 651, "Requires a suitably sized opening range.", 16, "#576A76"),
        text(582, 596, f'EMA{ema["period"]}: later discovery addition', 19, "#243444", weight=700),
        text(582, 624, "Long close above EMA; short close below it.", 17, "#416C96"),
        text(582, 651, "Optional filter; equality rejects the signal.", 16, "#576A76"),
        text(28, 713, "Initial price risk is measured from actual entry to the stop. Long exits use Bid; off-grid stop/target prices reject entry.", 14, "#526976"),
        text(28, 739, f"No post-entry outcome is illustrated. Indicators use all available completed CFD M15 bars. Source: {source}.", 14, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def render_ema(data: dict) -> str:
    pairs = ema_pair_deltas(data)
    source = data["source_evidence"]["factorial"]["source_id"]
    max_delta = max(abs(row["delta"]) for rows in pairs.values() for row in rows)
    bound = max(0.005, ceil(max_delta / 0.005) * 0.005)
    scale = 137.5 / bound
    out = chart_start(1120, 790, "What adding EMA changed across every matched pair", (
        "All twenty-four EMA-on minus EMA-off discovery differences in commission-scenario R "
        "per common eligible day, holding range, direction and ATR fixed. Both markets use the same scale."))
    out.append(text(28, 71, "EMA on minus off | Commission-scenario R per common eligible day | Same scale in both markets", 16, "#576A76"))
    out.append(rect(20, 322, 1080, 156, "#F0F4F7", 4))
    for x, label in ((30, "Range"), (110, "Direction"), (230, "ATR")):
        out.append(text(x, 141, label, 15, "#576A76", weight=700))
    centers = {"US500": 497.5, "USTEC": 897.5}
    for market, center in centers.items():
        out.append(text(center, 124, market, 21, "#243444", "middle", 700))
        out.append(text(center + 190, 148, "Change", 13, "#576A76", "end"))
        for i in range(-2, 3):
            tick = bound * i / 2.5
            x = center + tick * scale
            out.append(line(x, 167, x, 641, "#67808C" if i == 0 else "#DCE5EA", 1.6 if i == 0 else 1))
            out.append(text(x, 671, "0" if i == 0 else f"{tick:+.3f}", 14, "#576A76", "middle"))
    for i, row in enumerate(pairs["US500"]):
        y = 186 + i * 39
        out.extend((text(30, y + 5, f'{row["range_minutes"]}m', 17, "#243444", weight=700),
                    text(110, y + 5, row["direction"], 17, "#243444"),
                    text(230, y + 5, "On" if row["atr_enabled"] else "Off", 17, "#243444")))
        for market, center in centers.items():
            delta = pairs[market][i]["delta"]
            x = center + delta * scale
            color = "#197B66" if delta > 0 else ("#B45C43" if delta < 0 else "#576A76")
            out.extend((line(center, y, x, y, color, 2.5), dot(x, y, color, 5.5),
                        text(center + 190, y + 5, f"{delta:+.5f}", 15, color, "end", 700)))
    out.extend((
        text(28, 714, "Positive values favor EMA on. Range, direction and ATR stay fixed within each pair; configurations overlap.", 14, "#526976"),
        text(28, 740, "These are descriptive differences at released precision, not confidence intervals or independent trials.", 14, "#526976"),
        text(28, 766, f"Discovery only; this chart does not establish an out-of-sample improvement. Source: {source}.", 14, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def render_cost_sensitivity(data: dict) -> str:
    curve = primary_cost_curve(data)
    source = data["source_evidence"]["later_us500"]["source_id"]
    values = [value for _, value in curve["points"]]
    low, high = min(-2, floor(min(values) / 2) * 2), max(2, ceil(max(values) / 2) * 2)
    x0, x1, y0, y1 = 105, 1000, 165, 485

    def xpos(cost: float) -> float:
        return x0 + cost / 0.05 * (x1 - x0)

    def ypos(value: float) -> float:
        return y1 - (value - low) / (high - low) * (y1 - y0)

    out = chart_start(1120, 700, "How sensitive was the remaining margin to extra cost?", (
        f'Fixed-trade sensitivity for {curve["natural_closes"]} verified natural closes across two separately initialized '
        f'later US500 cohorts. The released commission-scenario total starts at {curve["base_R"]:.3f} R. '
        "An additional hypothetical cost is subtracted once at entry and once at exit."))
    out.extend((
        text(28, 71, f'US500 | {SELECTED_LABELS[curve["id"]]} | {curve["natural_closes"]} observed natural closes | EMA off', 16, "#576A76"),
        text(x0, 132, "Observed scenario total after extra cost (R)", 16, "#243444", weight=700),
    ))
    for value in range(low, high + 1, 2):
        y = ypos(value)
        out.extend((line(x0, y, x1, y, "#67808C" if value == 0 else "#DCE5EA", 1.6 if value == 0 else 1),
                    text(x0 - 17, y + 5, f"{value:+d}" if value else "0", 15, "#576A76", "end")))
    for i in range(6):
        cost = i / 100
        x = xpos(cost)
        out.extend((line(x, y0, x, y1, "#E6ECEF"),
                    text(x, 515, f"{cost:.2f}", 15, "#576A76", "middle")))
    points = " ".join(f"{xpos(cost):.6f},{ypos(value):.6f}" for cost, value in curve["points"])
    out.append(f'<polyline points="{points}" fill="none" stroke="#416C96" stroke-width="3"/>')
    for index, offset_x, offset_y, align in ((0, 14, -16, "start"), (5, 18, 35, "start"), (10, -14, 34, "end")):
        cost, value = curve["points"][index]
        x, y = xpos(cost), ypos(value)
        out.extend((dot(x, y, "#197B66" if value >= 0 else "#B45C43", 6),
                    text(x + offset_x, y + offset_y, f"{value:+.3f}R", 18, "#243444", align, 700)))
    break_even = curve["break_even_R_per_fill_side"]
    if 0 <= break_even <= 0.05:
        x, y = xpos(break_even), ypos(0)
        out.extend((dot(x, y, "#182D3A", 6), line(x, y0 + 26, x, y - 12, "#8096A3", 1.5, True),
                    text(x + 15, y0 + 3, "Break-even extra cost", 17, "#243444", weight=700),
                    text(x + 15, y0 + 27, f"about {break_even:.4f}R per side", 17, "#243444")))
    out.extend((
        text((x0 + x1) / 2, 550, "Additional hypothetical cost per fill side (R)", 17, "#243444", "middle", 700),
        text(28, 591, f'Fixed-trade arithmetic: R(c) = {curve["base_R"]:.3f} - 2 x {curve["natural_closes"]} x c', 17, "#416C96", weight=700),
        text(28, 625, "Same observed trades and fills; two fill-side debits per close. This is not measured slippage; financing remains extra.", 14, "#526976"),
        text(28, 651, "Rounded released totals across separately initialized cohorts, not a continuous equity curve or complete-cohort return.", 14, "#526976"),
        text(28, 677, f"Quoted spread and the published-commission assumption are already in the starting total. Source: {source}.", 14, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def render_admission(data: dict) -> str:
    rows = signal_admission_counts(data)
    admission = data["study_design"]["primary_signal_admission"]
    total = admission["total_direction_permitted_signals"]
    source = admission["source_id"]
    candidate = factorial_index(data)[admission["id"]]
    top = ceil(max(count for _, _, count in rows) / 100) * 100
    out = chart_start(1120, 730, "Which signals became trades?", (
        f'{total} direction-permitted discovery signals for the selected bidirectional ATR setup, '
        "assigned to mutually exclusive recorded final statuses under the implementation's rejection precedence. "
        "This is a categorical accounting, not a sequential funnel or causal estimate of missed profit."))
    out.append(text(28, 71, f'{candidate["market"]} | {SELECTED_LABELS[admission["id"]]} | EMA off | {total:,} direction-permitted discovery signals', 16, "#576A76"))
    for i in range(5):
        tick = top * i / 4
        x = 310 + tick / top * 600
        out.extend((line(x, 125, x, 542), text(x, 571, f"{tick:g}", 15, "#576A76", "middle")))
    for i, (key, label, count) in enumerate(rows):
        y = 137 + i * 51
        color = "#197B66" if key == "FILLED" else "#8099AC"
        out.extend((text(28, y + 22, label, 18, "#243444", weight=700 if key == "FILLED" else 400),
                    rect(310, y, count / top * 600, 31, color),
                    text(1086, y + 22, f"{count:,} ({100 * count / total:.1f}%)", 17, "#243444", "end", 700)))
    out.extend((
        text(610, 603, "Number of signals, grouped by recorded final status", 17, "#243444", "middle", 700),
        text(28, 641, f"The categories sum to {total:,}; each signal is counted once, according to recorded rejection precedence.", 14, "#526976"),
        text(28, 667, "A signal may violate several conditions. The independent price-grid diagnostic overlaps other checks and is excluded.", 14, "#526976"),
        text(28, 702, f"These are admission outcomes, not a causal estimate of foregone trades or profit. Source: {source}.", 14, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def build(data: dict) -> dict[str, str]:
    return {
        "orb-setup-filters-factorial.svg": render_factorial(data),
        "orb-setup-filters-oos.svg": render_oos(data),
        "orb-setup-filters-comparison.svg": render_comparison(data),
        "orb-setup-filters-setup.svg": render_setup(data),
        "orb-setup-filters-ema.svg": render_ema(data),
        "orb-setup-filters-cost-sensitivity.svg": render_cost_sensitivity(data),
        "orb-setup-filters-admission.svg": render_admission(data),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figures")
    args = parser.parse_args()
    data = json.loads(DATA.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, svg in build(data).items():
        (args.output / name).write_bytes(svg.encode("utf-8"))
        print(args.output / name)


if __name__ == "__main__":
    main()
