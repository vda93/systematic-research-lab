# Writing a research case study

A [library entry](../studies/README.md) should let a reader identify the question, finding, decision and most important caveat in one screen. Link directly to the full article and the relevant headings in the [evidence register](evidence.md).

Use this reading order for the article.

- **Question.** Name the market and the proposed mechanism. Phrase the headline as a question the test can answer.
- **Brief answer.** State what happened and which candidate or branch the finding covers.
- **Test definition.** Give the asset, timeframe or event clock, signal, order lifetime, entry and exit. Identify the tested rule version and distinguish it from any illustration of the original idea.
- **Costs and controls.** Explain which spread, commission, slippage and financing assumptions enter the calculation. State what was measured or modelled and what is unknown. Explain what the chosen comparison holds fixed.
- **Results and figures.** Give each result its unit, denominator and sample role. Caption each figure with the comparison the reader should make and link its exact source. Keep overlapping configurations and separate strategy lineages distinct.
- **Later validation.** Say when the rules were frozen, how history was used in selection, and whether later observations were independent, previously inspected or never opened.
- **Decision.** Name the criterion that determined the outcome and who made the decision when that matters. A closed program may still contain untested candidates.
- **Limitations.** Identify the uncertainty most likely to change the interpretation, such as sparse fills, an incomplete event calendar or unverified costs.
- **Evidence and reproducibility.** Cite the exact source IDs for each principal finding and link the relevant register entries. Identify what readers can rebuild from disclosed aggregates, what a synthetic example illustrates and which findings rely on private reports.

Before publication, review the quantitative paragraphs against their sources, update the [claim registry](../data/claim-registry.json) and [release inventory](../release-files.json), and run the [verification checks](security.md#reproduce-the-checks). Preserve the original sample labels and [source limitations](provenance.md).


## A short reading edition and a complete record

The public website uses concise, source-checked editorial summaries defined in [the site copy](../scripts/site_studies.py). It should show the finding, the strongest visual evidence and the important limitation before asking readers to open the full technical record. The complete [ORBINDEX](../studies/orbindex.md) and [news-release](../studies/news-research.md) studies retain their original methodological detail. The [ORB setup and filter case study](../studies/orb-setup-filters.md) pairs a concise research narrative with its [technical appendix](../studies/orb-setup-filters-appendix.md).

New public numeric statements must be represented as evidence-bound facts and verified against registered quantitative source paragraphs. Do not insert free-standing numerical claims into the website copy, relax the source checks or treat a previously examined period as an independent holdout.
