#!/usr/bin/env python3
"""Eight archived Win16 v1.10 memcpy NE2:6C80 direct caller contracts.

Sources: user's original Win16 Ghidra ASM nite3w(1).docx, plus the
original NE2:6C80 instruction/offset ledger. This is a *caller-specific
static proof*, not a fresh binary SHA recheck, heap safety proof,
runtime observation, full dynamic FAR edge proof or proof of 1:1 parity.

All 8 named direct callers have a recovered count, source and destination
expression. Where length/capacity arithmetic is 16-bit or signed, model
those facts explicitly and keep external input and alias reachability OPEN.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from n3d_win16_rep_destination_audit import MEMCPY_NAMED_DIRECT_CALLERS

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=(ROOT/"other/n3d/builds_12/static_byte_evidence"
    /"N3D_Win110_memcpy_6C80_direct_callers_20261020.csv")

# Original NE1/NE2 code XREF locations, *not* a list of all possible
# computed far pointers to 1008:6C80.
EXACT_DIRECT_CALLERS={
    "1000:0DD0","1000:0E16","1000:0E51","1000:0ED9",
    "1000:0EEA","1000:0F74","1000:4C72","1008:3F20",
}
EXPECTED_CALLER_ENTRIES={
    "1000:0DD0":"1000:0DA0",
    "1000:0E16":"1000:0DDE",
    "1000:0E51":"1000:0E26",
    "1000:0ED9":"1000:0EBA",
    "1000:0EEA":"1000:0EBA",
    "1000:0F74":"1000:0F4C",
    "1000:4C72":"1000:4C38",
    "1008:3F20":"1008:3EBE",
}
CAPACITY_SIGNED_BRANCH_SITES={
    "1000:0E51":"JGE",
    "1000:0F74":"JGE",
    "1000:4C72":"JLE",
}
ADDITION_WRAP_CONCERN_SITES={
    "1000:0DD0","1000:0ED9","1000:0EEA","1000:4C72",
}
INPUT_COUNT_PROVEN_FIT_ALL_STATES=False

def u16(n:int)->int:
    return n & 0xFFFF

def i16(n:int)->int:
    n=u16(n)
    return n-0x10000 if n & 0x8000 else n

def check_u16(n:int, parameter:str)->None:
    if not isinstance(n,int) or not 0<=n<=0xFFFF:
        raise ValueError(parameter+" must be unsigned 16-bit")

def append_direct_fast_path(used:int, added:int, capacity:int)->bool:
    """Original 1000:4C40..4C49: AX=uint16(used+added);
    CMP AX,[SI+4]; JLE (signed), before 1000:4C72 memcpy.

    DOES NOT assert that struct invariants make this fast branch safe.
    """
    for name,n in (("used",used),("added",added),("capacity",capacity)):
        check_u16(n,name)
    return i16(u16(used+added)) <= i16(capacity)

def enough_capacity_signed(capacity:int,requested:int)->bool:
    """Original NE1:0E30 + 0E33 JGE and 0F58 + 0F5B JGE.

    This is a CPU signed comparison, not unsigned length safety.
    """
    check_u16(capacity,"capacity")
    check_u16(requested,"requested")
    return i16(capacity)>=i16(requested)

def additive_required_len_u16(prefix:int,suffix:int)->int:
    """NE1:0EC7 and related ADD AX,word instructions wrap to uint16.
    A caller passing this length to 0:D3E may lose carry."""
    check_u16(prefix,"prefix")
    check_u16(suffix,"suffix")
    return u16(prefix+suffix)

def requested_localalloc_size_for_string_length(count:int)->int:
    """NE1:0D57 LEA AX,[DI+1] requests count+1, wrapping in uint16.
    A KERNEL LocalAlloc helper may substitute 1 for zero requests.
    No allocation-success claim is implied.
    """
    check_u16(count,"count")
    return u16(count+1)

def clamped_stream_chunk(available:int,remaining:int)->int:
    """1008:3F12 CMP AX,CX; JBE, else MOV AX,CX: unsigned min.
    The stream caller additionally rejects zero available before copy.
    """
    check_u16(available,"available")
    check_u16(remaining,"remaining")
    return min(available,remaining)

def load_manifest(path:Path=DEFAULT_MANIFEST)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def audit(rows:list[dict[str,str]])->dict[str,Any]:
    if len(rows)!=8:
        raise ValueError("Expected eight original memcpy caller records")
    sites=set()
    by_site={}
    for row in rows:
        site=row["site"]
        if site in sites:
            raise ValueError("Duplicate original memcpy caller "+site)
        sites.add(site)
        by_site[site]=row
        if site not in EXPECTED_CALLER_ENTRIES:
            raise ValueError("Unexpected memcpy caller "+site)
        if row["caller_entry"]!=EXPECTED_CALLER_ENTRIES[site]:
            raise ValueError("Caller function entry mismatch "+site)
        for key in ("destination_operand","source_operand",
                    "copy_count_operand","local_capacity_or_allocation_guard",
                    "guard_width","local_static_conclusion",
                    "unclosed_obligation"):
            if not row[key].strip():
                raise ValueError(f"Missing {key} provenance at "+site)
        if not row["unclosed_obligation"].strip():
            raise ValueError("Alias safety incorrectly marked closed "+site)

    if sites!=EXACT_DIRECT_CALLERS or sites!=MEMCPY_NAMED_DIRECT_CALLERS:
        raise ValueError("Incomplete original 1008:6C80 direct XREF census")
    for site,branch in CAPACITY_SIGNED_BRANCH_SITES.items():
        row=by_site[site]
        if (branch not in row["local_capacity_or_allocation_guard"]
            or "signed" not in row["guard_width"].split()):
            raise ValueError("Original signed capacity branch missing "+site)
    for site in ADDITION_WRAP_CONCERN_SITES:
        if "uint16" not in (
            by_site[site]["guard_width"]+
            by_site[site]["local_capacity_or_allocation_guard"]):
            raise ValueError("16-bit overflowing ADD evidence missing "+site)
    if "min(" not in by_site["1008:3F20"]["copy_count_operand"]:
        raise ValueError("Unsigned stream transfer minimum is missing")
    if "LocalAlloc" not in by_site["1000:0E16"]["local_capacity_or_allocation_guard"]:
        raise ValueError("Unproven strdup allocation path")

    return {
        "target":"NE2:6C80",
        "version":"NITE3W original Win16 1.10 (archived Ghidra text)",
        "direct_named_caller_count":len(sites),
        "direct_far_call_sites":sorted(sites-{"1008:3F20"}),
        "near_call_with_explicit_push_CS":"1008:3F20",
        "caller_entries":{k:v for k,v in sorted(EXPECTED_CALLER_ENTRIES.items())},
        "full_argument_provenance_recorded_for_all_eight":True,
        "signed_capacity_compare_sites":CAPACITY_SIGNED_BRANCH_SITES,
        "modulo_16_bit_addition_sites":sorted(ADDITION_WRAP_CONCERN_SITES),
        "input_count_proven_fit_all_states":INPUT_COUNT_PROVEN_FIT_ALL_STATES,
        "memcpy_helper_target_alias_excluded_for_all_states":False,
        "memcpy_helper_copy_sites_closed_in_full_program":0,
        "win16_original_exe_freshly_rehashed_in_this_run":False,
        "normal_valid_heap_contract_can_bound_some_caller_paths":True,
        "unsigned_stream_transfer_minimum_site":"1008:3F12/3F14",
        "literal_tested_counterexamples":[
            {
                "site":"1000:4C72",
                "used":65530,"added":10,"capacity":20,
                "wrapped_sum":additive_required_len_u16(65530,10),
                "signed_fast_append_taken":append_direct_fast_path(65530,10,20),
                "length_really_fits_unsigned_capacity":False,
            },
            {
                "site":"1000:0E51",
                "capacity":32767,"requested":32768,
                "signed_skip_resize":enough_capacity_signed(32767,32768),
                "unsigned_capacity_enough":False,
            },
            {
                "site":"1000:0F74",
                "capacity":32767,"requested":32768,
                "signed_skip_resize":enough_capacity_signed(32767,32768),
                "unsigned_capacity_enough":False,
            },
            {
                "site":"1000:0EBA",
                "prefix":65530,"suffix":10,
                "wrapped_requested_count":additive_required_len_u16(65530,10),
                "true_unbounded_sum":65540,
            },
        ],
        "proof_limits":[
            "Direct XREFs only; indirect FAR calls and computed pointers remain OPEN",
            "Count expressions recovered, but external struct/caller invariants not fully proved",
            "Signed/uint16 overflow is a local arithmetic witness, not runtime reachability",
            "No claim of writes to DGROUP DS:46B2 via arbitrary invalid buffer",
            "No 1:1 timing, rendering or gameplay runtime assertion",
        ],
    }

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        report=audit(load_manifest(args.manifest))
        txt=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
        if args.output:
            args.output.write_text(txt,encoding="utf-8")
            print("Win16 memcpy 6C80: all 8 direct caller arguments typed; "
                  "global capacity/alias reachability remains OPEN.")
        else:
            print(txt)
        return 0
    except (OSError,KeyError,ValueError) as exc:
        parser.exit(2,"Win16 memcpy proof rejected: "+str(exc)+"\n")

if __name__=="__main__":
    raise SystemExit(main())
