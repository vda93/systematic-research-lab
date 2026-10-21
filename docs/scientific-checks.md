# What the scientific checks actually enforce

The [claim registry](../data/claim-registry.json) binds reviewed digit-bearing Markdown blocks to exact text hashes and declared source IDs. It includes tables and headings. Navigation, software instructions and mathematical examples are explicitly classified as documentation or methods. Changing a quantitative paragraph, adding a document, removing a source or changing a declared figure input requires a new review. CI never regenerates this approval ledger automatically.

Every retained private source ID resolves to the [evidence register](evidence.md). This is traceability to a reviewed report, not a public re-analysis of its hidden data. A public-replay claim must refer to a public-replay source; changing its label cannot convert a private report into reproducible observations. The ledger's SHA256 values identify text and inputs; they do not prove a number true. Fenced code is excluded from prose enumeration and covered by executable checks.

Some blocks inherit a document-level source family; this is coarser traceability than a metric-by-metric evidence mapping. Specific citations beside historical findings and the separately retained private provenance provide the finer review context.

The [Research OS example](../experiments/evidence-example.json) validates the actual public historical aggregate asset as a consumed, spent reported aggregate. [Tests](../tests/test_evidence.py) reject altered bytes, disclosure gaps, overlapping scientific roles, invalid clean-OOS claims and attempts to rename spent evidence under a new identity. Transition checks require a trusted earlier ledger. A malicious rewrite of both current and historical metadata remains outside unsigned-manifest protection.

The [real-market pipeline](../src/srl/fx_study.py) separately qualifies the frozen provider snapshot, constructs information-ordered features, purges temporal boundaries, resets bootstrap seeds, reports the full fixed family and regenerates results. Its tests use small synthetic fixtures to test software behavior; empirical findings come from ECB observations. Exact output replay establishes repeatability under the pinned implementation. It does not establish market stationarity, bootstrap coverage, executable prices or future alpha.

Source review is still required. Passing software and reproduction checks does not settle scientific interpretation or permission to publish.
