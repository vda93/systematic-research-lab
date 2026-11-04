# Engulfing Bar Play: when order rules change the experiment

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

An engulfing candle looks easy to define on a chart. The harder question is which later setups can become trades while an earlier retracement order waits to fill. Alternative pending-order policies changed the trade population dramatically; the research retained those differences instead of choosing a winning interpretation.

## From engulfing candle to retracement order

An engulfing bar can sweep the previous candle's high or low and close beyond the opposite side of the previous candle's body. The two candles need not have opposite colors. This is typically framed as a higher-timeframe swing setup, with a focus on four-hour charts and above.

In one explicit ruleset, a close within roughly **15%** of the engulfing candle's extreme is treated as a stronger setup, with a limit entry at **25% retracement**, stop at **75% retracement** and **2R target**. A less decisive close uses entry at **50% retracement**, a stop at the retracement origin and the same **2R target**. Optional management rules include breakeven after a fresh high or low, limiting simultaneous trades per instrument and evaluating indecisive candles in context.

Each tested contract specifies which of these mechanics it implements. The results below distinguish historical replays, a repaired Discovery surface and an observational mechanism test. [Evidence and reproducibility limits](../docs/provenance.md) apply throughout.

## Pending-order lifetime changed which signals could trade [B21](../docs/evidence.md#b21)

Corrected-source EBP revalidation exposed a negative original Gold result: **1,039 closed trades**, **-102.5982R**, and profit factor **0.8373** over its already-inspected historical window. Separately, a source-faithful Python interpretation produced only three closed trades because one long-lived pending order blocked later setups. Its positive **+1R** aggregate failed exposure and stability gates and was parked. A good-till-cancelled (GTC) order can occupy the entry slot while later signals pass; replacing it changes which opportunities reach the market.

A frozen ambiguity matrix made that dependency visible. Two replacement-policy arms produced **1,257** and **1,297** trades, with totals **-119.4104R** and **-94.9029R**, while the GTC arms remained sparse. No interpretation was selected as a winner. These are different contracts and cannot be pooled as repeated confirmation of one strategy. Order lifetime and occupancy belong in the strategy specification before outcomes are interpreted.


## Repairing the signal clock before comparing timeframes [B22](../docs/evidence.md#b22)

The original timeframe matrix had a configuration defect: non-H4 chart periods still used an H4 signal clock. The repaired TF001R2 study verified **88 of 88 native-timeframe cells**, spanning eleven instruments and **152,753 closed trades** in 2020 to 2023. Only **25 cells** were positive; all eleven M15 cells were negative. Even the H4 pooled mean was approximately **+0.00633 price-R** per trade.

This is a Discovery topology map, not a best-cell competition or fresh OOS. Previously frozen candidates remained unchanged. Their separate validation records were mixed: a GBPUSD survivor retained qualification work, a USDJPY lockbox was weak, and a Nasdaq H4 candidate failed validation. After-cost significance and execution qualification remained separate gates. The repaired matrix did not authorize selecting a new clock or replacing an already-tested candidate after seeing the surface.


## The small-candle association left reversal untested [B23](../docs/evidence.md#b23)

STAT001 froze an observational small-candle mechanism test on three qualified M15 instrument histories from 2020 to 2023. The extraction record contained **28,097 placed opportunities** and **21,917 fills**. The equal-weighted contrast across twelve instrument-year strata was **-0.271784 price-R** for the smaller-versus-larger relative-range quartiles, with a **20,000 month-block bootstrap interval [-0.330415,-0.212793]**; nine strata were negative.

The association was heterogeneous: two instruments drove it while the third was approximately null. Gold was excluded because the exact at-test history identity was unresolved. The frozen negative-association finding was retained, while the parent Anti-EBP program was administratively **PARKED**. No causal stop intervention or reversed executable-economic test followed. An observed disadvantage in the original setup does not establish why it occurred or imply profitable opposite-direction trading.


## Quotes alone could not reconstruct broker acceptance [B24](../docs/evidence.md#b24)

EBP tooling separated reconstructed signal geometry from historical order acceptance. One replay reached a recorded market-closed rejection even though raw quotes existed, followed by acceptance on retry. The quote stream alone could not establish the missing historical session rules or broker constraints. Archived event-tape diagnostics were labeled oracle-assisted; independent causal broker parity remained **INDETERMINATE**.

A separate three-market transportability matrix left all twelve economic executions unrun because a qualified source and historical clock contract were missing, despite recorded engine tests and regression replay. Schedule-loader canaries likewise distinguish schedule consumption and observability from placebo significance. The tooling establishes these engineering limits while leaving the economic tests unrun. Historical session and broker constraints still need independent evidence.
