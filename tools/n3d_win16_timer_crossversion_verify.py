#!/usr/bin/env python3
"""Dedupe/compare the pinned Win16 1.8 and 1.10 timer anchor ledgers.

This is an ORIGINAL-EVIDENCE-METADATA comparison, not an execution of either
original EXE and not a byte-level closure of the entire timer initializer.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "other/n3d/builds_12/static_byte_evidence"
ANCHORS = EVIDENCE / "N3D_Win16_NE3_anchors.csv"
IMPORTS = EVIDENCE / "N3D_Win16_reloc_anchored_import_CALLs.csv"
SEGMENTS = EVIDENCE / "N3D_Win16_NE_segments.csv"

KNOWN_ROLES = ("read_time", "slow_clock", "frame_clock", "calibrate")
IMPORTED_CLOCK = (("MMSYSTEM", 604), ("MMSYSTEM", 605),
                  ("MMSYSTEM", 606), ("MMSYSTEM", 607), ("USER", 13))
EXPECTED_DELTA = 0xAE


def load_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(rows):
    if len(rows) != 2:
        raise ValueError("comparison requires exactly two 1.8/1.10 records")
    a, b = rows
    if b["offset"] - a["offset"] != EXPECTED_DELTA:
        raise ValueError("cross-version displacement is not +0xAE")
    return True


def analyze(anchor_rows, import_rows, segment_rows):
    anchors = {}
    imports = {}
    segments = {}
    for version in ("1.8", "1.10"):
        anchors[version] = {
            r["behavior"]: r
            for r in anchor_rows if r["Win16_version"] == version
        }
        imports[version] = {
            (r["import_module"], int(r["import_ordinal"])):
                int(r["caller_ip"], 0)
            for r in import_rows
            if r["Win16_version"] == version
            and r["caller_segment"] == "3"
            and ((r["import_module"], int(r["import_ordinal"]))
                 in IMPORTED_CLOCK)
        }
        segments[version] = next(
            (r for r in segment_rows
             if r["Win16_version"] == version and r["segment"] == "3"),
            None
        )
        if segments[version] is None:
            raise ValueError("Missing NE segment-3 layout for " + version)

    functions = []
    for role in KNOWN_ROLES:
        a, b = anchors["1.8"].get(role), anchors["1.10"].get(role)
        if a is None or b is None:
            raise ValueError("Missing original anchor: " + role)
        off_a, off_b = int(a["offset"], 0), int(b["offset"], 0)
        if (off_b - off_a) != EXPECTED_DELTA:
            raise ValueError("Function displacement mismatch: " + role)
        by_a, by_b = bytes.fromhex(a["first_16_bytes"]), bytes.fromhex(b["first_16_bytes"])
        if len(by_a) != 16 or by_a != by_b:
            raise ValueError("First 16 bytes mismatch: " + role)
        functions.append({
            "function": role,
            "win18": f"3:{off_a:04X}",
            "win110": f"3:{off_b:04X}",
            "delta": f"+0x{EXPECTED_DELTA:X}",
            "matched_instruction_prefix_bytes": 16,
            "sha256_scope": "prefix only",
        })

    api_sites = []
    for key in IMPORTED_CLOCK:
        a, b = imports["1.8"].get(key), imports["1.10"].get(key)
        if a is None or b is None:
            raise ValueError("Missing imported API site: " + str(key))
        if b - a != EXPECTED_DELTA:
            raise ValueError("Imported API site displacement mismatch: " + str(key))
        api_sites.append({
            "api": f"{key[0]}.{key[1]}",
            "win18": f"3:{a:04X}",
            "win110": f"3:{b:04X}",
            "delta": f"+0x{EXPECTED_DELTA:X}",
            "evidence": "import ordinal fixup-backed callsite record",
        })

    seg_a, seg_b = segments["1.8"], segments["1.10"]
    layout = {
        "win18": {"raw_file_offset": int(seg_a["raw_file_offset"]),
                  "segment_bytes": int(seg_a["bytes"]),
                  "segment_sha256": seg_a["sha256"]},
        "win110": {"raw_file_offset": int(seg_b["raw_file_offset"]),
                   "segment_bytes": int(seg_b["bytes"]),
                   "segment_sha256": seg_b["sha256"]},
    }
    if layout["win18"]["segment_sha256"] == layout["win110"]["segment_sha256"]:
        raise ValueError("Expected nonidentical full NE3 segment hashes")

    return {
        "scope": "Static evidence CSV only; not a fresh original Win16 1.10 byte dump",
        "builds": ("1.8", "1.10"),
        "offset_displacement": "+0xAE",
        "equal_function_prefixes": functions,
        "import_relocation_sites": api_sites,
        "matched_16_byte_prefixes": len(functions),
        "matched_prefix_bytes_total": 16 * len(functions),
        "matched_import_callsite_offsets": len(api_sites),
        "ne3_layout": layout,
        "timer_endperiod_operand_win18": "PUSH WORD PTR SS:[BP-2] - original byte verified",
        "timer_endperiod_operand_win110": None,
        "win110_stack_operand_closed": False,
        "win110_near_far_indirect_callgraph_closed": False,
        "limitations": [
            "The equal 16-byte prefixes do not prove complete routine equality.",
            "A +0xAE address shift across five import callsites is not a full binary diff.",
            "The Win16 1.8 [BP-2] historical defect cannot be automatically assigned to 1.10.",
            "V058-10 indirect/fixup-backed callgraph is still open.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON file")
    args = parser.parse_args()
    report = analyze(load_rows(ANCHORS), load_rows(IMPORTS), load_rows(SEGMENTS))
    result = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
        print(f"Written {args.output} — 4 aligned prefixes and 5 imports; D6BE still OPEN")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
