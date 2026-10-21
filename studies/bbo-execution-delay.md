# Waiting through a spread shock: qualification before economics

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

The amendment must be publicly committed before computing its labels/costs on the already accessed January development file or downloading additional outcome files. The later validation and final periods have not been accessed at this stage. There is no amended economic result to report yet.

## Rights and reproduction boundary

[Tardis's use conditions](https://docs.tardis.dev/faq/general.md#what-can-i-use-the-data-for) permit research and publication of non-reconstructible statistics; raw redistribution remains prohibited. Binance BTCUSDT is used; Coinbase data are excluded. Free first-of-month access determines the sample and limits generalization. The [acquisition identity receipt](../data/bbo-acquisition.json) records the protocol, source, compressed-file hash and contemporaneous documentation hashes. Those retained receipts are evidence of the declared workflow, not independently authenticated network-access logs or candidate authorship.

Download the original file privately under the provider's terms, then replay its aggregate qualification:

```sh
python scripts/bbo_qualify.py --day 2023-01-01 --raw-file /private/cache/BTCUSDT.csv.gz --check data/bbo-development-qualification.json
```

The input must stay outside this repository. The command verifies the raw identity and every retained result field, including method hashes, and fails on changed bytes, corrupt gzip or file-qualification errors. Ordinary CI uses original synthetic fixtures without downloading proprietary market data. The completed ECB study and its negative reference-rate finding remain unchanged.
