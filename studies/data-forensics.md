# MacroImpulse: when a clean backtest had the wrong event universe

[Portfolio](../README.md) · [Evidence register](../docs/evidence.md#b15) · [Ownership](../docs/ownership.md)

A backtest can complete without execution errors and still answer the wrong scientific question. TradingBotHQ's MacroImpulse MediumImpact study encountered that problem when an apparently failed later-period evaluation was traced to a structural break in the event calendar. The adopted classification became **INVALID_DATA_UNIVERSE**. The failed mechanical output remains part of the record; its interpretation changed after data qualification. ([calendar-forensics record](../docs/evidence.md#b15))

MacroImpulse is an event-driven news-straddle research system. This branch asked whether medium-impact releases supported a distinct opportunity set and whether a frozen measure of activity before a release improved stability. It was researched on retail FX broker data, with AUDUSD, EURUSD, GBPUSD and USDJPY in the primary candidate. This is an event-time experiment: its activity feature uses completed one-minute bars before the release, while execution depends on the quote stream. Calling it a generic “M1 strategy” would obscure that distinction. ([calendar record](../docs/evidence.md#b15), [medium-impact lineage](../docs/evidence.md#b14))

## Define the population before measuring the edge

The development sample was 2021 to 2024. The medium-impact experiment excluded release clusters containing high-impact news, so a medium-labelled observation could not quietly inherit a simultaneous high-impact announcement. A four-pair candidate excluded USDCAD before the pre-event activity rule was frozen. The later activity gate used only information available before the event minute; unavailable features meant skipping the opportunity. These choices defined the population to which any result could apply. ([calendar record](../docs/evidence.md#b15), [medium-impact lineage](../docs/evidence.md#b14))

A backward-validation checkpoint on 29 January to 31 December 2020 passed its recorded gates, but contained only 36 positions. The next evaluation was one combined block from 1 January 2025 through 30 June 2026, with the candidate unchanged. The small earlier checkpoint did not establish robustness by itself. ([calendar-forensics record](../docs/evidence.md#b15))

The later run completed with its execution-integrity checks passing. It produced 50 positions, approximately −$5.72 after the frozen research commission model, and profit factor 0.911. All four recorded economic gates failed. That was the mechanical result. Before accepting it as a clean strategy failure, the researchers noticed an implausibly sparse calendar: only 760 MEDIUM rows across eighteen months. ([calendar-forensics record](../docs/evidence.md#b15))

## Find the break in the source

The subsequent calendar audit dated the structural break to approximately **September to October 2024**, before the nominal OOS block. Total calendar density fell from roughly 900 to 1,100 rows per month to 340 to 435. The final forensic comparison reported 16,288 MEDIUM rows over the sixty months of 2020 to 2024, versus 760 over eighteen later months: 271.47 versus 42.22 per month, about 15.6% of the earlier rate. This compares recorded source density; it does not estimate the exact percentage of real events missing. ([calendar-forensics record](../docs/evidence.md#b15))

The surviving records still carried a successful parsing status. A parser-success rate therefore missed the failure: events absent from the input cannot appear in a rejected-row count. Recurring currency-and-title keys provided another check. Among keys historically dominated by MEDIUM classification, 503 disappeared entirely from the later sample, 34 migrated to LOW, six to HIGH and 35 retained MEDIUM. The recorded diagnosis favored source/content loss over a simple reclassification explanation. ([calendar-forensics record](../docs/evidence.md#b15))

The historical record also preserves a limitation in the audit itself. An earlier section reports 3,246 MEDIUM rows for 2020 and 12,813 for development, which sum to 16,059 rather than the later forensic total of 16,288. The available summary does not reconcile those extraction scopes. The later table supplies the rate comparison above; the discrepancy limits exact reconciliation and is not silently repaired here. ([calendar-forensics record](../docs/evidence.md#b15))

## Challenge the convenient cross-check

Vendor NewsScope trading statements initially looked like an independent check because their trading activity had not collapsed similarly. A follow-up audit corrected that interpretation. Of 1,061 later-period vendor trading minutes, 1,035 matched HIGH-impact events and only two matched MEDIUM. Those accounts could not establish completeness of the MediumImpact calendar. Another 23 apparent unmatched minutes were plausibly clock-calibration artifacts; they were not counted as proof of missing events. ([calendar-forensics record](../docs/evidence.md#b15))

The related strategy's activity covered a different event population, so it could not serve as a reference dataset for MEDIUM completeness. Vendor fill differences still documented execution sensitivity, but did not identify latency as the cause or validate the missing universe.

## Preserve the decision and its limits

On 2 September 2026, the canonical record reclassified the later evaluation as **INVALID_DATA_UNIVERSE**. It required an independently qualified event source before any unchanged-candidate rerun. Local source archaeology reportedly scanned 993 CSVs, detected 341 calendar-like schemas and profiled 334 candidates without finding a source that restored healthy 2025 MEDIUM coverage. This portfolio review did not repeat that scan or reconstruct a corrected OOS result. First-tick MacroImpulse work was subsequently shelved on 4 September. ([calendar-forensics record](../docs/evidence.md#b15))

Costs have a separate evidence limit: the historical commission model was documentation-based, without a same-account deal export for empirical validation. A repaired event calendar alone would not establish realized net profitability. ([cost-accounting record](../docs/evidence.md#b14))

The damaged sample could no longer adjudicate the frozen strategy's economic hypothesis. The record retains the failed output alongside the data-invalidity decision and the correction to the vendor argument, so a reviewer can follow why the interpretation changed.

*The [evidence register](../docs/evidence.md#b15) identifies the retained calendar-forensics decision and its [cost-accounting context](../docs/evidence.md#b14). This original summary was checked against the full canonical decision on 21 October 2026, including its later vendor-audit correction. The original calendar, vendor statements and historical backtest inputs remain private; this page does not independently reproduce their calculations.*

