"""Rebuild the ORB setup and filter study charts from reviewed aggregates.

No private market data, EA, MT5 terminal or account access required.
The charts visualize reported scenario aggregates, not historical broker-net P&L.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from decimal import Decimal
import json
from html import escape
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


def build(data: dict) -> dict[str, str]:
    return {
        "orb-setup-filters-factorial.svg": render_factorial(data),
        "orb-setup-filters-oos.svg": render_oos(data),
        "orb-setup-filters-comparison.svg": render_comparison(data),
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
