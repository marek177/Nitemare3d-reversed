#!/usr/bin/env python3
"""Fingerprint-gated DOS v2.0 versus Win16 v1.10 PUSH updater comparison.

Original bytes are read locally, not embedded/distributed. Equality after
masking address operands proves a scoped static control-flow match, NOT that
the original games were executed or share total runtime/timing behavior.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

DOS_IMAGE_SIZE = 171360
DOS_IMAGE_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"
WIN_RAW_SIZE = 230400
WIN_RAW_SHA256 = "12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481"
DOS_START = 0x0E50
WIN_SEG3_START = 0x2210
LENGTH = 0x124

# Offsets within the 292-byte updater, all verified instruction operands.
# No opcode, instruction prefix, conditional branch displacement or immediate
# gameplay value is whitelisted. Includes one 4-byte far-call target operand.
OPERAND_SPANS = (
    (0x007, 2, "PUSH pool data segment"),
    (0x00E, 2, "PUSH pool base"),
    (0x02F, 2, "OBJECT pool base"),
    (0x032, 2, "OBJECT pool segment"),
    (0x070, 2, "MAP cell byte base"),
    (0x073, 2, "MAP byte segment"),
    (0x091, 2, "destination OBJECT property array"),
    (0x101, 4, "sort/reindex far target"),
    (0x115, 2, "indirect pool segment selector"),
)

DOS_WITNESSES = {
    "start_wall_property_bit02": (0x0E21, "f6 87 0c d0 02"),
    "start_countdown8": (0x0E43, "26 c6 47 04 08"),
    "push_record_stride6": (0x0F5F, "83 c6 06"),
    "block_on_target_object_flags06": (0x0EF5, "f6 46 f7 06 75 64"),
    "old_object_layer_byte_read": (0x0F0C, "26 8a 47 01"),
    "old_object_layer_byte_clear": (0x0F1E, "26 c6 47 01 00"),
    "coordinate_commit": (0x0F23, "8b 46 f4 c4 5e fc"),
    "sort_far_call": (0x0F50, "9a 5e 01 ea 0a"),
    "counter_decrement_after_call": (0x0F5B, "26 fe 4c 04"),
    "fastcall_to_push_updater": (0xC172, "9a 50 0e 00 00"),
    "sort_helper_enter": (0xAFFE, "c8 06 00 00"),
    "sort_helper_x_index": (0xB007, "26 8b 7f 14"),
    "sort_helper_y_index": (0xB0C1, "26 8b 7f 16"),
}
WIN_WITNESSES = {
    "start_wall_property_bit02": (0x21E0, "f6 87 94 7e 02"),
    "start_countdown8": (0x2202, "26 c6 47 04 08"),
    "push_record_stride6": (0x231F, "83 c6 06"),
    "block_on_target_object_flags06": (0x22B5, "f6 46 f7 06 75 64"),
    "old_object_layer_byte_read": (0x22CC, "26 8a 47 01"),
    "old_object_layer_byte_clear": (0x22DE, "26 c6 47 01 00"),
    "coordinate_commit": (0x22E3, "8b 46 f4 c4 5e fc"),
    "sort_far_call": (0x2310, "9a a6 c9 c2 21"),
    "counter_decrement_after_call": (0x231B, "26 fe 4c 04"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dos_unpacked_image(raw):
    if len(raw) < 0x40 or raw[:2] != b"MZ":
        raise ValueError("DOS input must be an MZ executable")
    header_bytes = struct.unpack_from("<H", raw, 8)[0] * 16
    if not 28 <= header_bytes < len(raw):
        raise ValueError("invalid DOS MZ header length")
    return raw[header_bytes:]


def win_ne_segment(raw, segment=3):
    if len(raw) < 0x40 or raw[:2] != b"MZ":
        raise ValueError("Win16 input must be an NE executable with MZ stub")
    ne = struct.unpack_from("<I", raw, 0x3c)[0]
    if ne + 0x40 > len(raw) or raw[ne:ne+2] != b"NE":
        raise ValueError("no valid Win16 NE header")
    count = struct.unpack_from("<H", raw, ne+0x1c)[0]
    table = ne + struct.unpack_from("<H", raw, ne+0x22)[0]
    shift = struct.unpack_from("<H", raw, ne+0x32)[0]
    if not 1 <= segment <= count or shift > 15 or table + count*8 > len(raw):
        raise ValueError("invalid Win16 NE segment table")
    unit, length = struct.unpack_from("<HH", raw, table+(segment-1)*8)
    if not unit:
        raise ValueError("NE segment has no file offset")
    offset = unit << shift
    length = length or 65536
    if offset+length > len(raw):
        raise ValueError("NE segment overflows executable")
    return raw[offset:offset+length]


def byte_windows(image, witnesses):
    return {
        name: image[at:at+len(bytes.fromhex(code))] == bytes.fromhex(code)
        for name, (at, code) in witnesses.items()
    }


def compare_masked(dos_image, win_seg3):
    dos = dos_image[DOS_START:DOS_START+LENGTH]
    win = win_seg3[WIN_SEG3_START:WIN_SEG3_START+LENGTH]
    if len(dos) != LENGTH or len(win) != LENGTH:
        raise ValueError("one PUSH updater body is incomplete")
    allowed = {
        pos
        for start, length, _label in OPERAND_SPANS
        for pos in range(start, start+length)
    }
    if len(allowed) != 20 or max(allowed) >= LENGTH:
        raise ValueError("invalid explicit operand mask")
    changed = [i for i, (left, right) in enumerate(zip(dos, win)) if left != right]
    invalid = [i for i in changed if i not in allowed]
    return {
        "updater_length": LENGTH,
        "identical_bytes": LENGTH-len(changed),
        "different_bytes": len(changed),
        "relocatable_operand_positions": len(allowed),
        "operand_groups": [
            {"relative_offset": at, "length": length, "meaning": label}
            for at, length, label in OPERAND_SPANS
        ],
        "unexpected_difference_offsets": invalid,
        "masked_control_flow_equal": not invalid,
        "exact_original_pattern": set(changed) == allowed,
    }


def verify_pair(dos_raw, win_raw):
    image = dos_unpacked_image(dos_raw)
    # Require exact input identity before applying any code addresses.
    dos_ok = len(image) == DOS_IMAGE_SIZE and digest(image) == DOS_IMAGE_SHA256
    win_ok = len(win_raw) == WIN_RAW_SIZE and digest(win_raw) == WIN_RAW_SHA256
    base = {
        "dos_image_fingerprint": dos_ok,
        "win16_file_fingerprint": win_ok,
        "verified_static_control_flow": False,
        "original_runtime_executed": False,
        "runtime_1to1_confirmed": False,
    }
    if not dos_ok or not win_ok:
        base["verdict"] = "build_fingerprint_mismatch"
        return base
    seg3 = win_ne_segment(win_raw, 3)
    comparison = compare_masked(image, seg3)
    dos_sites = byte_windows(image, DOS_WITNESSES)
    win_sites = byte_windows(seg3, WIN_WITNESSES)
    passed = (comparison["masked_control_flow_equal"] and
              comparison["exact_original_pattern"] and
              all(dos_sites.values()) and all(win_sites.values()))
    base.update({
        "verdict": "push_static_match" if passed else "binary_opcode_divergence",
        "verified_static_control_flow": passed,
        "comparison": comparison,
        "dos20_opcode_witnesses": dos_sites,
        "win16_opcode_witnesses": win_sites,
        "unclosed": ("original runtime event order, callbacks/reentrancy, dynamic "
                     "collision flag construction, full general OBJECT scheduler"),
    })
    return base


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dos20", type=Path, required=True,
                        help="your original DOS v2.0 unpacked MZ file")
    parser.add_argument("--win16", type=Path, required=True,
                        help="your original Win16 v1.10 NE file")
    args = parser.parse_args(argv)
    try:
        report = verify_pair(args.dos20.read_bytes(), args.win16.read_bytes())
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verified_static_control_flow"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
