# Originality, evidence scope and reproducibility

This release was independently authored for Systematic Research Lab. Its generic Python methods, tests, experiment recipe, documentation, synthetic outputs and explanatory SVG were created for this repository with AI-assisted engineering. No private research source, historical experiment output, operational configuration, licensed market dataset or inherited repository history is part of the release.

All numerical outputs derive from [experiments/protocol.json](../experiments/protocol.json). The [result ledger](../results/study.json) retains the constructed cohort contributions and every calibration trial for every declared block length. The [figure renderer](../src/srl/visuals.py) consumes that same result structure. The reproduction command rebuilds both artifacts and fails on a byte mismatch.

`release-files.json` is the exact publication inventory. The local audit checks inventory equality, source types, links, private-content patterns and Git history metadata. Automated scans are useful controls rather than a proof that any arbitrary future addition is safe; changes need the same review discipline.

Runtime code uses only the Python standard library. Optional packaging uses the public pinned setuptools build dependency declared in pyproject.toml. No account, API key, private infrastructure or network input is used by the experiment.

The protocol's design is a reproducible teaching specification. The concentration outcome is intentionally constructed, and no independent timestamped preregistration is claimed. The calibration retains its misses rather than tuning the generator or block settings to improve the reported coverage.

All original material in this repository, including prose and figures, is released under [MIT](../LICENSE). The public Git identity uses the repository owner's noreply address.
