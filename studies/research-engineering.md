# Making research claims traceable from source to decision

[Portfolio](../README.md) · [Evidence register](../docs/evidence.md) · [Published aggregates](../results/historical-tables.md)

Research infrastructure is useful when it makes an unsupported claim harder to publish. TradingBotHQ's AI-assisted engineering program built an offline analytics and closeout layer with explicit evidence roles, source identities, verification checks and a separate path for public disclosure. Precise manual authorship is not reconstructed from Git metadata; the [ownership statement](../docs/ownership.md) separates direction, automation and coding assistance. The engineering objective was to connect a claim to inspectable evidence while preserving the distinction between software correctness, economic findings and permission to deploy. [E1](../docs/evidence.md#e1)

The independently authored public [Research OS implementation](../docs/research-os.md) is runnable code: validate real asset hashes and disclosure metadata, preserve consumed sample roles, reject invalid claims, and construct deterministic review packs. Its mutation tests demonstrate rejected states. This release does not copy the private operational engine or certify its behavior from the public demonstration.

## A compact evidence path

The local catalog imports one explicitly named compact CSV through a source manifest. The manifest records the expected SHA256, row count, time basis, evidence role, and fee status. A DuckDB catalog and derived Parquet support rebuilding and analysis outside version control. Verification checks the original inputs and derived artifacts; the catalog serves as an analysis aid rather than a replacement for the canonical research decision. [E1](../docs/evidence.md#e1)

The implementation tests consequential failure cases. A changed source, changed manifest, duplicate trade identity, or mutated derived artifact must be detectable. Unknown fees block net metrics. Already inspected evidence cannot silently regain an unseen holdout role. Idempotent imports also check metadata identity, so unchanged CSV bytes do not excuse a changed scientific interpretation. These controls are reflected in implementation tests, with recorded local QA receipts. [E2](../docs/evidence.md#e2)

A compact review-pack format adds deterministic ZIP creation and internal hashes. Its verifier also recomputes reference metrics: a self-consistent archive with newly calculated hashes but incorrect reference answers must fail. Integrity checking establishes agreement with specified bytes; agreement with a calculation requires an additional check. [E2](../docs/evidence.md#e2)

## Preserving what the numbers mean

The analytics distinguish trade outcomes measured in risk units from dated account equity. Trade-level R can support totals, profit factor, and ordered drawdown in R. It does not identify annualized account returns, CAGR, or Sharpe without the necessary capital and timing information. The synthetic trade fixture explicitly reports annualized returns as unidentifiable. A separate synthetic dated-NAV smoke included external cash flows; that is an engineering demonstration, not a historical performance claim. [E1](../docs/evidence.md#e1) [E2](../docs/evidence.md#e2)

Small governance functions encode similar boundaries. A failed candidate-support gate leaves expectancy unopened. A parity result is recorded separately from economics, with deployment authorization remaining false. Bounded handoff checks reject missing, oversized, duplicate, or hash-mismatched artifacts. Parsed tester preflight can validate identities and detect an active-campaign conflict without launching a process. [E3](../docs/evidence.md#e3)

## Reproducibility includes the checkout

The worktree freshness gate checks repository identity, guidance, required research skills, branch state, and ancestry. Its creation path refuses a dirty source or an existing destination and starts new unfrozen work from fetched private main. Frozen research has an explicit exception record tied to an exact commit; missing skills remain visible instead of being disguised by rewriting scientific ancestry. [E4](../docs/evidence.md#e4)

This is a capability of the maintained tooling checkout. Historical research branches can still lack current tooling, and the gate reports that limitation. It does not make every branch current automatically.

Formal closeout creates a private candidate for review, while public disclosure remains a separate decision. The demonstrated pack export was synthetic; broader historical export requires its own clearance. These controls demonstrate offline engineering and deterministic validation. They do not certify historical broker execution, live risk behavior, or deployment readiness. [E1–E4](../docs/evidence.md#engineering-source-register)

The public [methods code](../src/srl/validation.py) illustrates narrow semantic checks. It is separate from the private Research OS implementation. The [evidence register](../docs/evidence.md#engineering-source-register) identifies the inspected implementation and recorded QA.
