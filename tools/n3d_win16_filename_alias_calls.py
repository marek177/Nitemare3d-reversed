#!/usr/bin/env python3
"""Original Ghidra Win16 v1.10 filename-builder caller provenance.

Pin the concrete save/config suffix argument on EVERY known direct CALL
to FUN_1010_5260, including the three near-pointer wrapper functions.
The dynamically changeable string is the PREFIX in DS:46BE, not the
filename suffix at the 12 direct user-facing callsites.

The prefix can be populated by the original -p command-line branch via
FUN_1008_6B06 and FUN_1008_6442 / sprintf-like formatter. This tool
does NOT invent a maximum Win3.x lpCmdLine or printf output length.
"""
from __future__ import annotations

from collections import Counter
import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_LEDGER=(ROOT/"other/n3d/builds_12/static_byte_evidence"
                /"N3D_Win110_filename_alias_callers_20261020.csv")
PREFIX_START=0x46BE
OUTPUT_START=0x36BE
TIMER_FLAG=0x46B2
TIMER_OUTPUT_OFFSET=TIMER_FLAG-OUTPUT_START
LITERAL_SUFFIXES={
    "DS:101E":("config.sav",10),
    "DS:1E50":("user.sav",8),
}
EXPECTED_DIRECT_5260={
    "3:52F5","3:5358"
}
EXPECTED_WRAPPERS={
    "3:5388":{"4:2245","4:22BB","4:2321","4:2409","4:2C96"},
    "3:5466":{"4:2CAA","4:2D8F"},
    "3:574C":{"4:243B","4:2945","4:2CC9"},
}
WRAPPER_5260_CALL={
    "3:5388":"3:5397",
    "3:5466":"3:548C",
    "3:574C":"3:5759",
}
COMMAND_LINE_PREFIX_PATH={
    "option_character":"-p",
    "option_selector_case":"3:120C",
    "DGROUP_prefix_output_pointer":"DS:46BE",
    "tokenizer_call":"3:1218",
    "tokenizer_function":"2:6B06",
    "format_call":"3:1221",
    "format_function":"2:6442",
    "internal_formatter":"2:4504",
    "format_literal":"DS:0D8C",
    "format_specifier":"%s",
    "one_shot_zero_writer":"3:0ED9",
}


def load_ledger(path:Path=DEFAULT_LEDGER)->list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def clock_overwrite_possible_with_suffix(prefix_characters:int,
                                         suffix_characters:int)->bool:
    """Address overlap condition; not a claim of a reachable Win3.x input."""
    if prefix_characters<0 or suffix_characters<0:
        raise ValueError("negative length invalid")
    final_nul=prefix_characters+suffix_characters
    if OUTPUT_START+final_nul>=0x10000:
        raise ValueError("DGROUP wrap requires separate byte-exact model")
    return final_nul>=TIMER_OUTPUT_OFFSET


def verify(records:list[dict[str,str]])->dict[str,Any]:
    if len(records)!=12:
        raise ValueError("Original Ghidra direct caller count expected 12")
    seen=set()
    class_counts=Counter()
    all_wrapper_sites=set()
    for row in records:
        site=row["upstream_call_site"]
        if site in seen:
            raise ValueError("Duplicate original Ghidra caller site "+site)
        seen.add(site)
        literal=row["literal_DGROUP_address"]
        if literal not in LITERAL_SUFFIXES:
            raise ValueError("Unproven dynamic filename argument in direct list "+site)
        expected_label,n=LITERAL_SUFFIXES[literal]
        if (row["literal_file_name"]!=expected_label
            or int(row["suffix_characters"])!=n):
            raise ValueError("Filename suffix literal length or address mismatch "+site)
        if row["source_grade"]!="ARCHIVED_GHIDRA_ORIGINAL_NE3_NE4_DIRECT_CALLS":
            raise ValueError("Original source grade changed "+site)
        wrapper=row["wrapper_entry"]
        builder_call=row["call_into_5260_site"]
        classification=row["evidence_path"]
        if classification=="DIRECT_5260_CALL":
            if site not in EXPECTED_DIRECT_5260 or builder_call!=site:
                raise ValueError("Unexpected direct filename-builder caller "+site)
            if literal!="DS:101E":
                raise ValueError("Direct filename-builder expected config.sav")
        elif classification in ("VIA_5388","VIA_5466","VIA_574C"):
            if wrapper not in EXPECTED_WRAPPERS:
                raise ValueError("Unknown second-level wrapper "+site)
            if builder_call!=WRAPPER_5260_CALL[wrapper]:
                raise ValueError("Wrong wrapper-to-builder callsite "+site)
            if site not in EXPECTED_WRAPPERS[wrapper]:
                raise ValueError("Unexpected upstream save wrapper call "+site)
            if literal!="DS:1E50":
                raise ValueError("Save wrapper suffix must be user.sav "+site)
            all_wrapper_sites.add(site)
        else:
            raise ValueError("Unknown call-path type "+site)
        class_counts[classification]+=1

    if seen!={*EXPECTED_DIRECT_5260,*all_wrapper_sites}:
        raise ValueError("Unexpected set of original callers")
    if all_wrapper_sites!=set().union(*EXPECTED_WRAPPERS.values()):
        raise ValueError("All 10 expected save wrapper callsites are required")
    if class_counts!={
        "DIRECT_5260_CALL":2,"VIA_5388":5,"VIA_5466":2,"VIA_574C":3
    }:
        raise ValueError("Build-time Win16 direct caller fanout changed")

    return {
        "build":"Windows 1.10, archived original Ghidra",
        "complete_directly_named_FUN_1010_5260_callers":5,
        "direct_builder_calls_using_config_sav":2,
        "immediate_save_builder_wrappers_using_user_sav":3,
        "save_wrapper_upstream_direct_calls":10,
        "all_direct_suffix_call_paths":12,
        "literal_suffix_name_counts":{"config.sav":2,"user.sav":10},
        "save_wrapper_upstream_by_entry":{
            wrapper:sorted(sites)
            for wrapper,sites in EXPECTED_WRAPPERS.items()
        },
        "filename_literals":LITERAL_SUFFIXES,
        "output_staging_start":f"DS:{OUTPUT_START:04X}",
        "mutable_prefix_source":f"DS:{PREFIX_START:04X}",
        "timer_flag_at":f"DS:{TIMER_FLAG:04X}",
        "timer_flag_distance_from_output":TIMER_OUTPUT_OFFSET,
        "prefix_chars_required_for_user_sav":TIMER_OUTPUT_OFFSET-8,
        "prefix_chars_required_for_config_sav":TIMER_OUTPUT_OFFSET-10,
        "command_line_prefix_flow":COMMAND_LINE_PREFIX_PATH,
        "user_sav_is_literal_in_all_known_direct_paths":True,
        "config_sav_is_literal_in_all_known_direct_paths":True,
        "prefix_maximum_characters_statically_closed":False,
        "formatter_writes_with_explicit_capacity_argument":False,
        "win16_command_line_maximum_verified":False,
        "indirect_callers_of_builder_ruled_out":False,
        "alias_writer_graph_closed":False,
        "cautions":[
            "This is a direct Ghidra caller-graph closure, not full dynamic FAR closure.",
            "The '-p' path stores a parsed argv token via a custom formatter.",
            "The custom formatter is not yet instruction-proved bounded on destination.",
            "A long prefix can make 5260 REP MOVS overlap DS:46B2 at >=4084 characters total.",
            "No runtime-overflow scenario or actual oversized Win16 command line was observed.",
        ],
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=DEFAULT_LEDGER)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        result=verify(load_ledger(args.input))
        encoded=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if args.output:
            args.output.write_text(encoded,encoding="utf-8")
            print("12 original direct save/config paths verified; -p prefix bound OPEN")
        else:
            print(encoded)
        return 0
    except (ValueError,OSError,KeyError) as exc:
        parser.exit(2,f"Original filename proof rejected: {exc}\n")


if __name__=="__main__":
    raise SystemExit(main())
