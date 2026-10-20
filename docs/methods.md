# Estimands, controls and assumptions

This page documents the **synthetic methods appendix** and its public utilities. For real historical studies, read [empirical methods](empirical-methods.md).

## Cost-explicit amounts

For observation i, net amount is `gross_i - cost_i`; costs must be known, nonnegative and finite. Totals use explicit accurate floating-point summation with finite-result checks. Profit factor divides the sum of positive net amounts by the absolute sum of negative net amounts; it is undefined (`None`) when no negative contribution exists.

Drawdown starts at zero and uses net observations in `(closed date, key)` order. A key is a deterministic tie convention, not recovered intraday chronology. Accurate independent prefix sums currently use quadratic work; this deliberate small-ledger implementation is not a high-volume execution engine.

Concentration ranks complete opening-date cohorts by descending net sum, with ascending date breaking ties. The retained amount is summed from retained observations rather than inferred by subtracting rounded reported totals. This removal is a counterfactual sensitivity of supplied records. It does not regenerate market opportunities or account paths.

## Paired circular moving-block bootstrap

The observed statistic is

$$\widehat{\Delta}=\frac{1}{n}\sum_{t=1}^{n}(T_t-C_t).$$

Each replicate draws block starts uniformly from the n observed calendar indices. A block follows consecutive indices with modular wrap; enough blocks are drawn to obtain exactly n indices, truncating the last block if necessary. The replicate mean uses treatment and control on those same indices. The displayed interval is the linear-interpolated 2.5th and 97.5th percentiles of replicate means.

The implementation validates identical canonical, contiguous calendars, including zero-activity days. It requires at least four days, finite scalar amounts, integer parameters, and block length between one and half the sample length. That input restriction prevents a full-sample-block degeneracy; it is not a proof of adequate effective sample size.

The approximation needs dependence to be sufficiently represented inside blocks and the observed window to be a useful stationary approximation. Circular wrap joins the end to the start artificially. Long memory, structural changes, short samples, block choice and Monte Carlo error can undermine coverage. The calibration study makes one such failure inspectable. Increasing replications cannot add new independent observations.

This is a percentile bootstrap for a paired mean. It is not a centered-null hypothesis test, a selection-adjusted p-value, or an account simulation. Coverage across synthetic trials and the positive fraction within one bootstrap distribution are different quantities.

## Semantic event correspondence

`compare_events` aligns rows by a unique nonblank key. Exact fields require both the same scalar type and value. Only explicitly declared numeric fields use an absolute tolerance; there is no implicit relative tolerance. Keys cannot be tolerance fields. Nonfinite scalar values, ambiguous identity and invalid declared field policies are rejected. Two empty paths cannot establish correspondence.

A correspondence PASS establishes only the supplied fields. The study compares its supplied opening/closing event identity; it does not claim to reproduce broker fills, counterfactual occupancy, rejected orders or execution economics.

## Protocol and replay identities

The protocol specifies evidence role, generator, calendar, costs, stress rule, inference settings, all calibration trials and seeds. Unknown keys, duplicate JSON keys, empirical labels and invalid numerical designs fail validation. Canonical sorted JSON identifies the protocol and constructed input records by SHA256.

Committing a manifest is a useful freeze mechanism for subsequent changes, but a digest alone proves neither historical timing nor independent preregistration. This release's constructed counterexample is explicitly known by design. Any future empirical experiment would need a separately established data-access record and protocol frozen before outcomes are seen.

Computation uses full floats. Reporting normally rounds to ten decimal places; a nonzero value is retained at full precision if rounding would erase its sign. This preserves tiny interval signs and coverage decisions. The reproduction command verifies the exact released JSON and SVG bytes rather than silently replacing them.
