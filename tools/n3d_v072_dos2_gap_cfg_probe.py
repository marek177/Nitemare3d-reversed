#!/usr/bin/env python3
"""Locally inspect *pinned* original DOS2 CAB8/1021E CFG via Capstone 16-bit.

Does NOT contain, export, or publish original executable/opcode bytes.
Instruction-boundary and *direct-edge* reachability is heuristic: indirect
jumps, FAR control transfers, data overlays, relocations, different segment
bases, and runtime state may invalidate the inferred CFG. Report never declares
dead code or 100% semantics.
Optional dependency: pip install capstone==5.0.3
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import n3d_v071_dos20_opcode_gap_audit as previous


def capstone_module():
    try:
        import capstone
        from capstone.x86 import X86_OP_IMM
        return capstone, X86_OP_IMM
    except ImportError as exc:
        raise RuntimeError("Capstone is required: pip install capstone==5.0.3") from exc


def probe_image(image: bytes, first: int, last: int,
                gaps: tuple[tuple[int, int], ...]) -> dict:
    """Explore only statically direct edges from first. No execution proof."""
    if first < 0 or last < first or last >= len(image):
        raise ValueError("CFG image boundary out of range")
    capstone, X86_OP_IMM = capstone_module()
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    decoder.detail = True
    todo = [first]
    decoded_starts: dict[int, tuple[int, str]] = {}
    byte_ownership: dict[int, int] = {}
    errors: list[dict] = []
    external: list[dict] = []
    indirect: list[dict] = []
    gap_touched: set[int] = set()
    while todo:
        offset = todo.pop()
        if offset in decoded_starts or not first <= offset <= last:
            continue
        logical_ip = offset & 0xFFFF
        try:
            instructions = list(decoder.disasm(
                image[offset:min(len(image),offset+15)], logical_ip, count=1))
        except (ValueError, capstone.CsError) as exc:
            errors.append({"offset":hex(offset),"error":"decode_exception","detail":str(exc)})
            continue
        if not instructions:
            errors.append({"offset":hex(offset),"error":"undecodable"})
            continue
        ins = instructions[0]
        size = ins.size
        if size <= 0 or offset+size-1 > last:
            errors.append({"offset":hex(offset),"error":"instruction_crosses_function_boundary"})
            continue
        mn = ins.mnemonic.lower()
        decoded_starts[offset] = size,mn
        for i in range(size):
            addr = offset+i
            if addr in byte_ownership and byte_ownership[addr] != offset:
                errors.append({"offset":hex(addr),"error":"overlapping_instruction_paths"})
            byte_ownership[addr] = offset
            if any(a <= addr <= b for a,b in gaps):
                gap_touched.add(addr)
        is_jump = mn in ("jmp","ljmp") or mn.startswith("j") or mn.startswith("loop")
        is_cond = (mn.startswith("j") and mn not in ("jmp","ljmp")) or mn.startswith("loop")
        is_call = mn in ("call","lcall")
        is_terminator = mn.startswith("ret") or mn in ("iret","hlt","ud2")
        fallthrough = offset+size
        destination = None
        if is_jump or is_call:
            if len(ins.operands)>0 and ins.operands[0].type == X86_OP_IMM:
                # A 16-bit local IP wraps at 0xFFFF. The DOS2 image range can
                # exceed that, so remap the target within the current 64KiB band.
                destination = (offset & ~0xFFFF) + (ins.operands[0].imm & 0xFFFF)
            else:
                indirect.append({"offset":hex(offset),"mnemonic":mn})
        if destination is not None:
            if first <= destination <= last:
                todo.append(destination)
            else:
                external.append({"from":hex(offset),"to":hex(destination),
                                 "mnemonic":mn})
        if is_call or is_cond or (not is_jump and not is_terminator):
            if first <= fallthrough <= last:
                todo.append(fallthrough)
    unknown = sorted(
        addr for a,b in gaps for addr in range(a,b+1)
        if addr not in gap_touched)
    instructions_in_gap = [
        {"image_offset":hex(off),"size":size,"mnemonic":mn}
        for off,(size,mn) in sorted(decoded_starts.items())
        if any(a <= q <= b for a,b in gaps for q in range(off,off+size))
    ]
    return {
        "evidence_level": "STATIC_DIRECT_EDGE_CFG_HEURISTIC",
        "status": "PARTIAL_REQUIRES_MANUAL_ASM_AND_ORIGINAL_RUNTIME",
        "routine": [hex(first),hex(last)],
        "original_trace_gap_regions": [[hex(a),hex(b)] for a,b in gaps],
        "original_trace_gap_byte_count": sum(b-a+1 for a,b in gaps),
        "direct_cfg_decoded_gap_bytes": len(gap_touched),
        "not_reached_by_direct_cfg_gap_bytes": len(unknown),
        "not_reached_by_direct_cfg_gap_offsets": [hex(x) for x in unknown],
        "instructions_touching_gap": instructions_in_gap,
        "direct_cfg_instructions": len(decoded_starts),
        "possible_external_edges": external,
        "indirect_edges_unresolved": indirect,
        "decode_errors_or_overlaps": errors,
        "warning": "Absence from direct CFG is NOT dead-code proof, and decoded bytes are NOT runtime execution.",
    }


def audit_executable(raw: bytes) -> dict:
    previous.verify_original_exe(raw)
    original = previous.audit_bytes(raw)
    if not original["routines"]["FEFA_owner"]["matches_archived_FEFA_trace_hash"]:
        raise ValueError("FEFA static image disagrees with original trace")
    image = raw[previous.IMAGE_HEADER_BYTES:]
    blocks = {}
    for name in ("CAB8_projection","1021E_visibility"):
        start,end,_ = previous.ROUTINES[name]
        blocks[name] = probe_image(image,start,end,previous.RUNTIME_HOLES[name])
    return {
        "tool": "n3d_v072_dos2_gap_cfg_probe",
        "original_exe_sha256": previous.EXE_SHA,
        "original_exe_size": previous.EXE_SIZE,
        "decoded_from_original_exe": True,
        "source_exported": False,
        "proprietary_machine_bytes_in_report": False,
        "branches_proved_executed": False,
        "functions": blocks,
    }


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",required=True,type=Path)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    try:
        report=audit_executable(args.exe.read_bytes())
    except (OSError,RuntimeError,ValueError) as exc:
        ap.exit(2,"No accepted static audit: "+str(exc)+"\n")
    output=json.dumps(report,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
