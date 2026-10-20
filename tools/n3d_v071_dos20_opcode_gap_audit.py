#!/usr/bin/env python3
"""Audited DOS v2.0 renderer image: distinguish STATIC bytes from RUNTIME coverage.

Accepts only the SHA-256-pinned original *unpacked* N3D-E-20.EXE.
No proprietary opcode bytes are printed or copied into the JSON proof.
This is a source-byte census; it cannot establish the semantics/reachability
of unexecuted code or original-vs-port framebuffer parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXE_SHA = "552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301"
EXE_SIZE = 116606
FEFA_TRACE_SHA = "96cbfb9580f39715ff74f6b991f8645efd40e1c5771da55ec5a05ff97ef6ca12"
IMAGE_HEADER_BYTES = 0x200

# All addresses are DOS v2.0 *load image* offsets; MZ file offset = +0x200.
ROUTINES = {
    "CAB8_projection": (0xCAB8, 0xCEDB, 1009),
    "FEFA_owner": (0xFEFA, 0x1003D, 324),
    "1021E_visibility": (0x1021E, 0x104BD, 656),
}
RUNTIME_HOLES = {
    "CAB8_projection": ((0xCD9D, 0xCDCF),),
    "FEFA_owner": (),
    "1021E_visibility": (
        (0x10408, 0x1040B),
        (0x1043D, 0x10440),
        (0x10472, 0x10475),
        (0x104A6, 0x104A9),
    ),
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def header_size(raw: bytes) -> int:
    if len(raw) < 0x20 or raw[:2] != b"MZ":
        raise ValueError("Not an MZ executable")
    return int.from_bytes(raw[8:10], "little") * 16


def verify_original_exe(raw: bytes) -> None:
    if len(raw) != EXE_SIZE:
        raise ValueError(f"Wrong original EXE size: {len(raw)}")
    if sha256(raw) != EXE_SHA:
        raise ValueError("Unrecognized EXE SHA-256; do not mix DOS builds")
    if header_size(raw) != IMAGE_HEADER_BYTES:
        raise ValueError("Unexpected MZ header: image offsets cannot be mapped")


def image_bytes(raw: bytes, first: int, last: int, base: int = IMAGE_HEADER_BYTES) -> bytes:
    if first < 0 or last < first or base < 0:
        raise ValueError("Invalid offset range")
    lower, upper = base + first, base + last + 1
    if upper > len(raw):
        raise ValueError("Image range exceeds original EXE")
    return raw[lower:upper]


def audit_bytes(raw: bytes, *, base: int = IMAGE_HEADER_BYTES) -> dict:
    """Operate on supplied bytes; caller must verify SHA for original claims."""
    result: dict = {}
    total_hole_bytes = 0
    for name, (start, end, expected_trace_covered) in ROUTINES.items():
        whole = image_bytes(raw, start, end, base)
        holes = []
        hole_size = 0
        last_end = start - 1
        for hstart, hend in RUNTIME_HOLES[name]:
            if hstart <= last_end or not (start <= hstart <= hend <= end):
                raise AssertionError("Overlapping/out-of-range hole declaration")
            piece = image_bytes(raw, hstart, hend, base)
            hole_size += len(piece)
            holes.append({
                "image_range": [f"0x{hstart:05X}", f"0x{hend:05X}"],
                "file_range": [f"0x{base+hstart:05X}", f"0x{base+hend:05X}"],
                "size": len(piece),
                "sha256": sha256(piece),
                "all_zero": not any(piece),
                "interpretation": "raw_static_bytes_only",
            })
            last_end = hend
        if len(whole) - hole_size != expected_trace_covered:
            raise AssertionError("Archived dynamic coverage arithmetic changed")
        total_hole_bytes += hole_size
        record = {
            "image_range": [f"0x{start:05X}", f"0x{end:05X}"],
            "whole_function_bytes": len(whole),
            "original_trace_bytes_observed": expected_trace_covered,
            "original_trace_bytes_missing": hole_size,
            "static_bytes_available": len(whole),
            "sha256_whole": sha256(whole),
            "holes": holes,
        }
        if name == "FEFA_owner":
            record["matches_archived_FEFA_trace_hash"] = sha256(whole) == FEFA_TRACE_SHA
        result[name] = record
    return {
        "evidence": "STATIC_BYTES_ONLY",
        "semantics_of_missing_bytes": "UNVERIFIED",
        "missing_byte_runtime_reachability": "UNVERIFIED",
        "original_vs_port_indexed_framebuffer_parity": "NOT_TESTED",
        "mz_header_bytes": base,
        "routines": result,
        "routine_bytes": sum(e - s + 1 for s, e, _ in ROUTINES.values()),
        "runtime_missing_bytes": total_hole_bytes,
        "warning": "Exact original EXE bytes do not establish that these paths execute or that the remake renders pixel-for-pixel.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", required=True, type=Path, help="Exact original unpacked DOS2 EXE")
    ap.add_argument("--out", type=Path, help="Optional JSON destination")
    args = ap.parse_args()
    try:
        raw = args.exe.read_bytes()
        verify_original_exe(raw)
        proof = audit_bytes(raw)
        proof["original_exe_sha256"] = EXE_SHA
        proof["original_exe_bytes"] = EXE_SIZE
        # The complete FEFA trace was recovered before this static pass.
        if not proof["routines"]["FEFA_owner"]["matches_archived_FEFA_trace_hash"]:
            raise ValueError("FEFA EXE bytes disagree with original trace fingerprint")
        output = json.dumps(proof, indent=2, ensure_ascii=False) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (OSError, ValueError, AssertionError) as exc:
        ap.exit(2, f"FAIL (no audit accepted): {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
