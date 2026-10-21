"""Frozen reference-rate predictive study; no acquisition occurs in this module.

Signed reference changes are statistical measurements, not executable returns.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import io
import json
import math
import zipfile
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

ASSETS = ('EURUSD', 'USDJPY')
ROLES = {'development': ('2016-07-01', '2020-01-01', 250),
         'validation': ('2020-01-01', '2023-01-01', 500),
         'final': ('2023-01-01', '2026-01-01', 500)}
SEED = 20261021
REPETITIONS = 9999
BLOCK_LENGTHS = (10, 20, 60)
MINIMUM_EFFECT = .5 / 10000
SOURCE_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip'


@dataclass(frozen=True)
class Rate:
    day: date
    usd: str
    jpy: str


def _positive(text: str) -> float:
    try:
        value = Decimal(text)
        number = float(value)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        raise ValueError('invalid source decimal') from exc
    if not value.is_finite() or not math.isfinite(number) or number <= 0:
        raise ValueError('source rates must be positive finite decimals')
    if text != text.strip():
        raise ValueError('source decimals must not have surrounding whitespace')
    return number


def _validate(records: list[Rate]) -> list[Rate]:
    if not records:
        raise ValueError('empty selected source window')
    ordered = sorted(records, key=lambda r: r.day)
    for row in ordered:
        if not date(2016, 6, 1) <= row.day < date(2026, 1, 1):
            raise ValueError('selected date outside frozen acquisition window')
        if row.day.weekday() >= 5:
            raise ValueError('unexpected weekend provider observation')
        _positive(row.usd)
        _positive(row.jpy)
    for left, right in zip(ordered, ordered[1:]):
        if left.day == right.day:
            raise ValueError('duplicate provider date')
        if (right.day - left.day).days > 7:
            raise ValueError('provider gap exceeds seven calendar days')
    return ordered


def _day(text: str) -> date:
    try:
        result = date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError('date must be canonical YYYY-MM-DD') from exc
    if result.isoformat() != text:
        raise ValueError('date must be canonical YYYY-MM-DD')
    return result


def canonical_csv(records: list[Rate]) -> bytes:
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['Date', 'USD', 'JPY'])
    writer.writerows((r.day.isoformat(), r.usd, r.jpy) for r in _validate(records))
    return stream.getvalue().encode('utf-8')


def parse_csv(payload: bytes) -> list[Rate]:
    reader = csv.reader(io.StringIO(payload.decode('utf-8-sig'), newline=''))
    if next(reader, None) != ['Date', 'USD', 'JPY']:
        raise ValueError('canonical source schema must be exactly Date,USD,JPY')
    records = []
    for row in reader:
        if len(row) != 3:
            raise ValueError('canonical source row width mismatch')
        records.append(Rate(_day(row[0]), row[1], row[2]))
    return _validate(records)


def selected_archive(payload: bytes) -> tuple[bytes, dict]:
    """Select the frozen scope, failing closed on any extra archive document.

    An archive notice requires explicit human reconciliation with the provider
    terms. It is never silently classified as permitting redistribution.
    """
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        members = archive.infolist()
        if len(members) != 1 or members[0].filename != 'eurofxref-hist.csv':
            raise ValueError('unexpected archive member or notice: review before redistribution')
        if members[0].file_size > 50_000_000:
            raise ValueError('unexpected archive member size')
        if archive.testzip() is not None:
            raise ValueError('archive CRC failure')
        reader = csv.reader(io.StringIO(archive.read(members[0]).decode('utf-8-sig'), newline=''))
        header = next(reader, [])
        if any(header.count(name) != 1 for name in ('Date', 'USD', 'JPY')):
            raise ValueError('provider lacks unique Date/USD/JPY columns')
        positions = [header.index(name) for name in ('Date', 'USD', 'JPY')]
        selected = []
        for row in reader:
            if len(row) != len(header):
                raise ValueError('provider row width mismatch')
            day = _day(row[positions[0]])
            if date(2016, 6, 1) <= day < date(2026, 1, 1):
                selected.append(Rate(day, row[positions[1]], row[positions[2]]))
        result = canonical_csv(selected)
        return result, {'member': members[0].filename, 'crc32': f'{members[0].CRC:08x}',
                        'raw_archive_sha256': sha256(payload).hexdigest(),
                        'canonical_csv_sha256': sha256(result).hexdigest(),
                        'archive_notice_check': 'PASS_SINGLE_CSV_NO_EXTRA_NOTICE',
                        'selected_rows': len(selected)}


def rows_for_role(records: list[Rate], role: str, *, delay: int = 1) -> list[dict]:
    if role not in ROLES or delay not in (1, 2):
        raise ValueError('unknown role or delay')
    records = _validate(records)
    begin, end, _ = ROLES[role]
    feature_begin = '2016-06-01' if role == 'development' else begin
    prices = [(float(r.usd), float(r.jpy) / float(r.usd)) for r in records]
    rows = []
    for t in range(20, len(records) - delay - 1):
        first, last = t + delay, t + delay + 1
        if not (feature_begin <= records[t - 20].day.isoformat()
                and begin <= records[t].day.isoformat() < end
                and begin <= records[first].day.isoformat() < end
                and begin <= records[last].day.isoformat() < end):
            continue
        momentum = [math.log(prices[t][j] / prices[t - 20][j]) for j in range(2)]
        signs = [(m > 0) - (m < 0) for m in momentum]
        target = [math.log(prices[last][j] / prices[first][j]) for j in range(2)]
        if not all(math.isfinite(x) for x in momentum + target):
            raise ValueError('nonfinite feature or target arithmetic')
        signal = [s * y for s, y in zip(signs, target)]
        rows.append({'feature_start': records[t - 20].day.isoformat(),
                     'signal_date': records[t].day.isoformat(),
                     'target_start': records[first].day.isoformat(),
                     'target_end': records[last].day.isoformat(),
                     'sign': signs, 'signal': signal, 'target': target,
                     'difference': [a - b for a, b in zip(signal, target)]})
    return rows


def holm(p_values: list[float]) -> list[float]:
    if not p_values or any(not math.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ValueError('p-values must be finite and within [0,1]')
    ordered = sorted(range(len(p_values)), key=lambda i: (p_values[i], i))
    output = [0.] * len(p_values)
    previous = 0.
    for rank, i in enumerate(ordered):
        previous = max(previous, min(1., (len(p_values) - rank) * p_values[i]))
        output[i] = previous
    return output


def bootstrap(values: ArrayLike, *, block_length: int = 20, repetitions: int = REPETITIONS) -> dict:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 2 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('finite paired two-asset rows required')
    n = len(values)
    if type(block_length) is not int or not 1 <= block_length <= n // 2:
        raise ValueError('block length must be in [1,N//2]')
    if type(repetitions) is not int or repetitions < 1:
        raise ValueError('positive integer repetitions required')
    observed = values.mean(axis=0)
    centered = values - observed
    # Prefix sums avoid allocating B*N indices or B*N*assets gathered arrays.
    def sums(array: NDArray[np.float64], length: int) -> NDArray[np.float64]:
        extended = np.concatenate([array, array[:block_length]], axis=0)
        prefix = np.vstack([np.zeros(2), np.cumsum(extended, axis=0)])
        return prefix[length:length + n] - prefix[:n]
    full, remainder = divmod(n, block_length)
    blocks = full + bool(remainder)
    all_sums = (sums(values, block_length), sums(centered, block_length))
    tail_sums = (sums(values, remainder), sums(centered, remainder)) if remainder else None
    means, null_means = np.empty((repetitions, 2)), np.empty((repetitions, 2))
    rng = np.random.default_rng(SEED)
    for offset in range(0, repetitions, 128):
        size = min(128, repetitions - offset)
        starts = rng.integers(0, n, size=(size, blocks))
        for j, destination in enumerate((means, null_means)):
            total = all_sums[j][starts[:, :full]].sum(axis=1)
            if remainder:
                assert tail_sums is not None
                total += tail_sums[j][starts[:, -1]]
            destination[offset:offset + size] = total / n
    interval = np.quantile(means, [.025, .975], axis=0, method='linear')
    return {'block_length': block_length, 'repetitions': repetitions, 'seed': SEED,
            'units': 'logarithmic reference-rate change per observation',
            'sample_size': n, 'assets': [
                {'asset': asset, 'mean': float(observed[j]),
                 'ci_low': float(interval[0, j]), 'ci_high': float(interval[1, j]),
                 'p_value': float((1 + np.count_nonzero(null_means[:, j] >= observed[j])) / (repetitions + 1))}
                for j, asset in enumerate(ASSETS)]}


def classify(mean: float, ci_low: float, adjusted_p: float) -> str:
    if mean <= 0:
        return 'NEGATIVE_COMPARISON'
    if ci_low > 0 and adjusted_p <= .05 and mean >= MINIMUM_EFFECT:
        return 'PASS'
    return 'INCONCLUSIVE'


def _summary(rows: list[dict], j: int) -> dict:
    changes = np.array([r['target'][j] for r in rows])
    signals = np.array([r['signal'][j] for r in rows])
    differences = signals - changes
    signs = [r['sign'][j] for r in rows]
    return {'sample_size': len(rows), 'mean_signal_bps': float(signals.mean() * 10000),
            'mean_always_long_bps': float(changes.mean() * 10000),
            'mean_always_short_bps': float(-changes.mean() * 10000), 'mean_flat_bps': 0.,
            'mean_difference_bps': float(differences.mean() * 10000),
            'median_difference_bps': float(np.median(differences) * 10000),
            'sign_counts': {str(s): signs.count(s) for s in (-1, 0, 1)}}


def _period(rows: list[dict], role: str, *, repetitions: int) -> dict:
    minimum = ROLES[role][2]
    if len(rows) < minimum:
        return {'status': 'FAIL_SUPPORT', 'sample_size': len(rows), 'required': minimum}
    differences = np.array([r['difference'] for r in rows])
    by_block = [bootstrap(differences, block_length=length, repetitions=repetitions)
                for length in BLOCK_LENGTHS]
    primary = next(b for b in by_block if b['block_length'] == 20)
    adjusted = holm([a['p_value'] for a in primary['assets']])
    summaries = {}
    for j, asset in enumerate(ASSETS):
        stats = primary['assets'][j]
        summaries[asset] = {**_summary(rows, j), 'ci_low_bps': stats['ci_low'] * 10000,
                            'ci_high_bps': stats['ci_high'] * 10000,
                            'primary_p_value': stats['p_value'],
                            'holm_adjusted_p_value': adjusted[j],
                            'verdict': (classify(stats['mean'], stats['ci_low'], adjusted[j])
                                        if role == 'final' else 'DESCRIPTIVE_TEMPORAL_ROLE')}
    years = sorted({r['target_end'][:4] for r in rows})
    annual = []
    for year in years:
        subset = [r for r in rows if r['target_end'].startswith(year)]
        annual.append({'year': year, 'assets': {a: _summary(subset, j) for j, a in enumerate(ASSETS)},
                       'pooled_contribution_to_full_mean_bps': float(
                           np.array([r['difference'] for r in subset]).mean(axis=1).sum() / len(rows) * 10000)})
    strongest = max(annual, key=lambda r: (r['pooled_contribution_to_full_mean_bps'], -int(r['year'])))
    removed = strongest['year'] if strongest['pooled_contribution_to_full_mean_bps'] > 0 else None
    retained = [r for r in rows if not removed or not r['target_end'].startswith(removed)]
    concentration = {'status': 'DESCRIPTIVE_OUTCOME_DEPENDENT', 'removed_year': removed,
                     'removed_contribution_to_full_mean_bps': strongest['pooled_contribution_to_full_mean_bps'] if removed else 0.,
                     'retained_sample_size': len(retained),
                     'retained_pooled_mean_bps': float(np.array([r['difference'] for r in retained]).mean() * 10000) if retained else None}
    return {'status': 'QUALIFIED', 'sample_size': len(rows), 'first_target': rows[0]['target_start'],
            'last_target': rows[-1]['target_end'], 'assets': summaries, 'bootstrap': by_block,
            'pooled_mean_difference_bps': float(differences.mean() * 10000), 'annual': annual,
            'concentration': concentration,
            'family_verdict': ('PASS' if all(a['verdict'] == 'PASS' for a in summaries.values())
                               else 'NOT_PASS') if role == 'final' else 'DESCRIPTIVE_TEMPORAL_ROLE'}


def run_study(payload: bytes, *, repetitions: int = REPETITIONS) -> dict:
    records = parse_csv(payload)
    roles = {role: _period(rows_for_role(records, role), role, repetitions=repetitions) for role in ROLES}
    delayed = {}
    for role in ROLES:
        rows = rows_for_role(records, role, delay=2)
        delayed[role] = {'status': 'DESCRIPTIVE_SENSITIVITY', 'sample_size': len(rows),
                         'assets': {a: _summary(rows, j) for j, a in enumerate(ASSETS)} if rows else {}}
    return {'study_id': 'ECB-FX-MOM20-v001', 'evidence_role': 'REAL_MARKET_REFERENCE_OBSERVATIONS',
            'source_csv_sha256': sha256(payload).hexdigest(), 'numpy_version': np.__version__,
            'units': 'basis points of signed logarithmic reference-rate change per observation',
            'executable_profitability': 'NOT_EVALUATED', 'prospective_fresh_oos': False,
            'minimum_effect_bps': .5, 'minimum_effect_interpretation': 'ARBITRARY_STATISTICAL_RELEVANCE_SCREEN_NOT_TRADING_ECONOMICS',
            'roles': roles, 'extra_delay': delayed,
            'family_verdict': (roles['final'].get('family_verdict', 'FAIL_SUPPORT')
                               if all(r['status'] == 'QUALIFIED' for r in roles.values()) else 'FAIL_SUPPORT')}


def result_bytes(result: dict) -> bytes:
    def rounded(value: Any) -> Any:
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError('nonfinite result')
            return round(value, 10)
        if isinstance(value, dict):
            return {key: rounded(item) for key, item in value.items()}
        if isinstance(value, (tuple, list)):
            return [rounded(item) for item in value]
        return value
    return (json.dumps(rounded(result), sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
