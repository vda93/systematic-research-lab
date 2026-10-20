# What the evidence supports

- Every observation is synthetic. There is no real trading ledger, vendor feed, market forecast or evidence of a tradable edge.
- The concentration example was deliberately constructed to fail. It demonstrates arithmetic, grouping and decision discipline rather than discovering a phenomenon.
- The calibration audits one artificial AR(1) family at fixed parameters. Its 80 trials are a finite Monte Carlo diagnostic. All specified methods under-cover nominal 95% in this run; this does not prove that block bootstrap always fails or that one length is generally optimal.
- The supplied paths have explicit close-date net amounts, not portfolio NAV, flows, marked exposure or executable prices. CAGR, annualized Sharpe, account pass probabilities and economic viability are not inferred.
- Event correspondence does not regenerate opportunities after changed exits, position overlap or risk constraints. No production strategy, position-sizing engine or broker integration is included.
- Same-date record keys impose deterministic ordering for drawdown. Intraday timing is absent. Known synthetic costs are teaching inputs; financing and realistic fill costs are not modeled.
- Results are conditional on the protocol and implementation. Cross-platform CI provides engineering evidence, not independent scientific replication or a proof of statistical coverage.
- Hashes establish replay identity. They do not confer an earlier timestamp, establish unseen-data access or turn a constructed recipe into prospective validation.

Natural extensions would be a separately governed empirical study using redistributable data, a broader predeclared calibration grid with uncertainty on coverage, and additional inferential methods such as studentized intervals. They would create new evidence; none is implied by this release.
