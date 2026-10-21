"""Verify declared evidence, create a deterministic closeout, or verify a closeout."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from srl.evidence import load_manifest, pack, verify_manifest, verify_pack


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('verify', 'pack'):
        child = commands.add_parser(command)
        child.add_argument('manifest', type=Path)
        child.add_argument('--root', type=Path, default=ROOT)
        child.add_argument('--previous', type=Path, help='trusted prior role ledger; retain successive ledgers')
        if command == 'pack':
            child.add_argument('output', type=Path)
    closeout = commands.add_parser('verify-pack')
    closeout.add_argument('archive', type=Path)
    closeout.add_argument('--sha256', help='trusted external archive digest, independent of its internal hashes')
    args = parser.parse_args()
    try:
        if args.command == 'verify-pack':
            result = verify_pack(args.archive, expected_sha256=args.sha256)
        else:
            raw = load_manifest(args.manifest)
            previous = load_manifest(args.previous) if args.previous else None
            result = verify_manifest(args.root, raw, previous=previous)
            if args.command == 'pack':
                pack(args.root, raw, args.output, previous=previous)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    print(f'PASS: {len(result.evidence)} evidence files; {len(result.claims)} declared claims. '
          'Integrity and declared-policy checks only; no authentication of historical truth.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
