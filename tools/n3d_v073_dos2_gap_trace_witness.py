#!/usr/bin/env python3
"""Trace-execution witnesses for the *pinned* DOS v2.0 CAB8/1021E gaps.

Never equate 16-byte lookahead windows with executed instructions.
Reports offsets/counters/hashes only; no original code bytes or game assets.
For authentic results use the original user-owned N3D-E-20.EXE and N3DTRC01 ZIP
with the verified DOS load base. Static branches that never execute remain OPEN.
Optional dependency: capstone==5.0.3.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import zipfile

import n3d_v071_dos20_opcode_gap_audit as original

HEAD = struct.Struct("<8sII")
COMMON = struct.Struct("<cBHQQ")
CPU = struct.Struct("<6H3I8I16s4B")
MAGIC = b"N3DTRC01"
assert HEAD.size == 16 and COMMON.size == 20 and CPU.size == 76

RANGES = {
    "CAB8_projection": (0xCAB8, 0xCEDB),
    "FEFA_owner": (0xFEFA, 0x1003D),
    "1021E_visibility": (0x1021E, 0x104BD),
}


def decoder():
    try:
        import capstone
    except ImportError as exc:
        raise RuntimeError("Capstone 5 required (pip install capstone==5.0.3)") from exc
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    engine.detail = False
    return engine


def iterate_cpu(stream):
    header = stream.read(HEAD.size)
    if len(header) != HEAD.size:
        raise ValueError("Incomplete N3DTRC01 header")
    magic, version, _reserved = HEAD.unpack(header)
    if magic != MAGIC or version != 1:
        raise ValueError("Unsupported N3DTRC01 header or version")
    previous_seq = None
    while True:
        event_header = stream.read(COMMON.size)
        if not event_header:
            return
        if len(event_header) != COMMON.size:
            raise ValueError("Truncated event header")
        kind, v, size, event, instruction_seq = COMMON.unpack(event_header)
        if v != 1 or not COMMON.size <= size <= 16384:
            raise ValueError("Invalid N3DTRC01 event size or version")
        payload = stream.read(size - COMMON.size)
        if len(payload) != size - COMMON.size:
            raise ValueError("Truncated N3DTRC01 event payload")
        if kind != b"I":
            continue
        if size != 96:
            raise ValueError("CPU records must be 96 bytes")
        data = CPU.unpack(payload)
        cs, ds, es, ss, fs, gs, ip, linear_ip, flags = data[:9]
        code, code_valid, code32, pmode, reserved = data[17:]
        if code_valid > 16:
            raise ValueError("code_valid exceeds 16-byte CPU window")
        # A CPU record is a *pre-state*; contiguous prefix code_valid comes
        # directly from the DOSBox-X Advanced History tracing patch.
        yield {
            "event": event, "instruction_sequence": instruction_seq,
            "cs": cs, "ip": ip, "linear_ip": linear_ip,
            # 16-bit register lows from the real CPU pre-state. Optional
            # consumers include the v0.77 original 22CA wall-U witness.
            "ax": data[9] & 0xffff, "cx": data[11] & 0xffff,
            "si": data[13] & 0xffff, "di": data[14] & 0xffff,
            "code": code[:code_valid], "code_valid": code_valid,
            "code32": code32, "protected_mode": pmode,
        }


def routine_of(image_offset: int) -> str | None:
    for name, (start, end) in RANGES.items():
        if start <= image_offset <= end:
            return name
    return None


def witness_one(stream, image: bytes, load_segment: int, engine=None):
    if not 0 <= load_segment <= 0xFFFF:
        raise ValueError("load_segment must be a valid 16-bit value")
    if engine is None:
        engine = decoder()
    structures = {
        name: {
            "instruction_events": 0,
            "validated_executed_instruction_events": 0,
            "first_byte_disagrees_with_image": 0,
            "insufficient_code_valid": 0,
            "image_offset_outside_or_32bit": 0,
            "static_lookahead_gap_bytes": set(),
            "actual_decoded_executed_gap_bytes": set(),
            "executed_instruction_starts": set(),
            "observed_gap_instruction_starts": set(),
            "branch_targets_count": {},
        }
        for name in RANGES
    }
    scanned = 0
    outside = 0
    prev = None
    for row in iterate_cpu(stream):
        scanned += 1
        if row["protected_mode"] or row["code32"] or row["ip"] > 0xFFFF:
            prev = None
            outside += 1
            continue
        offset = (row["cs"] - load_segment) * 16 + row["ip"]
        name = routine_of(offset)
        if name is None:
            prev = None
            outside += 1
            continue
        record = structures[name]
        record["instruction_events"] += 1
        if prev is not None and prev["offset"] == 0xCBF2 and prev["is_branch"] and name == "CAB8_projection":
            if offset in (0xCED6,0xCBF6):
                key = f"0x{offset:05X}"
                record["branch_targets_count"][key] = record["branch_targets_count"].get(key,0)+1
        prev = None  # A failed or undecodable CPU row cannot witness a branch.
        prefix = row["code"]
        if not prefix:
            record["insufficient_code_valid"] += 1
            continue
        if offset < 0 or offset+len(prefix) > len(image):
            record["image_offset_outside_or_32bit"] += 1
            continue
        original_slice = image[offset:offset+len(prefix)]
        # Window observations require *individual matching bytes*, and are
        # never automatically counted as executed code.
        gap_ranges = original.RUNTIME_HOLES[name]
        for j, byte in enumerate(prefix):
            addr = offset+j
            if original_slice[j] == byte and any(lo <= addr <= hi for lo,hi in gap_ranges):
                record["static_lookahead_gap_bytes"].add(addr)
        if prefix[0] != original_slice[0]:
            record["first_byte_disagrees_with_image"] += 1
            continue
        ins = list(engine.disasm(prefix, row["ip"], count=1))
        if not ins or len(prefix) < ins[0].size:
            record["insufficient_code_valid"] += 1
            continue
        size = ins[0].size
        if prefix[:size] != original_slice[:size]:
            record["first_byte_disagrees_with_image"] += 1
            continue
        record["validated_executed_instruction_events"] += 1
        mnemonic = ins[0].mnemonic.lower()
        prev = {"offset": offset, "is_branch": mnemonic.startswith("j") or mnemonic.startswith("loop")}
        record["executed_instruction_starts"].add(offset)
        for addr in range(offset,offset+size):
            if any(lo<=addr<=hi for lo,hi in gap_ranges):
                record["actual_decoded_executed_gap_bytes"].add(addr)
                record["observed_gap_instruction_starts"].add(offset)
    result = {}
    for name, obj in structures.items():
        start,end=RANGES[name]
        gap_total=sum(hi-lo+1 for lo,hi in original.RUNTIME_HOLES[name])
        result[name] = {
            "image_range": [f"0x{start:05X}",f"0x{end:05X}"],
            "instruction_events": obj["instruction_events"],
            "validated_instruction_events": obj["validated_executed_instruction_events"],
            "instruction_starts_validated": len(obj["executed_instruction_starts"]),
            "mismatch_events_first_or_executed_byte": obj["first_byte_disagrees_with_image"],
            "insufficient_window_events": obj["insufficient_code_valid"],
            "static_gap_bytes": gap_total,
            "lookahead_matching_gap_bytes": len(obj["static_lookahead_gap_bytes"]),
            "executed_decoded_gap_bytes": len(obj["actual_decoded_executed_gap_bytes"]),
            "executed_gap_instruction_starts": sorted(
                f"0x{k:05X}" for k in obj["observed_gap_instruction_starts"]),
            "observed_branch_targets_from_CBF2": obj["branch_targets_count"],
            "gap_runtime_proven_complete": (
                len(obj["actual_decoded_executed_gap_bytes"]) == gap_total
            ),
            "semantic_equivalence_proven": False,
        }
    return {
        "evidence": "AUTHENTIC_TRACE_IF_ORIGINAL_EXE_AND_TRACE_VERIFIED",
        "trace_authenticity_independently_verified": False,
        "load_segment_user_supplied": f"0x{load_segment:04X}",
        "instructions_scanned": scanned,
        "instructions_outside_selected_routines": outside,
        "routines": result,
        "original_vs_remake_pixel_parity": "NOT_TESTED",
        "warning": "Lookahead bytes are not executed instructions. No new runtime session, control-flow completeness, or frame parity is claimed.",
    }


def witness_zip(path: Path, exe: bytes, load_segment: int):
    original.verify_original_exe(exe)
    image = exe[original.IMAGE_HEADER_BYTES:]
    engine = decoder()
    sessions = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir() or not member.filename.lower().endswith(".n3dt"):
                continue
            with archive.open(member) as stream:
                proof = witness_one(stream,image,load_segment,engine)
            proof["archive_member"] = member.filename
            proof["uncompressed_size_bytes"] = member.file_size
            sessions.append(proof)
    if not sessions:
        raise ValueError("ZIP contains no .n3dt trace streams")
    verified_events = sum(
        s["routines"][name]["validated_instruction_events"]
        for s in sessions for name in RANGES
    )
    if verified_events < 32:
        raise ValueError(
            "Insufficient verified CPU instruction witnesses in selected DOS2 routines; "
            "check load segment, EXE version, and trace integrity (minimum 32)")
    # Keep branch coverage session-local, only aggregate exact evidence counts.
    totals = {}
    for name in RANGES:
        rr = [s["routines"][name] for s in sessions]
        totals[name] = {
            "instruction_events": sum(x["instruction_events"] for x in rr),
            "validated_instruction_events": sum(x["validated_instruction_events"] for x in rr),
            "sessions_with_executed_gap_witness": sum(x["executed_decoded_gap_bytes"] > 0 for x in rr),
            "sessions_with_only_lookahead_or_no_gap_witness": sum(x["executed_decoded_gap_bytes"] == 0 for x in rr),
            "witnessed_gap_byte_lower_bound": max(x["executed_decoded_gap_bytes"] for x in rr),
            "note": "Lower bound is a max over per-session sets, not their union.",
        }
    return {
        "schema": "n3d-v073-original-trace-gap-witness-v1",
        "original_exe_sha256": original.EXE_SHA,
        "trace_zip_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sessions": sessions,
        "aggregate": totals,
        "whole_game_renderer_parity": "NOT_VERIFIED",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--trace-zip",required=True,type=Path)
    p.add_argument("--load-segment",required=True,type=lambda x:int(x,0))
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    try:
        result=witness_zip(a.trace_zip,a.exe.read_bytes(),a.load_segment)
    except (OSError,ValueError,RuntimeError,zipfile.BadZipFile) as exc:
        p.exit(2,f"UNVERIFIED: {exc}\n")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "schema":result["schema"],"sessions":len(result["sessions"]),
        "aggregate":result["aggregate"],"out":str(a.out)
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
