#!/usr/bin/env python3
"""Nitemare 3D DOS2 CEDC perspective-U: independently verify original CPU ledger.

The SHA-gated 1,808-row CSV is derived from authentic archived original
N3DTRC01 CPU prestates by the offline extractor distributed in the private
v0.79 artifact. No original EXE or commercial game data is shipped here.
Passing verifies CEDC arithmetic given ORIGINAL captured operands, NOT
that a remake generated the same world geometry or a pixel-perfect frame.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

CEDC_SHA = "1db25ccff303dafd2b87d168629af21c10d1dec17e7f6eb5031eb5d4edcbc220"
EDGE_SHA = "724151a85a119c40b3231b7d597aceb1958388c8136453cfd1ac7ea0b4b757ac"

EXPECTED = {
    "selector1_horizontal":1030,
    "selector1_vertical":474,
    "selector0_horizontal":187,
    "selector0_vertical":117,
}

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def s16(v: int) -> int:
    v &= 0xffff
    return v if v < 0x8000 else v - 0x10000

def s32(v: int) -> int:
    v &= 0xffffffff
    return v if v < 0x80000000 else v - 0x100000000

def idiv(a: int,b: int) -> int:
    if b == 0:
        raise ValueError("DOS2 signed IDIV divisor zero")
    x = abs(a)//abs(b)
    q = -x if (a<0)!=(b<0) else x
    if q < -0x80000000 or q > 0x7fffffff:
        raise ValueError("Original 32-bit signed IDIV quotient overflow")
    return q

def perspective(row: dict) -> dict:
    branch=row["branch_fourway"]
    if branch not in EXPECTED:
        raise ValueError("Unknown original DOS CEDC orientation/selector branch")
    x=int(row["x"]);center=int(row["center_x"])
    span=int(row["span"]);prod=int(row["product32"])
    inv=int(row["inverse_scale"]);vertical=int(row["vertical_numerator"])
    div=int(row["trig_divisor"])
    if not 0<span<=65535:raise ValueError("Invalid span denominator")
    use_screen=branch in ("selector1_horizontal","selector0_vertical")
    first=s32(s16(x-center)*inv) if use_screen else vertical
    partial=idiv(first,span)
    if branch=="selector1_horizontal":
        combined=s32(partial+prod)
    elif branch=="selector0_vertical":
        combined=s32(prod-partial)
    else:
        combined=s32(partial-prod)
    quotient=idiv(combined,div)
    ax=quotient&0xffff
    local=int(row["caller_local16"])&65535
    raw=(ax+local)&65535
    if row["caller_negates_u"]=="True":
        raw=(-raw)&65535
    elif row["caller_negates_u"]!="False":
        raise ValueError("Original caller NEG flag invalid")
    return {"partial":partial,"combined":combined,"quotient":quotient,
            "ax":ax,"raw_u_before_22ca":raw}

def load_corpus(path: Path, expected_sha: str):
    raw=path.read_bytes()
    if digest(raw)!=expected_sha:
        raise ValueError("Original CPU CSV failed strict SHA-256 provenance gate")
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def verify(cedc: list[dict],edge: list[dict]|None = None):
    if len(cedc)!=1808:raise ValueError("Missing original CEDC CPU rows")
    counts=Counter();neg=0;direct_product=0;direct_local=0
    for row in cedc:
        got=perspective(row)
        if (got["partial"]!=int(row["partial_original_result"]) or
            got["combined"]!=int(row["final_original_num"]) or
            got["quotient"]!=int(row["cedc_quotient_original"]) or
            got["ax"]!=int(row["returned_ax"]) or
            got["raw_u_before_22ca"]!=int(row["caller_pre_edge_u"])):
            raise ValueError(f"Original CEDC mismatch at event {row['first_event']}")
        if row["cached_2643_product32"]:
            direct_product+=1
            if int(row["cached_2643_product32"])!=int(row["product32"]):
                raise ValueError("Original independent IMUL input differs")
        if row["cached_2603_2620_local16"]:
            direct_local+=1
            if int(row["cached_2603_2620_local16"])!=int(row["caller_local16"]):
                raise ValueError("Original independent world local differs")
        neg+=(row["caller_negates_u"]=="True")
        counts[row["branch_fourway"]]+=1
    if dict(counts)!=EXPECTED or direct_product!=1804 or direct_local!=1804 or neg!=1172:
        raise ValueError("Original CEDC/25DC branch/independent-input census changed")
    result={
        "evidence":"ORIGINAL_CPU_OPERAND_ARITHMETIC_NOT_REMAKE_FRAME_PARITY",
        "original_cedc_calls":1808,
        "cedc_return_matches":1808,
        "pre22ca_unadjusted_u_matches":1808,
        "independent_25dc_parent_imul_matches":direct_product,
        "independent_25dc_parent_local_matches":direct_local,
        "original_caller_negation_count":neg,
        "four_branch_counts":dict(counts),
        "original_vs_port_framebuffer":"NOT_TESTED",
    }
    if edge is not None:
        if len(edge)!=1520:raise ValueError("Expected 1,520 original 22CA rows")
        groups=[];curr=[]
        for row in cedc:
            if curr and (row["session"]!=curr[-1]["session"] or
                         int(row["x"])<=int(curr[-1]["x"])):
                groups.append(curr);curr=[]
            curr.append(row)
        if curr:groups.append(curr)
        full=[g for g in groups if len(g)==304 and
              [int(r["x"]) for r in g]==list(range(8,312))]
        if len(full)!=5:raise ValueError("Exactly five full CEDC frames required")
        corrected=0
        for f in range(5):
            for before,after in zip(full[f],edge[f*304:(f+1)*304]):
                if (before["session"]!="".join(after["session"].split("session-",1)) or
                    int(before["x"])!=int(after["screen_x"]) or
                    int(before["orientation"])!=int(after["orientation"]) or
                    perspective(before)["raw_u_before_22ca"] !=
                        (int(after["unadjusted_u"])&0xffff)):
                    raise ValueError(f"Original original-CEDC-to-22CA bridge mismatched at frame {f}")
                corrected+=int(after["observed_u"])!=(
                    int(after["unadjusted_u"])&127)
        if corrected!=23:raise ValueError("Original 22CA correction count changed")
        result["five_full_original_U_frames_linked"]=5
        result["original_pre22ca_to_22ca_columns_linked"]=1520
        result["original_post_22ca_edge_corrections"]=corrected
    return result

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cedc-csv",type=Path,required=True)
    parser.add_argument("--edge-csv",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        cedc=load_corpus(args.cedc_csv,CEDC_SHA)
        edge=load_corpus(args.edge_csv,EDGE_SHA) if args.edge_csv else None
        report=verify(cedc,edge)
    except (OSError,ValueError) as e:
        parser.exit(2,"FAIL, NO PARITY CLAIM: "+str(e)+"\n")
    text=json.dumps(report,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
