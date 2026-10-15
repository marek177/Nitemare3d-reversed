#!/usr/bin/env python3
"""Read-only original DOS 1.0/1.7/1.9/2.0 protected-hit ordering audit.

Exact SHA-256 of the MZ load image is mandatory. The instrument checks
opcode windows, far damage-call targets, both protection-condition jumps
and the v2.0 hit-indicator timer branch. It does not run a DOS executable
or attest DEMO/RNG runtime ordering or visible on-screen behavior.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path


BUILDS = {
    "dos10": {
        "size": 154448,
        "sha256": "113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a",
        "entry": 0x6792, "shield": 0x6798, "dead": 0x679F,
        "call": 0x67B4, "target": 0x8350, "hp": 0x67BF, "exit": 0x6813,
        "windows": {
            "protection": (0x6798, "80 3e a9 3f 00 75 74"),
            "dead_state": (0x679F, "83 3e 6e 3b 02 74 6d"),
            "damage_call": (0x67B4, "9a 00 04 f5 07"),
            "hp_comparison": (0x67BF, "a0 df 3f 38 46 ff 72 3b"),
            "lethal_hp_zero": (0x67C7, "c6 06 df 3f 00"),
            "lethal_state_two": (0x67CC, "c7 06 6e 3b 02 00"),
        },
    },
    "dos17": {
        "size": 170848,
        "sha256": "df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff",
        "entry": 0x690C, "shield": 0x6912, "dead": 0x6919,
        "call": 0x692E, "target": 0x866A, "hp": 0x6939, "exit": 0x698D,
        "windows": {
            "protection": (0x6912, "80 3e c1 40 00 75 74"),
            "dead_state": (0x6919, "83 3e 44 3c 02 74 6d"),
            "damage_call": (0x692E, "9a 0a 04 26 08"),
            "hp_comparison": (0x6939, "a0 f7 40 38 46 ff 72 3b"),
            "lethal_hp_zero": (0x6941, "c6 06 f7 40 00"),
            "lethal_state_two": (0x6946, "c7 06 44 3c 02 00"),
        },
    },
    "dos19": {
        "size": 171296,
        "sha256": "e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e",
        "entry": 0x6A70, "shield": 0x6A76, "dead": 0x6A7D,
        "call": 0x6A92, "target": 0x87CE, "hp": 0x6A9D, "exit": 0x6AF1,
        "windows": {
            "protection": (0x6A76, "80 3e 51 41 00 75 74"),
            "dead_state": (0x6A7D, "83 3e d4 3c 02 74 6d"),
            "damage_call": (0x6A92, "9a 0e 04 3c 08"),
            "hp_comparison": (0x6A9D, "a0 87 41 38 46 ff 72 3b"),
            "lethal_hp_zero": (0x6AA5, "c6 06 87 41 00"),
            "lethal_state_two": (0x6AAA, "c7 06 d4 3c 02 00"),
        },
    },
    "dos20": {
        "size": 171360,
        "sha256": "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297",
        "entry": 0x6A70, "shield": 0x6A99, "dead": 0x6AA0,
        "call": 0x6A84, "target": 0x87D8, "hp": 0x6AA7, "exit": 0x6AFB,
        "windows": {
            "damage_call": (0x6A84, "9a 08 04 3d 08"),
            "store_damage_byte": (0x6A8C, "88 46 ff"),
            "zero_damage_skips_indicator": (0x6A8F, "0a c0 74 06"),
            "hit_indicator_set_three": (0x6A93, "c7 06 7a 41 03 00"),
            "protection": (0x6A99, "80 3e 51 41 00 75 5b"),
            "dead_state": (0x6AA0, "83 3e d4 3c 02 74 54"),
            "hp_comparison": (0x6AA7, "a0 89 41 38 46 ff 72 3b"),
            "lethal_hp_zero": (0x6AAF, "c6 06 89 41 00"),
            "lethal_state_two": (0x6AB4, "c7 06 d4 3c 02 00"),
            "indicator_update_nonnegative": (0xA236, "83 3e 7a 41 00 7c 13"),
            "indicator_countdown_decrement": (0xA23D, "ff 0e 7a 41"),
            "indicator_post_decrement_sign": (0xA241, "79 07"),
            "indicator_clear_draw_code_three": (0xA243, "66 6a 03"),
            "indicator_hit_draw_code_four": (0xA24A, "66 6a 04"),
            "indicator_draw_dispatch": (0xA2BA, "0e e8 4e f5"),
        },
    },
}


def unpacked_image(raw):
    if len(raw) < 64 or raw[:2] != b"MZ":
        raise ValueError("missing DOS MZ header")
    header = struct.unpack_from("<H", raw, 8)[0] * 16
    if header < 28 or header >= len(raw):
        raise ValueError("invalid DOS MZ header length")
    return raw[header:]


def far_call_target(image, site):
    if site + 5 > len(image) or image[site] != 0x9A:
        return None
    ofs, seg = struct.unpack_from("<HH", image, site + 1)
    return (seg << 4) + ofs


def conditional_target(image, cmp_site, compare_bytes, jump_opcode):
    """Offset after 5-byte CMP; short Jcc target, or None on wrong bytes."""
    if image[cmp_site:cmp_site+5] != bytes.fromhex(compare_bytes):
        return None
    site = cmp_site + 5
    if site + 2 > len(image) or image[site] != jump_opcode:
        return None
    return site + 2 + struct.unpack_from("<b", image, site + 1)[0]


def audit_static_image(image, build):
    spec = BUILDS[build]
    windows = {
        label: image[ofs:ofs+len(bytes.fromhex(pattern))] == bytes.fromhex(pattern)
        for label, (ofs, pattern) in spec["windows"].items()
    }
    shield_bytes = spec["windows"]["protection"][1].split()
    dead_bytes = spec["windows"]["dead_state"][1].split()
    shield_target = conditional_target(
        image, spec["shield"], " ".join(shield_bytes[:5]), 0x75)
    dead_target = conditional_target(
        image, spec["dead"], " ".join(dead_bytes[:5]), 0x74)
    exit_opcode_matches = image[spec["exit"]:spec["exit"]+4] == bytes.fromhex("5e 5f c9 cb")
    original_order = spec["shield"] < spec["dead"] < spec["call"] < spec["hp"]
    new_order = spec["call"] < 0x6A93 < spec["shield"] < spec["dead"] < spec["hp"]
    is_v20 = build == "dos20"
    branch_order_matches = new_order if is_v20 else original_order
    zero_skip_matches = not is_v20 or (
        image[0x6A91] == 0x74 and
        0x6A93 + struct.unpack_from("<b", image, 0x6A92)[0] == 0x6A99)
    return {
        "ok": all(windows.values()) and exit_opcode_matches and
              shield_target == spec["exit"] and dead_target == spec["exit"] and
              far_call_target(image, spec["call"]) == spec["target"] and
              branch_order_matches and zero_skip_matches,
        "machine_code_windows": windows,
        "shield_exit_target": shield_target,
        "dead_state_exit_target": dead_target,
        "expected_exit": spec["exit"],
        "epilogue_retf_matches": exit_opcode_matches,
        "damage_producer_call_target": far_call_target(image, spec["call"]),
        "expected_damage_producer_target": spec["target"],
        "producer_precedes_protection": is_v20,
        "gate_precedes_producer": not is_v20,
        "v20_zero_damage_skips_flash": zero_skip_matches if is_v20 else None,
        "v20_nonzero_damage_writes_timer_before_protection": is_v20,
        "zero_hp_zero_damage_lethal_conditional": windows["hp_comparison"],
        "original_runtime_executed": False,
    }


def verify_original(raw, build):
    if build not in BUILDS:
        raise ValueError("unsupported DOS build")
    image = unpacked_image(raw)
    spec = BUILDS[build]
    hash_value = hashlib.sha256(image).hexdigest()
    matches = len(image) == spec["size"] and hash_value == spec["sha256"]
    result = {
        "build": build, "image_bytes": len(image), "sha256": hash_value,
        "fingerprint_matches": matches, "ok": False,
        "original_runtime_executed": False,
        "rng_execution_chronology_verified": False,
        "rendered_hit_indicator_verified": False,
    }
    if not matches:
        result["verdict"] = "wrong_original_build"
        return result
    audit = audit_static_image(image, build)
    result.update(audit)
    result["verdict"] = ("static_damage_order_verified"
                         if result["ok"] else "opcode_or_branch_divergence")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for build in BUILDS:
        parser.add_argument("--" + build, type=Path)
    args = parser.parse_args(argv)
    chosen = [(name, getattr(args, name)) for name in BUILDS if getattr(args, name)]
    if not chosen:
        parser.error("provide at least one --dos10/--dos17/--dos19/--dos20")
    results = {}
    for build, path in chosen:
        try:
            results[build] = verify_original(path.read_bytes(), build)
        except (OSError, ValueError) as exc:
            results[build] = {"ok": False, "error": str(exc)}
    result = {
        "all_available_profiles_pass": all(x.get("ok") for x in results.values()),
        "all_four_builds_checked": len(results) == len(BUILDS),
        "results": results,
        "original_runtime_executed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_available_profiles_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
