"""Replay original BBO history support using a privately downloaded file."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from srl.bbo import qualify_day


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-file', type=Path, required=True, help='provider file outside this repository')
    parser.add_argument('--day', required=True, help='canonical UTC day')
    parser.add_argument('--check', type=Path, help='compare every result field with a retained public receipt')
    args = parser.parse_args()
    raw = args.raw_file.resolve()
    if raw.is_relative_to(ROOT) or not raw.is_file():
        parser.error('raw input must be an existing private file outside the repository')
    result = qualify_day(raw, day=args.day)
    result['method_sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                               for name in ('src/srl/bbo.py', 'scripts/bbo_qualify.py')}
    if args.check and json.loads(args.check.read_text(encoding='utf-8')) != result:
        print(json.dumps({'status': 'FAIL_REPLAY_IDENTITY_OR_RESULT'}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
