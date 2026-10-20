# Published historical aggregate tables

Generated from [historical-results.json](../data/historical-results.json). These are reported private-study aggregates, not a public backtest replay. R means normalized initial planned risk; price-space R and account returns are distinct.

## M2

**MOMCONT** · H021 final decision

Sample: `development`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| long_trades | 272 |
| long_total_r | 33.5558 |
| long_pf_r | 1.4146 |
| long_maxdd_r | 8.427 |
| short_trades | 224 |
| short_total_r | -12.422 |
| short_pf_r | 0.8559 |
| short_maxdd_r | 26.359 |

Recorded historical R-space results; no public raw trade replay. The recent window was already observed. Reported individual-arm uncertainty does not establish positive long alpha.

## M3

**MOMCONT** · H022 trailing ablation

Sample: `development`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| canonical_trades | 249 |
| canonical_total_r | 48.7192 |
| canonical_pf_r | 1.5809 |
| canonical_maxdd_r | 6.221 |
| no_trail_trades | 83 |
| no_trail_total_r | 52.831 |
| no_trail_pf_r | 1.9544 |
| no_trail_maxdd_r | 12.658 |
| matched_events | 64 |
| blocked_canonical_opportunities | 185 |
| paired_mean_delta_r | 0.40772 |

Primary block-100 paired interval NOT ESTIMABLE (64 pairs); all reported sensitivity intervals cross zero. Changed occupancy prevents trade-count equivalence.

## M4_EARLY

**MOMCONT** · H023A cross-era archaeology

Sample: `development`, [2016-01-01, 2020-01-01).

| Metric | Reported value |
| --- | ---: |
| canonical_trades | 652 |
| canonical_total_r | -27.2415 |
| canonical_maxdd_r | 49.192 |
| no_trail_trades | 212 |
| no_trail_total_r | -41.3705 |
| no_trail_maxdd_r | 66.558 |

Retrospective era comparison, not fresh OOS. Early canonical performance is negative. R totals describe different complete occupancy paths.

## M4_MID

**MOMCONT** · H023A cross-era archaeology

Sample: `development`, [2020-01-01, 2025-01-01).

| Metric | Reported value |
| --- | ---: |
| canonical_trades | 915 |
| canonical_total_r | 42.4909 |
| canonical_maxdd_r | 22.791 |
| no_trail_trades | 287 |
| no_trail_total_r | 35.7006 |
| no_trail_maxdd_r | 30.581 |

Retrospective era comparison, not fresh OOS. Early canonical performance is negative. R totals describe different complete occupancy paths.

## M4_RECENT

**MOMCONT** · H023A cross-era archaeology

Sample: `development`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| canonical_trades | 249 |
| canonical_total_r | 48.7192 |
| canonical_maxdd_r | 6.221 |
| no_trail_trades | 83 |
| no_trail_total_r | 52.831 |
| no_trail_maxdd_r | 12.658 |

Retrospective era comparison, not fresh OOS. Early canonical performance is negative. R totals describe different complete occupancy paths.

## M6

**MOMCONT** · H023B frozen exit bake-off

Sample: `development`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| canonical_trades | 249 |
| canonical_total_r | 48.7192 |
| canonical_maxdd_r | 6.221 |
| ratchet_trades | 133 |
| ratchet_total_r | 47.8081 |
| ratchet_maxdd_r | 13.265 |

Six archived controls passed before treatments. Common-entry contrasts are distinct from complete-path strategy effects; no direct promotion.

## M7_BLOCK14

**MOMCONT** · H025 paired portfolio evaluation

Sample: `historical_simulation`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| block_days | 14 |
| paths | 20000 |
| canonical_pass_pct | 97.98 |
| canonical_breach_pct | 1.86 |
| ratchet_pass_pct | 96.82 |
| ratchet_breach_pct | 2.98 |

Conditional historical account simulations, not live success probabilities. Block 14 indeterminate; primary 28 and block 56 favor canonical. Funded conclusion INDETERMINATE across sensitivities.

## M7_BLOCK28

**MOMCONT** · H025 paired portfolio evaluation

Sample: `historical_simulation`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| block_days | 28 |
| paths | 20000 |
| canonical_pass_pct | 98.73 |
| canonical_breach_pct | 1.04 |
| canonical_median_days | 107 |
| ratchet_pass_pct | 96.7 |
| ratchet_breach_pct | 3.1 |
| ratchet_median_days | 110 |

Conditional historical account simulations, not live success probabilities. Block 14 indeterminate; primary 28 and block 56 favor canonical. Funded conclusion INDETERMINATE across sensitivities.

## M7_BLOCK56

**MOMCONT** · H025 paired portfolio evaluation

Sample: `historical_simulation`, [2025-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| block_days | 56 |
| paths | 20000 |
| canonical_pass_pct | 98.52 |
| canonical_breach_pct | 1.34 |
| ratchet_pass_pct | 95.31 |
| ratchet_breach_pct | 4.58 |

Conditional historical account simulations, not live success probabilities. Block 14 indeterminate; primary 28 and block 56 favor canonical. Funded conclusion INDETERMINATE across sensitivities.

## D2

**DE30** · H002 development and H003 concentration rejection

Sample: `development`, [2020-01-29, 2025-01-01).

| Metric | Reported value |
| --- | ---: |
| trades | 837 |
| total_r | 41.4607 |
| pf_r | 1.1412 |
| maxdd_r | 20.0313 |
| remove_top10_date_total_r | -5.4293 |
| remove_top10_date_pf_r | 0.9815 |

H003 NOT SUPPORTED. Top complete entry-date cohorts selected by realized aggregate contribution; this is a stress, not an attainable deletion rule.

## D4

**DE30** · H004 terminal spent lockbox

Sample: `historical_oos_spent`, [2025-01-01, 2026-09-01).

| Metric | Reported value |
| --- | ---: |
| trades | 300 |
| total_r | 21.0171 |
| pf_r | 1.2096 |
| maxdd_r | 15.0985 |
| remove_best_trade_total_r | 16.8873 |
| remove_top3_date_total_r | 9.8748 |
| top3_date_contribution_pct | 53 |

One-shot terminal evaluation passed recorded gates but did not erase H003 rejection. Top-ten-date removal remained negative. Full historical access sequence not independently audited in this publication.

## D7

**DE30** · H005 final engineering gate and canonicalization amendment

Sample: `engineering_replay`, [2020-01-29, 2025-01-01).

| Metric | Reported value |
| --- | ---: |
| trades | 837 |
| parity_trades | 837 |
| requested_risk_pct | 0.5 |
| before_median_actual_risk_pct | 0.06032 |
| after_median_actual_risk_pct | 0.49605 |
| after_p05_actual_risk_pct | 0.48763 |
| after_max_actual_risk_pct | 0.50004 |
| price_abs_tolerance | 1e-09 |

Known-development replay only. Redundant floating-point actual prices use a disclosed narrow absolute tolerance; semantic event fields stay exact. Runtime and monetary qualification remain separate.

## N1

**NOWICK** · H004 matched event study final analysis

Sample: `retrospective_event_study`, [2020-01-31, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| events | 639057 |
| matched_events | 53605 |
| controls_per_event | 5 |
| bootstrap_repetitions | 10000 |
| estimate | 0.078668 |
| ci_low | -0.50361 |
| ci_high | 0.667196 |

Estimate and interval in percentage points of continuation probability; day-cluster 95% interval. Association, not causal proof or executable profitability.

## N2_CELL1

**ANTI-NOWICK** · R001 independent frozen reversal final decision

Sample: `discovery_reversal`, [2020-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| matched_events | 8324 |
| controls_per_event | 5 |
| estimate | -0.111939 |
| ci_low | -0.177759 |
| ci_high | -0.047463 |
| holm_adjusted_p | 1 |

Net reverse-minus-matched-control fixed-clock markout in ATR units, week-cluster 95% interval. Discovery-contaminated history. Research Bid/Ask cost assumptions, not historical fills. All three cells rejected; no reversed EA.

## N2_CELL2

**ANTI-NOWICK** · R001 independent frozen reversal final decision

Sample: `discovery_reversal`, [2020-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| matched_events | 5181 |
| controls_per_event | 5 |
| estimate | -0.10032 |
| ci_low | -0.188084 |
| ci_high | -0.013322 |
| holm_adjusted_p | 1 |

Net reverse-minus-matched-control fixed-clock markout in ATR units, week-cluster 95% interval. Discovery-contaminated history. Research Bid/Ask cost assumptions, not historical fills. All three cells rejected; no reversed EA.

## N2_CELL3

**ANTI-NOWICK** · R001 independent frozen reversal final decision

Sample: `discovery_reversal`, [2020-01-01, 2026-08-01).

| Metric | Reported value |
| --- | ---: |
| matched_events | 1395 |
| controls_per_event | 5 |
| estimate | -0.058142 |
| ci_low | -0.145536 |
| ci_high | 0.02906 |
| holm_adjusted_p | 1 |

Net reverse-minus-matched-control fixed-clock markout in ATR units, week-cluster 95% interval. Discovery-contaminated history. Research Bid/Ask cost assumptions, not historical fills. All three cells rejected; no reversed EA.

## O1

**ORB** · USTEC mechanism controls completed analysis

Sample: `development`, [2020-01-29, 2025-01-01).

| Metric | Reported value |
| --- | ---: |
| surface_cells | 1728 |
| plateau_cells | 18 |
| actual_median_mean_r | 0.08408 |
| close_control_median_mean_r | 0.07629 |
| open_control_median_mean_r | 0.08387 |
| actual_beats_close_cells | 6 |
| actual_beats_open_cells | 9 |
| paired_actual_minus_close_median_r | -0.011284055 |
| paired_actual_minus_open_median_r | 0.011479266 |

Median cell-level mean R over frozen 18-cell region. Same-width constructed-range controls on real market history, not synthetic outcomes. Small differences do not identify unique causal geometry.

## O2_A

**ORB** · USTEC standalone OOS-A completed analysis

Sample: `historical_oos_spent`, [2025-01-01, 2026-01-01).

| Metric | Reported value |
| --- | ---: |
| trades | 124 |
| total_r | 26.412958684602135 |
| pf_r | 1.3815404877055002 |

Signal eligibility window; January 2026 burnoff closes existing lifecycles. Price-space R, monetary parity not certified. This block passed its frozen gates.

## O2_B

**ORB** · USTEC standalone OOS-B completed analysis

Sample: `historical_oos_spent`, [2026-02-01, 2026-07-01).

| Metric | Reported value |
| --- | ---: |
| trades | 53 |
| total_r | -0.5763919629236827 |
| pf_r | 0.9820990189796721 |

Signal eligibility window; July 2026 burnoff. Primary and surrounding plateau failed. Do not pool away the standalone failure; no fresh OOS remains in these dates.

## O5

**ORB** · XAU terminal lockbox completed review

Sample: `historical_oos_spent`, [2026-01-01, 2026-07-01).

| Metric | Reported value |
| --- | ---: |
| candidate_a_trades | 53 |
| candidate_a_pf_money | 0.68 |
| candidate_c_trades | 51 |
| candidate_c_pf_money | 1 |

January-June eligible signals, July burnoff. Source PFs rounded to two decimals; monetary profit factor, distinct from USTEC price-space PF_R. A negative and C effectively flat; lineage closed.
