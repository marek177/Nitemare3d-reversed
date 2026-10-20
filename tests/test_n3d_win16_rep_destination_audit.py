#!/usr/bin/env python3
"""Synthetic regression tests of an existing Win16 Ghidra REP-write ledger."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_rep_destination_audit import (
    KNOWN_FIXED_32, KNOWN_FIXED_16, KNOWN_REP16_BOUNDED,
    KNOWN_HEAP_90B, WIN110_DGROUP_FILE_BACKED_BYTES,
    load_ledger, overlaps_linear_region, provenance_audit,
    STRING_CLOCK_OFFSET, STRING_STAGING_SITES,
    unbounded_string_copy_reaches_clock,
)


class Win16RepDestinationTests(unittest.TestCase):
    def setUp(self):
        self.rows=load_ledger()

    def test_complete_archived_textual_six_opcode_census(self):
        result=provenance_audit(self.rows)
        self.assertEqual(result["total_rep_sites"],83)
        self.assertEqual(result["opcode_type_counts"],{
            "STOSB.REP":7,"STOSW.REP":17,"STOSD.REP":11,
            "MOVSB.REP":14,"MOVSW.REP":20,"MOVSD.REP":14,
        })
        self.assertEqual(result["source_byte_bounded_rep_movsd_stosd"],25)
        self.assertEqual(result["source_byte_bounded_rep_movsw_stosw"],9)
        self.assertEqual(result["source_byte_bounded_rep_total"],34)
        self.assertEqual(result["remaining_rep_destinations_for_pointer_provenance"],49)
        self.assertFalse(result["alias_writer_graph_complete"])
        self.assertFalse(result["original_1_10_sha_reread_this_run"])

    def test_all_25_dword_rep_destinations_are_classified_with_lengths(self):
        relevant=[r for r in self.rows
                  if r["rep_operation"] in ("MOVSD.REP","STOSD.REP")]
        self.assertEqual(len(relevant),25)
        self.assertTrue(all(r["bounded_total_write_bytes"] for r in relevant))
        self.assertTrue(all(r["destination_class"] not in (
            "DESTINATION_PROVENANCE_OPEN",
            "GHIDRA_ANNOTATED_DEST_REQUIRES_BOUND") for r in relevant))
        self.assertEqual(sum(r["destination_class"]=="STACK_LOCAL_OR_SS_REGION"
                             for r in relevant),14)

    def test_exact_five_fixed_DGROUP_copy_ranges_are_disjoint(self):
        result=provenance_audit(self.rows)
        fixed=result["five_fixed_DGROUP_writes"]
        self.assertEqual(len(fixed),5)
        self.assertEqual({r["source"] for r in fixed},set(KNOWN_FIXED_32))
        for r in fixed:
            self.assertFalse(r["overlap_DS_00A2"])
            self.assertFalse(r["overlap_DS_46B2"])
        self.assertTrue(result["fixed_DGROUP_regions_exclude_clock_and_latch"])

    def test_all_nine_new_rep_movsw_stosw_are_bounded_from_original_asm(self):
        result=provenance_audit(self.rows)
        self.assertEqual(len(KNOWN_REP16_BOUNDED),9)
        for site,length in KNOWN_REP16_BOUNDED.items():
            record=next(row for row in self.rows if row["site"]==site)
            self.assertIn(record["rep_operation"],("MOVSW.REP","STOSW.REP"))
            self.assertEqual(int(record["bounded_total_write_bytes"]),length)
            self.assertNotIn(record["destination_class"],(
                "DESTINATION_PROVENANCE_OPEN",
                "GHIDRA_ANNOTATED_DEST_REQUIRES_BOUND",
                "STRING_DSGROUP_BUFFER_NO_LENGTH_BOUND"))
        self.assertEqual(result["source_byte_bounded_rep_total"],34)

    def test_seven_total_fixed_dgroup_write_ranges_exclude_clock(self):
        result=provenance_audit(self.rows)
        seven=result["seven_fixed_DGROUP_writes"]
        self.assertEqual(len(seven),7)
        self.assertEqual({r["source"] for r in seven},
                         set(KNOWN_FIXED_32)|set(KNOWN_FIXED_16))
        two=result["additional_two_18byte_fixed_DGROUP_writes"]
        self.assertEqual({r["source"] for r in two},set(KNOWN_FIXED_16))
        for r in two:
            self.assertEqual(r["address"],"DS:423E")
            self.assertEqual(r["last_written_address"],"DS:424F")
            self.assertEqual(r["bytes"],18)
            self.assertFalse(r["overlap_DS_00A2"])
            self.assertFalse(r["overlap_DS_46B2"])

    def test_new_rep16_stack_zeroing_is_32_bytes(self):
        originals={"1008:6A11","1008:6A6B","1008:6AC3","1008:6B18"}
        data=[row for row in self.rows if row["site"] in originals]
        self.assertEqual(len(data),4)
        self.assertTrue(all(row["rep_operation"]=="STOSW.REP"
                            and row["bounded_total_write_bytes"]=="32"
                            and row["destination_class"]=="STACK_LOCAL_OR_SS_REGION"
                            for row in data))

    def test_changed_32_byte_stack_zeroing_invalidates_original_proof(self):
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="1008:6B18")
        row["bounded_total_write_bytes"]="34"
        with self.assertRaisesRegex(ValueError,"REP16 instruction length"):
            provenance_audit(rows)

    def test_8e90_zero_fill_ends_exactly_at_file_backed_DGROUP_end(self):
        # NE segment 10 (file-backed bytes=36526) is corroborating original
        # segment-table evidence, not a runtime heap or total allocation size.
        self.assertEqual(WIN110_DGROUP_FILE_BACKED_BYTES,0x8EAE)
        result=provenance_audit(self.rows)
        self.assertEqual(result["DGROUP_tail_REP_STOSD_exclusive_end"],"DS:8EAE")
        zero=next(x for x in result["five_fixed_DGROUP_writes"]
                  if x["source"]=="1010:51C5")
        self.assertEqual(zero["address"],"DS:8E90")
        self.assertEqual(zero["last_written_address"],"DS:8EAD")
        self.assertEqual(zero["bytes"],30)

    def test_two_rep_movsd_heap_90_byte_contracts(self):
        destinations=[r for r in self.rows
                      if r["site"] in KNOWN_HEAP_90B]
        self.assertEqual(len(destinations),2)
        self.assertTrue(all(r["destination_class"]=="LOCALALLOC_FIXED_90B_RETURN"
                            for r in destinations))
        self.assertTrue(all(r["bounded_total_write_bytes"]=="90"
                            for r in destinations))
        self.assertTrue(provenance_audit(self.rows)[
            "heap_destinations_disjoint_from_globals_only_under_valid_Win16_LocalAlloc_contract"
        ])

    def test_invalid_opcode_or_copy_length_rejected(self):
        rows=copy.deepcopy(self.rows)
        rows[0]["opcode_hex"]="F3 66 AA"
        with self.assertRaisesRegex(ValueError,"opcode contradiction"):
            provenance_audit(rows)
        rows=copy.deepcopy(self.rows)
        r=next(x for x in rows if x["site"]=="1010:4E21")
        r["bounded_total_write_bytes"]="0"
        with self.assertRaisesRegex(ValueError,"Invalid source-bounded"):
            provenance_audit(rows)

    def test_unknown_bounded_copy_rejected(self):
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="1010:4E21")
        row["destination_class"]="DESTINATION_PROVENANCE_OPEN"
        with self.assertRaisesRegex(ValueError,"Length alone"):
            provenance_audit(rows)

    def test_partial_counts_are_detected(self):
        rows=copy.deepcopy(self.rows)
        rows.pop()
        with self.assertRaisesRegex(ValueError,"census mismatch"):
            provenance_audit(rows)

    def test_fake_write_range_can_cover_the_clock_byte(self):
        self.assertTrue(overlaps_linear_region(0x46B1,2,0x46B2))
        self.assertTrue(overlaps_linear_region(0x46AF,4,0x46B2))
        self.assertFalse(overlaps_linear_region(0x46B1,1,0x46B2))
        self.assertFalse(overlaps_linear_region(0x3930,20,0x46B2))

    def test_u16_boundary_and_zero_length(self):
        self.assertFalse(overlaps_linear_region(0x8E90,0,0x8E90))
        self.assertFalse(overlaps_linear_region(0x8E90,30,0x8EAE))
        self.assertTrue(overlaps_linear_region(0x8E90,30,0x8EAD))
        with self.assertRaisesRegex(ValueError,"segment wrap"):
            overlaps_linear_region(0xFFFF,2,0x0000)

    def test_modifying_fixed_range_to_hit_flag_is_not_accepted(self):
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="1010:51C5")
        row["fixed_DGROUP_start"]="0x46B1"
        report=provenance_audit(rows,enforce_archived_census=False)
        self.assertFalse(report["fixed_DGROUP_regions_exclude_clock_and_latch"])
        with self.assertRaisesRegex(ValueError,"destination span changed"):
            provenance_audit(rows)

    def test_string_buffer_clock_overlap_threshold_exact(self):
        self.assertEqual(STRING_CLOCK_OFFSET, 0xFF4)
        self.assertEqual(STRING_CLOCK_OFFSET, 4084)
        self.assertFalse(unbounded_string_copy_reaches_clock(0,0))
        self.assertFalse(unbounded_string_copy_reaches_clock(4083,0))
        self.assertTrue(unbounded_string_copy_reaches_clock(4084,0))
        self.assertTrue(unbounded_string_copy_reaches_clock(1000,3084))
        self.assertFalse(unbounded_string_copy_reaches_clock(1000,3083))

    def test_all_four_unbounded_string_copy_sites_remain_open(self):
        report=provenance_audit(self.rows)
        self.assertEqual(set(report["unbounded_string_staging_REP_sites"]),
                         STRING_STAGING_SITES)
        self.assertEqual(
            report["string_staging_distance_to_flag_bytes"],4084)
        self.assertEqual(
            report["last_NUL_overlaps_clock_if_sum_characters_at_least"],4084)
        self.assertFalse(report["string_alias_dynamic_reachability_proven"])
        self.assertEqual(
            report["remaining_rep_destinations_for_pointer_provenance"],58)

    def test_config_sav_fixed_suffix_threshold(self):
        result=provenance_audit(self.rows)
        self.assertEqual(result["fixed_config_sav_string"],"config.sav")
        self.assertEqual(result["fixed_config_sav_characters"],10)
        self.assertEqual(result["fixed_config_sav_callers"],
                         ["1010:52F5","1010:5358"])
        self.assertEqual(result["other_parameter_or_register_string_callers"],
                         ["1010:5397","1010:548C","1010:5759"])
        self.assertEqual(
            result["prefix_characters_required_to_touch_clock_with_config_sav"],4074)
        self.assertFalse(unbounded_string_copy_reaches_clock(0,10))
        self.assertFalse(unbounded_string_copy_reaches_clock(4073,10))
        self.assertTrue(unbounded_string_copy_reaches_clock(4074,10))

    def test_unsafe_long_or_negative_string_length_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError,"negative"):
            unbounded_string_copy_reaches_clock(-1,5)
        with self.assertRaisesRegex(ValueError,"wraps"):
            unbounded_string_copy_reaches_clock(65535,2)

    def test_string_copy_classification_downgrade_rejected(self):
        rows=copy.deepcopy(self.rows)
        row=next(x for x in rows if x["site"]=="1010:527E")
        row["destination_class"]="DESTINATION_PROVENANCE_OPEN"
        with self.assertRaisesRegex(ValueError,"string-staging"):
            provenance_audit(rows)

    def test_site_duplicate_rejected(self):
        rows=copy.deepcopy(self.rows)
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaisesRegex(ValueError,"Duplicate REP site"):
            provenance_audit(rows)


if __name__=="__main__":
    unittest.main()
