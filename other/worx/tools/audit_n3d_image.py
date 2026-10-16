#!/usr/bin/env python3
"""Offline static checks for the Nitemare 3D DOS v2.0 unpacked MZ image.

This does not emulate, execute, or decompile the image and cannot certify 1:1 parity.
Input: full N3D_DOS_v2.0_IDA.EXE, not N3D-UNFU intermediate/raw image.
The exact hash of the *unpacked load image*, not the full .EXE, is the anchor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_IMAGE_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"
EXPECTED_IMAGE_SIZE = 0x29D60
EXPECTED_HEADER = 0x1C00
VENDOR = b"WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE"
REGIONS = {
    "n3d_worx_abi": (0x10BFC, 0x11EE6),
    "worx_owned": (0x15BF7, 0x1BDA1),
    "worx_80_buffer": (0x15BFE, 0x17BFF),
    "worx_static_tables": (0x17C00, 0x18A04),
    "worx_mixed_code": (0x18A05, 0x1BD92),
}
# machine code CALL FAR PTR16:16 = 9A <offset_lo,offset_hi,segment_lo,segment_hi>
KNOWN_CALLS = {
    "init_far_call": (0x11A6A, bytes.fromhex("9A7D2EBF15")),
    "shutdown_far_call": (0x10C6C, bytes.fromhex("9A662FBF15")),
}


def audit_file(path: Path, expected_sha256: str = EXPECTED_IMAGE_SHA256) -> dict:
    data = path.read_bytes()
    report = {
        "input_file": path.name,
        "input_bytes": len(data),
        "image_expected_sha256": expected_sha256,
        "statuses": {},
        "notes": ["Only verified structure, not ABI/device/audio behavioral parity."],
    }
    checks = report["statuses"]
    checks["mz_magic"] = data[:2] == b"MZ"
    if len(data) < 0x1C or not checks["mz_magic"]:
        report["status"] = "NOT_A_VALID_MZ"
        return report
    mz_header_paragraphs = struct.unpack_from("<H", data, 8)[0]
    header_size = mz_header_paragraphs * 16
    report["mz_header_bytes"] = header_size
    checks["header_size_match"] = (header_size == EXPECTED_HEADER)
    if not 0x1C <= header_size <= len(data):
        report["status"] = "INVALID_HEADER"
        return report
    image = data[header_size:]
    report["unpacked_image_bytes"] = len(image)
    report["unpacked_image_sha256"] = hashlib.sha256(image).hexdigest()
    checks["load_image_size_match"] = len(image) == EXPECTED_IMAGE_SIZE
    checks["load_image_sha256_match"] = report["unpacked_image_sha256"] == expected_sha256
    checks["vendor_literal_present"] = VENDOR in image
    vendor_position = image.find(VENDOR)
    report["vendor_offset_in_image"] = vendor_position if vendor_position != -1 else None
    checks["vendor_is_in_worx_tables"] = 0x17C00 <= vendor_position <= 0x18A04
    checks["neutral_pcm_buffer_bytes"] = (
        len(image) > 0x17BFF and
        all(b == 0x80 for b in image[0x15BFE:0x17C00])
    )
    for name, (offset, opcode) in KNOWN_CALLS.items():
        checks[name] = image[offset:offset + len(opcode)] == opcode
    report["regions"] = {
        name: {"first_image_offset": f"0x{lo:05X}",
               "last_image_offset": f"0x{hi:05X}",
               "bytes": hi - lo + 1,
               "in_range": hi < len(image)}
        for name, (lo, hi) in REGIONS.items()
    }
    checks["regions_fit_in_image"] = all(r["in_range"] for r in report["regions"].values())
    failures = [key for key, ok in checks.items() if not ok]
    report["failed_checks"] = failures
    report["status"] = "STATIC_IMAGE_IDENTIFIED" if not failures else "DIFFERENT_OR_INCOMPLETE_IMAGE"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Complete MZ file N3D_DOS_v2.0_IDA.EXE")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    report = audit_file(args.image)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{args.image.name}: {report['status']}")
        print(f"Image bytes: {report.get('unpacked_image_bytes')} sha256={report.get('unpacked_image_sha256')}")
        for name, ok in report["statuses"].items():
            print(("[PASS] " if ok else "[FAIL] ") + name)
        print("NOTE: a fully PASS result is structural-only, not 100% reconstruction.")
    return 0 if report["status"] == "STATIC_IMAGE_IDENTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
