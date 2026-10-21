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

## Rights and reproduction boundary

[Tardis's use conditions](https://docs.tardis.dev/faq/general.md#what-can-i-use-the-data-for) permit research and publication of non-reconstructible statistics; raw redistribution remains prohibited. Binance BTCUSDT is used; Coinbase data are excluded. Free first-of-month access determines the sample and limits generalization. The [acquisition identity receipt](../data/bbo-acquisition.json) records the protocol, source, compressed-file hash and contemporaneous documentation hashes. Those retained receipts are evidence of the declared workflow, not independently authenticated network-access logs or candidate authorship.

Download the original file privately under the provider's terms, then replay its aggregate qualification:

```sh
python scripts/bbo_qualify.py --day 2023-01-01 --raw-file /private/cache/BTCUSDT.csv.gz --check data/bbo-development-qualification.json
```

The input must stay outside this repository. The command verifies the raw identity and every retained result field, including method hashes, and fails on changed bytes, corrupt gzip or file-qualification errors. Ordinary CI uses original synthetic fixtures without downloading proprietary market data. The completed ECB study and its negative reference-rate finding remain unchanged.
