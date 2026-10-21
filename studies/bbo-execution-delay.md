# Waiting through a spread shock: quote costs and support failures

[Portfolio](../README.md) · [Original protocol](../experiments/bbo-delay-protocol.md) · [Measurement amendment](../experiments/bbo-delay-measurement-v2.md)

The question is whether waiting an additional 500 ms after an observable spread shock lowers the quoted crossing cost of a small externally supplied BTCUSDT order, once midpoint movement and costs are included. This is AI-proposed research. It concerns historical displayed bid/ask, not guaranteed fills, alpha or portfolio returns.

## The first measurement design failed

The original protocol was publicly committed before the first data download. It required a fully known preceding 60 seconds, with quotes expiring after 250 ms and conflicting receive timestamps becoming unknown. The first development day, 2023-01-01, could not support that rule:

| Qualification fact | Observed value |
| --- | ---: |
| Raw native-BBO rows | 4,391,515 |
| Conflicting receive timestamps | 23,678 |
| Known time under the frozen age rule | 97.1400288% of the day |
| Continuous known runs | 48,242 |
| Longest known run | 28.405641 seconds |
| Intents with potentially eligible full histories | 0 / 86,099 |

This is **DEV_FAIL_SUPPORT** for that day, not a negative cost effect, a final-sample result or proof other days fail. High pointwise quote coverage does not imply a fully observed rolling window. Relaxing the old rule after this finding would not turn its failure into success. The [aggregate replay receipt](../data/bbo-development-qualification.json), [streaming source](../src/srl/bbo.py) and [tests](../tests/test_bbo.py) expose the calculation. No raw quotes or reconstructible event-price table is published.

## A separate, support-informed measurement amendment

The amended protocol keeps the economic question, delay, costs, order sides and final gates. It replaces point identification of the entire historical median with bounds over every numeric completion of unknown intervals. A shock is classifiable only when all admissible medians imply the same three-times threshold decision. This changes the eligible population and is disclosed as a new measurement design; it does not rescue the original test.

The amendment was publicly committed before its labels or costs were computed on the already accessed January development file and before further outcome downloads. Development, validation and final periods retain separate roles; a development result is not final validation.

## First development replay under the amendment

On 2023-01-01 the revised measurement classified 58,521 of 86,099 scheduled intents. It found 116 eligible shocks, of which 115 had both primary target quotes. Their descriptive mean saving was **−0.4323 bps** after the fixed 5 bps notional fees and 0.5 bps additional delayed slippage. The mean price saving before these assumptions was 0.06768 bps. These are conditional historical quote comparisons, not realized fills or funded returns.

The day is **FAIL_SUPPORT**: intent eligibility is below 95%, one shock lacks its delayed target, and only 76 of the 116 shocks have enough displayed size at both targets. Future size failures remain in the main price-paired calculation. The separately labelled depth subset, both order sides, normal-state controls and every fixed fee/slippage and latency sensitivity remain in the [coarse day report](../data/bbo-development-first-day-v2.json). One observed day has no bootstrap interval. A descriptive negative mean cannot override failed support or become a final-sample economic rejection.

The [replay engine](../src/srl/bbo_replay.py), [median bounds](../src/srl/bbo_history.py), [side and fee accounting](../src/srl/bbo_accounting.py) and [statistics](../src/srl/bbo_statistics.py) expose the implementation. Tests use original synthetic paths, exact rational bounds and independent decimal accounting. The private worker retains every scheduled intent with diagnostic reasons; public outputs omit raw quotes, event prices and timed intent ledgers. The AI-assisted implementation is inspectable; it does not establish the candidate's unaided technical mastery.

Reproduce this checked day from the independently downloaded, hash-matching source:

The historical per-day receipt binds the original engine revision `2a17530f7c27ddf55e15bd5ba67e1414979921d7`. Use that revision for its exact operational method hashes. The complete-stage route below uses the current controls and separately checks the unchanged scientific calculation core.

```sh
python scripts/bbo_run_day.py --day 2023-01-01 --raw /private/cache/BTCUSDT.csv.gz --output /private/new-day-run --protocol-commit 76c8952ac6a18b6ab167878974f9cf2b4bad89c9 --sha256 366e5d2ae6b8b6decd6628c300661c209e0fcc58e4079416075cfbe46be4ba49
python scripts/bbo_check_day.py --run-directory /private/new-day-run --check data/bbo-development-first-day-v2.json
```

The comparison checks all coarse statistics, raw identity and exact method hashes. It fails on changed source bytes or methods. Private compressed audits include operational metadata and are not expected to reproduce byte for byte. A retained workflow receipt is not an independently authenticated history of data access. Ordinary CI uses synthetic fixtures and never downloads this source.

## Complete development closeout

All twelve planned 2023 first-of-month days completed qualification and replay. They contain **2,421 price-paired primary shock observations** across twelve observed days. The equal-day descriptive mean saving is **−0.41005 bps**, with a primary 95% bootstrap interval of **[−0.50103, −0.31921] bps**; the two-day-block interval is **[−0.50717, −0.30684] bps**. Every daily mean is negative. The [full aggregate](../data/bbo-development-results.json) retains all daily means, leave-one-day-out values, tail penalties, controls, components and fixed sensitivities.

Support fails: no contributing day reaches the 95% intent-eligibility or 99% future-depth threshold, and every day has missing primary targets. Eleven days have at least 100 shocks; July's 47 eligible shocks and 44 paired observations remain in the estimate. Thus this is a **descriptive development finding with failed support**, rather than a confirmatory economic rejection. Price-paired outcomes include insufficient future depth; the separately reported sufficient-depth subset is post-outcome conditioning. No subset or sensitivity rescues support.

The [development closeout](../data/bbo-development-closeout.json) signs off implementation correctness and usable observations, not a positive effect. Validation and final access require a committed complete source/test/dependency manifest and preceding-stage results linked by exact hashes. The [stage guard](../src/srl/bbo_stage.py) verifies local immutable content; the acquisition orchestrator must separately verify public chronology before any new outcome download. Validation and final data remain unaccessed at this closeout.

For each declared source, independently download the exact compressed bytes under the provider's terms and run the private worker into a fresh external directory named `YYYY-MM-DD-v1`. The result file lists source URLs and hashes. Then reproduce every public development statistic in one offline comparison:

```sh
python scripts/bbo_summarize.py --runs /private/stage-runs --stage development --external-gates-passed --check data/bbo-development-results.json
```

The flag is an explicit caller assertion of separately reviewed rights, integrity and stage chronology. It is not inferred from a hash or a test pass. The command verifies complete private artifact inventories, source identities, the seven scientific calculation files and the aggregation module; runner/acquisition/CLI controls have separate operational version histories. Missing planned days stay visible, while an incomplete or changed existing run fails the whole comparison. No network access occurs. Raw quotes, event prices and timed intent ledgers remain private; derived worst observations and quantiles are intentionally published statistics.

## Validation closeout

All twelve fixed 2024 first-of-month days completed replay under the implementation publicly frozen after development. The [validation aggregate](../data/bbo-validation-results.json) contains **2,665 primary price-paired shocks** across 12 contributing days. Its equal-day descriptive mean saving is **−0.17343 bps**, with a primary 95% bootstrap interval of **[−0.28359, −0.04098] bps** and two-day-block interval **[−0.27163, −0.06692] bps**. These are conditional quote comparisons, not fills or net returns. [BB4](../docs/evidence.md#bb4)

Validation remains **DESCRIPTIVE_VALIDATION**, with support.pass=false: coverage, future depth and missing-target support remain explicit below. All planned days, including those below 100 shocks, stay in the aggregate; an undefined day would remain visible rather than being converted to a zero. No side, control, fee or latency cell changes the primary rule.

| Selected day | Eligible shocks | Price pairs | Mean saving, bps | 95% eligibility | 99% depth | No missing targets |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 2024-01-01 | 277 | 266 | −0.32836 | fail | fail | fail |
| 2024-02-01 | 281 | 263 | −0.14544 | fail | fail | fail |
| 2024-03-01 | 302 | 286 | −0.38672 | pass | fail | fail |
| 2024-04-01 | 807 | 751 | −0.26687 | fail | fail | fail |
| 2024-05-01 | 522 | 478 | −0.34559 | fail | fail | fail |
| 2024-06-01 | 29 | 23 | 0.13738 | fail | fail | fail |
| 2024-07-01 | 102 | 96 | −0.21121 | fail | fail | fail |
| 2024-08-01 | 167 | 153 | −0.43076 | fail | fail | fail |
| 2024-09-01 | 83 | 79 | −0.09181 | fail | fail | fail |
| 2024-10-01 | 119 | 107 | −0.14580 | fail | fail | fail |
| 2024-11-01 | 130 | 121 | −0.21605 | fail | fail | fail |
| 2024-12-01 | 52 | 42 | 0.35003 | fail | fail | fail |

The [validation closeout](../data/bbo-validation-closeout.json) binds these result bytes to the same frozen source/test/dependency inventory. READY_FOR_FINAL means the validation replay completed with reviewed correctness; it does not mean economic support passed. The [acquisition chronology](../data/bbo-validation-acquisition.json) records retained local GET receipts after the public development/implementation closeout. These receipts are not independent authentication of provider-access history. Final data remain unaccessed at this validation closeout.

After independently obtaining the declared source bytes under the provider's terms, replay each day into a new external `YYYY-MM-DD-v1` directory using implementation commit `28c779bd94e75b319dcaf065436c96b0359288d8` and the immutable development-closeout commit `e23ef8439a567ab3ad40c22180b3d48af9712dcb`. The worker accepts these through `--implementation-commit` and `--stage-commit`. Then compare every validation statistic offline:

```sh
python scripts/bbo_summarize.py --runs /private/stage-runs --stage validation --external-gates-passed --check data/bbo-validation-results.json
```

## Rights and reproduction boundary

[Tardis's use conditions](https://docs.tardis.dev/faq/general.md#what-can-i-use-the-data-for) permit research and publication of non-reconstructible statistics; raw redistribution remains prohibited. Binance BTCUSDT is used; Coinbase data are excluded. Free first-of-month access determines the sample and limits generalization. The [acquisition identity receipt](../data/bbo-acquisition.json) records the protocol, source, compressed-file hash and contemporaneous documentation hashes. Those retained receipts are evidence of the declared workflow, not independently authenticated network-access logs or candidate authorship.

Download the original file privately under the provider's terms, then replay its aggregate qualification:

```sh
python scripts/bbo_qualify.py --day 2023-01-01 --raw-file /private/cache/BTCUSDT.csv.gz --check data/bbo-development-qualification.json
```

The input must stay outside this repository. The command verifies the raw identity and every retained result field, including method hashes, and fails on changed bytes, corrupt gzip or file-qualification errors. Ordinary CI uses original synthetic fixtures without downloading proprietary market data. The completed ECB study and its negative reference-rate finding remain unchanged.
