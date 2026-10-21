"""Check reviewed prose and figure provenance; this does not verify private facts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


def quantitative_blocks(text: str) -> list[str]:
    """Conservatively include digit-bearing prose, headings and table blocks.

    Fenced code is executable documentation, covered by tests rather than this
    prose ledger. Link destinations are removed so a URL date is not a result.
    The review ledger may classify navigation/schema text explicitly.
    """
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
            lines.append('')
        elif not fenced:
            lines.append(line)
    blocks = re.split(r'\n\s*\n', '\n'.join(lines))
    return [b.strip() for b in blocks if re.search(r'\d', re.sub(r'\]\([^)]*\)', ']', b))]


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _source_file(root: Path, name: object) -> bool:
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or any(part in {'', '.', '..'} for part in name.split('/'))):
        return False
    path = root
    for part in name.split('/'):
        path = path / part
        if path.is_symlink() or path.is_junction():
            return False
    return path.is_file() and path.resolve().is_relative_to(root.resolve())


def audit_claims(root: Path) -> dict[str, Any]:
    """Fail closed for unreviewed numeric prose or changed declared inputs."""
    findings: list[str] = []
    raw = json.loads((root / 'data/claim-registry.json').read_text(encoding='utf-8'))
    sources = raw['sources']
    if not sources or len(sources) != len({s['id'] for s in sources}):
        findings.append('empty or duplicate source register')
    by_id = {s['id']: s for s in sources}
    register = (root / 'docs/evidence.md').read_text(encoding='utf-8')
    headings = set(re.findall(r'^## ([A-Z][A-Z0-9-]*)\s*$', register, re.M))
    for source in sources:
        if source['id'] not in headings or source['disclosure'] != 'approved':
            findings.append('missing source identity or disclosure')
        if source['kind'] not in {'retained_private_report', 'public_replay'}:
            findings.append('unsupported source kind')
    paths = {p.relative_to(root).as_posix() for p in root.rglob('*.md')
             if not any(part in {'build', '.venv', '.git', 'dist'} or part.endswith('.egg-info')
                        for part in p.relative_to(root).parts)}
    if set(raw['documents']) != paths:
        findings.append('Markdown scope changed without claim review')
    for name, reviewed in raw['documents'].items():
        path = root / name
        if name not in paths or not _source_file(root, name):
            findings.append(f'missing reviewed document: {name}')
            continue
        blocks = quantitative_blocks(path.read_text(encoding='utf-8'))
        if len(blocks) != len(reviewed):
            findings.append(f'quantitative paragraph count changed: {name}')
            continue
        for block, claim in zip(blocks, reviewed, strict=True):
            refs = claim['source_ids']
            if claim['sha256'] != digest(block.encode()):
                findings.append(f'unreviewed quantitative prose: {name}')
            if claim['kind'] not in {'historical_report', 'public_replay', 'methods', 'documentation'}:
                findings.append('unsupported public claim kind')
            if claim['kind'] in {'historical_report', 'public_replay'} and not refs:
                findings.append(f'empirical claim lacks source: {name}')
            if any(ref not in by_id for ref in refs):
                findings.append(f'unknown claim source: {name}')
            if claim['kind'] == 'public_replay' and any(by_id[ref]['kind'] != 'public_replay' for ref in refs):
                findings.append('private report cannot be relabeled public replay')
    for figure in raw['figures']:
        if not isinstance(figure['inputs'], dict) or not figure['inputs']:
            findings.append('figure requires nonempty declared inputs')
            continue
        for name, sha in figure['inputs'].items():
            if (not _source_file(root, name) or not isinstance(sha, str)
                    or not re.fullmatch('[0-9a-f]{64}', sha)):
                findings.append('figure input requires a safe source path and canonical SHA256')
            elif digest((root / name).read_bytes()) != sha:
                findings.append(f'figure input changed without provenance review: {name}')
        if not figure['source_ids'] or any(i not in by_id for i in figure['source_ids']):
            findings.append('figure lacks declared source identities')
        if not _source_file(root, figure['path']) or not _source_file(root, figure['renderer']):
            findings.append('figure output or renderer missing')
    actual_figures = {p.relative_to(root).as_posix() for p in (root / 'figures').glob('*.svg')}
    if ({f['path'] for f in raw['figures']} != actual_figures
            or len(raw['figures']) != len(actual_figures)):
        findings.append('figure inventory differs from provenance register')
    return {'status': 'FAIL' if findings else 'PASS', 'findings': sorted(set(findings)),
            'reviewed_blocks': sum(len(v) for v in raw['documents'].values()),
            'sources': len(sources), 'figures': len(raw['figures'])}


def audit_acquisition(root: Path) -> None:
    """Bind public data and method bytes to the pre-access receipt."""
    from srl.fx_study import SOURCE_URL, parse_csv

    receipt = json.loads((root / 'data/ecb-acquisition.json').read_text())
    snapshot = (root / 'data/ecb-fx-reference.csv').read_bytes()
    if (receipt['source_url'] != SOURCE_URL or receipt['rights_reviewed'] is not True
            or receipt['archive_notice_check'] != 'PASS_SINGLE_CSV_NO_EXTRA_NOTICE'
            or receipt['canonical_csv_sha256'] != digest(snapshot)
            or not re.fullmatch('[0-9a-f]{40}', receipt['protocol_commit'])
            or len(parse_csv(snapshot)) != receipt['selected_rows']):
        raise ValueError('acquisition source, rights, identity or qualification mismatch')
    expected_files = {'src/srl/fx_study.py', 'scripts/fx_study.py', 'tests/test_fx_study.py',
                      'experiments/ecb-fx-mom20-protocol.md', 'DATA_LICENSE.md'}
    if set(receipt['frozen_file_sha256']) != expected_files:
        raise ValueError('incomplete pre-access method identities')
    for name, sha in receipt['frozen_file_sha256'].items():
        if digest((root / name).read_bytes()) != sha:
            raise ValueError('method changed after pre-access freeze; versioned amendment required')
