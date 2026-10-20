#!/usr/bin/env python3
"""Synthetic regression of recovered Win16 1.10 Ghidra timer opcode manifest.

These tests do NOT access the original game EXE and MUST NOT claim that
the v1.10 SHA was verified during this CI execution.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from ne_renderer_audit import Relocation
from n3d_win16_timer_binary_proof import (
    WIN110_TIMER_ARCHIVED_ANCHORS,
    verify_win110_timer_call_and_stack,
)


class SyntheticWin110NEImage:
    """Synthetic NE3 byte view, filled with NOPs outside archived anchors."""

    def __init__(self):
        self.raw = bytearray(b"\x90" * 0xE000)
        for ip, hex_bytes in WIN110_TIMER_ARCHIVED_ANCHORS.items():
            blob = bytes.fromhex(hex_bytes)
            self.raw[ip:ip + len(blob)] = blob
        self.relocations = [
            Relocation(3, 0x0F37, 2, 4, "internal 3:D66C"),
            Relocation(3, 0x0F73, 2, 4, "internal 3:D66C"),
            Relocation(3, 0xD686, 3, 5, "import MMSYSTEM ordinal 604"),
            Relocation(3, 0xD6AC, 3, 5, "import MMSYSTEM ordinal 605"),
            Relocation(3, 0xD6BF, 3, 5, "import MMSYSTEM ordinal 606"),
        ]

    def bytes_at(self, segment, start, end):
        if segment != 3 or not 0 <= start <= end <= len(self.raw):
            raise ValueError("out of synthetic NE3")
        return bytes(self.raw[start:end])

    def file_offset(self, segment, ip):
        if segment != 3:
            raise ValueError("not synthetic NE3")
        return 0x1000 + ip

    def relocation_map(self, segment):
        return {
            r.source_offset: r for r in self.relocations if r.segment == segment
        }


class Win110ArchivedOpcodes(unittest.TestCase):

    def setUp(self):
        self.image = SyntheticWin110NEImage()

    def test_archived_opcode_facts_synthetic(self):
        result = verify_win110_timer_call_and_stack(self.image)
        self.assertEqual(result["proof"], "SYNTHETIC_OPCODE_MODEL_ONLY")
        self.assertEqual(result["init_immediate_argument"], 0)
        self.assertEqual(result["cleanup_immediate_argument"], 1)
        self.assertEqual(result["local_frame_bytes"], 6)
        self.assertEqual(result["end_period_push"], "WORD PTR SS:[BP-2]")
        self.assertEqual(result["checked_timer_imports"], 3)
        self.assertFalse(result["end_period_local_initialized"])
        self.assertEqual(result["bp_minus_2_references"][0]["address"], "3:D6BB")
        self.assertIn("3:0F37", result["verified_internal_far_relocation_sources"])
        self.assertIn("3:0F73", result["verified_internal_far_relocation_sources"])

    def test_mutated_end_period_operand_rejected(self):
        self.image.raw[0xD6BB] = 0x90
        with self.assertRaisesRegex(ValueError, "3:D6BB"):
            verify_win110_timer_call_and_stack(self.image)

    def test_mutated_init_immediate_rejected(self):
        self.image.raw[0x0F33] = 1
        with self.assertRaisesRegex(ValueError, "3:0F32"):
            verify_win110_timer_call_and_stack(self.image)

    def test_missing_caller_relocation_rejected(self):
        self.image.relocations = [
            r for r in self.image.relocations if r.source_offset != 0x0F37
        ]
        with self.assertRaisesRegex(ValueError, "direct FAR-caller fixups"):
            verify_win110_timer_call_and_stack(self.image)

    def test_mismatched_cleanup_import_rejected(self):
        self.image.relocations = [
            r for r in self.image.relocations if r.source_offset != 0xD6BF
        ]
        with self.assertRaisesRegex(ValueError, "MMSYSTEM import fixups"):
            verify_win110_timer_call_and_stack(self.image)

    def test_manifest_has_no_unspecified_magic_original_exe(self):
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0x0E9E], "80 3e a2 00 00")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0x0ECA], "a2 a2 00")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0x0ED6], "a2 b2 46")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0xD66C], "c8 06 00 00")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0xD6BB], "ff 76 fe")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0x0F32], "6a 00")
        self.assertEqual(WIN110_TIMER_ARCHIVED_ANCHORS[0x0F6E], "6a 01")
        self.assertGreaterEqual(len(WIN110_TIMER_ARCHIVED_ANCHORS), 40)


if __name__ == "__main__":
    unittest.main()
