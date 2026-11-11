# EBP visual evidence and reproduction boundary

[Case study](../studies/engulfing-and-support.md) · [Public aggregate extract](../data/ebp-public.json) · [Renderer](../scripts/render_ebp.py)

These figures present completed historical evidence. The public command rebuilds SVGs from disclosed aggregates; it does not rerun the private strategy, recover broker fills or reproduce a market-data backtest. The three experiments retain separate implementations, sample roles and decisions. Derived aggregate publication was authorized for this portfolio update; raw market data, trade records, private strategy code and sensitive locations remain excluded.

| Figure | Status | Exact experiment / source binding | What it supports |
| --- | --- | --- | --- |
| [Native-timeframe surface](../figures/ebp-native-timeframe.svg) | **APPROVED AS REPORTED** | `EBP-MT5-TF001R2-M15PLUS`, run `EBP_TF001R2_M15PLUS_20261007_100046`; B22 | All 88 native-clock cell means, 152,753 trades, 25 positive cells. Spent Discovery, not a synchronized portfolio or selection-adjusted validation. |
| [Full cell distribution and support](../figures/ebp-cell-distribution.svg) | **APPROVED AS REPORTED** | Same 88 original TF001R2 cells and source-member bindings as the native surface; B22 | Equal-cell histogram and mean-versus-completed-trades scatter. All cells retained; shared dates/instruments mean correlated observations. |
| [Pending-policy comparison](../figures/ebp-order-policy.svg) | **APPROVED AS REPORTED** | `EBP-PY-H002`, original review run `EBP_PY_H002_AMBIGUITY_MATRIX_20261004T193844Z`; B21 | Four exact pending-policy × break-even contracts; exposure sensitivity and PARK decisions. No winning interpretation selected. |
| [Small-candle observation](../figures/ebp-small-candle.svg) | **APPROVED AS REPORTED** | `EBP-M15-REV-H001-Q3-STAT001`, run `EBP_M15_REV_H001_Q3_STAT001_20261011_213401`; B23 | Twelve original symbol-year contrasts and the registered aggregate month-block interval. Association on spent Discovery; no causal intervention or inverse-profit result. |
| [Pending lifecycle](../figures/ebp-pending-lifecycle.svg) | **SCHEMATIC ONLY** / `CONCEPTUAL_SCHEMATIC` | H002 pending-policy contracts in the same original preregistration; B21 | Fictional A/B/C order-state example, with no prices, timestamps, returns or historical trade paths. GTC occupancy versus eligible cancel-and-replace. |

The lifecycle drawing is explicitly fictional. It assumes pending orders remain unfilled and replacement eligibility holds. A live position without `BE_APPLIED` blocks replacement. Both policies have no time expiry. The rows are conceptual examples, not contemporaneous historical counterfactual sequences; the empirical H002 arms were separate engine contracts. None of the approved statuses means independent broker certification, fresh OOS evidence or live authorization.

## Original-byte custody

The source keys in [ebp-public.json](../data/ebp-public.json) record safe archive basenames, original run identities, byte sizes and SHA-256 digests. Archive-internal member names are relative custody identifiers, not public downloads. The publication pass recomputed hashes from actual bytes and CRC-checked each original ZIP. The selected STAT001 aggregate and contract files were also byte-matched between the local completed package and the original review archive.

| Source | Original archive basename | Verified SHA-256 |
| --- | --- | --- |
| B22 | `EBP_TF001R2_M15PLUS_20261007_100046_REVIEW.zip` | `45849b254cb4b7e07fffe719dfa3e718371c4bbc44472b4209365f2c56d9fc9d` |
| B21 | `EBP_PY_H002_AMBIGUITY_MATRIX_20261004T193844Z_REVIEW.zip` | `99558ddcc5f308c319dacb1472c2ec5cef1501a79eaa7deac38b47fe7da2388b` |
| B23 | `EBP_M15_REV_H001_Q3_STAT001_20261011_213401_REVIEW.zip` | `1e52bf69309b678ca49f8df88ea8d78394cb2a0f947f28dd7df550669c8534c3` |

**TF001R2.** The 88 rows were derived directly from the 88 original archived `cells/<cell_id>/trades.csv` members. Each public row binds to its original member SHA-256. Counts are CSV data-row counts; total R is a decimal sum of the original four-decimal `r_result` field; mean R divides that sum by the count. The figure rounds means to three decimals, while the extract retains numerical precision. No cell was reconstructed from narrative totals or the older invalid timeframe surface. The additional distribution figure uses every one of these same 88 means, with fixed 0.05R histogram bins from −0.45 to +0.15R and one observation per cell. Its scatter pairs each mean with that cell's completed-trade count (193–12,143). Neither view weights the 88 cells by trade count. Instruments and dates overlap, so these are correlated cells, not 88 independent experiments or confidence intervals. `COMBINED_VALIDITY_SUMMARY.csv` verifies all 88 `PASS_NATIVE_TF` statuses and signal-clock checks. `R2_FREEZE.txt` and the original source, binary and baseline-set hashes identify the implementation; an exact original Git commit is not established by that freeze.

The run covers 2020-01-30 inclusive to 2024-01-01 exclusive, eleven instruments and M15/H1/H2/H3/H4/H6/H8/H12. M1, M5 and D1 are absent. These are overlapping backtests, so counts and pooled means are descriptive. Fixed 0.01-lot MT5 Model-4 outcomes are price-derived R, with no established net account-risk, commission or financing qualification. The prior audit identified 74 nonpositive initial-risk denominators assigned zero R, 7,790 exact-zero outcomes and defective `moved_to_be` telemetry. These limitations remain attached to the figure.

**H002.** `H002_MATRIX_SUMMARY.csv`, all four `summary.json` members, `H002_FREEZE_MANIFEST.json`, `EBP_H002_PREREGISTRATION.md` and `EBP_H002_EXECUTION_CORRECTIONS.md` bind the counts and contracts. The archive records original Git HEAD `d2501b8765ad6711381ab692cc4be12e6cdb9d82`, with the research implementation then untracked; the commit alone does not identify those bytes. The original archive and its member hashes govern this publication. This is a separate source-faithful Python interpretation on XAUUSD2 H4, 2020-01-01 inclusive to 2026-08-01 exclusive, with UTC Bid candles and executable Bid/Ask sides. Commission, financing and account-risk economics remain unqualified.

GTC blocks later signals behind one pending order. Replacement first checks active-position eligibility: a position without applied break-even blocks replacement; otherwise the earlier pending order is superseded by the new signal. Both have no time expiry. Break-even confirmation uses either a fully post-entry completed H4 candle or a later intrabar Bid tick exceeding the signal extreme. All four arms share executable stop-gap fills, arm-until-placeable break-even and deterministic target-level exits. Their results cannot be pooled with the native MT5 matrix as repeated confirmation.

**STAT001.** `PRIMARY_12_STRATA.csv`, `STAT001_RESULTS_MANIFEST.json`, `BOOTSTRAP_SUMMARY.json`, `STAT001_ANALYSIS_PLAN.json` and the frozen Phase-2 contract supply the observation and uncertainty. All placed opportunities in each symbol-year are ranked by engulf range divided by causal ATR. Filled Q1 mean original R minus filled Q4 mean is calculated in each of twelve strata, then averaged equally. The primary estimate is **−0.2717839056 price R**. Its reported **post-selection exploratory 95% percentile interval [−0.3304150126, −0.2127931269]** comes from 20,000 valid signal-calendar-month block-bootstrap replicates within each stratum, retaining frozen quartile assignments. This interval is **not selection-adjusted**. The estimator and bootstrap were frozen after strategy/domain selection on spent Discovery; that freeze does not adjust uncertainty for selection. The portfolio renderer displays these archived bounds; it does not rerun the bootstrap. Symbol/year intervals were not supplied and are not drawn.

The observational scope is JP225X, USDCAD2 and DE30X M15, 2020-01-30 inclusive to 2024-01-01 exclusive, with 28,097 placed opportunities and 21,917 fills. All 868 zero-R outcomes and 22 invalid actual-fill-risk rows are retained. XAUUSD2 was excluded for unresolved at-test history identity. Conditioning on fills and the heterogeneous DE30 contrast limit interpretation; this is neither causal identification nor a new OOS significance test.

## Blocked extensions and exact handoff

| Proposed display or claim | Status | Missing evidence required before making it |
| --- | --- | --- |
| Broker-qualified net expectancy or deployment-ready timeframe winner | **BLOCKED** | An independently qualified historical broker/session and contract specification, commissions/financing and account-risk monetary reconciliation for the exact run, followed by a separately authorized validation design. `R2_FREEZE.txt` and price-R telemetry do not supply this. |
| Per-symbol or per-year confidence intervals | **BLOCKED** | Original registered subgroup interval outputs with their resampling contract, sample definition and immutable hashes. The single aggregate `BOOTSTRAP_SUMMARY.json` cannot be reused as subgroup uncertainty. |
| Causal benefit from wider stops or profitable reverse trading | **BLOCKED** | A separately frozen and authorized stop intervention or executable opposite-direction experiment, with side-specific fills, costs, later-period role and complete decision evidence. STAT001 contains no such outcome. |
| Independent broker-acceptance reconstruction from quote geometry | **BLOCKED** | Independent historical trading-session rules and broker constraints covering the exact rejection/retry timestamps. Oracle-assisted event tapes are diagnostics, not independent parity. |

No new test, holdout opening, optimization, MT5 action or data publication was performed to fill these gaps.

## Public reproduction

In the repository's pinned Python environment:

```text
python scripts/render_ebp.py
python scripts/render_ebp.py --check
python -m unittest discover -s tests -p "test_ebp_figures.py" -v
```

The renderer uses Matplotlib and NumPy, fixes its SVG identifier salt and omits timestamps. The five retained outputs (four empirical figures and one conceptual schematic) are vector SVGs with accessible title/description text and no embedded raster. Tests check the complete native grid, original closeout reconciliation points, exposure contracts, registered interval arithmetic, source-member bindings, deterministic bytes and rejection of incomplete inputs. Review regressions additionally verify policy-arm order invariance, reject duplicate/missing identities or mismatched pending/BE contracts, reject inconsistent native mean/total/count and timeframe summaries, and verify that numeric figure annotations follow internally consistent source changes. Source-mutation checks verify that changing one cell's trade count moves its support point and changing one mean across bins alters histogram geometry. The lifecycle fails closed when either frozen pending-policy contract is missing. These are aggregate publication checks, not a public replay of the private backtests.
