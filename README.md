# TradingBotHQ | Systematic Trading Research

A research log of systematic trading hypotheses explored through TradingBotHQ. I use AI coding and analysis tools extensively. The aim is to document **the questions investigated, how they were tested, what the evidence showed, and what was decided**, not to claim that I personally wrote every engine or invented every rule.

I am deliberately narrowing this portfolio to research families I actually recognize, directed or participated in. A standalone AI-generated experiment is not automatically my personal research merely because its files landed in this repository. [Authorship and assistance](docs/ownership.md) remain documented separately from scientific results.

## The research lifecycle

Each case study follows the same format:

1. **Hypothesis:** What market behavior or failure mechanism are we testing? Where did the idea originate?
2. **Methodology:** Data and sampling windows, controls, baselines, execution assumptions, costs, validation gates and implementation checks.
3. **Results:** Sample sizes, observed outcomes, uncertainty and whether the predeclared test passed.
4. **Discussion:** Competing explanations, biases, limitations, regime dependence and what the evidence cannot establish.
5. **Conclusion and decision:** Continue, reject, park or close, with a reason. Untested follow-ups remain untested.

The results are historical experiments, not claims of live profitability or deployment approval. Code may be AI-assisted, vendor-derived or independently written; these distinctions are not the same as the scientific decision.

## Research case studies

### 1. Opening-range breakout (ORB)

**Hypothesis.** Does opening-range geometry and its timing predict exploitable continuation beyond simpler time-of-day or candle-based explanations?

**Methodology.** Tested timing regions on historical Nasdaq and gold CFDs, then compared real range boundaries with same-width alternative ranges and simpler controls. Tracked distinct Discovery and validation blocks, implementation parity and trading costs.

**Results.** Some Discovery regions appeared promising, but exact boundary geometry was not uniquely supported. A representative Nasdaq candidate passed one validation block and failed the next. The gold branch also failed later economic or terminal qualification despite technical progress.

**Discussion.** Searching many configurations creates selection risk. Scientific parity does not establish a profitable executable strategy, and untested parked alternatives are not negative OOS results.

**Decision.** The tested original program closed without deployment authorization; preserve separate untested branches without relabeling them failures. [Full ORB study](studies/opening-range.md) | [Branch outcomes](studies/opening-range-atlas.md)

### 2. Engulfing / EBP

**Hypothesis.** Do engulfing-pattern implementations retain a useful signal once the exact source rules, pending-order lifecycle and broker semantics are reconstructed correctly?

**Methodology.** Rebuilt competing interpretations of the original rule, checked order-occupancy consequences, repaired a native-timeframe matrix and separated observational candle-mechanism questions from executable strategy tests.

**Results.** Different pending-order interpretations produced dramatically different exposure. A corrected 88-cell native-timeframe Discovery matrix was mostly weak, and the separate small-candle study found a negative retrospective association that did not establish a viable reversed trade.

**Discussion.** An apparent advantage from a three-trade replay is not equivalent to a high-throughput result. Neither weak performance nor a negative association identifies a causal mechanism or profitable opposite-side strategy.

**Decision.** Preserve the competing interpretations and frozen candidate histories. No winner was selected merely by choosing the most attractive implementation. [Full EBP study](studies/engulfing-and-support.md)

### 3. NOWICK and ANTI-NOWICK

**Hypothesis.** Does a nearly wickless candle predict continuation beyond otherwise comparable candles? If not, does a separately specified reversal rule work?

**Methodology.** Compared eligible pattern events with deterministic matched ordinary-candle controls across four FX instruments, using dependence-aware uncertainty. A separate reversal study compared net reversed outcomes with matched controls.

**Results.** The continuation study did not establish robust incremental signal. The independently tested reversal also failed its frozen rule.

**Discussion.** Failure to predict continuation does not imply that trading the opposite direction should work. Matching also cannot eliminate every source of confounding.

**Decision.** Shelved the original wickless-candle family and rejected the distinct tested reversal. [NOWICK study](studies/nowick.md)

### 4. Momentum continuation (MOMCONT)

**Hypothesis.** Are direction symmetry and alternative exit mechanics improvements over a frozen vendor-derived momentum-continuation architecture?

**Methodology.** Tested mirrored short direction, trailing-stop ablation, historical-era sensitivity and a paired portfolio comparison, with reference-path parity before counterfactual analysis.

**Results.** Mirrored shorts failed their specified comparison. Removing the trail improved some recent gold metrics but increased drawdown and changed which future trades could occur. The later portfolio decision kept the canonical exit instead of promoting the attractive variant.

**Discussion.** Better standalone R does not imply a superior portfolio. Holding-time and signal-occupancy changes invalidate naive trade-by-trade comparisons.

**Historical decision.** The frozen exit studies retained the canonical architecture under their recorded criteria. **Subsequent disposition, 3 November 2026:** after a negative, broker-reconciled September–October forward sample, the MOMCONT program was shelved for new alpha work. Earlier results are not retroactively rejected; production/reference parity remains incomplete. Strategy origins and individual code contributions must be distinguished from research direction. [Full MOMCONT study](studies/momentum-continuation.md)

### 5. DE30 continuation and sizing

**Hypothesis.** Can a one-bar full-signal persistence variant survive robustness and independent terminal validation, and does configured percentage risk match actual contract loss?

**Methodology.** Tested development performance, preregistered concentration stress, a later separately authorized sealed holdout, and risk-sizing correctness with semantic trade-path parity.

**Results.** The development concentration gate rejected the early claim of robust support, while the later terminal test passed its separate criteria. A risk-sizing correction preserved 837 reference trade paths in the historical engineering test.

**Discussion.** Development robustness, later validation and execution correctness answer different questions. A corrected sizing engine is not evidence that the project owner personally wrote the correction.

**Historical decision.** Preserve both the failed concentration gate and the later positive terminal/correctness findings without blending them. **Subsequent disposition:** the November 2026 MOMCONT program closeout also covers the DE30 sleeve and supersedes continued rollout recommendations, not its historical H026 result. [Full DE30 study](studies/de30-continuation.md)

## Other TradingBotHQ research history

The [research atlas](docs/research-atlas.md) records additional investigations: [VWAP](studies/vwap-research.md), [news/MacroImpulse](studies/news-research.md), [data forensics](studies/data-forensics.md), [Venom and momentum diagnostics](studies/momentum-and-execution.md), [NYDR/SSR/timing](studies/reconstruction-and-timing.md), and [research engineering](studies/research-engineering.md). These are historical records, not all independently validated strategies or personal authorship claims.

## Evidence and reproducibility

The [evidence register](docs/evidence.md), [provenance](docs/provenance.md), [methods](docs/methods.md) and [limitations](docs/limitations.md) explain which outcomes are public checks versus summaries of qualified private research. Raw licensed market data, proprietary EAs and live deployment settings remain private.

An AI assistant can write implementation code, tests and reports while I direct a research question or decide whether to stop. Equally, agent-originated projects that I did not personally initiate or adopt should **not** be described as my individual research achievements. Public presence alone does not establish human authorship, independent technical mastery or real trading performance.

The full historical repository may contain artifacts outside this curated research narrative. Their presence does not imply that I claim them as personal work.

**Research standard:** a useful conclusion is one that follows from a test, including a negative one.
