# ECB-FX-MOM20-v001: complete result tables

Generated from `data/ecb-fx-results.json`. Units are basis points of signed logarithmic
reference-rate change per observation. Executable profitability: **NOT_EVALUATED**.
Intervals are marginal 95% percentile block-bootstrap intervals; primary block length 20.
Only the two final-period primary tests form the confirmatory Holm family.

Frozen family verdict: **NOT_PASS**. The 0.5-bp minimum is an arbitrary
statistical relevance screen, not validated trading economics.

## Temporal roles and unconditional comparators

| Role | Asset | N | Signal | Always long | Always short | Flat | Paired difference | Median difference | Primary 95% CI | Raw p | Holm p | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |
| development | EURUSD | 893 | -0.7952 | +0.0961 | -0.0961 | 0.0000 | -0.8913 | 0.0000 | [-4.4960, +2.9068] | 0.6809 | 1.0000 | DESCRIPTIVE_TEMPORAL_ROLE |
| development | USDJPY | 893 | -1.1741 | +0.6294 | -0.6294 | 0.0000 | -1.8035 | 0.0000 | [-5.7805, +2.1952] | 0.8172 | 1.0000 | DESCRIPTIVE_TEMPORAL_ROLE |
| validation | EURUSD | 750 | +0.4474 | -0.4740 | +0.4740 | 0.0000 | +0.9214 | 0.0000 | [-3.5065, +5.4641] | 0.3434 | 0.6868 | DESCRIPTIVE_TEMPORAL_ROLE |
| validation | USDJPY | 750 | -0.6639 | +2.5532 | -2.5532 | 0.0000 | -3.2171 | 0.0000 | [-8.8202, +2.7711] | 0.8701 | 0.8701 | DESCRIPTIVE_TEMPORAL_ROLE |
| final | EURUSD | 744 | +1.1813 | +1.0922 | -1.0922 | 0.0000 | +0.0892 | 0.0000 | [-3.6932, +3.8362] | 0.4799 | 0.9598 | INCONCLUSIVE |
| final | USDJPY | 744 | -0.0712 | +2.4663 | -2.4663 | 0.0000 | -2.5375 | 0.0000 | [-8.6025, +3.9619] | 0.7840 | 0.9598 | NEGATIVE_COMPARISON |

Development and validation p-values are descriptive; their displayed within-period
Holm calculations do not create additional confirmatory claims.

## Signal counts and target coverage

| Role | Target start | Last target end | N | Asset | Short | Flat | Long |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| development | 2016-07-04 | 2019-12-31 | 893 | EURUSD | 495 | 2 | 396 |
| development | 2016-07-04 | 2019-12-31 | 893 | USDJPY | 400 | 0 | 493 |
| validation | 2020-01-31 | 2022-12-30 | 750 | EURUSD | 404 | 2 | 344 |
| validation | 2020-01-31 | 2022-12-30 | 750 | USDJPY | 324 | 1 | 425 |
| final | 2023-01-31 | 2025-12-31 | 744 | EURUSD | 342 | 0 | 402 |
| final | 2023-01-31 | 2025-12-31 | 744 | USDJPY | 271 | 0 | 473 |

Zero paired differences occur whenever the signal is long: the signal and benchmark
then match exactly. Unchanged targets can create further zeros. A zero median is not
evidence of missing observations.

## All fixed block-length results

These are unadjusted one-sided p-values and marginal intervals. Length 20 is primary;
10 and 60 are sensitivities. Every row uses 9,999 shared-index draws and seed 20261021.

| Role | Block length | Asset | Mean difference | 95% CI | Raw p |
| --- | ---: | --- | ---: | --- | ---: |
| development | 10 | EURUSD | -0.8913 | [-4.8138, +3.0876] | 0.6658 |
| development | 10 | USDJPY | -1.8035 | [-6.1118, +2.4561] | 0.8021 |
| development | 20 | EURUSD | -0.8913 | [-4.4960, +2.9068] | 0.6809 |
| development | 20 | USDJPY | -1.8035 | [-5.7805, +2.1952] | 0.8172 |
| development | 60 | EURUSD | -0.8913 | [-4.3618, +3.1500] | 0.6670 |
| development | 60 | USDJPY | -1.8035 | [-5.6076, +1.7849] | 0.8306 |
| validation | 10 | EURUSD | +0.9214 | [-3.8884, +5.9756] | 0.3478 |
| validation | 10 | USDJPY | -3.2171 | [-9.1868, +2.7556] | 0.8635 |
| validation | 20 | EURUSD | +0.9214 | [-3.5065, +5.4641] | 0.3434 |
| validation | 20 | USDJPY | -3.2171 | [-8.8202, +2.7711] | 0.8701 |
| validation | 60 | EURUSD | +0.9214 | [-2.5806, +4.6021] | 0.3004 |
| validation | 60 | USDJPY | -3.2171 | [-8.6033, +3.5238] | 0.8524 |
| final | 10 | EURUSD | +0.0892 | [-3.6553, +3.8239] | 0.4849 |
| final | 10 | USDJPY | -2.5375 | [-8.3583, +3.6659] | 0.7976 |
| final | 20 | EURUSD | +0.0892 | [-3.6932, +3.8362] | 0.4799 |
| final | 20 | USDJPY | -2.5375 | [-8.6025, +3.9619] | 0.7840 |
| final | 60 | EURUSD | +0.0892 | [-3.5514, +4.2160] | 0.4634 |
| final | 60 | USDJPY | -2.5375 | [-8.1723, +3.9223] | 0.7912 |

## Annual differences and equal-weight pooled contributions

Annual means are descriptive. Contribution equals the annual pooled sum divided by
the full role sample size, so contributions sum to the full pooled mean.

| Role | Year | N | EURUSD mean difference | USDJPY mean difference | Pooled contribution to full mean |
| --- | --- | ---: | ---: | ---: | ---: |
| development | 2016 | 128 | +8.9158 | -13.5521 | -0.3323 |
| development | 2017 | 255 | -6.7306 | -1.5056 | -1.1759 |
| development | 2018 | 255 | -0.4480 | +2.9490 | +0.3571 |
| development | 2019 | 255 | -0.4181 | -0.9566 | -0.1963 |
| validation | 2020 | 235 | -2.4022 | -2.8700 | -0.8260 |
| validation | 2021 | 258 | +1.1616 | -6.7845 | -0.9671 |
| validation | 2022 | 257 | +3.7193 | +0.0467 | +0.6452 |
| final | 2023 | 233 | +0.3890 | -1.0233 | -0.0993 |
| final | 2024 | 256 | +2.9010 | -2.2123 | +0.1185 |
| final | 2025 | 255 | -3.0076 | -4.2476 | -1.2433 |

## Concentration diagnostic

Removing the strongest positive calendar contribution is an outcome-dependent descriptive
diagnostic, without an inferential p-value. The pool is descriptive, not another primary test.

| Role | Full pooled mean | Removed year | Removed contribution | Retained N | Retained pooled mean |
| --- | ---: | --- | ---: | ---: | ---: |
| development | -1.3474 | 2018 | +0.3571 | 638 | -2.3857 |
| validation | -1.1479 | 2022 | +0.6452 | 493 | -2.7279 |
| final | -1.2242 | 2024 | +0.1185 | 488 | -2.0470 |

## Extra-observation delay sensitivity

The fixed target becomes log(P[t+3]/P[t+2]); the signal remains unchanged. Means only,
without additional confirmatory inference. These rows cannot rescue the primary result.

| Role | Asset | N | Signal | Always long | Always short | Paired difference |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| development | EURUSD | 892 | -0.5096 | +0.0882 | -0.0882 | -0.5978 |
| development | USDJPY | 892 | -1.3969 | +0.7159 | -0.7159 | -2.1128 |
| validation | EURUSD | 749 | -1.2611 | -0.4915 | +0.4915 | -0.7695 |
| validation | USDJPY | 749 | -0.4656 | +2.6013 | -2.6013 | -3.0669 |
| final | EURUSD | 743 | +3.3879 | +1.0180 | -1.0180 | +2.3698 |
| final | USDJPY | 743 | -0.1996 | +2.5357 | -2.5357 | -2.7353 |

Source selected-CSV SHA256: `b6aa4be6327be74aab465f95ad1db8e97636fb215b9208b35d1b1744f10815b7`.

The snapshot is a retrieval vintage. Historical publication latency and executable
bid/ask fills are unverified. No cost, carry, financing or net-return estimate is supplied.
