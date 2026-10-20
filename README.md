# TradingBotHQ · Systematic Research Lab

**Empirical systematic-trading research: test the mechanism, challenge the backtest, verify the implementation, and stop when the evidence fails.**

TradingBotHQ is my independent quantitative research program. This portfolio distills its real historical experiments into research case studies, selected aggregate results and original figures. The work spans momentum continuation, opening ranges, candle features, event-driven trading and the infrastructure needed to investigate them. It includes rejected hypotheses and unresolved questions alongside constructive findings.

## Sixty seconds

| Question | What the research found |
| --- | --- |
| Does a better recent exit deserve promotion? | XAU no-trail increased recent total from **+48.72R to +52.83R**, while drawdown rose from **6.22R to 12.66R**. Earlier eras and portfolio sensitivity did not justify replacing the canonical exit. [MOMCONT](studies/momentum-continuation.md) |
| Can a positive backtest fail robustness? | DE30 development fell from **+41.46R to −5.43R** after removing its ten best complete entry-date cohorts. A separate sizing repair preserved **837/837** meaningful trade paths. [DE30](studies/de30-continuation.md) |
| Can correct software implement an unsuccessful strategy? | USTEC ORB passed one OOS block and failed the next. A separate gold lineage passed final implementation parity but failed monetary qualification and its terminal holdout. [ORB](studies/opening-range.md) |
| Does failed continuation imply profitable reversal? | NOWICK's matched continuation effect was **+0.079 percentage points**, with a 95% interval crossing zero. A separately frozen reversal study rejected all three tested cells. [NOWICK](studies/nowick.md) |

R is normalized initial planned trade risk, not an account-return percentage. These are reported historical results. Sample roles, costs, uncertainty and source access limits are stated in each study and the [evidence register](docs/evidence.md).

![Historical momentum results: directional symmetry and cross-era exit comparison](figures/momentum.svg)

## Five minutes

Read a case study that interests you, then inspect how it was challenged:

- [Research atlas](docs/research-atlas.md): the wider evidence survey, including studies that did not become flagships.
- [Research engineering](studies/research-engineering.md): source manifests, mutation detection, evidence roles and reproducible closeout.
- [Methods](docs/empirical-methods.md): estimands, occupancy, paired block inference, concentration and semantic parity.
- [Timeline](docs/timeline.md): how hypotheses evolved and why the decisions changed.

## Thirty minutes

Follow a claim from a [case study](studies/momentum-continuation.md) to the [source register](docs/evidence.md), [machine-readable aggregates](data/historical-results.json), [generated tables](results/historical-tables.md) and [figure reconstruction](scripts/render_historical.py). The [aggregate diagnostics](results/aggregate-diagnostics.json) derive the concentration, risk-fill and cross-era comparisons directly in [inspectable code](src/srl/diagnostics.py). Then inspect the [paired resampling](src/srl/resampling.py), [cost accounting](src/srl/accounting.py) and [semantic comparator](src/srl/validation.py), with their [tests](tests).

The original [synthetic methods study](docs/study.md) remains available as a supporting calibration exercise. It is explicitly synthetic and supplies no evidence of a market edge.

## Rebuild and verify

Python 3.12 or 3.13, in a fresh virtual environment:

```sh
python -m pip install .
python scripts/reproduce.py --check
```

This runs the tests, disclosure and link audit, rebuilds the historical aggregate tables and four Matplotlib figures, and replays the synthetic calibration. To retain a separate bundle with hashes:

```sh
python scripts/reproduce.py --check --output build/my-run
```

CI runs on Linux and Windows with both Python versions. Historical backtests require private licensed inputs and are **not** reproduced by this command. The public verification boundary is [documented explicitly](docs/provenance.md).

## Scope and authorship

This is vda93's research portfolio, prepared with AI-assisted engineering and writing. Public prose, figures and methods code are released under [MIT](LICENSE). Private strategy implementations, raw market data, account records, production configurations and evidence bundles are excluded.

The strongest result is the ability to distinguish a promising observation, a failed test, a correct implementation and an unresolved economic question. The [limitations](docs/limitations.md) remain part of the research.
