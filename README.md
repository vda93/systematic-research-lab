# TradingBotHQ systematic trading research

I investigate what happens to familiar trading setups when their rules are made explicit. The studies follow each idea from the chart to a decision about whether it is worth trading.

**[Browse the research library](studies/README.md)** for the questions, findings and decisions on opening-range breakouts, engulfing candles and scheduled news.

## How much can one order rule change a test?

In the gold Engulfing Bar Play study, keeping an unfilled order open could block the next signal. Each persistent-order version closed just 3 trades. Versions that could replace the pending order closed 1,257 and 1,297. The positive result on three trades was too sparse to select a winner. [Read the study](studies/engulfing-and-support.md) · [Order-policy evidence](docs/evidence.md#b21)

![Closed trades and total price R for the gold pending-order policies under two break-even rules](figures/ebp-order-policy.svg)

*Each version saw the same signals. The counts show how often each set of order rules reached a closed trade on the historical sample. Price R measures the result relative to initial price risk.* [Figure source and limits](docs/ebp-visual-evidence.md)

## How to read the evidence

Each study specifies the signal, order rules and costs, then tests the proposed explanation against a relevant control or a later sample where available. The article identifies which evidence informed selection and which evidence determined the decision. [Research atlas](docs/research-atlas.md) · [Empirical methods](docs/empirical-methods.md)

The public Python code reproduces selected aggregate figures and tables and runs synthetic examples. Replaying the original market experiments requires private inputs and implementations. [Code](src/srl) · [Reproduction instructions](docs/security.md#reproduce-the-checks) · [Evidence register](docs/evidence.md) · [Limitations](docs/limitations.md)

I direct the research questions and priorities. Engineering, analysis and writing use AI assistance. The project draws on trading ideas with prior sources. [Contribution record](docs/ownership.md) · [Provenance](docs/provenance.md)
