> Independent AI review of the initial publication candidates; private storage paths have been redacted. Findings and their original conditional verdict are retained. See the [coordinator response](visual-v002-resolution.md) for subsequent fixes and verification. This is not independent human scientific peer review.

> SHA256 of the unredacted private report: `9c1f846b3077038ea5e822221d18e8fbed5b4b645b46443beedf31bf8e518a41`.

# Visual Research Portfolio v002 — quantitative research review

Date: 2026-11-11. Review mode: read-only quantitative and source-fidelity audit. This is a fresh AI review by an agent that did not implement the bundles; it is not independent human scientific peer review. Only this private report was written.

## Verdict

**Needs revision for one source-fidelity wording issue; otherwise share with the existing caveats within the reviewed quantitative scope.** No Critical finding or material numerical transcription error was found. Final integration, figure rendering, links and repository-wide tests are separate checks, not certified by this report.

## Critical findings

None observed in the reviewed scope.

## Important findings

1. **Retain the original post-selection status beside the EBP interval.** Location: `studies/engulfing-and-support.md:49–55` and `ebp/docs/ebp-visual-evidence.md:35–37`; corresponding integrated public paths have the same paragraphs. The original B23 archive's `EBP_H001_Q3_Phase2_Frozen_Analysis_Contract_20261011.md:3` explicitly calls this a **post-selection exploratory** analysis of already-opened development observations. The article says retrospective/spent, but emphasizes frozen/registered without preserving this exact selection boundary beside the reported 95% interval. Freezing the estimator after selection is not prospective confirmation. **Fix proposed:** add “post-selection exploratory” to the STAT001 caption/paragraph and evidence note, retaining the original estimate and bounds. State that this interval does not account for the full historical selection process. No new inference or bootstrap is required. Status: sent to integrating agent; pending verified final wording.

## Minor findings

1. **Distinguish a required placebo criterion from its achieved result.** Location: public `data/orb-ustec-public.json:1`, JSON pointer `/placebo_gate/both_median_deltas_positive`. This is currently `true`, although the achieved C1 paired median is −0.011284054701126844 R/trade and C2 is +0.011479265821862268. The article, chart and overall `result: NO` are correct; the Boolean appears to represent a requirement but is ambiguous to data consumers. **Fix proposed:** rename it to `requires_both_median_deltas_positive`, or explicitly separate requirement and observation. Status: integrating agent accepted; pending final-byte verification.

## Verification actually performed

All calculations below were independent ad hoc read-only Python/stdlib or DuckDB reads of the supplied projections and selected original evidence. The implementation render helpers were not used to obtain these reconciliations. Archive hashes establish retained-byte identity, not independently audited original feed acquisition or economic truth.

| Component | Original evidence and checks | Result |
| --- | --- | --- |
| ORB source custody | All 25 entries in private `orb/source-map.json`; recomputed SHA-256 from the original named files. Read original aggregation, selection, mechanism and 8B/8C/8D manifests and selection/mechanism/OOS reports. | All 25 hashes matched. Manifest commits, selection protocol identity, full CORE gates and final parity classification agree with publication. |
| USTEC Discovery surface | All 1,728 original `SURFACE_SUMMARY.csv` rows against public count/total/mean/PF values; all selection flags against `CELL_SELECTION_METRICS.parquet`. Checked medoid/max diagnostics against original `TAIL_CONCENTRATION_REPORT.json`. | Exact source fidelity within floating-point tolerance; null PF preserves source undefined PF. 140 positive, 22 robust and 18 selected-region cells remain distinct; medoid 545 trades/+29.871955R versus maximum 649/+120.367758R. Maximum's largest-absolute-trade removal gives −43.284416R, without deleting source outcomes. |
| USTEC paired controls | All 36 published paired rows against original mechanism Parquet; independently calculated actual mean minus control mean and median/favourable-cell counts. | C1 6/18, median −0.0112841; C2 9/18, median +0.0114793 R/trade. This is the median of paired cell differences, not a difference of medians or a trade-pair estimate. Specificity fails. |
| Separate USTEC OOS | Original 124 A trade rows and 53 B trade rows; independently grouped actual UTC exits by month, counted trades and summed cumulative price-space R. Read each original report. | All disclosed exit-month points/counts reconcile. A +26.412958685R/PASS and 14/18 region positive. B −0.576391963R/FAIL and 8/18 positive. B July burnoff appears; A primary finishes December while region January burnoff remains consumed. No pooling rescues B. |
| Modern gold surface | All 1,728 original `SURFACE_METRICS.csv` identities/classifications and all scored counts/totals/derived means. | 1,726 valid; two invalid; 30 valid zero-trade undefined means; 1,696 valid with trades; 17 positive, 1,679 negative. Invalid and zero-trade states are not conflated. This is the modern 1,728-cell UTC contract, not the older 1,152-cell surface. |
| Gold stress | All 60 disclosed rows against original `CANDIDATE_SCENARIO_METRICS.csv`, including counts, mean/total/PF, cost and latency. Original source additionally has 30 POOLED rows, deliberately not disclosed as a third validation block. | All values match. Separate Discovery/OOS CORE contract includes PF and drawdown as well as positive R. Normalized shocks remain separate from measured broker costs. |
| Gold money | Independently reaggregated all 1,376 original `MONETARY_PARITY.csv` rows into four candidate/period groups, checking count, synthetic flags, gross/commission/swap/fees/net. Read deployment feasibility and manifest. | Counts 505/206/453/212, six synthetic exits, correct financing sign flips. A Discovery $1,590.72−$1,973.73=−$383.01; C $1,977.72−$2,631.86=−$654.14. All 22 feasibility rows fail. Accounting population differs from stress populations and remains expressly scoped. |
| Gold terminal | Recomputed actual original spent terminal ZIP hash `7844242f737201c277617c00c15fd2f2d841761d8abb308896cc3199f7deb314`; read its original `SUMMARY.csv`. | A 53 trades, PF 0.68, valid/economically negative; C 51, PF 1.00 rounded, valid/economically flat. No rounding-to-exact-breakeven inference. |
| EBP custody | Recomputed all three original archive hashes and all 109 selected member hashes (93 TF001R2, nine H002, seven STAT001). | All match. Original Git identity gaps and untracked implementation caveat are preserved; public source/member hashes bind actual bytes. |
| EBP native matrix | Reaggregated every original archived `trades.csv` for all 88 cells using Decimal `r_result` sums, original row counts and means; compared each public row. | All 88 match; total 152,753 closed observations and 25 positive cells. Shared instrument/dates are overlapping studies, not a capital-synchronized portfolio. Price-R data limitations are explicitly retained in evidence note/JSON. |
| EBP H002 | All four arms against original `H002_MATRIX_SUMMARY.csv`; read original pending/BE contract descriptions and archive bindings. | Counts 3/1,257/3/1,297 and return aggregates match, all PARK. Two three-trade arms are inadequate exposure, not winners. Different pending/BE policies remain separate contracts; conceptual A/B/C lifecycle carries no fabricated history. |
| EBP STAT001 | All twelve original stratum rows; equal-stratum mean independently recomputed; compared archived bootstrap summary bounds and original analysis/frozen contract. | −0.2717839056R and [−0.330415012574377,−0.21279312685784468] match. No bootstrap rerun. Fill conditioning, excluded gold, no subgroup intervals and heterogeneous association retained. Explicit post-selection wording requested above. |
| Macro custody | Recomputed four original archive hashes and all 16 selected member hashes; sequential canonical snapshot SHA-256 independently checked. | All match. Sequential remains canonical-text AS_REPORTED, not newly reconstructed original group evidence. No raw-calendar/trade publication. |
| Macro baseline/filter | All ten original baseline cells and five original paired filter aggregates against projections, plus original validation readout. | Baseline 1,396/$4,250.48; separate 2021–22 control $2,741.19 versus treatment $2,733.57, delta −$7.62; 700/697 trades; three profitable removals; double-trigger totals unchanged. REJECT/no retuning retained. |
| Macro cost study | Every disclosed original year/pair aggregate and nominal cost total against archived CSVs; read original commission model and adjudication. | 638 five-pair versus 563 four-pair trades; $589.46 versus $639.68 adjusted totals; four-pair 2021 −$16.29. $3.50/actual lot/side; DOCUMENTATION_ONLY, no same-account empirical validation. PARK, not hypothesis rejection. |
| Macro calendar | All 78 original monthly rows, with each impact/all count compared; independently summed the period totals. | 16,288 earlier/760 later MEDIUM rows. Earlier strategy-input scope 16,059 is retained unreconciled; 229 difference not guessed away. Rate 15.6% describes source density rather than real-world missing-event proportion. INVALID_DATA_UNIVERSE supersedes clean strategy failure. |

## Methods and interpretation

The three cases preserve distinct hypotheses, contracts, sample fences and decisions. ORB discloses outcome-selected correlated cells, medoid selection does not remove the search, placebo comparisons are posthoc Discovery, and separate failed validation is not pooled away. The hypothetical Bonferroni illustration is arithmetic rather than a manufactured adjusted inference; PBO, deflated Sharpe and adjusted p-values remain unestimated. Gold price-space stress, tester money and spent terminal monetary PF retain different accounting bases.

EBP native-clock repair, H002 policy arms and STAT001 association are not replications of a single executable strategy. The source interval conditions on fixed selected histories, frozen quartiles and fills; it is not a causal intervention, selection-adjusted significance result, independently validated joint cross-instrument inference or reverse-strategy expectancy. The primary source explicitly calls it exploratory. Macro's positive baseline does not qualify its interventions; the cost and calendar stages preserve their separate samples and revised decisions.

## Limitations

This is an aggregate/source-fidelity review, not an independent rerun or certification of private engines, historical broker specifications, session completeness, monetary conversion, actual execution or live investability. No strategy, optimization, new bootstrap, holdout, MT5 action or sealed-evidence opening was performed. Archived already-opened rows were read only for authorized reconciliation; no private original rows were copied into the public bundle.

No TradingBotHQ checkout was opened for this review: original runtime files and retained archives supplied the evidence, so no historical dirty worktree was resumed or changed. Current public Git root/origin/branch/HEAD/status were inspected; this is the unrelated `vda93/systematic-research-lab` repository. The private current-source freshness assertion in another agent's map is not independently certified here.

Source acquisition/custody before the retained manifests, complete search/access chronology, original protocol file bytes beyond manifest identities, and every pre-existing nonvisual article claim were not exhaustively re-audited. Original 8D-R1 decomposition/portability tables and Macro sequential group decomposition remain unavailable for independent reconstruction and correctly blocked/qualified. Pixel rendering and narrow-screen readability are outside this numerical review. The default reviewer Python lacks Matplotlib; no render or repository test-suite pass is claimed by this reviewer. Separate integration checks must verify current output bytes after fixes.

## Reviewed artifact identities

Snapshot is of the ORB public worktree plus completed EBP/Macro handoff bundles, before the integrating agent's response to the findings. The worktree moved between implementation branches during authorized integration; initial ORB branch was `codex/visual-orb-v002`; last observed branch was `codex/visual-ebp-v002`, HEAD `caa9351767063e08d80bd3cb739da5c85220dd56`. Diff was reviewed against fetched public baseline `af4b28dc7a43e152ad8460f0e65ea9f0f3ba5512`. Later bytes require the narrow final verification addendum below.

| Reviewed file | SHA-256 |
| --- | --- |
| [publication checkout]\data\orb-ustec-public.json | `b9bce7f4518b11349a009da31ed8e3ed404ff0a9d3761fbef398a918372eb3ef` |
| [publication checkout]\data\orb-gold-public.json | `0b42748f2952d8fc9d1d09987382669094b2df54ae60630c1ab95f34ab8b360b` |
| [publication checkout]\scripts\render_orb.py | `cff62f2c8d2a435f2903880a6515543bb7cbdd508e7b09cde0c23577ba4120cb` |
| [publication checkout]\studies\opening-range.md | `235d8f77458fe3fcf32fadfbca2cdeec24145f971c5234bfd84902276a0880a1` |
| [publication checkout]\docs\orb-visual-evidence.md | `1848a5c906da239bf5d62e1c7ba7cc05c7b36e40d8ff94e999fb37867bd00705` |
| data\ebp-public.json | `b57de61f3f038d88cd703742c13149575f305e9fd317f88d370e506b4f2f589a` |
| scripts\render_ebp.py | `3ca05179e71ca5aca63785d0eb9f3447817ef200cd558f0e6dc74d880f76c2a0` |
| studies\engulfing-and-support.md | `4c84c8e4768f4163c43308310e6545d8b9eaf3a59713e9e913242c24f16fe06c` |
| docs\ebp-visual-evidence.md | `962c87dacd5c0e6d3050028e6745fd51b0b5d94a25bed3779c4996ad9c1f5e3a` |
| data\macro-public.json | `de62b96ce2c66965125051e3020fc3cb1b00668dbfe38297374bba8aef941c97` |
| scripts\render_macro.py | `82e99c46c769f7be5491e1cc2a4b259551ee70cdbd5bf1175c1ad95d0ad56c63` |
| studies\news-research.md | `0ccccc7ce86361642222504706e8b03f22f84848a586150a5c5c14012f4d6469` |
| docs\macro-visual-evidence.md | `5fc646560b2b5b8b2ec6c76b6804c0a85150312a243e62b23e937568a877c2c9` |
