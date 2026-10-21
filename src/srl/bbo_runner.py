"""Offline day replay with external private artifacts and fail-closed receipts.

No network access. Local Git checks establish content identity, not publication.
Validation/final replay requires frozen implementation and preceding closeouts.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import time
from typing import Any, Callable, Iterator

from srl.bbo import QuoteCounts, QuoteUpdate, iter_updates
from srl.bbo_acquire import ROOT, _atomic, _cache, _freeze, _git
from srl.bbo_replay import replay_updates
from srl.bbo_stage import verify_stage

METHOD_FILES = tuple(f'src/srl/{name}.py' for name in (
    'bbo', 'bbo_acquire', 'bbo_accounting', 'bbo_history', 'bbo_replay', 'bbo_statistics',
    'bbo_runner', 'bbo_stage', 'block_means', 'resampling')) + ('scripts/bbo_run_day.py',)
MEMORY_CAP = 2 * 1024**3
OUTPUT_CAP = 2 * 1024**3
TIME_CAP = 120 * 60


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rss() -> int:
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                        *[(name, ctypes.c_size_t) for name in (
                            'PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
                            'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        process = ctypes.windll.kernel32.GetCurrentProcess
        process.restype = wintypes.HANDLE
        measure = ctypes.windll.psapi.GetProcessMemoryInfo
        measure.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        measure.restype = wintypes.BOOL
        if not measure(process(), ctypes.byref(counters), counters.cb):
            raise OSError('cannot measure process memory')
        return int(counters.PeakWorkingSetSize)
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == 'darwin' else peak * 1024)


def _hash(path: Path, check: Callable[[], None] | None = None) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1 << 20):
            if check is not None:
                check()
            result.update(chunk)
    return result.hexdigest()


def run_day(raw: Path, *, day: str, output: Path, protocol_commit: str,
            expected_sha256: str, implementation_commit: str | None = None,
            stage_commit: str | None = None) -> dict[str, Any]:
    """Keep every scheduled audit row private; publish no partial day on failure.

    The caller must enforce cumulative campaign time/output limits across days.
    This worker additionally checks its own limits at bounded row intervals.
    An existing run directory is never reused, even after interruption.
    """
    parsed = date.fromisoformat(day)
    if parsed.isoformat() != day or parsed.day != 1 or parsed.year not in (2023, 2024, 2025):
        raise ValueError('only the frozen 36 monthly first days are permitted')
    stage_proof: dict[str, Any] = {'stage': 'DEVELOPMENT', 'verification': 'DEVELOPMENT_ONLY'}
    if parsed.year != 2023:
        if implementation_commit is None or stage_commit is None:
            raise ValueError('later stages require immutable implementation and preceding closeout')
        stage_proof = verify_stage(ROOT, day=day, implementation_commit=implementation_commit,
                                   stage_commit=stage_commit)
    if not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('exact lowercase SHA256 required')
    if output.exists():
        raise ValueError('existing run directory preserved; choose a new version')
    freeze = _freeze(protocol_commit)
    raw = raw.absolute()
    # Validate both paths against links/Git without creating or copying raw data.
    _cache(raw.parent)
    if raw.is_symlink() or not raw.is_file() or raw.is_junction():
        raise ValueError('regular external raw file required')
    output = _cache(output.parent) / output.name
    output.mkdir(exist_ok=False)
    started = time.monotonic()
    counts = QuoteCounts()
    methods = {name: _hash(ROOT / name) for name in METHOD_FILES}
    receipt: dict[str, Any] = dict(
        status='RUNNING', day=day, started_utc=_utc(), pid=os.getpid(),
        protocol_commit=protocol_commit, protocol_freeze=freeze,
        freeze_verification='LOCAL_CONTENT_ONLY_PUBLICATION_VERIFIED_BY_ORCHESTRATOR',
        implementation_commit=implementation_commit, stage_commit=stage_commit, stage_proof=stage_proof,
        method_sha256=methods, expected_sha256=expected_sha256,
        python=sys.version, platform=platform.platform(),
        source_url=f'https://datasets.tardis.dev/v1/binance/book_ticker/{parsed:%Y/%m/%d}/BTCUSDT.csv.gz',
        artifacts_sha256={}, resource_limits=dict(resident_bytes=MEMORY_CAP,
                                                  temporary_bytes=OUTPUT_CAP, seconds=TIME_CAP))
    receipt_path = output / 'receipt.json'
    _atomic(receipt_path, receipt)
    peak = 0

    def check() -> None:
        nonlocal peak
        peak = max(peak, _rss())
        if peak > MEMORY_CAP or time.monotonic() - started > TIME_CAP:
            raise ValueError('analysis resource cap exceeded')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) > OUTPUT_CAP:
            raise ValueError('private output cap exceeded')
        if shutil.disk_usage(output).free < 5 * 1024**3:
            raise ValueError('free disk reserve violated')

    try:
        check()
        if implementation_commit is not None:
            for name in METHOD_FILES:
                if _git(ROOT, 'show', f'{implementation_commit}:{name}') != (ROOT/name).read_bytes():
                    raise ValueError('implementation differs from specified local freeze')
        receipt['raw_bytes'] = raw.stat().st_size
        if receipt['raw_bytes'] > 2 * 1024**3:
            raise ValueError('compressed source exceeds file cap')
        receipt['raw_sha256'] = _hash(raw, check)
        if receipt['raw_sha256'] != expected_sha256:
            raise ValueError('compressed source SHA256 mismatch')
        # Exact sources used for an uncommitted development run remain private.
        snapshot = output / 'method-source'
        snapshot.mkdir()
        for name in METHOD_FILES:
            (snapshot / Path(name).name).write_bytes((ROOT/name).read_bytes())
        start = int(datetime(parsed.year, parsed.month, 1, tzinfo=timezone.utc).timestamp()) * 1_000_000
        with gzip.open(raw, 'rt', encoding='utf-8', newline='') as source:
            def bounded_lines() -> Iterator[str]:
                index = 0
                while True:
                    # Count input lines, not emitted states: timestamp groups may be huge.
                    if index % 16384 == 0:
                        check()
                    # Bound allocation before CSV field validation, including gzip bombs.
                    line = source.readline((1 << 20) + 1)
                    if not line:
                        break
                    if len(line) > 1 << 20:
                        raise ValueError('resource limit: raw line exceeds 1Mi characters')
                    index += 1
                    yield line

            def bounded() -> Iterator[QuoteUpdate]:
                for index, update in enumerate(iter_updates(bounded_lines(), day=day, counts=counts)):
                    if index % 16384 == 0:
                        check()
                    yield update

            with gzip.open(output / 'audit.jsonl.gz', 'wt', encoding='utf-8', newline='\n') as audit:
                audit_count = 0

                def emit(row: dict[str, Any]) -> None:
                    nonlocal audit_count
                    audit.write(json.dumps(row, sort_keys=True, allow_nan=False, separators=(',', ':'))+'\n')
                    audit_count += 1
                    if audit_count % 4096 == 0:
                        check()

                result = replay_updates(bounded(), start_us=start, audit=emit)
        if audit_count != result.report['scheduled_intents']:
            raise ValueError('private audit does not reconcile scheduled intents')
        # The complete gzip/CSV was consumed; no prefix can become a report.
        check()
        for name in METHOD_FILES:
            if _hash(ROOT/name) != methods[name]:
                raise ValueError('method changed during replay')
        if _hash(raw, check) != expected_sha256:
            raise ValueError('raw source changed during replay')
        with gzip.open(output/'savings.json.gz', 'wt', encoding='utf-8', newline='\n') as stream:
            json.dump(result.savings, stream, sort_keys=True, allow_nan=False)
            stream.write('\n')
        check()
        _atomic(output/'report.json', dict(result.report, day=day, quote_counts=asdict(counts)))
        check()
        artifacts = {str(p.relative_to(output)).replace('\\', '/'): _hash(p)
                     for p in output.rglob('*') if p.is_file() and p != receipt_path}
        receipt.update(status='COMPLETE', artifacts_sha256=artifacts, audit_rows=audit_count,
                       gzip_crc_verified=True)
        _atomic(receipt_path, receipt)
        check()
    except Exception as exc:
        # An unexpected ordinary error or MemoryError also invalidates the whole run.
        # This directory belongs to this invocation; no earlier run is overwritten.
        (output/'report.json').unlink(missing_ok=True)
        receipt.update(status='FAILED', error_type=type(exc).__name__, reason=str(exc))
    except BaseException:
        (output/'report.json').unlink(missing_ok=True)
        receipt.update(status='INTERRUPTED', reason='INTERRUPTED_NO_COMPLETED_REPORT')
        raise
    finally:
        receipt.update(completed_utc=_utc(), elapsed_seconds=time.monotonic()-started,
                       peak_resident_bytes=peak, quote_counts=asdict(counts))
        _atomic(receipt_path, receipt)
    return receipt
