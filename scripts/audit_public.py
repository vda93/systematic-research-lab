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


GENERATED = {'.git', '.venv', '__pycache__', 'build', 'dist', '.pytest_cache'}
TEXT_TYPES = {'.py', '.json', '.md', '.toml', '.svg', '.yml', '.yaml', '.txt'}
SPECIAL = {'LICENSE', '.gitignore', '.gitattributes'}
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


def text_findings(name: str, payload: bytes) -> list[str]:
    if len(payload) > 600_000 or (Path(name).suffix not in TEXT_TYPES and name not in SPECIAL):
        return [f'unsupported source type or size: {name}']
    try:
        text = payload.decode('utf-8')
    except UnicodeDecodeError:
        return [f'non-text source: {name}']
    return [f'private-content pattern in {name}' for pattern in PRIVATE if pattern.search(text)]


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
    for name, path in actual.items():
        if (path.is_symlink() or not path.resolve().is_relative_to(root) or
                any(getattr(part.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
                    for part in [path, *path.parents] if part != root and part.is_relative_to(root))):
            findings.append(f'linked or escaping source: {name}')
            continue
        payload = path.read_bytes()
        hashes[name] = hashlib.sha256(payload).hexdigest()
        problems = text_findings(name, payload)
        findings.extend(problems)
        if not problems and path.suffix == '.md':
            for raw in LINK.findall(payload.decode('utf-8')):
                target = unquote(raw.strip('<>'))
                parts = urlsplit(target)
                if parts.scheme or not parts.path:
                    continue
                named = (path.parent / parts.path).resolve()
                if not named.is_relative_to(root) or not named.exists():
                    findings.append(f'broken local link: {name}')
    return {'status': 'PASS' if not findings else 'FAIL', 'files': hashes,
            'findings': sorted(set(findings))}


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
        if set(git('ls-files').decode().splitlines()) != approved_names:
            findings.append('tracked files differ from the exact public inventory')
        checked_blobs = set()
        for revision in revisions:
            # NUL records preserve exact paths instead of relying on shell quoting.
            for record in git('ls-tree', '-rz', revision).split(b'\0'):
                if not record:
                    continue
                header, raw_name = record.split(b'\t', 1)
                mode, kind, oid = header.decode().split()
                name = raw_name.decode('utf-8')
                if mode != '100644' or kind != 'blob' or name not in approved_names:
                    findings.append('unapproved type or path in publication history')
                    continue
                if oid not in checked_blobs:
                    findings.extend(text_findings(name, git('cat-file', 'blob', oid)))
                    checked_blobs.add(oid)
            metadata = git('show', '-s', '--format=%an%n%ae%n%cn%n%ce%n%B', revision).decode('utf-8')
            fields = metadata.splitlines()
            if len(fields) < 4 or fields[0] != 'vda93' or fields[2] != 'vda93':
                findings.append('unexpected Git author or committer identity')
            if any(not re.fullmatch(r'\d+\+vda93@users\.noreply\.github\.com', fields[i]) for i in (1, 3)):
                findings.append('Git metadata must use the public noreply address')
            if any(pattern.search(metadata) for pattern in PRIVATE):
                findings.append('private-content pattern in Git metadata')
    except (subprocess.CalledProcessError, OSError, ValueError, IndexError):
        return {'status': 'FAIL', 'findings': ['Git audit could not complete']}
    return {'status': 'PASS' if not findings else 'FAIL', 'commits': len(revisions),
            'root_commits': roots, 'unique_blobs_checked': len(checked_blobs), 'findings': sorted(set(findings))}


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
