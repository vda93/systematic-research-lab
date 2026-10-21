# Ownership, assistance and study identity

[Portfolio](../README.md) · [Evidence register](evidence.md) · [Reproducibility boundary](provenance.md)

TradingBotHQ is my research project. I direct this portfolio's questions, priorities and presentation, and take responsibility for preserving the research decisions and their limitations. Engineering, analysis, review and writing use automated systems and AI assistance.

Personal ownership does not mean that I manually wrote every line of code or originated every historical hypothesis. The study pages distinguish a documented research decision from a calculation performed by a research engine, a repair implemented with assistance, and a result retained from a canonical record. Git author names establish attribution metadata; they cannot establish manual implementation.

## Contribution evidence

| Contribution | What the record establishes | What remains unverified |
| --- | --- | --- |
| Historical hypothesis development | [MOMCONT H006–H010](../studies/momentum-continuation.md#how-the-earlier-question-developed) records competing explanations, a factorial comparison and rejection of the original horizon explanation. | Who first proposed each question or design. The records do not establish personal idea origin. |
| A personal research decision | The [NOWICK closeout](evidence.md#n1) explicitly labels rejection and shelving of the original family as a user decision. | That decision does not establish authorship of the matching engine or statistical analysis. |
| Public engineering | The [evidence package](research-os.md) has public source, adversarial tests and an AI-assisted implementation receipt. I supplied project requirements; implementation used agents. [E5](evidence.md#e5) | A function-by-function account of my manual code and review contributions. |
| Independent technical defense | The source and tests provide inspectable material for derivation, modification and debugging exercises. | My unaided performance has not been assessed. Preparation worksheets are not evidence of completed exercises or mastery. |

Personal hypothesis-origin, manual-authorship and review claims remain **HUMAN_ATTESTATION_REQUIRED** where the records do not identify them. Any later attestation must describe the specific contribution and its supporting artifact; it cannot retroactively turn AI work into unaided work. New explanatory prose and engineering in this portfolio also use AI assistance.

## What the five main stories represent

| Study or system | Identity | My documented role and the assistance boundary |
| --- | --- | --- |
| [MOMCONT](../studies/momentum-continuation.md) | Momentum-continuation bot family on USDJPY and gold CFDs, H1. Directional and exit comparisons feed a portfolio-level decision. | I preserve the decision to retain canonical exits when the attractive alternative changed path occupancy and remained sensitive to inference assumptions. [H025's decision and handoff](evidence.md#m7) establish the historical result. Automated replay and analysis produced the calculations; the inspected records do not identify the personal origin of every rule or code contribution. |
| [MOMCONT on DE30X H1](../studies/de30-continuation.md) | The same bot family adapted to a German equity-index CFD. One-bar full-signal persistence, concentration stress, terminal validation and sizing correctness are separate experiments. | I keep the failed development concentration gate visible alongside later evidence. The [sizing study](evidence.md#d7) records a repair and 837/837 meaningful historical trade paths. That is a historical engineering gate, distinct from a later production hotfix and current build qualification. No sole manual authorship is inferred from its source hashes. |
| [ORB](../studies/opening-range.md) | Opening-range breakout research on gold and US technology-index CFDs. Tick-driven sessions, anchors and range durations define the studies. | I preserve conflicting validation blocks, mechanism controls and the [closed deployment verdict](evidence.md#o6). Automated campaigns, Python/MT5 comparison and AI-assisted forensic engineering supported the workflow. A large search and its infrastructure do not by themselves establish a deployable signal or prove personal design of every component. |
| [NOWICK](../studies/nowick.md) | Mechanical wickless-candle trading family; H004 studies USDJPY2, AUDUSD2, GBPUSD2 and AUDJPY2 on M15. Separate ANTI-NOWICK R001 uses AUDJPY2 M5, XAUUSD2 M5 and XAUUSD2 M15. | The canonical closeout explicitly records my decision to reject and shelve the original trading family, with no more continuation optimization or timeframe fishing. I preserve the separate reversal rejection. The [matched-study](evidence.md#n1) and [reversal](evidence.md#n2) evidence comes from research-system implementation, deterministic matching and assisted analysis; the personal shelving decision does not establish sole authorship of those tools. |
| [Research OS](../studies/research-engineering.md) | Evidence governance and research infrastructure. It has no trading instrument or chart timeframe. | I set this portfolio's evidence and reproducibility requirements. AI-assisted utilities and automated checks implement inspectable controls for identity, sample roles and claims. The [private-system evidence](evidence.md#e1) and [public implementation](research-os.md) have distinct scopes; the public code is not an export of the private operations system. |

The [MacroImpulse data-forensics case](../studies/data-forensics.md) shows another part of that responsibility: preserving a failed mechanical output while withdrawing its clean-OOS interpretation after a source-coverage defect. The historical audit detected and adjudicated the defect; this portfolio does not claim that I personally counted every missing recurring key. It also retains the audit's correction that HIGH-impact vendor activity could not validate MEDIUM-impact calendar coverage.

## What a reviewer can verify

Public code, tests, declared inputs and reproduction commands show the behavior of the released implementation. Original prose and figures explain selected historical results. A private claim-to-source ledger connects those summaries to canonical records, identities and hashes.

The private historical backtests, account simulations, strategy code and raw market data remain outside this repository. Their aggregates are historical evidence summaries, with the [verification limits](evidence.md) stated beside them. Public test success does not independently authenticate unavailable private inputs, establish realized broker performance or authorize deployment.

The record shows the decisions I take responsibility for preserving: keep failed stress tests visible, withhold promotion when sensitivities disagree, and correct explanations that the evidence no longer supports. Engineering correctness and economic support retain separate decisions.

