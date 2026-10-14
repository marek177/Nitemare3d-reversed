#!/usr/bin/env python3
"""Compare two ordered Nitemare 3D DOS-v2.0 trace captures, fail closed.

A successful comparison is evidence of agreement *between supplied files*,
not proof that a recorder captured the original game's complete execution.
Trace envelopes contain assertions from the recorder, not trusted telemetry.
"""

import argparse
import hashlib
import json
from pathlib import Path

from n3d_trace_audit import audit_fast, audit_rng, read_csv

# Exact DOS v2.0 UNPACKED executable-image profile (v0.22 registry).
# It is NOT the SHA-256 of a packed distribution EXE or a Win16 build.
DOS20_UNPACKED_BYTES = 171360
DOS20_UNPACKED_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"
TRACE_SCHEMA = "n3d-trace-envelope-v1"


def file_hash(path):
    sha = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""):
            sha.update(chunk)
            size += len(chunk)
    return {"sha256": sha.hexdigest(), "size": size}


def verify_reference_image(path):
    actual = file_hash(path)
    return {
        "match": actual["size"] == DOS20_UNPACKED_BYTES and
                 actual["sha256"] == DOS20_UNPACKED_SHA256,
        "expected_sha256": DOS20_UNPACKED_SHA256,
        "expected_size": DOS20_UNPACKED_BYTES,
        "actual_sha256": actual["sha256"],
        "actual_size": actual["size"],
    }


def validate_envelope(path, csv_path, trace_type, count, role):
    """Validate recorder-declared boundaries and integrity, NOT their truth."""
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{role}: envelope must be a JSON object")
    if manifest.get("schema") != TRACE_SCHEMA:
        raise ValueError(f"{role}: unsupported envelope schema")
    if manifest.get("trace_type") != trace_type:
        raise ValueError(f"{role}: trace_type mismatch")
    build = manifest.get("build")
    if not isinstance(build, str) or not build:
        raise ValueError(f"{role}: missing build name")
    if role == "reference" and build != "dos-v2.0":
        raise ValueError("reference: must declare dos-v2.0 (no cross-build offset reuse)")
    if type(manifest.get("row_count")) is not int or manifest["row_count"] != count:
        raise ValueError(f"{role}: row_count does not equal file contents")
    if manifest.get("csv_sha256") != file_hash(csv_path)["sha256"]:
        raise ValueError(f"{role}: CSV digest mismatch")
    begin, end = manifest.get("begin"), manifest.get("end")
    if not isinstance(begin, str) or not begin:
        raise ValueError(f"{role}: begin marker missing")
    if not isinstance(end, str) or not end:
        raise ValueError(f"{role}: end marker missing")
    # The seal is a recorder assertion. We cannot infer event presence from CSV.
    if type(manifest.get("closed")) is not bool or not manifest["closed"]:
        raise ValueError(f"{role}: capture not declared closed")
    return {"build": build, "begin": begin, "end": end,
            "row_count": count, "integrity_attested": True}


def compare_ordered(reference, candidate, fields):
    """First chronological difference, no sorting and no gap masking."""
    limit = min(len(reference), len(candidate))
    for index in range(limit):
        expected = {name: reference[index][name] for name in fields}
        observed = {name: candidate[index][name] for name in fields}
        if expected != observed:
            # One-record lookahead suggests a *logger* omission/duplication,
            # not necessarily a skipped or extra game-engine RNG call.
            clue = "ordinary_divergence"
            if index + 1 < len(reference):
                later_expected = {n: reference[index + 1][n] for n in fields}
                if observed == later_expected:
                    clue = "candidate_record_maybe_missing"
            if clue == "ordinary_divergence" and index + 1 < len(candidate):
                later_observed = {n: candidate[index + 1][n] for n in fields}
                if expected == later_observed:
                    clue = "candidate_record_maybe_extra"
            return {"equal": False, "index": index, "expected": expected,
                    "observed": observed, "classification": clue}
    if len(reference) != len(candidate):
        index = limit
        return {
            "equal": False, "index": index,
            "expected": {n: reference[index][n] for n in fields}
                        if index < len(reference) else None,
            "observed": {n: candidate[index][n] for n in fields}
                        if index < len(candidate) else None,
            "classification": "length_mismatch",
        }
    return {"equal": True, "index": None, "expected": None,
            "observed": None, "classification": "match"}


def compare_captures(trace_type, reference, candidate, *,
                     seed=1, strict_callers=True, invocation=None, tick_at_gate=None,
                     reference_csv=None, candidate_csv=None,
                     reference_envelope=None, candidate_envelope=None,
                     reference_image=None, require_provenance=False):
    if trace_type not in ("rng", "fast"):
        raise ValueError("trace type must be rng or fast")
    fields = (("caller", "before", "after", "result") if trace_type == "rng"
              else ("invocation", "caller", "target"))

    if trace_type == "rng":
        reference_check = audit_rng(reference, seed=seed, strict_callers=strict_callers)
        candidate_check = audit_rng(candidate, seed=seed, strict_callers=strict_callers)
    else:
        if invocation is None or tick_at_gate is None:
            raise ValueError("FAST requires invocation and tick_at_gate")
        reference_check = audit_fast(reference, invocation, tick_at_gate)
        candidate_check = audit_fast(candidate, invocation, tick_at_gate)

    first_difference = compare_ordered(reference, candidate, fields)
    provenance = {"envelopes_attested": False,
                  "reference_image_profile_matches": False,
                  "reference_image_checked": reference_image is not None}
    provenance_errors = []

    if bool(reference_envelope) != bool(candidate_envelope):
        provenance_errors.append("both envelopes required; one is missing")
    elif reference_envelope and candidate_envelope:
        if not reference_csv or not candidate_csv:
            raise ValueError("CSV file paths required for envelope integrity validation")
        left = validate_envelope(reference_envelope, reference_csv, trace_type,
                                 len(reference), "reference")
        right = validate_envelope(candidate_envelope, candidate_csv, trace_type,
                                  len(candidate), "candidate")
        if (left["begin"], left["end"]) != (right["begin"], right["end"]):
            provenance_errors.append("capture boundaries differ")
        elif left["begin"] == left["end"]:
            provenance_errors.append("begin/end markers indistinguishable")
        else:
            provenance["envelopes_attested"] = True
        provenance["reference_build"] = left["build"]
        provenance["candidate_build"] = right["build"]
        provenance["boundaries"] = {"begin": left["begin"], "end": left["end"]}

    if reference_image is not None:
        image = verify_reference_image(reference_image)
        provenance["reference_image_profile_matches"] = image["match"]
        provenance["image"] = image
        if not image["match"]:
            provenance_errors.append("unpacked DOS v2.0 binary fingerprint mismatch")

    provenance["evidence_gate"] = (
        provenance["envelopes_attested"] and
        provenance["reference_image_profile_matches"] and
        not provenance_errors
    )
    matches = (reference_check["ok"] and candidate_check["ok"] and
               first_difference["equal"])
    if not reference_check["ok"]:
        reason = "invalid_reference_trace"
    elif not candidate_check["ok"]:
        reason = "invalid_candidate_trace"
    elif not first_difference["equal"]:
        reason = "first_divergence"
    elif provenance_errors:
        reason = "provenance_rejected"
    elif require_provenance and not provenance["evidence_gate"]:
        reason = "provenance_required"
    else:
        reason = ("trace_match_with_attested_provenance"
                  if provenance["evidence_gate"] else "trace_match_unsealed")

    accepted = matches and not provenance_errors and (
        provenance["evidence_gate"] if require_provenance else True)
    return {
        "ok": accepted, "verdict": reason,
        "trace_type": trace_type, "reference_count": len(reference),
        "candidate_count": len(candidate),
        "reference_validation": reference_check,
        "candidate_validation": candidate_check,
        "first_difference": first_difference,
        "provenance": provenance, "provenance_errors": provenance_errors,
        "original_runtime_verified": False,
        "note": ("Attested envelope and executable digest do not prove the "
                 "recorder actually observed every original-game event."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace_type", choices=["rng", "fast"])
    parser.add_argument("reference_csv")
    parser.add_argument("candidate_csv")
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=1)
    parser.add_argument("--allow-unknown-callers", action="store_true")
    parser.add_argument("--invocation", type=lambda x: int(x, 0))
    parser.add_argument("--tick-at-gate", type=lambda x: int(x, 0))
    parser.add_argument("--reference-envelope")
    parser.add_argument("--candidate-envelope")
    parser.add_argument("--reference-image")
    parser.add_argument("--require-provenance", action="store_true")
    args = parser.parse_args(argv)

    try:
        fields = (("caller", "before", "after", "result") if args.trace_type == "rng"
                  else ("invocation", "caller", "target"))
        reference = read_csv(args.reference_csv, fields)
        candidate = read_csv(args.candidate_csv, fields)
        report = compare_captures(
            args.trace_type, reference, candidate, seed=args.seed,
            strict_callers=not args.allow_unknown_callers,
            invocation=args.invocation, tick_at_gate=args.tick_at_gate,
            reference_csv=args.reference_csv, candidate_csv=args.candidate_csv,
            reference_envelope=args.reference_envelope,
            candidate_envelope=args.candidate_envelope,
            reference_image=args.reference_image,
            require_provenance=args.require_provenance)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
