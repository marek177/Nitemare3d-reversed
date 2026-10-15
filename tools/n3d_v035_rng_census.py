#!/usr/bin/env python3
"""Fingerprint-gated DOS v2.0 direct RNG far-call census and local consumers.

Read-only analysis of a user-owned UNPACKED MZ executable. Counts literal
9A A0 01 BA 0F far-CALL opcodes across the full load image, then verifies
known instruction windows and the damage jump-table wiring. It does NOT
observe original execution, prove all indirect calls or validate DEMO timing.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_IMAGE_LENGTH = 171360
EXPECTED_IMAGE_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"
RNG_FAR_CALL_OPCODE = bytes.fromhex("9a a0 01 ba 0f")
# Byte offsets in the canonical DOS v2.0 UNPACKED load image.
DIRECT_CALLS = (
    0x2478, 0x525E, 0x5582, 0x5666, 0x56A6, 0x573F, 0x58A7,
    0x85AD, 0x8860, 0x886C, 0x887C, 0x9A68, 0x9A77,
    0x9C98, 0x9CC2, 0x9D6E, 0x9F0C, 0x9F36,
    0x9FE3, 0xA047, 0xA12B, 0xB276,
)

# 87D8 dispatch: class at OBJECT+06, class-0x08, range 0..0x16,
# CS near jump via table 045E. The table lives at image offset 882E
# because this CODE segment starts at image offset 83D0.
DAMAGE_TABLE_SITE = 0x882E
DAMAGE_JMP_OPCODE = 0x8829
DAMAGE_CODE_SEGMENT_IMAGE_BASE = 0x83D0
DAMAGE_BRANCH_TARGETS = (
    0x8860, 0x886C, 0x886C, 0x8876, 0x889D,
    0x885C, 0x885C, 0x885C, 0x885C,
    0x887C, 0x887C, 0x887C, 0x887C,
    0x885C, 0x8886, 0x885C, 0x885C, 0x889A,
    0x885C, 0x885C, 0x885C, 0x889D, 0x889D,
)
assert len(DAMAGE_BRANCH_TARGETS) == 0x17

# Small, exact machine-code witnesses. These prove the stated local operations
# only; helper side effects and class names remain scoped to other reports.
WITNESSES = {
    "damage_class_table_jump": (0x8829, "2e ff a7 5e 04"),
    "damage_rng_mask_07": (0x8860, "9a a0 01 ba 0f 25 07 00"),
    "damage_rng_mask_0f": (0x886C, "9a a0 01 ba 0f 25 0f 00"),
    "damage_rng_mask_1f": (0x887C, "9a a0 01 ba 0f 25 1f 00"),
    "guard_state_7_or_8_gate": (0x5572, "26 8a 44 0b 2a e4 2d 07 00"),
    "guard_wake_draw_mod8": (0x5582, "9a a0 01 ba 0f b9 08 00 99 f7 f9"),
    "guard_wake_timer_and_state": (0x5590, "26 89 54 06 26 c6 44 0b 01"),
    "projected_variant_draw_and_mask7": (0xB276, "9a a0 01 ba 0f 24 07"),
    "projected_variant_index_write": (0xB280, "26 88 44 02"),
    "projected_variant_reject_empty": (0xB293, "80 7e ff 00 74 dd"),
    "projected_variant_frame_write": (0xB29C, "8e 46 08 26 88 44 03"),
    "sfx_variant_17_mod3": (0x9C98, "9a a0 01 ba 0f b9 03 00 99 f7 f9 8b f2 83 c6 17"),
    "sfx_variant_4b_mod4": (0x9CC2, "9a a0 01 ba 0f b9 04 00 99 f7 f9 8b f2 83 c6 4b"),
    "sfx_variant_0b_mod3": (0x9D6E, "9a a0 01 ba 0f b9 03 00 99 f7 f9 8b f2 83 c6 0b"),
    "sfx_variant_38_mod3": (0x9F0C, "9a a0 01 ba 0f b9 03 00 99 f7 f9 8b f2 83 c6 38"),
    "sfx_variant_36_mod2": (0x9F36, "9a a0 01 ba 0f b9 02 00 99 f7 f9 8b f2 83 c6 36"),
    "position_draw_mod62": (0x9A68, "9a a0 01 ba 0f b9 3e 00 99 f7 f9 89 16 32 36"),
    "position_draw_mod36": (0x9A77, "9a a0 01 ba 0f b9 24 00 99 f7 f9 89 16 30 36"),
    "effect_timer_mod240_plus160": (0xA12B, "9a a0 01 ba 0f b9 f0 00 99 f7 f9 81 c2 a0 00"),
    "resource_slot1_mod7_dead_compare": (0x9FE3, "9a a0 01 ba 0f b9 07 00 99 f7 f9 8b f2 3b f1 74 ef"),
    "resource_slot2_mod7_dead_compare": (0xA047, "9a a0 01 ba 0f b9 07 00 99 f7 f9 8b f2 3b f1 74 ef"),
    "resource_slot1_real_empty_retry": (0xA00C, "38 6f 4b 74 d2"),
    "resource_slot2_real_empty_retry": (0xA070, "38 6f 3b 74 d2"),
}


def load_image(raw):
    if len(raw) < 64 or raw[:2] != b"MZ":
        raise ValueError("expected unpacked DOS MZ executable")
    header_bytes = struct.unpack_from("<H", raw, 8)[0] * 16
    if not 28 <= header_bytes < len(raw):
        raise ValueError("invalid DOS MZ header length")
    return raw[header_bytes:]


def find_opcode_sites(image):
    result = []
    start = 0
    while True:
        at = image.find(RNG_FAR_CALL_OPCODE, start)
        if at == -1:
            return tuple(result)
        result.append(at)
        start = at + 1


def damage_table_targets(image):
    if image[DAMAGE_JMP_OPCODE:DAMAGE_JMP_OPCODE+5] != bytes.fromhex("2e ff a7 5e 04"):
        raise ValueError("damage class jump instruction differs from canonical")
    end = DAMAGE_TABLE_SITE + 2 * len(DAMAGE_BRANCH_TARGETS)
    if len(image) < end:
        raise ValueError("truncated class jump table")
    return tuple(
        DAMAGE_CODE_SEGMENT_IMAGE_BASE +
        struct.unpack_from("<H", image, DAMAGE_TABLE_SITE+i*2)[0]
        for i in range(len(DAMAGE_BRANCH_TARGETS))
    )


def validate_sites(image):
    actual = find_opcode_sites(image)
    missing = sorted(set(DIRECT_CALLS) - set(actual))
    extra = sorted(set(actual) - set(DIRECT_CALLS))
    targets = damage_table_targets(image)
    windows = {
        name: image[site:site+len(bytes.fromhex(blob))] == bytes.fromhex(blob)
        for name, (site, blob) in WITNESSES.items()
    }
    return {
        "ok": not missing and not extra and targets == DAMAGE_BRANCH_TARGETS and
              all(windows.values()),
        "observed_direct_opcode_occurrences": len(actual),
        "expected_direct_opcode_occurrences": len(DIRECT_CALLS),
        "missing_original_callsite_offsets": missing,
        "unexpected_raw_signature_offsets": extra,
        "damage_jump_table_matches": targets == DAMAGE_BRANCH_TARGETS,
        "damage_class_08_entry": targets[0],
        "damage_class_09_entry": targets[1],
        "damage_class_0a_entry": targets[2],
        "damage_class_11_to_14_entries": list(targets[9:13]),
        "witnesses": windows,
    }


def verify_original(raw):
    image = load_image(raw)
    digest = hashlib.sha256(image).hexdigest()
    identified = len(image) == EXPECTED_IMAGE_LENGTH and digest == EXPECTED_IMAGE_SHA256
    report = {
        "fingerprint_matches": identified,
        "image_length": len(image),
        "image_sha256": digest,
        "ok": False,
        "original_game_executed": False,
        "total_dynamic_rng_order_verified": False,
        "indirect_rng_census_closed": False,
    }
    if not identified:
        report["verdict"] = "incorrect_original_executable"
        return report
    details = validate_sites(image)
    report.update(details)
    report["verdict"] = ("static_22_callsite_census_verified"
                         if report["ok"] else "static_instruction_or_table_divergence")
    report["note"] = ("22 literal direct far-CALL opcode occurrences including "
                      "damage classes 08/09/0A and 11..14; data xrefs checked "
                      "for new callers. Neither indirect RNG calls nor per-tick "
                      "reachability and full seed-1 chronology were measured.")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dos20_unpacked_executable", type=Path)
    args = parser.parse_args(argv)
    try:
        report = verify_original(args.dos20_unpacked_executable.read_bytes())
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
