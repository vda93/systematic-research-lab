# Research library

These case studies ask what a trading rule predicts, what it costs to act on it and which result determined the decision. Each finding belongs to the market, order rules and historical sample named in its study.

## Does the opening range tell us more than the time of day?

**Opening Range Breakout (ORB) · Tested branches closed for deployment.** The Nasdaq candidate passed its first validation block and failed its second. In a separate gold study, the implementations agreed, but financing erased the discovery gains of both candidates in the monetary comparison. [Nasdaq validation (O2)](../docs/evidence.md#o2) · [Gold parity (O3)](../docs/evidence.md#o3) · [Gold economics (O4)](../docs/evidence.md#o4)

The Nasdaq study used placebo boundaries to test whether the exact range mattered. Gold had its own costs and test periods. Some successor candidates never reached an out-of-sample test and still have no verdict. [Timing controls (O1)](../docs/evidence.md#o1) · [Program closeout (O6)](../docs/evidence.md#o6)

[Read the ORB study](opening-range.md) · [Other ORB branches](opening-range-atlas.md) · [Validation and financing figure](../figures/orb-summary.svg)

## Which engulfing-candle signals actually reach a trade?

**Engulfing Bar Play (EBP) · All order-policy variants parked.** On four-hour gold signals, leaving a retracement order open could block later setups, while replacing it admitted a different set of trades.

The positive good-till-cancelled variants each closed only 3 trades. That left too little evidence to choose an order policy. A separate discovery study corrected how each timeframe generated signals and still found mostly weak results. Neither experiment produced a candidate for trading.

[Read the EBP study](engulfing-and-support.md) · [Order-policy comparison](../docs/evidence.md#b21) · [Repaired timeframe study](../docs/evidence.md#b22) · [Order-policy figure](../figures/ebp-order-policy.svg)

## Did promising opening times hold up in a later period?

**ORBINDEX · Three frozen German index portfolios rejected for economic promotion.** The DE30, JP225 and UK100 discovery search compared overlapping opening times. All three DE30 portfolios subsequently lost euros at fixed lot size before additional commission or financing.

Some portfolios still showed a positive result when price moves were scaled by initial trade risk. That measure answers a different question from fixed-lot profit. Historical broker-net profit remains unverified, and earlier research may already have examined part of the later period. Its independence as a holdout is uncertain.

[Read the ORBINDEX study](orbindex.md) · [Discovery search](../docs/evidence.md#ix1) · [Portfolio construction](../docs/evidence.md#ix2) · [Later-period results and limits](../docs/evidence.md#ix3) · [Fixed-volume EUR figure](../figures/orbindex-economics.svg)

## Could scheduled currency news be traded at the available fills?

**MacroImpulse · Shelved over live execution.** The project owner reported wide fills, large spreads and slippage across brokers around scheduled releases. Those conditions made the strategy impractical to trade. [Owner’s closeout clarification](../docs/provenance.md#macroimpulse-closeout-clarification)

A separate historical test relied on a calendar that missed medium-impact events. The missing releases left profitability on that event universe unresolved. The owner’s account describes a practical stopping decision. The historical reports quantify only their stated cost scenarios.

[Read the MacroImpulse study](news-research.md) · [Calendar investigation](data-forensics.md) · [Historical cost assumptions](../docs/evidence.md#b14) · [Calendar evidence](../docs/evidence.md#b15) · [Calendar coverage figure](../figures/macro-calendar.svg)

## Historical archive and methods

[NOWICK and ANTI-NOWICK](nowick.md) preserves the matched-candle comparison and the decision to shelve the original family. [Closeout record](../docs/evidence.md#n1)

The [research atlas](../docs/research-atlas.md) maps the experiment lineages. [Research engineering](research-engineering.md) explains how the project checks implementations and evidence. The [publishing guide](../docs/research-publishing-guide.md) describes how to trace an article’s findings to their sources.
