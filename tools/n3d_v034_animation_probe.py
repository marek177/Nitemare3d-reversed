#!/usr/bin/env python3
"""Read-only original-byte evidence for Nitemare 3D DOS v2.0 animation call paths.

Only the canonical unpacked MZ *load image* is supported. This program
checks selected direct call edges and opcode windows, NOT every indirect
call, real-time execution order, sprite visibility or complete 1:1 parity.
It distributes none of the original game's binary data.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

DOS20_UNPACKED_SIZE = 171360
DOS20_UNPACKED_SHA256 = "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297"

# Exact opcode sites in DOS v2.0 MZ load image: target is also an image offset.
# A far seg:off is normalized to image offset (segment << 4) + offset.
# A near call uses opcode position +3 + signed 16-bit displacement.
CALL_EDGES = {
    "fast_to_noop_hook": (0xC153, "far", 0xC51A),
    "fast_to_push_not_generic_object": (0xC172, "far", 0x0E50),
    "normal_bucket_to_fast": (0xC1EA, "near", 0xC150),
    "demo_odd_frame_to_fast": (0xC22E, "near", 0xC150),
    "outer_frame_to_renderer": (0xC239, "near", 0xBF36),
    "renderer_build_spans": (0xBF40, "far", 0x213E),
    "renderer_raster_spans": (0xBF5A, "far", 0x2500),
    "renderer_project_sorted_objects": (0xBF5F, "far", 0x21F0),
    "renderer_overlay_pass": (0xBF64, "far", 0x273C),
    "span_render_to_animation": (0x2721, "near", 0x241E),
    "sorted_scene_to_projection": (0x2225, "far", 0xB2D4),
    "projectiles_also_to_projection": (0x8307, "far", 0xB2D4),
    "projected_regular_animation": (0xB521, "near", 0xB22C),
    "projected_directional_animation": (0xB532, "near", 0xB17E),
    "outer_frame_to_secret_panel": (0xC246, "far", 0x0AEA),
    "outer_frame_to_projectiles": (0xC24B, "far", 0x8230),
}

# Short original instruction windows, including all three actual +03 writes.
# These witnesses are not a complete function decompilation.
WITNESSES = {
    "noop_hook_retf": (0xC51A, "cb 90"),
    "frame_render_generation_increment": (0xBF36, "66 ff 06 40 45"),
    "build_span_pool_reset": (0x2144, "33 f6 89 36 64 4d"),
    "span_loop_reads_span_count": (0x250B, "bf 6e 4d 83 3e 64 4d 00"),
    "span_descriptor_from_object_selector": (0x251B, "8a 47 04 2a e4 c1 e0 03 05 10 43"),
    "span_nonzero_interval_gate": (0x2716, "83 7f 02 00 74 0b"),
    "span_deadline_unsigned_guard": (0x2427, "66 a1 1e 08 66 39 44 08 0f 87 c9 00"),
    "span_frame_increment": (0x2433, "fe 44 03"),
    "span_random_variant_rng": (0x2478, "9a a0 01 ba 0f 24 07"),
    "span_next_deadline_writer": (0x24E6, "a1 1e 08 8b 5e 08 8b 16 20 08 03 47 02 83 d2 00 89 44 08 89 54 0a"),
    "projection_active_flag_gate": (0xB2E0, "26 f6 44 05 01 0f 84 5a 02"),
    "projection_vertical_distance_clip": (0xB325, "3b c1 0f 8f 18 02"),
    "projection_special_class_dispatch": (0xB500, "8a 47 06 2d 05 00 74 3b 2d 27 00"),
    "regular_projected_interval_gate": (0xB515, "83 7f 02 00 74 28"),
    "regular_projected_deadline_guard": (0xB235, "66 a1 1e 08 66 26 39 44 08 0f 87 8d 00"),
    "regular_projected_frame_increment": (0xB242, "26 fe 44 03"),
    "directional_projected_deadline_guard": (0xB1AE, "66 a1 1e 08 66 26 39 44 08 77 04"),
    "directional_projected_frame_increment": (0xB1B9, "26 fe 44 03"),
}


def unpacked_mz_image(raw):
    if len(raw) < 64 or raw[:2] != b"MZ":
        raise ValueError("missing DOS MZ header")
    header_bytes = struct.unpack_from("<H", raw, 8)[0] * 16
    if header_bytes < 28 or header_bytes >= len(raw):
        raise ValueError("invalid MZ header size")
    return raw[header_bytes:]


def decode_direct_call(image, site, encoding):
    size = 3 if encoding == "near" else 5
    if site < 0 or site + size > len(image):
        return None
    opcode = image[site]
    if encoding == "near" and opcode == 0xE8:
        displacement = struct.unpack_from("<h", image, site + 1)[0]
        return site + size + displacement
    if encoding == "far" and opcode == 0x9A:
        offset, segment = struct.unpack_from("<HH", image, site + 1)
        return (segment << 4) + offset
    return None


def check_static_image(image):
    """Accept only selected byte witnesses; not a global disassembly/call census."""
    edges = {}
    for name, (site, encoding, expected_target) in CALL_EDGES.items():
        actual_target = decode_direct_call(image, site, encoding)
        edges[name] = {
            "ok": actual_target == expected_target,
            "site": site,
            "expected_target": expected_target,
            "observed_target": actual_target,
        }
    witnesses = {}
    for name, (offset, hex_bytes) in WITNESSES.items():
        expected = bytes.fromhex(hex_bytes)
        witnesses[name] = image[offset:offset + len(expected)] == expected
    return {
        "ok": all(record["ok"] for record in edges.values()) and
              all(witnesses.values()),
        "direct_call_edges": edges,
        "opcode_witnesses": witnesses,
    }


def verify_original_executable(raw):
    image = unpacked_mz_image(raw)
    fingerprint_ok = len(image) == DOS20_UNPACKED_SIZE and (
        hashlib.sha256(image).hexdigest() == DOS20_UNPACKED_SHA256)
    result = {
        "build": "dos-v2.0-unpacked-load-image",
        "fingerprint_matches": fingerprint_ok,
        "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "ok": False,
        "original_game_executed": False,
        "runtime_animation_order_verified": False,
        "complete_object_scheduler_identified": False,
    }
    # Fails closed: a signature match in some other build cannot borrow
    # DOS v2.0 offsets or claim v2.0 evidence.
    if not fingerprint_ok:
        result["verdict"] = "incorrect_original_executable"
        return result
    proof = check_static_image(image)
    result.update(proof)
    result["verdict"] = ("static_callsite_and_opcode_evidence_passed"
                         if result["ok"] else "instruction_or_callsite_mismatch")
    result["note"] = ("Per-span and projected OBJECT frame writes are proven "
                      "statical call paths; no original gameplay timing, "
                      "visibility reachability or RNG draw order is measured.")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_dos20_exe", type=Path)
    args = parser.parse_args(argv)
    try:
        report = verify_original_executable(
            args.original_dos20_exe.read_bytes())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
