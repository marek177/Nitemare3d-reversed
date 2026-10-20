#!/usr/bin/env python3
"""Bounded Win16 v1.10 original string-buffer {ptr,used,capacity} audit.

Source: archived original NITE3W Win16 v1.10 Ghidra ASM, NE1 / 1000
0:0CDC..0D8B, NE2 / 1008 5AB0..5B0A. All values below are
instruction-local 16-bit arithmetic or explicit callgraph witnesses.

This is NOT an emulator of a Windows 3.11 LocalAlloc heap, a fresh
whole-file original SHA check, a complete alias writer/callback census,
an observed OOM scenario, or a runtime parity claim.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

# These are *original DGROUP near offsets*, not host C++ pointers.
EMPTY_SENTINEL = 0x0584
CLOCK_FLAG_DS = 0x46B2
ONESHOT_LATCH_DS = 0x00A2
COUNT_MAX = 0xFFFF

# Archived original Ghidra instruction witness table. Verification against
# the original 230400-byte EXE is NOT performed by synthetic regression.
INSTRUCTION_WITNESSES = {
    "1000:0CE4": ("89 47 04", "MOV [BX+4],AX ; capacity=0"),
    "1000:0CE7": ("89 47 02", "MOV [BX+2],AX ; used=0"),
    "1000:0CEA": ("C7 07 84 05", "MOV WORD [BX],0584 ; ptr=empty sentinel"),
    "1000:0CF8": ("81 F9 84 05", "CMP CX,0584 ; skip sentinel free"),
    "1000:0D43": ("8B 7E 08", "MOV DI,[BP+8] ; requested data bytes"),
    "1000:0D46": ("0B FF", "OR DI,DI ; empty guard"),
    "1000:0D48": ("75 0A", "JNZ 0D54 ; nonzero allocation"),
    "1000:0D4D": ("9A DC 0C 00", "CALL FAR 1000:0CDC ; empty"),
    "1000:0D57": ("8D 45 01", "LEA AX,[DI+1] ; request n+1 modulo 65536"),
    "1000:0D5B": ("9A E0 5F 08", "CALL FAR 1008:5FE0 ; allocated pointer"),
    "1000:0D61": ("8B D8", "MOV BX,AX ; allocation return pointer"),
    "1000:0D63": ("89 04", "MOV [SI],AX ; store returned pointer"),
    "1000:0D65": ("C6 01 00", "MOV BYTE [BX+DI],0 ; terminator BEFORE NULL check"),
    "1000:0D68": ("89 7C 02", "MOV [SI+2],DI ; used=n"),
    "1000:0D6B": ("89 7C 04", "MOV [SI+4],DI ; cap=n"),
    "1000:0D7D": ("9A F2 0C 00", "CALL FAR 1000:0CF2 ; conditional free"),
    "1000:0D84": ("9A DC 0C 00", "CALL FAR 1000:0CDC ; reset"),
    "1008:5AB8": ("83 7E 06 00", "CMP requested bytes,0"),
    "1008:5ABE": ("C7 46 06 01 00", "replace zero request with one"),
    "1008:5AD3": ("9A 08 00 00", "CALL FAR KERNEL.LOCALALLOC (relocated bytes)"),
    "1008:5AE4": ("83 7E FC 00", "CMP returned handle,0"),
    "1008:5AF1": ("74 0E", "if no callback, allow zero return"),
    "1008:5AF6": ("FF 1E 4A 09", "CALL FAR [DS:094A], OOM callback if configured"),
    "1008:5AFF": ("75 C2", "retry LocalAlloc if callback requests"),
    "1008:5B01": ("8B 46 FC", "MOV AX,last LocalAlloc return"),
}


@dataclass(frozen=True)
class Trio:
    ptr: int
    used: int
    capacity: int

    def as_dict(self) -> dict[str, int]:
        return {"ptr":self.ptr,"used":self.used,"capacity":self.capacity}


@dataclass(frozen=True)
class AllocPath:
    requested_used: int
    localalloc_passed_bytes: int | None
    localalloc_wrapper_effective_bytes: int | None
    resulting_trio: Trio
    original_terminator_write_DS_offset: int | None
    heap_pointer_was_zero: bool | None
    ptr_null_guard_before_terminator: bool
    old_ptr_freed: bool
    result_is_valid_normal_owned_block_proven: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_used":self.requested_used,
            "localalloc_passed_bytes":self.localalloc_passed_bytes,
            "localalloc_wrapper_effective_bytes":self.localalloc_wrapper_effective_bytes,
            "resulting_trio":self.resulting_trio.as_dict(),
            "original_terminator_write_DS_offset":(
                self.original_terminator_write_DS_offset),
            "heap_pointer_was_zero":self.heap_pointer_was_zero,
            "ptr_null_guard_before_terminator":self.ptr_null_guard_before_terminator,
            "old_ptr_freed":self.old_ptr_freed,
            "result_is_valid_normal_owned_block_proven":(
                self.result_is_valid_normal_owned_block_proven),
        }


def check_word(name:str,value:int)->None:
    if not isinstance(value,int) or not 0<=value<=COUNT_MAX:
        raise ValueError(name+" must be an unsigned 16-bit word")


def init_trio()->Trio:
    """1000:0CDC: static shared zero byte, no allocation/free."""
    return Trio(EMPTY_SENTINEL,0,0)


def free_is_attempted(ptr:int)->bool:
    """1000:0CF2: free every non-sentinel pointer, via 1008:5FD0."""
    check_word("ptr",ptr)
    return ptr!=EMPTY_SENTINEL


def teardown_trio(old:Trio)->tuple[Trio,bool]:
    """1000:0D74 calls 0CF2(old.ptr), then 0CDC."""
    for name,val in old.as_dict().items():
        check_word(name,val)
    return init_trio(),free_is_attempted(old.ptr)


def allocate_trio(requested_used:int,heap_result_ptr:int | None,
                  previous_state:Trio | None = None)->AllocPath:
    """Original 0D3E transition, assuming a returned LocalAlloc result.

    For requested_used=0 the original skips allocation and overwrites
    the trio with the empty sentinel (WITHOUT calling free).

    For n>0 original near request (n+1)&0xffff passes through
    1008:5AB0, which changes zero allocation requests into one byte.
    Original 0D65 stores byte 0 to DS:[BX+DI] irrespective of BX=0
    (the returned LocalAlloc pointer). This is only an *address plan*;
    no writes to memory are actually performed here.
    """
    check_word("requested_used",requested_used)
    if previous_state is not None:
        for name,val in previous_state.as_dict().items():
            check_word("previous_"+name,val)
    if requested_used==0:
        return AllocPath(
            0,None,None,init_trio(),None,None,False,False,
            previous_state is None or previous_state.ptr==EMPTY_SENTINEL)
    if heap_result_ptr is None:
        raise ValueError("nonzero requested_used requires modeled heap result")
    check_word("heap_result_ptr",heap_result_ptr)
    passed=(requested_used+1)&COUNT_MAX
    effective=passed if passed else 1
    terminator=(heap_result_ptr+requested_used)&COUNT_MAX
    return AllocPath(
        requested_used,passed,effective,
        Trio(heap_result_ptr,requested_used,requested_used),
        terminator,heap_result_ptr==0,False,False,False)


def failing_alloc_global_zero_writer(length:int,target:int)->bool:
    """Could the terminal NUL write DS:[length] hit target IF AX=0?

    This is a conditional instruction/offset proof, *not* proof that
    OOM occurs, the OOM callback returns, the caller is reachable with
    this length, or subsequent code survives the bad pointer.
    """
    check_word("length",length)
    check_word("target",target)
    return length!=0 and length==target


def audit()->dict[str, Any]:
    initial=init_trio()
    clock_failure=allocate_trio(CLOCK_FLAG_DS,0)
    latch_failure=allocate_trio(ONESHOT_LATCH_DS,0)
    clock_good=allocate_trio(CLOCK_FLAG_DS,0x2000)
    full=allocate_trio(0xFFFF,0)
    return {
        "original":"NITE3W Windows 1.10 archived static Ghidra",
        "instruction_witnesses":len(INSTRUCTION_WITNESSES),
        "original_empty_pointer":"DS:0584",
        "original_empty_sentinel_byte":"00",
        "fields":{"ptr":"+0","used":"+2","capacity":"+4"},
        "initial_state":initial.as_dict(),
        "free_skips_shared_empty_sentinel":not free_is_attempted(EMPTY_SENTINEL),
        "free_attempts_heap_pointer_if_non_sentinel":free_is_attempted(0x2000),
        "alloc_zero_resets_to_empty_without_freeing_prior_ptr":True,
        "alloc_nonzero_sets_used_and_capacity_both_to_n":True,
        "allocation_request_word_expression":"(requested_used+1)&0xFFFF",
        "zero_request_replaced_with_one_by_1008_5AB0":True,
        "nonzero_allocation_result_null_checked_before_terminator":False,
        "original_terminator_opcode":"1000:0D65 C6 01 00 => DS:[BX+DI]=0",
        "clock_on_failed_nonzero_localalloc":clock_failure.as_dict(),
        "latch_on_failed_nonzero_localalloc":latch_failure.as_dict(),
        "nonzero_heap_pointer_example":clock_good.as_dict(),
        "max_word_requested_alloc_example":full.as_dict(),
        "failure_to_global_flag_write_possible_if_sized":{
            "DS:00A2":failing_alloc_global_zero_writer(ONESHOT_LATCH_DS,ONESHOT_LATCH_DS),
            "DS:46B2":failing_alloc_global_zero_writer(CLOCK_FLAG_DS,CLOCK_FLAG_DS),
        },
        "new_conditional_scalar_alias_writer":"1000:0D65",
        "actual_allocator_failure_or_alias_reachability_proved":False,
        "oom_callback_possible":{"far_pointer":"DS:094A/094C",
                                 "indirect_far_call":"1008:5AF6",
                                 "retry_if_callback_nonzero":"1008:5AFF"},
        "limitations":[
            "No new executable rehash; instruction table sourced from archived original Ghidra",
            "Conditional OOM LocalAlloc return 0 is modeled, not observed",
            "A data copy after failed allocation can introduce additional pointer-derived writes",
            "Array indices and string lengths reaching 00A2/46B2 are not fully proven",
            "Null result can be returned by the wrapper when no OOM handler or callback declines",
            "Normal valid LocalAlloc heap pointers must be proved nonaliasing by separate OS contract",
            "All other computed memory writes and dynamic FAR callers remain OPEN",
        ],
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=audit()
    rendered=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered,encoding="utf-8")
        print("Win16 trio: original empty sentinel and conditional OOM DS:n scalar alias documented")
        print("Report:",args.output)
    else:
        print(rendered)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
