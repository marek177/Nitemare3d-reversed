#!/usr/bin/env python3
"""DOS v2.0 scheduler's original-byte static checks, NOT a runtime emulator.

Use the canonical unpacked MZ executable. Strict hash, 25 instruction
windows, 13 short branch targets and 13 direct call targets. No copyrighted
binary is committed. Complete nested callbacks/interrupt ordering remains OPEN.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

IMAGE_SIZE = 171360
IMAGE_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"

# Offsets in DOS v2.0 UNPACKED MZ LOAD IMAGE (not packed EXE offsets).
WINDOWS = {
    "slow_quantized_shift8": (0xBEB8, "66 8b 46 06 66 c1 e0 03"),
    "slow_divisor1000": (0xBEC0, "66 b9 e8 03 00 00 66 33 d2 66 f7 f1"),
    "slow_inequality_guard": (0xBED0, "66 2b 06 fa 16 66 3d 00 00 00 00 74 0d"),
    "slow_cache_and_counter_write": (0xBEDD, "66 8b 46 fc 66 a3 fa 16 66 ff 06 f6 16"),
    "slow_return_counter": (0xBEEA, "a1 f6 16 8b 16 f8 16"),
    "frame_signed_calibration": (0xBEF8, "66 0f bf 06 c2 3c 66 f7 66 06"),
    "frame_divisor1000": (0xBF02, "66 b9 e8 03 00 00 66 33 d2 66 f7 f1"),
    "frame_inequality_guard": (0xBF12, "66 2b 06 02 17 66 3d 00 00 00 00 74 0d"),
    "frame_cache_counter_write": (0xBF1F, "66 8b 46 fc 66 a3 02 17 66 ff 06 fe 16"),
    "frame_return_counter": (0xBF2C, "a1 fe 16 8b 16 00 17"),
    "outer_clock_snapshot": (0xC1AC, "0e e8 c4 fc 89 46 fc 89 56 fe"),
    "outer_legacy_clock_snapshot": (0xC1B6, "0e e8 3e fc 89 46 f8 89 56 fa"),
    "slow_threshold_unsigned_high_low": (0xC1D2, "39 16 3a 17 77 22 72 06 39 06 38 17 77 1a"),
    "normal_mode_gate": (0xC1E0, "83 3e d6 3c 00 75 09"),
    "slow_next_due_skip_catchup": (0xC1F0, "66 a1 72 36 66 40 66 a3 38 17"),
    "frame_threshold_unsigned_high_low": (0xC20C, "39 16 3e 17 77 74 72 06 39 06 3c 17 77 6c"),
    "demo_mode_and_old_generation": (0xC21A, "83 3e d6 3c 00 74 13 f6 06 40 45 01 74 0c"),
    "demo_fast_argument_slow_counter": (0xC228, "66 ff 36 72 36 0e e8 1f ff"),
    "frame_main_render_start": (0xC234, "0e e8 a0 fe 0e e8 fa fc"),
    "frame_secret_panel_projectile": (0xC246, "9a ea 0a 00 00 9a 60 03 ed 07"),
    "frame_next_due_and_legacy_reset": (0xC274, "66 a1 76 36 66 40 66 a3 3c 17 66 8b 46 f8 66 a3 34 17"),
    "unsigned_500_lag_fallback": (0xC286, "66 8b 46 f8 66 2b 06 34 17 66 3d f4 01 00 00 76 1d"),
    "fallback_pause_resume": (0xC297, "6a 01 0e e8 47 fb 83 c4 02 6a 00 0e e8 3e fb 83 c4 02"),
    "fallback_update_legacy_epoch": (0xC2A9, "0e e8 4b fb a3 34 17 89 16 36 17"),
    "render_generation_increment": (0xBF36, "66 ff 06 40 45"),
}

# These are the scheduler's short forward branches in C1A8..C2B4,
# including unsigned hi/lo due gates, demo mode and unsigned lag check.
# The fixed instruction window above also proves counters are set to
# (current RETURNED counter + 1), never repeatedly incremented to catch up.
SHORT_BRANCHES = {
    "slow_high_too_early": (0xC1D6, 0x77, 0xC1FA),
    "slow_high_overdue": (0xC1D8, 0x72, 0xC1E0),
    "slow_low_too_early": (0xC1DE, 0x77, 0xC1FA),
    "slow_demo_mode_skip_fast": (0xC1E5, 0x75, 0xC1F0),
    "frame_high_too_early": (0xC210, 0x77, 0xC286),
    "frame_high_overdue": (0xC212, 0x72, 0xC21A),
    "frame_low_too_early": (0xC218, 0x77, 0xC286),
    "normal_game_skip_demo_fast": (0xC21F, 0x74, 0xC234),
    "demo_even_generation_skip_fast": (0xC226, 0x74, 0xC234),
    "render_delay_long_branch": (0xC25C, 0x75, 0xC26A),
    "render_delay_65_limit": (0xC261, 0x73, 0xC26A),
    "render_delay_skip_other": (0xC268, 0xEB, 0xC26F),
    "unsigned_500_lag_no_recovery": (0xC295, 0x76, 0xC2B4),
}

# Call edges are direct only; they DO NOT exhaust nested calls of BF36 etc.
DIRECT_CALLS = {
    "sample_clock_BE74": (0xC1AD, "near", 0xBE74),
    "sample_legacy_BDF8": (0xC1B7, "near", 0xBDF8),
    "quantize_slow_BEB4": (0xC1C5, "near", 0xBEB4),
    "normal_fast_C150": (0xC1EA, "near", 0xC150),
    "quantize_frame_BEF4": (0xC1FF, "near", 0xBEF4),
    "demo_fast_C150": (0xC22E, "near", 0xC150),
    "main_C0D8": (0xC235, "near", 0xC0D8),
    "frame_BF36": (0xC239, "near", 0xBF36),
    "secret_panel_0AEA": (0xC246, "far", 0x0AEA),
    "projectiles_8230": (0xC24B, "far", 0x8230),
    "legacy_recovery_hook_1": (0xC29A, "near", 0xBDE4),
    "legacy_recovery_hook_0": (0xC2A3, "near", 0xBDE4),
    "legacy_recovery_resample": (0xC2AA, "near", 0xBDF8),
}


def mz_load_image(raw):
    if len(raw) < 64 or raw[:2] != b"MZ":
        raise ValueError("expected an original DOS MZ executable")
    header = struct.unpack_from("<H", raw, 8)[0] * 16
    if header < 28 or header >= len(raw):
        raise ValueError("invalid DOS MZ header size")
    return raw[header:]


def decode_call(image, site, mode):
    if mode == "near" and image[site:site+1] == b"\xE8" and site+3 <= len(image):
        return site + 3 + struct.unpack_from("<h", image, site+1)[0]
    if mode == "far" and image[site:site+1] == b"\x9A" and site+5 <= len(image):
        off, segment = struct.unpack_from("<HH", image, site+1)
        return (segment << 4) + off
    return None


def decode_short_branch(image, site, opcode):
    if site+2 > len(image) or image[site] != opcode:
        return None
    return site + 2 + struct.unpack_from("<b", image, site+1)[0]


def audit_original_image(image):
    windows = {name: image[site:site+len(bytes.fromhex(pattern))] == bytes.fromhex(pattern)
               for name, (site, pattern) in WINDOWS.items()}
    branches = {name: decode_short_branch(image, site, opcode) == target
                for name, (site, opcode, target) in SHORT_BRANCHES.items()}
    calls = {name: decode_call(image, site, mode) == target
             for name, (site, mode, target) in DIRECT_CALLS.items()}
    forward = all(target > site for site, opcode, target in SHORT_BRANCHES.values())
    return {
        "ok": all(windows.values()) and all(branches.values()) and
              all(calls.values()) and forward,
        "verified_opcode_windows": windows,
        "verified_short_branches": branches,
        "verified_direct_calls": calls,
        "audited_short_branches_forward_only": forward,
        "slow_counter_one_increment_per_quotient_change": windows["slow_cache_and_counter_write"],
        "frame_counter_one_increment_per_quotient_change": windows["frame_cache_counter_write"],
        "slow_threshold_set_to_counter_plus_one": windows["slow_next_due_skip_catchup"],
        "frame_threshold_set_to_counter_plus_one": windows["frame_next_due_and_legacy_reset"],
        "demo_fast_receives_slow_counter": windows["demo_fast_argument_slow_counter"],
        "legacy_recovery_uses_unsigned_500_limit": windows["unsigned_500_lag_fallback"],
    }


def verify_original(raw):
    image = mz_load_image(raw)
    digest = hashlib.sha256(image).hexdigest()
    passed = len(image) == IMAGE_SIZE and digest == IMAGE_SHA256
    report = {
        "dos_build": "v2.0-unpacked-MZ-load-image",
        "unpacked_image_size": len(image),
        "image_sha256": digest,
        "fingerprint_valid": passed,
        "ok": False,
        "original_game_executed": False,
        "full_fast_main_runtime_order_verified": False,
        "indirect_callbacks_verified": False,
        "clock_source_latency_verified": False,
    }
    if not passed:
        report["verdict"] = "original_build_fingerprint_mismatch"
        return report
    result = audit_original_image(image)
    report.update(result)
    report["verdict"] = ("local_static_scheduler_gates_verified"
                         if report["ok"] else "opcode_or_control_edge_mismatch")
    report["note"] = (
        "Quantized counter changes each increment by ONE; the outer slow/frame "
        "thresholds jump to (observed counter + 1). This rejects naive "
        "catch-up replay for these local branches but does not prove "
        "interrupt/callback/global original runtime chronology.")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_dos20_mz", type=Path)
    args = ap.parse_args(argv)
    try:
        result = verify_original(args.original_dos20_mz.read_bytes())
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
