#!/usr/bin/env python3
"""Bounded original-static Win16 clock/latch writer-width overlap audit.

Source: archived Win16 1.10 Ghidra ASM listing in user's nite3w(1).docx.
Checks the opcode-anchored DIRECT, FIXED-DS-address writer witnesses,
including immediately adjacent globals whose wider writes could overlap
DS:46B2. This is not a complete alias/pointer-writer graph.

Optionally recheck all witness bytes against the exact SHA-256-pinned
original Win16 1.10 NE EXE. Nothing executes the original program.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (ROOT / "other/n3d/builds_12/static_byte_evidence"
                    / "N3D_Win110_timer_direct_write_witnesses_20261020.csv")

LATCH = 0x00A2
CLOCK = 0x46B2
EXPECTED_ONE_SHOT_RESET = "3:0ECA"
EXPECTED_CLOCK_DIRECT_WRITERS = {"3:0ED6", "3:D691"}
EXPECTED_NEIGHBOR_WRITERS = {
    "3:300D", "3:0ED3", "3:2D95", "3:2EC8",
    "3:93A4", "3:93CB", "3:93D2",
}


@dataclass(frozen=True)
class DirectWitness:
    build: str
    segment: int
    ip: int
    absolute_ds_address: int
    width: int
    raw_opcode: bytes
    classification: str
    origin: str

    @property
    def source(self) -> str:
        return f"{self.segment}:{self.ip:04X}"

    @property
    def last_byte(self) -> int:
        return self.absolute_ds_address + self.width - 1

    def overlaps(self, target: int) -> bool:
        # All bounded addresses below are far from 0xFFFF; wrapping does not occur.
        return self.absolute_ds_address <= target <= self.last_byte


def load_manifest(path: Path = DEFAULT_MANIFEST) -> list[DirectWitness]:
    with path.open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    result = []
    for r in records:
        result.append(DirectWitness(
            r["build"], int(r["segment"]), int(r["offset"], 0),
            int(r["absolute_ds_address"], 0),
            int(r["width_bytes"]),
            bytes.fromhex(r["opcode_hex"]),
            r["classification"], r["origin"]))
    return result


def instruction_width(w: DirectWitness) -> int:
    """Verify exactly the supported static fixed-moffs writer encoding.

    This is intentionally *not* a general x86 decoder. Unknown opcodes
    are rejected, rather than inventing a source-register width.
    """
    b = w.raw_opcode
    address = w.absolute_ds_address.to_bytes(2, "little")
    if b.startswith(b"\xA2") and b[1:3] == address:
        return 1
    if b.startswith(b"\xA3") and b[1:3] == address:
        return 2
    if b.startswith(b"\x66\xA3") and b[2:4] == address:
        return 4
    if b.startswith(b"\xC6\x06") and b[2:4] == address and len(b) >= 5:
        return 1
    if b.startswith(b"\xC7\x06") and b[2:4] == address and len(b) >= 6:
        return 2
    if b.startswith(b"\x66\xC7\x06") and b[3:5] == address and len(b) >= 9:
        return 4
    if b.startswith(b"\x88\x06") and b[2:4] == address:
        return 1
    if b.startswith(b"\x89\x06") and b[2:4] == address:
        return 2
    if b.startswith(b"\x66\x89\x06") and b[3:5] == address:
        return 4
    raise ValueError(
        f"Unsupported or mismatched absolute writer opcode at {w.source}: {b.hex(' ')}"
    )


def audit(witnesses: list[DirectWitness],
          *, strict_original_manifest: bool = True) -> dict:
    if not witnesses:
        raise ValueError("Empty direct-writer evidence manifest")
    seen = set()
    for w in witnesses:
        if w.source in seen:
            raise ValueError("Duplicate direct-writer site " + w.source)
        seen.add(w.source)
        if w.build != "1.10" or w.segment != 3:
            raise ValueError("Manifest contains non-Win16-v1.10/NE3 witness")
        expected_width = instruction_width(w)
        if w.width != expected_width:
            raise ValueError(
                f"Recorded instruction width mismatch at {w.source}: "
                f"{w.width} != {expected_width}"
            )
        if w.width <= 0 or w.last_byte > 0xFFFF:
            raise ValueError("Out-of-range DS writer " + w.source)

    latch_writers = [w for w in witnesses if w.overlaps(LATCH)]
    clock_writers = [w for w in witnesses if w.overlaps(CLOCK)]
    literal_clock_writers = [w for w in clock_writers
                             if w.absolute_ds_address == CLOCK]
    overlapping_neighbor_writers = [
        w for w in clock_writers
        if w.absolute_ds_address != CLOCK
    ]
    direct_neighbor_writers = [
        w for w in witnesses
        if 0x46AF <= w.absolute_ds_address < CLOCK
    ]
    # A DWORD writer starting at 46AF/46B0/46B1 would extend into 46B2;
    # a WORD writer at 46B1 would also overlap.
    exact_sites = set(w.source for w in literal_clock_writers)
    neighbor_sites = set(w.source for w in direct_neighbor_writers)
    latch_sites = set(w.source for w in latch_writers)
    proven = (exact_sites == EXPECTED_CLOCK_DIRECT_WRITERS
              and neighbor_sites == EXPECTED_NEIGHBOR_WRITERS
              and latch_sites == {EXPECTED_ONE_SHOT_RESET}
              and not overlapping_neighbor_writers)
    if strict_original_manifest and not proven:
        raise ValueError("Win16 1.10 archived direct fixed-address width census diverged")

    return {
        "build": "1.10",
        "source_grade": "ARCHIVED_GHIDRA_DIRECT_FIXED_ADDRESS_WRITER_WITNESSES",
        "recorded_witnesses": len(witnesses),
        "clock_flag_address": "DS:46B2",
        "one_shot_address": "DS:00A2",
        "clock_direct_writer_sites": sorted(exact_sites),
        "one_shot_direct_writer_sites": sorted(latch_sites),
        "neighbor_direct_writer_sites": sorted(neighbor_sites),
        "neighbor_direct_writes_proven_not_to_overlap_clock": (
            len(direct_neighbor_writers)
            - len(overlapping_neighbor_writers)),
        "direct_neighbor_write_overlaps_clock": [
            {"site": w.source, "start": f"{w.absolute_ds_address:04X}",
             "end": f"{w.last_byte:04X}", "width": w.width}
            for w in overlapping_neighbor_writers
        ],
        "direct_witness_manifest_consistent": proven,
        "complete_original_1_10_ne_image_scanned": False,
        "computed_address_aliases_ruled_out": False,
        "interprocedural_memcpy_or_rep_stos_ruled_out": False,
        "full_runtime_writer_graph_closed": False,
        "limitations": [
            "Covers only direct constant-DS-address Ghidra-mapped writer sites.",
            "No proof of absence of computed indexed or segment-overridden writes.",
            "No pointer-alias, call-based copy or overlapping unknown write census.",
            "Synthetic CI checks this ledger; only --original makes a fresh EXE SHA check.",
        ],
    }


def verify_pinned_original(witnesses: list[DirectWitness], path: Path):
    # Do not import capstone-dependent code in synthetic-only regression.
    from n3d_win16_timer_binary_proof import find_pinned_original
    from ne_renderer_audit import NeImage
    import tempfile

    source, original, profile = find_pinned_original(path, "1.10")
    if profile.version != "1.10":
        raise ValueError("Must be SHA-pinned Win16 1.10")
    with tempfile.TemporaryDirectory(prefix="win16-clock-alias-") as tmp:
        scratch = Path(tmp, "nitemare_original_ne.exe")
        scratch.write_bytes(original)
        image = NeImage(scratch)
        for w in witnesses:
            actual = image.bytes_at(w.segment, w.ip,
                                    w.ip + len(w.raw_opcode))
            if actual != w.raw_opcode:
                raise ValueError(
                    f"Original Win16 1.10 opcode mismatch at {w.source}: "
                    f"{actual.hex(' ')} vs {w.raw_opcode.hex(' ')}"
                )
    return {"source": source, "sha256": profile.sha256,
            "manifest_exact_opcodes_passed": len(witnesses)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--original", type=Path,
                        help="Exact original Win16 1.10 EXE or ZIP; optional")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    try:
        witnesses = load_manifest(args.manifest)
        report = audit(witnesses)
        if args.original:
            report["fresh_original_sha_check"] = verify_pinned_original(
                witnesses, args.original)
            report["complete_original_1_10_ne_image_scanned"] = False
            # 10 exact instruction comparisons do not constitute a full
            # alias-writer scan across every original NE code segment.
        else:
            report["fresh_original_sha_check"] = None
        data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(data, encoding="utf-8")
            print(f"Static alias-writer proof written to {args.output}")
        else:
            print(data)
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Static proof failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
