"""Run the complete suite and replay the original synthetic experiment offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

from scripts.audit_public import audit_directory, safe_name
from srl.study import load_protocol, run_study
from srl.visuals import render_summary


def artifact_bytes(root: Path) -> dict[str, bytes]:
    result = run_study(load_protocol(root / 'experiments/protocol.json'))
    return {'results/study.json': (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n').encode(),
            'figures/research-summary.svg': render_summary(result).encode('utf-8')}


def check_artifacts(root: Path, artifacts: dict[str, bytes]) -> list[str]:
    return [name for name, payload in artifacts.items()
            if not (root / name).is_file() or (root / name).read_bytes() != payload]


def write_output(destination: Path, artifacts: dict[str, bytes], source: dict) -> dict:
    if destination.exists() or destination.is_symlink():
        raise ValueError('choose a new output directory; existing work is preserved')
    if any(not safe_name(name) or not isinstance(payload, bytes) for name, payload in artifacts.items()):
        raise ValueError('artifact names must be safe relative paths with byte payloads')
    receipt = {'scope': 'SYNTHETIC_ONLY', 'python': platform.python_version(), 'source_sha256': source,
               'artifacts': {name: hashlib.sha256(payload).hexdigest() for name, payload in artifacts.items()}}
    destination.mkdir(parents=True)
    for name, payload in artifacts.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    (destination / 'reproduction-receipt.json').write_bytes(
        (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode())
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify checked-in artifact bytes (also the default)')
    parser.add_argument('--output', type=Path, help='optionally write artifacts and hashes into a new directory')
    args = parser.parse_args()
    # Discovering with an explicit project root also works in a fresh source clone.
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    tested = unittest.TextTestRunner(verbosity=2).run(suite)
    if not tested.wasSuccessful():
        return 1
    audit = audit_directory(ROOT)
    if audit['status'] != 'PASS':
        print(json.dumps({'audit': audit}, indent=2, sort_keys=True))
        return 1
    artifacts = artifact_bytes(ROOT)
    differences = check_artifacts(ROOT, artifacts)
    if differences:
        print(json.dumps({'artifact_mismatch': differences}, indent=2))
        return 1
    receipt = {'status': 'PASS', 'scope': 'SYNTHETIC_ONLY', 'python': platform.python_version(),
               'tests': tested.testsRun, 'skipped': len(tested.skipped),
               'source_files': len(audit['files']),
               'artifacts': {name: hashlib.sha256(payload).hexdigest() for name, payload in artifacts.items()}}
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT) and not target.is_relative_to(ROOT / 'build'):
            raise ValueError('in-repository output must be under ignored build/')
        write_output(target, artifacts, audit['files'])
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
