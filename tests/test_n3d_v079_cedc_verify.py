"""Synthetic-only DOS v2.0 CEDC signed32/16 arithmetic regression, no assets."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import n3d_v079_cedc_verify as v

CASE_BASE = dict(session="synthetic",first_event="1",last_event="2",
                 x="308",orientation="0",branch_fourway="selector1_horizontal",
                 center_x="160",span="337",inverse_scale="459074",
                 vertical_numerator="0",product32="-221544",
                 trig_divisor="-724",caller_local16="27",
                 caller_negates_u="True",
                 partial_original_result="201611",final_original_num="-19933",
                 cedc_quotient_original="27",returned_ax="27",
                 caller_pre_edge_u="65482",
                 cached_2643_product32="-221544",
                 cached_2603_2620_local16="27")

class CedcTests(unittest.TestCase):
    def test_original_selector1_horizontal(self):
        x=v.perspective(CASE_BASE)
        self.assertEqual(x["ax"],27)
        self.assertEqual(x["raw_u_before_22ca"],65482)
        self.assertEqual(x["partial"],201611)

    def test_original_selector1_vertical(self):
        r=CASE_BASE | dict(x="8",orientation="3",span="633",
            branch_fourway="selector1_vertical",vertical_numerator="81715200",
            product32="119460",inverse_scale="0",trig_divisor="-724",
            caller_local16="65522",caller_negates_u="False")
        x=v.perspective(r)
        self.assertEqual((x["partial"],x["combined"],x["quotient"]),
                         (129091,9631,-13))
        self.assertEqual(x["raw_u_before_22ca"],65509)

    def test_original_selector0_horizontal(self):
        r=CASE_BASE | dict(x="8",orientation="0",span="2132",
            branch_fourway="selector0_horizontal",
            vertical_numerator="81715200",product32="0",
            trig_divisor="-1024",caller_local16="96",inverse_scale="0",
            caller_negates_u="True")
        x=v.perspective(r)
        self.assertEqual((x["partial"],x["combined"],x["quotient"]),
                         (38327,38327,-37))
        self.assertEqual(x["raw_u_before_22ca"],65477)

    def test_original_selector0_vertical(self):
        r=CASE_BASE | dict(x="102",orientation="2",span="831",
            branch_fourway="selector0_vertical",product32="0",
            trig_divisor="-1024",caller_local16="65504",
            caller_negates_u="False")
        x=v.perspective(r)
        self.assertEqual((x["partial"],x["combined"],x["quotient"]),
                         (-32041,32041,-31))
        self.assertEqual(x["raw_u_before_22ca"],65473)

    def test_8086_subtract16_wrap(self):
        r=CASE_BASE | dict(x="-32768",center_x="32767",span="2",
            inverse_scale="10",product32="0",trig_divisor="1",
            caller_local16="0",caller_negates_u="False")
        self.assertEqual(v.perspective(r)["partial"],5)

    def test_32bit_mul_wrap(self):
        r=CASE_BASE | dict(x="260",center_x="160",span="1",
            inverse_scale="2147483647",product32="0",trig_divisor="1",
            caller_local16="0",caller_negates_u="False")
        self.assertEqual(v.perspective(r)["partial"],-100)

    def test_original_idiv_truncates_to_zero(self):
        r=CASE_BASE | dict(x="8",orientation="0",span="2",
            branch_fourway="selector0_horizontal",
            vertical_numerator="-7",product32="0",trig_divisor="-2")
        self.assertEqual(v.perspective(r)["partial"],-3)
        self.assertEqual(v.perspective(r)["quotient"],1)

    def test_zero_denominator_is_rejected(self):
        with self.assertRaises(ValueError):
            v.perspective(CASE_BASE | dict(span="0"))
        with self.assertRaises(ValueError):
            v.perspective(CASE_BASE | dict(trig_divisor="0"))

    def test_signed_idiv_int32_min_negative_one_overflow(self):
        r=CASE_BASE | dict(x="160",span="1",inverse_scale="0",
                           product32="-2147483648",trig_divisor="-1")
        with self.assertRaises(ValueError):
            v.perspective(r)

    def test_mutated_original_row_must_fail(self):
        r=CASE_BASE | dict(cedc_quotient_original="28")
        with self.assertRaisesRegex(ValueError,"Original CEDC mismatch"):
            v.verify([r]*1808)

    def test_unknown_branch_fails(self):
        with self.assertRaises(ValueError):
            v.perspective(CASE_BASE | dict(branch_fourway="guess"))

    def test_sha_guard_denies_pretend_original(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"pretend-original.csv"
            p.write_bytes(b"session,x\nsynthetic,8\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                v.load_corpus(p,v.CEDC_SHA)

if __name__=="__main__":
    unittest.main()
