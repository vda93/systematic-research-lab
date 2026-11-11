# Visual portfolio review response and verification

[Quantitative review](visual-v002-quantitative.md) · [Visual review](visual-v002-visual.md) · [Engineering review](visual-v002-engineering.md) · [Verification receipt](../../results/visual-v002-verification.json)

Three fresh AI reviewers examined the initial publication candidates independently of their implementation. Their original conditional verdicts remain in the linked reports, with private custody paths redacted and original report hashes retained. This coordinator response records subsequent corrections; it does not turn the reviewers into independent human scientific peers or imply that they re-reviewed every fix.

## Responses

| Finding | Response and verification |
| --- | --- |
| Quantitative: post-selection status beside the EBP interval | Added “post-selection exploratory” and the absence of selection adjustment to the article, public metadata, evidence note, SVG subtitle and interval annotation. Original estimates and bounds unchanged. |
| Quantitative: ambiguous placebo Boolean | Renamed the requirement to `requires_both_median_deltas_positive`. The achieved specificity decision remains `NO`; original comparison rows unchanged. |
| Engineering I1: Macro ambiguous inputs and stale annotation values | Added identity, finite-value, chronology and accounting validation. Duplicate/missing/contradictory inputs fail closed. Consistent mutations alter both marks and corresponding labels/rates. |
| Engineering I2: EBP positional policy labels | Policy arms are validated by unique canonical identity and their pending/break-even contracts. Reordered arms produce identical output; missing, duplicate or mismatched contracts fail. Native means, totals, counts and timeframe summaries reconcile; annotations derive from validated cells. |
| Engineering I3: ORB stale annotations and curve inconsistency | Qualification/validity counts and concentration labels follow disclosed inputs. OOS month counts, chronology, totals and cumulative endpoints must reconcile. Changed geometry and contradictory-input rejection are tested separately. |
| Visual V1: Macro figure access | Added explicit full-resolution links after every figure caption. |
| Visual V2: standalone accessible descriptions | Added native SVG title/description and linked image semantics to the new ORB and Macro outputs. Existing ORBINDEX output bytes remain unchanged. Screen-reader operation was not directly tested. |
| Visual V3: sparse EBP marker clipping | Endpoint markers may extend beyond the clipping box while preserving the zero-based count axis and exact labels. |
| Visual V4: dense conceptual layout at phone width | Deferred compact stacked redesign. The adjacent prose gives the mechanism and each figure offers a full-resolution link; dense labels still require zoom. This is a presentation limit, not missing or fabricated historical evidence. |

Review regressions were observed failing before implementation, then passed. The original implementers and coordinator inspected the affected full-size and narrow renders after repair. The independent visual review inspected all 19 initial figures at width 390. The coordinator additionally authenticated the source archive/member and inspected the later symbolic Macro mechanics figure; its states are explicitly fictional, with no historical price path or measured timing.

## Final local gates

The integrated code passed 127 tests on Windows / Python 3.12.10, with one skipped symlink test because the OS denied symlink creation. Library statement/branch coverage was 92.00%, above the existing 90% gate. Ruff, mypy, dependency compatibility, deterministic regeneration, claim/source bindings and exact release inventory passed. The final documentation-only packaging was checked again for claims, inventory, relative links and sensitive content. CI supplies the separate supported-platform checks for the exact pushed heads.

Gitleaks 8.30.1 found no leaks in the inspected complete public history or working tree, and the pinned dependency advisory audit found no known vulnerabilities. Those results do not establish raw-data redistribution rights or undisclosed-vulnerability absence. Hosted CodeQL and security job outcomes are checked separately on the PRs.

Hosted Linux reproduced an EBP diamond-marker signed-zero difference that changed SVG identifiers. Explicit axis vertices replaced trigonometric rotation; a regression emulates the observed last-bit variation. Source estimates, interval bounds and mark positions remain unchanged. The affected files were regenerated and the complete suite rerun.

The identity audit caught local integration merges created with the checkout's default email. Their superseded branch and PR were preserved outside the active publication ancestry. A new Macro branch starts from the corrected EBP branch and reuses the original publication commit with the approved public author/committer identity. No history was rewritten and no force-push occurred. The active ancestry passed the original identity audit without relaxing its rules.

There are 20 new figures: 18 EMPIRICAL_REPORTED displays and two CONCEPTUAL_SCHEMATIC diagrams. Every empirical display is APPROVED AS REPORTED under the requested aggregate publication scope. Public commands reproduce the disclosed presentation, not the unavailable private backtests. The separate [ORB](../orb-visual-evidence.md), [EBP](../ebp-visual-evidence.md) and [MacroImpulse](../macro-visual-evidence.md) matrices retain BLOCKED extensions and exact handoff requirements.

No new backtest, optimization, bootstrap, sealed access, MT5 state change, entry/risk change, deployment or automatic PR merge occurred. ORBINDEX and the archived NOWICK study and figures remain byte-identical to the fetched public baseline. The private current-source checkout passed its freshness gate; historical dirty checkouts were preserved and their missing-skill limits do not establish current support.

The source-backed financing ledger is available, while the distinct original portability/decomposition tables remain missing. Macro sequential totals remain a canonical reported aggregate without recovered original group decomposition. Calendar extraction scopes remain unreconciled, commission qualification remains documentation-only, and the EBP observational association does not establish reversal economics. Those limitations survived publication.
