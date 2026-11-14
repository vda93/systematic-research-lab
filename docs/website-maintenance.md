# Maintaining the research website

Open [the research library](index.html) directly from a checkout for offline reading. Keep the HTML, stylesheet and `plots` folder together. The article summaries and figures work offline. Links to the original articles, evidence register and source repository open on GitHub.

## Edit and verify

Edit the [canonical library](../studies/README.md) or detailed article first. Verify changes against the [evidence register](evidence.md) and review any quantitative Markdown blocks in the [claim registry](../data/claim-registry.json). The [editorial selections](../scripts/site_studies.py) identify the synopsis, whole source paragraphs, evidence IDs and approved figures for each case. A change to a selected paragraph must preserve its sample, units, accounting and qualifications.

Use the pinned Python environment described in the [verification instructions](security.md#reproduce-the-checks). Rebuild from the repository root and review the diff.

```sh
python scripts/render_site.py --write
python scripts/render_site.py
python -m coverage run scripts/reproduce.py --check
python -m coverage report
python scripts/audit_public.py --history
```

The [renderer](../scripts/render_site.py) derives the five HTML pages and offline copies of the original figures. The second command checks those outputs byte for byte. The [publication policy](../scripts/site_policy.py) limits pages, resources and markup. Review stylesheet or figure byte changes before approving new digests, and retain the narrowly scoped verification of previously published bytes in Git history. Add any approved new paths to the [release inventory](../release-files.json) and stage them before the history check.

Preview with only `docs` as the web root. Check the landing page and each case on a narrow phone and a desktop, follow the article contents and evidence links, and use Tab and Enter to check the skip link and focus indicators. The charts should load with external network requests blocked.

## Publish the reviewed revision

After review and successful CI, mark the draft ready and merge the reviewed head into `main`. In the repository’s **Settings → Pages → Build and deployment**, choose **Deploy from a branch**, select **main** and **/docs**, then choose **Save**. The empty `.nojekyll` marker lets Pages serve the audited static files directly and keeps the canonical Markdown files from becoming a second set of generated pages. [GitHub’s publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

Wait for the Pages deployment in Actions to succeed for the merged revision. Open **Visit site** in Pages settings, navigate to all four cases, open a full-size chart, follow a source citation and check the archive and mobile layout before announcing the live address.
