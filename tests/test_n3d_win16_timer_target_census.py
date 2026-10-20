#!/usr/bin/env python3
"""Synthetic boundary checks for NE3:D66C direct-vs-indirect call classification.

No original NITE3W.EXE is distributed or executed.
"""
from __future__ import annotations

import struct
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ne_renderer_audit import Relocation
from n3d_win16_timer_target_census import (
    reference_sites, raw_e8_candidates, audit, assert_known_win110_direct_callers
)


class SyntheticNE:
    def __init__(self):
        self.buffers = {3: bytearray(b"\x90" * 0xE000),
                        4: bytearray(b"\x00" * 0x100)}
        code = self.buffers[3]
        # NE relocated selector words are at CALL+3.
        code[0x0F34:0x0F39] = b"\x9a\x6c\xd6\x00\x00"
        code[0x0F70:0x0F75] = b"\x9a\x6c\xd6\x00\x00"
        # Code-segment address-taken pointer, not a FAR CALL.
        code[0x0520:0x0525] = b"\x68\x6c\xd6\x00\x00"
        # Direct FAR JMP (not CALL).
        code[0x0620:0x0625] = b"\xea\x6c\xd6\x00\x00"
        # A possible raw E8 displacement byte sequence, without CFG context.
        raw_ip = 0x0700
        offset = ((0xD66C - raw_ip - 3 + 0x8000) & 0xFFFF) - 0x8000
        code[raw_ip:raw_ip+3] = b"\xe8" + struct.pack("<h", offset)
        data = self.buffers[4]
        data[0x20:0x24] = b"\x6c\xd6\x00\x00"

        self.relocations = [
            Relocation(3, 0x0F37, 2, 4, "internal 3:D66C"),
            Relocation(3, 0x0F73, 2, 4, "internal 3:D66C"),
            Relocation(3, 0x0523, 2, 4, "internal 3:D66C"),
            Relocation(3, 0x0623, 2, 4, "internal 3:D66C"),
            Relocation(4, 0x0022, 2, 4, "internal 3:D66C"),
            Relocation(3, 0x0813, 2, 4, "internal 3:1234"),
        ]

    def segment(self, segment):
        return SimpleNamespace(file_offset=0x1000, length=len(self.buffers[segment]),
                               flags=0x1D51 if segment == 4 else 0x1D50)

    def bytes_at(self, segment, start, end):
        if not 0 <= start <= end <= len(self.buffers[segment]):
            raise ValueError("out of bounds")
        return bytes(self.buffers[segment][start:end])


class TimerTargetCensusTests(unittest.TestCase):

    def setUp(self):
        self.image = SyntheticNE()

    def test_direct_xrefs_and_indirect_far_data_are_separate(self):
        result = audit(self.image)
        self.assertEqual(result["target"], "3:D66C")
        self.assertEqual(result["expanded_internal_relocations_to_target"], 5)
        self.assertEqual(result["direct_far_call_sites"], ["3:0F34", "3:0F70"])
        self.assertEqual(result["direct_far_jump_sites"], ["3:0620"])
        self.assertEqual(result["classes"]["DIRECT_FAR_CALL"], 2)
        self.assertEqual(result["classes"]["DIRECT_FAR_JUMP"], 1)
        self.assertEqual(result["classes"]["DATA_FAR_POINTER"], 1)
        self.assertEqual(result["classes"]["ADDRESS_TAKEN_OR_UNKNOWN"], 1)
        self.assertEqual(len(result["non_direct_fixups_requiring_pointer_flow"]), 2)
        self.assertFalse(result["all_runtime_indirect_calls_excluded"])
        assert_known_win110_direct_callers(result)

    def test_unaligned_raw_e8_is_not_upgraded_to_resolved_call(self):
        result = audit(self.image)
        self.assertIn("3:0700", result["raw_e8_near_call_candidates_unverified"])
        self.assertNotIn("3:0700", result["direct_far_call_sites"])

    def test_direct_far_jump_not_counted_as_call(self):
        refs = reference_sites(self.image)
        jump = next(x for x in refs if x.fixup_offset == 0x0623)
        self.assertEqual(jump.kind, "DIRECT_FAR_JUMP")
        self.assertEqual(jump.instruction_address, "3:0620")

    def test_removed_original_init_call_rejected(self):
        self.image.relocations = [
            r for r in self.image.relocations if r.source_offset != 0x0F37
        ]
        with self.assertRaisesRegex(ValueError, "3:0F34"):
            assert_known_win110_direct_callers(audit(self.image))

    def test_mutated_opcode_downgrades_call_to_address_taken(self):
        self.image.buffers[3][0x0F34] = 0x90
        result = audit(self.image)
        self.assertEqual(result["direct_far_call_sites"], ["3:0F70"])
        unknown = next(r for r in result["all_target_fixups"]
                       if r["source"] == "3:0F37")
        self.assertEqual(unknown["kind"], "ADDRESS_TAKEN_OR_UNKNOWN")

    def test_mutated_far_offset_marks_suspicious(self):
        self.image.buffers[3][0x0F35:0x0F37] = b"\x00\x00"
        classes = audit(self.image)["classes"]
        self.assertEqual(classes["SUSPICIOUS_TARGET_OPERAND_MISMATCH"], 1)

    def test_explicit_unknown_fixup_target_is_not_merged(self):
        other = next(r for r in self.image.relocations
                     if r.target == "internal 3:1234")
        self.assertEqual(other.source_offset, 0x0813)
        self.assertFalse(any(r.fixup_offset == other.source_offset
                             for r in reference_sites(self.image)))


if __name__ == "__main__":
    unittest.main()
