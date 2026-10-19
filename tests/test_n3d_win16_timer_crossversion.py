#!/usr/bin/env python3
"""Regression: precise cross-build timer evidence never upgrades hypothesis to proof."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from n3d_win16_timer_crossversion_verify import (
    ANCHORS, IMPORTS, SEGMENTS, analyze, load_rows, EXPECTED_DELTA,
)


class CrossVersionTimerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchors = load_rows(ANCHORS)
        cls.imports = load_rows(IMPORTS)
        cls.segments = load_rows(SEGMENTS)

    def test_four_prefixes_and_five_fixup_anchors(self):
        proof = analyze(self.anchors, self.imports, self.segments)
        self.assertEqual(proof["offset_displacement"], "+0xAE")
        self.assertEqual(proof["matched_16_byte_prefixes"], 4)
        self.assertEqual(proof["matched_prefix_bytes_total"], 64)
        self.assertEqual(proof["matched_import_callsite_offsets"], 5)
        self.assertEqual(
            {r["function"] for r in proof["equal_function_prefixes"]},
            {"read_time", "slow_clock", "frame_clock", "calibrate"})
        self.assertEqual(
            {r["api"] for r in proof["import_relocation_sites"]},
            {"MMSYSTEM.604", "MMSYSTEM.605", "MMSYSTEM.606",
             "MMSYSTEM.607", "USER.13"})

    def test_full_ne3_not_claimed_equal(self):
        proof = analyze(self.anchors, self.imports, self.segments)
        left = proof["ne3_layout"]["win18"]
        right = proof["ne3_layout"]["win110"]
        self.assertEqual(left["raw_file_offset"], 90016)
        self.assertEqual(right["raw_file_offset"], 90048)
        self.assertNotEqual(left["segment_sha256"], right["segment_sha256"])
        self.assertFalse(proof["win110_stack_operand_closed"])
        self.assertFalse(proof["win110_near_far_indirect_callgraph_closed"])
        self.assertIsNone(proof["timer_endperiod_operand_win110"])

    def test_mutated_prefix_rejected(self):
        rows = copy.deepcopy(self.anchors)
        target = next(r for r in rows if
                      r["Win16_version"] == "1.10" and r["behavior"] == "read_time")
        target["first_16_bytes"] = "00 " + target["first_16_bytes"][3:]
        with self.assertRaisesRegex(ValueError, "First 16 bytes mismatch"):
            analyze(rows, self.imports, self.segments)

    def test_bad_fixup_offset_rejected(self):
        rows = copy.deepcopy(self.imports)
        target = next(r for r in rows if
                      r["Win16_version"] == "1.10" and
                      r["import_module"] == "MMSYSTEM" and
                      r["import_ordinal"] == "606")
        target["caller_ip"] = "0xD6BF"
        with self.assertRaisesRegex(ValueError, "Imported API site displacement"):
            analyze(self.anchors, rows, self.segments)

    def test_calibration_displacement(self):
        proof = analyze(self.anchors, self.imports, self.segments)
        cal = next(r for r in proof["equal_function_prefixes"] if
                   r["function"] == "calibrate")
        self.assertEqual(int(cal["win110"][2:], 16) -
                         int(cal["win18"][2:], 16), EXPECTED_DELTA)


if __name__ == "__main__":
    unittest.main()
