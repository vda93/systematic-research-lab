# Published historical aggregate tables

Generated from [historical-results.json](../data/historical-results.json). These are reported private-study aggregates, not a public backtest replay. R means normalized initial planned risk; price-space R and account returns are distinct.

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
