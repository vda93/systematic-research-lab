# MacroImpulse visual evidence review

These figures reconstruct retained historical aggregates. They do not execute a strategy, open a new sample, repair the calendar, validate live costs or change a scientific decision. Monetary amounts are source research-account USD, not account returns or risk-normalized R. Publication permission covers these aggregate transcriptions; original private calendars, trade rows, ticks, binaries and source locations are excluded.

The [public extract](../data/macro-public.json) records SHA-256 identities of original archive bytes and the selected original members. Basenames identify evidence artifacts without disclosing private storage locations. Archive SHA-256 identifies the complete retained ZIP; member SHA-256 identifies the exact original CSV/JSON bytes used for transcription. A canonical decision text snapshot is identified separately and is never described as original trade-level evidence. Public figure reproduction starts from the aggregate JSON, so it can verify the rendering and arithmetic but cannot independently replay the private research.

| Figure | Publication status | Source and supported comparison | Limits and decision |
| --- | --- | --- | --- |
| [Baseline](../figures/macro-baseline.svg) | APPROVED AS REPORTED | `MACRO-BASELINE`: original `BASELINE_CELL_SUMMARY.csv`, ten FX pair-year cells, 2023–2024 historical bridge; 1,396 trades, +$4,250.48 spread-only, aggregate PF 3.6889. | Commission excluded. No historical live-net claim or independent uncertainty estimate. Baseline remains the scientific control. |
| [Spread filter](../figures/macro-spread-filter.svg) | APPROVED AS REPORTED | `MACRO-SPREAD`: original `PAIR_AGGREGATE_2021_2022.csv` and `VALIDATION_DECISION_READOUT.json`, already-opened frozen validation. +$2,741.19 control versus +$2,733.57 treatment. | Separate sample from the bridge. Three completed trades removed, all profitable; double-trigger aggregate unchanged. REJECT, no retuning. |
| [Sequential reversals](../figures/macro-sequential.svg) | APPROVED AS REPORTED | `MACRO-SEQUENTIAL`: freshly archived canonical decision text, 2021–2024 EventPath development. 139 groups / 278 positions; −$287.99 first leg, +$188.22 reversal, −$99.77 combined. | Original group-level decomposition was not recovered here. Reported canonical aggregates only. Dependent components of the same groups, not independent equity paths. Blanket suppression rejected. |
| [Commission and stability](../figures/macro-costs.svg) | APPROVED AS REPORTED | `MACRO-COST`: original `SUMMARY_BY_YEAR.csv`, `SUMMARY_BY_PAIR.csv`, `COST_SENSITIVITY.csv` and adjudication. Clean medium-only 2021–2024 discovery, five-pair n=638 and four-pair n=563. | USD 3.50 per actual lot per side on entry and exit. DOCUMENTATION_ONLY qualification, no same-account deal export. Four-pair adjusted 2021 −$16.29; failed annual gate, PARK. |
| [Calendar coverage](../figures/macro-calendar.svg) | APPROVED AS REPORTED | `MACRO-CALENDAR`: original `COUNTS_BY_MONTH_IMPACT.csv` and forensic period table. Calendar audit January 2020–June 2026: 16,288 MEDIUM rows / 60 earlier months; 760 / 18 later months. | Recorded source density, not real-world event completeness. Earlier strategy-input scope sums to 16,059 and remains unreconciled. INVALID_DATA_UNIVERSE supersedes the provisional clean failure. |
| [Order mechanics](../figures/macro-mechanics.svg) | SCHEMATIC ONLY | `MACRO-MECHANICS`: original frozen `BEHAVIORAL_SPEC.md`, EXP-MACROIMPULSE-001. Ask-based buy-stop / Bid-based sell-stop entry, spread-aware geometry, protective/trailing exits and scheduled pending deletion. The canonical sequential record supports the possibility of a later opposite trigger. | Fictional state example; generic two-sided event-order schematic. Exact contracts vary. No price path, empirical sample, numerical example price, observed latency or fill probability. Arrows depict optional state transitions, not measured market history. |
| Broker-net equity, new holdout result, group-level uncertainty or a repaired-calendar backtest | BLOCKED | Required inputs are not qualified by this publication bundle. | Do not infer these from existing totals or generate synthetic paths, error bars or trades. |

“APPROVED AS REPORTED” means suitable for this authorized aggregate publication with the stated source limits. It does not mean independently verified raw-market replication, research promotion or deployment approval. The original program remains shelved. The baseline/filter/medium/forensic samples are not pooled.

The cost and calendar rows above are historical source records outside the featured MacroImpulse article. My practical reason for shelving the program was the execution I saw across brokers. [Closeout clarification](provenance.md#macroimpulse-closeout-clarification)

## Exact missing-artifact handoff

1. **Sequential decomposition:** recover the original reviewed 2021–2024 139-group summary with a manifest tying group count, ordered first/reversal leg status and aggregate spread-only P&L to the EventPath run. A public replacement needs only group/leg aggregate totals and the original artifact hash. Position IDs, event-level rows and timestamps remain private. Until then, the canonical decision snapshot governs the reported figure.
2. **Commission validation:** a same-account Exness Raw Spread deal export, matched to the existing entry/exit volumes and commission currency, is needed for empirical historical cost validation. The model and its documented rate do not supply those observations. No export is included or requested for public release.
3. **Calendar scope reconciliation:** recover the original extraction contracts behind the 3,246-row 2020 strategy-input count and 12,813-row 2021–2024 count, then reconcile those filters against the forensic `COUNTS_BY_YEAR_IMPACT.csv` (2020 = 3,475; 2021–2024 = 12,813). The observed 229-row difference is concentrated in the reported 2020 totals; its cause remains unknown. No scope correction is guessed.
4. **Calendar repair and valid economic evaluation:** an independently qualified post-break event universe, exact original candidate/cost identities and separately authorized unchanged-candidate evaluation would be needed. This publication does not acquire data, rerun a backtest or grant that authorization. Vendor HIGH-impact trading minutes cannot validate MEDIUM completeness.

## Rebuild and checks

Run from the public repository root with its pinned Matplotlib/NumPy environment:

```powershell
python scripts/render_macro.py
python scripts/render_macro.py --check
python -m unittest discover -s tests -p test_macro_figures.py -v
```

The renderer has no dependency on private locations or on another study renderer. SVG dates are omitted, IDs use a fixed salt and text remains accessible SVG text. Each original SVG includes a title and description. The table above links directly to those files.

Before rendering, validation rejects duplicate or missing baseline identities, nonfinite numbers and inconsistent cell/summary accounting. It also checks filter pair identities/deltas, dependent reversal totals, medium annual/pair/aggregate accounting, and 78 unique consecutive calendar months with consistent impact counts and forensic rates. Fixed scientific verdicts are explicit contracts: a replacement dataset that contradicts them fails closed rather than inheriting their captions. Quantitative annotations derive from validated disclosed data. The focused tests include consistent source mutations that update both marks and labels, contradictory mutations that raise `ValueError`, source identities, private-location exclusions and byte-for-byte figure determinism. No historical source value, new confidence interval or equity curve is calculated or changed by this publication repair.
