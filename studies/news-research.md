# MacroImpulse, NewsScope and event-driven research

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

These entries distinguish completed negative research, uncertain historical associations, support-only stops, data forensics, and engineering qualification. Numerical findings are retained experiment aggregates; this portfolio preparation did not rerun market studies. Underlying proprietary inputs and operational configurations remain private. A favorable historical aggregate, parity check, or accepted research hypothesis does not authorize deployment.

## MacroImpulse and NewsScope: controlled parity with bounded scope [B08](../docs/evidence.md#b08)

I reconstructed an event-driven execution state machine and compared it with a NewsScopeEA reference under controlled events, broker ticks, and parameters. Recorded parity gates covered pending geometry, spread-aware stops, trigger/fill behavior, trailing ratchets, reverse-exit ordering, deletion, commission, and final balances on three FX instruments. This is a controlled engineering comparison. It does not establish full-year event-selection equivalence or standalone NewsScope profitability.

A separate historical timestamp qualification found that the selected news source aligned directly with the qualified UTC clock, without a timestamp shift or DST adjustment. That frozen alignment is an input contract, not proof of publication latency. Preserving these distinctions prevents a successful state-machine comparison from becoming a claim about every broker, every configuration, or the reference vendor's broader performance. Unresolved comparator scope remains explicit rather than silently assumed.


## MacroImpulse baseline bridge and a rejected spread filter [B09](../docs/evidence.md#b09)

The frozen high-impact baseline was evaluated on ten FX pair-year cells in 2023–2024. The recorded aggregate contained **1,396 trades**, spread-only P&L of **+$4,250.48**, and spread-only profit factor **3.6889**. All ten cells were positive. This is historical bridge evidence under its specified accounting, with commission excluded; it is not a net investable-return claim.

A separately frozen spread-filter validation then ran twenty pair-year-arm cells in 2021–2022. Integrity passed, but the treatment reduced spread-only P&L by **$7.62**. No pair or year improved. The filter removed only three completed trades, all profitable, and did not remove the targeted double-trigger losses. The filter was **REJECTED** without retuning. The pair of studies shows why a favorable control and a plausible risk narrative are insufficient reasons to add a particular intervention.


## Sequential reversals: correcting a misleading failure story [B10](../docs/evidence.md#b10)

An early cross-broker interpretation treated two-sided triggering as a broadly toxic mechanism. Later Exness evidence required a narrower account. All **139** inspected double-trigger groups were sequential: the first position had already stopped before the opposite side triggered. First legs lost **$287.99** spread-only, while subsequent reversal legs recovered **$188.22**. Suppressing the second leg would therefore remove meaningful recovery.

Rapid sequences were still descriptively weak: the shortest observed latency groups had negative combined outcomes. That association did not identify a clean intervention, because the failed first leg was already closed and the second leg could recover part of its loss. The universal cross-broker formulation and blanket suppression proposal were rejected; the rapid-state observation remained parked. This preserved a real historical pattern while withdrawing an overly general explanation and avoiding an unjustified management rule.


## Early failure detection: discrimination did not earn an abort rule [B11](../docs/evidence.md#b11)

EventPath research compared early post-trigger states with eventual trade development. The data contained statistical separation, but the frozen operational requirement also limited harm to delayed legitimate impulses. Within the early decision window and a 2% false-abort budget, failure capture did not reach the required 20%. Reported logistic capture was approximately 9.5%, 12.2%, and 7.3% at the tested early checkpoints, with weak leave-one-year-out stability.

The generic early-abort hypothesis was **REJECTED**. Related blanket time stops all worsened spread-only counterfactual P&L, and simple reverse exits reduced failure losses while sacrificing too much successful exposure. These findings show why a useful research instrument and a discriminating classifier can coexist with a poor trading intervention. The relevant question was whether an action improved the complete decision problem, rather than whether failed trades looked different after the fact.


## Trigger-time filters: preserving the information boundary [B12](../docs/evidence.md#b12)

MacroImpulse studies tested breadth, pre-trigger drift, and prediction of future double triggering. The work distinguished eventual event labels from information actually available when a trade triggered. Events that eventually involved many pairs looked attractive, but causal trigger-time breadth did not support the proposed filter. Coarse drift filters likewise failed to produce a robust return/drawdown improvement.

A trigger-time classifier had approximate ROC AUC 0.74, yet at a 2% false-rejection rate captured only about 12% of future double triggers. Its simulated action sacrificed more profitable single-trigger exposure than it saved. These filter hypotheses were **REJECTED**. The methodological result is an explicit information-time discipline: a future label can describe outcomes but cannot enter the feature set before becoming observable. Attractive descriptive grouping and classifier discrimination were insufficient substitutes for the frozen economic decision test.


## Event families and information density: a qualified development association [B13](../docs/evidence.md#b13)

Another MacroImpulse branch examined scheduled event families and simultaneous-release density. Cluster-robust family-only associations were positive for Labor and negative for Growth/Retail. A simple exposure-normalized development allocation improved spread-only P&L by **$149.07**, with a reported cluster-bootstrap 95% interval of approximately **+$39.9 to +$265.3** for the improvement.

However, family and information density were materially related. Adding both attenuated individual coefficients, and the more complex model improved leave-one-year-out predictive MSE by only about **0.13%**. This supports a qualified development ranking, not a causal taxonomy claim. The registry retains the candidate as parked, with later validation and implementation qualification separate. Costs remain spread-only in this finding. Its role in the atlas is to show how a promising association can be preserved alongside confounding, model-complexity, and evidence-period limits.


## Medium-impact research: costs changed the stability conclusion [B14](../docs/evidence.md#b14)

Medium-impact MacroImpulse research used a separately defined event universe. The five-pair 2021–2024 Discovery aggregate contained **638 trades** and **+$1,036.06** spread-only P&L. Applying the documented commission model reduced that to **+$589.46**, with profit factor **1.5827**. A preregistered four-pair candidate improved the adjusted aggregate to **+$639.68** and profit factor **1.7328**.

The candidate still failed its every-year-positive stability requirement: 2021 was **-$16.29** after modeled commission. Commission sensitivity did not repair that failed year. The disposition remained **PARK**. The cost validation is explicitly **documentation-only**, since a same-account deal export was unavailable. This study demonstrates that positive aggregate accounting, positive retained instruments, and favorable concentration can all coexist with a failed frozen stability gate. It does not supply validated live economics or permission to tune away the weak year.


## Calendar forensics: invalid data is different from strategy failure [B15](../docs/evidence.md#b15)

A later medium-impact extension initially appeared to fail in a later historical period. Calendar forensics found a source-content coverage collapse beginning around late 2024. Records still parsed successfully, so a parser success marker could not establish that the event universe remained complete. The canonical interpretation became **INVALID_DATA_UNIVERSE**, superseding the earlier provisional clean-OOS failure.

Vendor-statement context also showed substantial overlap in selected trades alongside different fills and outcomes, reinforcing the need to distinguish event selection, feed coverage, and execution sensitivity. That context does not independently validate the strategy or repair the calendar. The program remains shelved pending a newly qualified data universe. The useful finding is the withdrawal of an invalid scientific conclusion: damaged input coverage cannot earn either a clean strategy rejection or a retrospective success claim.


## Order-free shadow intent: observing requests without creating a trading sink [B16](../docs/evidence.md#b16)

The MacroImpulse engineering lineage also built a native request-composition seam that emitted immutable intent telemetry while order transmission stayed disabled outside a frozen tester reference. In a bounded five-symbol comparison, **11 real-tick reference cases passed 342 exact field checks**. A separate deterministic boundary corpus passed **13 cases**.

The design distinguished no-intent, valid-would-send, and precheck-rejected states. Its purpose was to inspect what the frozen implementation would request without treating an order-disabled early return as a working shadow mode. No shadow runtime or live provider daemon was started at this checkpoint. These are request-parity and boundary-test results, not proof of live provider behavior, broker acceptance, historical economics, or deployment readiness. The record demonstrates a concrete observation interface and an explicit execution boundary.
