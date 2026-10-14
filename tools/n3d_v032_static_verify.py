#!/usr/bin/env python3
"""Read-only v0.32 Nitemare 3D original-byte proof; never claims runtime parity."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

# DOS hashes are for the unpacked MZ load image; v1.2 is a PACKED full file.
# Win16 hash is the entire NE file. Original assets are not distributed.
PROFILES = {
    "dos10": ("mz-image", 154448, "113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a"),
    "dos12": ("mz-raw", 115856, "f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5"),
    "dos19": ("mz-image", 171296, "e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e"),
    "dos20": ("mz-image", 171360, "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"),
    "win16": ("ne-raw", 230400, "12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481"),
}
# Exact short opcode windows. The preceding build fingerprint is mandatory;
# matching a byte pattern alone is not evidence of executable identity.
WIN16_SEG3 = {
    "push_wall_property_forbidden_bit_02": (0x21E0, "f6 87 94 7e 02 75 25"),
    "save_block_94_bytes_from_4be8": (0x55A7, "6a 5e 68 e8 4b"),
    "pain_old_state_to_next_if_nonzero": (0x8290, "26 88 44 0c"),
    "pain_enter_state_15": (0x8297, "26 c6 44 0b 15"),
    "pain_invalidate_direction_cache": (0x81F3, "26 c6 44 12 08"),
    "dracula_class_14": (0xA16D, "26 c6 44 06 14"),
    "dracula_state_08": (0xA17A, "26 c6 45 0b 08"),
    "dracula_nextstate_02": (0xA17F, "26 c6 45 0c 02"),
    "dracula_timer_1": (0xA184, "26 c7 45 06 01 00"),
    "demo_double_step_bit": (0x9903, "24 20 74 07"),
    "demo_unit_step_bit": (0x992B, "24 40 74 05"),
    "demo_unit_move_override": (0x992F, "c7 46 fc 01 00"),
    "demo_unit_turn_override": (0x993B, "be 01 00"),
    "projectile_pool_count_8": (0x9AC2, "83 ff 08 75 05"),
    "projectile_full_pool_early_return": (0x9AC7, "32 c0 5e 5f cb"),
    "projectile_ammo_helper_below_guard": (0x9ACC, "9a 7c a9"),
}
DOS20_IMAGE = {
    "door_obstruction_check": (0x0A83, "26 80 7f 01 00 75 42"),
    "door_rearm_retry_4": (0x0ACF, "26 c7 44 0a 04 00"),
    "panel_step_plus2": (0x0BDD, "b9 02 00 eb 03"),
    "panel_step_minus2": (0x0BE2, "b9 fe ff"),
    "panel_commit_delta": (0x0BF4, "01 0d 8b 5e f4 01 0f"),
    "panel_state2_completion_test": (0x0C02, "26 83 7c 08 02"),
    "panel_cleanup_clear_wall_bit": (0x0D8D, "36 80 67 05 fe"),
    "panel_cleanup_clear_map_object": (0x0DBC, "c4 5c 08 26 c6 47 01 00"),
}
SAVE_SLOT_SIZE = 0xD6E7
SAVE_HP_OFFSET = 0x2035 + (0x4C1D - 0x4BE8)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def mz_image(raw):
    if len(raw) < 0x40 or raw[:2] != b"MZ":
        raise ValueError("not a complete MZ file")
    header_size = struct.unpack_from("<H", raw, 8)[0] * 16
    if header_size < 28 or header_size >= len(raw):
        raise ValueError("bad MZ header size")
    return raw[header_size:]


def ne_segment(raw, number):
    if len(raw) < 0x40 or raw[:2] != b"MZ":
        raise ValueError("missing NE MZ stub")
    ne = struct.unpack_from("<I", raw, 0x3c)[0]
    if ne + 0x40 > len(raw) or raw[ne:ne+2] != b"NE":
        raise ValueError("bad NE header")
    count = struct.unpack_from("<H", raw, ne+0x1c)[0]
    table = ne + struct.unpack_from("<H", raw, ne+0x22)[0]
    shift = struct.unpack_from("<H", raw, ne+0x32)[0]
    if not 1 <= number <= count or shift > 15 or table+count*8 > len(raw):
        raise ValueError("invalid NE segment table")
    units, size = struct.unpack_from("<HH", raw, table+(number-1)*8)
    if units == 0:
        raise ValueError("segment has no file data")
    offset = units << shift
    size = size or 65536
    if offset+size > len(raw):
        raise ValueError("segment exceeds file")
    return raw[offset:offset+size]


def check_sites(image, sites):
    return {name: image[off:off+len(bytes.fromhex(code))] == bytes.fromhex(code)
            for name, (off, code) in sites.items()}


def verify(name, raw):
    kind, expected_size, expected_sha = PROFILES[name]
    if kind == "mz-image":
        image = mz_image(raw)
    elif kind == "mz-raw":
        if raw[:2] != b"MZ":
            raise ValueError("packed candidate missing MZ")
        image = raw
    else:
        ne_segment(raw, 3)
        image = raw
    valid = len(image) == expected_size and sha256(image) == expected_sha
    sites = {}
    if valid and name == "win16":
        sites = check_sites(ne_segment(raw, 3), WIN16_SEG3)
    if valid and name == "dos20":
        sites = check_sites(image, DOS20_IMAGE)
    return {"ok": valid and all(sites.values()), "fingerprint_valid": valid,
            "size": len(image), "sha256": sha256(image), "scope": kind,
            "opcode_witnesses": sites, "original_runtime_verified": False}


def inspect_save(data, slot=0):
    if slot < 0 or len(data) % SAVE_SLOT_SIZE:
        raise ValueError("not a fixed-size Win16 v1.10 USER.SAV container")
    base = SAVE_SLOT_SIZE*slot
    if base+SAVE_SLOT_SIZE > len(data) or struct.unpack_from("<I", data, base)[0] != SAVE_SLOT_SIZE:
        raise ValueError("missing slot or bad size marker")
    return {"slot": slot, "hp_absolute_file_offset": base+SAVE_HP_OFFSET,
            "hp_observed": data[base+SAVE_HP_OFFSET], "load_timing_verified": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in PROFILES:
        p.add_argument("--"+name, type=Path)
    p.add_argument("--save", type=Path)
    p.add_argument("--slot", type=int, default=0)
    args = p.parse_args(argv)
    report = {"original_runtime_executed": False, "profiles": {}, "save": None}
    for name in PROFILES:
        file = getattr(args, name)
        if file is None:
            continue
        try:
            report["profiles"][name] = verify(name, file.read_bytes())
        except (OSError, ValueError) as exc:
            report["profiles"][name] = {"ok": False, "error": str(exc)}
    if args.save:
        try:
            report["save"] = inspect_save(args.save.read_bytes(), args.slot)
        except (OSError, ValueError) as exc:
            report["save"] = {"error": str(exc)}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["profiles"] and all(x["ok"] for x in report["profiles"].values()) and (
        report["save"] is None or "error" not in report["save"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
