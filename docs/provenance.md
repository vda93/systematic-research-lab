# Public evidence and reproducibility boundaries

The portfolio documents selected private TradingBotHQ research on ORB, EBP, ORBINDEX and MacroImpulse. The original trading setups were sometimes published by other traders. Original public prose, AI-assisted engineering and human decisions are not interchangeable kinds of authorship. The [ownership disclosure](ownership.md) and [evidence register](evidence.md) describe those boundaries.

The public [historical aggregate data](../data/historical-results.json) retain original ORB and archived NOWICK summary metrics. The separate [ORBINDEX aggregate extract](../data/orbindex-public.json) supports six public charts, derived from reviewed 2020–2023 discovery and 2024–2026 later-period receipts. [Historical figure code](../scripts/render_historical.py) rebuilds two illustrations and an aggregate table; the [diagnostic module](../src/srl/diagnostics.py) checks arithmetic identities. This is a reproducible presentation from disclosed aggregates, **not** an independent replay of unavailable raw feeds, broker fills or private execution code. Other flagship results are historical reported conclusions, not public trade-level backtests.

The illustrated [ORB](orb-visual-evidence.md), [EBP](ebp-visual-evidence.md) and [MacroImpulse](macro-visual-evidence.md) studies additionally disclose source-bound configuration and reported-result projections. Their Python renderers reproduce complete parameter surfaces and selected comparisons. Original archive/member identities, missing sources and per-figure classifications accompany each study; private trade rows and proprietary market data remain outside the publication boundary. Labelled fictional mechanics remain separate from empirical results.

The [review reports and coordinator response](reviews/visual-v002-resolution.md) preserve the initial findings, subsequent corrections, checks actually run and outstanding presentation limits.

The [synthetic methods study](study.md) is separate from historical markets. Its fixed protocol and generated figures demonstrate software behavior and a synthetic inference example, not investable performance or independent preregistration.

The [source inventory](../release-files.json) and [publication checks](../scripts/audit_public.py) validate the current tree and inspect old public history. Deleting irrelevant files from current HEAD does **not** rewrite historical commits. Previously public files remain historical Git records and are excluded from the new portfolio narrative.

Public code and original writing are under [MIT](../LICENSE). That license does not grant rights to excluded market data, external strategy PDFs or proprietary EAs. External explanatory handouts, where consulted during rule formalization, are not redistributed here. Exact source provenance is retained separately in the private research records.

## MacroImpulse closeout clarification

On 12 November 2026, the project owner clarified that MacroImpulse was shelved because live execution across brokers was inadequate: fills were wide, and spreads and slippage were large. The available execution conditions were insufficient for the strategy. This is the owner's account of the practical stopping decision, rather than a new measured broker-by-broker cost study.

The calendar-coverage defect belongs to a separate medium-impact historical evaluation and limits that sample's validity. It was not the reason given for shelving the broader program. Repairing that calendar would not by itself resolve the live execution problem. Previously reported numerical results and the sample's INVALID_DATA_UNIVERSE classification are unchanged.
