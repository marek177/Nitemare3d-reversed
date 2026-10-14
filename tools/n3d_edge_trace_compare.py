#!/usr/bin/env python3
"""Strict ordered snapshot comparison for four Nitemare 3D edge cases.

Synthetic fixtures and matching snapshots do NOT prove original-game parity.
The recorder must independently attest source/build and observed boundaries.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

SCHEMA = "n3d-edge-trace-envelope-v1"
FIELDS = {
    "push": ("step", "push_id", "x", "y", "remaining", "blocked",
             "old_cell_object", "destination_cell_object"),
    "door": ("step", "door_id", "state", "timer", "blocked", "pair_state"),
    "projectile": ("step", "fire_pressed", "weapon", "ammo_before",
                   "ammo_after", "allocated_slot", "slot_states_before",
                   "slot_states_after"),
    "panel": ("step", "panel_id", "x0", "y0", "x1", "y1", "blocking"),
}
BIT_FIELDS = {"blocked", "fire_pressed", "blocking"}
STATE_FIELDS = {"slot_states_before", "slot_states_after"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_trace(path, scenario):
    fields = FIELDS[scenario]
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path}: CSV header must be {','.join(fields)}")
        records = []
        for index, row in enumerate(reader):
            if None in row or any(row.get(name) is None for name in fields):
                raise ValueError(f"{path}: malformed row {index}")
            parsed = {}
            for name in fields:
                token = row[name].strip()
                if name in STATE_FIELDS:
                    if (len(token) != 16 or
                            any(char not in "0123456789abcdefABCDEF" for char in token)):
                        raise ValueError(f"{path}: row {index}: {name} must contain eight hex bytes")
                    parsed[name] = token.lower()
                else:
                    try:
                        parsed[name] = int(token, 16 if token.lower().lstrip("-").startswith("0x") else 10)
                    except ValueError as exc:
                        raise ValueError(f"{path}: row {index}: invalid integer {name}={token!r}") from exc
                    if name in BIT_FIELDS and parsed[name] not in (0, 1):
                        raise ValueError(f"{path}: row {index}: {name} must be 0 or 1")
            if parsed["step"] != index:
                raise ValueError(f"{path}: expected contiguous normalized step {index}")
            if scenario == "projectile":
                if parsed["allocated_slot"] < -1 or parsed["allocated_slot"] > 7:
                    raise ValueError(f"{path}: row {index}: allocated_slot outside -1..7")
                if parsed["ammo_before"] < 0 or parsed["ammo_after"] < 0:
                    raise ValueError(f"{path}: row {index}: negative ammo")
            records.append(parsed)
    if not records:
        raise ValueError(f"{path}: empty trace is not evidence")
    return records


def compare_rows(reference, candidate, fields):
    for index in range(min(len(reference), len(candidate))):
        expected, actual = reference[index], candidate[index]
        if expected != actual:
            return {"index": index,
                    "field": next(name for name in fields if expected[name] != actual[name]),
                    "expected": expected, "actual": actual, "kind": "different_record"}
    if len(reference) != len(candidate):
        idx = min(len(reference), len(candidate))
        return {"index": idx, "field": None,
                "expected": reference[idx] if idx < len(reference) else None,
                "actual": candidate[idx] if idx < len(candidate) else None,
                "kind": "different_length"}
    return None


def validate_envelope(path, csv_path, scenario, count):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"{path}: invalid envelope schema")
    if data.get("scenario") != scenario:
        raise ValueError(f"{path}: scenario mismatch")
    if type(data.get("row_count")) is not int or data["row_count"] != count:
        raise ValueError(f"{path}: row_count mismatch")
    if data.get("csv_sha256") != sha256(csv_path):
        raise ValueError(f"{path}: CSV hash mismatch")
    for name in ("build", "begin", "end"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"{path}: missing {name}")
    if data["begin"] == data["end"]:
        raise ValueError(f"{path}: begin/end markers must differ")
    if data.get("closed") is not True:
        raise ValueError(f"{path}: capture not declared closed")
    return {name: data[name] for name in ("build", "begin", "end")}


def compare_traces(scenario, reference_csv, candidate_csv, *,
                   reference_envelope=None, candidate_envelope=None,
                   require_boundaries=False):
    if scenario not in FIELDS:
        raise ValueError(f"unknown scenario: {scenario}")
    reference = read_trace(reference_csv, scenario)
    candidate = read_trace(candidate_csv, scenario)
    mismatch = compare_rows(reference, candidate, FIELDS[scenario])

    boundary_attested = False
    errors = []
    if bool(reference_envelope) != bool(candidate_envelope):
        errors.append("both boundary envelopes are required together")
    elif reference_envelope and candidate_envelope:
        original = validate_envelope(reference_envelope, reference_csv, scenario, len(reference))
        port = validate_envelope(candidate_envelope, candidate_csv, scenario, len(candidate))
        if (original["begin"], original["end"]) != (port["begin"], port["end"]):
            errors.append("reference and candidate capture boundaries differ")
        else:
            boundary_attested = True

    ok = mismatch is None and not errors and (boundary_attested or not require_boundaries)
    if mismatch is not None:
        verdict = "first_divergence"
    elif errors:
        verdict = "invalid_boundaries"
    elif require_boundaries and not boundary_attested:
        verdict = "boundaries_required"
    else:
        verdict = "trace_match_with_declared_boundaries" if boundary_attested else "trace_match_unsealed"
    return {
        "ok": ok, "verdict": verdict, "scenario": scenario,
        "reference_count": len(reference), "candidate_count": len(candidate),
        "first_difference": mismatch, "boundary_declarations_valid": boundary_attested,
        "boundary_errors": errors, "original_runtime_verified": False,
        "note": "Matching CSV/envelopes do not authenticate the original CPU capture or prove 1:1 parity.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=sorted(FIELDS))
    parser.add_argument("reference_csv")
    parser.add_argument("candidate_csv")
    parser.add_argument("--reference-envelope")
    parser.add_argument("--candidate-envelope")
    parser.add_argument("--require-boundaries", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = compare_traces(
            args.scenario, args.reference_csv, args.candidate_csv,
            reference_envelope=args.reference_envelope,
            candidate_envelope=args.candidate_envelope,
            require_boundaries=args.require_boundaries)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
