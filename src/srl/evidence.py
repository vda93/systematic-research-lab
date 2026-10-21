"""Declared evidence integrity and sample-role controls; never a truth certificate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping
import zipfile


@dataclass(frozen=True)
class Evidence:
    id: str
    path: str
    sha256: str
    bytes: int
    source: str
    license: str
    redistribution: str
    disclosure: str
    disclosure_approved: bool
    owner: str
    kind: str
    study_id: str
    sample_space: str
    period_start: str
    period_end_exclusive: str
    sample_role: str
    consumed: bool


@dataclass(frozen=True)
class Claim:
    id: str
    kind: str
    text: str
    evidence_ids: list[str]
    disclosure_approved: bool


@dataclass(frozen=True)
class Manifest:
    version: int
    evidence: tuple[Evidence, ...]
    claims: tuple[Claim, ...]


ROLES = {'development', 'validation', 'test', 'spent', 'invalid', 'engineering', 'illustration'}
KINDS = {'historical', 'reported_aggregate', 'synthetic', 'engineering'}
CLAIMS = {'engineering', 'historical_report', 'historical_alpha', 'clean_oos_economic'}
NON_SCIENTIFIC = {'engineering', 'illustration'}


def _safe_name(name: str) -> bool:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        return False
    parts = name.split('/')
    return all(part not in {'', '.', '..'} and part == part.strip()
               and not part.endswith('.') and not any(ord(c) < 32 for c in part)
               and not any(c in '<>"|?*' for c in part)
               and not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?', part)
               for part in parts)


def _json(payload: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def nonfinite(value: str) -> None:
        raise ValueError(f'nonfinite JSON value: {value}')

    try:
        result = json.loads(payload, object_pairs_hook=unique, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('invalid JSON') from exc
    if not isinstance(result, dict):
        raise ValueError('manifest must be an object')
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    """Read JSON without accepting duplicate keys or nonfinite constants."""
    return _json(Path(path).read_bytes())


def _parse(raw: Mapping[str, Any]) -> Manifest:
    if not isinstance(raw, Mapping) or set(raw) != {'version', 'evidence', 'claims'}:
        raise ValueError('expected version, evidence and claims only')
    if type(raw['version']) is not int or raw['version'] != 1:
        raise ValueError('unsupported manifest version')
    if not isinstance(raw['evidence'], list) or not raw['evidence'] or not isinstance(raw['claims'], list):
        raise ValueError('evidence must be nonempty; claims must be a list')
    try:
        evidence = tuple(Evidence(**row) for row in raw['evidence'])
        claims = tuple(Claim(**row) for row in raw['claims'])
    except TypeError as exc:
        raise ValueError('missing, unknown or malformed record fields') from exc
    rows: tuple[Evidence | Claim, ...] = (*evidence, *claims)
    for row in rows:
        strings = (value for key, value in vars(row).items()
                   if key not in {'bytes', 'consumed', 'disclosure_approved', 'evidence_ids'})
        if any(not isinstance(value, str) or not value.strip() for value in strings):
            raise ValueError('metadata must contain nonblank strings')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', row.id):
            raise ValueError('invalid evidence or claim id')
        if type(row.disclosure_approved) is not bool or not row.disclosure_approved:
            raise ValueError('public disclosure approval is required')
    if len({e.id for e in evidence}) != len(evidence) or len({c.id for c in claims}) != len(claims):
        raise ValueError('duplicate evidence or claim id')
    for e in evidence:
        if not _safe_name(e.path) or not re.fullmatch('[0-9a-f]{64}', e.sha256):
            raise ValueError('unsafe path or invalid SHA256')
        if type(e.bytes) is not int or e.bytes < 0 or type(e.consumed) is not bool:
            raise ValueError('invalid size or consumed flag')
        if e.sample_role not in ROLES or e.kind not in KINDS or e.redistribution != 'permitted':
            raise ValueError('unsupported role, kind or redistribution permission')
        try:
            start, end = date.fromisoformat(e.period_start), date.fromisoformat(e.period_end_exclusive)
        except (TypeError, ValueError) as exc:
            raise ValueError('invalid ISO period') from exc
        if start.isoformat() != e.period_start or end.isoformat() != e.period_end_exclusive or start >= end:
            raise ValueError('period must be canonical ISO dates with start < exclusive end')
        if e.sample_role == 'test' and e.consumed:
            raise ValueError('consumed evidence cannot be unseen test evidence')
    for i, a in enumerate(evidence):
        for b in evidence[i + 1:]:
            if a.path.casefold() == b.path.casefold() and (a.path != b.path or a.sha256 != b.sha256):
                raise ValueError('conflicting portable file paths')
            if (a.study_id == b.study_id and a.sample_space == b.sample_space
                    and a.sample_role != b.sample_role
                    and not {a.sample_role, b.sample_role} & NON_SCIENTIFIC
                    and a.period_start < b.period_end_exclusive and b.period_start < a.period_end_exclusive):
                raise ValueError('overlapping scientific sample roles in the same study and sample space')
    by_id = {e.id: e for e in evidence}
    for claim in claims:
        if (claim.kind not in CLAIMS or not isinstance(claim.evidence_ids, list)
                or not claim.evidence_ids or any(not isinstance(i, str) for i in claim.evidence_ids)
                or len(set(claim.evidence_ids)) != len(claim.evidence_ids)
                or any(i not in by_id for i in claim.evidence_ids)):
            raise ValueError('claim requires a supported kind and unique existing evidence references')
        sources = [by_id[i] for i in claim.evidence_ids]
        if claim.kind in {'historical_alpha', 'clean_oos_economic'}:
            if any(e.kind != 'historical' or e.sample_role in NON_SCIENTIFIC | {'invalid'} for e in sources):
                raise ValueError('economic claim requires historical, scientifically usable evidence')
        if claim.kind == 'historical_report' and any(e.kind not in {'historical', 'reported_aggregate'} for e in sources):
            raise ValueError('historical report requires historical evidence or reported aggregates')
        if claim.kind == 'clean_oos_economic' and any(e.sample_role != 'test' or e.consumed for e in sources):
            raise ValueError('clean OOS economic claim requires unconsumed test samples')
    return Manifest(1, evidence, claims)


def _history(current: Manifest, previous: Manifest) -> None:
    for now in current.evidence:
        for old in previous.evidence:
            if now.id == old.id and now.sha256 != old.sha256:
                raise ValueError('evidence identity cannot change its content hash')
            if now.id == old.id or now.sha256 == old.sha256:
                if old.consumed and not now.consumed:
                    raise ValueError('consumption is irreversible for an evidence identity')
                if old.sample_role in {'spent', 'invalid'} and now.sample_role != old.sample_role:
                    raise ValueError('spent or invalid evidence retains its role')
                if (old.sample_role in {'development', 'validation'}
                        and now.sample_role not in {old.sample_role, 'spent', 'invalid'}):
                    raise ValueError('observed scientific samples may only retain their role, be spent or invalidated')
                if now.sample_role == 'test' and (old.consumed or old.sample_role in {'spent', 'invalid', 'development', 'validation'}):
                    raise ValueError('observed, spent or invalid evidence cannot become unseen test evidence')


def _read(root: Path, name: str) -> bytes:
    path = root
    for part in ('', *name.split('/')):
        path = path / part
        if path.is_symlink() or path.is_junction():
            raise ValueError('symlink or junction evidence paths are forbidden')
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('evidence must be a regular file within the root')
    return path.read_bytes()


def _verify(manifest: Manifest, read: Callable[[str], bytes]) -> None:
    for e in manifest.evidence:
        payload = read(e.path)
        if len(payload) != e.bytes or hashlib.sha256(payload).hexdigest() != e.sha256:
            raise ValueError(f'content hash or size mismatch: {e.id}')


def verify_manifest(root: Path, raw: Mapping[str, Any], *, previous: Mapping[str, Any] | None = None) -> Manifest:
    """Check bytes and declared roles; supply trusted prior ledgers to check transitions."""
    manifest = _parse(raw)
    _history(manifest, manifest)
    if previous is not None:
        _history(manifest, _parse(previous))
    _verify(manifest, lambda name: _read(Path(root), name))
    return manifest


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def pack(root: Path, raw: Mapping[str, Any], output: Path, *, previous: Mapping[str, Any] | None = None) -> None:
    """Write an exclusive, deterministic ZIP of approved declared evidence and metadata."""
    manifest = verify_manifest(root, raw, previous=previous)
    members = {'manifest.json': _canonical(raw)}
    if previous is not None:
        members['history.json'] = _canonical(previous)
    for e in manifest.evidence:
        members['evidence/' + e.path] = _read(Path(root), e.path)
    _verify(manifest, lambda name: members['evidence/' + name])
    members['hashes.json'] = _canonical({name: {'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)}
                                        for name, payload in sorted(members.items())})
    # Exclusive creation preserves existing work, including dangling symlinks.
    with Path(output).open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
            for name, payload in sorted(members.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system, info.external_attr = 3, 0o100644 << 16
                archive.writestr(info, payload)


def verify_pack(path: Path, *, expected_sha256: str | None = None) -> Manifest:
    """Check every ZIP member, CRC, hash, exact membership and embedded manifest without extraction."""
    try:
        if expected_sha256 is not None and hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected_sha256:
            raise ValueError('archive does not match the externally recorded SHA256')
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if (len(set(n.casefold() for n in names)) != len(names)
                    or any(not _safe_name(n) for n in names)
                    or any((info.external_attr >> 16) & 0o170000 == 0o120000 for info in infos)):
                raise ValueError('duplicate, unsafe or symlink archive members')
            if sum(info.file_size for info in infos) > 64 * 1024 * 1024:
                raise ValueError('closeout exceeds the 64 MiB verification limit')
            if archive.testzip() is not None:
                raise ValueError('archive CRC mismatch')
            members = {n: archive.read(n) for n in names}
        manifest = _parse(_json(members['manifest.json']))
        _history(manifest, manifest)
        expected = {'manifest.json', 'hashes.json'} | {'evidence/' + e.path for e in manifest.evidence}
        if 'history.json' in members:
            _history(manifest, _parse(_json(members['history.json'])))
            expected.add('history.json')
        if set(members) != expected:
            raise ValueError('archive members do not match the manifest')
        hashes = _json(members['hashes.json'])
        actual = {n: {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
                  for n, b in members.items() if n != 'hashes.json'}
        if hashes != actual:
            raise ValueError('archive internal hashes mismatch')
        _verify(manifest, lambda name: members['evidence/' + name])
        return manifest
    except (KeyError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError('invalid or incomplete closeout archive') from exc
