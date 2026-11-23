# Maintaining the research website

The site has two layers: concise public reading editions and complete technical research records. The public copy is in [scripts/site_studies.py](../scripts/site_studies.py), while the detailed [ORBINDEX](../studies/orbindex.md), [news-release](../studies/news-research.md), and [ORB setup and filter](../studies/orb-setup-filters.md) articles remain canonical for scientific results.

## Editing a reading edition

Edit the study's presentation copy and keep the summary limited to the question, the actual decision, the evidence and the most consequential uncertainty. Numeric facts are bound to registered paragraphs of the complete studies. The renderer refuses unbound numeric claims or figures without matching source IDs.

The ORB setup and filter study also links to a [technical appendix](../studies/orb-setup-filters-appendix.md) for implementation details, missing-data conventions, and statistical limits. Its reading edition keeps the setup, matched-period comparison, EMA uncertainty, and research decision visible.

The original ORBINDEX figures, tables and technical classifications remain in its complete record. The public page should explain potential prior exposure of the later period in ordinary language, not print internal status flags.

Regenerate and verify from the repository root using the pinned environment:

```sh
python scripts/render_site.py --write
python scripts/render_site.py
python -m coverage run scripts/reproduce.py --check
python -m coverage report
python scripts/audit_public.py --history
```

Review the generated HTML changes, claim bindings, exact release inventory, Git history audit, figures and source links before opening a PR. Check all pages on desktop and mobile, with network resources blocked to verify that the approved SVG figures remain usable offline. The website's short reading editions are not substitutes for the full technical records.

## Publishing

GitHub Pages serves `main` from `/docs`. A merge updates the public site. Review the draft PR and its hosted checks first, then verify the Pages deployment uses the merged commit. Confirm that all public studies, source links and figures work before announcing the live revision.
