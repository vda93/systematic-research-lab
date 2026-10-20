"""Compare finite scalar event rows by semantic key, independent of row order."""

import math
from typing import Iterable, Mapping


def _number(value: object) -> bool:
    return type(value) in (int, float)


def _check_scalar(value: object) -> None:
    if value is None or type(value) in (str, bool):
        return
    if not _number(value):
        raise ValueError("event values must be finite scalars")
    try:
        finite = math.isfinite(value)
    except OverflowError as exc:
        raise ValueError("event number exceeds finite float range") from exc
    if not finite:
        raise ValueError("event values must be finite")


def _index(rows: Iterable[Mapping], tolerant_fields: tuple[str, ...]) -> dict[str, dict]:
    indexed = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("each event must be a mapping")
        row = dict(row)
        if any(not isinstance(field, str) or not field.strip() for field in row):
            raise ValueError("event field names must be nonblank strings")
        key = row.get("key")
        if not isinstance(key, str) or not key.strip() or key in indexed:
            raise ValueError("event keys must be nonblank unique strings")
        for value in row.values():
            _check_scalar(value)
        for field in tolerant_fields:
            if field not in row or not _number(row[field]):
                raise ValueError("declared tolerance fields must exist and be numeric in every row")
        indexed[key] = row
    return indexed


def compare_events(
    control: Iterable[Mapping], treatment: Iterable[Mapping], *,
    tolerant_fields: tuple[str, ...] = (), atol: float = 1e-9,
) -> dict:
    """Compare shared keyed rows, reporting missing rows, fields and values.

    `matched` counts identities shared by both inputs, even if values differ.
    Exact fields require the same scalar type and value. Declared numeric fields
    use absolute tolerance only; no relative tolerance is implied. Empty pairs
    return FAIL because no event correspondence was demonstrated.
    """
    if not isinstance(tolerant_fields, tuple) or any(
        not isinstance(field, str) or not field.strip() or field == "key"
        for field in tolerant_fields
    ) or len(set(tolerant_fields)) != len(tolerant_fields):
        raise ValueError("tolerant_fields must be a tuple of unique non-key field names")
    _check_scalar(atol)
    if not _number(atol) or atol < 0:
        raise ValueError("atol must be a finite nonnegative number")
    left, right = _index(control, tolerant_fields), _index(treatment, tolerant_fields)
    differences = []
    common = set(left) & set(right)
    if not left and not right:
        differences.append({"reason": "no_events"})
    for key in sorted(set(left) | set(right)):
        if key not in common:
            differences.append({"key": key, "reason": "missing_control" if key not in left else "missing_treatment"})
            continue
        a, b = left[key], right[key]
        for field in sorted(set(a) | set(b)):
            if field not in a or field not in b:
                differences.append({"key": key, "field": field, "reason": "schema_mismatch"})
                continue
            if field in tolerant_fields:
                # Overflow of a finite subtraction implies a distance larger
                # than every valid finite atol, so it is simply a mismatch.
                same = abs(a[field] - b[field]) <= atol
            else:
                same = type(a[field]) is type(b[field]) and a[field] == b[field]
            if not same:
                differences.append({"key": key, "field": field, "reason": "value_mismatch",
                                    "control": a[field], "treatment": b[field]})
    return {"status": "FAIL" if differences else "PASS", "matched": len(common), "differences": differences}
