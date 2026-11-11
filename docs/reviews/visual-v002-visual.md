> Independent AI review of the initial publication candidates; private storage paths have been redacted. Findings and their original conditional verdict are retained. See the [coordinator response](visual-v002-resolution.md) for subsequent fixes and verification. This is not independent human scientific peer review.

> SHA256 of the unredacted private report: `c1298f9e4f2f452c6e5767e9ce466c5cac9bbf9453b42720ac559a0851d5fa86`.

# Visual Research Portfolio v002: independent visual communication review

Review date: 2026-11-11. This is an AI visual and communication review, independent of the implementation claims. It is not human scientific peer review or a new validation of the private backtests.

## Verdict

**Conditional pass.** The three studies expose substantive negative results and distinguish development evidence, validation, engineering parity and economic qualification. Their leads and captions make the central decisions understandable within roughly 30–60 seconds of scanning. One Important navigation issue should be addressed before calling narrow-screen delivery complete: MacroImpulse has no explicit full-resolution links beside its figures. No Critical visual misrepresentation was found. The remaining issues are minor accessibility and layout polish.

The review made no source, data, implementation or strategy changes, and ran no new market experiment. Only this report and private preview PNGs were retained.

## Scope and artifact identities

ORB was reviewed in `[publication checkout]`, origin `https://github.com/vda93/systematic-research-lab.git`. The initial inspected HEAD was `caa9351767063e08d80bd3cb739da5c85220dd56`. During review, the parent moved the worktree to `codex/visual-ebp-v002` and began EBP integration; that work was not overwritten. This is not a TradingBotHQ worktree; its TradingBotHQ freshness procedure does not apply. No `AGENTS.md` was present at this public root.

The review covered the ORB renderer, nine SVGs, `studies/opening-range.md`, `docs/orb-visual-evidence.md`, and both public aggregate extracts. EBP and MacroImpulse were reviewed from the complete scratch bundles at `[EBP draft bundle]` and `[MacroImpulse draft bundle]`: each renderer, five SVGs, article, evidence note and public aggregate extract. Integration byte matching into the final public tree remains the parent's responsibility.

Renderer SHA-256 identities at review:

| Renderer | SHA-256 |
| --- | --- |
| ORB | `cff62f2c8d2a435f2903880a6515543bb7cbdd508e7b09cde0c23577ba4120cb` |
| EBP | `3ca05179e71ca5aca63785d0eb9f3447817ef200cd558f0e6dc74d880f76c2a0` |
| MacroImpulse | `82e99c46c769f7be5491e1cc2a4b259551ee70cdbd5bf1175c1ad95d0ad56c63` |

## Rendered inspection and bounded checks

All 19 main figures were visually inspected through actual PNG renders, not SVG text alone. Supplied desktop previews were inspected for all nine ORB, five EBP and five MacroImpulse figures. Current renderers were then executed without writing public outputs, capturing all 19 figures privately at desktop resolution and width 390px. Every 390px render was inspected, with fresh desktop inspection of ORB qualification/validation, EBP order policy and Macro spread filter to resolve stale-preview concerns. Private captures are under `reviews/previews`.

A separate narrow reproduction check confirmed renderer-returned SVG bytes exactly matched all nine ORB SVGs and all five SVGs in each scratch bundle. That check passed for 19/19 outputs using the existing pinned environment at `[private custody]/python.exe`. This was figure reproduction only, not a backtest or broad test-suite run.

The supplied ORB qualification preview lacked labels and the supplied validation preview had crowded start/date labels. Fresh renders confirmed the current qualification map includes every duration and direction title and the validation now has distinct endpoint labels. Those stale-preview defects are not findings against the reviewed current artifacts.

## Findings

### Important V1: Macro figures need explicit full-resolution links

Location: `studies/news-research.md:28`, also captions at lines 34, 43, 77 and 88.

All five image captions omit direct full-resolution SVG links. At 390px the figures preserve their overall finding, but fine units, sample notes and annual detail require zoom. Depending on host-specific image-click behavior makes that necessary route unreliable. Add a descriptive full-resolution link to each existing SVG, following ORB and EBP. No data or figure redesign is required.

### Minor V2: standalone ORB and Macro SVGs lack native accessible descriptions

Locations: public `scripts/render_orb.py:16` and `scripts/render_orbindex.py:42`; scratch `macro/scripts/render_macro.py:42`.

These serializers write RDF metadata Title/Description, but do not add native SVG `<title>`, `<desc>` and linked image semantics as EBP does at `ebp/scripts/render_ebp.py:66`. The article Markdown supplies meaningful alternative text, so the embedded-image context is substantially better than the standalone SVG context. Add native semantics to new ORB/Macro SVG outputs if feasible. Preserve existing ORBINDEX outputs; changing its shared helper globally would expand scope unnecessarily. No screen-reader behavior was directly tested.

### Minor V3: the sparse EBP count markers clip at the zero boundary

Location: `scripts/render_ebp.py:123` and line 128; `figures/ebp-order-policy.svg`, left panel, arms A and C.

The circular endpoints at three trades extend left of the axes' zero boundary and are partially clipped. The exact labels remain visible and the zero-based count comparison is honest, so this does not change the conclusion. Let those endpoint markers extend outside the clipping box or use an unclipped marker treatment while retaining a zero-based bar scale. The total-R endpoints and negative labels were inspected and are not cropped off the figure.

### Minor V4: the conceptual lifecycle is still a desktop graphic

Location: `scripts/render_ebp.py:256`; article image/caption at `studies/engulfing-and-support.md:29` and line 31.

At width 390px the six state boxes and technical skipped-state labels are too small to read comfortably without zoom. The article caption explicitly conveys GTC occupancy versus eligible replacement and clearly labels the example fictional, so the narrow reader still receives the finding. A future compact stacked variant would improve this explanatory schematic more than it would improve the inherently dense empirical grids. The current full-resolution link is present.

## What communicates well

**ORB.** The compact hero is legible at 390px and leads with the two actual reasons for stopping: independent USTEC block failure and gold financing. Detailed figures reveal the complete searched landscape, qualification flags, representative-versus-maximum concentration, paired geometry controls, separate validation blocks, execution stress and monetary qualification. The USTEC and gold histories, clocks and units remain distinct. Zero, clipped color ranges, valid zero-trade cells and scientific-invalid cells are disclosed rather than silently filled. The summary and detailed economic figures do not invite pooling the candidates into a portfolio. No misleading marker cropping or remaining label overlap was found in current ORB renders.

**EBP.** The 88-cell matrix displays signed values, with bold positive text supplementing color. The added histogram and trade-support scatter explain the actual distribution rather than displaying only a winning cell. The pending-policy comparison makes the three-trade denominator prominent; positive GTC totals cannot reasonably be mistaken for a robust winner. The schematic announces its fictional status in the image, alt text and caption. The small-candle plot distinguishes an archived aggregate confidence interval from subgroup point estimates, keeps the near-null DE30 result visible, and does not turn association into profitable reverse trading. Price-R and overlapping-trade limitations remain visible.

**MacroImpulse.** The favorable baseline remains visible alongside failed interventions. The spread filter's near-equal zero-based totals are paired with exact negative deltas, avoiding a misleadingly enlarged absolute comparison. Sequential-leg bars identify dependent components of the same groups. The medium-impact cost figure exposes the failed year despite positive aggregate totals, names the documented commission model and retains its documentation-only qualification. The calendar chart shows recorded source density, preserves HIGH as a comparison and explains why the apparent later failure became INVALID_DATA_UNIVERSE. Missing source-scope reconciliation is disclosed rather than hidden.

Across the studies, chart titles carry findings, captions identify scope and units, and alternative text gives substantive results. Color is generally supplemented by signs, position relative to zero, direct numbers, marker shapes, line styles or hatching. Dense grid detail needs full-resolution inspection; the text leads and captions carry the conclusions at ordinary mobile text size. The material reviewed retains AI attribution through ORB's contribution/ownership link and MacroImpulse's explicit AI-assisted engineering wording; no recommendation here removes that attribution or restores named-source branding.

## Limits

This review inspected rendered chart images and the supplied Markdown, not a deployed browser page or actual phone. Width-390 captures test static figure legibility, not host CSS, browser zoom controls, keyboard navigation or screen-reader operation. Formal color-vision simulation and contrast-ratio measurement were not performed. No raw private backtest, custody chain, broker schedule or historical cost model was independently re-audited; source qualifications were assessed as communication, not promoted to new scientific certification. Existing ORBINDEX and NOWICK were outside this review's modification scope and were not changed by the reviewer.

After V1 is resolved, the artifacts are suitable for this aggregate portfolio publication within those limits. Any later renderer or substantive text changes should be checked against the affected figure and caption rather than treated as covered automatically by this snapshot.
