#!/usr/bin/env python3
"""Audit normalized, action-only DOS2 key masks, never original-vs-remake parity.

CSV columns phase,expected_mask,observed_mask,stable. Only Ctrl/Alt/Space
mask bits are permitted. Stable-window classification must be supplied by
an independently justified observation; host polling != emulated DOS ticks.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from typing import TextIO

MASKS = frozenset((0,0x80,0x100,0x180,0x200,0x280,0x300,0x380))
FIELDS = {"phase","expected_mask","observed_mask","stable"}

def parse_mask(s: str) -> int:
    try:
        n=int(s.strip(),0)
    except (ValueError,AttributeError) as e:
        raise ValueError(f"invalid mask {s!r}") from e
    if n not in MASKS:
        raise ValueError(f"{n:#06x} is not a Ctrl/Alt/Space-only mask")
    return n

def parse_stable(s: str) -> bool:
    s=s.strip().lower()
    if s in ("true","yes","1"):return True
    if s in ("false","no","0"):return False
    raise ValueError(f"invalid stable flag {s!r}")

def read_rows(f: TextIO) -> list[tuple[str,int,int,bool]]:
    reader=csv.DictReader(f)
    if not reader.fieldnames or len(reader.fieldnames)!=4 or set(reader.fieldnames)!=FIELDS:
        raise ValueError("expected phase,expected_mask,observed_mask,stable")
    rows=[]
    for line,row in enumerate(reader,2):
        if None in row or any(row.get(key) is None for key in FIELDS):
            raise ValueError(f"line {line}: incorrect number of fields")
        phase=row["phase"].strip()
        if not phase:raise ValueError(f"line {line}: empty phase")
        try:
            rows.append((phase,parse_mask(row["expected_mask"]),
                parse_mask(row["observed_mask"]),parse_stable(row["stable"])))
        except ValueError as e:
            raise ValueError(f"line {line}: {e}") from e
    if not rows:raise ValueError("no samples")
    return rows

def audit(rows: list[tuple[str,int,int,bool]]) -> dict:
    if not rows:raise ValueError("no samples")
    seen={observed for _,_,observed,_ in rows}
    return {
        "kind":"normalized_original_action_masks_only",
        "samples":len(rows),
        "phases":len({p for p,_,_,_ in rows}),
        "matching_samples":sum(expected==observed for _,expected,observed,_ in rows),
        "stable_mismatches":sum(stable and expected!=observed for _,expected,observed,stable in rows),
        "transition_mismatches":sum(not stable and expected!=observed for _,expected,observed,stable in rows),
        "observed_masks":[f"0x{m:04X}" for m in sorted(seen)],
        "all_eight_masks_observed":seen==MASKS,
        "original_vs_remake_parity":False,
        "tick_atomic":False,
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--out",type=Path)
    p.add_argument("--strict-stable",action="store_true")
    args=p.parse_args()
    try:
        with args.csv.open("r",newline="",encoding="utf-8") as f:
            result=audit(read_rows(f))
    except (OSError,ValueError) as e:
        p.error(str(e))
    output=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return int(args.strict_stable and result["stable_mismatches"]>0)

if __name__=="__main__":raise SystemExit(main())
