#!/usr/bin/env python3
"""Nitemare 3D DOS v2.0: strict candidate-versus-original 320x200 byte parity gate.

Normalizes NEITHER side: pass already-normalized 64000-byte indexed frames
and 768-byte 6-bit VGA DAC captures. Both state manifests must identify the
same exact original data and synchronized gameplay/render state. A pass proves
equality of only the supplied pair of files; it cannot authenticate the capture
or claim global parity for other states.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

WIDTH = 320
HEIGHT = 200
FRAME_BYTES = WIDTH * HEIGHT
DAC_BYTES = 768
ORIGINAL_DOS2_UNPACKED_SHA = "552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301"
MATCH_FIELDS = (
    "reference_exe_sha256",
    "data_manifest_sha256",
    "episode",
    "level",
    "game_tick",
    "player_x",
    "player_y",
    "angle_units",
    "world_state_sha256",
    "render_checkpoint",
    "palette_phase",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class Incomparable(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_manifest(original: dict, candidate: dict) -> dict:
    if original.get("role") != "original-dos2" or candidate.get("role") != "candidate":
        raise Incomparable("Role labels must be original-dos2 and candidate")
    if original.get("reference_exe_sha256") != ORIGINAL_DOS2_UNPACKED_SHA:
        raise Incomparable("Reference EXE SHA must identify the pinned unpacked DOS2 v2.0")
    for name in MATCH_FIELDS:
        if name not in original or name not in candidate:
            raise Incomparable(f"Missing required state field: {name}")
        if original[name] != candidate[name]:
            raise Incomparable(f"Unsynchronized state field: {name}")
    for key in ("reference_exe_sha256", "data_manifest_sha256", "world_state_sha256"):
        if not isinstance(original[key], str) or not HEX64.fullmatch(original[key]):
            raise Incomparable(f"Invalid SHA-256 state field: {key}")
    if not (isinstance(original["episode"], int) and original["episode"] in (1, 2, 3)):
        raise Incomparable("Episode must be 1..3")
    if not (isinstance(original["level"], int) and 1 <= original["level"] <= 11):
        raise Incomparable("Level must be 1..11")
    for key in ("game_tick", "player_x", "player_y", "angle_units"):
        if not isinstance(original[key], int):
            raise Incomparable(f"Non-integer state field: {key}")
    for key in ("render_checkpoint", "palette_phase"):
        if not isinstance(original[key], str) or not original[key]:
            raise Incomparable(f"Empty render state field: {key}")
    return {name: original[name] for name in MATCH_FIELDS}


def compare_pair(original_frame: bytes, candidate_frame: bytes,
                 original_dac: bytes, candidate_dac: bytes,
                 original_state: dict, candidate_state: dict) -> dict:
    state = check_manifest(original_state, candidate_state)
    if len(original_frame) != FRAME_BYTES or len(candidate_frame) != FRAME_BYTES:
        raise Incomparable("Each indexed frame must be exactly 64000 bytes")
    if len(original_dac) != DAC_BYTES or len(candidate_dac) != DAC_BYTES:
        raise Incomparable("Each DAC buffer must be exactly 768 bytes")
    if max(original_dac) > 63 or max(candidate_dac) > 63:
        raise Incomparable("DAC must be 6-bit components (0..63)")
    diffs = [i for i, (a, b) in enumerate(zip(original_frame, candidate_frame)) if a != b]
    dac_diff = [i for i, (a, b) in enumerate(zip(original_dac, candidate_dac)) if a != b]
    if diffs:
        first = {"x": diffs[0] % WIDTH, "y": diffs[0] // WIDTH,
                 "original_index": original_frame[diffs[0]],
                 "candidate_index": candidate_frame[diffs[0]]}
        box = {"left": min(i % WIDTH for i in diffs),
               "right": max(i % WIDTH for i in diffs),
               "top": min(i // WIDTH for i in diffs),
               "bottom": max(i // WIDTH for i in diffs)}
    else:
        first, box = None, None
    return {
        "evidence_level": "SUPPLIED_PAIR_BYTE_COMPARISON_ONLY",
        "capture_authenticity": "USER_ASSERTED_NOT_INDEPENDENTLY_PROVEN",
        "state_fields_match": True,
        "verified_state": state,
        "original_frame_sha256": digest(original_frame),
        "candidate_frame_sha256": digest(candidate_frame),
        "original_dac_sha256": digest(original_dac),
        "candidate_dac_sha256": digest(candidate_dac),
        "compared_indexed_pixels": FRAME_BYTES,
        "different_indexed_pixels": len(diffs),
        "first_indexed_mismatch": first,
        "indexed_mismatch_box": box,
        "compared_dac_components": DAC_BYTES,
        "different_dac_components": len(dac_diff),
        "first_dac_component_mismatch": dac_diff[0] if dac_diff else None,
        "pair_matches": not diffs and not dac_diff,
        "warning": "A passing pair is not proof of full-game or other-camera pixel-perfect parity.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("original_frame", "candidate_frame",
                 "original_dac", "candidate_dac", "original_state", "candidate_state"):
        p.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    try:
        original_state = json.loads(a.original_state.read_text(encoding="utf-8"))
        candidate_state = json.loads(a.candidate_state.read_text(encoding="utf-8"))
        result = compare_pair(a.original_frame.read_bytes(), a.candidate_frame.read_bytes(),
                              a.original_dac.read_bytes(), a.candidate_dac.read_bytes(),
                              original_state, candidate_state)
    except (OSError, ValueError, TypeError, Incomparable) as e:
        p.exit(2, f"INCOMPARABLE: {e}\n")
    out = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(out, encoding="utf-8")
    print(out, end="")
    return 0 if result["pair_matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
