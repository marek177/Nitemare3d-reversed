#!/usr/bin/env python3
"""Fail-closed original DOS2 vs candidate VEC -> OWNER -> SPAN -> FRAME -> DAC gate.

Inputs are *paired user-supplied captures*, not certified recordings. A PASS
means only equality at these matched checkpoints. It never proves whole-game
pixel parity, original capture authenticity, or algorithmic equivalence.
No Nitemare3D original game data is distributed or embedded by this tool.

Capture layout on each side:
  manifest.json  (see docs/V072_RENDERER_FIRST_DIVERGENCE_SK.md)
  stages/35_span_build_end/vec.bin    1000 x 28 bytes
  stages/35_span_build_end/owner.bin  2 + 320 x 2 bytes
  stages/35_span_build_end/spans.bin  10 + 50 x 18 bytes
  frame.idx                           320 x 200 bytes
  dac.bin                               256 x RGB6 bytes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from n3d_v071_frame_parity_gate import Incomparable, check_manifest

W, H = 320, 200
VIEW_LEFT, VIEW_RIGHT = 8, 311
VIEW_TOP, VIEW_BOTTOM = 4, 155
VEC_BASE, VEC_SIZE, VEC_MAX = 0x62AC, 28, 1000
SPAN_HEADER, SPAN_SIZE, SPAN_MAX = 10, 18, 50
FILE_SHAPES = {
    "vec.bin": (("stages", "35_span_build_end", "vec.bin"), VEC_SIZE * VEC_MAX),
    "owner.bin": (("stages", "35_span_build_end", "owner.bin"), 2 + 320 * 2),
    "spans.bin": (("stages", "35_span_build_end", "spans.bin"), SPAN_HEADER + SPAN_SIZE * SPAN_MAX),
    "frame.idx": (("frame.idx",), W * H),
    "dac.bin": (("dac.bin",), 256 * 3),
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VEC_FIELDS = (
    (0, 1, "wall_id"), (1, 2, "texture_offset"), (2, 3, "animation_aux"),
    (3, 4, "animation_frame"), (4, 5, "texture_set"), (5, 6, "flags"),
    (6, 7, "render_class"), (7, 8, "orientation"), (8, 12, "timer"),
    (12, 14, "world_x1"), (14, 16, "world_y1"),
    (16, 18, "world_x2"), (18, 20, "world_y2"),
    (20, 22, "screen_x1"), (22, 24, "screen_y1_q4"),
    (24, 26, "screen_x2"), (26, 28, "screen_y2_q4"),
)
SPAN_FIELDS = (
    (0, 2, "owner_near"), (2, 4, "x_start"),
    (4, 6, "y_start_q4"), (6, 8, "x_end"), (8, 10, "y_end_q4"),
    (10, 14, "y_step_16_16"), (14, 18, "y_accumulator_16_16"),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(raw: bytes, start: int) -> int:
    return int.from_bytes(raw[start:start+2], "little")


def field_at(offset: int, fields: tuple) -> str:
    for lo, hi, name in fields:
        if lo <= offset < hi:
            return name
    return "unknown"


def read_capture(root: Path) -> tuple[dict, dict[str, bytes]]:
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise Incomparable(f"Invalid or missing manifest.json in {root}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise Incomparable("Manifest must be an object")
    if manifest.get("format") != "n3d-dos20-stage-frame-v072":
        raise Incomparable("Unexpected capture format; require explicit v072 manifest")
    count = manifest.get("vec_count")
    if type(count) is not int or not (0 <= count <= VEC_MAX):
        raise Incomparable("vec_count must be an integer from 0 to 1000")
    if manifest.get("stage_checkpoint") != "post_span":
        raise Incomparable("Required post_span capture is not documented")
    if manifest.get("frame_checkpoint") != "post_present":
        raise Incomparable("Required post_present indexed capture is not documented")
    fingerprints = manifest.get("capture_sha256")
    if not isinstance(fingerprints, dict) or set(fingerprints) != set(FILE_SHAPES):
        raise Incomparable("capture_sha256 must contain digests for all five files")
    buffers: dict[str, bytes] = {}
    for name, (relative, size) in FILE_SHAPES.items():
        try:
            blob = root.joinpath(*relative).read_bytes()
        except OSError as exc:
            raise Incomparable(f"Missing stage data {name} from {root}: {exc}") from exc
        if len(blob) != size:
            raise Incomparable(f"Invalid {name} size: got {len(blob)}, expected {size}")
        claimed = fingerprints[name]
        if not isinstance(claimed, str) or not HEX64.fullmatch(claimed):
            raise Incomparable(f"Malformed SHA-256 for {name}")
        if digest(blob) != claimed:
            raise Incomparable(f"Manifest SHA-256 does not match bytes of {name}")
        buffers[name] = blob

    owner = buffers["owner.bin"]
    columns = [u16(owner, 2 + x * 2) for x in range(VIEW_LEFT, VIEW_RIGHT + 1)]
    filled = sum(v != 0 for v in columns)
    remaining = u16(owner, 0)
    if remaining != (VIEW_RIGHT - VIEW_LEFT + 1) - filled:
        raise Incomparable("Owner remaining count disagrees with populated viewport columns")

    def valid_near(pointer: int) -> bool:
        return pointer >= VEC_BASE and (pointer-VEC_BASE) % VEC_SIZE == 0 and (
            (pointer-VEC_BASE)//VEC_SIZE < count
        )

    for x, ptr in enumerate(columns, VIEW_LEFT):
        if ptr and not valid_near(ptr):
            raise Incomparable(f"Owner column {x} references an invalid active VEC")
    spans = buffers["spans.bin"]
    nspan = u16(spans, 0)
    if not 0 <= nspan <= SPAN_MAX:
        raise Incomparable("Span count exceeds the DOS2 maximum of 50")
    if filled and not nspan:
        raise Incomparable("Occupied owner viewport with empty post-span table")
    for j in range(nspan):
        start = SPAN_HEADER + j * SPAN_SIZE
        ptr = u16(spans, start)
        if not valid_near(ptr):
            raise Incomparable(f"Span {j} references a non-active VEC pointer")

    if any(component > 63 for component in buffers["dac.bin"]):
        raise Incomparable("DAC must consist of 6-bit color components")
    return manifest, buffers


def bytes_mismatch(a: bytes, b: bytes) -> tuple[int, int | None]:
    bad = 0
    first = None
    for offset, (left, right) in enumerate(zip(a, b)):
        if left != right:
            bad += 1
            if first is None:
                first = offset
    if len(a) != len(b):
        bad += abs(len(a)-len(b))
        if first is None:
            first = min(len(a), len(b))
    return bad, first


def compare_stages(original: dict[str, bytes], candidate: dict[str, bytes],
                   nvec: int) -> tuple[str, dict]:
    stages: dict = {}
    # Ignore inactive/uninitialized VEC slots (but both full dumps were SHA checked).
    sources = (
        ("VEC_MISMATCH", original["vec.bin"][:nvec*VEC_SIZE],
         candidate["vec.bin"][:nvec*VEC_SIZE]),
        # Owner count and only the active viewport; pixels outside can be uninitialized.
        ("OWNER_MISMATCH",
         original["owner.bin"][:2] + original["owner.bin"][2+VIEW_LEFT*2:2+(VIEW_RIGHT+1)*2],
         candidate["owner.bin"][:2] + candidate["owner.bin"][2+VIEW_LEFT*2:2+(VIEW_RIGHT+1)*2]),
        # Ignore uninitialized span tail and the 8-byte gap in the 10-byte prefix.
        ("SPAN_MISMATCH",
         original["spans.bin"][:2] + original["spans.bin"][SPAN_HEADER:
             SPAN_HEADER + u16(original["spans.bin"], 0)*SPAN_SIZE],
         candidate["spans.bin"][:2] + candidate["spans.bin"][SPAN_HEADER:
             SPAN_HEADER + u16(candidate["spans.bin"], 0)*SPAN_SIZE]),
        ("FRAME_MISMATCH", original["frame.idx"], candidate["frame.idx"]),
        ("DAC_MISMATCH", original["dac.bin"], candidate["dac.bin"]),
    )
    first_stage = "PASS"
    for stage, a, b in sources:
        errors, first = bytes_mismatch(a, b)
        rec = {
            "compared_bytes_original": len(a), "compared_bytes_candidate": len(b),
            "mismatched_bytes": errors, "first_offset": first,
            "original_sha256_meaningful": digest(a),
            "candidate_sha256_meaningful": digest(b),
        }
        if first is not None:
            if stage == "VEC_MISMATCH":
                sub = first % VEC_SIZE
                rec["first_field"] = field_at(sub, VEC_FIELDS)
                rec["first_vec_index"] = first // VEC_SIZE
                rec["byte_in_vec"] = sub
            elif stage == "OWNER_MISMATCH":
                rec["first_field"] = "remaining_unowned" if first < 2 else "column_owner"
                if first >= 2:
                    rec["first_screen_x"] = VIEW_LEFT + (first - 2)//2
            elif stage == "SPAN_MISMATCH":
                if first < 2:
                    rec["first_field"] = "span_count"
                else:
                    sub = (first-2) % SPAN_SIZE
                    rec["first_field"] = field_at(sub, SPAN_FIELDS)
                    rec["first_span_index"] = (first-2)//SPAN_SIZE
            elif stage == "FRAME_MISMATCH":
                x, y = first % W, first // W
                rec["first_pixel"] = {
                    "x": x, "y": y,
                    "original_index": a[first], "candidate_index": b[first],
                    "in_3d_viewport": VIEW_LEFT <= x <= VIEW_RIGHT and VIEW_TOP <= y <= VIEW_BOTTOM,
                }
            elif stage == "DAC_MISMATCH":
                rec["first_palette_index"] = first // 3
                rec["first_channel"] = "RGB"[first % 3]
        stages[stage] = rec
        if errors and first_stage == "PASS":
            first_stage = stage
    return first_stage, stages


def analyze(original_root: Path, candidate_root: Path) -> dict:
    original_state, original = read_capture(original_root)
    candidate_state, candidate = read_capture(candidate_root)
    try:
        validated = check_manifest(original_state, candidate_state)
    except (Incomparable, TypeError) as exc:
        raise Incomparable(f"State manifests not comparable: {exc}") from exc
    if original_state["vec_count"] != candidate_state["vec_count"]:
        raise Incomparable("VEC pool sizes differ; do not align unequal records by index")
    if original_state["stage_checkpoint"] != candidate_state["stage_checkpoint"] or (
        original_state["frame_checkpoint"] != candidate_state["frame_checkpoint"]
    ):
        raise Incomparable("Different capture stage checkpoints")
    verdict, stages = compare_stages(original, candidate, original_state["vec_count"])
    return {
        "format": "n3d-dos20-stage-frame-verdict-v072",
        "evidence": "SUPPLIED_CAPTURE_BYTE_COMPARISON_ONLY",
        "original_recording_authenticated": False,
        "gameplay_state_authenticated": False,
        "whole_game_pixel_parity_proven": False,
        "state_fields_match": True,
        "state": validated,
        "vec_count": original_state["vec_count"],
        "first_divergent_stage": verdict,
        "stage_results": stages,
        "zero_diff_at_supplied_checkpoints": verdict == "PASS",
        "warning": "PASS never establishes source authenticity, other-scene parity, or a live VEC renderer.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        report = analyze(args.original, args.candidate)
        exit_code = 0 if report["zero_diff_at_supplied_checkpoints"] else 1
    except (Incomparable, OSError, ValueError) as exc:
        report = {
            "format": "n3d-dos20-stage-frame-verdict-v072",
            "first_divergent_stage": "INCOMPARABLE",
            "zero_diff_at_supplied_checkpoints": False,
            "reason": str(exc),
            "warning": "No pixel-parity verdict was issued because captures are not comparable.",
        }
        exit_code = 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
