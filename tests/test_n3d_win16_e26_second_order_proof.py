#!/usr/bin/env python3
"""Synthetic tests for archived Win16 E26 second-order direct caller census."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_win16_e26_second_order_proof import (
    load_ledger,audit,EXPECTED_GROUPS,EXPECTED_INNER,
    NEAR_TRIO_WRAPPER,NEAR_STRLEN_WRAPPER,RESOURCE_LOADSTRING_MAX,
    RESOURCE_LOADSTRING_CALL,POTENTIALLY_DANGEROUS_MIN_LENGTH,
)


class Win16E26DirectUpstreamPaths(unittest.TestCase):
    def setUp(self):
        self.rows=load_ledger()

    def test_all_ten_second_order_xrefs_are_typed_not_runtime_inferred(self):
        report=audit(self.rows)
        self.assertEqual(report["second_order_sites_in_known_original_direct_graph"],10)
        self.assertEqual(report["source_trio_second_order_sites"],6)
        self.assertEqual(report["source_strlen_second_order_sites"],4)
        self.assertEqual(len(EXPECTED_GROUPS[NEAR_TRIO_WRAPPER]),6)
        self.assertEqual(len(EXPECTED_GROUPS[NEAR_STRLEN_WRAPPER]),4)
        self.assertEqual(sum(len(x) for x in EXPECTED_GROUPS.values()),10)
        self.assertEqual(set(EXPECTED_INNER),set(EXPECTED_GROUPS))

    def test_two_immediate_wrapper_calls_differ_in_length_semantics(self):
        report=audit(self.rows)
        wrappers=report["e26_direct_wrappers"]
        self.assertEqual(wrappers["1000:0E7B"]["caller"],"1000:0E6A")
        self.assertEqual(wrappers["1000:0E7B"]["n"],"source_trio.used")
        self.assertEqual(wrappers["1000:0EAB"]["caller"],"1000:0E88")
        self.assertIn("strlen",wrappers["1000:0EAB"]["n"])

    def test_resource_path_is_originally_bounded_by_loadstring(self):
        report=audit(self.rows)
        self.assertEqual(RESOURCE_LOADSTRING_CALL,"1000:3275")
        self.assertEqual(RESOURCE_LOADSTRING_MAX,255)
        self.assertTrue(report["third_direct_caller_excludes_32768"])
        self.assertLess(RESOURCE_LOADSTRING_MAX,POTENTIALLY_DANGEROUS_MIN_LENGTH)

    def test_ten_source_paths_retain_open_large_input_status(self):
        report=audit(self.rows)
        self.assertFalse(report["reachability_of_n_ge_32768_proven"])
        self.assertFalse(report["other_two_direct_wrapper_input_32768_excluded"])
        self.assertFalse(report["complete_dynamic_e26_callgraph_proven"])
        self.assertFalse(report["original_1_10_SHA_reverified_in_this_pass"])
        self.assertEqual(report["underlying_target_memory_interval_if_no_realloc_at_n32768"],{
            "first":"DS:0584","last":"DS:8583","clock_flag":"DS:46B2"
        })
        for row in self.rows:
            self.assertFalse(row["upper_bound_characters_verified"])
            self.assertEqual(row["excludes_unsigned_n_ge_8000"],"false")

    def test_all_near_strlen_xrefs_have_source_termination_obligation(self):
        r=[x for x in self.rows if x["target_wrapper"]==NEAR_STRLEN_WRAPPER]
        self.assertEqual(len(r),4)
        self.assertTrue(all("strlen" in x["n_source"] for x in r))
        self.assertEqual({x["callsite"] for x in r},
                         {"1000:A407","1000:A8E7","1008:1430","1008:15F7"})

    def test_all_source_trio_xrefs_load_used_word_plus_2(self):
        r=[x for x in self.rows if x["target_wrapper"]==NEAR_TRIO_WRAPPER]
        self.assertEqual(len(r),6)
        self.assertTrue(all("used" in x["n_source"] and "+2" in x["n_source"] for x in r))
        self.assertEqual({x["callsite"] for x in r},
                         {"1000:4FF9","1000:69DF","1000:A3F6",
                          "1000:A577","1008:16CA","1008:16E7"})

    def test_do_not_bound_earlier_source_by_later_getfiletitle(self):
        row=next(x for x in self.rows if x["callsite"]=="1008:15F7")
        self.assertIn("GETFILETITLE(256)",row["next_static_obligation"])
        self.assertFalse(row["upper_bound_characters_verified"])
        self.assertEqual(row["target_wrapper"],NEAR_STRLEN_WRAPPER)

    def test_missing_or_duplicate_direct_callers_rejected(self):
        with self.assertRaisesRegex(ValueError,"requires 10"):
            audit(self.rows[:-1])
        bad=copy.deepcopy(self.rows)
        bad[0]=copy.deepcopy(bad[1])
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            audit(bad)

    def test_forged_upper_bound_is_rejected_not_promoted_to_closed(self):
        bad=copy.deepcopy(self.rows)
        bad[0]["upper_bound_characters_verified"]="255"
        with self.assertRaisesRegex(ValueError,"invented"):
            audit(bad)
        bad=copy.deepcopy(self.rows)
        bad[1]["excludes_unsigned_n_ge_8000"]="true"
        with self.assertRaisesRegex(ValueError,"Cannot exclude"):
            audit(bad)

    def test_source_trio_used_word_invariant_is_checked(self):
        bad=copy.deepcopy(self.rows)
        row=next(x for x in bad if x["callsite"]=="1000:A3F6")
        row["n_source"]="row length"
        with self.assertRaisesRegex(ValueError,"used-word"):
            audit(bad)

    def test_wrapper_and_original_inner_site_mutation_rejected(self):
        bad=copy.deepcopy(self.rows)
        bad[0]["E26_direct_inner_callsite"]="1000:3275"
        with self.assertRaisesRegex(ValueError,"inner direct"):
            audit(bad)
        bad=copy.deepcopy(self.rows)
        bad[0]["target_wrapper"]=NEAR_STRLEN_WRAPPER
        with self.assertRaisesRegex(ValueError,"wrapper"):
            audit(bad)


if __name__=="__main__":
    unittest.main()
