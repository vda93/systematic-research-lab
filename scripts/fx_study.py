"""Offline ECB reference-study replay; explicit gated one-time acquisition."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from srl.fx_study import SOURCE_URL, result_bytes, run_study, selected_archive

FROZEN_FILES = ('src/srl/fx_study.py', 'scripts/fx_study.py', 'tests/test_fx_study.py',
                'experiments/ecb-fx-mom20-protocol.md', 'DATA_LICENSE.md')


def freeze_identity(commit: str, rights_reviewed: bool) -> dict:
    """Fail before network access unless all method files match exact HEAD."""
    if not rights_reviewed or not re.fullmatch('[0-9a-f]{40}', commit or ''):
        raise ValueError('acquisition requires --rights-reviewed and a full frozen --freeze-commit')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(ROOT), *args])
    if git('rev-parse', 'HEAD').decode().strip() != commit:
        raise ValueError('frozen commit must equal current HEAD')
    identities = {}
    for name in FROZEN_FILES:
        frozen = git('show', f'{commit}:{name}')
        current = (ROOT / name).read_bytes()
        if frozen != current:
            raise ValueError(f'method file differs from frozen commit: {name}')
        identities[name] = sha256(current).hexdigest()
    return {'protocol_commit': commit, 'frozen_file_sha256': identities}


def acquire(raw_zip: Path, snapshot: Path, commit: str, rights_reviewed: bool) -> dict:
    identity = freeze_identity(commit, rights_reviewed)
    raw_zip, snapshot = raw_zip.resolve(), snapshot.resolve()
    receipt_path = raw_zip.with_suffix(raw_zip.suffix + '.receipt.json')
    if raw_zip.is_relative_to(ROOT):
        raise ValueError('raw archive must be outside this repository')
    if raw_zip.exists() or snapshot.exists() or receipt_path.exists():
        raise ValueError('acquisition will not overwrite archive, snapshot or receipt')
    if not raw_zip.parent.is_dir() or not snapshot.parent.is_dir():
        raise ValueError('choose existing archive and snapshot parent directories')
    # urllib uses normal certificate verification. No credentials or API key.
    with urlopen(Request(SOURCE_URL, headers={'User-Agent': 'systematic-research-lab/2'}), timeout=60) as response:
        if response.status != 200 or response.geturl() != SOURCE_URL:
            raise ValueError('unexpected provider status or redirect')
        payload = response.read(10_000_001)
        headers = {key: response.headers.get(key) for key in ('Content-Type', 'Last-Modified', 'ETag')}
    if len(payload) > 10_000_000:
        raise ValueError('archive exceeds frozen acquisition size limit')
    # Preserve original bytes outside Git even if subsequent qualification fails.
    with raw_zip.open('xb') as handle:
        handle.write(payload)
    selected, qualification = selected_archive(payload)
    receipt = {**identity, **qualification, 'source_url': SOURCE_URL,
               'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'provider_headers': headers,
               'rights_reviewed': True, 'data_license': 'ECB_FREE_USE_CONDITIONS_NOT_SOFTWARE_LICENSE'}
    with receipt_path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(receipt, handle, sort_keys=True, indent=2)
        handle.write('\n')
    with snapshot.open('xb') as handle:
        handle.write(selected)
    return receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true', help='default: offline exact JSON replay')
    actions.add_argument('--write', action='store_true', help='write a previously absent result JSON, offline')
    actions.add_argument('--acquire', action='store_true', help='explicit one-time provider acquisition after freeze')
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'data/ecb-fx-reference.csv')
    parser.add_argument('--results', type=Path, default=ROOT / 'data/ecb-fx-results.json')
    parser.add_argument('--raw-zip', type=Path)
    parser.add_argument('--freeze-commit')
    parser.add_argument('--rights-reviewed', action='store_true')
    args = parser.parse_args(argv)
    if args.acquire:
        if args.raw_zip is None:
            parser.error('--acquire requires --raw-zip outside the repository')
        receipt = acquire(args.raw_zip, args.snapshot, args.freeze_commit, args.rights_reviewed)
        print(json.dumps(receipt, sort_keys=True, indent=2))
        return 0
    if args.raw_zip or args.freeze_commit or args.rights_reviewed:
        parser.error('acquisition options require --acquire')
    if not args.snapshot.is_file():
        raise ValueError('frozen snapshot missing; default replay never downloads data')
    expected = result_bytes(run_study(args.snapshot.read_bytes()))
    if args.write:
        with args.results.open('xb') as handle:
            handle.write(expected)
    elif not args.results.is_file() or args.results.read_bytes() != expected:
        print(json.dumps({'status': 'FAIL', 'reason': 'RESULT_BYTES_MISMATCH_OR_MISSING'}))
        return 1
    print(json.dumps({'status': 'PASS', 'mode': 'OFFLINE_REFERENCE_STUDY',
                      'source_csv_sha256': sha256(args.snapshot.read_bytes()).hexdigest(),
                      'result_sha256': sha256(expected).hexdigest()}, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ECB study blocked: {exc}', file=sys.stderr)
        raise SystemExit(1)
