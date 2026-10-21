"""Explicit offline private BBO replay; never downloads provider data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))

from srl.bbo_runner import run_day  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--day', required=True)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--protocol-commit', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--implementation-commit')
    args = parser.parse_args()
    try:
        receipt = run_day(args.raw, day=args.day, output=args.output,
                          protocol_commit=args.protocol_commit, expected_sha256=args.sha256,
                          implementation_commit=args.implementation_commit)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'NOT_RUN', 'error_type': type(exc).__name__, 'reason': str(exc)}))
        return 2
    # This receipt contains identities and operational data, no individual quotes/costs.
    print(json.dumps(receipt, sort_keys=True, allow_nan=False))
    return 0 if receipt['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
