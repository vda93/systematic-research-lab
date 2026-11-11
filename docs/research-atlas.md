# Research atlas: featured research and its evidence

[Portfolio](../README.md) · [Evidence](evidence.md) · [Timeline](timeline.md)

The four research programs ask different questions about trading signals and execution. Their studies preserve the tested contract, sample role and decision. The [contribution record](ownership.md) identifies documented research decisions and assistance.

| Program | Question | Main studies |
| --- | --- | --- |
| Opening-range breakout | Does breaking a session range predict continuation beyond generic clock or momentum effects? | [ORB](../studies/opening-range.md), [historical branches](../studies/opening-range-atlas.md), [O1](evidence.md#o1) |
| Engulfing Bar Play | Does an engulfing/retracement setup survive explicit order-lifecycle definitions? | [EBP](../studies/engulfing-and-support.md), [B21](evidence.md#b21) |
| ORBINDEX | Do DE30 index opening-range timing regions survive shared order ownership, costs and a later-period test? | [ORBINDEX](../studies/orbindex.md), [IX1–IX4](evidence.md#ix1) |
| MacroImpulse | Are scheduled economic-release impulses tradeable after execution, costs, filtering and calendar-completeness checks? | [News research](../studies/news-research.md), [calendar forensics](../studies/data-forensics.md), [B08](evidence.md#b08) |

Supporting [research engineering](../studies/research-engineering.md) covers evidence manifests, sample-role checks and implementation comparisons. It supplies methods for these programs.

The [ORB branch atlas](../studies/opening-range-atlas.md) deliberately separates negative baselines, promising but unrun discovery successors, conflicting validation, scoped parity and financing failures. An unrun test cannot be reported as a negative test.

The news studies preserve a particularly important correction: a parser can finish while its input economic calendar is incomplete. That invalidates a clean strategy verdict for the missing-event universe, rather than establishing profitability or loss.

Earlier publication branches outside the owner's chosen portfolio scope have been removed from the **current public tree**. Their original Git history and private research provenance remain preserved. This is editorial selection, not retroactive scientific revision.

**Retained archive:** [NOWICK / ANTI-NOWICK](../studies/nowick.md) preserves its original matched-control findings and rejection; removing it from the featured lineup does not rewrite its evidence.
