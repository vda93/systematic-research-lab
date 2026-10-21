"""Bounded, explicit native-BBO acquisition; no network access on import.

Raw/cache destinations must be outside Git. This validates local commit content,
not remote publication, data rights, or later-stage scientific authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import gzip
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import zlib

ROOT = Path(__file__).resolve().parents[2]
BASE_PROTOCOL_COMMIT = 'c5f205fdeff02ea3f667a804974a6ee4d9098790'
_PROTOCOL = 'experiments/bbo-delay-protocol.md'
_AMENDMENT = 'experiments/bbo-delay-measurement-v2.md'
_CHUNK = 4 * 1024**2
_USER_AGENT = 'systematic-research-lab/3.0 (+https://github.com/vda93/systematic-research-lab)'
_sleep = time.sleep
_clock = time.monotonic


@dataclass(frozen=True)
class _Limits:
    file_bytes: int = 2 * 1024**3
    total_bytes: int = 12 * 1024**3
    reserve_bytes: int = 5 * 1024**3
    elapsed_seconds: int = 120 * 60


_LIMITS = _Limits()


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


def _open(request: Request, *, timeout: float) -> Any:
    # No environment proxy credentials, redirects, authentication or API keys.
    return build_opener(ProxyHandler({}), _NoRedirect()).open(request, timeout=timeout)


class _Stop(Exception):
    def __init__(self, status: str, reason: str):
        self.status, self.reason = status, reason
        super().__init__(reason)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, timeout=15)
    if result.returncode:
        raise _Stop('NOT_RUN_PROTOCOL', 'LOCAL_GIT_VERIFICATION_FAILED')
    return result.stdout


def _freeze(commit: str) -> dict[str, str]:
    if not isinstance(commit, str) or not re.fullmatch('[0-9a-fA-F]{40}', commit):
        raise _Stop('NOT_RUN_PROTOCOL', 'EXACT_LOCAL_COMMIT_REQUIRED')
    if _git(ROOT, 'cat-file', '-t', commit).strip() != b'commit':
        raise _Stop('NOT_RUN_PROTOCOL', 'OBJECT_IS_NOT_COMMIT')
    _git(ROOT, 'merge-base', '--is-ancestor', BASE_PROTOCOL_COMMIT, commit)
    hashes = {}
    for name in (_PROTOCOL, _AMENDMENT):
        committed = _git(ROOT, 'show', f'{commit}:{name}')
        if not committed or committed != (ROOT / name).read_bytes():
            raise _Stop('NOT_RUN_PROTOCOL', 'CURRENT_PROTOCOL_OR_AMENDMENT_NOT_FROZEN')
        hashes[name] = hashlib.sha256(committed).hexdigest()
    if _git(ROOT, 'show', f'{BASE_PROTOCOL_COMMIT}:{_PROTOCOL}') != (ROOT / _PROTOCOL).read_bytes():
        raise _Stop('NOT_RUN_PROTOCOL', 'ORIGINAL_PROTOCOL_CHANGED')
    hashes['commit_utc'] = _git(ROOT, 'show', '-s', '--format=%cI', commit).decode().strip()
    return hashes


def _link(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def _cache(destination: Path) -> Path:
    absolute = destination.absolute()
    if any(_link(p) for p in (absolute, *absolute.parents)):
        raise _Stop('NOT_RUN_CACHE', 'SYMLINK_OR_JUNCTION_CACHE_REFUSED')
    resolved = absolute.resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        raise _Stop('NOT_RUN_CACHE', 'CACHE_INSIDE_SOURCE_ROOT')
    existing = resolved
    while not existing.exists():
        existing = existing.parent
    if not existing.is_dir():
        raise _Stop('NOT_RUN_CACHE', 'CACHE_PARENT_IS_NOT_DIRECTORY')
    check = subprocess.run(['git', '-C', str(existing), 'rev-parse', '--show-toplevel'],
                           capture_output=True, timeout=15)
    if check.returncode == 0:
        raise _Stop('NOT_RUN_CACHE', 'CACHE_INSIDE_GIT_CHECKOUT')
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _atomic(path: Path, receipt: dict) -> None:
    # Serial cache lock protects this replace; interruption leaves either old or new JSON.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.bbo-receipt-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(receipt, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _elapsed(start: float, *, incomplete: bool = False) -> None:
    if _clock() - start > _LIMITS.elapsed_seconds:
        raise _Stop('INCOMPLETE_RESOURCE' if incomplete else 'NOT_RUN_RESOURCE', 'ACQUISITION_TIME_CAP')


def _retained(cache: Path) -> int:
    total = 0
    for path in cache.rglob('*'):
        if _link(path):
            raise _Stop('NOT_RUN_CACHE', 'CACHE_CONTAINS_LINK')
        if path.is_file():
            total += path.stat().st_size
    return total


def _digest(path: Path, start: float) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(_CHUNK):
            _elapsed(start)
            digest.update(chunk)
    return digest.hexdigest()


def _reuse(target: Path, partial: Path, receipt_path: Path, receipt: dict, start: float) -> dict | None:
    if any(_link(p) for p in (target, partial, receipt_path)):
        raise _Stop('NOT_RUN_CACHE', 'SOURCE_OR_RECEIPT_IS_LINK')
    if partial.exists():
        raise _Stop('NOT_RUN_EXISTING', 'PARTIAL_PRESERVED_MANUAL_ADJUDICATION_REQUIRED')
    if not target.exists() and not receipt_path.exists():
        return None
    if not target.is_file() or not receipt_path.is_file():
        raise _Stop('NOT_RUN_EXISTING', 'COMPLETE_SOURCE_AND_RECEIPT_REQUIRED')
    try:
        recorded = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        raise _Stop('FAIL_INTEGRITY', 'UNREADABLE_EXISTING_RECEIPT') from None
    if not isinstance(recorded, dict) or recorded.get('status') != 'COMPLETE' or not recorded.get('gzip_crc_verified'):
        raise _Stop('NOT_RUN_EXISTING', 'VERIFIED_COMPLETE_RECEIPT_REQUIRED')
    for key in ('day', 'url', 'protocol_sha256', 'amendment_sha256'):
        if recorded.get(key) != receipt[key]:
            raise _Stop('FAIL_INTEGRITY', 'EXISTING_RECEIPT_IDENTITY_CHANGED')
    if target.stat().st_size > _LIMITS.file_bytes:
        raise _Stop('NOT_RUN_RESOURCE', 'EXISTING_FILE_EXCEEDS_CAP')
    digest = _digest(target, start)
    if digest != recorded.get('sha256') or target.stat().st_size != recorded.get('bytes'):
        raise _Stop('FAIL_INTEGRITY', 'EXISTING_SOURCE_CHANGED')
    if receipt.get('expected_sha256') and digest != receipt['expected_sha256']:
        raise _Stop('FAIL_INTEGRITY', 'EXPECTED_SOURCE_CHANGED')
    return dict(recorded, status='REUSED_VERIFIED', reuse_verified_utc=_utc(),
                local_verification_commit=receipt['protocol_commit'])


def _provider_headers(headers: Any) -> dict[str, str]:
    names = ('Content-Length', 'Content-Type', 'Content-Encoding', 'ETag', 'Last-Modified',
             'Content-MD5', 'Digest', 'x-amz-checksum-sha256', 'x-amz-checksum-crc32')
    return {key: str(headers[key]) for key in names if headers.get(key) is not None}


def _status_stop(status: int) -> _Stop:
    if status == 404:
        return _Stop('NOT_RUN_SOURCE_UNAVAILABLE', 'HTTP_404_NO_SUBSTITUTION')
    if status in (401, 403, 429):
        return _Stop('NOT_RUN_ACCESS', f'HTTP_{status}_STOP_NO_EVASION')
    return _Stop('NOT_RUN_HTTP', f'HTTP_{status}_NOT_COMPLETE_GZIP')


def _transfer(url: str, target: Path, partial: Path, receipt_path: Path, receipt: dict,
              cache: Path, retained: int, start: float) -> dict:
    transient = (500, 502, 503, 504)
    for attempt in range(1, 4):
        _elapsed(start)
        observation = {'attempt': attempt, 'request_utc': _utc(), 'http_status': None}
        receipt['attempts'].append(observation)
        _atomic(receipt_path, receipt)
        response = None
        try:
            try:
                response = _open(Request(url, headers={'User-Agent': _USER_AGENT,
                                                      'Accept-Encoding': 'identity'}), timeout=60)
            except HTTPError as exc:
                observation['http_status'] = exc.code
                observation['provider_headers'] = _provider_headers(exc.headers or {})
                exc.close()
                if exc.code in transient and attempt < 3:
                    _atomic(receipt_path, receipt)
                    _sleep(2 * attempt)
                    continue
                raise _status_stop(exc.code) from None
            except (URLError, TimeoutError, ConnectionError, OSError) as exc:
                observation['transport_error_type'] = type(exc).__name__
                _atomic(receipt_path, receipt)
                if attempt < 3:
                    _sleep(2 * attempt)
                    continue
                raise _Stop('INCOMPLETE_TRANSPORT', 'OPEN_RETRIES_EXHAUSTED') from None
            status = int(response.status)
            observation['http_status'] = status
            observation['provider_headers'] = _provider_headers(response.headers)
            receipt['status'] = 'HTTP_RECEIVED'
            _atomic(receipt_path, receipt)
            if response.geturl() != url:
                raise _Stop('NOT_RUN_ACCESS', 'REDIRECTED_SOURCE_REFUSED')
            if status != 200:
                if status in transient and attempt < 3:
                    _sleep(2 * attempt)
                    continue
                raise _status_stop(status)
            length = response.headers.get('Content-Length')
            if length is not None:
                if not str(length).isascii() or not str(length).isdecimal():
                    raise _Stop('FAIL_INTEGRITY', 'INVALID_CONTENT_LENGTH')
                length = int(length)
                if length > _LIMITS.file_bytes or retained + length > _LIMITS.total_bytes:
                    raise _Stop('NOT_RUN_RESOURCE', 'HTTP_CONTENT_LENGTH_EXCEEDS_CAP')
            digest = hashlib.sha256()
            receipt['partial_sha256'] = digest.hexdigest()
            try:
                with partial.open('xb') as stream:
                    while True:
                        _elapsed(start, incomplete=True)
                        chunk = response.read(_CHUNK)
                        if not chunk:
                            break
                        size = receipt['bytes'] + len(chunk)
                        if size > _LIMITS.file_bytes or retained + size > _LIMITS.total_bytes:
                            raise _Stop('INCOMPLETE_RESOURCE', 'STREAM_BYTE_CAP')
                        if shutil.disk_usage(cache).free - len(chunk) < _LIMITS.reserve_bytes:
                            raise _Stop('INCOMPLETE_RESOURCE', 'FREE_DISK_RESERVE')
                        stream.write(chunk)
                        digest.update(chunk)
                        receipt['partial_sha256'] = digest.hexdigest()
                        receipt['bytes'] = size
                    stream.flush()
                    os.fsync(stream.fileno())
            except (TimeoutError, ConnectionError, OSError, http.client.IncompleteRead) as exc:
                receipt['transport_error_type'] = type(exc).__name__
                raise _Stop('INCOMPLETE_TRANSPORT', 'BODY_INTERRUPTED_PARTIAL_PRESERVED') from None
            receipt['sha256'] = digest.hexdigest()
            if length is not None and receipt['bytes'] != length:
                raise _Stop('FAIL_INTEGRITY', 'CONTENT_LENGTH_MISMATCH')
            if receipt['expected_sha256'] and receipt['sha256'] != receipt['expected_sha256']:
                raise _Stop('FAIL_INTEGRITY', 'EXPECTED_SHA256_MISMATCH')
            if receipt['bytes'] < 20:
                raise _Stop('FAIL_INTEGRITY', 'BODY_TOO_SHORT_FOR_GZIP')
            try:
                with gzip.open(partial, 'rb') as stream:
                    while stream.read(_CHUNK):
                        _elapsed(start, incomplete=True)
            except (gzip.BadGzipFile, EOFError, zlib.error, OSError):
                raise _Stop('FAIL_INTEGRITY', 'GZIP_DECOMPRESSION_OR_CRC_FAILED') from None
            receipt['gzip_crc_verified'] = True
            receipt['status'] = 'VERIFIED_PENDING_RENAME'
            _atomic(receipt_path, receipt)
            if target.exists():
                raise _Stop('NOT_RUN_EXISTING', 'TARGET_APPEARED_PARTIAL_PRESERVED')
            os.replace(partial, target)
            receipt.update(status='COMPLETE', completed_utc=_utc())
            _atomic(receipt_path, receipt)
            return receipt
        finally:
            if response is not None:
                response.close()
    raise _Stop('INCOMPLETE_TRANSPORT', 'RETRIES_EXHAUSTED')


def download_day(day: str | date, destination: str | Path, *, protocol_commit: str,
                 expected_sha256: str | None = None, allow_year: int = 2023) -> dict:
    """Download one fixed monthly first day into an external private cache.

    Default accepts only 2023 development. `allow_year=2024` or `2025` is an
    explicit caller assertion, NOT evidence of development/validation sign-off.
    The orchestrator must verify immutable stage, rights and public-freeze receipts
    before calling. All days must share one cache for the retained-byte cap.
    The 120-minute deadline is per call, checked between bounded operations;
    the orchestrator must enforce the separate cumulative campaign time cap.
    Existing partials and changed files require manual adjudication.
    Three opening attempts maximum, with 2/4 second backoff; interrupted bodies
    are preserved and never silently retried or replaced. No CSV values are read.
    """
    receipt = {'status': 'NOT_STARTED', 'started_utc': _utc(), 'attempts': [], 'bytes': 0,
               'sha256': None, 'gzip_crc_verified': False,
               'protocol_commit': protocol_commit, 'expected_sha256': expected_sha256,
               'freeze_verification': 'LOCAL_COMMIT_CONTENT_ONLY_PUBLICATION_NOT_PROVEN',
               'stage_authorization': 'DEVELOPMENT_ONLY' if allow_year == 2023 else 'CALLER_EXPLICIT_YEAR_ONLY'}
    receipt_path = None
    owned_receipt = False
    lock = None
    lock_owned = False
    start = _clock()
    try:
        try:
            parsed = date.fromisoformat(day) if isinstance(day, str) else day
            if type(parsed) is not date or str(parsed) != str(day) or parsed.year not in (2023, 2024, 2025) or parsed.day != 1:
                raise ValueError
        except (ValueError, TypeError):
            raise _Stop('NOT_RUN_DATE', 'ONLY_FIXED_36_MONTHLY_FIRST_DAYS') from None
        if type(allow_year) is not int or allow_year != parsed.year:
            raise _Stop('NOT_RUN_STAGE', 'EXPLICIT_MATCHING_YEAR_REQUIRED')
        if expected_sha256 is not None and (not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256)):
            raise _Stop('FAIL_INTEGRITY', 'EXPECTED_SHA256_MUST_BE_64_LOWERCASE_HEX')
        freeze = _freeze(protocol_commit)
        receipt.update(day=str(parsed), protocol_sha256=freeze[_PROTOCOL], amendment_sha256=freeze[_AMENDMENT],
                       protocol_commit_utc=freeze['commit_utc'])
        url = f'https://datasets.tardis.dev/v1/binance/book_ticker/{parsed:%Y/%m/%d}/BTCUSDT.csv.gz'
        cache = _cache(Path(destination))
        target = cache / f'binance_book_ticker_{parsed}_BTCUSDT.csv.gz'
        partial = Path(str(target) + '.partial')
        receipt_path = Path(str(target) + '.receipt.json')
        receipt.update(url=url, path=str(target), partial_path=str(partial), receipt_path=str(receipt_path))
        lock = cache / '.bbo-acquisition.lock'
        if _link(lock):
            raise _Stop('NOT_RUN_CACHE', 'CACHE_LOCK_IS_LINK')
        try:
            with lock.open('x') as stream:
                stream.write('serial native-BBO acquisition\n')
                lock_owned = True
        except FileExistsError:
            lock = None
            raise _Stop('NOT_RUN_CONCURRENT', 'CACHE_LOCK_EXISTS_MANUAL_ADJUDICATION_REQUIRED') from None
        retained = _retained(cache)
        if retained > _LIMITS.total_bytes:
            raise _Stop('NOT_RUN_RESOURCE', 'RETAINED_CACHE_CAP')
        reused = _reuse(target, partial, receipt_path, receipt, start)
        if reused is not None:
            return reused
        if retained + _LIMITS.file_bytes > _LIMITS.total_bytes:
            raise _Stop('NOT_RUN_RESOURCE', 'RETAINED_CACHE_CAP')
        if shutil.disk_usage(cache).free < _LIMITS.reserve_bytes + _LIMITS.file_bytes:
            raise _Stop('NOT_RUN_RESOURCE', 'FREE_DISK_RESERVE_PLUS_FILE_CAP_REQUIRED')
        _elapsed(start)
        receipt['status'] = 'STARTED'
        owned_receipt = True
        _atomic(receipt_path, receipt)
        return _transfer(url, target, partial, receipt_path, receipt, cache, retained, start)
    except _Stop as exc:
        receipt.update(status=exc.status, reason=exc.reason, stopped_utc=_utc())
    except (OSError, subprocess.SubprocessError) as exc:
        receipt.update(status='INCOMPLETE_LOCAL', reason='LOCAL_IO_OR_GIT_FAILURE',
                       error_type=type(exc).__name__, stopped_utc=_utc())
    finally:
        if owned_receipt and receipt_path is not None and receipt['status'] != 'COMPLETE':
            try:
                _atomic(receipt_path, receipt)
            except OSError:
                receipt['checkpoint_write_failed'] = True
        if lock_owned and lock is not None:
            try:
                lock.unlink(missing_ok=True)
            except OSError:
                receipt['lock_cleanup_failed'] = True
    return receipt
