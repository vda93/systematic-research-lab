# Empirical methods: identify the actual estimand

[Portfolio](../README.md) · [Research atlas](research-atlas.md) · [Evidence register](evidence.md)

The featured studies compare different objects: ordered executable trade paths, event-pattern versus control outcomes, time-conditioned range configurations and scheduled-release data universes. A positive raw result does not imply a positive incremental signal.

## Make information time and cost units explicit

A normalized trade outcome may divide payoff by planned initial risk, whereas *price-space R* normalizes executable price movement by stop distance. Broker monetary P&L additionally depends on contract specifications, risk sizing, bid/ask, slippage, commission and financing. [Accounting code](../src/srl/accounting.py) demonstrates unit-explicit arithmetic without reconstructing broker fills.

For a fixed-clock long markout, executable entry normally uses Ask and exit uses Bid; the short direction uses the reverse quote sides. Negating a long return without changing executable quote sides is not a correct short comparison. News-event filters must use information observable **before the trade trigger**, rather than future labels.

## Keep discovery separate from validation

A search over many candidate parameter cells rewards configurations selected by favorable noise. The [ORB research](../studies/opening-range.md) examined a representative plateau, width-preserving placebo ranges and independent validation blocks. A correlated 18-cell region is a stability diagnostic, not 18 independent confirmations. The second frozen validation block cannot be excused by pooling it with a favorable first block.

The exact original opening-range PDF defines one discretionary trading approach. Its human-readable rules and an objectively testable software specification need explicit comparison; scientific results apply to the tested rules only.

The separate [ORBINDEX case study](../studies/orbindex.md) searched 3,456 correlated index/clock/duration/direction cells, demanded adjacent timing-duration support, then tested A/B/C as synchronized position-limited portfolios. Even after the source/MT5 parity checks, all later-period fixed-lot gross EUR sums were negative. Historical net costs and fully independent holdout status were not certified. A separate weekly bootstrap procedure failed an exact null-model calibration check and was not used to claim 95% confidence.

## Match comparable events without asserting causality

The [NOWICK event study](../studies/nowick.md) compared trend-aligned wickless-candle events with five matched ordinary-candle controls per qualifying event. Day-cluster inference and an independent week-cluster reversal study test distinct claims. Matching reduces specified differences but does not randomize pattern occurrence or eliminate all confounding.

A failure to establish continuation does not justify reversing trades without a separate cost-aware test.

## Formalize order lifecycle and execution

A persistent limit order, replacement policy or position occupancy changes which future signals can generate entries. The [EBP study](../studies/engulfing-and-support.md) demonstrates why unambiguous candle geometry still permits incompatible backtest interpretations.

[Semantic validation code](../src/srl/validation.py) checks duplicate keys, missing events and narrowly defined field tolerances. An implementation parity PASS does not independently validate historical fills or current broker rules.

## Detect incomplete event populations

The [MacroImpulse calendar forensic case](../studies/data-forensics.md) found a major economic-calendar coverage collapse despite clean parser completion. Events absent from an input are not necessarily malformed rows. The resulting test was invalid for its intended event universe and must not be promoted as a valid economic success or failure.

## What the public tools actually replay

The [historical aggregate validator](../src/srl/historical.py), [renderer](../scripts/render_historical.py) and [diagnostics](../src/srl/diagnostics.py) reproduce selected ORB/NOWICK summaries and deterministic presentation, not private raw trade-level research. The [synthetic methods example](study.md) and [resampling utility](../src/srl/resampling.py) illustrate public, bounded methodology without claiming live alpha.
