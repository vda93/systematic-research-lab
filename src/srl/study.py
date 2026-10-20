"""Original synthetic concentration construction and a known-zero-mean audit.

The protocol is an inspectable replay template. Its constructed outcomes are
known by design; its presence is not proof of an unseen preregistration.
"""

from dataclasses import asdict
from datetime import date, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
import random

from .accounting import Record, concentration, summarize
from .resampling import paired_daily_bootstrap
from .validation import compare_events


def _keys(value, expected, path):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{path}: expected exactly {sorted(expected)}")


def _integer(value, path, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{path}: expected integer >= {minimum}")
    return value


def _number(value, path, *, minimum=None):
    if type(value) not in (int, float):
        raise ValueError(f"{path}: expected a finite number")
    try:
        valid = math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid or (minimum is not None and value < minimum):
        raise ValueError(f"{path}: invalid finite number or lower bound")
    return value


def _calendar(value, path):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{path}: expected canonical ISO calendar date") from None
    if parsed.isoformat() != value:
        raise ValueError(f"{path}: expected canonical ISO calendar date")
    return parsed


def _blocks(value, maximum, path):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{path}: expected a nonempty list")
    for block in value:
        _integer(block, path, 1)
        if block > maximum:
            raise ValueError(f"{path}: block exceeds series length")
    if len(set(value)) != len(value):
        raise ValueError(f"{path}: duplicate block length")


def _validate(protocol):
    _keys(protocol, ("schema_version", "evidence_role", "constructed_teaching_example",
                     "cohort_design", "inference", "stop_rule", "calibration"), "protocol")
    if type(protocol["schema_version"]) is not int or protocol["schema_version"] != 1:
        raise ValueError("schema_version: only integer 1 is supported")
    if protocol["evidence_role"] != "SYNTHETIC" or protocol["constructed_teaching_example"] is not True:
        raise ValueError("only a disclosed constructed SYNTHETIC teaching example is supported")
    design = protocol["cohort_design"]
    _keys(design, ("start_date", "weeks", "days_per_cohort", "close_offsets_days", "record_cost",
                   "second_record_net", "control_base_weekly_net", "treatment_base_weekly_net",
                   "special_weeks"), "cohort_design")
    start = _calendar(design["start_date"], "cohort_design.start_date")
    weeks = _integer(design["weeks"], "cohort_design.weeks", 1)
    if _integer(design["days_per_cohort"], "days_per_cohort", 1) != 7:
        raise ValueError("cohort_design.days_per_cohort: weekly cohorts require 7 days")
    offsets = design["close_offsets_days"]
    if not isinstance(offsets, list) or len(offsets) != 2:
        raise ValueError("close_offsets_days: expected two increasing offsets inside each week")
    for offset in offsets:
        _integer(offset, "close_offsets_days", 1)
    if not 0 < offsets[0] < offsets[1] < 7:
        raise ValueError("close_offsets_days: expected two increasing offsets inside each week")
    try:
        start + timedelta(days=weeks * 7 - 1)
    except (OverflowError, ValueError):
        raise ValueError("cohort_design: calendar extent is outside supported dates") from None
    _number(design["record_cost"], "record_cost", minimum=0)
    for field in ("second_record_net", "control_base_weekly_net", "treatment_base_weekly_net"):
        _number(design[field], field)
    specials = design["special_weeks"]
    if not isinstance(specials, list):
        raise ValueError("special_weeks: expected a list")
    indices = []
    for special in specials:
        _keys(special, ("index", "control_weekly_net", "treatment_weekly_net"), "special_week")
        index = _integer(special["index"], "special_week.index")
        if index >= weeks:
            raise ValueError("special_week.index: outside cohort range")
        indices.append(index)
        _number(special["control_weekly_net"], "special_week.control_weekly_net")
        _number(special["treatment_weekly_net"], "special_week.treatment_weekly_net")
    if len(set(indices)) != len(indices):
        raise ValueError("special_weeks: duplicate index")
    inference = protocol["inference"]
    _keys(inference, ("block_sizes", "repetitions", "seed"), "inference")
    _blocks(inference["block_sizes"], weeks * 7 // 2, "inference.block_sizes")
    _integer(inference["repetitions"], "inference.repetitions", 2)
    _integer(inference["seed"], "inference.seed")
    stop = protocol["stop_rule"]
    _keys(stop, ("remove_cohorts", "minimum_retained_net"), "stop_rule")
    if _integer(stop["remove_cohorts"], "stop_rule.remove_cohorts") > weeks:
        raise ValueError("stop_rule.remove_cohorts exceeds cohort count")
    _number(stop["minimum_retained_net"], "stop_rule.minimum_retained_net")
    calibration = protocol["calibration"]
    _keys(calibration, ("trials", "days", "burn_in", "rho", "innovation_scale",
                        "common_shock_scale", "block_sizes", "repetitions", "seed"), "calibration")
    _integer(calibration["trials"], "calibration.trials", 1)
    _integer(calibration["days"], "calibration.days", 4)
    _integer(calibration["burn_in"], "calibration.burn_in")
    if calibration["days"] > (date.max - date(2050, 1, 1)).days + 1:
        raise ValueError("calibration.days: calendar extent is outside supported dates")
    rho = _number(calibration["rho"], "calibration.rho")
    if not -1 < rho < 1:
        raise ValueError("calibration.rho: expected absolute value below 1")
    if _number(calibration["innovation_scale"], "calibration.innovation_scale", minimum=0) == 0:
        raise ValueError("calibration.innovation_scale: expected positive scale")
    _number(calibration["common_shock_scale"], "calibration.common_shock_scale", minimum=0)
    _blocks(calibration["block_sizes"], calibration["days"] // 2, "calibration.block_sizes")
    _integer(calibration["repetitions"], "calibration.repetitions", 2)
    _integer(calibration["seed"], "calibration.seed")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate protocol key: {key}")
        result[key] = value
    return result


def load_protocol(path):
    """Read an exact-schema JSON protocol, rejecting duplicate keys and NaN."""
    protocol = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    _validate(protocol)
    return protocol


def build_fixture(protocol):
    """Construct two paired observations per opened-date cohort, in net units."""
    _validate(protocol)
    design = protocol["cohort_design"]
    start = date.fromisoformat(design["start_date"])
    specials = {row["index"]: row for row in design["special_weeks"]}
    fixture = {"control": [], "treatment": []}
    for week in range(design["weeks"]):
        opened = start + timedelta(days=week * 7)
        for arm in fixture:
            total = specials.get(week, {}).get(f"{arm}_weekly_net", design[f"{arm}_base_weekly_net"])
            nets = (total - design["second_record_net"], design["second_record_net"])
            for observation, (offset, net) in enumerate(zip(design["close_offsets_days"], nets)):
                fixture[arm].append(Record(
                    f"cohort-{week:03d}-observation-{observation}", opened.isoformat(),
                    (opened + timedelta(days=offset)).isoformat(), net + design["record_cost"],
                    design["record_cost"]))
    return fixture


def _daily(records, start, days):
    values = {(start + timedelta(days=day)).isoformat(): 0.0 for day in range(days)}
    for record in records:
        values[record.closed] += record.gross - record.cost
    return values


def _calibration(design):
    # Zero initial state and symmetric zero-mean innovations imply E[D_t] = 0
    # at every date, even before the fixed burn-in. Burn-in is not a claim of
    # exact stationary initialization of an infinite-innovation process.
    samples = []
    innovations = (-2, -1, 0, 1, 2)
    start = date(2050, 1, 1)
    for trial in range(design["trials"]):
        rng = random.Random(design["seed"] + 1009 * trial)
        difference = 0.0
        for _ in range(design["burn_in"]):
            difference = design["rho"] * difference + rng.choice(innovations) * design["innovation_scale"]
        control, treatment = {}, {}
        for day in range(design["days"]):
            difference = design["rho"] * difference + rng.choice(innovations) * design["innovation_scale"]
            shared = rng.choice(innovations) * design["common_shock_scale"]
            label = (start + timedelta(days=day)).isoformat()
            control[label], treatment[label] = shared, shared + difference
        samples.append((control, treatment))
    by_block = []
    for block in design["block_sizes"]:
        outcomes = []
        for trial, (control, treatment) in enumerate(samples):
            result = paired_daily_bootstrap(
                control, treatment, block_size=block, repetitions=design["repetitions"],
                seed=design["seed"] + 1009 * trial + 7919 * block)
            outcomes.append({"trial": trial, **result,
                             "covered": result["ci_low"] <= 0 <= result["ci_high"],
                             "width": result["ci_high"] - result["ci_low"]})
        covered = sum(outcome["covered"] for outcome in outcomes)
        coverage = covered / design["trials"]
        by_block.append({"block_size": block, "trials": design["trials"], "covered": covered,
                         "coverage": coverage,
                         "monte_carlo_se": math.sqrt(coverage * (1 - coverage) / design["trials"]),
                         "mean_interval_width": math.fsum(outcome["width"] for outcome in outcomes) / design["trials"],
                         "trials_detail": outcomes})
    return {"known_mean_delta": 0.0,
            "model": "zero-initialized AR(1); fixed burn-in; symmetric uniform integer innovations [-2,-1,0,1,2]",
            "units": "synthetic net units per calendar day", "nominal_coverage": 0.95,
            "design": dict(design), "by_block": by_block}


def _reported(value):
    """Round display floats, preserving nonzero values if rounding erases them.

    The tiny-value exception retains interval signs used by coverage decisions,
    plus nonzero scales and widths. Calculations always use the original float.
    """
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("nonfinite computed study output")
        rounded = round(value, 10)
        if rounded == 0:
            return value if value != 0 else 0.0
        return rounded
    if isinstance(value, dict):
        return {key: _reported(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_reported(item) for item in value]
    return value


def run_study(protocol):
    """Run the full declared design, retaining every block and calibration trial."""
    _validate(protocol)
    fixture = build_fixture(protocol)
    design = protocol["cohort_design"]
    start = date.fromisoformat(design["start_date"])
    daily = {arm: _daily(records, start, design["weeks"] * 7) for arm, records in fixture.items()}
    identities = {arm: [{"key": row.key, "opened": row.opened, "closed": row.closed}
                        for row in records] for arm, records in fixture.items()}
    pairing = compare_events(identities["control"], identities["treatment"])
    if pairing["status"] != "PASS":
        raise ValueError("constructed event identities failed parity")
    inference = protocol["inference"]
    bootstraps = [paired_daily_bootstrap(daily["control"], daily["treatment"], block_size=block,
                  repetitions=inference["repetitions"], seed=inference["seed"])
                  for block in inference["block_sizes"]]
    stress = concentration(fixture["treatment"], protocol["stop_rule"]["remove_cohorts"])
    cohorts = []
    for index in range(design["weeks"]):
        row = {"index": index, "opened": (start + timedelta(days=index * 7)).isoformat()}
        for arm in fixture:
            row[f"{arm}_net"] = math.fsum(record.gross - record.cost for record in fixture[arm][index*2:index*2+2])
        cohorts.append(row)
    threshold = protocol["stop_rule"]["minimum_retained_net"]
    result = {
        "schema_version": 1, "evidence_role": "SYNTHETIC", "constructed_teaching_example": True,
        "protocol_sha256": sha256(_canonical(protocol)).hexdigest(),
        "input_sha256": sha256(_canonical({arm: [asdict(row) for row in rows] for arm, rows in fixture.items()})).hexdigest(),
        "design": {**design, "calendar_days": design["weeks"] * 7,
                   "daily_net_assignment": "net recognized on closed date; inactive calendar days are zero",
                   "units": "synthetic net units"},
        "main": {"control": summarize(fixture["control"]), "treatment": summarize(fixture["treatment"]),
                 "concentration": stress, "event_pairing": pairing, "bootstrap": bootstraps,
                 "cohorts": cohorts, "stop_rule": {**protocol["stop_rule"],
                     "requirement": "retained net must strictly exceed minimum_retained_net",
                     "decision": "PASS" if stress["retained_total"] > threshold else "REJECT",
                     "bootstrap_cannot_rescue_failed_gate": True}},
        "calibration": _calibration(protocol["calibration"]),
    }
    return _reported(result)
