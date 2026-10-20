# A result, a stress, and an audit of the inference tool

**All observations and reported outcomes are synthetic.** This is a methods study with a deliberately constructed counterexample and a separate known-data-generator experiment. It is not a market backtest.

## Concentration is a decision gate

The [fixed protocol](../experiments/protocol.json) constructs 24 weekly opening-date cohorts, each with two observations. Both members share an opening date and close two and four calendar days later. Known synthetic cost is 0.125 units per observation. Gross amounts are constructed from the specified net amounts plus that cost.

Twenty-two treatment cohorts contribute -1 unit each; the other two contribute +16 and +12. A losing observation remains inside each winning cohort. Removing a cohort therefore removes both its positive and negative members.

| Quantity | Independent arithmetic in synthetic net units |
| --- | --- |
| Control total | 22 × -0.5 + 3 + 2 = **-6** |
| Treatment total | 22 × -1 + 16 + 12 = **+6** |
| After removing the two best treatment cohorts | +6 - 16 - 12 = **-22** |
| Fixed rule | Retained net must be strictly greater than zero: **REJECT** |

The rule rejects this supplied path even though its aggregate and treatment-minus-control difference are positive. This is a declared sensitivity decision, not a universal rule that concentrated opportunities are invalid. No favorable bootstrap fraction can rescue the failed gate.

The example was designed to make that failure visible. Its protocol is a reproducibility and preregistration **template**, not evidence that a constructed outcome was unknown to its author or registered with an independent party before access.

## Pair the same calendar

Net amounts are recognized on their close dates in an explicit 168-day calendar; inactive days are zero. The two arms have matching supplied event IDs and opening/closing dates. Event correspondence passes before differences are interpreted. Different amounts are intentional.

The [resampling implementation](../src/srl/resampling.py) draws circular moving blocks at the declared lengths of 7, 14 and 28 days, using the same sampled indices for both paths. Its statistic is the daily **mean** treatment-minus-control amount. It is not the difference between two independent bootstrap draws. Blocks wrap at the calendar boundary, and the final block is truncated to preserve the original number of days.

These intervals are conditional on the supplied path and a block model. The fraction of positive bootstrap means is neither a p-value nor a posterior probability that a treatment has a positive effect. The [methods note](methods.md) defines the estimator and assumptions.

## Calibrate the inference tool

A second experiment asks whether a nominal 95% percentile interval actually contains a known ensemble mean. Daily differences follow

$$D_t = 0.75 D_{t-1} + \epsilon_t,$$

where the innovations are independent uniform draws from `[-2, -1, 0, 1, 2] × 0.25`. The state starts at zero, receives a fixed 512-step burn-in, and then supplies 128 observations. Shared synthetic shocks are added to both arms and cancel in the paired difference. Symmetry and a zero initial state imply an ensemble mean of zero at every time; burn-in is not a claim of exact stationary initialization.

The protocol fixes 80 trials, 399 bootstrap replications per trial, and block lengths 1, 8 and 16. Block 1 is the IID-day comparison. Every trial and every declared block length remains in [the result ledger](../results/study.json), including intervals that miss zero.

| Block length | Intervals containing zero | Observed coverage | Monte Carlo SE | Mean interval width |
| --- | ---: | ---: | ---: | ---: |
| 1 day | 42 / 80 | 52.50% | 5.58 percentage points | 0.1797 |
| 8 days | 65 / 80 | 81.25% | 4.36 percentage points | 0.3614 |
| 16 days | 66 / 80 | 82.50% | 4.25 percentage points | 0.3855 |

Widths use synthetic units per calendar day. Monte Carlo SE is `sqrt(p_hat × (1-p_hat) / 80)` for the coverage indicator; it is simulation uncertainty, not the bootstrap interval's own standard error. The same generated trials are used across lengths, so the coverage estimates are correlated. No independent-sample significance test between rows is claimed.

Longer blocks produce wider intervals and higher observed coverage in this fixed experiment. **All declared settings still fall below nominal 95% coverage.** The study retains that deficiency; it does not choose the best-looking length and call the method validated. Eighty trials give only a rough calibration assessment, and a finite audit of one data generator cannot establish universal coverage behavior.

## Correctness and the stop decision

Tests independently check the -6/+6/-22 arithmetic, complete membership, exact seeded small-sample resampling references, shared-index pairing, circular wrap and truncation, missing dates, duplicate identities, nonfinite values, aggregate overflow and narrow numeric tolerance. Artifact tests detect changed result bytes and chart labels that diverge from the computed cohort count or decision.

The final record therefore has two preserved failures: the constructed candidate does not survive its concentration rule, and the chosen inference settings do not achieve nominal coverage in this finite known-null audit. The useful result is an inspectable boundary on the conclusion, with no market or deployment claim attached.
