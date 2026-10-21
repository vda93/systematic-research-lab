"""Streaming qualification for the frozen native-BBO protocol.

Original code; no provider rows are embedded. This layer emits unknown states
explicitly. Consumers must not carry a previous valid quote through them.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, replace
from datetime import date, datetime, timezone
import gzip
import hashlib
import math
from pathlib import Path
from typing import Any, Iterable, Iterator

FIELDS = ['exchange', 'symbol', 'timestamp', 'local_timestamp', 'ask_amount',
          'ask_price', 'bid_price', 'bid_amount']
DAY_US = 86_400_000_000


@dataclass(frozen=True)
class Quote:
    exchange_us: int
    ask: float
    bid: float
    ask_amount: float
    bid_amount: float


@dataclass(frozen=True)
class QuoteUpdate:
    local_us: int
    quote: Quote | None
    reason: str


@dataclass
class QuoteCounts:
    rows: int = 0
    duplicate_rows: int = 0
    invalid_rows: int = 0
    conflicting_timestamps: int = 0
    valid_states: int = 0
    unknown_states: int = 0


def _timestamp(text: str, start: int) -> int:
    if not text.isascii() or not text.isdecimal():
        raise ValueError('timestamps must be integral ASCII UTC microseconds')
    value = int(text)
    if not start <= value < start + DAY_US:
        raise ValueError('timestamp outside requested UTC day')
    return value


def _state(row: dict[str, str], exchange_us: int, local_us: int) -> QuoteUpdate:
    try:
        ask, bid, ask_amount, bid_amount = (float(row[k]) for k in
                                           ('ask_price', 'bid_price', 'ask_amount', 'bid_amount'))
    except ValueError:
        return QuoteUpdate(local_us, None, 'INVALID_NUMERIC_QUOTE')
    values = (ask, bid, ask_amount, bid_amount)
    if not all(math.isfinite(value) for value in values):
        return QuoteUpdate(local_us, None, 'NONFINITE_QUOTE')
    if min(values) <= 0:
        return QuoteUpdate(local_us, None, 'NONPOSITIVE_QUOTE')
    if bid >= ask:
        return QuoteUpdate(local_us, None, 'LOCKED_OR_CROSSED')
    return QuoteUpdate(local_us, Quote(exchange_us, ask, bid, ask_amount, bid_amount), 'VALID')


def _emit(update: QuoteUpdate, conflict: bool, counts: QuoteCounts) -> QuoteUpdate:
    if conflict:
        counts.conflicting_timestamps += 1
        update = QuoteUpdate(update.local_us, None, 'AMBIGUOUS_TIMESTAMP')
    if update.quote is None:
        counts.unknown_states += 1
    else:
        counts.valid_states += 1
    return update


def iter_updates(lines: Iterable[str], *, day: str, counts: QuoteCounts) -> Iterator[QuoteUpdate]:
    """Yield strictly increasing receive-time states; fail the file on bad identity.

    All equal-receive-time rows are resolved as a group, without inventing order.
    Exact duplicate rows count once as state; conflicting BBO/validity becomes
    unknown until a later update. Different exchange timestamps with identical
    BBO are diagnostic-only and do not make the BBO state ambiguous.
    Counts are explicitly supplied, mutable acquisition diagnostics. After an
    exception the entire file is unqualified, including its previously yielded
    prefix. The caller must discard partial scientific results, retain counts
    and the failure receipt, and never sort or salvage a favorable subset.
    """
    parsed = date.fromisoformat(day)
    if parsed.isoformat() != day:
        raise ValueError('day must be canonical YYYY-MM-DD')
    start = int(datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc).timestamp()) * 1_000_000
    reader = csv.DictReader(lines, strict=True)
    try:
        actual_fields = reader.fieldnames
    except csv.Error as exc:
        raise ValueError('malformed CSV header') from exc
    if actual_fields != FIELDS:
        raise ValueError('unexpected native BBO schema')
    pending: QuoteUpdate | None = None
    signature: QuoteUpdate | None = None
    conflict = False
    seen: set[tuple[str, ...]] = set()
    try:
        for row in reader:
            counts.rows += 1
            if set(row) != set(FIELDS) or any(not isinstance(row[k], str) for k in FIELDS):
                raise ValueError('malformed native BBO row')
            if row['exchange'] != 'binance' or row['symbol'] != 'BTCUSDT':
                raise ValueError('unexpected exchange or symbol')
            local_us = _timestamp(row['local_timestamp'], start)
            exchange_us = _timestamp(row['timestamp'], start)
            update = _state(row, exchange_us, local_us)
            if update.quote is None:
                counts.invalid_rows += 1
            if pending is not None and local_us < pending.local_us:
                raise ValueError('backward local timestamp; never reorder')
            if pending is None or local_us > pending.local_us:
                if pending is not None:
                    yield _emit(pending, conflict, counts)
                pending, signature, conflict, seen = update, None, False, set()
            raw = tuple(row[k] for k in FIELDS)
            if raw in seen:
                counts.duplicate_rows += 1
            seen.add(raw)
            comparable = replace(update, quote=replace(update.quote, exchange_us=0) if update.quote else None)
            if signature is not None and comparable != signature:
                conflict = True
            signature = comparable
    except csv.Error as exc:
        raise ValueError('malformed CSV') from exc
    if pending is not None:
        yield _emit(pending, conflict, counts)


def _valid_segments(updates: Iterable[QuoteUpdate], end_us: int, age: int) -> Iterator[tuple[int, int]]:
    previous = None
    for update in updates:
        if type(update.local_us) is not int or update.local_us >= end_us:
            raise ValueError('state timestamps must be integers before the end boundary')
        if previous is not None:
            if update.local_us <= previous.local_us:
                raise ValueError('state timestamps must be strictly increasing')
            if previous.quote is not None:
                yield previous.local_us, min(update.local_us, previous.local_us + age)
        previous = update
    if previous is not None and previous.quote is not None:
        yield previous.local_us, min(end_us, previous.local_us + age)


def known_runs(
    updates: Iterable[QuoteUpdate], *, end_us: int, max_age_us: int = 250_000,
) -> Iterator[tuple[int, int]]:
    """Merge known time intervals; an invalid state or expiry gap breaks a run.

    Intervals measure duration [start,end); a strict-past intent at end may use
    that full prior history and a quote exactly at its maximum allowed age.
    The stream uses constant state memory in addition to its input iterator.
    """
    if type(end_us) is not int or type(max_age_us) is not int or max_age_us <= 0:
        raise ValueError('integer end and positive integer maximum age required')
    run_start = None
    run_end = 0
    for start, end in _valid_segments(updates, end_us, max_age_us):
        if run_start is None:
            run_start, run_end = start, end
        elif start <= run_end:
            run_end = end
        else:
            yield run_start, run_end
            run_start, run_end = start, end
    if run_start is not None:
        yield run_start, run_end


def history_grid_count(
    runs: Iterable[tuple[int, int]], *, first_intent_us: int, last_intent_us: int,
) -> int:
    """Count frozen one-second intents with fully known preceding sixty seconds.

    This is an upper bound on final eligibility: depth, shock status and target
    outcomes are deliberately not used. Touching intervals form one continuous
    run; overlapping or reversed intervals fail. Failure cannot be rescued by a cost.
    """
    step, history = 1_000_000, 60_000_000
    if (type(first_intent_us) is not int or type(last_intent_us) is not int
            or first_intent_us > last_intent_us or first_intent_us % step or last_intent_us % step):
        raise ValueError('ordered whole-second intent boundaries required')
    total = 0
    previous_end = None
    run_start = None

    def count(low: int, high: int) -> int:
        low = max(low + history, first_intent_us)
        high = min(high, last_intent_us)
        return max(0, high // step - (low + step - 1) // step + 1) if low <= high else 0

    for start, end in runs:
        if (type(start) is not int or type(end) is not int or start >= end
                or (previous_end is not None and start < previous_end)):
            raise ValueError('ordered nonoverlapping positive-duration known runs required')
        if previous_end is None:
            run_start = start
        elif start > previous_end:
            assert run_start is not None
            total += count(run_start, previous_end)
            run_start = start
        previous_end = end
    if run_start is not None and previous_end is not None:
        total += count(run_start, previous_end)
    return total


def qualify_day(raw_file: Path, *, day: str) -> dict[str, Any]:
    """Reproduce original full-history support without publishing quote values.

    A failure propagates, so no partial-prefix summary can become a finding.
    Full gzip iteration checks the trailer/CRC. Compressed identity is streamed.
    This evaluates the original measurement rule, not the v2 completion rule.
    """
    parsed = date.fromisoformat(day)
    if parsed.isoformat() != day:
        raise ValueError('day must be canonical YYYY-MM-DD')
    start = int(datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc).timestamp()) * 1_000_000
    digest = hashlib.sha256()
    with raw_file.open('rb') as binary_stream:
        while chunk := binary_stream.read(1 << 20):
            digest.update(chunk)
    counts = QuoteCounts()
    summary = {'known_runs': 0, 'known_duration_us': 0, 'longest_known_run_us': 0}

    def summarized(runs: Iterable[tuple[int, int]]) -> Iterator[tuple[int, int]]:
        for low, high in runs:
            summary['known_runs'] += 1
            summary['known_duration_us'] += high - low
            summary['longest_known_run_us'] = max(summary['longest_known_run_us'], high - low)
            yield low, high

    with gzip.open(raw_file, 'rt', encoding='utf-8', newline='') as quote_stream:
        updates = iter_updates(quote_stream, day=day, counts=counts)
        supported = history_grid_count(summarized(known_runs(updates, end_us=start + DAY_US)),
                                       first_intent_us=start + 300_000_000,
                                       last_intent_us=start + DAY_US - 2_000_000)
    scheduled = (DAY_US - 302_000_000) // 1_000_000 + 1
    return {'measurement': 'original full-history BBO protocol', 'day': day,
            'source_url': f'https://datasets.tardis.dev/v1/binance/book_ticker/{parsed:%Y/%m/%d}/BTCUSDT.csv.gz',
            'raw_sha256': digest.hexdigest(), 'compressed_bytes': raw_file.stat().st_size,
            'counts': asdict(counts), **summary, 'scheduled_intents': scheduled,
            'maximum_history_eligible_intents': supported,
            'maximum_eligibility_fraction': supported / scheduled,
            'status': 'DEV_FAIL_SUPPORT' if supported == 0 else 'HISTORY_SUPPORT_POSSIBLE',
            'economic_outcomes_calculated': False}
