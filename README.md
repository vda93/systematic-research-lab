# TradingBotHQ research

Systematic trading research focused on robustness, honest validation and realistic execution. These case studies examine how trading ideas behave under stricter tests and what evidence is sufficient to justify a decision.

**[Browse the research library](https://vda93.github.io/systematic-research-lab/)** · [Research by Andrew Vu](https://www.linkedin.com/in/andrew-vu-4861b9191/)

## ORBINDEX

An opening-range timing search across German, Japanese and UK index CFDs produced three frozen German-index portfolios. All three lost fixed-volume EUR in the later historical comparison, before additional commission or financing. Earlier research may have inspected some of that later history, so it is not a pristine holdout.

[Read the study](https://vda93.github.io/systematic-research-lab/orbindex.html) · [Complete technical record](studies/orbindex.md)

## Trading Steady ORB: independent reconstruction and later historical validation

An independent reconstruction of a publicly described S&P 500 opening-range breakout was expanded into **48 fixed US500/USTEC real-tick configurations**. None of 27 corrected factor contrasts was significant. Later US500 data were much weaker than discovery, and USTEC's later period was source-blocked. No strategy was promoted; historical all-in broker net remains unknown.

[Full case study](studies/trading-steady-orb.md) · [Released aggregate data](data/trading-steady-orb-public.json)

## News-Release Trading

Historical FX news tests showed promise under their stated cost assumptions. Live spreads, slippage and poor fills across brokers made the strategy impractical to pursue.

[Why I shelved this](https://vda93.github.io/systematic-research-lab/macroimpulse.html) · [Complete technical record](studies/news-research.md)

The public code rebuilds released figures from aggregates. Replaying the original market backtests requires private inputs. I bring the research ideas, direct the investigations and make the final decisions; code implementation uses AI assistance. [Sources and limits](docs/provenance.md)
