"""Audit the explicit public source inventory, links and independent Git history."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

if __package__:
    from . import site_policy as site
else:  # Direct CLI invocation: python scripts/audit_public.py
    import site_policy as site


GENERATED = {'.git', '.venv', '__pycache__', 'build', 'dist', '.pytest_cache'}

# Digest of sorted newline-separated paths in the reviewed depublication ledger.
# A file count or name prefix cannot establish which exact paths were removed.
ARCHIVE_SHA256 = 'cdd44f8c480ac68a1bef453e3f9b9544c7d15c4769da6dd35f4d1dfc10f7112c'
LAST_FOUR_STUDY_MAIN = 'b1a8b0874625dac0d11074c718ec25e8e154d63a'
TEXT_TYPES = {'.py', '.json', '.md', '.toml', '.svg', '.yml', '.yaml', '.txt'}
SPECIAL = {'LICENSE', '.gitignore', '.gitattributes'}
# Previous publication policies applied to these exact Git trees and blobs.
# Generic type, size, encoding, privacy and identity checks still run.
V001_COMMITS = {
    '24d794f5efcc0ba8b3911c5452f47e6d23223de8',
    '4e787e90db81cc29336c163088c806b23bc6225c',
}
V002_COMMITS = {'a3451382bea0064c950c5aff44c80a9680a66ef1', LAST_FOUR_STUDY_MAIN}
V002_SITE_BLOBS = {
    'docs/index.html': '5bec6b184978ca5f7eb376d95031deda4bede472',
    'docs/orbindex.html': 'e34fd0c79b2bb414f151117f3ba5a1320d147e89',
    'docs/macroimpulse.html': '9a2b2466fef03f8516008ec62dd40c70eaa3ade5',
    'docs/orb.html': 'e57e3149d57a557a09a076ae8324905e9860803f',
    'docs/ebp.html': '775f1c99184447447f04423a5be35e7b55999702',
    'docs/site.css': '20b3f817991cf07bd6f6ae1e66fe9449506044e4',
    'docs/plots/orb-summary.svg': 'd18114588dc68744b975ccf50c1a0c0653924a69',
    'docs/plots/orb-gold-economics.svg': 'a07b2827959bb27f8c443aefe6e996251698d9e6',
    'docs/plots/ebp-order-policy.svg': '300008cc68c6ebe15c78925a95046b1566db13e8',
    'docs/plots/ebp-native-timeframe.svg': 'fefa9d4700befb08e1018951b3b99fdb88a782fa',
}
LINK = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
PRIVATE = [re.compile(pattern, re.I) for pattern in (
    r'https?://(?:app\.notion\.com|(?:docs|drive)\.google\.com)/',
    r'[A-Z]:[\\/](?:Users|Trading|MT5)[^\s]*',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'gh[pousr]_[A-Za-z0-9]{30,}',
    r'github_pat_[A-Za-z0-9_]{30,}',
    r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
)]


def safe_name(name: str) -> bool:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        return False
    path = PurePosixPath(name)
    return (not path.is_absolute() and path.as_posix() == name and
            all(part not in {'.', '..'} | GENERATED and not part.endswith('.egg-info') for part in path.parts))


def source_files(root: Path):
    return [path for path in sorted(root.rglob('*')) if path.is_file() and
            not any(part in GENERATED or part.endswith('.egg-info') for part in path.relative_to(root).parts)]


def is_archived_site_blob(name: str, oid: str, revision: str) -> bool:
    if revision in V001_COMMITS:
        return name == 'docs/index.html' and oid == '35b280c49072484b6f6379707bf87ef0f374b874'
    return revision in V002_COMMITS and V002_SITE_BLOBS.get(name) == oid


def valid_archive(names: object, current: set[str]) -> bool:
    if not isinstance(names, list) or not all(safe_name(name) for name in names):
        return False
    canonical = '\n'.join(sorted(names)).encode()
    return hashlib.sha256(canonical).hexdigest() == ARCHIVE_SHA256 and not current.intersection(names)


def text_findings(name: str, payload: bytes, *, archived_site: bool = False,
                  pages: dict[str, site.SitePage] | None = None) -> list[str]:
    # One specifically reviewed, provider-permitted market snapshot. This does
    # not admit arbitrary raw vendor CSVs to the publication boundary.
    approved_csv = name == 'data/ecb-fx-reference.csv'
    approved_site_path = name in site.PAGES or name in {site.CSS, site.MARKER}
    if (len(payload) > 600_000 or (Path(name).suffix not in TEXT_TYPES and
            name not in SPECIAL and not approved_csv and not approved_site_path and not archived_site)):
        return [f'unsupported source type or size: {name}']
    try:
        text = payload.decode('utf-8')
    except UnicodeDecodeError:
        return [f'non-text source: {name}']
    findings = [f'private-content pattern in {name}' for pattern in PRIVATE if pattern.search(text)]
    if name in site.PAGES and not archived_site:
        page = site.SitePage(name, text)
        findings.extend(f'{name}: {error}' for error in page.errors)
        if pages is not None:
            pages[name] = page
    if name == site.CSS and not archived_site and hashlib.sha256(payload).hexdigest() != site.CSS_SHA256:
        findings.append('unreviewed site stylesheet')
    if name == site.MARKER and payload:
        findings.append('Pages marker must be empty')
    if name.startswith('docs/') and name.endswith('.svg') and not archived_site:
        if site.PLOT_HASHES.get(name) != hashlib.sha256(payload).hexdigest():
            findings.append(f'unreviewed site figure: {name}')
    return findings


def heading_anchors(text: str) -> set[str]:
    """GitHub-style slugs for the ordinary ATX headings used by this release."""
    anchors, counts = set(), {}
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
        match = None if fenced else re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if match:
            slug = re.sub(r'[^\w\- ]', '', match[1].lower()).replace(' ', '-')
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            anchors.add(slug + (f'-{count}' if count else ''))
    return anchors


def site_references(pages: dict[str, site.SitePage], hashes: dict[str, str], root: Path) -> list[str]:
    """Resolve all website links against safe, inventoried local source bytes."""
    errors = []
    anchors = {name: page.ids for name, page in pages.items()}
    for name, page in pages.items():
        for target, fragment in page.references:
            if target not in hashes:
                errors.append(f'broken site link: {name} -> {target}')
                continue
            if not fragment:
                continue
            if target.endswith('.md') and target not in anchors:
                anchors[target] = heading_anchors((root / target).read_text(encoding='utf-8'))
            if fragment not in anchors.get(target, set()):
                errors.append(f'broken site fragment: {name} -> {target}#{fragment}')

    copies = hashes.keys() & site.PLOT_HASHES.keys()
    if copies:
        try:
            registry = 'data/claim-registry.json'
            if registry not in hashes:
                raise ValueError('missing figure provenance')
            declared = json.loads((root / registry).read_bytes())['figures']
            originals = {figure['path'] for figure in declared}
        except (KeyError, TypeError, ValueError):
            return errors + ['invalid source register for site figures']
        for copy in copies:
            original = 'figures/' + Path(copy).name
            if original not in originals or hashes.get(original) != hashes[copy]:
                errors.append(f'site figure differs from the registered original: {copy}')
    return errors


def audit_directory(root: Path) -> dict:
    root = root.resolve()
    findings = []
    manifest = root / 'release-files.json'
    try:
        names = json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {'status': 'FAIL', 'findings': ['missing or invalid explicit file inventory']}
    if (not isinstance(names, list) or not names or not all(safe_name(name) for name in names) or
            len(names) != len(set(names))):
        return {'status': 'FAIL', 'findings': ['unsafe, duplicated or empty source inventory']}
    actual = {p.relative_to(root).as_posix(): p for p in source_files(root)}
    if set(actual) != set(names):
        findings.append('actual source inventory differs from release-files.json')
    hashes = {}
    pages = {}
    for name, path in actual.items():
        if (path.is_symlink() or not path.resolve().is_relative_to(root) or
                any(getattr(part.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
                    for part in [path, *path.parents] if part != root and part.is_relative_to(root))):
            findings.append(f'linked or escaping source: {name}')
            continue
        payload = path.read_bytes()
        hashes[name] = hashlib.sha256(payload).hexdigest()
        problems = text_findings(name, payload, pages=pages)
        findings.extend(problems)
        if not problems and path.suffix == '.md':
            for raw in LINK.findall(payload.decode('utf-8')):
                target = unquote(raw.strip('<>'))
                parts = urlsplit(target)
                if parts.scheme or (not parts.path and not parts.fragment):
                    continue
                named = (path.parent / parts.path).resolve() if parts.path else path
                if not named.is_relative_to(root) or not named.exists():
                    findings.append(f'broken local link: {name}')
                elif parts.fragment and named.suffix == '.md' and named.is_file():
                    if parts.fragment not in heading_anchors(named.read_text(encoding='utf-8')):
                        findings.append(f'broken heading fragment: {name} -> {target}')
    findings.extend(site_references(pages, hashes, root))
    return {'status': 'PASS' if not findings else 'FAIL', 'files': hashes,
            'findings': sorted(set(findings))}


def metadata_findings(metadata: str, *, merge: bool = False) -> list[str]:
    """Allow the public owner and GitHub's public merge-service committer only."""
    fields = metadata.splitlines()
    if len(fields) < 4:
        return ['incomplete Git metadata']
    public_owner = lambda name, email: name == 'vda93' and bool(
        re.fullmatch(r'\d+\+vda93@users\.noreply\.github\.com', email))
    findings = []
    if not public_owner(fields[0], fields[1]):
        findings.append('unexpected Git author identity')
    if not public_owner(fields[2], fields[3]) and not (
            merge and fields[2] == 'GitHub' and fields[3] == 'noreply@github.com'):
        findings.append('unexpected Git committer identity')
    if any(pattern.search(metadata) for pattern in PRIVATE):
        findings.append('private-content pattern in Git metadata')
    return findings


def audit_git(root: Path) -> dict:
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)
    findings = []
    try:
        revisions = git('rev-list', 'HEAD').decode().splitlines()
        roots = git('rev-list', '--max-parents=0', 'HEAD').decode().splitlines()
        if len(roots) != 1:
            findings.append('history must have one independently created root')
        approved_names = set(json.loads((root / 'release-files.json').read_text()))
        # Preserve the exact historical publication boundary after scoped de-publication.
        # Removed files are still scanned in every old commit, but cannot reappear in HEAD.
        archived_list = json.loads((root / 'archived-public-paths.json').read_text())
        if not valid_archive(archived_list, approved_names):
            findings.append('invalid curated-history path allowlist')
            archived_names = set()
        else:
            archived_names = set(archived_list)
        # Only the ancestry already public at curation may contain retired paths.
        prior_revisions = set(git('rev-list', LAST_FOUR_STUDY_MAIN).decode().splitlines())
        if set(git('ls-files').decode().splitlines()) != approved_names:
            findings.append('tracked files differ from the exact public inventory')
        checked_blobs = set()
        for revision in revisions:
            allowed_history_names = approved_names | archived_names if revision in prior_revisions else approved_names
            # NUL records preserve exact paths instead of relying on shell quoting.
            for record in git('ls-tree', '-rz', revision).split(b'\0'):
                if not record:
                    continue
                header, raw_name = record.split(b'\t', 1)
                mode, kind, oid = header.decode().split()
                name = raw_name.decode('utf-8')
                if mode != '100644' or kind != 'blob' or name not in allowed_history_names:
                    findings.append('unapproved type or path in publication history')
                    continue
                legacy = is_archived_site_blob(name, oid, revision)
                # Path-specific rules must still run when a blob appears at a new path.
                key = (name, oid, legacy)
                if key not in checked_blobs:
                    findings.extend(text_findings(name, git('cat-file', 'blob', oid), archived_site=legacy))
                    checked_blobs.add(key)
            metadata = git('show', '-s', '--format=%an%n%ae%n%cn%n%ce%n%B', revision).decode('utf-8')
            parents = git('rev-list', '--parents', '-n', '1', revision).decode().split()
            findings.extend(metadata_findings(metadata, merge=len(parents) > 2))
    except (subprocess.CalledProcessError, OSError, ValueError, IndexError):
        return {'status': 'FAIL', 'findings': ['Git audit could not complete']}
    return {'status': 'PASS' if not findings else 'FAIL', 'commits': len(revisions),
            'root_commits': roots, 'unique_blobs_checked': len({oid for _, oid, _ in checked_blobs}), 'findings': sorted(set(findings))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    result = {'directory': audit_directory(args.root)}
    if args.history:
        result['history'] = audit_git(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(item['status'] == 'PASS' for item in result.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
