#!/usr/bin/env python3
"""Bounded provenance review for archived Nitemare Win16 1.10 REP writes.

All 83 records came from pre-existing original Ghidra textual disassembly.
25 REP MOVSD/STOSD and 9 REP MOVSW/STOSW sites have original source
destination/length traces; the remaining 49 need more pointer flow.
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
KNOWN_REP16_BOUNDED={
    "1000:11D3":18,
    "1000:1294":18,
    "1000:2B57":18,
    "1000:2BE2":18,
    "1000:3CAD":18,
    "1008:6A11":32,
    "1008:6A6B":32,
    "1008:6AC3":32,
    "1008:6B18":32,
}
KNOWN_FIXED_16={
    "1000:1294":(0x423E,18),
    "1000:2BE2":(0x423E,18),
}
KNOWN_BOUNDED_TOTAL=KNOWN_REP32+len(KNOWN_REP16_BOUNDED)
STRING_STAGING_START=0x36BE
STRING_CLOCK_FLAG=0x46B2
STRING_CLOCK_OFFSET=STRING_CLOCK_FLAG-STRING_STAGING_START
STRING_STAGING_SITES={"1010:527E","1010:5282","1010:52A1","1010:52A5"}
# Original DS:101E = "config.sav\0"; direct callers 3:52F5 and 3:5358.
FIXED_CONFIG_SAV_SUFFIX_CHARACTERS=10
FIXED_CONFIG_SAV_CALLERS={"1010:52F5","1010:5358"}
DYNAMIC_STRING_CALLERS={"1010:5397","1010:548C","1010:5759"}
OPEN_CATEGORIES={
    "DESTINATION_PROVENANCE_OPEN",
    "GHIDRA_ANNOTATED_DEST_REQUIRES_BOUND",
    "STRING_DSGROUP_BUFFER_NO_LENGTH_BOUND",
}


def unbounded_string_copy_reaches_clock(prefix_characters:int,
                                        appended_characters:int)->bool:
    """Conditional address arithmetic, NOT input-length reachability proof.

    Original 3:5260 copies a NUL-terminated prefix to DS:36BE then
    appends another NUL-terminated string. The last copied NUL is at
    DS:36BE+prefix_characters+appended_characters. For 16-bit,
    nonwrapping strings the flag DS:46B2 is reached once that final
    offset is >=0xFF4 (4084).
    """
    if prefix_characters<0 or appended_characters<0:
        raise ValueError("String lengths cannot be negative")
    final_offset=prefix_characters+appended_characters
    if STRING_STAGING_START+final_offset>=0x10000:
        raise ValueError("String copy wraps DGROUP: requires separate model")
    return final_offset>=STRING_CLOCK_OFFSET


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
    bounded32=[]
    bounded16=[]
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
            if op not in ("MOVSD.REP","STOSD.REP","MOVSW.REP","STOSW.REP"):
                raise ValueError("Unexpected unreviewed REP length "+site)
            if category in OPEN_CATEGORIES:
                raise ValueError("Length alone is not destination provenance "+site)
            bounded.append(site)
            if op in ("MOVSD.REP","STOSD.REP"):
                bounded32.append(site)
            else:
                bounded16.append(site)
        if category in OPEN_CATEGORIES:
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
    if enforce_archived_census and len(bounded)!=KNOWN_BOUNDED_TOTAL:
        raise ValueError("Expected exactly 34 source-bounded REP sites")
    if enforce_archived_census and {
        row["site"] for row in rows
        if row["destination_class"]=="STRING_DSGROUP_BUFFER_NO_LENGTH_BOUND"
    }!=STRING_STAGING_SITES:
        raise ValueError("Four archived string-staging copy site classifications changed")
    if enforce_archived_census and set(bounded32)!={
        r["site"] for r in rows if r["rep_operation"] in ("MOVSD.REP","STOSD.REP")
    }:
        raise ValueError("Not all 25 REP32 sites were inspected")
    if enforce_archived_census and set(bounded16)!=set(KNOWN_REP16_BOUNDED):
        raise ValueError("Nine archived REP16 destination sites changed")
    if enforce_archived_census:
        for row in rows:
            site=row["site"]
            if site in KNOWN_REP16_BOUNDED:
                if int(row["bounded_total_write_bytes"])!=KNOWN_REP16_BOUNDED[site]:
                    raise ValueError("Archived REP16 instruction length mismatch "+site)
        all_fixed={**KNOWN_FIXED_32,**KNOWN_FIXED_16}
        if {r["source"] for r in fixed}!=set(all_fixed):
            raise ValueError("Seven expected fixed DGROUP destinations changed")
        for record in fixed:
            start,length=all_fixed[record["source"]]
            if record["address"]!=f"DS:{start:04X}" or record["bytes"]!=length:
                raise ValueError("Original fixed REP destination span changed")
        if not KNOWN_HEAP_90B.issubset(set(bounded)):
            raise ValueError("Missing LocalAlloc 90-byte REP sources")
        if len(open_sites)!=49:
            raise ValueError(f"Expected 49 unresolved REP destinations, got {len(open_sites)}")

    return {
        "build":"Win16 v1.10",
        "source":"archived original Ghidra textual listing, not fresh 1.10 EXE bytes",
        "scope":"REP MOVS/STOS sites found in pre-existing analyzed original text",
        "total_rep_sites":len(rows),
        "opcode_type_counts":dict(actual),
        "source_byte_bounded_rep_movsd_stosd":len(bounded32),
        "source_byte_bounded_rep_movsw_stosw":len(bounded16),
        "source_byte_bounded_rep_total":len(bounded),
        "bounded_rep_sites":sorted(bounded),
        "destination_classes":dict(sorted(class_counts.items())),
        "remaining_rep_destinations_for_pointer_provenance":len(open_sites),
        "remaining_rep_sites":sorted(open_sites),
        "unbounded_string_staging_REP_sites":sorted(
            row["site"] for row in rows
            if row["destination_class"]=="STRING_DSGROUP_BUFFER_NO_LENGTH_BOUND"),
        "string_staging_start":"DS:36BE",
        "timer_flag_in_staging_region":"DS:46B2",
        "string_staging_distance_to_flag_bytes":STRING_CLOCK_OFFSET,
        "last_NUL_overlaps_clock_if_sum_characters_at_least":STRING_CLOCK_OFFSET,
        "fixed_config_sav_string":"config.sav",
        "fixed_config_sav_characters":FIXED_CONFIG_SAV_SUFFIX_CHARACTERS,
        "fixed_config_sav_callers":sorted(FIXED_CONFIG_SAV_CALLERS),
        "other_parameter_or_register_string_callers":sorted(DYNAMIC_STRING_CALLERS),
        "prefix_characters_required_to_touch_clock_with_config_sav":(
            STRING_CLOCK_OFFSET-FIXED_CONFIG_SAV_SUFFIX_CHARACTERS),
        "string_alias_dynamic_reachability_proven":False,
        "five_fixed_DGROUP_writes":[
            record for record in fixed if record["source"] in KNOWN_FIXED_32],
        "seven_fixed_DGROUP_writes":fixed,
        "additional_two_18byte_fixed_DGROUP_writes":[
            record for record in fixed if record["source"] in KNOWN_FIXED_16],
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
            "Other 49 REP destinations need interprocedural pointer/length or bounds proof",
            "Four string copies at DS:36BE could overlap DS:46B2 if NUL-terminated combined char count >=4084; actual input reachability unproved",
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
            print("Reviewed 83 original textual REP sites; 34 local bounds "
                  "(25 REP32 + 9 REP16), 7 fixed DGROUP spans, 49 pending.")
            print(f"JSON report: {args.output}")
        else:
            print(rendered)
        return 0
    except (OSError,ValueError,KeyError) as exc:
        parser.exit(2,f"REP provenance evidence rejected: {exc}\n")


if __name__=="__main__":
    raise SystemExit(main())
