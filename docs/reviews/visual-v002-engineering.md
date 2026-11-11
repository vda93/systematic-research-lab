> Independent AI review of the initial publication candidates; private storage paths have been redacted. Findings and their original conditional verdict are retained. See the [coordinator response](visual-v002-resolution.md) for subsequent fixes and verification. This is not independent human scientific peer review.

> SHA256 of the unredacted private report: `61f86d74958e97c00c112cd9ebd3f4510ede74e2c263128131fff677397e5a23`.

# Visual Research Portfolio v002 — engineering/publication review

Status: final independent review of the initial publication implementations. Coordinator owns remediation and final integrated gates.

## Scope

Read-only review of ORB commit `caa9351767063e08d80bd3cb739da5c85220dd56` over public baseline `af4b28dc7a43e152ad8460f0e65ea9f0f3ba5512`, the completed EBP and Macro publication bundles, and the integrating public worktree. This reviewer made no implementation changes, commits, external comments or agent delegations. Private evidence was not independently reopened; source-transcription verification belongs to the separate evidence review.

## Checks actually run

- Inspected actual Git root, origin, branch, HEAD, working status and diff, including untracked publication files.
- Read the three renderers, their focused tests, the reproduction entry point, publication/evidence notes, claim audit, release audit and retained CI/security configuration.
- Ran supplied EBP focused suite: **9 tests passed**. Ran supplied Macro focused suite: **5 tests passed**. These establish original bundle rendering/arithmetic checks, not resolution of the findings below.
- Ran in-memory source-mutation probes (no input files changed): duplicate Macro baseline identity with a changed value; changed calendar monthly count; reversed EBP arm order; changed ORB robust flag. All were accepted and exposed misleading labels/identity handling described below.
- Confirmed no baseline diff in dependency pins, CI workflows, CodeQL, Dependabot, security documents, core scientific modules, existing historical renderer or ORBINDEX renderer at the inspected revision.

## Critical

None identified in the reviewed scope.

## Important

### I1 — Macro accepts ambiguous/incomplete inputs and numeric labels are independent of their source values

Initial bundle `scripts/render_macro.py`, `_baseline` at lines 62–78, `_calendar` at lines 152–155, and `build_figures`: there is no input validation. Baseline cells are converted to a dictionary without checking duplicate identities. Appending a duplicate existing cell with `spread_only_usd=999` is accepted: its heatmap cell becomes `$999.00`, while the summary remains the hard-coded `+$4,250.48`, `1,396`, `PF 3.6889` and `10 / 10`. Changing an early monthly MEDIUM count by 1,000 changes the calendar line while the displayed earlier total/rate remains `16,288 / 271.47` and the ratio remains `15.6%`. Similar literals appear in filter/count and annual-cost annotations.

Required response: reject duplicate, missing, invalid and inconsistent identities; derive quantitative labels from validated disclosed data. Fixed scientific conclusions should be asserted against their explicit reviewed data contract if not dynamically calculated. Add tests that inspect data-dependent marks/labels and ambiguity rejection rather than testing only one frozen snapshot.

### I2 — EBP policy identity depends on row order

Initial bundle `scripts/render_ebp.py:116–117` and `_validate:29–43`: labels are fixed positional A/B/C/D contracts, but the data's arm identity/order is not validated or used to bind those labels. Reversing `policy_matrix.arms` passes `_validate` and plots D's 1,297 trades and −94.90R under A's GTC/completed-H4 label. This changes the scientific interpretation without an error. Native/distribution summary counts and pooled statistics also include hard-coded numeric annotations.

Required response: normalize arms by validated unique identity or reject noncanonical order, and bind labels to actual policy fields. Reject missing/duplicate arms and inconsistent dependent statistics; derive numeric summaries from their source cells.

### I3 — ORB qualification annotations and OOS consistency are not protected by current mutation tests

Initial `scripts/render_orb.py` qualification legend at lines 100–101: changing one robust flag is accepted (21 robust cells), but the legend still reports 4 robust cells outside the 18-cell selected plateau. Several validity/empty-cell and concentration annotations are also literals. In `_validation`, total R is read separately for the title from the cumulative endpoint used for geometry. The existing source-change test changes only `oos[0].total_r`, proving that some bytes changed while allowing an unchanged path endpoint and contradictory total.

Required response: derive counts and source-dependent annotation values, validate subset/flag relationships, tie OOS totals to final cumulative values, and use meaningful mutation/rejection checks. Complete missing-grid rejection already exists and should be preserved.

## Minor

No additional actionable minor finding. Review findings concern engineering correctness; they do not assert the currently retained numerical figures are wrong. The supplied frozen values passed their focused reconciliation tests.

## Limits and interim verdict

**Changes required before publication approval** for I1–I3. Findings were sent promptly to the coordinator, who accepted them and is implementing targeted fixes. This reviewer will not independently re-review those fixes; the coordinator owns their new tests and final gates. Final status must distinguish that response from this initial independent finding.

Only Windows / Python 3.12 execution was observed locally. Pinned dependency and four-target CI configurations are preserved, but Linux/Python 3.13 byte equality and hosted security scans require actual CI execution. No market replay, deployment qualification, broker-net reconstruction, strategy run or independent human scientific peer review is claimed. The final release/claim inventory, local-link check, integrated reproduction, full suite and hosted CI are coordinator-owned final gates; they were not independently rerun here.
