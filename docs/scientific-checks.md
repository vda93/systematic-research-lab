# What the scientific checks enforce

The [claim registry](../data/claim-registry.json) records hashes and source categories for reviewed quantitative prose blocks, as well as figure-input hashes and source references. CI checks this ledger but never automatically approves new results.

The retained [evidence register](evidence.md) distinguishes historical private reports from publicly executable synthetic checks. Hash equality proves byte identity, **not** that a hidden backtest is correct. Reworded conclusions, revised claims or changed figure inputs need explicit review.

The [evidence example](../experiments/evidence-example.json) is checked as reported, previously inspected data. [Tests](../tests/test_evidence.py) reject altered bytes and incompatible scientific roles. Unsigned evidence manifests cannot defend against a malicious rewrite of the current and historical ledger together.

The [index renderer](../scripts/render_orbindex.py) and [news renderer](../scripts/render_macro.py) regenerate figures from published aggregates. A separate [synthetic protocol](../experiments/protocol.json) generates artificial observations. The [site renderer](../scripts/render_site.py) builds the public reading edition from reviewed Markdown and approved figures.

Full repository verification also checks file types, internal links, Python tests, source inventory and CI workflows. Passing checks does not certify profitability, independent historical replication or authorship.
