#!/usr/bin/env python3
"""Bounded direct original Win16 file-name suffix and -p prefix proofs."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_filename_alias_calls import (
    COMMAND_LINE_PREFIX_PATH, EXPECTED_WRAPPERS,
    LITERAL_SUFFIXES, TIMER_OUTPUT_OFFSET,
    clock_overwrite_possible_with_suffix,load_ledger,verify
)


class Win16DirectFileNames(unittest.TestCase):
    def setUp(self):
        self.rows=load_ledger()

    def test_all_twelve_original_filename_paths_pin_suffix_literals(self):
        result=verify(self.rows)
        self.assertEqual(result["all_direct_suffix_call_paths"],12)
        self.assertEqual(result["literal_suffix_name_counts"],{
            "config.sav":2,"user.sav":10})
        self.assertEqual(result["complete_directly_named_FUN_1010_5260_callers"],5)
        self.assertTrue(result["user_sav_is_literal_in_all_known_direct_paths"])
        self.assertTrue(result["config_sav_is_literal_in_all_known_direct_paths"])

    def test_all_save_wrapper_second_parameters_are_fixed_user_sav(self):
        result=verify(self.rows)
        self.assertEqual(result["save_wrapper_upstream_direct_calls"],10)
        self.assertEqual(result["immediate_save_builder_wrappers_using_user_sav"],3)
        self.assertEqual(result["save_wrapper_upstream_by_entry"],{
            k:sorted(v) for k,v in EXPECTED_WRAPPERS.items()})
        saves=[r for r in self.rows if r["literal_file_name"]=="user.sav"]
        self.assertEqual(len(saves),10)
        self.assertTrue(all(r["literal_DGROUP_address"]=="DS:1E50" for r in saves))
        self.assertTrue(all(r["suffix_characters"]=="8" for r in saves))

    def test_both_config_file_direct_calls_have_ten_character_literal(self):
        configs=[r for r in self.rows if r["literal_file_name"]=="config.sav"]
        self.assertEqual(len(configs),2)
        self.assertEqual({r["upstream_call_site"] for r in configs},
                         {"3:52F5","3:5358"})
        self.assertTrue(all(r["literal_DGROUP_address"]=="DS:101E"
                            and r["suffix_characters"]=="10" for r in configs))

    def test_minus_p_prefix_staging_dataflow_exact_asm_sites(self):
        path=verify(self.rows)["command_line_prefix_flow"]
        self.assertEqual(path["option_character"],"-p")
        self.assertEqual(path["option_selector_case"],"3:120C")
        self.assertEqual(path["DGROUP_prefix_output_pointer"],"DS:46BE")
        self.assertEqual(path["tokenizer_call"],"3:1218")
        self.assertEqual(path["format_call"],"3:1221")
        self.assertEqual(path["format_function"],"2:6442")
        self.assertEqual(path["internal_formatter"],"2:4504")
        self.assertEqual(path["format_specifier"],"%s")
        self.assertEqual(path["one_shot_zero_writer"],"3:0ED9")

    def test_user_suffix_8_threshold_requires_prefix_4076(self):
        result=verify(self.rows)
        self.assertEqual(TIMER_OUTPUT_OFFSET,4084)
        self.assertEqual(result["prefix_chars_required_for_user_sav"],4076)
        self.assertFalse(clock_overwrite_possible_with_suffix(0,8))
        self.assertFalse(clock_overwrite_possible_with_suffix(4075,8))
        self.assertTrue(clock_overwrite_possible_with_suffix(4076,8))

    def test_config_suffix_10_threshold_requires_prefix_4074(self):
        result=verify(self.rows)
        self.assertEqual(result["prefix_chars_required_for_config_sav"],4074)
        self.assertFalse(clock_overwrite_possible_with_suffix(0,10))
        self.assertFalse(clock_overwrite_possible_with_suffix(4073,10))
        self.assertTrue(clock_overwrite_possible_with_suffix(4074,10))

    def test_nothing_claims_real_commandline_overflow_or_complete_callgraph(self):
        result=verify(self.rows)
        self.assertFalse(result["prefix_maximum_characters_statically_closed"])
        self.assertFalse(result["win16_command_line_maximum_verified"])
        self.assertFalse(result["indirect_callers_of_builder_ruled_out"])
        self.assertFalse(result["alias_writer_graph_closed"])

    def test_rejects_wrong_direct_literal(self):
        rows=copy.deepcopy(self.rows)
        rows[0]["literal_file_name"]="user.sav"
        with self.assertRaisesRegex(ValueError,"literal"):
            verify(rows)

    def test_rejects_missing_upstream_site(self):
        rows=copy.deepcopy(self.rows)
        rows.pop()
        with self.assertRaisesRegex(ValueError,"expected 12"):
            verify(rows)

    def test_rejects_new_unknown_suffix_pointer(self):
        rows=copy.deepcopy(self.rows)
        rows[5]["literal_DGROUP_address"]="DS:3200"
        with self.assertRaisesRegex(ValueError,"Unproven"):
            verify(rows)

    def test_rejects_mutated_wrapper_to_builder_branch(self):
        rows=copy.deepcopy(self.rows)
        row=next(r for r in rows if r["wrapper_entry"]=="3:5466")
        row["call_into_5260_site"]="3:5397"
        with self.assertRaisesRegex(ValueError,"Wrong wrapper"):
            verify(rows)

    def test_rejects_duplicate_direct_caller(self):
        rows=copy.deepcopy(self.rows)
        rows[0]["upstream_call_site"]=rows[1]["upstream_call_site"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            verify(rows)

    def test_invalid_string_lengths_rejected(self):
        with self.assertRaisesRegex(ValueError,"negative"):
            clock_overwrite_possible_with_suffix(-1,8)
        with self.assertRaisesRegex(ValueError,"negative"):
            clock_overwrite_possible_with_suffix(1,-8)
        with self.assertRaisesRegex(ValueError,"wrap"):
            clock_overwrite_possible_with_suffix(65535,8)


if __name__=="__main__":
    unittest.main()
