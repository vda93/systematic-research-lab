# BBO delay: measurement amendment with partial-identification bounds

Status: **FROZEN DESIGN, EFFECTIVE ONLY AFTER A VERIFIED PUBLIC COMMIT**. AI-proposed and AI-assisted; candidate origin, manual implementation and unaided mastery are not asserted.

This is the same economic question as the [original protocol](bbo-delay-protocol.md): can an additional 500 ms wait after an observable spread shock reduce quoted crossing cost after midpoint drift? It is a support-informed measurement amendment, not a successful replication or a rescue of the original test. The original design and its first-day development failure remain intact.

## Exposure and chronology

The original protocol was publicly committed as `c5f205fdeff02ea3f667a804974a6ee4d9098790` before any outcome GET. Its first development file, 2023-01-01, was subsequently downloaded and parsed for schema/state qualification. It contained 4,391,515 rows, 23,678 conflicting receive timestamps and 48,242 known runs under the frozen age rule. The longest run was 28.405641 seconds: zero of 86,099 scheduled intents could have a fully known preceding 60 seconds. The original first-day result is **DEV_FAIL_SUPPORT**, not an economic finding and not proof other days fail.

No spread-shock labels, policy quote costs, delay savings or cost-dependent selections have been calculated before this amendment. Nonetheless the January development file has been accessed; it is not fresh OOS. This amendment is motivated by observed measurement support. Its public commit must precede computing amended history bounds, labels or economic outcomes on that already accessed file and every subsequent outcome-file GET. Save the commit/time, file hashes and acquisition receipts. The still-unaccessed 2024 validation and 2025 final files remain prospective analysis commitments within this project, not globally unseen market history.

The follow-up changes one measurement rule and therefore its eligible population. It does not claim that the original continuously observed median passed or that the economic estimand is unchanged. No earlier outcome is retroactively preregistered.

## One changed feature: robust classification over missing-history completions

Keep the original receive clock, strict-past decision state, 250 ms quote expiry, equal-timestamp ambiguity handling, price/depth qualification and history window `[t-60 seconds,t)`. Invalid states, conflicts and expired intervals are unknown. Never interpolate or carry a quote through an unknown interval. Valid state intervals contribute their relative spread with their actual microsecond duration.

Let T be the 60-second duration, U its unknown duration, and K the empirical measure of known spreads weighted by known duration. Define the lower median as the smallest value whose cumulative duration is at least T/2. The completion family assigns **arbitrary real values** to unknown intervals; it does not assume the hidden exchange book was positive, uncrossed, present or tradable. The policy feature is agreement over numeric completions, not authentication of an unobserved market state.

Outer bounds on this median are:

```text
lower = -infinity                            if U >= T/2
        smallest known x with K(<=x) >= T/2-U otherwise
upper = +infinity                            if T-U < T/2
        smallest known x with K(<=x) >= T/2   otherwise
```

These follow by putting all missing mass below or above the known observations. At a half-duration tie the lower-quantile convention matters. Infinite endpoints are bounds, not invented prices or realized spreads. In implementation compare doubled integer durations, avoiding a rounded half threshold.

Require finite positive lower and upper bounds. With current qualified spread s(t), define:

- **Robust shock:** `s(t) >= 3*upper`. Every numeric completion meets the original three-times-median shock condition.
- **Robust normal:** `s(t) < 3*lower`. Every completion fails that shock condition.
- **Unclassified:** neither inequality holds, or bounds are nonfinite/nonpositive. Record `MEDIAN_AMBIGUOUS`; do not choose a completion or label it a normal control.

The robust-shock population is generally a subset of the original hypothetical full-history shock population. Cost estimates apply only to this revised observable population. Unknown/unclassified intents count against the same scheduled-intent coverage gate; the denominator does not shrink to hide missingness. This is an identification rule, not a tuned minimum coverage percentage or a promise that support will pass.

The implemented observable spread indicator uses parsed finite binary-float prices, midpoint `bid+(ask-bid)/2`, and `(ask-bid)/midpoint*10000` in that order. Duration weights are integer microseconds. Bounds apply to these recorded numerical indicators, with their rounding limits, not infinitely precise original decimal prices or unobserved exchange states. Compare the three-times threshold by exact integer-ratio cross multiplication of the finite float indicators, avoiding an outcome-tuned epsilon or a separately rounded multiplication. Test near-threshold ties independently. Costs use finite float arithmetic and checked spread/mid/fee decomposition with a fixed absolute tolerance of 1e-8 bps; an arithmetic failure invalidates the file rather than dropping an adverse intent.

## All other scientific rules stay fixed

The source is native Tardis `binance/book_ticker/BTCUSDT`, all 36 already planned first-month days in 2023/2024/2025, with the original roles and resource caps. No new asset, venue, date extension or alternate feed. Provider research and non-reconstructible-result permission must be snapshotted/rechecked before acquisition; raw quotes, event prices and private caches stay outside Git. This amendment does not grant a data license; see the linked original source/rights policy and acquisition-time notices.

Every second from 00:05:00 through 23:59:58 UTC remains an exogenous intent. Even epoch second buys, odd sells. Decision state is strictly before intent; quantity is fixed at `100/m(intent)` BTC, with sufficient displayed intended-side depth at intent. Baseline and delayed outcomes remain last qualified quotes at or before `t+50 ms` and `t+550 ms`, at most 250 ms old. No first-after-target quote or future information enters a feature.

The original order-side cost equations, fee-notional accounting and decomposition apply unchanged. The sole primary saving uses a 5 bps taker-fee assumption and 0.5 bps extra delayed slippage, both in units of the original 100 USDT intent. Keep all price-paired shocks even when future displayed size is insufficient. Missing targets remain missing, with exact eligibility/availability denominators; complete-case cost estimates are conditional on paired quote availability and do not establish the effect on unobserved orders.

The main comparison is delay versus immediate crossing on robust shocks. Robust normal intents are a descriptive control, not a second confirmatory hypothesis. Report both sides, spread versus signed midpoint components, fee difference, tail penalty, displayed-depth failures and all fixed cost/latency sensitivities. Do not average both order sides at the same instant. No inventory, financing, borrowing, turnover-as-real-trades, fills or account-profit claim is introduced. Scheduled order counts/notional describe hypothetical opportunities; overlapping alternating intents are not a funded strategy.

The original support gates remain: ten final days with at least 100 eligible shocks each, 95% scheduled-intent eligibility on every contributing day, zero missing primary targets among final eligible shocks, and 99% future displayed-depth sufficiency on each contributing day. A day below 100 shocks remains in the equal-day estimate if it has observations. Do not drop an unfavorable or low-coverage day. Report all planned days and missing reasons. If gates fail, label `FAIL_SUPPORT`; any available cost estimates are descriptive and cannot be promoted.

The original primary equal-day mean, 20,000 bootstrap repetitions, seed 20261021, one-day blocks, two-day sensitivity, 95% percentile interval, leave-one-day-out means, 0.1 bps net economic threshold and all cost/latency grids remain unchanged. With fewer than four observed days do not manufacture a bootstrap interval; report descriptive observations only. Twelve possible final days provide limited uncertainty evidence. The sole primary comparison has no additional multiplicity adjustment; all sensitivities remain descriptive and cannot rescue a failed gate. Only all-gates-passed results may use the original narrowly scoped promotion rule. A support failure cannot be called a negative economic effect merely because its descriptive mean is negative.

## Implementation freeze and staged access

The fewer-than-four-days bootstrap prohibition and explicit development-usability signoff below are additional conservative operational clarifications. They were not independently written into v1 in this form and do not relax a final support or economic gate.

Before validation, commit and hash the complete implementation, tests and reproducible development closeout. Require independent synthetic reference checks of streaming state/history bounds, strict-as-of prices, sides, quantity, fees, missingness and equal-day statistics. Record a development stage signoff that verifies correctness and tells whether the design has any usable economic observations. Signoff is not a requirement to see a positive effect and does not tune parameters.

If development has no eligible price-paired shocks at all, stop as `DEV_FAIL_SUPPORT`; do not open validation/final solely to hunt observations. If usable observations exist but coverage/promotion gates fail, retaining that limitation does not authorize a relaxed final pass: record it and proceed only to quantify the same frozen rules, not to manufacture a winner. Freeze implementation before validation access; record validation before final access. Any later substantive scientific amendment is new and explicitly labels already accessed data exploratory. Version correctness fixes, retain affected results and rerun the same samples; never silently regenerate a favorable artifact.

Public code must reproduce acquisition identities, aggregate results and exact checked JSON offline from privately downloaded raw data. Ordinary CI uses original synthetic fixtures, never implicit network or restricted data. A reviewer independently downloads the same bytes under provider terms and fails on changed hashes or unavailable sources. Publish only coarse, non-reconstructible daily statistics, histograms, code and hashes; no tick or per-intent price ledger. A failed original design and an informative negative/inconclusive amended study both remain visible.
