"""Render the complete canonical Markdown articles as a static reading edition."""

from argparse import ArgumentParser
from html import escape
import json
from pathlib import Path
import posixpath
import sys
from xml.etree import ElementTree

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from scripts.site_studies import STUDIES
from srl.claims import digest, quantitative_blocks

REPO = 'https://github.com/vda93/systematic-research-lab'
LIBRARY = 'studies/README.md'
MARKDOWN = MarkdownIt('commonmark', {'html': False}).enable('table')


def source(path, label):
    return f'<a href="{REPO}/blob/main/{escape(path, quote=True)}">{escape(label)}</a>'


def reviewed_markdown(path, text, ledger):
    blocks = quantitative_blocks(text)
    expected = [record['sha256'] for record in ledger['documents'][path]]
    if [digest(block.encode()) for block in blocks] != expected:
        raise ValueError(f'Quantitative Markdown differs from the reviewed claim registry: {path}')
    return MARKDOWN.parse(text)


def target_path(path, href):
    if not href or href.startswith('/') or any(c in href for c in ':\\%?'):
        raise ValueError(f'Expected a repository-relative link in {path}: {href}')
    target, separator, fragment = href.partition('#')
    dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), target)) if target else path
    if dest == '..' or dest.startswith('../'):
        raise ValueError(f'Link leaves repository: {href}')
    return dest + separator + fragment


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
  <nav aria-label="Main navigation"><a href="index.html#research">Studies</a>
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


class ReadingEdition:
    """Share the original figures and canonical document routes across one render."""

    def __init__(self, root, ledger):
        self.root = root
        self.ledger = ledger
        self.figures = {figure['path'] for figure in ledger['figures']}
        self.outputs = {}
        self.routes = {'README.md': 'index.html', LIBRARY: 'index.html#research'}
        self.routes.update({study['article']: f'{slug}.html' for slug, study in STUDIES.items()})

    def document(self, path):
        text = (self.root / path).read_text(encoding='utf-8')
        return reviewed_markdown(path, text, self.ledger)

    def figure_url(self, path):
        if path not in self.figures:
            raise ValueError(f'Unregistered figure: {path}')
        return 'plots/' + Path(path).name

    def image(self, path, alt):
        url = self.figure_url(path)
        if not alt.strip():
            raise ValueError(f'Missing alternative text: {path}')
        data = (self.root / path).read_bytes()
        self.outputs['docs/' + url] = data
        _, _, width, height = map(float, ElementTree.fromstring(data).attrib['viewBox'].split())
        return (f'<img src="{url}" width="{round(width)}" height="{round(height)}" '
                f'alt="{escape(alt, quote=True)}" loading="lazy">')

    def inline(self, children, path):
        html = []
        for token in children:
            if token.type == 'text':
                html.append(escape(token.content))
            elif token.type == 'link_open':
                dest = target_path(path, token.attrGet('href'))
                if dest.startswith('figures/'):
                    url = self.figure_url(dest)
                else:
                    url = self.routes.get(dest, f'{REPO}/blob/main/{dest}')
                html.append(f'<a href="{escape(url, quote=True)}">')
            elif token.type == 'image':
                dest = target_path(path, token.attrGet('src'))
                html.append(f'<a class="chart" href="{self.figure_url(dest)}">{self.image(dest, token.content)}</a>')
            elif token.type == 'code_inline':
                html.append(f'<code>{escape(token.content)}</code>')
            elif token.type == 'softbreak':
                html.append('\n')
            elif token.type in ('strong_open', 'em_open', 'strong_close', 'em_close', 'link_close'):
                slash = '/' if token.nesting < 0 else ''
                html.append(f'<{slash}{token.tag}>')
            else:
                raise ValueError(f'Unsupported inline Markdown in {path}: {token.type}')
        return ''.join(html)

    @staticmethod
    def inline_title(token):
        # A source heading may contain evidence links. Its TOC entry is one anchor.
        return escape(''.join(c.content for c in token.children if c.type in ('text', 'code_inline')))

    def article(self, slug, study, tokens):
        path = study['article']
        if tokens[0].tag != 'h1' or sum(t.type == 'heading_open' and t.tag == 'h1' for t in tokens) != 1:
            raise ValueError(f'Expected one article title at the start of {path}')
        title = self.inline(tokens[1].children, path)
        intro = []
        sections = []
        toc = []
        body = intro
        heading = ''
        table_number = 0
        for i, token in enumerate(tokens[3:], start=3):
            if token.type == 'heading_open' and token.tag == 'h2':
                heading = self.inline_title(tokens[i + 1])
                section_id = f'section-{len(sections) + 1}'
                body = []
                sections.append((section_id, body))
                toc.append(f'<li><a href="#{section_id}">{heading}</a></li>')
            if token.type == 'inline':
                body.append(self.inline(token.children, path))
            elif token.type == 'table_open':
                table_number += 1
                body.append(f'<section class="table-scroll" tabindex="0" aria-label="Table {table_number}: {heading}"><table>')
            elif token.type == 'table_close':
                body.append('</table></section>')
            elif token.tag in ('p', 'h2', 'h3', 'thead', 'tr', 'th', 'tbody', 'td'):
                if token.tag == 'th' and token.nesting == 1:
                    body.append('<th scope="col">')
                else:
                    slash = '/' if token.nesting < 0 else ''
                    body.append(f'<{slash}{token.tag}>')
                if token.nesting < 0:
                    body.append('\n')
            else:
                raise ValueError(f'Unsupported Markdown block in {path}: {token.type}')
        # When the article opens directly with a section, show that lead before
        # the contents navigation, especially on mobile.
        if not intro and sections:
            key, parts = sections.pop(0)
            intro.append(f'<section id="{key}">{"".join(parts)}</section>')
        article_sections = '\n'.join(
            f'<section id="{key}">{"".join(parts)}</section>' for key, parts in sections)
        related = ' · '.join(f'<a href="{key}.html">{other["name"]}</a>'
                             for key, other in STUDIES.items() if key != slug)
        name = study['name']
        return shell(name, f"""<nav class="crumb" aria-label="Breadcrumb"><a href="index.html#research">Studies</a>
<span aria-hidden="true"> / </span><span aria-current="page">{name}</span></nav>
<article><div class="article-head"><h1>{title}</h1>
{''.join(intro)}</div><div class="article-layout">
<nav class="contents" aria-label="Article contents"><strong>In this study</strong><ul>{''.join(toc)}</ul></nav>
<div class="reading">{article_sections}</div></div></article>
<nav class="related" aria-label="Study navigation">{source(path, 'Original Markdown article')} · {related}</nav>""")

    def landing(self, articles):
        tokens = self.document(LIBRARY)
        headings = [i for i, t in enumerate(tokens) if t.type == 'heading_open' and t.tag == 'h2']
        cards = []
        for i, (slug, study) in zip(headings, STUDIES.items(), strict=True):
            if tokens[i + 3].type != 'paragraph_open':
                raise ValueError(f'Missing synopsis under {tokens[i+1].content}')
            heading = self.inline_title(tokens[i + 1])
            if heading != study['name']:
                raise ValueError(f"Library needs a section headed {study['name']}")
            summary = self.inline(tokens[i + 4].children, LIBRARY)
            cover = study['cover']
            path = study['article']
            cover_image = next(c for t in articles[slug] for c in (t.children or [])
                               if c.type == 'image' and target_path(path, c.attrGet('src')) == cover)
            cards.append(f"""<article class="card">
<div class="plot">{self.image(cover, cover_image.content)}</div>
<div class="card-body"><h3><a href="{slug}.html">{heading}</a></h3>
<p>{summary}</p><a class="read" href="{slug}.html">Read the {study['name']} study <span aria-hidden="true">→</span></a></div>
</article>""")
        return shell('Research library', f"""<section class="hero">
<div><p class="kicker">Systematic trading research</p><h1>Research library</h1>
<p class="lead">I tested when to trade an index breakout and whether I could trade the first move after a news release. These are the results and the decisions I made.</p></div>
</section>
<section id="research"><h2>Case studies</h2><div class="cards">{''.join(cards)}</div></section>
<section class="method" id="method"><h2>How I read the evidence</h2>
<p>I keep the discovery period separate from later tests and ask what the quoted prices would have meant for a trade. The public code rebuilds the figures from research aggregates. Replaying the original trades requires private data.</p>
<nav aria-label="Methods and sources">{source('docs/empirical-methods.md', 'Empirical methods')}
{source('docs/evidence.md', 'Evidence register')} {source('docs/security.md#reproduce-the-checks', 'Reproduce the figures')}</nav></section>""")


def site_artifacts(root):
    edition = ReadingEdition(root, json.loads((root / 'data/claim-registry.json').read_bytes()))
    articles = {slug: edition.document(study['article']) for slug, study in STUDIES.items()}
    for slug, study in STUDIES.items():
        edition.outputs[f'docs/{slug}.html'] = edition.article(slug, study, articles[slug])
    edition.outputs['docs/index.html'] = edition.landing(articles)
    return edition.outputs


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate reviewed website outputs')
    args = parser.parse_args()
    for name, payload in site_artifacts(ROOT).items():
        path = ROOT / name
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        elif not path.exists() or path.read_bytes() != payload:
            raise SystemExit(f'Stale site output: {name}')
