#!/usr/bin/env python3
"""Bounded provenance review for archived Nitemare Win16 1.10 REP writes.

All 83 records came from pre-existing original Ghidra textual disassembly.
25 REP MOVSD/STOSD sites have direct source-register/local destination
traces and lengths; the remaining 58 require further static pointer flow.
This file never claims complete Win16 x86 code coverage, runtime parity, or
an independently re-hashed Win16 v1.10 original executable.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_LEDGER=(ROOT/"other/n3d/builds_12/static_byte_evidence"
    /"N3D_Win110_Ghidra_REP_destination_register_20261020.csv")
EXPECTED_OPS={
    "STOSB.REP":(7,"F3 AA"),
    "STOSW.REP":(17,"F3 AB"),
    "STOSD.REP":(11,"F3 66 AB"),
    "MOVSB.REP":(14,"F3 A4"),
    "MOVSW.REP":(20,"F3 A5"),
    "MOVSD.REP":(14,"F3 66 A5"),
}
WATCHED_DGROUP=(0x00A2,0x46B2)
WIN110_DGROUP_FILE_BACKED_BYTES=36526 # Win16 1.10 logical segment 10, 0x8EAE
KNOWN_REP32=25
KNOWN_FIXED_32={
    "1010:5102":(0x4C74,42),
    "1010:DACA":(0x3930,20),
    "1010:DB65":(0x4BD4,20),
    "1010:51C5":(0x8E90,30),
    "1010:BA27":(0x4BE8,94),
}
KNOWN_HEAP_90B={"1010:4E21","1010:500E"}


def load_ledger(path:Path=DEFAULT_LEDGER)->list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))


def overlaps_linear_region(start:int,length:int,target:int)->bool:
    """Zero-length write is empty; reject invalid/wrapping DGROUP spans."""
    if not (0 <= start <= 65535) or not (0 <= length <= 65536):
        raise ValueError("Address/length outside a 16-bit segment")
    if start + length > 65536:
        raise ValueError("16-bit segment wrap requires separate proof")
    return start <= target < start+length


def provenance_audit(rows:list[dict[str,str]],
                     *, enforce_archived_census:bool=True)->dict[str,Any]:
    if not rows:
        raise ValueError("No archived REP records")
    all_sites=set()
    counts=Counter()
    class_counts=Counter()
    open_sites=[]
    bounded=[]
    fixed=[]
    for row in rows:
        site=row["site"]
        m=re.fullmatch(r"[0-9A-F]{4}:[0-9A-F]{4}",site)
        if m is None:
            raise ValueError("Invalid Ghidra logical site "+site)
        if site in all_sites:
            raise ValueError("Duplicate REP site "+site)
        all_sites.add(site)
        op=row["rep_operation"]
        if op not in EXPECTED_OPS:
            raise ValueError("Unknown REP mnemonic "+op)
        counts[op]+=1
        if row["opcode_hex"].upper()!=EXPECTED_OPS[op][1]:
            raise ValueError("REP opcode contradiction at "+site)
        category=row["destination_class"]
        class_counts[category]+=1
        n=row["bounded_total_write_bytes"]
        if n:
            length=int(n)
            if length<=0 or length>65536:
                raise ValueError("Invalid source-bounded REP length "+site)
            if op not in ("MOVSD.REP","STOSD.REP"):
                raise ValueError("Unexpected unreviewed REP length "+site)
            if category in ("DESTINATION_PROVENANCE_OPEN",
                            "GHIDRA_ANNOTATED_DEST_REQUIRES_BOUND"):
                raise ValueError("Length alone is not destination provenance "+site)
            bounded.append(site)
        if category in ("DESTINATION_PROVENANCE_OPEN",
                        "GHIDRA_ANNOTATED_DEST_REQUIRES_BOUND"):
            open_sites.append(site)
        if row["fixed_DGROUP_start"]:
            start=int(row["fixed_DGROUP_start"],0)
            if not n:
                raise ValueError("Fixed destination missing byte count "+site)
            length=int(n)
            if category!="FIXED_DATA_REGION":
                raise ValueError("Fixed offset without proven fixed-class "+site)
            if start+length>WIN110_DGROUP_FILE_BACKED_BYTES:
                raise ValueError("Fixed range exceeds original Win16 DGROUP file image")
            record={
                "source":site,
                "address":f"DS:{start:04X}",
                "last_written_address":f"DS:{start+length-1:04X}",
                "exclusive_end":f"DS:{start+length:04X}",
                "bytes":length,
                "overlap_DS_00A2":overlaps_linear_region(start,length,0x00A2),
                "overlap_DS_46B2":overlaps_linear_region(start,length,0x46B2),
            }
            fixed.append(record)

    actual={k:counts[k] for k in EXPECTED_OPS}
    expected={k:v[0] for k,v in EXPECTED_OPS.items()}
    if enforce_archived_census and actual!=expected:
        raise ValueError(f"REP textual census mismatch: {actual} vs {expected}")
    if enforce_archived_census and len(rows)!=83:
        raise ValueError(f"Expected 83 Ghidra textual REP sites, got {len(rows)}")
    if enforce_archived_census and len(bounded)!=KNOWN_REP32:
        raise ValueError("Expected exactly 25 inspected REP MOVSD/STOSD sites")
    if enforce_archived_census and set(bounded)!={
        r["site"] for r in rows if r["rep_operation"] in ("MOVSD.REP","STOSD.REP")
    }:
        raise ValueError("Not all 25 REP32 sites were inspected")
    if enforce_archived_census:
        if {r["source"] for r in fixed}!=set(KNOWN_FIXED_32):
            raise ValueError("Five expected fixed DGROUP destinations changed")
        for record in fixed:
            start,length=KNOWN_FIXED_32[record["source"]]
            if record["address"]!=f"DS:{start:04X}" or record["bytes"]!=length:
                raise ValueError("Original fixed REP destination span changed")
        if not KNOWN_HEAP_90B.issubset(set(bounded)):
            raise ValueError("Missing LocalAlloc 90-byte REP sources")
        if len(open_sites)!=58:
            raise ValueError(f"Expected 58 unresolved REP destinations, got {len(open_sites)}")

    return {
        "build":"Win16 v1.10",
        "source":"archived original Ghidra textual listing, not fresh 1.10 EXE bytes",
        "scope":"REP MOVS/STOS sites found in pre-existing analyzed original text",
        "total_rep_sites":len(rows),
        "opcode_type_counts":dict(actual),
        "source_byte_bounded_rep_movsd_stosd":len(bounded),
        "bounded_rep_sites":sorted(bounded),
        "destination_classes":dict(sorted(class_counts.items())),
        "remaining_rep_destinations_for_pointer_provenance":len(open_sites),
        "remaining_rep_sites":sorted(open_sites),
        "five_fixed_DGROUP_writes":fixed,
        "fixed_DGROUP_regions_exclude_clock_and_latch":all(
            not r["overlap_DS_46B2"] and not r["overlap_DS_00A2"] for r in fixed),
        "win110_DGROUP_file_backed_exclusive_end":"DS:8EAE",
        "DGROUP_tail_REP_STOSD_exclusive_end":next(
            (r["exclusive_end"] for r in fixed if r["source"]=="1010:51C5"),None),
        "local_heap_90_byte_destinations":sorted(KNOWN_HEAP_90B),
        "heap_destinations_disjoint_from_globals_only_under_valid_Win16_LocalAlloc_contract":True,
        "stack_destinations_disjoint_from_globals_only_under_valid_stack_segment_contract":True,
        "original_1_10_sha_reread_this_run":False,
        "alias_writer_graph_complete":False,
        "notes":[
            "Missing Ghidra REP sites in undiscovered code islands are not excluded",
            "All destination-provenance classes rely on original Ghidra local instructions",
            "Fixed DS ranges can be bounded algebraically independent of runtime stack or heap",
            "Other-segment, stack, heap and framebuffer disjointness uses valid OS segment/allocator semantics",
            "Other 58 REP destinations need interprocedural pointer/length or bounds proof",
            "Non-REP writes, computed SI/DI/BX/ES stores and call-based memcpy are separate",
        ],
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=DEFAULT_LEDGER)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        report=provenance_audit(load_ledger(args.input))
        rendered=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
        if args.output:
            args.output.write_text(rendered,encoding="utf-8")
            print("Reviewed 83 original textual REP sites; 25 local bounds, "
                  "5 fixed DGROUP spans, 58 pending pointer flows.")
            print(f"JSON report: {args.output}")
        else:
            print(rendered)
        return 0
    except (OSError,ValueError,KeyError) as exc:
        parser.exit(2,f"REP provenance evidence rejected: {exc}\n")


if __name__=="__main__":
    raise SystemExit(main())
