"""Rebuild the published Trading Steady ORB charts from reviewed aggregates.

No private market data, EA, MT5 terminal or account access required.
The charts visualize reported scenario aggregates, not historical broker-net P&L.
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "trading-steady-orb-public.json"


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
    rows = data["factorial_cells"]
    if len(rows) != 48 or len({row["id"] for row in rows}) != 48:
        raise ValueError("Expected exactly 48 distinct native factorial configurations")
    by_id = {r["id"]: r for r in rows}
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
        text(25, 484, "Source: TS1 | 48 overlapping models on privately held US500 / USTEC Exness Bid/Ask quotes.", 12, "#526976"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def render_oos(data: dict) -> str:
    rows = data["later_us500"]["results"]
    if len(rows) != 8:
        raise ValueError("Expected four selected US500 configurations in two cohorts")
    keyed = {(r["id"], r["cohort"]): r for r in rows}
    labels = {
        "US500_OR15_LS_A1_E0": "15m Both + ATR",
        "US500_OR15_L_A0_E0": "15m Long",
        "US500_OR15_L_A1_E0": "15m Long + ATR",
        "US500_OR05_L_A0_E0": "5m Long",
    }
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="427" '
        'viewBox="0 0 1020 427" role="img" '
        'aria-label="US500 out-of-sample commission-scenario R for four fixed strategy '
        'configurations in two historical cohorts">',
        rect(0, 0, 1020, 427, "#FBFCFD"),
        text(28, 43, "US500: later historical performance, four frozen variants", 26, "#182D3A", weight=700),
        text(28, 68, "Published-commission-scenario R, verified natural closes only. Cohort A has missing coverage.", 14, "#576A76"),
    ]
    groups = (("A", "A | Jun 2025–Feb 2026", 435), ("B", "B | Apr–Oct 2026", 820))
    for cohort, name, axis in groups:
        out.append(text(axis - 70, 111, name, 16, "#273F4E", "middle", 700))
        out.append(f'<line x1="{axis}" y1="128" x2="{axis}" y2="334" stroke="#4B6573" stroke-width="1.6"/>')
        out.append(text(axis, 355, "0R", 12, "#5A6F78", "middle"))
    for i, (id_, label) in enumerate(labels.items()):
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
        text(28, 382, "A: 187 eligible sessions, one incomplete confirmation window; two cutoff-censored trades across long-only variants.", 12, "#5B6D79"),
        text(28, 404, "B: 148 eligible sessions. Bars are not broker-net results, continuous equity curves, or formal absolute-return tests.", 12, "#5B6D79"),
        "</svg>",
    ))
    return "\n".join(out) + "\n"


def build(data: dict) -> dict[str, str]:
    return {
        "trading-steady-orb-factorial.svg": render_factorial(data),
        "trading-steady-orb-oos.svg": render_oos(data),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figures")
    args = parser.parse_args()
    data = json.loads(DATA.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, svg in build(data).items():
        (args.output / name).write_text(svg, encoding="utf-8")
        print(args.output / name)


if __name__ == "__main__":
    main()
