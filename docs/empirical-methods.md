# How the studies test a trading idea

[Portfolio](../README.md) · [Research atlas](research-atlas.md) · [Evidence register](evidence.md)

## Measure the outcome in the right units

In ORBINDEX, price R measures the move relative to the trade’s initial price risk. The euro scenario holds lot size fixed. These measures can have different signs across the same set of trades because the initial risk distance varies. A broker cash result also depends on execution, contract terms, commission and financing. [Portfolio economics](../studies/orbindex.md) · [Public accounting code](../src/srl/accounting.py)

For a long trade, entry normally uses Ask and exit uses Bid. For a short trade the quote sides reverse. MacroImpulse also depends on which side triggers an order, when that order can fill and what the trader could observe before acting. A feature observed after a release cannot justify a decision made before it. [Execution comparisons](evidence.md#b08) · [Trigger-time filters](evidence.md#b12)

## Separate selection from evaluation

ORBINDEX searched overlapping market conditions and opening times. Nearby settings help show how sensitive a result is to the clock, but similar settings can share the same trades. The later evaluation fixed the portfolios in advance and treated earlier exposure to the same history as a limitation. [Discovery design](evidence.md#ix1) · [Later evaluation](evidence.md#ix3)

## Account for competing orders

An isolated signal may look attractive even when the portfolio already holds a position and cannot take it. ORBINDEX therefore simulated the portfolio with shared order and position limits. In MacroImpulse, stopping out of the first position could leave another order waiting on the opposite side of the release. [Index portfolio rules](evidence.md#ix2) · [News trade sequences](evidence.md#b10)

[Semantic validation code](../src/srl/validation.py) checks duplicate keys, missing events and field tolerances. Agreement on those fields establishes which behaviors the implementations shared under the test conditions.

## What readers can reproduce

The [index renderer](../scripts/render_orbindex.py) and [news renderer](../scripts/render_macro.py) rebuild exhibits from disclosed aggregates. The [synthetic study](study.md) illustrates inference on artificial data. The original market experiments require their private records and execution code.
