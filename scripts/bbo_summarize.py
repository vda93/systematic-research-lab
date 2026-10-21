"""Offline BBO stage aggregation from external private replay runs.

Reproduce a checked aggregate without downloading anything:
    python scripts/bbo_summarize.py --runs PRIVATE_RUNS --stage development --check data/bbo-development-results.json

Only the bounded PASS/FAIL summary is printed. Private audit rows, sample vectors
and filesystem paths are never printed or embedded in the aggregate envelope.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from typing import Any
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from srl.bbo_report import aggregate_stage  # noqa: E402

PROTOCOL_COMMIT = '76c8952ac6a18b6ab167878974f9cf2b4bad89c9'
CORE_FILES = tuple(f'src/srl/{name}.py' for name in
                  ('bbo','bbo_accounting','bbo_history','bbo_replay','bbo_statistics','block_means','resampling'))
_AGGREGATION = 'src/srl/bbo_report.py'
_YEARS = {'development':2023,'validation':2024,'final':2025}
_REQUIRED_ARTIFACTS = {'report.json','savings.json.gz','audit.jsonl.gz'}
_SCOPE = ('Calculation identity covers only the seven scientific core files; runner, acquisition and CLI controls '
          'are operational and excluded. Aggregation identity separately binds bbo_report.py. Receipt metadata '
          'and local artifact hashes do not authenticate provider history, actual audit-row execution or rights.')


def _hash(path: Path) -> str:
    result=hashlib.sha256()
    with path.open('rb') as stream:
        while chunk:=stream.read(1<<20):
            result.update(chunk)
    return result.hexdigest()


def _links(path: Path) -> None:
    if any(p.is_symlink() or p.is_junction() for p in (path,*path.parents)):
        raise ValueError('links or junctions are not permitted')


def _regular(path: Path) -> None:
    _links(path)
    if not path.exists() or not stat.S_ISREG(path.stat().st_mode) or path.stat().st_nlink!=1:
        raise ValueError('single-link regular artifact required')


def _external(path: Path) -> Path:
    absolute=path.absolute()
    _links(absolute)
    resolved=absolute.resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        raise ValueError('private artifacts must remain outside the public checkout')
    existing=resolved
    while not existing.exists():
        existing=existing.parent
    if not existing.is_dir():
        existing=existing.parent
    result=subprocess.run(['git','-C',str(existing),'rev-parse','--show-toplevel'],
                          capture_output=True,timeout=15)
    if result.returncode==0:
        raise ValueError('private artifacts must remain outside every Git checkout')
    return resolved


def _digest(value: Any) -> str:
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):
        raise ValueError('lowercase SHA256 identity required')
    return value


def _count(value: Any) -> int:
    if type(value) is not int or value<0:
        raise ValueError('nonnegative integer count required')
    return value


def _unique(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field is not permitted')
        result[key]=value
    return result


def _constant(value: str) -> Any:
    raise ValueError('nonfinite JSON constant is not permitted')


def _json(path: Path, *, compressed: bool=False) -> dict[str,Any]:
    _regular(path)
    try:
        if compressed:
            with gzip.open(path,'rt',encoding='utf-8') as stream:
                result=json.load(stream,object_pairs_hook=_unique,parse_constant=_constant)
        else:
            result=json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=_unique,parse_constant=_constant)
    except (OSError,EOFError,UnicodeError,zlib.error,RecursionError) as exc:
        raise ValueError('artifact cannot be decoded completely') from exc
    if not isinstance(result,dict):
        raise ValueError('JSON artifact must be an object')
    return result


def _artifact_paths(run: Path, manifest: Any) -> dict[str,str]:
    if not isinstance(manifest,dict) or not _REQUIRED_ARTIFACTS<=set(manifest):
        raise ValueError('complete required artifact manifest is missing')
    checked={}
    for name,digest in manifest.items():
        if not isinstance(name,str) or '\\' in name or ':' in name:
            raise ValueError('unsafe artifact path')
        relative=PurePosixPath(name)
        if (not name or relative.is_absolute() or relative.as_posix()!=name or name=='receipt.json'
            or any(part in ('.','..') for part in relative.parts)):
            raise ValueError('unsafe artifact path')
        path=run.joinpath(*relative.parts)
        _regular(path)
        if _hash(path)!=_digest(digest):
            raise ValueError('replay artifact digest changed')
        checked[name]=digest
    actual=set()
    for path in run.rglob('*'):
        _links(path)
        if path.is_dir():
            continue
        _regular(path)
        if path!=run/'receipt.json':
            actual.add(path.relative_to(run).as_posix())
    if actual!=set(checked):
        raise ValueError('receipt artifact inventory is incomplete or changed')
    return checked


def load_stage(runs: Path, stage: str, *, external_gates_passed: bool=False) -> dict[str,Any]:
    """Verify every present v1 run, then aggregate all twelve planned days.

    Missing directories become MISSING_REPORT. An existing incomplete, unbound or
    changed run invalidates the entire call; no favorable prefix is salvaged.
    Receipts declare source identities/audit counts, not authenticated historical
    provider provenance. The caller independently enforces rights, complete replay,
    immutable stage gates and campaign resources before asserting external gates.
    This function consumes saved private cost samples, never raw quote CSV/audits.
    """
    if stage not in _YEARS or type(external_gates_passed) is not bool:
        raise ValueError('known stage and boolean gate assertion required')
    runs=_external(Path(runs))
    if not runs.is_dir():
        raise ValueError('existing external runs directory required')
    planned=[f'{_YEARS[stage]}-{month:02d}-01' for month in range(1,13)]
    core={name:_hash(ROOT/name) for name in CORE_FILES}
    aggregate_hash=_hash(ROOT/_AGGREGATION)
    reports,samples,sources={},{},{}
    verified: list[tuple[Path,str,dict[str,str]]]=[]
    for day in planned:
        run=runs/f'{day}-v1'
        _links(run)
        if not run.exists():
            continue
        if not run.is_dir():
            raise ValueError('planned run is not a directory')
        receipt=_json(run/'receipt.json')
        receipt_hash=_hash(run/'receipt.json')
        if receipt.get('status')!='COMPLETE' or receipt.get('protocol_commit')!=PROTOCOL_COMMIT:
            raise ValueError('present replay is incomplete or has another frozen protocol')
        if receipt.get('gzip_crc_verified') is not True or _count(receipt.get('audit_rows'))!=86099:
            raise ValueError('complete CRC-verified full schedule is required')
        raw_hash=_digest(receipt.get('raw_sha256'))
        if _digest(receipt.get('expected_sha256'))!=raw_hash:
            raise ValueError('raw identity differs from expected acquisition identity')
        raw_bytes=_count(receipt.get('raw_bytes'))
        if not 0<raw_bytes<=2*1024**3:
            raise ValueError('compressed source size is outside the frozen file cap')
        url=f'https://datasets.tardis.dev/v1/binance/book_ticker/{day.replace("-","/")}/BTCUSDT.csv.gz'
        if receipt.get('source_url')!=url:
            raise ValueError('source URL does not match the frozen day/venue/asset')
        artifacts=_artifact_paths(run,receipt.get('artifacts_sha256'))
        methods=receipt.get('method_sha256')
        if not isinstance(methods,dict):
            raise ValueError('calculation method identities missing')
        for name,digest in core.items():
            if _digest(methods.get(name))!=digest:
                raise ValueError('scientific calculation method differs from current source')
            if artifacts.get('method-source/'+Path(name).name)!=digest:
                raise ValueError('scientific method snapshot is unbound or changed')
        report=_json(run/'report.json')
        if report.get('day')!=day or _count(report.get('scheduled_intents'))!=86099:
            raise ValueError('coarse report must cover the exact planned full day')
        reports[day]=report
        samples[day]=_json(run/'savings.json.gz',compressed=True)
        sources[day]=dict(raw_sha256=raw_hash,source_url=url,compressed_bytes=raw_bytes)
        verified.append((run,receipt_hash,artifacts))
    result=aggregate_stage(planned,reports,samples,stage=stage,external_gates_passed=external_gates_passed)
    for run,receipt_hash,artifacts in verified:
        _regular(run/'receipt.json')
        if _hash(run/'receipt.json')!=receipt_hash:
            raise ValueError('replay receipt changed during aggregation')
        _artifact_paths(run,artifacts)
    if core!={name:_hash(ROOT/name) for name in CORE_FILES} or aggregate_hash!=_hash(ROOT/_AGGREGATION):
        raise ValueError('calculation or aggregation source changed during summarization')
    return dict(protocol_commit=PROTOCOL_COMMIT,calculation_method_sha256=core,
                aggregation_method_sha256={_AGGREGATION:aggregate_hash},day_sources=sources,
                method_identity_scope=_SCOPE,report=result)


def _bytes(envelope: dict[str,Any]) -> bytes:
    return (json.dumps(envelope,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--stage',choices=tuple(_YEARS),required=True)
    parser.add_argument('--external-gates-passed',action='store_true',
                        help='explicit caller assertion; local metadata does not authenticate rights/publication')
    target=parser.add_mutually_exclusive_group()
    target.add_argument('--check',type=Path,help='compare the entire deterministic envelope to checked JSON bytes')
    target.add_argument('--output',type=Path,help='write a NEW external private JSON file, never overwrite')
    args=parser.parse_args()
    try:
        envelope=load_stage(args.runs,args.stage,external_gates_passed=args.external_gates_passed)
        payload=_bytes(envelope)
        if args.check is not None:
            _regular(args.check)
            if args.check.read_bytes()!=payload:
                print(json.dumps(dict(status='FAIL',reason='AGGREGATE_ENVELOPE_MISMATCH')))
                return 1
        if args.output is not None:
            output=_external(args.output)
            if not output.parent.is_dir():
                raise ValueError('existing external output parent required')
            with output.open('xb') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
    except (ValueError,OSError,TypeError,KeyError,subprocess.SubprocessError) as exc:
        # Exception messages can carry a private path/value; never echo them.
        print(json.dumps(dict(status='FAIL',reason='OFFLINE_STAGE_INTEGRITY_OR_INPUT_FAILURE',error_type=type(exc).__name__)))
        return 2
    print(json.dumps(dict(status='PASS',stage=args.stage,completed_days=len(envelope['day_sources']),
                         planned_days=12,report_status=envelope['report']['status'],
                         verification='OFFLINE_ARTIFACT_IDENTITY_AND_AGGREGATION')))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
