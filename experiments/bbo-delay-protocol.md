# Frozen protocol: waiting through a spread shock

Status: **FROZEN DESIGN — EFFECTIVE ONLY AFTER VERIFIED PUBLIC COMMIT**

Question origin: proposed by an AI research agent for this portfolio. The candidate's independent authorship, implementation, review, or technical mastery is not asserted. The protocol and its implementation require independent scrutiny. This study neither changes nor retests the completed ECB reference-rate momentum study.

The public Git commit containing this protocol must precede every outcome-file GET, download, decompression, price inspection, or empirical calculation for this experiment. Record that exact commit, its UTC timestamp, and the protocol's SHA256 in the acquisition receipt. A draft file, a local clock, or this status line is not evidence that the commitment occurred. Outcome-dependent amendments after access make affected comparisons exploratory; preserve the original protocol and all negative results.

## Economic question and competing explanations

For externally supplied small BTCUSDT spot buy/sell intents, does waiting an additional 500 ms after an observable spread shock reduce the **quoted cost of crossing the spread**, after accounting for intervening midpoint movement?

A transient liquidity withdrawal may widen the spread briefly; waiting could lower the spread paid. Alternatively, the withdrawal may accompany information or directional pressure, so an adverse midpoint move offsets the saving. A third explanation is measurement: stale, reconstructed, or unavailable quotes can create apparent savings that cannot be traded. Native best-bid/offer data, receive-time features, age checks, missingness accounting, and explicit size diagnostics distinguish some of these explanations. They do not identify structural causality or establish actual fills.

This is a fixed-policy historical quote comparison. It is not a trading-alpha study, a randomized experiment, a recommendation to delay orders, or evidence of profitable inventory management. The delay decision does not cause the historical market path, and an actual submitted order could change that path. The novelty claimed is this portfolio's explicitly frozen, economically decomposed question and implementation, not discovery of a new microstructure phenomenon.

## Data identity, rights, and acquisition gate

Use only Tardis's **native `book_ticker`** dataset for exchange `binance`, spot symbol `BTCUSDT`. Do not substitute L2-derived `quotes`, another venue, another asset, or another date after observing access or support failures.

- [Official schema](https://docs.tardis.dev/downloadable-csv-files/data-types.md#book_ticker): `exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount`; prices and displayed amounts, UTC epoch microseconds, exchange and local-receipt clocks.
- [Dataset API documentation](https://docs.tardis.dev/downloadable-csv-files/api.md): first day of each month can be downloaded without an API key; files are ordered and partitioned by local receive time. CSVs do not include disconnect events.
- [Official use conditions](https://docs.tardis.dev/faq/general.md#what-can-i-use-the-data-for): research use and publication of non-reconstructible charts, statistics and reports are permitted; raw redistribution/resale is prohibited. The publication exception excludes Coinbase data; Coinbase is outside this study.
- [Collection details](https://docs.tardis.dev/historical-data-details/binance.md) and metadata-only endpoint `https://api.tardis.dev/v1/exchanges/binance` identify coverage. The API documented BTCUSDT `book_ticker` availability during source review. HEAD requests for two prospective dates returned 404; a successful outcome GET is still unverified. Documentation availability is not acquisition success.

Outcome URL template: `https://datasets.tardis.dev/v1/binance/book_ticker/YYYY/MM/01/BTCUSDT.csv.gz`. The explicit manifest contains exactly the 36 dates below; no wildcard date extension.

After commitment, snapshot the controlling terms, schema, collection documentation, and availability metadata with UTC retrieval times and SHA256 hashes before the first outcome GET. Recheck whether those terms permit this nonmonetized educational research and its proposed aggregate publication. If the permission is missing, contradictory, or changed materially, stop with `NOT_RUN_RIGHTS`; do not infer data rights from an open-source client license or from Binance Vision's separate dataset terms.

For every acquisition, retain source URL, HTTP status, UTC request time, byte count, provider integrity metadata, own compressed-file SHA256, decompression/CRC result, and qualification counts. ETags or multipart MD5 values are not substitutes for a full-file SHA256. Fetch serially with at most three attempts for transient network/5xx failures and documented backoff; stop on access restrictions. A 404 is `NOT_RUN_SOURCE_UNAVAILABLE` for the affected file, not permission to replace it. No access keys or paid subscriptions are required or acquired for this protocol.

Raw data, caches, event prices, per-intent outcomes, and tables from which raw prices can be reconstructed remain **private and outside Git**. Public artifacts contain original source code, manifests/hashes, qualification summaries, and coarse aggregate research results. Do not publish sampled tick rows or event-price ledgers under the repository's code license. Check aggregate outputs for reconstructibility before publication; no agency, venue, or vendor endorsement is implied.

## Fixed sample and resource boundaries

Use 00:00:00 through 24:00:00 UTC on the first calendar day of every month in:

| Period | Role | Dates |
|---|---|---|
| 2023 | Engineering/development and descriptive characterization | January 1 through December 1, monthly first days |
| 2024 | Temporal validation | January 1 through December 1, monthly first days |
| 2025 | Final analysis holdout | January 1 through December 1, monthly first days |

All rules below are frozen before accessing **any** of these outcome files. Development permits parser corrections and correctness checks, not tuning the delay, shock threshold, lookback, sample, notional, estimand, or promotion standard. Validation and final access occur only after synthetic tests pass and development qualification is signed off in an immutable receipt. Freeze implementation SHA before validation; access final only after validation is recorded. Scientific-rule changes after development access require a public amendment and cannot preserve the original confirmatory label for already accessed periods.

These are historical public market dates, not globally unseen history. First-of-month selection is imposed by free access and may concentrate calendar flows, weekends, holidays, and funding-related behavior. Results generalize only to the qualified selected BTCUSDT venue-days, not all days, markets, or traders. Schema pages incidentally exposed a few literal BTCUSDT quotes from 2024-01-01; that exposure must remain disclosed. No outcome dataset was intentionally opened in source discovery.

Use one acquisition/compute worker. Limits: 12 GiB total retained compressed outcome data, 2 GiB resident compute memory, 2 GiB additional temporary disk, 120 minutes acquisition time and 120 minutes analysis time. Stream gzip files; do not expand whole days to disk. Maximum compressed file size is 2 GiB. Check free space before each download and leave 5 GiB free. Exceeding a cap yields `NOT_RUN_RESOURCE` or `INCOMPLETE_RESOURCE`; preserve receipts and partial downloads privately without calculating a favorable partial-sample conclusion. Extending a resource cap requires a recorded operational amendment before further outcome access and cannot change scientific rules.

## Quote qualification and information clock

`local_timestamp` is the causal information clock: it records receipt by the historical collector, not receipt by an actual trader. `timestamp` is diagnostic only and may fall back to local time. No feature may use a message received after the intent time. Never sort backward local timestamps into apparent causal order.

Require exact schema, correct exchange/symbol, integral UTC microsecond timestamps within the requested day, and finite strictly positive bid/ask prices and displayed amounts with `bid_price < ask_price`. A malformed schema, backward local timestamp, unsafe archive, corrupt gzip, or unparseable timestamp fails the entire file. Exact duplicate rows at one receive time may be collapsed with a count. Different BBO states sharing one receive timestamp have ambiguous ordering: mark the state at that timestamp invalid until the next strictly later valid state, count it, and do not invent sub-microsecond order. The resulting qualified state times must be strictly increasing.

A nonfinite, nonpositive, locked, or crossed quote invalidates the state until a later valid update; record its reason. Do not silently bridge it. A valid state expires 250 ms after receipt. Between updates it is known only until that expiry; intervals after expiry are unknown, even if the next quote has the same price. Report age and interarrival distributions, invalid intervals, duplicates, equal-time conflicts, gaps, and backward timestamps. No interpolation, crossed-market repair, or unknown-gap forward fill.

Every UTC second `t` from 00:05:00 through 23:59:58 inclusive is an intent. The last second is omitted to keep the longest sensitivity target within the day. Side is `q=+1` (buy) if integer Unix epoch second is even and `q=-1` (sell) if odd. This is an externally fixed alternating-side intent schedule, not a market signal. One side is evaluated at each time; do not average buy and sell at the same instant, which would cancel midpoint drift algebraically. It is not a holdings simulation, a guarantee of inventory neutrality, or a claim that alternating intents actually execute.

The intent state is the last qualified state received **strictly before `t`**, aged at most 250 ms. This conservative convention avoids assigning a same-time message an unproved earlier arrival. Quantity is fixed at intent: `Q=100/m(t)` BTC, where `m(t)=(ask(t)+bid(t))/2`. Require displayed amount on the intended crossing side at intent to be at least `Q`. No future quote, depth, return, or outcome enters intent eligibility.

The feature-history window is `[t-60 seconds,t)`. Compute the time-weighted median of relative spread `s(u)=10000*(ask(u)-bid(u))/m(u)` over piecewise-constant valid states. A quote before the window may seed its beginning only while age remains at most 250 ms. Require the entire 60 seconds to be qualified and known; otherwise record `HISTORY_GAP`, without imputing a median. For a weighted median use the smallest observed spread whose cumulative duration is at least half the valid duration. Require the median strictly positive. A **shock** is `s(t) >= 3*median60(t)`; equality qualifies. Nonshock eligible intents form the fixed normal-state descriptive control. The first five minutes provide warm-up; no observations from the previous day are fetched.

## Policy quotes and retention of failures

Baseline target is `t+50 ms`. Delayed target is `t+550 ms`. At each target take the last qualified BBO received **at or before that target**, with age at most 250 ms. This is an as-of observation, never the first update after a future target. Decision features remain frozen at `t`; target-time quotes serve only as historical outcomes. The difference in targets is exactly 500 ms. The 50 ms is an assumed observation/decision latency, not measured routing performance.

Crossing quote `P(q,T)` is ask for buys and bid for sells. Record target-side displayed amount, quote age, and whether it can cover the fixed `Q`. **Do not drop intents because future displayed depth is insufficient.** Retain their quoted prices in the main quote-cost outcome when a qualified price exists; label them `FUTURE_DEPTH_FAIL` and report how frequently each policy and either policy fails. These are especially uncertain counterfactuals, not fills at undersized quotes.

If a target has no qualified quote, retain the intent with `MISSING_BASELINE_QUOTE`, `MISSING_DELAYED_QUOTE`, or both. Its numeric saving is missing, not zero; do not fabricate a price or remove the row from eligibility totals. Report the exact paired-availability denominator and complete-case estimand. Since missing price outcomes have no defensible finite universal bound, do not claim robustness to their unobserved values. Promotion requires **zero missing target quotes among final eligible shock intents**. Thus a favorable complete-case result cannot rescue outcome-dependent attrition.

Retain every scheduled intent privately, with its side, all eligibility/failure flags, shock label when defined, and target qualification status. Use mutually exclusive primary exclusion reasons in this order: missing intent state; intent state too old/invalid; insufficient intent depth; invalid/incomplete history; nonpositive median. Retain all additional diagnostic flags. Publish day-level totals and reconciliation, not event prices. Do not discard a day because its observed outcome is poor or its shock count is small.

## Accounting, primary estimand, and decomposition

The one-order price cost, in basis points of the original 100 USDT intent, is

`C(q,T) = 10000 * q * Q * (P(q,T)-m(t)) / 100`.

Quantity does not change when prices move. A taker fee assumption `f` bps applies to quote notional at that target: `F(q,T;f)=f*Q*P(q,T)/100` bps of intent notional. Therefore fee costs need not cancel exactly when target prices differ. Fees are hypothetical common rates, not a historical account-tier attestation. Extra adverse slippage `a` bps for the delayed policy is an additive cost on original intent notional. No maker rebate or queue fill is modeled.

Saving is positive when delaying is cheaper:

`S(q,t;f,a) = C(q,T0)+F(q,T0;f) - C(q,T1)-F(q,T1;f) - a`.

**One primary outcome:** `S` at `f=5 bps` and delayed extra slippage `a=0.5 bps`, conditional on the intent-time shock. This is a deliberately conservative policy screen, not an estimate of actual fees/slippage. Compute each day's equal-intent mean saving, then the equal-day mean over all qualified final days containing at least one paired shock intent. Never weight days by number of ticks, shocks, or trading volume. A day with fewer than 100 shocks remains in the analysis and its count remains visible.

For audit, decompose price saving exactly using half-spread `h=(ask-bid)/2`:

`C(T0)-C(T1) = 10000*Q/100 * [h(T0)-h(T1) + q*(m(T0)-m(T1))]`.

Report spread saving, signed midpoint-drift contribution, fee difference and slippage separately, and verify their sum equals total saving numerically. Report buy and sell summaries separately with their intent counts; parity assignment may confound second-level periodicities, so side differences are descriptive. No pooled side result alone identifies adverse selection.

## Support, controls, robustness, and inference

Report all 12 planned final days, including inaccessible/corrupt files and days without eligible shocks. Confirmatory support requires at least 10 final days each with at least 100 eligible shock intents; at least 95% of scheduled intents on every day contributing numeric shock outcomes must pass the intent quote/depth/history gates; no missing target quotes among final eligible shocks; and at least 99% of eligible shock intents on every contributing day must have enough displayed depth for `Q` at **both** policy targets. These depth failures remain in numeric outcomes and totals. The intent eligibility threshold is evaluated before target outcomes. A contributing day with fewer than 100 shock intents stays in the equal-day primary mean; it simply does not count toward the ten-day/100-intent requirement. If any contributing day fails the 95% intent-coverage or 99% future-depth threshold, retain its result and mark the confirmatory experiment `FAIL_SUPPORT`; do not omit it to improve the estimate. Files that cannot be qualified contribute no invented values and are reported explicitly; at least ten fully qualified final files remain mandatory.

The primary inferential unit is the sampled day, not individual intents. Use a paired circular moving-block bootstrap of the chronological final daily means with 20,000 repetitions, fixed seed `20261021`, primary block length one sampled day. Report an equal-tail 95% percentile interval. Fixed sensitivity block length two sampled days uses the same repetition count and seed. Adjacent sampled days are roughly a month apart; these blocks do not reconstruct intervening daily dependence. With only 12 possible final days, even day-block bootstrap uncertainty can be unreliable. Report sample SD, all daily means, sign counts, and leave-one-day-out means alongside the interval. No exact-test, asymptotic-certainty, or broad market-generalization claim.

One primary hypothesis/estimand means no multiplicity correction is required for its sole confirmatory comparison. All following analyses are explicitly descriptive and cannot rescue a failed primary result:

- The same quote accounting on normal-state eligible intents, on the same days, to expose whether savings are specific to observable shocks rather than a universal drift/calendar effect.
- Buy/sell splits, spread/drift/fee components, daily median saving, and day-equal empirical quantiles of delay penalty `-S` at 50%, 90%, 95%, and 99%; for the pooled quantile, each intent on day `d` has weight `1/(D*n_d)`, where `D` is the number of contributing days and `n_d` its paired shock count. Publish the worst day and worst observed penalty without claiming a population extreme.
- The full fixed fee grid `0,5,10 bps` crossed with delayed extra adverse-slippage grid `0,0.5,1 bps`. Show every cell; the primary cell remains `5,0.5`.
- Additional delay targets `t+300 ms` and `t+1050 ms`, representing 250 ms and 1000 ms added wait relative to the same `t+50 ms` baseline. Apply the identical as-of, age, quantity and missingness rules. These are latency sensitivities, not alternative winners.
- Block-length-two interval and leave-one-day-out means. Report disagreement; do not select the favorable interval. Separately report results on all price-paired intents versus those with sufficient future depth, labelling the latter post-outcome conditioning rather than treating it as a new primary sample.

Validation and development results remain visible even when the final result differs. Do not pool all years to turn a failed final test into success. Investigate abnormal data through frozen qualification rules; any substantive measurement correction is versioned, explains affected observations, and reruns all periods without deleting the original result.

## Decision and stop rules

Promote only the narrow statement that waiting passed this **historical quote-cost screen on the selected final days** if all support/rights/integrity gates pass, the primary 95% interval's lower endpoint is strictly above zero, and the primary mean net saving is at least **0.1 bps** after the already included 0.5 bps delayed slippage stress and 5 bps notional fees. The 0.1 bps threshold is an AI-selected practical screen (0.001 USDT per 100 USDT intent), not a calibrated routing-profit hurdle. It is frozen to prevent declaring arbitrarily tiny positive effects economically persuasive. Report whether the block-two and leave-one-day-out checks contradict that interpretation; any contradiction limits promotion to `SENSITIVITY_DEPENDENT` rather than an unqualified pass.

Otherwise retain `NEGATIVE` (estimated primary saving nonpositive), `INCONCLUSIVE` (positive estimate but uncertainty/economic screen not passed), or an explicit `FAIL_SUPPORT`/`NOT_RUN_*` status. Failed access, few shocks, stale quotes, missing outcomes, insufficient depth, or rights ambiguity never authorize changing the source, period, threshold, quantity, latency, or inference family. No result licenses live trading or establishes alpha.

Stop before any outcome GET until commitment is verified. Stop acquisition or analysis on rights/access/resource/integrity failure and preserve receipts. A partial study is not completed empirical evidence. Do not open additional symbols/days or derive an alternative strategy in response to failure. Any follow-up question receives a new protocol and a disclosed sample-exposure history.

## Reproduction and correctness contract

Public source must expose typed quote/state/intent/outcome interfaces, explicit eligibility reasons, streaming acquisition and replay, and deterministic day aggregation. Use independently calculated small synthetic paths to check as-of boundaries, no-future-feature access, exact weighted-median duration, expiries/gaps, equal-time conflicts, alternating sides, quantity fixation, fee-notional differences, depth failures retained, end-of-day targets, and cost-decomposition identities. Synthetic fixtures must be clearly labelled and must not copy restricted raw rows. Compare streaming output against a deliberately simple independent reference on synthetic/adversarial inputs.

Implement offline network-free tests and a downloader requiring the committed protocol SHA; do not make raw-market-data access an implicit CI step. Run schema/integrity checks before scientific calculations, and use atomic private receipts to preserve interrupted acquisition. Aggregate hashes, exact software/environment versions, seeds, acquisition and implementation commits, resource usage and failure counts form the reproducibility record. A reviewer downloads raw data independently under the provider's terms; results must fail closed on a changed hash or unavailable source rather than silently refreshing the frozen sample.

This experiment observes historical displayed BBO, not executable fills, full depth, queue priority, exchange matching, spread paid by a particular account, or market impact. Collector receive time is not strategy infrastructure latency. There are no modeled holdings, realized trading returns, inventory exposure, borrowing, financing or carry; those quantities are **outside the one-order quote comparison**, not assumed costless. Only qualified aggregate research claims may be published.
