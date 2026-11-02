# TradingBotHQ · Systematic Research Lab

This is a **curated public record of systematic trading research I directed**, with substantial AI-assisted coding, analysis, review and writing. It is not a claim that I invented every underlying strategy or personally implemented every experiment. [Ownership and assistance](docs/ownership.md) explains what the records establish and what remains unverified.

I am most interested in research that can **reject** a plausible trading hypothesis: qualified data, frozen controls, independent validation, implementation correctness, realistic execution costs and documented stopping decisions. The studies below report historical experiments, not live-account profitability or deployment approval.

## Start with the TradingBotHQ research programs

These are the historical strategy families I want to be accountable for explaining. Many methods and implementation details were developed by agents; ownership of a research decision is not sole authorship of its code.

| Program | Research question and outcome | Read |
| --- | --- | --- |
| **Opening-range breakout (ORB)** | Would timing regions and range geometry survive mechanism controls, independent validation and financing? The tested program closed without deployment authorization; some exploratory branches remain untested rather than proven failures. | [ORB case study](studies/opening-range.md) · [branch atlas](studies/opening-range-atlas.md) |
| **Engulfing / EBP** | Can the original rules and broker behavior be reconstructed faithfully? Pending-order interpretations radically changed exposure; a repaired 88-cell timeframe matrix was weak, and a separate negative small-candle association did not justify a reversal strategy. | [EBP and strict-support research](studies/engulfing-and-support.md) |
| **NOWICK and ANTI-NOWICK** | Does an almost wickless candle add information beyond matched ordinary candles, and does reversing it help? Neither frozen claim passed; the original family was deliberately shelved. | [NOWICK closeout](studies/nowick.md) |
| **MOMCONT, USDJPY and gold** | Which parts of a vendor-derived continuation system survive direction, exit, era and portfolio-level challenges? Attractive alternatives were not automatically promoted over the canonical exit. | [MOMCONT research](studies/momentum-continuation.md) |
| **MOMCONT on DE30** | Could a one-bar persistence candidate survive concentration and holdout tests, while execution sizing remained correct? Development concentration failed; later terminal evaluation and sizing correction were separately recorded. | [DE30 research](studies/de30-continuation.md) |

**My documented role:** I select and commission trading research, direct questions and priorities, interpret findings and make decisions to continue, park or stop. Individual strategy origins, exact experiment designs, calculations and code authorship vary. Do not interpret any study as independently hand-coded or personally derived without its own evidence. See the [contribution map](docs/ownership.md).

## What the research process looks like

1. **Specify a falsifiable claim.** Identify its actual mechanism, not just a backtest's highest parameter cell.
2. **Qualify the inputs.** Data coverage, time alignment, broker semantics and rights are separate gates.
3. **Preserve controls and sample roles.** Discovery is not OOS; opened lockboxes stay spent; exact historical ancestry matters.
4. **Challenge the hypothesis.** Run relevant ablations, matched comparisons, concentration checks and independent validation without retrospective rescue.
5. **Check implementation and costs.** Code parity does not prove a viable net strategy.
6. **Record the decision.** Promote, reject, park or stop, even when the result is disappointing.

Examples: [ORB selection risk](studies/opening-range.md), [EBP exposure semantics](studies/engulfing-and-support.md), [NOWICK matching and reversal rejection](studies/nowick.md), [MOMCONT paired exit comparison](studies/momentum-continuation.md).

## Wider historical research

The [research atlas](docs/research-atlas.md) maps the larger TradingBotHQ history, including [VWAP](studies/vwap-research.md), [news and MacroImpulse](studies/news-research.md), [calendar-data forensics](studies/data-forensics.md), [NYDR, SSR and timing](studies/reconstruction-and-timing.md), [Venom and additional momentum](studies/momentum-and-execution.md), and [research infrastructure](studies/research-engineering.md). A historical branch being parked does not mean it failed OOS or must be restarted.

### Additional public studies and AI-assisted engineering

The following are available to inspect but **are not presented as my independently originated or personally implemented flagships**:

- [BTCUSDT BBO execution-delay study](studies/bbo-execution-delay.md): explicitly **AI-proposed and AI-implemented**. The complete final sample retained a failed support verdict; its reported displayed quote costs are not guaranteed fills or alpha. This is distinct from the historical BTCUSD2 TradingBotHQ bot research.
- [ECB FX reference-rate momentum](studies/fx-reference-momentum.md): a public reference-data study that failed its fixed comparison. Individual personal idea origin and unaided technical defense are not established. Reference observations do not establish executable trading returns.
- [Exact circular-block means](docs/exact-block-means.md): an **AI-assisted implementation**, with source, independent arithmetic tests and a workload-specific benchmark. Public code quality does not by itself establish my personal derivation or manual coding.
- [Public Research OS](docs/research-os.md): AI-assisted evidence/governance utilities; distinct from the private TradingBotHQ operational system.

These artifacts remain in the repository for provenance and inspection, not as a shortcut to personal authorship claims.

## Evidence, provenance and limitations

- [Claim and evidence register](docs/evidence.md) distinguishes historical summaries, publicly checkable results, partial verification and missing source access.
- [Ownership, assistance and study identity](docs/ownership.md) keeps unknown personal contributions unknown.
- [Provenance](docs/provenance.md), [methods](docs/methods.md), [empirical methods](docs/empirical-methods.md) and [limitations](docs/limitations.md) describe assumptions and reproduction boundaries.
- Private EA sources, vendor tick data, account credentials, proprietary artifacts and live deployment configurations are not published. Historical R is normalized planned price risk, not a guaranteed account return.

### Reproduce the public engineering checks

With Python 3.12 or 3.13 in a clean virtual environment:

~~~sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps .
python scripts/reproduce.py --check
python scripts/benchmark_block_means.py --repeats 5 --repetitions 2048
~~~

Public tests validate released software and derived artifacts; they do **not** independently rerun licensed private backtests or authenticate human authorship. Historical research results should be assessed through the [evidence register](docs/evidence.md). [Data terms](DATA_LICENSE.md), [software license](LICENSE), [security](SECURITY.md) and [roadmap](docs/roadmap.md) remain separate.

**Principle:** preserve the evidence, be clear about who did what, and don't promote a result that failed its gate.
