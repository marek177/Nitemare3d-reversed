#!/usr/bin/env python3
"""Strict PASS320 ledger integrity audit. Does not infer code/data semantics.
UNEXECUTED in the 2026-11-11 authoring session; requires original inputs.
CSV contract: start,end,sha256,classification. Offsets are decimal or 0x-prefixed,
relative to the supplied canonical BIN; end is exclusive. Do not pass an EXE
until its mapping to the historical canonical BIN is established.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

EXPECTED = {
    "DEEP_VERIFIED": 0, "PARTIAL": 72014, "ALIGNMENT": 84,
    "NOP": 597, "EMBEDDED_TABLE": 752, "UNASSESSED_N3D": 0,
    "NON_CODE": 57295, "EXTERNAL_CRT_WORX": 40618,
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def number(value):
    value = value.strip()
    return int(value, 16 if value.lower().startswith("0x") else 10)

def audit(image, rows, expected_sha):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha):
        raise ValueError("Expected SHA-256 must come from the trusted historical manifest")
    if sha(image) != expected_sha.lower():
        raise ValueError("Canonical image SHA-256 mismatch")
    if len(image) != 171360:
        raise ValueError("Canonical image size differs from the historical baseline")
    if len(rows) != 1488:
        raise ValueError("Expected the complete historical 1488-interval ledger")
    cursor = 0
    counts = Counter()
    checked = []
    # Input must already be ordered; silently sorting could mask a ledger defect.
    for index, row in enumerate(rows, 2):
        start, end = number(row["start"]), number(row["end"])
        category = row["classification"]
        digest = row["sha256"].strip().lower()
        if category not in EXPECTED:
            raise ValueError(f"CSV line {index}: unmapped classification {category!r}")
        if start != cursor or not start < end <= len(image):
            raise ValueError(f"CSV line {index}: gap, overlap, empty or invalid bounds")
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or sha(image[start:end]) != digest:
            raise ValueError(f"CSV line {index}: interval hash mismatch")
        counts[category] += end - start
        checked.append({"start": start, "end": end, "length": end-start,
                        "sha256": digest, "classification": category,
                        "semantic_status": "NOT_REASSESSED",
                        "evidence_kind": "binary_integrity_only"})
        cursor = end
    if cursor != len(image):
        raise ValueError("Ledger does not cover the canonical image")
    if any(counts[k] != n for k, n in EXPECTED.items()):
        raise ValueError(f"Category totals differ: {dict(counts)}")
    return {"image_sha256": sha(image), "image_size": len(image),
            "interval_count": len(checked), "category_bytes": dict(counts),
            "semantic_promotions": 0, "runtime_tests": 0, "intervals": checked}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_bin", type=Path)
    parser.add_argument("ledger_csv", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.ledger_csv.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not {"start", "end", "sha256", "classification"} <= set(reader.fieldnames or []):
                raise ValueError("CSV requires start,end,sha256,classification")
            rows = list(reader)
        result = audit(args.canonical_bin.read_bytes(), rows, args.expected_sha256)
        # Output is created only after every validation gate passes.
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "integrity_audit.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        with (args.out_dir / "noncode_queue.csv").open("w", encoding="utf-8", newline="") as stream:
            fields = ["start", "end", "length", "sha256", "classification",
                      "semantic_status", "evidence_kind"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(r for r in result["intervals"] if r["classification"] == "NON_CODE")
    except (OSError, ValueError, KeyError, csv.Error) as error:
        parser.exit(2, f"Audit failed: {error}\n")
    print("Integrity PASS only; no semantic verification or runtime parity claimed.")

if __name__ == "__main__":
    main()
