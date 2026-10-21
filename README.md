# TradingBotHQ · Systematic Research Lab

I direct TradingBotHQ, a systematic-trading research project. This portfolio contains historical experiments, a publicly reproducible market-data study and tested research software. Analysis, engineering and writing use AI assistance; the [contribution map](docs/ownership.md) separates documented decisions from implementation and unresolved personal-authorship claims.

## Thirty seconds

- **Research:** Does waiting through a spread shock lower quoted crossing costs? The [BBO study](studies/bbo-execution-delay.md) follows a frozen question through real bid/ask replay and a final support failure. The historical [MOMCONT sequence](studies/momentum-continuation.md#how-the-earlier-question-developed) shows how competing mechanism explanations developed.
- **Engineering:** An [exact circular-block sampler](docs/exact-block-means.md) links mathematics, source, independent arithmetic oracles and measured speed/memory tradeoffs. You can inspect the implementation and reproduce the benchmark.
- **A decision that survived disappointment:** [NOWICK](studies/nowick.md) was shelved; failed continuation did not justify a reversal strategy. The separate reversal study also failed its gate.

Historical case studies reconstruct published aggregates from retained primary records. The [ECB FX study](studies/fx-reference-momentum.md) additionally replays real reference-rate observations from a permitted public snapshot. Its negative finding remains intact; reference marks do not establish executable fills or net trading returns. [Evidence and limitations](docs/evidence.md) distinguish these verification levels.

The [BBO execution-delay study](studies/bbo-execution-delay.md) compares actual displayed bid/ask costs under separately frozen sample stages. The final sample contains 572 paired shocks and a descriptive mean saving of −0.22962 bps, with **failed support**. Development and validation remain separately reported. Raw inputs require independent retrieval under provider terms; no fills or trading profits are claimed.

## Five minutes

| Read | Inspect | What to challenge |
| --- | --- | --- |
| [MOMCONT mechanism development](studies/momentum-continuation.md) | Competing explanations, factorial correction and later exit decisions | Confounding, non-nested paths and already-seen samples |
| [BBO quote-cost research](studies/bbo-execution-delay.md) | [Final aggregate](data/bbo-final-results.json), causal replay and order-side accounting | Missing quotes, displayed depth, conditional estimates and failed support |
| [Exact block means walkthrough](docs/exact-block-means.md) | [Implementation](src/srl/block_means.py), [independent oracles](tests/test_block_means.py), [measurements](data/block-means-benchmark.json) | Numerical precision, RNG equivalence, complexity and memory cost |
| [NOWICK rejection](studies/nowick.md) | Matched controls and the separate reversal test | Why a failed hypothesis does not imply its opposite works |

For other historical decisions: [DE30 concentration and sizing](studies/de30-continuation.md), [ORB selection and validation](studies/opening-range.md), [calendar-data failure](studies/data-forensics.md). The [research atlas](docs/research-atlas.md) includes parked and incomplete hypotheses. Historical R is normalized initial planned trade risk, not an account-return percentage.

## Thirty minutes

Follow the quote-cost chain: [question and decision](studies/bbo-execution-delay.md) → [original protocol and measurement failure](experiments/bbo-delay-protocol.md) → [separately frozen amendment](experiments/bbo-delay-measurement-v2.md) → [source rights](data/BBO_DATA_NOTICE.md) → [median bounds](src/srl/bbo_history.py) and [side/fee accounting](src/srl/bbo_accounting.py) → [causal replay](src/srl/bbo_replay.py) → [all final sensitivities and support](data/bbo-final-results.json) → [private-input reproduction](studies/bbo-execution-delay.md#final-sample-support-fails). The original failure is retained; the amendment changes the observable population and is not pristine retrospective preregistration.

For a real-data study with inputs bundled under separate terms, follow the [ECB protocol, method and failed benchmark comparison](studies/fx-reference-momentum.md). Its reference prices cannot establish executable trading returns.

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
