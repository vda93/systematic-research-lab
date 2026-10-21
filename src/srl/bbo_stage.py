"""Local immutable stage gates, not proof of publication or independent review.

The caller separately verifies the commits are public BEFORE later-sample GETs.
Closeout fields are explicit accountable assertions; hashes cannot authenticate
human review, rights, elapsed work, or an unobserved provider-access history.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from srl.bbo_acquire import _git, _Stop

REQUIRED_FILES = tuple(f'src/srl/{name}.py' for name in (
    'bbo', 'bbo_acquire', 'bbo_accounting', 'bbo_history', 'bbo_replay',
    'bbo_statistics', 'bbo_report', 'bbo_runner', 'bbo_stage', 'block_means', 'resampling')) + (
    'scripts/bbo_run_day.py', 'scripts/bbo_check_day.py', 'scripts/bbo_summarize.py',
    'pyproject.toml', 'requirements-lock.txt',
    *(f'tests/test_{name}.py' for name in (
        'bbo', 'bbo_acquire', 'bbo_accounting', 'bbo_history', 'bbo_replay',
        'bbo_statistics', 'bbo_report', 'bbo_runner', 'bbo_stage', 'bbo_check_day', 'bbo_summarize')))
PROTOCOL_COMMIT = '76c8952ac6a18b6ab167878974f9cf2b4bad89c9'


def _result(root: Path, commit: str, record: dict[str, Any], stage: str, year: int) -> int:
    if record.get('protocol_commit') != PROTOCOL_COMMIT:
        raise ValueError('closeout must name the exact frozen measurement protocol')
    payload = _git(root, 'show', f'{commit}:data/bbo-{stage}-results.json')
    if hashlib.sha256(payload).hexdigest() != record.get('results_sha256'):
        raise ValueError('closeout results are not hash-bound')
    result = json.loads(payload)
    if not isinstance(result, dict) or result.get('protocol_commit') != PROTOCOL_COMMIT:
        raise ValueError('result protocol identity differs')
    report = result.get('report', {})
    if not isinstance(report, dict) or report.get('stage') != stage:
        raise ValueError('preceding result has wrong stage')
    rows = report.get('days')
    planned = [f'{year}-{month:02}-01' for month in range(1, 13)]
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('complete planned-day accounting required')
    if [row.get('day') for row in rows] != planned:
        raise ValueError('all twelve days must appear chronologically')
    sources = result.get('day_sources')
    complete = [row for row in rows if row.get('status') == 'COMPLETE']
    if not isinstance(sources, dict) or set(sources) != {row['day'] for row in complete}:
        raise ValueError('completed days require exact source identity coverage')
    paired = 0
    for row in rows:
        day = row['day']
        if row.get('status') == 'MISSING':
            if row.get('reason') not in {'SOURCE_UNAVAILABLE', 'FAIL_INTEGRITY', 'NOT_RUN_FOLLOWING_STOP', 'MISSING_REPORT'}:
                raise ValueError('reviewed missing-reason code required')
            continue
        if row.get('status') != 'COMPLETE':
            raise ValueError('unknown preceding-day status')
        count = row.get('paired_shocks')
        if type(count) is not int or count < 0:
            raise ValueError('nonnegative paired shock count required')
        paired += count
        source = sources[day]
        if not isinstance(source, dict) or not re.fullmatch('[0-9a-f]{64}', str(source.get('raw_sha256', ''))):
            raise ValueError('exact compressed source digest required')
        expected_url = f'https://datasets.tardis.dev/v1/binance/book_ticker/{day.replace("-", "/")}/BTCUSDT.csv.gz'
        if source.get('source_url') != expected_url:
            raise ValueError('source URL differs from frozen day/venue/asset')
    return paired


def verify_stage(root: Path, *, day: str, implementation_commit: str,
                 stage_commit: str) -> dict[str, Any]:
    """Reject unfrozen methods or absent/failed preceding-stage closeouts.

    Validation requires positive usable development count, never positive effect.
    Final additionally requires an immutable validation closeout. Current files
    and the implementation commit must both match every required source/test hash.
    """
    parsed = date.fromisoformat(day)
    if str(parsed) != day or parsed.day != 1 or parsed.year not in (2024, 2025):
        raise ValueError('fixed validation/final monthly first day required')
    for commit in (implementation_commit, stage_commit):
        if not re.fullmatch('[0-9a-f]{40}', commit):
            raise ValueError('exact lowercase local commit required')
    try:
        _git(root, 'merge-base', '--is-ancestor', implementation_commit, stage_commit)
        closeouts = [('data/bbo-development-closeout.json', 'READY_FOR_VALIDATION')]
        if parsed.year == 2025:
            closeouts.append(('data/bbo-validation-closeout.json', 'READY_FOR_FINAL'))
        for name, status in closeouts:
            record = json.loads(_git(root, 'show', f'{stage_commit}:{name}'))
            if not isinstance(record, dict):
                raise ValueError('closeout must be a JSON object')
            if record.get('status') != status or record.get('correctness_verified') is not True:
                raise ValueError('preceding closeout has not passed correctness/usability signoff')
            if status == 'READY_FOR_VALIDATION':
                paired = _result(root, stage_commit, record, 'development', 2023)
                count = record.get('usable_price_paired_shocks')
                if type(count) is not int or count <= 0 or count != paired:
                    raise ValueError('development must have usable price-paired shocks')
            else:
                _result(root, stage_commit, record, 'validation', 2024)
            hashes = record.get('method_sha256')
            if not isinstance(hashes, dict) or set(hashes) != set(REQUIRED_FILES):
                raise ValueError('complete source/test hash manifest required')
            for source in REQUIRED_FILES:
                committed = _git(root, 'show', f'{implementation_commit}:{source}')
                current = (root/source).read_bytes()
                if committed != current or hashlib.sha256(committed).hexdigest() != hashes[source]:
                    raise ValueError('current/committed implementation differs from stage freeze')
    except (_Stop, OSError, json.JSONDecodeError) as exc:
        raise ValueError('immutable stage proof unavailable') from exc
    return dict(stage='VALIDATION' if parsed.year == 2024 else 'FINAL',
                implementation_commit=implementation_commit, stage_commit=stage_commit,
                publication_verified=False, verification='LOCAL_CONTENT_AND_ASSERTED_CLOSEOUT_ONLY')
