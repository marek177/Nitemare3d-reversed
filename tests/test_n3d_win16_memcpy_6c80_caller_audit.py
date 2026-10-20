#!/usr/bin/env python3
"""Synthetic CPU-width and archived Win16 NE2:6C80 caller contract tests.

These tests do not execute Nitemare game code, Windows 3.11, or the
original v1.10 SHA-256-pinned executable.
"""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_memcpy_6c80_caller_audit import (
    EXACT_DIRECT_CALLERS,
    EXPECTED_CALLER_ENTRIES,
    CAPACITY_SIGNED_BRANCH_SITES,
    ADDITION_WRAP_CONCERN_SITES,
    load_manifest,audit,u16,i16,check_u16,
    append_direct_fast_path,enough_capacity_signed,
    additive_required_len_u16,
    requested_localalloc_size_for_string_length,
    clamped_stream_chunk,
)
from n3d_win16_rep_destination_audit import (
    MEMCPY_NAMED_DIRECT_CALLERS,win16_memcpy_exact_rep_schedule,
)


class Win16MemcpyCallerAudit(unittest.TestCase):
    def setUp(self):
        self.rows=load_manifest()

    def test_all_eight_archived_direct_callers_are_accounted_for(self):
        report=audit(self.rows)
        self.assertEqual(len(self.rows),8)
        self.assertEqual(set(row["site"] for row in self.rows),EXACT_DIRECT_CALLERS)
        self.assertEqual(EXACT_DIRECT_CALLERS,MEMCPY_NAMED_DIRECT_CALLERS)
        self.assertEqual(report["direct_named_caller_count"],8)
        self.assertEqual(report["caller_entries"],EXPECTED_CALLER_ENTRIES)
        self.assertTrue(report["full_argument_provenance_recorded_for_all_eight"])
        self.assertEqual(report["near_call_with_explicit_push_CS"],"2:3F20")
        self.assertEqual(len(report["direct_far_call_sites"]),7)

    def test_does_not_claim_full_alias_or_all_inputs_safe(self):
        report=audit(self.rows)
        self.assertFalse(report["input_count_proven_fit_all_states"])
        self.assertFalse(report["memcpy_helper_target_alias_excluded_for_all_states"])
        self.assertFalse(report["win16_original_exe_freshly_rehashed_in_this_run"])
        self.assertEqual(report["memcpy_helper_copy_sites_closed_in_full_program"],0)

    def test_signed_capacity_guard_sites_have_exact_branch_types(self):
        report=audit(self.rows)
        self.assertEqual(report["signed_capacity_compare_sites"],{
            "0:0E51":"JGE","0:0F74":"JGE","0:4C72":"JLE"})
        self.assertEqual(report["signed_capacity_compare_sites"],
                         CAPACITY_SIGNED_BRANCH_SITES)
        for site,kind in CAPACITY_SIGNED_BRANCH_SITES.items():
            row=next(r for r in self.rows if r["site"]==site)
            self.assertIn(kind,row["local_capacity_or_allocation_guard"])
            self.assertIn("signed",row["guard_width"])

    def test_16bit_signed_unsigned_capacity_disagreement(self):
        # Signed comparisons are not unsigned capacity proofs.
        self.assertEqual(i16(0x7FFF),32767)
        self.assertEqual(i16(0x8000),-32768)
        self.assertEqual(i16(0xFFFF),-1)
        self.assertTrue(enough_capacity_signed(32767,32768))
        self.assertFalse(32767>=32768)
        self.assertFalse(enough_capacity_signed(32768,32767))
        self.assertTrue(32768>=32767)

    def test_signed_capacity_matches_unsigned_for_small_nonnegative_lengths(self):
        for capacity in range(0,257):
            for count in range(0,257):
                self.assertEqual(enough_capacity_signed(capacity,count),
                                 capacity>=count)

    def test_append_fast_path_accepts_wrapped_addition(self):
        # Original JLE signed compares wrapped 16-bit used+added.
        self.assertTrue(append_direct_fast_path(65530,10,20))
        self.assertEqual(additive_required_len_u16(65530,10),4)
        self.assertGreater(65530+10,20)
        self.assertTrue(append_direct_fast_path(10,10,20))
        self.assertFalse(append_direct_fast_path(10,11,20))
        # No unsigned wrap, but compare result has the sign bit set.
        self.assertTrue(append_direct_fast_path(32760,10,20))

    def test_signed_append_compare_proven_only_when_nonoverflow_nonnegative(self):
        for used in range(0,61,3):
            for added in range(0,61,5):
                for capacity in (0,12,35,65,120):
                    self.assertEqual(append_direct_fast_path(used,added,capacity),
                                     used+added<=capacity)

    def test_additive_path_requests_can_wrap(self):
        report=audit(self.rows)
        self.assertEqual(set(report["modulo_16_bit_addition_sites"]),
                         ADDITION_WRAP_CONCERN_SITES)
        self.assertEqual(additive_required_len_u16(65530,10),4)
        self.assertEqual(additive_required_len_u16(32768,32768),0)
        self.assertEqual(additive_required_len_u16(0,0),0)
        self.assertEqual(additive_required_len_u16(65535,0),65535)
        self.assertEqual(additive_required_len_u16(65535,1),0)

    def test_localalloc_size_plus_one_wrap_boundary(self):
        self.assertEqual(requested_localalloc_size_for_string_length(0),1)
        self.assertEqual(requested_localalloc_size_for_string_length(1),2)
        self.assertEqual(requested_localalloc_size_for_string_length(65534),65535)
        self.assertEqual(requested_localalloc_size_for_string_length(65535),0)
        for n in range(65536):
            self.assertEqual(requested_localalloc_size_for_string_length(n),
                             (n+1)&0xFFFF)

    def test_stream_minimum_is_unsigned_and_never_exceeds_either(self):
        self.assertEqual(clamped_stream_chunk(15,25),15)
        self.assertEqual(clamped_stream_chunk(25,15),15)
        self.assertEqual(clamped_stream_chunk(65535,1),1)
        self.assertEqual(clamped_stream_chunk(1,65535),1)
        self.assertEqual(clamped_stream_chunk(0,65535),0)
        for avail in range(0,65536,257):
            for remaining in (0,1,2,10,65535):
                c=clamped_stream_chunk(avail,remaining)
                self.assertLessEqual(c,avail)
                self.assertLessEqual(c,remaining)
                for odd in (True,False):
                    sched=win16_memcpy_exact_rep_schedule(c,odd)
                    self.assertEqual(sched["total_bytes"],c)

    def test_rejects_missing_or_duplicate_direct_caller(self):
        with self.assertRaisesRegex(ValueError,"eight"):
            audit(self.rows[:-1])
        rows=copy.deepcopy(self.rows)
        rows[1]=copy.deepcopy(rows[0])
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            audit(rows)

    def test_rejects_forged_struct_or_missing_guard(self):
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="0:0E51")
        row["guard_width"]="unsigned"
        with self.assertRaisesRegex(ValueError,"signed capacity"):
            audit(rows)
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="0:4C72")
        row["caller_entry"]="0:0000"
        with self.assertRaisesRegex(ValueError,"Caller function entry"):
            audit(rows)
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="0:0DD0")
        row["source_operand"]=""
        with self.assertRaisesRegex(ValueError,"source_operand"):
            audit(rows)

    def test_rejects_unverified_count_or_unsigned_value(self):
        for func,args in [
            (append_direct_fast_path,(65536,2,10)),
            (enough_capacity_signed,(-1,0)),
            (additive_required_len_u16,(0,65536)),
            (requested_localalloc_size_for_string_length,(-1,)),
            (clamped_stream_chunk,(65536,0)),
        ]:
            with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
                func(*args)
        with self.assertRaisesRegex(ValueError,"unsigned 16-bit"):
            check_u16(65536,"input")

    def test_src_dst_count_words_present_in_each_original_asm_row(self):
        entries={r["site"]:r for r in self.rows}
        self.assertIn("[param1 struct + 0]",entries["0:0DD0"]["source_operand"])
        self.assertIn("[param1 struct + 0]",entries["0:0F74"]["destination_operand"])
        self.assertIn("param5",entries["0:0ED9"]["copy_count_operand"])
        self.assertIn("param3",entries["0:0EEA"]["copy_count_operand"])
        self.assertIn("strlen",entries["0:0E16"]["copy_count_operand"])
        self.assertIn("min(",entries["2:3F20"]["copy_count_operand"])


if __name__=="__main__":
    unittest.main()
