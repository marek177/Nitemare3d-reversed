#!/usr/bin/env python3
"""Check v0.79 research-addendum metadata. Does not execute the original game."""
import argparse
import json
from pathlib import Path

SCHEMA = "n3d.v079-evidence-addendum.v1"
STATUSES = {
    "BOUNDED_ARCHIVED_PROOF", "REPORTED_PENDING_ARTIFACT_IMPORT",
    "LIBRARY_REPORT_NOT_REPLAYED"
}

def audit(document, root):
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise ValueError("unexpected schema")
    if document.get("global_original_vs_remake_parity") is not False:
        raise ValueError("false or missing global parity guard")
    if document.get("original_runtime_reexecuted") is not False:
        raise ValueError("false or missing runtime rerun guard")
    rows = document.get("items")
    if not isinstance(rows, list) or not rows:
        raise ValueError("empty evidence inventory")
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("non-object record")
        ident = row.get("id")
        if not isinstance(ident, str) or ident in ids or not ident:
            raise ValueError("duplicate or missing evidence id")
        ids.add(ident)
        if row.get("status") not in STATUSES:
            raise ValueError("invalid evidence status: " + ident)
        if not row.get("domain") or not row.get("blocker"):
            raise ValueError("missing domain/blocker: " + ident)
        source = row.get("source")
        if source is not None:
            if not isinstance(source, str) or not source.startswith("docs/") or ".." in Path(source).parts:
                raise ValueError("invalid relative evidence source")
            if not (root / source).is_file():
                raise ValueError("missing evidence file: " + source)
        if row.get("status") == "REPORTED_PENDING_ARTIFACT_IMPORT" and source is not None:
            raise ValueError("pending item claims a checked source")
        if not isinstance(row.get("metrics"), dict):
            raise ValueError("missing metrics")
    noncode = next((x for x in rows if x["id"] == "NONCODE_20261119"), None)
    if noncode:
        m = noncode["metrics"]
        if m["classified_bytes"] + m["unknown_bytes"] != m["total_bytes"]:
            raise ValueError("NON-CODE byte arithmetic inconsistent")
        if not 0 <= m["new_deep_verified_bytes"] <= m["classified_bytes"]:
            raise ValueError("impossible DEEP_VERIFIED delta")
    cedc = next((x for x in rows if x["id"] == "V079_CEDC"), None)
    if cedc:
        m = cedc["metrics"]
        if sum(m["branches"]) != m["calls"] or m["linked_columns"] % 304:
            raise ValueError("CEDC branch or frame count inconsistent")
    return {"status": "METADATA_ONLY_PASS", "items": len(rows),
            "original_reexecution": False, "global_parity": False}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--input", type=Path, default=Path("research/v079_20261120_evidence.json"))
    args = ap.parse_args()
    target = args.input if args.input.is_absolute() else args.root / args.input
    try:
        result = audit(json.loads(target.read_text(encoding="utf-8")), args.root)
    except (ValueError, OSError, KeyError, TypeError) as error:
        ap.error(str(error))
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
