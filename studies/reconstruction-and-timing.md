# Paper reconstruction, calendar signals and timing nulls

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

These studies reconstruct paper rules and test calendar signals or timing explanations. Their numbers come from retained historical reports; the portfolio did not rerun the original market studies. Proprietary inputs and operational configurations remain private. Deployment still requires separate authorization.

## NYDR replication: interpretation uncertainty without a winner search [B17](../docs/evidence.md#b17)

The engineering program implemented a partial paper reconstruction using a qualified alternative FX source and explicit deterministic conventions. The frozen reference produced **754 trades**, **-70.602004R**, and profit factor **0.862078** in 2021 to 2022. Its decision was **INCONCLUSIVE** as a paper replication because original data, code, and several definitions were unavailable. Commission and latency were zero in this reference, so its accounting must remain labeled.

A separately preregistered interpretation census examined **305 frozen cells**. Every combined equal-risk FX cell was nonpositive, and source-supported interpretations remained negative. The positive FX replication claim was rejected under this tested source and contract. This does not falsify every possible author implementation. The work retained source fidelity as the comparison criterion instead of promoting the highest historical cell, kept the Nasdaq result separate, and left the external holdout sealed.


## NYDR news exclusion: improvement was neither robust nor broad [B18](../docs/evidence.md#b18)

H002 tested whether high-impact-news exclusion improved the frozen NYDR reconstruction. Its control parity passed with **1,152 exact semantic trade rows** across three instruments. One exclusion definition worsened combined FX by **7.638183R**. Another improved the total by **15.958832R**, but its mean-per-eligible-session cluster interval crossed zero and the instrument effects disagreed: EURUSD worsened while GBPUSD improved.

The frozen conclusion was **NO_SUPPORT**. The study also retained several predefined accuracy denominators instead of selecting whichever most closely resembled an undefined paper statistic. Neither an aggregate gain nor one favorable instrument overrode the cross-instrument and uncertainty requirements. This is a completed negative mechanism test on the specified paper-period source. It did not reopen the interpretation census, optimize the filter, spend the external holdout, or authorize an execution port.


## NY-open continuation: a discovery subgroup met independent uncertainty [B19](../docs/evidence.md#b19)

The calendar-clean NY-open study contained **982 official-session events** in 2020 to 2023. The generic 60-minute signed return averaged **+3.24 basis points**, with a 95% bootstrap interval **[-0.73,+7.18]** and permutation p **0.118**. The all-weekday hypothesis was parked as inconclusive. A stronger Tuesday subset was explicitly post hoc and became a separate frozen 2024 validation hypothesis.

That validation retained **53 of 53 official Tuesdays**. The mean was **+3.7127 basis points**, with interval **[-9.68,+17.21]** and one-sided shuffled-signal permutation p **0.2848**. It replicated only about one quarter of the Discovery mean and remained **INCONCLUSIVE**. Signed event returns are not a net trading backtest. The branch was parked while 2025 to 2026 remained sealed. The canonical completed decision also supersedes stale local documents that still label the validation pending.


## SSR smoke-test adjudication: valid CSV can differ in raw text [B25](../docs/evidence.md#b25)

A corrected-data baseline smoke produced one completed trade and a native fail-closed marker. Offline review found that its sole failed gate compared raw CSV serialization: the expected 71 unquoted column names and the actual 71 legally quoted cells parsed to exactly the same ordered names. Sixteen of seventeen native gates had passed; semantic header mismatches were zero.

The original failure receipt was preserved, and the validator fix was accepted for a new sealed-package rerun. This is mechanical acceptance with a documented false positive, rather than permission to erase history. One trade does not establish expectancy, archived binary provenance remained a separate issue, and the partial-close path was not exercised. Phase 1 remained blocked pending the required native pass.


## Matched random timing: a bounded falsification test [B26](../docs/evidence.md#b26)

A frozen null study compared four existing strategies with **20,000 matched random-timing paths each**. Paths preserved accepted counts, direction sequence, calendar blocking, ownership, and the respective frozen exit/risk engines. Exact replay passed before inference. Each actual total exceeded its sampled null distribution, with empirical raw p **1/20,001** and four-test Holm-adjusted p **4/20,001**.

| Frozen research family | Replayed trades | Actual total R | Historical window, end exclusive |
| --- | ---: | ---: | --- |
| MOMCONT USDJPY hourly | 272 | +33.555770 | 2025-01-01 to 2026-08-01 |
| MOMCONT Gold hourly | 249 | +48.719219 | 2025-01-01 to 2026-08-01 |
| DE30 corrected-sizing development replay | 837 | +41.693798 | 2020-01-29 to 2025-01-01 |
| Venom frozen Gold development candidate | 188 | +43.098091 | 2020-01-01 to 2026-08-01 |

These are the source study's replayed totals, with its cost/contract definitions. The corrected-sizing DE30 total differs from the earlier H002 path's reported net R; they must not be substituted silently. The extreme rank p-values describe this fixed null design and family, rather than the probability a strategy is profitable. Broader research selection is outside that four-test correction.

The conclusion is that the four frozen historical samples beat this particular matched timing null. It does not establish universal alpha, fresh OOS, or independent cost and broker proof. A combined portfolio null was explicitly **NOT_RUN_DATA_ALIGNMENT**, because the four frozen windows had no common intersection. The individual results stand, while the combined-window result remains unavailable. The random-timing baseline was fixed for falsification, with no search for a more favorable comparison.
