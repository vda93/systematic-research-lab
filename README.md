# TradingBotHQ research

Systematic trading research focused on robustness, honest validation and realistic execution. These case studies examine how trading ideas behave under stricter tests and what evidence is sufficient to justify a decision.

**[Browse the research library](https://vda93.github.io/systematic-research-lab/)** · [Research by Andrew Vu](https://www.linkedin.com/in/andrew-vu-4861b9191/)

## ORBINDEX

An opening-range timing search across German, Japanese and UK index CFDs produced three frozen German-index portfolios. All three lost fixed-volume EUR in the later historical comparison, before additional commission or financing. Earlier research may have inspected some of that later history, so it is not a pristine holdout.

[Read the study](https://vda93.github.io/systematic-research-lab/orbindex.html) · [Complete technical record](studies/orbindex.md)

## ORB: cash-open setup, EMA filter, and later results

Another opening-range breakout study: form the range at the New York cash open, require a completed candle to confirm the breakout, place the stop across the range, and take profit at a fixed multiple of initial risk. I later added an EMA trend filter and compared the variants in discovery.

The study reports **48 US500/USTEC configurations**, then compares the same selected US500 setups in sample and in later historical periods. All four weakened; the bidirectional ATR setup stayed slightly positive. The EMA extension has no qualified later result, and no candidate was promoted.

[Setup and full study](studies/orb-setup-filters.md) · [Released aggregate data](data/orb-setup-filters-public.json)

## News-Release Trading

Historical FX news tests showed promise under their stated cost assumptions. Live spreads, slippage and poor fills across brokers made the strategy impractical to pursue.

[Why I shelved this](https://vda93.github.io/systematic-research-lab/macroimpulse.html) · [Complete technical record](studies/news-research.md)

The public code rebuilds released figures from aggregates. Replaying the original market backtests requires private inputs. I bring the research ideas, direct the investigations and make the final decisions; code implementation uses AI assistance. [Sources and limits](docs/provenance.md)
