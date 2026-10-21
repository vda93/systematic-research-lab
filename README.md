# TradingBotHQ · Systematic Research Lab

**Independent quantitative research: falsifiable questions, preserved failures and tested research software.**

TradingBotHQ is my systematic-trading research program. I direct its questions, constraints and publication decisions using automated research systems and AI-assisted engineering. The historical closeout explicitly records my decision to shelve NOWICK. Exact manual authorship of every private component is not established; [ownership and AI assistance](docs/ownership.md) states that boundary plainly.

This portfolio combines authentic historical research summaries with a new, completely reproducible study of real ECB FX reference observations. The historical case studies rebuild published aggregates; the ECB study rebuilds the empirical analysis from a lawfully distributed snapshot. These are different verification scopes.

## Sixty seconds

| Research question | Finding and decision | What it demonstrates |
| --- | --- | --- |
| Does removing the MOMCONT exit trail help? | XAUUSD2 H1 recent total rose from **48.72R to 52.83R**, while drawdown rose from **6.22R to 12.66R**. Cross-era and portfolio evidence retained canonical exits. [MOMCONT](studies/momentum-continuation.md) | Occupancy, paired comparisons, economic tradeoffs |
| Can a positive MOMCONT DE30X H1 backtest fail? | Removing ten best entry-date cohorts changed development **+41.46R to −5.43R**. A separate sizing repair preserved **837/837** meaningful trade paths. [DE30X](studies/de30-continuation.md) | Concentration stress versus engineering correctness |
| What did the ORB timing search earn? | The **1,728-configuration** USTEC2 search led to a representative region; a later validation block failed. Gold parity passed but economics did not. [ORB](studies/opening-range.md) | Selection risk, independent gates, financing |
| Does failed continuation imply profitable reversal? | NOWICK's incremental continuation interval crossed zero; all three independent reversal cells failed their frozen gate. [NOWICK](studies/nowick.md) | Matched controls, dependence, multiplicity, stopping |
| Can clean execution validate damaged research data? | MacroImpulse's later MEDIUM-event calendar lost coverage. **INVALID_DATA_UNIVERSE** superseded a clean strategy-failure interpretation. [Data forensics](studies/data-forensics.md) | Universe qualification before statistical inference |

R is normalized initial planned trade risk, not an account-return percentage. All historical numbers retain their [source records and limitations](docs/evidence.md). Favorable engineering evidence does not authorize trading.

## Five minutes

Read the [MOMCONT](studies/momentum-continuation.md), [DE30X H1](studies/de30-continuation.md), [ORB](studies/opening-range.md) and [NOWICK](studies/nowick.md) contract tables, then the [calendar failure](studies/data-forensics.md). Each identifies its system, markets, hypothesis, comparison, sample and decision. The [engineering case](studies/research-engineering.md) separates semantic parity, numerical tolerances and economic validation.

| Capability | Inspect the evidence | Inspect the software |
| --- | --- | --- |
| Statistical inference and temporal validation | [Real FX study](studies/fx-reference-momentum.md), [methods](docs/empirical-methods.md) | [Empirical pipeline](src/srl/fx_study.py), [resampling](src/srl/resampling.py) |
| Experimental design and overfitting control | [ORB selection-risk analysis](studies/opening-range.md#what-the-search-can-and-cannot-establish) | [Study protocol](experiments/ecb-fx-mom20-protocol.md), [boundary tests](tests/test_fx_study.py) |
| Market-data qualification | [MacroImpulse failure](studies/data-forensics.md) | [Schema and temporal checks](src/srl/fx_study.py) |
| Research-to-execution correctness | [DE30 risk repair](studies/de30-continuation.md) | [Semantic comparator](src/srl/validation.py) and [tests](tests/test_validation.py) |
| Provenance and sample governance | [Public Research OS](docs/research-os.md) | [Manifest/pack controls](src/srl/evidence.py), [mutation tests](tests/test_evidence.py) |
| Reviewable communication and disclosure | [Evidence register](docs/evidence.md), [ownership](docs/ownership.md) | [Claim ledger](data/claim-registry.json), [publication audit](scripts/audit_public.py) |

## Thirty minutes

Start with the [real-market study](studies/fx-reference-momentum.md): question → [frozen protocol](experiments/ecb-fx-mom20-protocol.md) → [source rights](DATA_LICENSE.md) → observations → code → inference → robustness → conclusion. Run the command below. Then contrast that full public replay with the private-history [provenance boundary](docs/provenance.md), follow a flagship claim through its source ID and [published aggregates](data/historical-results.json), and inspect [Research OS](docs/research-os.md) mutations that reject invalid evidence states.

The [research atlas](docs/research-atlas.md) retains the wider census and parked or incomplete hypotheses. The [synthetic calibration](docs/study.md) checks generic methods under a known process; it supplies no market-edge evidence.

## Rebuild and verify

Python 3.12 or 3.13 in a fresh virtual environment:

```sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps .
python scripts/reproduce.py --check
```

The command runs tests, disclosure/link/inventory and scientific claim checks, regenerates the historical presentations and replays the real FX study offline. CI verifies Linux and Windows. Historical TradingBotHQ backtests still require private licensed inputs and are not replayed. An optional new output directory records hashes:

```sh
python scripts/reproduce.py --check --output build/my-run
```

Code and original prose use [MIT](LICENSE). ECB observations have [separate provider terms](DATA_LICENSE.md). Private strategies, proprietary datasets, account records and production configurations remain private. [Security controls](docs/security.md), [limitations](docs/limitations.md) and the [long-term roadmap](docs/roadmap.md) state the remaining boundaries.
