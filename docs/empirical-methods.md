# The estimand comes before the backtest

[Portfolio](../README.md) · [Research atlas](research-atlas.md) · [Evidence register](evidence.md)

The case studies use several different objects: ordered trade paths, matched events, fixed-clock markouts and modeled account trajectories. Comparing their headline numbers without preserving the object being measured would change the scientific question.

## Risk units, costs and economic identity

A normalized trade outcome is $r_i = P_i / L_i$, where $P_i$ is the recorded payoff under the study's cost model and $L_i$ is planned initial loss. Price-space R can instead normalize executable price movement by initial stop distance. These quantities coincide only under additional assumptions about sizing, contract economics and charges.

Profit factor in R-space is $\sum_i \max(r_i,0) / |\sum_i \min(r_i,0)|$. Ordered drawdown uses the running maximum of cumulative R. Neither quantity identifies annualized account returns or Sharpe: trade order, duration, exposure overlap, capital and cash flows matter. The [public accounting module](../src/srl/accounting.py) illustrates explicit charge accounting; it does not reproduce private broker economics.

For a buy fixed-clock markout, executable entry is Ask and exit is Bid. For a sell, entry is Bid and exit is Ask. Negating a long return while keeping the same prices fails to model a reversal. Research commission and slippage allowances also need a stated unit and timing convention. Even correct side accounting cannot reconstruct absent historical execution.

## An exit changes the next opportunity

Let $E(a)$ denote the entry set generated under exit architecture $a$. Usually $E(a)\ne E(b)$ because an open position can block later signals. A whole-path contrast,

$$\Delta_{\mathrm{path}}=\sum_{i\in E(b)}r_i(b)-\sum_{i\in E(a)}r_i(a),$$

includes changes in exit payoff, occupancy and the opportunity set. A contrast on $E(a)\cap E(b)$ conditions on common entries and answers a narrower question. It is not a substitute for the full strategy effect. [MOMCONT](../studies/momentum-continuation.md) reports both and retains the blocked opportunities.

The primary paired interval in the small H022 matched sample was not estimable under its frozen block rule. Choosing a shorter block after seeing this limitation would produce a sensitivity result, not retroactively satisfy the original design.

## Paired calendar blocks preserve a comparison

For aligned daily contributions $x_t$ and $y_t$, define $d_t=y_t-x_t$. Draw blocks of common calendar indices and compute $\bar d^*=n^{-1}\sum_j d_{I_j}$. Using the same indices preserves pairing and within-block temporal dependence. Resampling each strategy independently would discard shared market shocks.

The [public circular-block implementation](../src/srl/resampling.py) requires identical contiguous daily calendars, finite values, an explicit seed and a bounded block size. It estimates uncertainty in a paired mean difference. It is a generic methods utility; the private H025 study additionally simulated whole trade lifecycles and account rules. The utility does not reconstruct that account engine.

Block length changes the dependence model. H025 used 28 days primary and 14/56-day sensitivities. A funded conclusion that changed across these settings remained indeterminate. Simulated pass fractions are conditional on the historical resampling model and rules; they are not identified real-world probabilities.

The [synthetic coverage experiment](study.md#calibrate-the-inference-tool) checks this tool against a known data-generating mean. Its undercoverage is preserved. Deterministic replay proves the output is repeatable; it does not prove the inferred interval is calibrated for markets.

## Matched events are observational evidence

For pattern event $i$ and its frozen control group $C_i$, an incremental endpoint can be estimated as

$$\hat\tau=\frac1m\sum_{i=1}^{m}\left(z_i-\frac1{|C_i|}\sum_{j\in C_i}z_j\right).$$

H004 used continuation indicators and UTC-day cluster uncertainty. R001 used executable-side fixed-clock markouts and UTC-week clusters. Their units and estimands differ. Day/week clustering preserves dependence within that chosen cluster; it does not remove all long-range dependence or turn observational matching into randomization. Reused controls and cross-instrument dependence require careful interpretation of the declared resampling unit.

R001's three positive-effect hypotheses used Holm familywise adjustment: ordered p-values are compared against $\alpha/(m-k+1)$, with monotonic adjusted values. The displayed cluster intervals are individual intervals, **not** simultaneous Holm-adjusted intervals. A failed positive-effect gate is not proof of a profitable opposite strategy.

## Concentration is a stress, not an executable filter

The public [aggregate diagnostic module](../src/srl/diagnostics.py) derives the reported top-date contribution, median risk-fill percentage, exit drawdown ratio, era return differences and descriptive pooled OOS total from the real [published inputs](../data/historical-results.json). Its [JSON output](../results/aggregate-diagnostics.json) is rebuilt by the verification command. It refuses overlapping OOS eligibility windows and inconsistent return bases. These are transparent arithmetic checks; they cannot recover trade-level standard errors, independent significance or missing event paths.

The public inputs are rounded. For example, subtracting the displayed DE30 totals gives 46.8900R removed, while the private source reports 46.8901R from higher-precision observations. The diagnostic is a reconciliation at published precision, not an independent trade-level recomputation.

For complete entry-date cohort contributions $c_g$, sort by realized contribution and compute $S_k=\sum_g c_g-\sum_{j=1}^{k}c_{(j)}$. This removes full cohorts, preserving the unit chosen before the test. It is intentionally outcome-dependent as a diagnostic of concentration. It is not a live trading policy that can identify tomorrow's best dates in advance.

The DE30 robustness contract was conjunctive. A failed top-date stress stayed failed even when leave-one-year-out or bootstrap checks were favorable. Passing a later terminal block answered a different question.

## Compare mechanisms with controls

The ORB range controls preserved width while changing centering on actual historical market data. They were synthetic *ranges*, not invented historical returns. Similar performance weakens the claim that exact boundary geometry uniquely explains the effect. It does not establish a different causal mechanism.

Neighboring cells share observations and strategy semantics. An 18-cell plateau is a stability diagnostic, not 18 independent trials. A medoid reduces champion selection within a region; it does not eliminate selection bias or certify out-of-sample performance.

## Semantic equality and numerical serialization

Hash equality proves byte identity. Scientific parity compares canonical event identities, exact meaningful fields, missing/extra events and narrowly declared numerical fields. A redundant floating-point price string can differ while the underlying decision is unchanged. The DE30 tolerance amendment was disclosed and limited to those redundant fields.

The [comparator](../src/srl/validation.py) rejects duplicate keys, missing fields, nonfinite values and empty comparisons. It never applies a broad relative tolerance to semantic fields. Its tests demonstrate the method on small original fixtures; the historical 837-path result remains a separately reported private engineering replay.
