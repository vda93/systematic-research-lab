"""Render short, source-checked reading editions; retain full technical studies in Markdown."""

from __future__ import annotations

from argparse import ArgumentParser
from html import escape
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from scripts.site_studies import STUDIES
from scripts import site_policy
from srl.claims import digest, quantitative_blocks


REPO = "https://github.com/vda93/systematic-research-lab"
FIGURE_ROOT = "figures/"


def source(path: str, label: str) -> str:
    return f'<a href="{REPO}/blob/main/{escape(path, quote=True)}">{escape(label)}</a>'


def public_text(template: str, facts: dict[str, str]) -> str:
    """Only verified numeric placeholders may introduce digits into website prose."""
    if re.search(r"\d", template):
        raise ValueError(f"Unbound numeric claim in public copy: {template[:75]}")
    try:
        return escape(template.format_map(facts), quote=True)
    except KeyError as exc:
        raise ValueError(f"Undefined public fact: {exc}") from exc


def validate_study(root: Path, slug: str, study: dict, ledger: dict) -> dict[str, str]:
    technical = study["technical"]
    original = (root / technical).read_text(encoding="utf-8")
    blocks = quantitative_blocks(original)
    claims = ledger["documents"][technical]
    if len(blocks) != len(claims) or any(
        digest(block.encode("utf-8")) != claim["sha256"]
        for block, claim in zip(blocks, claims, strict=True)
    ):
        raise ValueError(f"Technical record changed without claim review: {technical}")

    known_sources = {source_record["id"] for source_record in ledger["sources"]}
    values: dict[str, str] = {}
    for key, fact in study["facts"].items():
        value, evidence = fact["value"], fact["source"]
        if evidence not in known_sources or not any(
            value in block and evidence in claim["source_ids"]
            for block, claim in zip(blocks, claims, strict=True)
        ):
            raise ValueError(f"Unverified website fact {slug}:{key}: {value}")
        values[key] = value

    figures = {figure["path"]: figure for figure in ledger["figures"]}
    for section in study["sections"]:
        if not section["sources"] or set(section["sources"]) - known_sources:
            raise ValueError(f"Unregistered section evidence in {slug}")
        if "figure" in section:
            file_name = "figures/" + section["figure"]
            if file_name not in figures or not (
                set(section["sources"]) & set(figures[file_name]["source_ids"])
            ):
                raise ValueError(f"Figure without matching source: {file_name}")
        for paragraph in section["paragraphs"]:
            public_text(paragraph, values)
        public_text(section["heading"], values)
        if "caption" in section:
            public_text(section["caption"], values)
        if "table" in section:
            for row in [section["table"]["heading"], *section["table"]["rows"]]:
                for cell in row:
                    public_text(cell, values)
    for key in ("name", "title", "subtitle", "decision", "caveat"):
        public_text(study[key], values)
    if "figures/" + study["cover"] not in figures:
        raise ValueError(f"Unknown cover in {slug}")
    return values


def figure(root: Path, name: str, alt: str) -> str:
    original = root / FIGURE_ROOT / name
    node = ElementTree.fromstring(original.read_bytes())
    _, _, width, height = map(float, node.attrib["viewBox"].split())
    img = (f'<img src="plots/{name}" width="{round(width)}" '
           f'height="{round(height)}" alt="{escape(alt, quote=True)}" loading="lazy">')
    return f'<a class="chart" href="plots/{name}">{img}</a>'


def shell(title: str, content: str) -> bytes:
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
<nav aria-label="Main navigation"><a href="index.html#research">Studies</a>
<a href="index.html#method">Methods</a>
{source("docs/evidence.md", "Evidence")} <a href="{REPO}">GitHub</a></nav>
</div></header>
<main id="content" tabindex="-1" class="shell">
{content}
</main>
<footer><div class="shell foot"><span>TradingBotHQ · Public research</span>
<nav aria-label="Publication information">{source("docs/provenance.md", "Provenance")} {source("docs/limitations.md", "Limitations")}</nav></div></footer>
</body>
</html>
""".encode("utf-8")


def article(root: Path, slug: str, study: dict, values: dict[str, str]) -> bytes:
    label = public_text(study["name"], values)
    sections = []
    links = []
    for i, section in enumerate(study["sections"], start=1):
        anchor = f"section-{i}"
        heading = public_text(section["heading"], values)
        links.append(f'<li><a href="#{anchor}">{heading}</a></li>')
        parts = [f'<section id="{anchor}"><h2>{heading}</h2>']
        parts.extend(f'<p>{public_text(paragraph, values)}</p>'
                     for paragraph in section["paragraphs"])
        if "table" in section:
            table = section["table"]
            parts.append('<section class="table-scroll" tabindex="0" aria-label="Historical portfolio comparison"><table>')
            parts.append("<thead><tr>" + "".join(
                f'<th scope="col">{public_text(h, values)}</th>'
                for h in table["heading"]) + "</tr></thead><tbody>")
            for row in table["rows"]:
                parts.append("<tr>" + "".join(
                    f"<td>{public_text(cell, values)}</td>" for cell in row) + "</tr>")
            parts.append("</tbody></table></section>")
        if "figure" in section:
            parts.append(figure(root, section["figure"], section["alt"]))
            parts.append(f'<p class="citation">{public_text(section["caption"], values)} · '
                         f'<a href="plots/{section["figure"]}">Open figure</a></p>')
        parts.append('<p class="citation">Evidence: ' + " · ".join(
            source("docs/evidence.md#" + evidence.lower(), evidence)
            for evidence in section["sources"]) + "</p>")
        parts.append("</section>")
        sections.append("\n".join(parts))
    technical = source(study["technical"], "Complete research record")
    data = ("data/orbindex-public.json" if slug == "orbindex" else "data/macro-public.json")
    verification = (
        '<section id="verification"><h2>Data and verification</h2>'
        '<p>The public figures can be rebuilt from released aggregates. The original '
        'market backtests require private quotes and implementations, so they cannot '
        'be independently rerun from this website.</p>'
        f'<p>{technical} · {source(data, "Published aggregate data")} · '
        f'{source("docs/security.md#reproduce-the-checks", "Reproduce the figures")}</p>'
        '</section>'
    )
    links.append('<li><a href="#verification">Data and verification</a></li>')
    related = " · ".join(
        f'<a href="{other_slug}.html">{escape(other["name"])}</a>'
        for other_slug, other in STUDIES.items() if other_slug != slug
    )
    html = f"""<nav class="crumb" aria-label="Breadcrumb"><a href="index.html#research">Studies</a>
<span aria-hidden="true"> / </span><span aria-current="page">{label}</span></nav>
<article><div class="article-head">
<h1>{public_text(study["title"], values)}</h1>
<p class="lead">{public_text(study["subtitle"], values)}</p>
<p><strong>Decision.</strong> {public_text(study["decision"], values)}</p>
<p><strong>Main limitation.</strong> {public_text(study["caveat"], values)}</p>
<p class="citation">{technical} · {source("docs/evidence.md", "Evidence register")}</p>
</div><div class="article-layout">
<nav class="contents" aria-label="Article contents"><strong>In this study</strong>
<ul>{"".join(links)}</ul></nav>
<div class="reading">{"".join(sections)}{verification}</div>
</div></article>
<nav class="related" aria-label="Study navigation">{related}</nav>"""
    return shell(study["name"], html)


def landing(root: Path, studies: dict[str, dict[str, str]]) -> bytes:
    cards = []
    for slug, study in STUDIES.items():
        values = studies[slug]
        cover = figure(root, study["cover"], study["cover_alt"])
        cards.append(
            f'<article class="card"><div class="plot">{cover}</div>'
            f'<div class="card-body"><h3><a href="{slug}.html">'
            f'{public_text(study["name"], values)}</a></h3>'
            f'<p>{public_text(study["subtitle"], values)}</p>'
            f'<p>{public_text(study["decision"], values)}</p>'
            f'<a class="read" href="{slug}.html">Read the study '
            f'<span aria-hidden="true">→</span></a></div></article>'
        )
    body = f"""<section class="hero">
<p class="kicker">Independent systematic trading research</p>
<h1>What survives after the backtest?</h1>
<p class="lead">Two studies, two different reasons to stop. The conclusions come first; the evidence and full technical records remain available.</p>
</section>
<section id="research"><h2>Research library</h2><div class="cards">{"".join(cards)}</div></section>
<section class="method" id="method"><h2>How the evidence is used</h2>
<p>Historical results are not live fills. Each study distinguishes what was tested, what failed and which uncertainties remain.</p>
<nav aria-label="Methods and sources">{source("docs/empirical-methods.md", "Research methods")} {source("docs/evidence.md", "Evidence register")} {source("docs/security.md#reproduce-the-checks", "Reproduce figures")}</nav>
</section>"""
    return shell("Research library", body)


def site_artifacts(root: Path) -> dict[str, bytes]:
    ledger = json.loads((root / "data/claim-registry.json").read_text(encoding="utf-8"))
    checked = {slug: validate_study(root, slug, study, ledger)
               for slug, study in STUDIES.items()}
    artifacts = {"docs/index.html": landing(root, checked)}
    for slug, study in STUDIES.items():
        artifacts[f"docs/{slug}.html"] = article(root, slug, study, checked[slug])
    for path in site_policy.PLOT_HASHES:
        artifacts[path] = (root / FIGURE_ROOT / Path(path).name).read_bytes()
    return artifacts


if __name__ == "__main__":
    args = ArgumentParser(description=__doc__)
    args.add_argument("--write", action="store_true")
    parsed = args.parse_args()
    for name, content in site_artifacts(ROOT).items():
        output = ROOT / name
        if parsed.write:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        elif not output.is_file() or output.read_bytes() != content:
            raise SystemExit(f"Stale site output: {name}")
