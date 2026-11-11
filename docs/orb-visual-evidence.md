# ORB figure evidence and discovery matrix

[Illustrated study](../studies/opening-range.md) · [USTEC projection](../data/orb-ustec-public.json) · [Gold projection](../data/orb-gold-public.json) · [Renderer](../scripts/render_orb.py) · [Tests](../tests/test_orb_figures.py)

These publication statuses describe source qualification under the owner's requested publication scope. They are not independent human scientific peer review or trading approval. Every historical figure is **EMPIRICAL_REPORTED / APPROVED AS REPORTED**: the disclosed aggregates and figures reproduce publicly, while the original market backtest remains private. No figure is classified as a publicly replayable market experiment.

## Figure discovery matrix

| Figure | Original experiment and canonical artifact | Sample and units | Status and limitation |
| --- | --- | --- | --- |
| Compact opening summary | EXP-ORB-005/006 and Phase 8D original sources below | Separate USTEC validation total R and gold Discovery monetary-parity USD | APPROVED AS REPORTED. Two distinct panels and accounting bases; no pooled performance. |
| Complete USTEC timing surface | EXP-ORB-003; `SURFACE_SUMMARY.csv`, `PARAMETER_SURFACE.csv`, `CELL_SELECTION_METRICS.parquet` | USTEC2 spent Discovery; 96 New York anchors × six durations × three directions; mean price R/trade | APPROVED AS REPORTED. All 1,728 original cells, no interpolation; commission/financing not qualified. |
| Frozen robustness map | EXP-ORB-003; `SELECTION_MANIFEST.json`, `CELL_SELECTION_METRICS.parquet` | Same Discovery; frozen positive/robust/selected-region flags | APPROVED AS REPORTED. 140 positive, 22 robust, 18 selected-region cells; flags were not recomputed to improve results. |
| Maximum versus medoid | EXP-ORB-003; `TAIL_CONCENTRATION_REPORT.json`, `SELECTED_CELL.json` | Same Discovery; total price R and original annual medoid totals | APPROVED AS REPORTED. Largest absolute-R removal is a sensitivity diagnostic; raw outcomes unchanged. |
| Paired placebo comparisons | EXP-ORB-004; `MECHANISM_CELL_COMPARISONS.parquet` | Posthoc Discovery mechanism study; paired differences in configuration mean R/trade across the frozen 18-cell region | APPROVED AS REPORTED. Correlated cell comparisons; no invented confidence interval, significance or causal explanation. |
| Separate validation curves | EXP-ORB-005/006; `OOS_PRIMARY_TRADES.csv`, `OOS_B_PRIMARY_TRADES.parquet` | Spent OOS-A 2025; spent OOS-B Feb–Jun 2026; actual UTC exit-month cumulative closed-trade R | APPROVED AS REPORTED. Original rows were hash-checked and aggregated without strategy replay. The failed second gate stays separate. |
| Separate gold surface | OriginalGeometry Phase 6 V004; `SURFACE_METRICS.csv`, `ANALYSIS_MANIFEST.json` | XAUUSD2 spent 2019–2023 Discovery; UTC clock, mean price R/trade | APPROVED AS REPORTED. All 1,728 represented cells: two invalid and 30 valid zero-trade means remain explicitly undefined. This is distinct from older gold baseline surfaces. |
| Gold execution stress | Phase 8C; `CANDIDATE_SCENARIO_METRICS.csv` | Separate 2019–2023 Discovery and 2024–2025 validation; price R/trade under normalized latency/cost shocks | APPROVED AS REPORTED. Full CORE gate includes return, PF and drawdown; shocks are not measured live execution costs. |
| Gold accounting and terminal outcome | Phase 8D `MONETARY_PARITY.csv`, `DEPLOYMENT_FEASIBILITY.csv`; valid `ORB_2026_LOCKBOX_A_C_20260930_092445_REVIEW.zip` | Monetary-parity row aggregates in USD; separately rounded monetary PF from spent Jan–Jun 2026 terminal cohort | APPROVED AS REPORTED. Six synthetic scientific exits; source sizing; no combined A+C portfolio, live account or deployment qualification. |
| Original 8D-R1 financing model and portability counterfactual | Separate original decomposition / broker-portability result tables | Historical original accounting contracts | BLOCKED for an additional empirical decomposition: original dedicated files not recovered in this bounded search. The plotted parity ledger does not replace that experiment. |
| Unopened parked-branch validation | Sealed OOS belonging to separate filtered-momentum and other parked lineages | Unperformed tests | BLOCKED by scope. No sealed files opened; these branches remain unadjudicated. |
| Fibonacci-target equivalence | Illustrative 1-STDV Fibonacci rule versus tested structural target | Rule equivalence | BLOCKED: independently certified equivalence unavailable. The article retains the distinction. |
| New PBO / deflated Sharpe / adjusted p-value | Complete synchronized candidate returns and complete search/selection history | Selection-adjusted inference | BLOCKED: aggregate cells do not supply the required synchronized observations and assumptions. No new statistic was manufactured. |

## Source identity and projection

Both JSON files carry original artifact basenames, archived identities, experiment IDs, actual SHA256 values, source commits where recorded, sample roles, costs and reproducibility limits. Basenames identify original artifacts within their named archive, rather than exposing sensitive machine paths. Hashes identify inspected bytes; they do not prove independent historical broker completeness or a license to redistribute raw market data.

The USTEC aggregation manifest matches the selection manifest's frozen input hash. Both original CSV matrices and the selection Parquet match their original manifests; every projected total and trade count reconciles between the summary and selection rows. The mechanism and OOS input members match their own evidence manifests. Gold surface output hashes match its original analysis manifest. Phase 8C/8D output files match their recorded manifest hashes, including the dependency on the final Phase 8B parity certificate. The valid spent terminal archive matches the retained canonical archive identity; its A/C trade members also match retained original hashes and its ZIP CRC passes. Original acquisition, historical feed completeness and the complete access chronology were not independently re-audited.

Projection rules are deliberately small. USTEC `columns` names each position in the corresponding `cells` arrays; rows retain canonical surface order. Gold arrays retain the original scientific classification. A valid gold mean is total price R divided by completed trades. Invalid cells have no scored mean; valid zero-trade cells also have no mean, but remain a different state. The renderers do not fill absent combinations. Gold surface statistics, USTEC results and later monetary qualification remain separate contracts.

Month-end validation points use original `exit_utc` timestamps and `price_space_r`, summed by UTC exit month for the frozen eligible signal cohort. They are closed-trade summaries, not account equity. OOS-A's January 2026 burnoff was consumed by regional lifecycle completion, although its primary medoid's last closed-trade point is in December 2025. OOS-B includes July burnoff exits. No new signals, fills, exits, optimization or backtest were generated.

Public reproduction requires only the disclosed JSON projections and pinned Python environment. Private source extraction used an additional local Parquet reader; that dependency is unnecessary for public figure regeneration. The primary rows remain private and are not repackaged as public market data. Rebuilding a figure establishes presentation consistency, not private source authenticity by itself.

## Selection contract

The original frozen selection protocol is identified by SHA256 `447a1eb7d704ffe0189f0abb926921e4fde208aa23b8a8fa86f5160844dbe63f` and selection-protocol commit `759e109fffb12c7e232fb209a936029f7bca8bd2`. It was read from the preserved committed experiment record; the figure copies the historical classifications.

- Basic eligibility: at least 300 trades, positive total and mean R, and PF above one.
- Year stability: at least three of four complete years, 2021–2024, positive; positive median full-year mean R. Partial 2020 is descriptive.
- Local support: the same-direction Cartesian neighborhood of the center and adjacent cyclic anchors/duration ranks; at least 60% positive cells, positive median mean R and median PF above one. The center is included; boundary durations have six cells, interior durations nine.
- Robustness requires all three. Within a direction, eight-neighbor connectivity forms regions; eligibility requires at least six robust cells, three anchors and two durations. Directions do not connect.
- Region priorities are size, anchor span, duration span, median R/DD, median mean R and canonical identity. The representative minimizes summed cyclic anchor-step plus duration-rank distance. Frozen local-robustness, R/DD, mean-R and identity tie-breaks follow; the maximum return never substitutes for the medoid.

These definitions explain a historical freeze. They do not authorize reselection. The actual grid durations are 5, 10, 15, 30, 45 and 60 minutes, with 96 quarter-hour anchors. USTEC uses America/New_York; gold uses UTC.

## Gold accounting boundary

The Phase 8D chart groups only its 1,376 reconciled tester monetary rows by candidate and original period. Source row counts are A Discovery 505, A validation 206, C Discovery 453 and C validation 212. This is the monetary-parity population, not a claim that every population in other stages is identical. Six rows are explicitly synthetic scientific exits; the remaining rows retain their physical accounting identity privately.

For each group, recorded net P&L equals recorded gross P&L plus commission, swap and fees. Commission and fees are zero in these particular rows; the difference plotted is swap. Gross here already follows source executable-price accounting, so it is not a frictionless midquote return. Amounts use the source position sizes and are not account percentage returns or a pooled candidate portfolio.

| Candidate / period | Trades | Before financing (USD) | Recorded swap (USD) | After recorded costs (USD) |
| --- | ---: | ---: | ---: | ---: |
| A Discovery | 505 | 1,590.72 | −1,973.73 | −383.01 |
| A validation | 206 | 2,782.74 | −438.42 | 2,344.32 |
| C Discovery | 453 | 1,977.72 | −2,631.86 | −654.14 |
| C validation | 212 | 2,174.85 | −713.37 | 1,461.48 |

Discovery eligible sessions end November 2023; validation ends November 2025; each final December is lifecycle burnoff. All 22 frozen policy/risk configurations failed the complete deployment feasibility gate. The separate terminal PF bars use the previously approved two-decimal historical report: A 0.68 and C 1.00, with 53 and 51 trades respectively. Rounding does not certify exact breakeven or live investability.

## Missing-evidence handoff

To add the blocked original financing/portability comparison, supply the completed 8D-R1 cost decomposition and IC Markets counterfactual tables with their original archived identity, manifest, hashes, definitions and publication rights. To establish target equivalence, supply a reviewed derivation tying the exact structural calculation to the illustrative Fibonacci rule. Do not rerun strategies or open sealed samples to fill either gap. Connected Drive access was tested successfully in this session; local primary evidence supplied the plotted rows.

## Reproduce

```sh
python -m scripts.render_orb --check
python -m unittest tests.test_orb_figures
python scripts/reproduce.py --check
```

The owner directed the research and publication scope; agents recovered evidence, implemented the projection and figures, and assisted with prose. Automated checks and AI reviews are not independent human scientific peer review.
