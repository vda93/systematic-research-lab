# ECB-FX-MOM20-v001: fixed historical reference-rate study

This protocol and its implementation must be committed before the first
historical observation download. The execution receipt identifies that prior
commit. This document itself contains no study outcome and does not prove a
freeze occurred; the commit and acquisition receipts establish chronology.

## Question and limitations

Does the sign of twenty preceding reference observations outperform an
unconditional always-long reference-direction benchmark in predicting a
subsequent delayed reference change? Test EURUSD and author-derived USDJPY,
selected before outcomes. These share inputs and are not independent
replications. Causally ordered features establish temporal ordering, not causal
identification of a market mechanism.

The observations come from the [European Central Bank reference-rate
dataset](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).
They are real market-derived reference observations, not executable bid/ask
quotes. See [data conditions](../DATA_LICENSE.md). The [ECB framework](https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf)
describes setting around 14:10 CET and publication around 16:00; corrections may
occur by the next business day's publication. Its current version does not
establish every historical publication time. A current download is a retrieval
vintage, not proof of a point-in-time historical information set.

The [ECB announcement of 7 December 2015](https://www.ecb.europa.eu/press/pr/date/2015/html/pr151207.en.html)
documents the 16:00 publication regime effective 1 July 2016. This determines
the analysis start. The observation delay below avoids assigning a same-day
unpublished fixing to an entry, while proving neither actual publication
latency nor executable fills.

## Fixed source and qualification

Download only the official [historical ZIP](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip)
after the freeze. Credentials are unnecessary. Select Date, USD-per-EUR and
JPY-per-EUR for `[2016-06-01, 2026-01-01)`. The canonical CSV header is exactly
`Date,USD,JPY`. Preserve selected decimal strings, serialize UTF-8 with LF and
ascending dates. Independent source and selected-snapshot SHA256 hashes belong
in the acquisition receipt. Preserve the raw ZIP outside Git. There is no
automatic fallback provider, refresh, overwrite or outcome-dependent vintage
selection.

Require a ZIP with exactly `eurofxref-hist.csv`, passing CRC, with no additional
notice/document; an unexpected member blocks selection pending explicit
rights review. Reject ambiguous column names, wrong row widths, noncanonical
dates, duplicates, weekend rows, missing/nonfinite/nonpositive selected rates,
and date gaps exceeding seven calendar days. Do not fill, interpolate,
winsorize or suppress outliers. This gap screen does not certify complete
historical TARGET-calendar coverage. Record any failure without relaxing it.
The canonical parser independently reapplies these checks. Convert source
decimals to binary64 for calculations in the pinned Python/NumPy environment.

## Instruments, features and paired target

Let t index common valid provider observations, not calendar days.

- `P_EURUSD,t = USD_per_EUR,t`.
- `P_USDJPY,t = JPY_per_EUR,t / USD_per_EUR,t` (author calculation).
- `M_i,t = log(P_i,t / P_i,t-20)`; `s_i,t = sign(M_i,t)`, exact zero maps to 0.
- `y_i,t = log(P_i,t+2 / P_i,t+1)`.
- Signed signal statistic `a_i,t = s_i,t * y_i,t`.
- Unconditional always-long benchmark `b_i,t = y_i,t`.
- Primary paired difference `d_i,t = a_i,t - b_i,t`.

No feature uses a future observation. Compare precisely aligned targets. The
primary result is mean paired difference, with ordinary basis points equal to
10,000 times the logarithmic change. Signed changes are not portfolio returns.
An always-short comparator `-y` and flat comparator zero are descriptive only.
Report sign frequencies and unconditional drift: benchmark superiority can
reflect short exposure during negative drift and is not proof of a momentum
mechanism. No risk scaling, parameter search, currency reorientation, ML model,
transaction-cost proxy, carry adjustment or capital curve is permitted.

## Fixed temporal roles and support

| Half-open bounds | Role | Minimum eligible targets |
| --- | --- | --- |
| `[2016-06-01,2016-07-01)` | Development feature warmup only | 20 preceding observations per signal |
| `[2016-07-01,2020-01-01)` | Development diagnostics, no tuning | 250 |
| `[2020-01-01,2023-01-01)` | Validation, no tuning | 500 |
| `[2023-01-01,2026-01-01)` | Final historical evaluation | 500 |

For validation and final evaluation, t-20, t, t+1 and t+2 must all belong to the
same role. Purge cross-boundary signals and outcomes. Development alone may use
its designated June warmup for features. The extra-delay sensitivity also
requires t+3 within the role. Failure of a minimum is `FAIL_SUPPORT`, never
authority to change periods. Report all periods. No early performance stop or
validation-driven revision is allowed.

These roles were designed in October 2026 and are historical temporal
holdouts, not fresh prospective OOS. General prior market knowledge is not
excluded. Metadata searches incidentally displayed example/reference values
dated before June 2016 or during 2026; those values are outside this study's
acquisition window. No study series or forward statistic was inspected before
this protocol was written. The chronology receipt must distinguish the actual
freeze from this statement.

## Inference, multiplicity and frozen decision

Final evaluation has exactly two primary one-sided hypotheses:
`H0_i: E[d_i] <= 0`, against `H1_i: E[d_i] > 0`. Use Holm correction across
these two assets, alpha 0.05. Other roles, pooled statistics, annual results and
sensitivities are descriptive and cannot rescue a failed primary result.

Use 9,999 paired circular moving-block replicates, primary length 20
observations, seed 20261021. NumPy's default_rng generates uniform starts;
concatenate circular blocks and truncate to N. The same starts are used across
both assets. Reset the seed for every role, block length and sensitivity.
Bootstrap the observed paired differences for the marginal 95% percentile
interval (linear interpolation). For null p-values, subtract the observed mean
from each asset series before applying the identical resampling indices. Use
`(1 + count(null_boot_mean >= observed_mean)) / 10000`. Publish raw and Holm
adjusted p-values. The marginal intervals are not simultaneous intervals.

Each asset passes only if all three hold at full calculation precision:

1. Primary marginal 95% interval lower bound is strictly greater than zero.
2. Holm-adjusted primary p-value is at most 0.05.
3. Mean paired difference is at least **0.5 basis points per observation**.

The 0.5-bp threshold is an arbitrary preregistered statistical relevance screen,
not validated trading economics. Family PASS requires both preselected assets
to pass and all period support minima to hold. A nonpositive estimate is
`NEGATIVE_COMPARISON`; other asset failures are `INCONCLUSIVE`. Family failure
is `NOT_PASS`, or `FAIL_SUPPORT` when a required period lacks support. A PASS
would support only this benchmark-relative predictive association under the
resampling assumptions. Executable profitability remains `NOT_EVALUATED`.

Approximate stability and sufficiently weak dependence are assumptions, not
verified guarantees. Circular blocks introduce an end/start join. Regime
change, long memory, few effective blocks and finite-sample coverage errors can
invalidate nominal inference.

## Fixed sensitivities and reports

Publish block lengths 10 and 60 with the same 9,999 replicates and reset seed;
retain length 20 as primary. Also publish the same signal with extra-delay
target `log(P[t+3]/P[t+2])`, means and comparators only. No new confirmatory
hypotheses arise from these checks.

For each role report sample size, mean signed statistic, mean always-long,
always-short and flat comparators, mean/median difference, sign counts, annual
contributions and equal-weight pooled daily difference. The pool is
descriptive. For concentration, remove the single calendar year contributing
the largest positive sum of pooled differences; ties go to the earliest year.
Report its contribution to the full-period mean and the retained pooled mean.
If no contribution is positive, remove none. This outcome-dependent diagnostic
gets no inferential p-value. Keep negative years and failed comparisons.

## Reproduction, freeze and amendments

Before acquisition, commit this protocol, `src/srl/fx_study.py`,
`scripts/fx_study.py`, `tests/test_fx_study.py` and `DATA_LICENSE.md`. The explicit
acquisition command requires that exact HEAD, byte equality of these files and
an affirmative rights-review flag. The owner separately verifies public
freeze chronology and writes an external authorization receipt. Synthetic
tests do not establish historical findings.

Default `python scripts/fx_study.py --check` reads only the frozen selected CSV
and checks the exact JSON artifact; it never downloads. One-time
`python scripts/fx_study.py --write` creates a previously absent JSON result.
Acquisition uses `--acquire --raw-zip EXTERNAL_NEW_PATH --freeze-commit FULL_SHA
--rights-reviewed`; it downloads no outcomes until explicitly invoked. Output
JSON has sorted keys and floats rounded to 10 decimal places; decisions use
unrounded calculations. Pin Python minor and dependency versions for exact
replay. The source CSV hash is included in the result; bind protocol/receipt
hashes externally in the manifest.

Data or implementation corrections after acquisition require a versioned
amendment explaining the trigger and retaining original artifacts and
conclusions. Never retroactively call a repaired outcome-blind preregistration.
The study does not reopen or qualify any private TradingBotHQ sealed sample.
