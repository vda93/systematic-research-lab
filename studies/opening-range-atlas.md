# The wider opening-range evidence

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

These entries describe completed historical studies, exploratory findings and one separately registered successor. They have different sample roles and different maturity. Historical replays are private research evidence, not live returns or independent public replications. R denotes the source study's normalized trade-risk measure; price-space R and financing-adjusted monetary R are identified separately where material. Correlated parameter configurations and repeated trade observations are not independent strategies or a combined portfolio.

## A broad naked-breakout baseline

**Maturity: completed Discovery; rejected baseline.**

The initial gold study asked whether an unfiltered, symmetric fixed-target breakout could produce a stable timing region. It evaluated 1,152 configurations on historical Discovery sessions from August 2015 through December 2021. The surface varied time of day, opening-range duration and direction while keeping the research contract fixed.

None of the 1,152 configurations had positive expectancy or a profit factor above one. The decision rejected that defined baseline and preserved it as a research instrument. It did not authorize a search for one favorable configuration in the remaining sealed periods. [A01](../docs/evidence.md#a01)

The surface still had information: some regions were less adverse, and the opening-range duration changed the topology. Those observations became named follow-up questions with their own boundaries. Keeping them separate prevented a weak relative improvement from becoming an unsupported profitability claim.

The mapped negative result narrowed the search space. The rejected strategy and its regional observations left separate hypotheses for future tests.

## Extending the range-duration boundary

**Maturity: completed Discovery extension; rejected naked strategy.**

A separate gold extension tested whether longer opening ranges changed the adverse baseline. It added 576 configurations on the same August 2015 to December 2021 Discovery domain. The complete campaign passed its engineering gates before economic interpretation.

Longer ranges improved some comparisons, but improvement was insufficient. Mean configuration expectancy was approximately −0.176R for one duration group and −0.160R for the longer group. Only seven of 576 configurations were positive. The strongest reported configuration had 382 trades, approximately +19.14R, profit factor 1.114 and five positive years out of seven. No configuration achieved six or seven positive years. [A02](../docs/evidence.md#a02)

The study also retained matched comparisons: the longer duration outperformed in roughly 61% of valid matched pairs. That descriptive improvement could reflect transaction-cost geometry and the shorter remaining signal-search window as well as market behavior.

The decision closed the naked extension and prohibited another duration expansion under that branch. The relative improvement was repeatable, but too weak to support promotion.

## Bridging two platform builds

**Maturity: completed technical parity; bounded implementation evidence.**

The baseline and duration extension had run on different MT5 builds. Before interpreting them as one larger Discovery surface, the program needed evidence that the build change had not altered strategy semantics. This became a separate parity study rather than an assumption attached to the economic analysis.

Forty-eight overlapping configurations supplied matched observations across the two builds. The comparison covered 33,424 trades and 576 paired tables across twelve output families. After excluding the campaign identifier, the scientific tables matched row for row and value for value. Run metadata retained the expected build and run-identity differences. [A03](../docs/evidence.md#a03)

The observed agreement covered trade timing, direction, execution prices, stops, targets, volume, economics and path diagnostics within the tested overlap. It justified combining the earlier and extended surfaces for research interpretation.

The build comparison resolved an implementation uncertainty for this engine, historical source and overlap set. It allowed the larger scientific comparison to proceed. The result provides neither evidence of alpha nor certification of future platform releases.

## Filtered momentum: strong Discovery, unopened OOS

**Maturity: completed Discovery; parked and unadjudicated out of sample.**

A filtered gold continuation branch tested whether signal-bar momentum could distinguish better breakout opportunities. Its fixed Discovery experiment contained 48 filtered configurations and four aligned controls on August 2015 to December 2021 history.

All 52 configurations completed the engineering checks, and 47 of the 48 filtered configurations had positive Discovery results. The frozen representative recorded 114 trades, approximately +44.67R, mean +0.392R, profit factor 2.79 and seven positive calendar years. Neighboring configurations formed a strength-versus-frequency plateau rather than a single isolated maximum. [A04](../docs/evidence.md#a04)

Those results are notable Discovery evidence. The reserved OOS was never opened under this lineage, however. When the historical program was sunset in September 2026, the candidate was parked with its future evidence boundary intact.

The candidate has strong development evidence and no OOS verdict. Active work stopped with that uncertainty unresolved; neither failure nor validation can be assigned to an unopened test.

## The London relative-strength ridge

**Maturity: exploratory Discovery topology; parked.**

One recurring gold observation was a region around the London morning where naked breakout configurations were less adverse than the wider timing surface. The longer-range extension made this pattern more visible and produced a few weakly positive configurations.

The strongest reported member had 382 trades, approximately +19.14R, mean +0.0501R and profit factor 1.114, with five positive Discovery years out of seven. Across the 48 added regional configurations, however, mean expectancy remained approximately −0.0497R per trade. The local positive examples did not establish a uniformly profitable region. [A05](../docs/evidence.md#a05)

The ledger retained this as hypothesis-generating topology. It was never an independently validated trading candidate, and the historical program's sunset parked the branch without authorizing a new filter search.

The relative strength suggests questions about market structure, costs or directional continuation. It remains exploratory until a separately defined hypothesis passes independent validation. The local configurations are retained as historical observations, with no deployment recommendation.

## A midday ridge without positive expectancy

**Maturity: exploratory Discovery topology; parked.**

A second gold continuation region persisted across opening-range durations around the middle of the trading day. Its repeatability made it worth documenting even though the underlying naked configurations remained negative.

The duration extension contributed 42 configurations in this region. Their mean expectancy was approximately −0.0460R per trade. Even the strongest new examples remained negative, around −0.019R to −0.021R per trade. The observation was therefore about relative performance within an adverse surface, rather than a demonstrated positive edge. [A06](../docs/evidence.md#a06)

The branch was parked at the historical program sunset, and its record explicitly prohibited further filter searching under the same hypothesis. No independent OOS success or failure is attributed to it.

The ridge is a stable region of smaller losses. Its negative values remain visible because relative strength alone supplies no evidence of executable profitability. A new market-structure question would need a separate test.

## A rollover anomaly kept in quarantine

**Maturity: qualitative microstructure observation; parked and quarantined.**

The gold timing research also found pronounced breakout failure in a late-day window around rollover. Such a pattern is visually tempting for a reversal strategy, but its location creates substantial identification problems.

The ledger specifically flags spread widening, liquidity holes, day-boundary effects and broker microstructure as plausible contributors. It records an observation requiring caution, rather than a clean quantified alpha result. No independently validated executable strategy or OOS result is attached to this branch. [A07](../docs/evidence.md#a07)

At the September 2026 program sunset, the anomaly was parked as a microstructure warning. The record did not classify an unperformed strategy test as rejected. Any later investigation would require a new hypothesis that explicitly identifies the market mechanism and relevant evidence.

This is an example of useful restraint in an atlas. An observed price pattern can be retained without being promoted. The finding helps explain where a research feed or execution environment may behave differently, while the uncertainty remains visible. It also guards against turning a negative breakout observation into automatic evidence that an opposite-direction trade would be profitable.

## Failed-breakout Fade across four configurations

**Maturity: completed Discovery; rejected economic hypothesis.**

A separate gold Fade study turned a failed-breakout observation into a frozen executable experiment. The four-configuration surface used August 2015 to December 2021 Discovery history and tested a specified opposite-direction response after a failed short breakout.

All configurations were engineering-valid, integrity-clean and reproducible. Economics were consistently adverse. The four samples contained 303, 309, 219 and 163 trades, with total results of approximately −105.81R, −86.25R, −78.78R and −38.11R. Their R-based profit factors ranged from 0.372 to 0.616. Twenty-seven of the 28 configuration-year observations were negative. Duplicate runs reproduced trade economics apart from run identity. [A08](../docs/evidence.md#a08)

The completed decision rejected the hypothesis and prohibited escalation into its reserved OOS and lockbox. Market-close handling, deferred exits and financing did not explain away the adverse result in the final adjudication.

The record retains the earlier implementation defects and pre-canary checks alongside the later completed evidence. The working implementation produced an economically unsuccessful strategy result; the earlier defects do not explain away that negative result.

## The earlier completed-candle Fade baseline

**Maturity: completed legacy Discovery; rejected baseline.**

An earlier Fade experiment used a different historical universe and a completed-candle reentry rule. On its frozen 2003 to 2014 Discovery sample, it entered opposite the initial breakout only after the specified return into the range, with a structural stop and midpoint objective.

The accepted sample contained 781 trades, all closed once. The study lost approximately 320.30 net R, with mean −0.410R and profit factor 0.251. None of its twelve calendar years was positive, and each of the three predeclared eras was negative. Independent integrity checks passed before economic interpretation. [OF1](../docs/evidence.md#of1)

Operational delays were visible rather than hidden: maintenance-deferred trades were retained, and the much larger nondeferred cohort was still strongly negative. The report preserved source-quality warnings instead of filtering a more attractive subset.

The baseline was rejected without opening its OOS gate or tuning after the outcome. It is separate from the later four-configuration Fade experiment and from the newly registered timing successor. Keeping those identities distinct preserves what each result can establish about a particular execution rule and historical domain.

## Testing an alternative target without inventing fills

**Maturity: completed posthoc proxy and bounds analysis.**

A read-only Discovery analysis examined a range-derived target using archived outcomes from the frozen 1,152-configuration gold baseline. It covered approximately 1.245 million repeated configuration-trade observations; these are not independent portfolio trades.

The analysis explicitly separated inferable outcomes from cases censored by the original target or invalid at the recorded entry. On approximately 1.053 million inferable observations, the alternative net proxy averaged −0.218R, slightly worse than the original inferable subset at −0.208R. This used recorded non-price drag as a proxy rather than claiming exact alternate broker fills. [OP1](../docs/evidence.md#op1)

A related historical-geometry check identified cases where both the target and stop lay within the observed extrema. Extrema alone could not establish which came first. The study retained those cases as ambiguous and reported lower and upper gross-R bounds spanning zero.

The result did not validate a replacement strategy. Its contribution was methodological: a counterfactual can be informative while remaining partially identified. Inferability, censoring and event order belong in the reported conclusion, especially when archived summaries cannot reconstruct a complete executable path.

## USTEC: mechanism rejection and mixed OOS evidence

**Maturity: completed Discovery and two OOS blocks; parked at the protocol stop.**

The index lineage selected a representative configuration from a robust region rather than the highest-return point in its 1,728-configuration Discovery surface. Same-width placebo controls subsequently failed to support a special role for the exact opening-range boundaries. The broader candidate remained frozen while that narrower mechanism claim was downgraded. [A09](../docs/evidence.md#a09) [A10](../docs/evidence.md#a10)

OOS-A, covering eligible 2025 sessions, was strong: 124 trades, approximately +26.41 price-space R and profit factor 1.382, with 14 of 18 regional configurations positive. OOS-B, covering February to June 2026, disagreed: 53 trades, approximately −0.576R and profit factor 0.982, with only eight regional configurations positive. Both standalone OOS-B gates failed. [A11](../docs/evidence.md#a11) [A12](../docs/evidence.md#a12)

The pooled OOS total remained positive, but it could not override the preregistered second-block decision. The candidate was parked with no retuning, reselection or deployment authorized.

The earlier confirmation stands, and the later failure still determines the stop under its gate. The mechanism test answers a narrower question than cumulative strategy return. The flagship case study gives the full evidence chain.

## Gold qualification: parity passed, deployment did not

**Maturity: completed engineering, monetary and terminal qualification; rejected deployment branch.**

The later gold lineage used a different modern sample: Discovery in 2019 to 2023, validation in 2024 to 2025 and a terminal January to June 2026 holdout, with explicit lifecycle burnoff months. Its final Python to MT5 scientific parity certificate passed after earlier discrepancies were resolved and preserved.

Two frozen candidates, A and C, survived the primary execution stress. Monetary reconciliation then matched 1,376 scientific trades with zero unexplained discrepancies, explicitly separating six synthetic scientific exits from physical-deal records. Despite those engineering successes, none of 22 frozen deployment configurations met the complete gate. Financing and overnight dependence materially constrained the economics. [A13](../docs/evidence.md#a13)

The terminal holdout added a clear stopping result. A completed 53 trades with profit factor 0.68; C completed 51 with profit factor 1.00 after rounding. The runs were valid, while economic continuation was negative or not demonstrated. The holdout is spent. [A14](../docs/evidence.md#a14)

The frozen deployment branch was rejected. That decision does not reclassify the earlier momentum candidate's unopened OOS. It applies to this specific candidate family, accounting model and completed qualification chain.

## A distinct first-tick timing successor

**Maturity: implementation and canary evidence; economic Discovery pending.**

A separately registered successor asks whether a Fade opportunity decays while waiting for completed-candle reentry confirmation. The changed dimension is entry timing: after the confirmed initial breakout, the strategy observes the first qualifying executable return into the range. The remaining strategy definition stays frozen.

The connected October 2026 record identifies this as a new post-closeout hypothesis, separate from the rejected historical Fade branch. Its available evidence consists of implementation checks and valid canaries: fifteen hypothesis-specific deterministic tests, thirty-three predecessor regressions, three parser checks, a clean compile and three integrity-valid canary runs. Runner recovery checks also passed. [A16](../docs/evidence.md#a16)

Those results support readiness for the specified economic experiment. They do not establish edge. The planned domain remains the earlier 2003 to 2014 Discovery sample, and 2015 onward remains sealed under this successor's contract. The ledger permits one canonical Discovery adjudication before any timing surface or OOS escalation.

The successor is an active hypothesis with engineering evidence and unknown economics. Its correctness checks cannot supply the missing economic result, and the predecessor's rejection does not adjudicate the changed entry rule.
