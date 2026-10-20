# VWAP events and anchored-continuation support

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

These entries distinguish completed negative research, uncertain historical associations, support-only stops, data forensics, and engineering qualification. Numerical findings are retained experiment aggregates; this portfolio preparation did not rerun market studies. Underlying proprietary inputs and operational configurations remain private. A favorable historical aggregate, parity check, or accepted research hypothesis does not authorize deployment.

## VWAP displacement: structured asymmetry without a confirmed unconditional edge [B01](../docs/evidence.md#b01)

I evaluated displacement from a causal quote-arrival-weighted price reference on Gold and a Nasdaq CFD. This reference is QAVWAP, rather than consolidated exchange volume-weighted price. Gold Discovery covered 2015–2022; the independently preregistered Nasdaq replication covered 2020–2023. Both primary studies were classified **MIXED**. On Gold, the downside 60-minute mean was -0.027430 price units, with a day-cluster 95% interval spanning zero. The Nasdaq counterpart was +0.207842 index-price units, also with an interval spanning zero. These units are instrument prices, rather than ATR-normalized trade returns.

Recovery-path asymmetry was clearer than the mean-return evidence, but a secondary recovery statistic could not replace the primary endpoint. The work preserved year and feed-quality heterogeneity and left validation/OOS unopened. It supports a description of the event population, not an unconditional executable mean-reversion strategy. The bounded pipeline and explicit censoring conventions made the mixed finding inspectable.


## VWAP slope and excursion velocity: separate hypotheses, separate decisions [B02](../docs/evidence.md#b02)

Two preregistered studies investigated why nominally similar displacement events behaved differently. H004 tested a causal reference-slope mechanism. Its registered direction was not supported on either instrument. Gold's continuous coefficient was +0.466764 with a day-bootstrap interval entirely above zero, opposite the hypothesized sign; its quartile contrast remained uncertain. The bounded slope hypothesis was **REJECTED**, without rejecting the entire research program.

H005 examined excursion velocity. Gold's primary coefficient was -0.078161, with a 95% interval [-0.178624,+0.021327]. The Nasdaq estimate did not replicate the Gold direction and also remained uncertain. The recorded H005 decision was **INCONCLUSIVE**, rather than a stronger rejection. Both studies ended at Discovery. This distinction matters: a coherent but uncertain association and a failed directional mechanism deserve different records, even when neither earns promotion.


## VWAP cash-hours and trend context: plausible explanations that failed [B03](../docs/evidence.md#b03)

H006 tested a fixed cash-session context; H007 tested a separately frozen trend-alignment state. Both used the existing Nasdaq Discovery population and dependence-aware uncertainty. For cash hours, the 60-minute aligned-return difference was +0.091160 ATR, with a 95% interval [-0.268488,+0.458278]. For trend alignment, the difference was +0.345473 ATR, with interval [-0.053775,+0.742763]. Both estimates had the opposite sign to their registered negative-direction hypotheses, and both intervals crossed zero.

Each mechanism was **REJECTED** under its own decision rule. Those decisions do not establish that session or trend can never matter, nor do they claim causal identification. They close these specific tests. No alternative session boundary or indicator combination was selected to rescue the result, and the later evidence periods stayed closed. The negative studies prevented familiar market explanations from becoming unsupported strategy filters.


## VWAP return persistence and the previous-session reference [B04](../docs/evidence.md#b04)

H009 tested pre-event return persistence; H011 tested a binary state relative to the preceding session's price reference. Both addressed a frozen 60-minute endpoint. H009's contrast was +0.194883 ATR, with a day-cluster 95% interval [-0.352064,+0.769944], opposite its intended direction. H011's contrast was +0.009448 ATR, with interval [-0.272213,+0.295407], economically small under its registered materiality rule.

Both studies were **REJECTED** for the bounded claims. H009 marked the stopping point for the current simple conditioning search rather than permission to try more lookbacks. H011 retained balanced outcome-coverage diagnostics and legitimate horizon attrition. Secondary horizons did not replace the primary tests. These are historical conditional associations in Discovery, not trading P&L or universal statements about market structure. The untested trend-strength candidate H008 remained parked instead of becoming another rescue experiment.


## Relative activity: support qualification before a result [B05](../docs/evidence.md#b05)

The H010 activity study first audited whether broker tick arrivals could support a causal predictor. The selected measure describes **relative broker/feed activity**, not Nasdaq traded volume. The original design stopped before outcomes: only four events occupied its critical predictor state, insufficient for the registered inference and stability requirements.

A separately preregistered version then evaluated a supported contrast. Its primary difference was +0.171502 ATR, with 95% day-cluster interval [-0.256715,+0.595934]. Only two of four years shared the aggregate sign, and the predefined materiality requirement failed. That version was **REJECTED**; the original version remains a pre-outcome support stop. Treating them as distinct records preserves what was known at each design decision. Neither favorable secondary horizons nor the feed-activity label justify an exchange-volume claim or a promoted strategy.


## Cash-open anchored continuation: close is still below the frozen gate [B06](../docs/evidence.md#b06)

H012 investigated an anchored continuation candidate through pre-entry geometry alone. Its original design generated 121 valid Discovery candidates against a frozen total minimum of 300. A separately preregistered redesign generated 263. The redesigned annual counts were 82, 92, and 89; directional counts were 135 and 128. Annual and directional requirements passed, while the total requirement still failed.

The final interpretation is **PREDICTOR_SUPPORT_BLOCKED**, with the geometry search parked before expectancy. These candidates are not backtested trades. No outcome, target/stop, P&L, MFE/MAE, validation, or OOS result was opened to justify the redesign or evaluate profitability. The practical contribution is a complete causal candidate-construction and leakage-QA record that stops at its evidence boundary. A count numerically near the threshold is insufficient when the gate was frozen in advance.


## Prior-range anchored continuation: an auditable attrition funnel [B07](../docs/evidence.md#b07)

H013 used a distinct prior-range anchor and a fixed candidate geometry. The anchor stage passed, but the candidate stage produced **219 valid candidates** against a required 300. One year's count was 66 against 75, and the short-side count was 81 against 100. The recorded disposition is **PARK / PREDICTOR_SUPPORT_BLOCKED**.

The complete 763-session screening ledger reconciled terminal attrition. Leakage checks included physical truncation, future-data mutation, and confirmation-window probes; the preserved receipt reports zero mismatches in its tested samples. Those checks establish properties of the candidate builder. They do not establish expectancy. No post-entry outcome or later evidence period was accessed. This study is publishable as a support-and-causality audit with a failed gate, while any claim about profitable continuation remains unanswered under the frozen design.
