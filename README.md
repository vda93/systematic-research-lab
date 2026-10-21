# TradingBotHQ · Systematic Research Lab

I direct TradingBotHQ, a systematic-trading research project. This portfolio contains historical experiments, a publicly reproducible market-data study and tested research software. Analysis, engineering and writing use AI assistance; the [contribution map](docs/ownership.md) separates documented decisions from implementation and unresolved personal-authorship claims.

## Thirty seconds

- **Research:** Why did momentum rules weaken on finer bars? The [MOMCONT sequence](studies/momentum-continuation.md#how-the-earlier-question-developed) tests competing clock-window and volatility-scaling explanations, including a rejected initial explanation.
- **Engineering:** An [exact circular-block sampler](docs/exact-block-means.md) links mathematics, source, independent arithmetic oracles and measured speed/memory tradeoffs. You can inspect the implementation and reproduce the benchmark.
- **A decision that survived disappointment:** [NOWICK](studies/nowick.md) was shelved; failed continuation did not justify a reversal strategy. The separate reversal study also failed its gate.

Historical case studies reconstruct published aggregates from retained primary records. The [ECB FX study](studies/fx-reference-momentum.md) additionally replays real reference-rate observations from a permitted public snapshot. Its negative finding remains intact; reference marks do not establish executable fills or net trading returns. [Evidence and limitations](docs/evidence.md) distinguish these verification levels.

The [BBO execution-delay study](studies/bbo-execution-delay.md) compares actual displayed bid/ask costs. Its separately frozen amendment now has twelve development days and 2,421 paired shock observations: a descriptive mean saving of −0.41005 bps, with failed coverage, missing-target and depth support. The separate twelve-day validation sample contains 2,665 pairs and a descriptive mean of −0.17343 bps, also with failed support. Final results remain pending; no fills or trading profits are claimed.

## Five minutes

| Read | Inspect | What to challenge |
| --- | --- | --- |
| [MOMCONT mechanism development](studies/momentum-continuation.md) | Competing explanations, factorial correction and later exit decisions | Confounding, non-nested paths and already-seen samples |
| [BBO quote-cost development](studies/bbo-execution-delay.md) | [Checked aggregates](data/bbo-development-results.json), causal replay and order-side accounting | Missing quotes, displayed depth, conditional estimates and failed support |
| [Exact block means walkthrough](docs/exact-block-means.md) | [Implementation](src/srl/block_means.py), [independent oracles](tests/test_block_means.py), [measurements](data/block-means-benchmark.json) | Numerical precision, RNG equivalence, complexity and memory cost |
| [NOWICK rejection](studies/nowick.md) | Matched controls and the separate reversal test | Why a failed hypothesis does not imply its opposite works |

For other historical decisions: [DE30 concentration and sizing](studies/de30-continuation.md), [ORB selection and validation](studies/opening-range.md), [calendar-data failure](studies/data-forensics.md). The [research atlas](docs/research-atlas.md) includes parked and incomplete hypotheses. Historical R is normalized initial planned trade risk, not an account-return percentage.

## Thirty minutes

Follow one complete public empirical chain: [question](studies/fx-reference-momentum.md) → [frozen protocol](experiments/ecb-fx-mom20-protocol.md) → [data rights](DATA_LICENSE.md) → [method](docs/empirical-methods.md) → [implementation](src/srl/fx_study.py) → [robustness and decision](studies/fx-reference-momentum.md). Its inference is reproducible; its prices cannot support an executable trading claim.

Then follow the engineering chain: [sampling contract and derivation](docs/exact-block-means.md) → [integer-prefix implementation](src/srl/block_means.py) → [Fraction/Decimal and adversarial tests](tests/test_block_means.py) → [benchmark script](scripts/benchmark_block_means.py). The [Research OS](docs/research-os.md) adds evidence-state and disclosure controls; those controls cannot authenticate private scientific findings.

## Rebuild and verify

Python 3.12 or 3.13 in a fresh virtual environment:

```sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps .
python scripts/reproduce.py --check
python scripts/benchmark_block_means.py --repeats 5 --repetitions 2048
```

Reproduction runs tests, disclosure/link/inventory checks, claim checks and exact artifact comparisons. CI covers Linux and Windows. Benchmark timings vary by machine and are separate from deterministic scientific outputs. Private historical backtests require licensed inputs and are not rerun here; see the [provenance boundary](docs/provenance.md). The [synthetic calibration](docs/study.md) tests methods under a known process and supplies no market-edge evidence.

Code and original prose use [MIT](LICENSE); ECB observations have [separate terms](DATA_LICENSE.md). [Security](docs/security.md), [limitations](docs/limitations.md) and the [roadmap](docs/roadmap.md) record remaining boundaries.
