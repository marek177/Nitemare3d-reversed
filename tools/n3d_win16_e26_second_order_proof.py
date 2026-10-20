#!/usr/bin/env python3
"""Win16 1.10 E26 large memcpy-to-shared-empty reachability frontier.

This strict original Ghidra direct-call XREF proof inventories all TEN
second-order callers to the TWO remaining non-bounded immediate wrappers
0E6A -> E26(0E7B) and 0E88 -> E26(0EAB). Original LOADSTRING
E26 at 1000:3275 already has 255-byte bound, covered by the older
string_trio_lifecycle_audit.py.

Not an original EXE SHA recheck, runtime, indirect FAR complete census,
or claim that huge 0x8000 copy from shared DS:0584 is actually reachable.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=(ROOT/"other/n3d/builds_12/static_byte_evidence"
         /"N3D_Win110_E26_second_order_caller_sources_20261020.csv")
NEAR_TRIO_WRAPPER="1000:0E6A"
NEAR_STRLEN_WRAPPER="1000:0E88"
EXPECTED_GROUPS={
    NEAR_TRIO_WRAPPER:{
        "1000:4FF9","1000:69DF","1000:A3F6","1000:A577",
        "1008:16CA","1008:16E7"
    },
    NEAR_STRLEN_WRAPPER:{
        "1000:A407","1000:A8E7","1008:1430","1008:15F7"
    },
}
EXPECTED_INNER={
    NEAR_TRIO_WRAPPER:"1000:0E7B",
    NEAR_STRLEN_WRAPPER:"1000:0EAB",
}
POTENTIALLY_DANGEROUS_MIN_LENGTH=0x8000
RESOURCE_LOADSTRING_CALL="1000:3275"
RESOURCE_LOADSTRING_MAX=255
EMPTY_SHARED_DS_OFFSET=0x0584
CLOCK_FLAG_DS_OFFSET=0x46B2


def load_ledger(path:Path=DEFAULT)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def audit(rows:list[dict[str,str]])->dict[str,Any]:
    if len(rows)!=10:
        raise ValueError("Win16 E26 second-order original XREF list requires 10 paths")
    seen=set()
    groups={}
    for row in rows:
        site=row["callsite"]
        if site in seen:
            raise ValueError("Duplicate Win16 E26 second-order call "+site)
        seen.add(site)
        wrapper=row["target_wrapper"]
        if wrapper not in EXPECTED_GROUPS or site not in EXPECTED_GROUPS[wrapper]:
            raise ValueError("Original E26 helper caller/wrapper mismatch "+site)
        if row["E26_direct_inner_callsite"]!=EXPECTED_INNER[wrapper]:
            raise ValueError("Original E26 inner direct callsite mismatch "+site)
        for col in ("destination_trio_origin","source_origin","n_source",
                    "original_static_proof_grade","next_static_obligation"):
            if not row[col]:
                raise ValueError(f"Missing {col} provenance for "+site)
        if row["upper_bound_characters_verified"]:
            raise ValueError("Unverified huge-source upper bound was invented at "+site)
        if row["excludes_unsigned_n_ge_8000"].lower()!="false":
            raise ValueError("Cannot exclude E26 n>=8000 from source-provenance-only "+site)
        if wrapper==NEAR_TRIO_WRAPPER:
            if "+2" not in row["n_source"] or "used" not in row["n_source"]:
                raise ValueError("Source trio used-word origin missing at "+site)
        elif "strlen" not in row["n_source"]:
            raise ValueError("Input string length origin missing at "+site)
        groups.setdefault(wrapper,[]).append(site)
    if {k:set(v) for k,v in groups.items()}!=EXPECTED_GROUPS:
        raise ValueError("Win16 E26 second-order direct CALL fanout incomplete")
    return {
        "version":"Nitemare 3-D original Win16 1.10 archived Ghidra",
        "e26_direct_wrappers":{
            "1000:0E7B":{"caller":"1000:0E6A","second_order_sites":sorted(groups[NEAR_TRIO_WRAPPER]),"n":"source_trio.used"},
            "1000:0EAB":{"caller":"1000:0E88","second_order_sites":sorted(groups[NEAR_STRLEN_WRAPPER]),"n":"strlen(source) or 0 when source null"},
        },
        "second_order_sites_in_known_original_direct_graph":10,
        "source_trio_second_order_sites":len(groups[NEAR_TRIO_WRAPPER]),
        "source_strlen_second_order_sites":len(groups[NEAR_STRLEN_WRAPPER]),
        "third_e26_direct_caller":RESOURCE_LOADSTRING_CALL,
        "third_e26_direct_caller_api_bound":RESOURCE_LOADSTRING_MAX,
        "third_direct_caller_excludes_32768":True,
        "other_two_direct_wrapper_input_32768_excluded":False,
        "underlying_target_memory_interval_if_no_realloc_at_n32768":{
            "first":f"DS:{EMPTY_SHARED_DS_OFFSET:04X}",
            "last":f"DS:{EMPTY_SHARED_DS_OFFSET + POTENTIALLY_DANGEROUS_MIN_LENGTH - 1:04X}",
            "clock_flag":f"DS:{CLOCK_FLAG_DS_OFFSET:04X}",
        },
        "reachability_of_n_ge_32768_proven":False,
        "complete_dynamic_e26_callgraph_proven":False,
        "original_1_10_SHA_reverified_in_this_pass":False,
        "limitations":[
            "These 10 are the names in the archived direct XREF graph; not 10 independent runtime paths",
            "Six source-trio+2 lengths depend on prior triple writers and pointer aliases",
            "Four near-string lengths depend on upstream Win16 UI/data sources and termination",
            "Indexed table and object fields have source expressions but no global reachability bound",
            "Bound of COMMDLG.GetFileTitle(256) AFTER 1008:15F7 call cannot bound its earlier source",
            "Do not claim the conditional DS:46B2 copied-into-memory scenario occurs in normal gameplay",
        ],
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    try:
        result=audit(load_ledger(a.input))
        serialized=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
        if a.output:
            a.output.write_text(serialized,encoding="utf-8")
            print("E26 second-order direct callers: 6 source-trio, 4 strlen; bounds remain OPEN")
        else:
            print(serialized)
        return 0
    except (OSError,ValueError,KeyError) as ex:
        p.exit(2,f"E26 proof rejected: {ex}\n")


if __name__=="__main__":
    raise SystemExit(main())
