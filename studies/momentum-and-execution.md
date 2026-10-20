# Momentum, portability and risk engineering

[Portfolio](../README.md) · [Research atlas](../docs/research-atlas.md) · [Evidence register](../docs/evidence.md)

These are original high-level drafts drawn from completed research decisions. R is normalized trade-risk output; reported PF and drawdown refer to the stated research metric. Historical selection, simulation, engineering and prospective evidence remain distinct.

## Component ablation: an inconclusive result can preserve the model

A five-market continuation study completed 35 fixed cells to test the contribution of three existing signal gates. The historical panel contained 52,655 valid primary trades across all variants; 17 forced end-of-test exits remained explicitly flagged. Markets had different recorded starts and feed conventions, so their totals were not treated as a single homogeneous out-of-sample dataset.

The frozen panel rules rated all three gates **WEAK / UNCLEAR CONTRIBUTION**. One gate had a positive paired contribution on the USDJPY anchor, but the other markets did not provide the required breadth of interval-supported evidence. That outcome supported neither a universal value claim nor a deletion.

Path dependence explained why a simple “filter removes bad trades” story would be inadequate. Removing a gate admitted additional trades while also occupying the symbol during opportunities taken by the reference path. A newly admitted profitable trade could displace an even stronger reference trade. The program therefore retained the gates, selected no production variant and recorded **INCONCLUSIVE**. The result illustrates the difference between a plausible component and evidence sufficient to assign it a general economic role. [A-MOM-ABLATION](../docs/evidence.md#a-mom-ablation)

## Scale decomposition: a plausible explanation was overturned

A continuation model looked weaker at fine bar resolutions. Historical screens on USDJPY over **29 January 2020 to 1 August 2026, end exclusive**, showed a gradual transition rather than an isolated hourly optimum: nearby half-hour, hourly and two-hour paths were positive, while very fine scales deteriorated.

An initial explanation emphasized the shorter economic horizons created when fixed bar counts were moved to smaller bars. A subsequent factorial experiment separated clock horizons from the volatility reference used in price-risk geometry. The latter explained most of the recovery. At native fine-scale horizons, changing the geometry reference raised reported mean R from **+0.02093 to +0.10761 per trade**, while drawdown fell from **53.31R to 15.01R**.

A further development-only decomposition distinguished signal normalization from stop, trailing and risk geometry. It again located the main contribution in the geometry role. The earlier primary-horizon explanation was recorded as rejected rather than preserved alongside its contradictory successor.

These were historical mechanism experiments, with interacting interventions and path-dependent trade sets. Their value lies in narrowing an explanation; they do not establish an independently validated fine-scale strategy. [A-MOM-SCALE](../docs/evidence.md#a-mom-scale)

## Development strength, recent decay and architecture comparison

A bounded development sequence froze a fine-scale continuation candidate before its final retrospective comparison. Discovery on **29 January 2020 to 1 January 2025** produced **2,197 trades, +161.68R, profit factor 1.3157 and drawdown 10.32R**. The reserved recent comparison, **1 January 2025 to 1 August 2026**, produced **719 trades, +17.68R, profit factor 1.0998 and drawdown 16.70R**.

Mean R fell to roughly one-third of discovery, while the bootstrap interval crossed zero. The finding was directional persistence with substantial deterioration, not confirmation of the development magnitude. The “retrospective holdout” label also requires care because earlier lineage screens had already included these calendar dates.

Later comparisons favored the complete frozen hourly architecture on USDJPY and gold. This was a bundle comparison, so no individual parameter received causal credit. Separate implementation checks reproduced the two hourly research paths with zero parsed deal-path mismatches.

The wider portability screen retained its failures of evidence: one market failed data quality, and another was blocked by the runner’s fixed panel. Those were unresolved data and tooling questions, not negative strategy results. [A-MOM-DECAY](../docs/evidence.md#a-mom-decay)

## Bitcoin continuation: an attractive development mechanism was parked

The Bitcoin branch examined whether slower resolution could improve a continuation model whose recent hourly result was negative. Development evidence suggested a broad slower-scale region, leading to a frozen primary validation band and a separate resolution-versus-horizon decomposition.

The recent **1 January 2025 to 1 August 2026** comparison did not support the primary band. Two-hour and three-hour paths returned **−7.858R and −3.489R**. Slower neighboring paths remained positive, but their bootstrap intervals included zero and their samples were smaller.

The factorial study then identified a constructive coarse-resolution effect in development. Its relevant arm had **310 trades, +54.09R, profit factor 1.526 and drawdown 11.22R**. Yet the same arm returned **−5.22R over 103 trades** in the recent stress, with profit factor **0.876**.

The branch was parked for the current portfolio objective. No additional threshold search was used to rescue it, and a separately reserved prospective period remained unopened. The conclusion is narrower than “Bitcoin continuation cannot work”: this lineage had an interesting historical mechanism without enough robust recent support or portfolio fit to justify continuing its selection program. [A-MOM-BTC](../docs/evidence.md#a-mom-btc)

## DE30 half-hour research: stress simulations did not replace new evidence

A seven-cell development timeframe screen found a coherent half-hour/hourly region. The half-hour candidate produced **1,520 trades, +78.3565R, profit factor 1.1485 and drawdown 26.2534R** on **2020–2024** development history. A follow-up decomposition and exact control parity supported freezing the candidate.

Resampling then examined risk rather than adding independent validation. Its observed drawdown lay around the 58th percentile of 10,000 order permutations. Block-bootstrap tails were materially worse than the observed drawdown, showing why the original path alone was an inadequate risk description.

A later **2025–August 2026** diagnostic used an already-spent period. It returned **+11.0421R over 564 trades**, profit factor **1.0562** and drawdown **29.3759R**. The 2026 segment was negative, and removing the five best entry-date cohorts made the aggregate **−14.9111R**.

The architecture stayed frozen, and the separate prospective protocol remained pending. These results support a case study about maintaining evidence roles: a favorable development surface, useful simulation stress and a weak retrospective diagnostic do not add up to completed prospective validation. [A-DE30-M30](../docs/evidence.md#a-de30-m30)

## Gold execution fragility: feed disagreement narrowed the mechanism

A gold continuation study challenged a positive recent result with an independent tick feed over **January 2025 through July 2026**. Removing a stock spread restriction restored comparable trade counts, yet economics diverged: one feed reported **207 trades and −48.31R**, versus **219 trades and +53.98R** on the original feed. Cross-feed performance portability was rejected.

Passive instrumentation then compared spread with planned trade risk. Across **151 exact-minute, same-direction pairs**, there were **12 loss-on-one-feed/win-on-the-other flips** and no reverse flips. The evidence pointed toward execution friction as a material source of fragility, without establishing that it explained everything.

That broader explanation was tested too. Older low-friction trades still lost while recent low-friction trades were positive, so the claim that spread and absolute setup size fully explained the change was rejected. A volatility-state candidate was subsequently selected in development and replayed against its offline reconstruction.

The candidate remained frozen with **188 development trades**. Its true later holdout had not been run in the reviewed decision record. The sequence supports a feed-sensitivity and mechanism narrative, while leaving independent validation explicitly pending. [A-VENOM-FEEDS](../docs/evidence.md#a-venom-feeds)

## Risk engineering: shared calculations can conceal a guard defect

A later engineering review found that a sizing calculation and its overshoot check relied on the same monetary-loss input. Agreement between them could therefore fail to reveal a shared error. A separate revision added independent applicable native-economics ceilings, explicit request identity, downward volume normalization and fail-closed margin checks.

The latest bounded native tester comparison reproduced the frozen reference path across **188 trades and 11,407 byte-identical event rows**. All 188 admitted requests passed the recorded risk ceilings without overshoot. In a separate margin-pressure case, two infeasible requests were skipped without submission, resizing or retry.

The evidence has a precise limit: qualification used a tester-specific permissive risk-governor shim. It did not prove production risk-governor state, live ticket ownership, restart behavior, real fills or current target-terminal contract conditions. The package’s final record explicitly withheld live deployment authorization.

The historical incident’s root cause also remained probable rather than proved because dated broker specifications and authoritative incident state were unavailable. Engineering confidence improved without rewriting that uncertainty or converting tester parity into economic or operational approval. [A-VENOM-ENGINEERING](../docs/evidence.md#a-venom-engineering)
