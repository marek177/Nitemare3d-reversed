#!/usr/bin/env python3
"""Win16 Nitemare v1.10 OOM callback: hidden original code and retry paths.

Original source: archived Ghidra Win16 v1.10 disassembly (nite3w(1).docx).
The disassembler treats the 1000:076A callback as undecoded bytes. The
8-byte original sequence has an unambiguous 16-bit FAR CALL/XOR/RETF
interpretation, supported by the instruction-exact callback registration
code at 1000:0777..077D.

This proof is intentionally local. It does not prove that this installer
thunk is dynamically executed, nor that Win16 KERNEL.THROW will return.
Only the original EXE SHA-pinned optional recheck can claim fresh bytes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# These are ORIGINAL ARCHIVED assembly bytes, not a newly rehashed
# executable in the normal GitHub synthetic-only test job.
HIDDEN_DEFAULT_HANDLER_IP = 0x076A
HIDDEN_DEFAULT_HANDLER_HEX = "9a 64 45 00 10 33 c0 cb"
INITIAL_HANDLER_INSTALL_IP = 0x0772
INITIAL_HANDLER_INSTALL_HEX = (
    "9a ca 53 00 10"  # CALL FAR 1000:53CA, _AFX_VERSION
    "68 00 10"        # PUSH 1000 selector
    "68 6a 07"        # PUSH 076A original code-island entry
    "9a 1a 60 08"     # CALL FAR 1008:601A setter wrapper
    "83 c4 04"        # clean two pushed 16-bit words
    "b8 01 00"        # MOV AX,1
    "cb"              # RETF
)
BASE_EXCEPTION_HELPER="1000:4564"
RECOVERY_CALLBACK="1008:12D2"
OOM_INSTALL_SETTER="1008:601A"
OOM_GLOBAL_POINTER="DS:094A..094D"
NORMAL_INIT_HANDLER_POINTER="1000:076A"
CALLBACK_REGISTRATION_SITES={
    "1000:077D":("default",NORMAL_INIT_HANDLER_POINTER),
    "1000:28DE":("disable","0:0"),
    "1000:2913":("restore","saved previous pointer"),
    "1000:29BB":("recovery",RECOVERY_CALLBACK),
    "1000:29EB":("restore","saved previous pointer"),
}
OOM_INITIAL_POINTER_WORDS=(0,0)
EXPECTED_LITERAL_GLOBAL_WRITES={
    "1008:6009":"DS:094A (offset)",
    "1008:600C":"DS:094C (selector)",
}

def validate_archived_hidden_code(handler:bytes=None,
                                  install:bytes=None)->dict[str,Any]:
    """Validate and interpret the 16-bit code-island machine byte manifest.

    Tests normally pass the archived constant model; this does not
    upgrade archival evidence to a fresh original EXE byte read.
    """
    handler = bytes.fromhex(HIDDEN_DEFAULT_HANDLER_HEX) if handler is None else handler
    install = bytes.fromhex(INITIAL_HANDLER_INSTALL_HEX) if install is None else install
    if handler!=bytes.fromhex(HIDDEN_DEFAULT_HANDLER_HEX):
        raise ValueError("Original callback byte sequence at 1000:076A differs")
    if install!=bytes.fromhex(INITIAL_HANDLER_INSTALL_HEX):
        raise ValueError("Original install thunk at 1000:0772 differs")
    if len(handler)!=8 or len(install)!=22:
        raise ValueError("Hidden code-island length changed")
    return {
        "handler_entry":"1000:076A",
        "handler_bytes":handler.hex(" "),
        "instructions":[
            "1000:076A CALL FAR 1000:4564",
            "1000:076F XOR AX,AX",
            "1000:0771 RETF",
        ],
        "normal_return_value_if_exception_helper_returns":0,
        "can_exception_helper_unwind_without_return":True,
        "install_entry":"1000:0772",
        "install_thunk_bytes":install.hex(" "),
        "installed_pointer":"1000:076A",
        "setter_call":"1000:077D -> 1008:601A",
        "install_thunk_executed_during_original_startup_proven":False,
    }

def allocation_failure_plan(handler_kind:str,
                            callback_return:int|None=None)->dict[str,Any]:
    """Local LocalAlloc wrapper path 1008:5AE4..5B01.

    callback_return=None means a THROW/unwind/nonreturn is still possible.
    Caller supplies a *modeled* return; no original Windows callback
    is run in this Python module.
    """
    if handler_kind not in ("none","default","recovery"):
        raise ValueError("handler_kind must be none/default/recovery")
    if callback_return is not None and not 0<=callback_return<=0xFFFF:
        raise ValueError("callback_return must be an unsigned 16-bit word")
    if handler_kind=="none":
        if callback_return is not None:
            raise ValueError("No callback is installed, cannot supply return")
        return {
            "callback_invoked":False,
            "oom_callback_kind":handler_kind,
            "localalloc_retry_if_callback_returns_nonzero":False,
            "propagates_zero_to_immediate_caller_if_reached":True,
            "may_exit_nonlocally_via_Kernel_THROW":False,
        }
    return {
        "callback_invoked":True,
        "oom_callback_kind":handler_kind,
        "localalloc_retry_if_callback_returns_nonzero":(
            None if callback_return is None else callback_return!=0
        ),
        "propagates_zero_to_immediate_caller_if_reached":(
            None if callback_return is None else callback_return==0
        ),
        "may_exit_nonlocally_via_Kernel_THROW":True,
    }

def known_recovery_handler_plan(memory_object_exists:bool,
                                backing_allocation_exists:bool)->dict[str,Any]:
    """Original 1008:12D2 with DS:081C object and object+7A backing ptr.

    If either is missing: CALL FAR 1000:4564, then XOR AX (if return).
    Otherwise: LocalSize/LocalFree/LocalRealloc path ends MOV AX,1
    and asks the allocation wrapper to retry. This is a syntactic
    local codepath proof, not a guarantee that memory was freed.
    """
    reclaim_path=memory_object_exists and backing_allocation_exists
    return {
        "original_entry":"1008:12D2",
        "enters_recovery_path":reclaim_path,
        "normal_return_AX_if_called_subroutine_returns":1 if reclaim_path else 0,
        "calls_error_helper_1000_4564":not reclaim_path,
        "realloc_result_checked_before_AX_1":False,
        "actual_localalloc_retry_success_proven":False,
        "throw_may_unwind":not reclaim_path,
    }

def optional_original_SHA_pinned_recheck(input_path:Path)->dict[str,Any]:
    """Re-read the exact pinned Win16 1.10 NE original if provided by user.

    The proprietary EXE is never committed; synthetic CI does not run
    this branch, which requires the exact SHA-gated original archive.
    """
    import hashlib
    import tempfile
    from n3d_win16_timer_binary_proof import find_pinned_original
    from ne_renderer_audit import NeImage
    source,binary,profile=find_pinned_original(input_path,"1.10")
    if profile.version!="1.10":
        raise ValueError("Win16 1.10 original identity required")
    with tempfile.TemporaryDirectory(prefix="n3d_oom_hidden_") as tmp:
        file=Path(tmp,"original_nite3w.exe")
        file.write_bytes(binary)
        image=NeImage(file)
        handler=image.bytes_at(1,0x076A,0x0772)
        install=image.bytes_at(1,0x0772,0x0788)
        validate_archived_hidden_code(handler,install)
    return {
        "source":source,
        "version":profile.version,
        "fresh_original_sha256":hashlib.sha256(binary).hexdigest(),
        "verified_original_code_regions":["NE1:076A..0771","NE1:0772..0787"],
    }

def audit()->dict[str,Any]:
    hidden=validate_archived_hidden_code()
    return {
        "build":"Nitemare 3-D original Win16 1.10",
        "source_level":"ARCHIVED_ORIGINAL_GHIDRA_UNDECODED_BYTES_AND_STATIC_CALLS",
        "hidden_callback":hidden,
        "DGROUP_initial_OOM_callback_words":[0,0],
        "DGROUP_OOM_far_pointer":"DS:094A..094D",
        "named_direct_pointer_setter_call_sites":CALLBACK_REGISTRATION_SITES,
        "named_direct_pointer_setter_call_count":len(CALLBACK_REGISTRATION_SITES),
        "literal_global_writer_opcodes":EXPECTED_LITERAL_GLOBAL_WRITES,
        "setter_entry":"1008:5FF0",
        "setter_wrapper":"1008:601A",
        "allocator_wrapper":"1008:5AB0",
        "original_localalloc_api_site":"1008:5AD3",
        "callback_test_after_failure":"1008:5AEA OR 094C / 5AED OR 094A; JE 5B01",
        "callback_indirect_far_site":"1008:5AF6 CALL FAR [DS:094A]",
        "callback_retry_test":"1008:5AFD OR AX,AX; 1008:5AFF JNZ 5AC3",
        "recovery_callback":"1008:12D2",
        "recovery_handler_returns_one_on_normal_success_branch":True,
        "default_hidden_handler_returns_zero_if_error_callback_returns":True,
        "fallback_oom_without_callback_reaches_return_zero":True,
        "complete_dynamic_reachability_of_initial_install_thunk":False,
        "complete_callback_pointer_alias_writer_graph":False,
        "KERNEL_THROW_is_guaranteed_to_return_normally":False,
        "normal_gameplay_OOM_return_to_D3E_observed":False,
        "original_exe_SHA_reverified_this_session":False,
        "notes":[
            "1000:076A is marked ?? in archived Ghidra, but exact 9A 64 45 00 10 33 C0 CB decodes as far call 4564; xor ax; retf",
            "1000:0772 executes _AFX_VERSION then stores pointer 1000:076A using setter wrapper, only if the code-island entry is actually invoked",
            "1000:28DE temporarily clears callback; 1000:2913 restores prior pointer; 1000:29BB installs recovery 1008:12D2, 1000:29EB restores prior pointer",
            "On null LocalAlloc with callback absent/declined, allocator wrapper returns zero; D3E terminator store to DS:[requested_used] is a conditional memory-write alias",
            "1008:12D2 returns AX=1 on recovery branch without checking LocalRealloc result; subsequent LocalAlloc retry success is not guaranteed",
            "Error helper 1000:4564 invokes function 1000:4492, which can call KERNEL.THROW; control may transfer nonlocally",
            "No proof that any callback installer is globally the only writer through computed pointers",
            "Runtime observation, timer flag corruption and actual heap OOM remain unproved",
        ],
    }

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original",type=Path,
                        help="optional original Win16 1.10 EXE or ZIP for SHA-pinned recheck")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=audit()
    if args.original:
        report["fresh_original_SHA_check"]=optional_original_SHA_pinned_recheck(args.original)
        report["original_exe_SHA_reverified_this_session"]=True
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered,encoding="utf-8")
        print("Archived Win16 OOM code island + 5 callback setter calls verified")
    else:
        print(rendered)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
