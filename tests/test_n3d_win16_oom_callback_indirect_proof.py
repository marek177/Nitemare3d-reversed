#!/usr/bin/env python3
"""Synthetic regression of archived Ghidra Win16 hidden OOM callback bytes.

No original Windows game binary is executed. No original EXE SHA recheck
is performed by this synthetic-only test suite.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_oom_callback_indirect_proof import (
    HIDDEN_DEFAULT_HANDLER_HEX,
    INITIAL_HANDLER_INSTALL_IP,INSTALL_PREFIX_HEX,INSTALL_SUFFIX_HEX,
    UNKNOWN_INSTALL_BYTE_IP,CALLBACK_REGISTRATION_SITES,
    OOM_INITIAL_POINTER_WORDS,EXPECTED_LITERAL_GLOBAL_WRITES,
    validate_archived_hidden_code,allocation_failure_plan,
    known_recovery_handler_plan,audit
)
from n3d_win16_string_trio_lifecycle_audit import (
    allocate_trio,failing_alloc_global_zero_writer,
    ONESHOT_LATCH_DS,CLOCK_FLAG_DS
)


class Win16HiddenOOMCallback(unittest.TestCase):
    def test_original_eight_bytes_decode_indirect_callable_handler(self):
        decoded=validate_archived_hidden_code()
        self.assertEqual(len(bytes.fromhex(HIDDEN_DEFAULT_HANDLER_HEX)),8)
        self.assertEqual(decoded["handler_entry"],"1000:076A")
        self.assertEqual(decoded["instructions"],[
            "1000:076A CALL FAR 1000:4564",
            "1000:076F XOR AX,AX",
            "1000:0771 RETF",
        ])
        self.assertEqual(decoded["normal_return_value_if_exception_helper_returns"],0)
        self.assertTrue(decoded["can_exception_helper_unwind_without_return"])

    def test_indirect_registration_1000_0772_is_masked_not_guessed(self):
        decoded=validate_archived_hidden_code()
        self.assertEqual(INITIAL_HANDLER_INSTALL_IP,0x0772)
        self.assertEqual(UNKNOWN_INSTALL_BYTE_IP,0x0781)
        self.assertEqual(len(bytes.fromhex(INSTALL_PREFIX_HEX)),15)
        self.assertEqual(len(bytes.fromhex(INSTALL_SUFFIX_HEX)),7)
        self.assertEqual(decoded["install_thunk_unverified_original_byte_offset"],
                         "1000:0781")
        self.assertFalse(decoded["install_relocation_0781_was_recovered_from_archived_text"])
        self.assertFalse(decoded["install_thunk_executed_during_original_startup_proven"])
        self.assertEqual(decoded["setter_call"],"1000:077D -> 1008:601A")
        self.assertEqual(decoded["installed_pointer"],"1000:076A")

    def test_unknown_original_high_relocation_byte_is_not_invented(self):
        prefix=bytes.fromhex(INSTALL_PREFIX_HEX)
        suffix=bytes.fromhex(INSTALL_SUFFIX_HEX)
        for x in range(256):
            model=validate_archived_hidden_code(install=prefix+bytes((x,))+suffix)
            self.assertFalse(model["install_relocation_0781_was_recovered_from_archived_text"])
        with self.assertRaisesRegex(ValueError,"known install thunk"):
            validate_archived_hidden_code(install=b"\x90"+prefix[1:]+b"\x00"+suffix)
        with self.assertRaisesRegex(ValueError,"known install thunk"):
            validate_archived_hidden_code(install=prefix+b"\x00"+suffix[:-1]+b"\x90")

    def test_mutated_callback_bytes_or_length_rejected(self):
        h=bytearray(bytes.fromhex(HIDDEN_DEFAULT_HANDLER_HEX))
        h[5]=0x90
        with self.assertRaisesRegex(ValueError,"callback byte"):
            validate_archived_hidden_code(handler=bytes(h))
        with self.assertRaisesRegex(ValueError,"length"):
            validate_archived_hidden_code(handler=bytes.fromhex(HIDDEN_DEFAULT_HANDLER_HEX)[:-1])

    def test_original_dgroup_starts_without_callback_registered(self):
        report=audit()
        self.assertEqual(OOM_INITIAL_POINTER_WORDS,(0,0))
        self.assertEqual(report["DGROUP_initial_OOM_callback_words"],[0,0])
        self.assertEqual(report["DGROUP_OOM_far_pointer"],"DS:094A..094D")
        self.assertEqual(EXPECTED_LITERAL_GLOBAL_WRITES,{
            "1008:6009":"DS:094A (offset)",
            "1008:600C":"DS:094C (selector)",
        })
        self.assertFalse(report["complete_callback_pointer_alias_writer_graph"])

    def test_all_five_original_named_registration_call_sites(self):
        self.assertEqual(CALLBACK_REGISTRATION_SITES,{
            "1000:077D":("default","1000:076A"),
            "1000:28DE":("disable","0:0"),
            "1000:2913":("restore","saved previous pointer"),
            "1000:29BB":("recovery","1008:12D2"),
            "1000:29EB":("restore","saved previous pointer"),
        })
        self.assertEqual(audit()["named_direct_pointer_setter_call_count"],5)

    def test_failed_localalloc_without_callback_returns_zero(self):
        plan=allocation_failure_plan("none")
        self.assertFalse(plan["callback_invoked"])
        self.assertFalse(plan["localalloc_retry_if_callback_returns_nonzero"])
        self.assertTrue(plan["propagates_zero_to_immediate_caller_if_reached"])
        self.assertFalse(plan["may_exit_nonlocally_via_Kernel_THROW"])
        with self.assertRaisesRegex(ValueError,"cannot supply return"):
            allocation_failure_plan("none",0)

    def test_default_callback_returns_zero_only_if_exception_helper_returns(self):
        zero=allocation_failure_plan("default",0)
        self.assertTrue(zero["callback_invoked"])
        self.assertTrue(zero["propagates_zero_to_immediate_caller_if_reached"])
        self.assertFalse(zero["localalloc_retry_if_callback_returns_nonzero"])
        self.assertTrue(zero["may_exit_nonlocally_via_Kernel_THROW"])
        unknown=allocation_failure_plan("default")
        self.assertIsNone(unknown["localalloc_retry_if_callback_returns_nonzero"])
        self.assertIsNone(unknown["propagates_zero_to_immediate_caller_if_reached"])

    def test_recovery_handler_requests_retry_on_local_success_path(self):
        v=known_recovery_handler_plan(True,True)
        self.assertTrue(v["enters_recovery_path"])
        self.assertEqual(v["normal_return_AX_if_called_subroutine_returns"],1)
        self.assertFalse(v["realloc_result_checked_before_AX_1"])
        self.assertFalse(v["actual_localalloc_retry_success_proven"])
        retry=allocation_failure_plan("recovery",1)
        self.assertTrue(retry["localalloc_retry_if_callback_returns_nonzero"])
        self.assertFalse(retry["propagates_zero_to_immediate_caller_if_reached"])

    def test_recovery_handler_missing_resource_follows_exception_helper(self):
        for o,b in ((False,False),(False,True),(True,False)):
            v=known_recovery_handler_plan(o,b)
            self.assertFalse(v["enters_recovery_path"])
            self.assertTrue(v["calls_error_helper_1000_4564"])
            self.assertTrue(v["throw_may_unwind"])
            self.assertEqual(v["normal_return_AX_if_called_subroutine_returns"],0)

    def test_original_oom_to_DGROUP_scalar_store_is_conditionally_reachable(self):
        self.assertTrue(failing_alloc_global_zero_writer(0x00A2,ONESHOT_LATCH_DS))
        self.assertTrue(failing_alloc_global_zero_writer(0x46B2,CLOCK_FLAG_DS))
        self.assertEqual(allocate_trio(0x00A2,0).original_terminator_write_DS_offset,
                         ONESHOT_LATCH_DS)
        self.assertEqual(allocate_trio(0x46B2,0).original_terminator_write_DS_offset,
                         CLOCK_FLAG_DS)
        self.assertFalse(audit()["normal_gameplay_OOM_return_to_D3E_observed"])

    def test_reject_wrong_callback_return_value_or_kind(self):
        with self.assertRaisesRegex(ValueError,"must be none/default/recovery"):
            allocation_failure_plan("silent_bad")
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            allocation_failure_plan("default",-1)
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            allocation_failure_plan("recovery",65536)


if __name__=="__main__":
    unittest.main()
