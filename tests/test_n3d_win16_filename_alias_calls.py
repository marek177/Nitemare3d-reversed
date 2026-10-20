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
    WIN31_PROGRAM_MANAGER_CMDLINE_FIELD_MAX,
    WIN110_SSCANF_FORMAT_DISPATCH, WIN110_SSCANF_BYTE_STORE,
    WIN110_SSCANF_WIDTH_GATE, WIN110_SSCANF_TERMINAL_NUL_STORE,
    win31_program_manager_launcher_excludes_timer_alias,
    original_commandline_near_copy_request_bytes,
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

    def test_original_input_scanner_not_sprintf(self):
        result=verify(self.rows)
        flow=result["command_line_prefix_flow"]
        self.assertEqual(flow["scanner_kind"],"sscanf-like INPUT scanner")
        self.assertTrue(flow["scanner_input_token_is_source"])
        self.assertEqual(flow["scan_call"],"3:1221")
        self.assertEqual(flow["scan_function"],"2:6442")
        self.assertEqual(flow["input_formatter"],"2:4504")
        self.assertEqual(flow["scanner_format_source"],"DS:0D8C")
        self.assertEqual(flow["format_specifier"],"%s")
        self.assertEqual(result["input_scan_format"],"%s")
        self.assertTrue(result["input_scan_source_argument_is_token"])
        self.assertFalse(result["input_scan_destination_capacity_argument_present"])

    def test_original_input_scan_has_no_percent_s_width_guard(self):
        result=verify(self.rows)
        self.assertEqual(WIN110_SSCANF_FORMAT_DISPATCH,"2:46AC")
        self.assertEqual(WIN110_SSCANF_WIDTH_GATE,"2:47F5")
        self.assertEqual(WIN110_SSCANF_BYTE_STORE,"2:484B")
        self.assertEqual(WIN110_SSCANF_TERMINAL_NUL_STORE,"2:4892")
        self.assertEqual(
            result["scan_direct_byte_store_opcode"],
            "2:484B MOV BYTE PTR ES:[BX],AL")
        self.assertFalse(result["scan_explicit_width_limit_for_percent_s"])

    def test_historical_win31_program_manager_command_field_bound(self):
        proof=verify(self.rows)
        self.assertEqual(WIN31_PROGRAM_MANAGER_CMDLINE_FIELD_MAX,128)
        self.assertEqual(proof["win31_program_manager_command_field_max"],128)
        self.assertTrue(proof["win31_program_manager_launch_route_cannot_reach_flag"])
        self.assertTrue(win31_program_manager_launcher_excludes_timer_alias(128,10))
        self.assertTrue(win31_program_manager_launcher_excludes_timer_alias(128,8))
        self.assertTrue(win31_program_manager_launcher_excludes_timer_alias(0,10))
        self.assertFalse(clock_overwrite_possible_with_suffix(128,10))
        self.assertFalse(clock_overwrite_possible_with_suffix(128,8))

    def test_program_manager_limit_cannot_be_applied_to_arbitrary_win16(self):
        proof=verify(self.rows)
        self.assertTrue(proof["win31_program_manager_scoped_only"])
        self.assertFalse(proof["Win311_program_manager_limit_independently_verified"])
        self.assertFalse(proof["all_Win16_launch_methods_proven_bounded"])
        self.assertFalse(proof["win16_command_line_maximum_verified"])
        with self.assertRaisesRegex(ValueError,"not within documented"):
            win31_program_manager_launcher_excludes_timer_alias(129,8)
        with self.assertRaisesRegex(ValueError,"negative"):
            win31_program_manager_launcher_excludes_timer_alias(-1,8)

    def test_full_original_commandline_input_provenance_reaches_tokenizer(self):
        p=verify(self.rows)["original_win16_lpCmdLine_near_copy"]
        self.assertEqual(p["mfc_lpCmdLine_argument_forwarded"],
                         "3:0084 -> 3:0088")
        self.assertEqual(p["application_parser_entry"],"3:1118")
        self.assertEqual(p["near_copy_call"],"3:1136 -> 2:6C3C")
        self.assertEqual(p["far_strlen_call"],"2:6C4C -> 2:7344")
        self.assertEqual(p["near_heap_alloc"],"2:6C5A -> 2:5AB0 (LocalAlloc)")
        self.assertEqual(p["far_to_near_copy"],"2:6C6D -> 2:735E")
        self.assertEqual(p["first_tokenizer_call"],"3:1141 -> 2:6B06")
        self.assertEqual(p["subsequent_token_cursor"],"DS:0A8E (written by 2:6B06)")
        self.assertFalse(p["local_literal_128_length_guard"])

    def test_original_near_allocation_uses_dynamic_source_length_not_128(self):
        report=verify(self.rows)
        self.assertTrue(report["original_commandline_copy_uses_dynamic_strlen_plus_one"])
        self.assertFalse(report["game_locally_enforces_128_char_limit_in_command_copy"])
        self.assertEqual(original_commandline_near_copy_request_bytes(0),1)
        self.assertEqual(original_commandline_near_copy_request_bytes(128),129)
        self.assertEqual(original_commandline_near_copy_request_bytes(4096),4097)
        self.assertEqual(original_commandline_near_copy_request_bytes(65534),65535)
        with self.assertRaisesRegex(ValueError,"overflowing"):
            original_commandline_near_copy_request_bytes(65535)
        with self.assertRaisesRegex(ValueError,"overflowing"):
            original_commandline_near_copy_request_bytes(-1)

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
        rows[0]=copy.deepcopy(rows[1])
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
