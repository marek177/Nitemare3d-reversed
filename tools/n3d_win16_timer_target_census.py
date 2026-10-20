#!/usr/bin/env python3
"""Target-specific Win16 NE relocation call/pointer census.

This is a bounded static scanner. It distinguishes *direct* machine CALL FAR
at a relocation-backed immediate from address-taken FAR pointers and raw
byte-pattern candidates. It does not assert dynamic/virtual target closure.

Use on an original NE image AFTER independent whole-file SHA-256 validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import struct

from ne_renderer_audit import Relocation

# The Win16 NE segment flag 0x0001 denotes a data, rather than code, segment.
NE_SEGMENT_IS_DATA = 0x0001


@dataclass(frozen=True)
class TimerReference:
    source_segment: int
    fixup_offset: int
    target: str
    kind: str
    instruction_address: str | None
    relocation_type: int
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": f"{self.source_segment}:{self.fixup_offset:04X}",
            "target": self.target,
            "kind": self.kind,
            "instruction_address": self.instruction_address,
            "relocation_type": self.relocation_type,
            "reason": self.reason,
        }


def reference_sites(image: Any, target_segment: int = 3,
                    target_offset: int = 0xD66C) -> list[TimerReference]:
    """Classify *all expanded internal NE fixups* naming one static target.

    Source type 2 is a Win16 segment-word relocation at the selector half
    of a 4-byte far pointer; if preceded by opcode 9A or EA we have a
    direct 16-bit far CALL/JMP. A selector fixup elsewhere means that the
    code takes a target address, which could later flow through indirect
    CALL FAR. It does *not* prove such a call happens.
    """
    target = f"internal {target_segment}:{target_offset:04X}".lower()
    out: list[TimerReference] = []
    for reloc in image.relocations:
        if reloc.target.lower() != target:
            continue
        seg = image.segment(reloc.segment)
        source = reloc.source_offset
        kind = "OTHER_FIXUP_REFERENCE"
        instruction_address = None
        reason = "Target is referenced by a NE relocation; calling mechanism unresolved"

        if reloc.source_type == 2 and source >= 3:
            pointer = image.bytes_at(reloc.segment, source - 2, source + 2)
            offset_word = struct.unpack_from("<H", pointer, 0)[0]
            opcode = image.bytes_at(reloc.segment, source - 3, source - 2)[0]
            if offset_word != target_offset:
                kind = "SUSPICIOUS_TARGET_OPERAND_MISMATCH"
                reason = "NE selector fixup says target but offset operand differs"
            elif (seg.flags & NE_SEGMENT_IS_DATA) != 0:
                kind = "DATA_FAR_POINTER"
                reason = "Fixup in a data segment, not a machine CALL opcode"
            elif opcode == 0x9A:
                kind = "DIRECT_FAR_CALL"
                instruction_address = f"{reloc.segment}:{source-3:04X}"
                reason = "9A CALL FAR ptr16:16 with NE segment-word fixup"
            elif opcode == 0xEA:
                kind = "DIRECT_FAR_JUMP"
                instruction_address = f"{reloc.segment}:{source-3:04X}"
                reason = "EA JMP FAR ptr16:16 with NE segment-word fixup"
            else:
                kind = "ADDRESS_TAKEN_OR_UNKNOWN"
                reason = "NE target far pointer without direct call/jump opcode"
        elif (seg.flags & NE_SEGMENT_IS_DATA) != 0:
            kind = "DATA_OTHER_FIXUP"
            reason = "NE target relocation in data: pointer-flow tracing required"

        out.append(TimerReference(reloc.segment, source, reloc.target, kind,
                                  instruction_address, reloc.source_type, reason))
    return sorted(out, key=lambda row: (row.source_segment, row.fixup_offset))


def raw_e8_candidates(image: Any, segment: int, target_offset: int) -> list[str]:
    """Scan target segment for matching bytewise NEAR E8 displacement.

    E8 values in tables, immediates or undiscovered code are possible.
    Returned sites remain *unproven* until a validated CFG confirms that
    the E8 byte begins an instruction.
    """
    entry = image.segment(segment)
    if not entry.file_offset:
        return []
    raw = image.bytes_at(segment, 0, entry.length)
    candidates = []
    for ip in range(len(raw) - 2):
        if raw[ip] != 0xE8:
            continue
        displacement = struct.unpack_from("<h", raw, ip + 1)[0]
        if (ip + 3 + displacement) & 0xFFFF == target_offset:
            candidates.append(f"{segment}:{ip:04X}")
    return candidates


def audit(image: Any, segment: int = 3, offset: int = 0xD66C) -> dict[str, Any]:
    refs = reference_sites(image, segment, offset)
    near = raw_e8_candidates(image, segment, offset)
    classes = {}
    for item in refs:
        classes[item.kind] = classes.get(item.kind, 0) + 1
    direct = sorted([r.instruction_address for r in refs
                     if r.kind == "DIRECT_FAR_CALL"])
    potential = [r.as_dict() for r in refs
                 if r.kind not in ("DIRECT_FAR_CALL", "DIRECT_FAR_JUMP")]
    return {
        "target": f"{segment}:{offset:04X}",
        "expanded_internal_relocations_to_target": len(refs),
        "classes": classes,
        "direct_far_call_sites": direct,
        "direct_far_jump_sites": [
            r.instruction_address for r in refs if r.kind == "DIRECT_FAR_JUMP"],
        "non_direct_fixups_requiring_pointer_flow": potential,
        "all_target_fixups": [r.as_dict() for r in refs],
        "raw_e8_near_call_candidates_unverified": near,
        "evidence_scope": "NE fixup census and unaligned near E8 byte scan only",
        "all_runtime_indirect_calls_excluded": False,
        "limitations": [
            "NE segment-word fixups resolve some FAR pointers, but not target-dynamic callbacks",
            "An E8 byte scan is not a CFG-reachable direct NEAR CALL census",
            "Writable FAR slots and imported GetProcAddress callback dispatch require dataflow",
            "Relocation + opcode 9A alone cannot prove a newly discovered site is on a CFG instruction boundary; confirm each unfamiliar callsite with original disassembly",
            "A complete list of known fixups is not exhaustive proof of 100% dynamic target reachability",
        ],
    }


def assert_known_win110_direct_callers(report: dict[str, Any]) -> None:
    """Enforce only the two archived Ghidra original-ASM immediate caller edges.

    Additional target fixups must not be silently discarded; the audit
    reports them, but does not demand their absence.
    """
    expected = {"3:0F34", "3:0F70"}
    direct = set(report["direct_far_call_sites"])
    if not expected.issubset(direct):
        raise ValueError(
            f"Missing archived NE3:D66C direct calls: {sorted(expected-direct)}"
        )
