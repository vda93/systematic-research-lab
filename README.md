# TradingBotHQ | Systematic Trading Research

I investigate whether intuitive trading ideas survive systematic testing. The question is not whether a chart setup looks convincing, but whether its rules can be implemented consistently, compared with sensible controls and evaluated after trading costs.

This portfolio focuses on research I recognize, directed or participated in. The underlying trading ideas often originated with other traders; I used AI-assisted implementation, analysis and review. Neither that assistance nor the presence of a study in Git implies that I invented a strategy or personally wrote every line of code. [Ownership and assistance](docs/ownership.md).

## Four research stories

### 1. Opening-range breakout (ORB)

**The idea.** Mark the high and low of a market's first defined trading window. When price breaks beyond that range, test whether directional continuation follows. Our documented version waited for a completed five-minute breakout candle, placed a stop around the range midpoint and used either a market entry or a retest of the broken boundary depending on planned risk/reward. This summarizes **our recorded tested implementation**, not an independently recovered original FX Replay PDF.

**Hypothesis.** Does the opening range itself explain continuation, or would simpler time-of-day momentum do just as well?

**Method.** Tested Nasdaq and gold CFD timing configurations, placebo range boundaries, independent validation periods, exact-tick/MQL5 correspondence and execution/financing costs.

**Finding.** Some development configurations and a first Nasdaq validation period looked promising; range-specific geometry did not establish a unique effect and the next independent validation failed. The gold implementation passed important parity checks but not the full economic/terminal qualification.

**Decision.** Close the tested original program for deployment. Preserve separate untested hypotheses as untested, not as failures. [ORB study](studies/opening-range.md) · [Branch decisions](studies/opening-range-atlas.md).

### 2. Engulfing Bar Play (EBP)

**The idea.** In Omar Agag's *EBP Strategy (Swing Trading Variation)*, a candle sweeps the previous candle's high or low and closes through the body on the other side. A decisive close near its extreme suggests a continuation setup, with a proposed limit entry on a partial retracement; a less decisive close uses a deeper retracement. The source specifies a 2R target and additional management rules. We tested explicit mechanical interpretations rather than treating the visual idea as one unambiguous program.

**Hypothesis.** Does a candle-engulfing setup retain an advantage once ambiguous order lifetime, retracement and timeframe rules are made explicit?

**Method.** Reconstructed alternative pending-order semantics, corrected a native-timeframe test matrix and examined a separate observational small-candle mechanism.

**Finding.** The order interpretation materially changed exposure. The corrected discovery matrix was generally weak; a small-candle association did not demonstrate a profitable opposite-side trade.

**Decision.** Preserve the tested interpretations without selecting the most flattering replay as a winner. [EBP study](studies/engulfing-and-support.md).

### 3. NOWICK

**The idea.** In Bard FX's *Compensation Play (Nowick) Strategy*, a candle with little or no wick on one side signals an apparent directional imbalance. The source proposes trading with the trend after a retest within nine candles, with a structure-based stop and a 1:1 target. That sounds plausible, but a visually distinctive candle may simply encode momentum or volatility already visible elsewhere.

**Hypothesis.** Does wicklessness add predictive information beyond otherwise comparable candles? If continuation lacks support, does a separately specified reversal hypothesis work?

**Method.** Matched pattern events with comparable ordinary candles across four FX instruments. Tested reversal separately, with its own frozen controls and costs. These research contracts are not a claim to have replayed every discretionary filter in the source PDF.

**Finding.** No robust incremental continuation advantage was established. The separately specified reversal also failed.

**Decision.** Shelve the original family and reject the tested reversal without trying to manufacture a reverse-trading edge. [NOWICK study](studies/nowick.md).

### 4. MacroImpulse: news-driven event trading

**The idea.** Major scheduled economic announcements can move currency prices sharply. We studied an event-time strategy that attempts to capture the post-release price impulse using preplanned trigger levels. The difficulty is that the same moments can produce wider spreads, sequential opposite-side triggers and poor fills.

**Hypothesis.** Can a repeatable event-driven entry survive realistic trading frictions, data-quality checks and independent validation, and can filters improve the *whole* trade process rather than just retrospectively identify losing trades?

**Method.** Evaluated historical event-triggered trades, execution mechanics, spread/commission assumptions, trigger-time filters, early-exit proposals and the completeness of economic-calendar records.

**Finding.** Some historical spread-only results were positive, but several seemingly sensible filters failed. A later medium-impact calendar source lost coverage, invalidating a clean out-of-sample strategy verdict rather than proving either success or failure.

**Decision.** Preserve the engineering and data-forensics lessons; the historical program remains shelved until the event universe and execution economics can be independently qualified. [Event-driven study](studies/news-research.md) · [Calendar forensic case](studies/data-forensics.md).

## How the research is conducted

Each case study distinguishes **hypothesis, method, results, discussion and decision**. I try to freeze comparisons before looking at outcomes, check selection effects and alternative explanations, distinguish event studies from executable trading backtests, and refuse to promote a strategy merely because one historical configuration is attractive.

Many historical results are documented from qualified private reports; they **cannot be independently replayed using this public repository alone**. Public code and tests illustrate selected methods, not a substitute for licensed tick data, vendor strategy code, complete trade ledgers or broker execution records. See the [evidence register](docs/evidence.md), [limitations](docs/limitations.md) and [provenance](docs/provenance.md).

The original EBP and NOWICK ideas are credited to Omar Agag and Bard FX in FX Replay educational strategy materials. Their PDFs are not redistributed here; source-specific rules, tested mechanical approximations and empirical verdicts are different things.

**Research standard:** a useful result includes a clear reason to reject or shelve a hypothesis when its evidence is insufficient.
