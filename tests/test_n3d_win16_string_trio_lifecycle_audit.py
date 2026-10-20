#!/usr/bin/env python3
"""Synthetic Win16 original string trio state/conditional OOM-writer tests.

No original proprietary game binaries, historical Win16 APIs, live heap,
DOSBox or Windows 3.11 runtime execution in this regression suite.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_string_trio_lifecycle_audit import (
    EMPTY_SENTINEL,CLOCK_FLAG_DS,ONESHOT_LATCH_DS,
    INSTRUCTION_WITNESSES,
    Trio,init_trio,free_is_attempted,teardown_trio,
    allocate_trio,failing_alloc_global_zero_writer,
    initial_empty_assignment_plan,word_signed,audit,
    E26_NAMED_DIRECT_COUNT_SOURCES, E26_LOADSTRING_BUFFER_MAX,
    E26_LOADSTRING_CSTRING_LOCAL_FRAME_SIZE,
    e26_direct_caller_count_upper_bound
)


class Win16OriginalStringTrioAudit(unittest.TestCase):

    def test_initial_three_words_match_original_0cdc(self):
        self.assertEqual(init_trio(),Trio(0x0584,0,0))
        report=audit()
        self.assertEqual(report["initial_state"],{
            "ptr":0x0584,"used":0,"capacity":0})
        self.assertEqual(report["original_empty_sentinel_byte"],"00")
        self.assertEqual(report["fields"],{
            "ptr":"+0","used":"+2","capacity":"+4"})

    def test_sentinel_is_not_null_and_free_skips_it(self):
        self.assertNotEqual(EMPTY_SENTINEL,0)
        self.assertFalse(free_is_attempted(EMPTY_SENTINEL))
        self.assertTrue(free_is_attempted(0))
        self.assertTrue(free_is_attempted(0x2000))
        self.assertEqual(teardown_trio(init_trio()),(init_trio(),False))
        self.assertEqual(teardown_trio(Trio(0x2000,6,12)),(init_trio(),True))

    def test_zero_count_reinitializes_without_free(self):
        previous=Trio(0x2000,5,10)
        transition=allocate_trio(0,None,previous)
        self.assertEqual(transition.resulting_trio,init_trio())
        self.assertFalse(transition.old_ptr_freed)
        self.assertFalse(transition.result_is_valid_normal_owned_block_proven)
        self.assertIsNone(transition.original_terminator_write_DS_offset)
        self.assertIsNone(transition.localalloc_passed_bytes)

    def test_positive_count_has_n_plus_one_heap_request(self):
        for n in (1,2,10,163,18098,32767,65534):
            t=allocate_trio(n,0x2000)
            self.assertEqual(t.resulting_trio,Trio(0x2000,n,n))
            self.assertEqual(t.localalloc_passed_bytes,n+1)
            self.assertEqual(t.localalloc_wrapper_effective_bytes,n+1)
            self.assertFalse(t.heap_pointer_was_zero)
            self.assertFalse(t.ptr_null_guard_before_terminator)

    def test_maximum_unsigned_length_allocation_request_wraps_to_one(self):
        t=allocate_trio(65535,0)
        self.assertEqual(t.localalloc_passed_bytes,0)
        self.assertEqual(t.localalloc_wrapper_effective_bytes,1)
        self.assertEqual(t.original_terminator_write_DS_offset,0xFFFF)
        self.assertEqual(t.resulting_trio.used,65535)
        self.assertEqual(t.resulting_trio.capacity,65535)
        self.assertEqual(t.resulting_trio.ptr,0)

    def test_failed_allocation_for_clock_flag_length_zeroes_clock(self):
        t=allocate_trio(CLOCK_FLAG_DS,0)
        self.assertTrue(t.heap_pointer_was_zero)
        self.assertEqual(t.localalloc_passed_bytes,CLOCK_FLAG_DS+1)
        self.assertEqual(t.original_terminator_write_DS_offset,CLOCK_FLAG_DS)
        self.assertTrue(
            failing_alloc_global_zero_writer(CLOCK_FLAG_DS,CLOCK_FLAG_DS))
        self.assertEqual(t.resulting_trio.ptr,0)

    def test_failed_allocation_for_one_shot_length_zeroes_latch(self):
        t=allocate_trio(ONESHOT_LATCH_DS,0)
        self.assertTrue(t.heap_pointer_was_zero)
        self.assertEqual(t.localalloc_passed_bytes,ONESHOT_LATCH_DS+1)
        self.assertEqual(t.original_terminator_write_DS_offset,ONESHOT_LATCH_DS)
        self.assertTrue(failing_alloc_global_zero_writer(
            ONESHOT_LATCH_DS,ONESHOT_LATCH_DS))

    def test_original_scalar_alias_does_not_claim_runtime_reachability(self):
        report=audit()
        self.assertEqual(report["new_conditional_scalar_alias_writer"],"1000:0D65")
        self.assertFalse(report["actual_allocator_failure_or_alias_reachability_proved"])
        self.assertFalse(report["nonzero_allocation_result_null_checked_before_terminator"])
        self.assertEqual(report["oom_callback_possible"]["indirect_far_call"],
                         "1008:5AF6")
        self.assertEqual(report["oom_callback_possible"]["retry_if_callback_nonzero"],
                         "1008:5AFF")

    def test_normal_nonzero_heap_pointer_shifts_null_store_offset(self):
        n=CLOCK_FLAG_DS
        good=allocate_trio(n,0x2000)
        self.assertEqual(good.original_terminator_write_DS_offset,0x66B2)
        self.assertNotEqual(good.original_terminator_write_DS_offset,CLOCK_FLAG_DS)
        self.assertFalse(good.heap_pointer_was_zero)
        # Nonzero allocated pointer is NOT an independent heap ownership proof.
        self.assertFalse(good.result_is_valid_normal_owned_block_proven)

    def test_uint16_alias_scan_failing_heap_pointer_across_all_lengths(self):
        hits_clock=[]
        hits_latch=[]
        for n in range(1,0x10000):
            if failing_alloc_global_zero_writer(n,CLOCK_FLAG_DS):
                hits_clock.append(n)
            if failing_alloc_global_zero_writer(n,ONESHOT_LATCH_DS):
                hits_latch.append(n)
            # In null-result case, byte written at DS:n.
            if n in (CLOCK_FLAG_DS,ONESHOT_LATCH_DS):
                self.assertEqual(
                    allocate_trio(n,0).original_terminator_write_DS_offset,n)
        self.assertEqual(hits_clock,[CLOCK_FLAG_DS])
        self.assertEqual(hits_latch,[ONESHOT_LATCH_DS])
        self.assertFalse(failing_alloc_global_zero_writer(0,CLOCK_FLAG_DS))

    def test_u16_wrap_of_pointer_plus_index_is_explicit(self):
        t=allocate_trio(0x0200,0xFFF0)
        self.assertEqual(t.original_terminator_write_DS_offset,0x01F0)
        self.assertFalse(t.heap_pointer_was_zero)
        # This does NOT establish the underlying allocation may alias DGROUP.
        self.assertFalse(t.result_is_valid_normal_owned_block_proven)

    def test_critical_original_instruction_bytes_are_pinned(self):
        self.assertEqual(INSTRUCTION_WITNESSES["1000:0CEA"][0],"C7 07 84 05")
        self.assertEqual(INSTRUCTION_WITNESSES["1000:0D57"][0],"8D 45 01")
        self.assertEqual(INSTRUCTION_WITNESSES["1000:0D65"][0],"C6 01 00")
        self.assertEqual(INSTRUCTION_WITNESSES["1000:0D68"][0],"89 7C 02")
        self.assertEqual(INSTRUCTION_WITNESSES["1000:0D6B"][0],"89 7C 04")
        self.assertEqual(INSTRUCTION_WITNESSES["1008:5AF6"][0],"FF 1E 4A 09")
        self.assertGreaterEqual(len(INSTRUCTION_WITNESSES),20)

    def test_canonical_empty_signed_jge_skips_alloc_at_32768(self):
        p=initial_empty_assignment_plan(32768)
        self.assertEqual(p["signed_requested_used"],-32768)
        self.assertTrue(p["jge_skips_reallocation"])
        self.assertEqual(p["copy_destination_DS_offset_if_no_allocation"],0x0584)
        self.assertEqual(p["copy_last_offset_before_uint16_wrap"],0x8583)
        self.assertTrue(p["copy_intersects_DS_46B2_if_nonfaulting"])
        self.assertTrue(p["would_call_copy"])
        self.assertFalse(p["actual_normal_runtime_reachability_proven"])
        self.assertFalse(p["observed_source_length_and_pointer_valid"])
        self.assertLess(0x8583,0x8EAE)

    def test_canonical_empty_small_positive_requests_do_allocate(self):
        for n in (1,2,100,ONESHOT_LATCH_DS,CLOCK_FLAG_DS,32767):
            p=initial_empty_assignment_plan(n)
            self.assertFalse(p["jge_skips_reallocation"])
            self.assertIsNone(p["copy_destination_DS_offset_if_no_allocation"])
            self.assertFalse(p["copy_intersects_DS_46B2_if_nonfaulting"])
        self.assertTrue(initial_empty_assignment_plan(0)[
            "jge_skips_reallocation"])
        self.assertFalse(initial_empty_assignment_plan(0)["would_call_copy"])

    def test_all_signed_high_bit_counts_skip_growth_from_zero_cap(self):
        for n in range(32768,65536):
            p=initial_empty_assignment_plan(n)
            self.assertTrue(p["jge_skips_reallocation"])
            self.assertEqual(p["copy_destination_DS_offset_if_no_allocation"],
                             EMPTY_SENTINEL)
            self.assertTrue(p["copy_intersects_DS_46B2_if_nonfaulting"])
        self.assertEqual(word_signed(0xFFFF),-1)
        self.assertEqual(word_signed(0x8000),-32768)
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            word_signed(65536)

    def test_initial_large_copy_into_sentinel_requires_no_localalloc_failure(self):
        report=audit()
        p=report["conditional_direct_memcpy_to_sentinel_from_empty"]
        self.assertEqual(p["state"],init_trio().as_dict())
        self.assertEqual(p["allocator_skipped_by_signed_JGE"],"1000:0E33")
        self.assertEqual(p["target_callee"],"1008:6C80")
        self.assertEqual(p["copy_site"],"1000:0E51")
        self.assertEqual(p["example"]["copy_last_offset_before_uint16_wrap"],
                         0x8583)
        self.assertTrue(p["can_touch_clock_flag_under_nonfaulting_model"])
        self.assertFalse(p["large_source_data_reachability_proven"])
        self.assertEqual(p["original_DGROUP_file_backed_exclusive_end"],"0x8EAE")

    def test_three_named_e26_direct_caller_count_sources(self):
        p=audit()
        self.assertEqual(set(p["assignment_direct_caller_count_sources"]),{
            "1000:0E7B","1000:0EAB","1000:3275"})
        self.assertEqual(p["resource_assignment_LoadString_site"],"1000:3275")
        self.assertEqual(p["resource_assignment_resource_import_call"],"1000:3293")
        self.assertEqual(p["remaining_direct_assignment_sources_32768_reachability_open"],
                         ["1000:0E7B","1000:0EAB"])
        self.assertEqual(E26_NAMED_DIRECT_COUNT_SOURCES["1000:0E7B"],
                         "source_trio.used at 1000:0E75")

    def test_loadstring_u255_resource_copy_excludes_negative_signed_request(self):
        self.assertEqual(E26_LOADSTRING_BUFFER_MAX,255)
        self.assertEqual(E26_LOADSTRING_CSTRING_LOCAL_FRAME_SIZE,256)
        self.assertEqual(e26_direct_caller_count_upper_bound("1000:3275"),255)
        self.assertIsNone(e26_direct_caller_count_upper_bound("1000:0E7B"))
        self.assertIsNone(e26_direct_caller_count_upper_bound("1000:0EAB"))
        for count in range(256):
            self.assertFalse(initial_empty_assignment_plan(count)[
                "jge_skips_reallocation"] if count else False)
            self.assertFalse(initial_empty_assignment_plan(count)[
                "copy_intersects_DS_46B2_if_nonfaulting"])
        self.assertFalse(audit()["resource_assignment_high_bit_32768_reachable"])
        with self.assertRaisesRegex(ValueError,"Unrecognized"):
            e26_direct_caller_count_upper_bound("1000:0000")

    def test_original_free_then_init_distinct_from_init_only(self):
        old=Trio(0x2000,5,10)
        reset,attempted_free=teardown_trio(old)
        self.assertTrue(attempted_free)
        self.assertEqual(reset,init_trio())
        simply_reset=allocate_trio(0,None,old)
        self.assertFalse(simply_reset.old_ptr_freed)
        self.assertEqual(simply_reset.resulting_trio,reset)

    def test_reject_nonword_length_pointer_and_target(self):
        for args in [(-1,0),(65536,0),(1,65536),(1,-1)]:
            with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
                allocate_trio(*args)
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            free_is_attempted(65536)
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            failing_alloc_global_zero_writer(1,65536)
        with self.assertRaisesRegex(ValueError,"requires modeled heap result"):
            allocate_trio(1,None)


if __name__=="__main__":
    unittest.main()
