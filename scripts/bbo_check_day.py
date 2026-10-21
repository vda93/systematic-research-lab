"""Compare an offline private day replay to its checked public aggregate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_day(run: Path, checked: Path) -> list[str]:
    expected = json.loads(checked.read_text(encoding='utf-8'))
    report = json.loads((run/'report.json').read_text(encoding='utf-8'))
    receipt = json.loads((run/'receipt.json').read_text(encoding='utf-8'))
    findings = []
    if receipt['status'] != 'COMPLETE':
        findings.append('private replay is incomplete')
    if report != expected['report']:
        findings.append('coarse report differs')
    for name in ('raw_sha256', 'method_sha256'):
        if receipt[name] != expected[name]:
            findings.append(f'{name} differs')
    for name, digest in expected['method_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            findings.append(f'current method differs: {name}')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-directory', type=Path, required=True)
    parser.add_argument('--check', type=Path, required=True)
    args = parser.parse_args()
    findings = check_day(args.run_directory, args.check)
    print(json.dumps(dict(status='FAIL' if findings else 'PASS', findings=findings)))
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
