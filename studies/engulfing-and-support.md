# Engulfing Bar Play: source rules and implementation sensitivity

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

## The original trading idea, before the statistics

Omar Agag's FX Replay *EBP Strategy (Swing Trading Variation)* describes an engulfing bar that sweeps the previous candle's high or low and closes beyond the opposite side of the prior candle body. The candles need not have opposite colors. The source is a higher-timeframe swing concept, primarily four-hour charts and above.

A close within about 15% of the engulfing candle's extreme is treated as **strong**: the source proposes a limit entry at 25% retracement, stop at 75% retracement and a 2R target. A less decisive close proposes entry at 50% retracement, stop at the retracement origin and the same 2R target. It additionally describes breakeven after a fresh high/low, one active trade per pair until breakeven, and discretionary considerations for very indecisive candles and context.

That is the **source idea**, not a claim that every published test below implements every discretionary clause. Our research problem was that seemingly minor formalization choices, especially pending-order lifetime and replacement, can create radically different trade populations.

The engulfing research includes completed negative tests, uncertain associations and designs that stopped before economic outcomes. The numbers are retained historical aggregates, not new market-study runs. Proprietary inputs and operational configurations remain private; research acceptance or parity alone does not authorize deployment.

## EBP recovery and Python semantics: exposure depends on interpretation [B21](../docs/evidence.md#b21)

Corrected-source EBP revalidation exposed a negative original Gold result: **1,039 closed trades**, **-102.5982R**, and profit factor **0.8373** over its already-inspected historical window. Separately, a source-faithful Python interpretation produced only three closed trades because one long-lived pending order blocked later setups. Its positive **+1R** aggregate failed exposure and stability gates and was parked.

A frozen ambiguity matrix made that dependency visible. Two replacement-policy arms produced **1,257** and **1,297** trades, with totals **-119.4104R** and **-94.9029R**, while the GTC arms remained sparse. No interpretation was selected as a winner. These are different contracts and cannot be pooled as repeated confirmation of one strategy. The record retains how occupancy and pending-order semantics changed exposure. Those historical-replay limits were preserved without choosing an interpretation to manufacture a favorable sample.


## EBP native-timeframe discovery: repairing a misleading matrix [B22](../docs/evidence.md#b22)

The original timeframe matrix had a configuration defect: non-H4 chart periods still used an H4 signal clock. The repaired TF001R2 study verified **88 of 88 native-timeframe cells**, spanning eleven instruments and **152,753 closed trades** in 2020 to 2023. Only **25 cells** were positive; all eleven M15 cells were negative. Even the H4 pooled mean was approximately **+0.00633 price-R** per trade.

This is a Discovery topology map, not a best-cell competition or fresh OOS. Previously frozen candidates remained unchanged. Their separate validation records were mixed: a GBPUSD survivor retained qualification work, a USDJPY lockbox was weak, and a Nasdaq H4 candidate failed validation. After-cost significance and execution qualification remained separate gates. The repaired matrix did not authorize selecting a new clock or replacing an already-tested candidate after seeing the surface.


## EBP STAT001: an association that does not authorize reversal [B23](../docs/evidence.md#b23)

STAT001 froze an observational small-candle mechanism test on three qualified M15 instrument histories from 2020 to 2023. The extraction record contained **28,097 placed opportunities** and **21,917 fills**. The equal-weighted contrast across twelve instrument-year strata was **-0.271784 price-R** for the smaller-versus-larger relative-range quartiles, with a **20,000 month-block bootstrap interval [-0.330415,-0.212793]**; nine strata were negative.

The association was heterogeneous: two instruments drove it while the third was approximately null. Gold was excluded because the exact at-test history identity was unresolved. The frozen negative-association finding was retained, while the parent Anti-EBP program was administratively **PARKED**. No causal stop intervention or reversed executable-economic test followed. An observed disadvantage in the original setup does not establish why it occurred or imply profitable opposite-direction trading.


## EBP transport and broker state: stop where the tape stops [B24](../docs/evidence.md#b24)

EBP tooling separated reconstructed signal geometry from historical order acceptance. One replay reached a recorded market-closed rejection even though raw quotes existed, followed by acceptance on retry. The quote stream alone could not establish the missing historical session rules or broker constraints. Archived event-tape diagnostics were labeled oracle-assisted; independent causal broker parity remained **INDETERMINATE**.

A separate three-market transportability matrix left all twelve economic executions unrun because a qualified source and historical clock contract were missing, despite recorded engine tests and regression replay. Schedule-loader canaries likewise distinguish schedule consumption and observability from placebo significance. The tooling establishes these engineering limits while leaving the economic tests unrun. Missing historical state blocks an independently identified result; copying the reference answer into the simulator would not resolve it.
