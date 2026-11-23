# Public evidence and reproducibility

These studies build on trading ideas selected for testing; some reference rules have earlier sources. This page explains what the published evidence can establish, what readers can reproduce and what remains private.

The [ORBINDEX extract](../data/orbindex-public.json) supplies the six published figures. The [source register](evidence.md#orbindex-publication-verification) distinguishes figures transcribed from verified original research packages from the follow-up evidence recovered through a handoff. Public scripts rebuild those exhibits. Independent replay of the market experiments would require the private quote history, trade records and implementations.

The [MacroImpulse figure record](macro-visual-evidence.md) identifies the aggregate inputs, source files and limits of each historical comparison. The order-mechanics illustration uses a fictional sequence. Its arrows describe possible order states without measuring fill probability, slippage or profit. The separate [synthetic methods study](study.md) uses artificial observations to illustrate inference.

## MacroImpulse closeout clarification

On 12 November 2026 I clarified why I shelved MacroImpulse. Around news releases, I saw large spreads, poor fills and slippage across brokers. I could not get execution conditions that justified trading it. This records my experience and decision. I did not quantify the differences between brokers in a new cost study.

A separate historical medium-impact evaluation had an incomplete event calendar. The original record preserves the invalid-data-universe finding and its limits. [Calendar evidence](evidence.md#b15)

## ORB setup and filter study

The [ORB setup and filter study](../studies/orb-setup-filters.md) is another investigation of a cash-open breakout idea. It documents the implemented rules, the later EMA extension, discovery comparisons, and later historical validation. The generic ORB concept is not claimed as an original invention. Its configuration and research record remain distinct from ORBINDEX and previously retired ORB publications. It publishes original prose and reviewed aggregates; third-party materials, private ticks, implementations, and source reports are not redistributed. Native tester qualification and positive scenario R do not authenticate historical broker-net profitability.

The [technical appendix](../studies/orb-setup-filters-appendix.md) records the execution admission rule, frozen shortlist, differing missing-data conventions, and statistical specification. Public code reproduces the figures and selected aggregate arithmetic. The reported confidence intervals and adjusted significance tests require the private daily inputs and are not independently reproduced from the released summaries.

## Publication history and rights

The portfolio includes ORBINDEX, MacroImpulse, and the later ORB setup and filter study. Earlier Git commits preserve the ordinary opening-range, Engulfing Bar Play and NOWICK publications and their research decisions. The [depublication inventory](../archived-public-paths.json) records the retired paths so the [history audit](../scripts/audit_public.py) can still check them.

Public code and original writing are under [MIT](../LICENSE). External strategy PDFs, proprietary EAs and raw market data have separate rights and remain outside this repository.
