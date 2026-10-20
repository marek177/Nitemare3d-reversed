#!/usr/bin/env python3
"""Fail-closed stage alignment for ONE SHA-pinned original DOS2 E1M1 capture.

At image 267A the original wall loop reads the span phase high word BEFORE
image 2684 adds the 16.16 slope in memory. The archived mid-wall DS contains
the post-add phase; a replay consuming a post-span/pre-draw DS needs prior phase.
Do not treat this as a universal scene/savegame correction or a pixel-parity
claim. Original private DOS2 game bytes are neither embedded nor published.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct

EXPECTED_DS="1878c03fbd7f40d06dd87691e608d6143c16de0dcb347894d0e0bd6c2a49d98e"
EXPECTED_EXE="552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301"
SPAN=0x4d6e

def digest(raw:bytes)->str:
    return sha256(raw).hexdigest()

def rewind_one_phase(post_advance:int, step:int)->int:
    if not 0<=post_advance<=0xffffffff or not -(1<<31)<=step<(1<<31):
        raise ValueError("32-bit phase/step out of range")
    return (post_advance-step)&0xffffffff

def normalize(original_ds:bytes, original_exe:bytes)->tuple[bytes,dict]:
    if len(original_ds)!=65536 or digest(original_ds)!=EXPECTED_DS:
        raise ValueError("Not the pinned original E1M1 mid-wall capture")
    if len(original_exe)!=116606 or digest(original_exe)!=EXPECTED_EXE:
        raise ValueError("Not the pinned original unpacked DOS2 v2.0 EXE")
    code=original_exe[0x200:]
    if code[0x267a:0x267d]!=bytes.fromhex("8b 47 10") or (
        code[0x2684:0x2688]!=bytes.fromhex("66 01 47 0e")):
        raise ValueError("Original pre-load/post-add instruction order differs")
    if struct.unpack_from("<H",original_ds,0x4d64)[0]!=9 or (
        struct.unpack_from("<H",original_ds,SPAN)[0]!=0x89b8) or (
        struct.unpack_from("<H",original_ds,SPAN+2)[0]!=8):
        raise ValueError("Unexpected span owner/count/start")
    after=struct.unpack_from("<I",original_ds,SPAN+14)[0]
    step=struct.unpack_from("<i",original_ds,SPAN+10)[0]
    before=rewind_one_phase(after,step)
    corrected=bytearray(original_ds)
    struct.pack_into("<I",corrected,SPAN+14,before)
    return bytes(corrected),{
      "stage":"ORIGINAL_MID_WALL_ONE_SPAN_PHASE_NORMALIZATION",
      "original_ds_sha256":digest(original_ds),
      "normalized_ds_sha256":digest(corrected),
      "source_code_read_before_write":"0x267A",
      "source_code_add_step_writer":"0x2684",
      "original_span_owner":"0x89B8",
      "captured_phase_after_advance":f"0x{after:08X}",
      "signed_step":step,
      "restored_phase_before_advance":f"0x{before:08X}",
      "before_high_word":before>>16,
      "after_high_word":after>>16,
      "mutated_only":"DWORD DS:4D7C..4D7F",
      "whole_frame_pixel_parity_proven":False,
      "warning":"For one source-hash-pinned original CPU capture only; not a new runtime emulator session."
    }

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ds",required=True,type=Path)
    parser.add_argument("--exe",required=True,type=Path)
    parser.add_argument("--out-ds",required=True,type=Path)
    parser.add_argument("--out-report",required=True,type=Path)
    a=parser.parse_args()
    try:
        if a.out_ds.exists() or a.out_report.exists():
            raise ValueError("Output already exists")
        result,report=normalize(a.ds.read_bytes(),a.exe.read_bytes())
        a.out_ds.parent.mkdir(parents=True,exist_ok=True)
        a.out_report.parent.mkdir(parents=True,exist_ok=True)
        a.out_ds.write_bytes(result)
        a.out_report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0
    except (ValueError,OSError,struct.error) as exc:
        parser.exit(2,f"NOT_VERIFIED: {exc}\n")

if __name__=="__main__":
    raise SystemExit(main())
