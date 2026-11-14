"""Render the public reading edition from selected, reviewed Markdown paragraphs."""

from argparse import ArgumentParser
from html import escape
import json
from pathlib import Path
import posixpath
import re
import sys
from xml.etree import ElementTree

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from scripts.site_studies import STUDIES
from srl.claims import digest, quantitative_blocks

REPO = 'https://github.com/vda93/systematic-research-lab'
LIBRARY = 'studies/README.md'
SECTIONS = (
    ('mechanism', 'Trading mechanism'), ('design', 'Test design'),
    ('results', 'Results and figures'), ('controls', 'Controls and robustness'),
    ('validation', 'Later validation'), ('limits', 'Limitations'),
    ('decision', 'Final decision'),
)


def source(path, label):
    return f'<a href="{REPO}/blob/main/{escape(path, quote=True)}">{escape(label)}</a>'


def paragraphs(text):
    return re.split(r'\n\s*\n', text.strip())


def select_paragraph(blocks, prefix):
    matches = [p for p in blocks if p.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f'Expected one canonical paragraph beginning {prefix!r}')
    return matches[0]


def check_summary(sentence, blocks):
    matches = [block for block in blocks if sentence in block]
    if len(matches) != 1:
        raise ValueError(f'Summary differs from the canonical library: {sentence}')
    return matches[0]


def check_excerpt(block, records, refs, source_ids):
    if set(refs) - source_ids:
        raise ValueError(f'Unknown evidence IDs: {refs}')
    if quantitative_blocks(block):
        sha = digest(block.encode())
        record = next((r for r in records if r['sha256'] == sha), None)
        if not record or not set(refs).intersection(record['source_ids']):
            raise ValueError(f'Quantitative excerpt lacks a matching reviewed source: {block[:75]}')


def display_prose(block, path):
    # Render only the inline Markdown constructs used in the selected paragraphs.
    # Every URL originates in the canonical document and is checked again by the site audit.
    html = []
    for token in MarkdownIt().parseInline(block)[0].children:
        if token.type == 'text':
            html.append(escape(token.content))
        elif token.type == 'link_open':
            href = token.attrGet('href')
            if not href or any(c in href for c in ':\\%?') or href.startswith('/'):
                raise ValueError(f'Expected a repository-relative citation in {path}')
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), href))
            if dest.startswith('../'):
                raise ValueError(f'Citation leaves repository: {href}')
            html.append(f'<a href="{REPO}/blob/main/{escape(dest, quote=True)}">')
        elif token.type == 'code_inline':
            html.append(f'<code>{escape(token.content)}</code>')
        elif token.type in ('strong_open', 'em_open', 'strong_close', 'em_close', 'link_close'):
            slash = '/' if token.nesting < 0 else ''
            html.append(f'<{slash}{token.tag}>')
        else:
            raise ValueError(f'Unsupported Markdown token {token.type} in {path}')
    return ''.join(html)


def evidence_links(refs):
    return ' · '.join(source(f'docs/evidence.md#{ref.lower()}', ref) for ref in refs)


def shell(title, content):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | TradingBotHQ</title>
  <link rel="stylesheet" href="site.css">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header><div class="shell nav">
  <a class="logo" href="index.html"><span class="mark" aria-hidden="true">TB</span>TradingBotHQ</a>
  <nav aria-label="Main navigation"><a href="index.html#research">Library</a>
    <a href="index.html#method">Methods</a>
    {source('docs/evidence.md', 'Evidence')} <a href="{REPO}">GitHub</a></nav>
</div></header>
<main id="content" tabindex="-1" class="shell">
{content}
</main>
<footer><div class="shell foot"><span>TradingBotHQ · Public research</span>
<nav aria-label="Publication information">{source('docs/ownership.md', 'Contributions')}
{source('docs/provenance.md', 'Provenance')} {source('docs/limitations.md', 'Limitations')}</nav></div></footer>
</body>
</html>
""".encode()


def image(root, name, study, ledger, *, full=False):
    figure_records = {f['path']: f for f in ledger['figures']}
    record = figure_records[f'figures/{name}']
    node = ElementTree.fromstring((root / record['path']).read_bytes())
    title = node.findtext('{http://www.w3.org/2000/svg}title') or ''
    title = title.split('|', 1)[-1].strip()
    if not title:
        raise ValueError(f'Figure lacks a title: {name}')
    url = 'plots/' + name
    blocks = paragraphs((root / study['article']).read_text(encoding='utf-8'))
    image_line = next(p for p in blocks if p.startswith('![') and p.endswith(f'(../figures/{name})'))
    check_excerpt(image_line, ledger['documents'][study['article']], record['source_ids'],
                  {s['id'] for s in ledger['sources']})
    alt = escape(image_line[2:image_line.index('](')], quote=True)
    _, _, width, height = map(float, node.attrib['viewBox'].split())
    img = (f'<img src="{url}" width="{round(width)}" height="{round(height)}" '
           f'alt="{alt}" loading="lazy">')
    if not full:
        return f'<div class="plot">{img}</div>'
    scope = 'Conceptual illustration' if record['scope'] == 'CONCEPTUAL_SCHEMATIC' else 'Reported historical figure'
    return (f'<figure><a href="{url}">{img}</a>'
            f'<figcaption><strong>{scope}</strong> · {escape(title)}. '
            f'{evidence_links(record["source_ids"])} · <a href="{url}">Full size</a></figcaption></figure>')


def landing(root, ledger):
    cards = []
    for slug, study in STUDIES.items():
        cards.append(f"""<article class="card">
  {image(root, study['hero'], study, ledger)}
  <div class="card-body"><p class="kicker">{escape(study['title'])}</p>
  <h3><a href="{slug}.html">{escape(study['question'])}</a></h3>
  <p>{escape(study['finding'])}</p>
  <p class="qualification"><strong>Limitation</strong> {escape(study['caveat'])}</p>
  <p class="verdict">{escape(study['decision'])}</p>
  <a class="read" href="{slug}.html">Read the {escape(slug.upper() if slug != 'macroimpulse' else 'MacroImpulse')} study <span aria-hidden="true">→</span></a></div>
</article>""")
    return shell('Research library', f"""<section class="hero">
  <div><p class="kicker">Systematic trading research</p><h1>Research library</h1>
  <p class="lead">What happens to a trading idea when its rules, costs and validation period are fixed?</p></div>
  <aside class="note"><strong>About the evidence</strong><p>Public code reproduces selected figures and synthetic examples.
  Replaying the original market experiments requires private records.</p>{source('docs/provenance.md', 'Reproduction boundaries')}</aside>
</section>
<section id="research"><h2>Featured studies</h2><div class="cards">{''.join(cards)}</div></section>
<section class="method" id="method"><h2>Research methods</h2>
<p>Each study identifies the signal, order rules and costs, then explains which control or later sample determined the decision.</p>
<nav aria-label="Methods and sources">{source('docs/empirical-methods.md', 'Empirical methods')}
{source('docs/evidence.md', 'Evidence register')} {source('docs/security.md#reproduce-the-checks', 'Reproduce the exhibits')}</nav></section>
<section class="archive"><h2>Historical archive</h2><p>{source('studies/nowick.md', 'NOWICK and ANTI-NOWICK')} · Matched-candle study and original closeout.</p></section>""")


def study_page(root, slug, study, ledger, source_ids):
    sections = []
    toc = []
    for (anchor, role), (heading, excerpts) in zip(SECTIONS, study['sections'], strict=True):
        toc.append(f'<li><a href="#{anchor}">{role}</a></li>')
        body = []
        for path, prefix, refs in excerpts:
            block = select_paragraph(paragraphs((root / path).read_text(encoding='utf-8')), prefix)
            check_excerpt(block, ledger['documents'][path], refs, source_ids)
            refs_html = evidence_links(refs)
            body.append(f'<p>{display_prose(block, path)}</p>')
            if not refs:
                refs_html = source('docs/provenance.md#macroimpulse-closeout-clarification', 'Owner’s closeout clarification')
            body.append(f'<p class="citation">{source(path, "Source text")} · {refs_html}</p>')
        if anchor == 'results':
            body.append(image(root, study['result_figure'], study, ledger, full=True))
        sections.append(f'<section id="{anchor}"><h2>{escape(heading)}</h2>{"".join(body)}</section>')

    title = escape(study['title'])
    related = ' · '.join(f'<a href="{key}.html">{escape(other["title"])}</a>'
                         for key, other in STUDIES.items() if key != slug)
    sources = (f'{source(study["article"], "Original Markdown article")} · {evidence_links(study["evidence"])}')
    if slug == 'macroimpulse':
        sources += ' · ' + source('docs/provenance.md#macroimpulse-closeout-clarification', 'Owner’s closeout clarification')
    return shell(study['title'], f"""<nav class="crumb" aria-label="Breadcrumb"><a href="index.html#research">Research library</a>
<span aria-hidden="true"> / </span><span aria-current="page">{title}</span></nav>
<article><div class="article-head"><p class="kicker">{title}</p>
<h1>{escape(study['question'])}</h1><p class="lead">{escape(study['finding'])}</p>
<div class="summary"><p class="verdict"><strong>Decision</strong> {escape(study['decision'])}</p>
<p><strong>Limitation</strong> {escape(study['caveat'])}</p></div>
<p class="citation">{source(study['article'], 'Original Markdown article')} · <a href="#sources">Evidence and reproducibility</a></p></div>
<div class="article-layout"><nav class="contents" aria-label="Article contents"><strong>In this study</strong>
<ul>{''.join(toc)}<li><a href="#sources">Sources and reproducibility</a></li></ul></nav>
<div class="reading">{''.join(sections)}
<section id="sources"><h2>Source evidence and reproducibility</h2><p>{sources}</p>
<p>The public scripts rebuild selected exhibits from disclosed aggregates. The historical backtests require private inputs and implementations.</p>
<p>{source('docs/security.md#reproduce-the-checks', 'Reproduction instructions')} · {source('docs/provenance.md', 'Source boundaries')}</p></section>
</div></div></article>
<nav class="related" aria-label="Related studies"><strong>Other studies</strong> {related}</nav>""")


def site_artifacts(root):
    ledger = json.loads((root / 'data/claim-registry.json').read_bytes())
    figures = {f['path']: f for f in ledger['figures']}
    source_ids = {s['id'] for s in ledger['sources']}
    library = paragraphs((root / LIBRARY).read_text(encoding='utf-8'))
    artifacts = {}
    for slug, study in STUDIES.items():
        for key in ('question', 'decision', 'finding', 'caveat'):
            block = check_summary(study[key], library)
            if quantitative_blocks(study[key]):
                check_excerpt(block, ledger['documents'][LIBRARY], study['evidence'], source_ids)
        artifacts[f'docs/{slug}.html'] = study_page(root, slug, study, ledger, source_ids)
        for name in (study['hero'], study['result_figure']):
            artifacts[f'docs/plots/{name}'] = (root / figures[f'figures/{name}']['path']).read_bytes()
    artifacts['docs/index.html'] = landing(root, ledger)
    return artifacts


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate the reviewed website outputs')
    args = parser.parse_args()
    for name, payload in site_artifacts(ROOT).items():
        path = ROOT / name
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        elif not path.exists() or path.read_bytes() != payload:
            raise SystemExit(f'Stale site output: {name}')
