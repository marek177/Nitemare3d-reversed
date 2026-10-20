#!/usr/bin/env python3
"""Prove only bounded direct constant-DS writer widths and overlap gates.

Fixtures come from pre-existing Ghidra Win16 1.10 ASM XREF and mnemonics;
no new original game EXE is distributed/executed by these synthetic tests.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from n3d_win16_clock_alias_writes import (
    DirectWitness, EXPECTED_CLOCK_DIRECT_WRITERS, EXPECTED_NEIGHBOR_WRITERS,
    LATCH, CLOCK, load_manifest, instruction_width, audit,
)


class ClockAliasDirectWriters(unittest.TestCase):

    def setUp(self):
        self.witnesses = load_manifest()

    def test_archived_original_witnesses_identify_direct_writers_only(self):
        result = audit(self.witnesses)
        self.assertEqual(result["recorded_witnesses"], 10)
        self.assertEqual(set(result["clock_direct_writer_sites"]),
                         EXPECTED_CLOCK_DIRECT_WRITERS)
        self.assertEqual(set(result["neighbor_direct_writer_sites"]),
                         EXPECTED_NEIGHBOR_WRITERS)
        self.assertEqual(result["one_shot_direct_writer_sites"], ["3:0ECA"])
        self.assertEqual(
            result["neighbor_direct_writes_proven_not_to_overlap_clock"], 7)
        self.assertEqual(result["direct_neighbor_write_overlaps_clock"], [])
        self.assertTrue(result["direct_witness_manifest_consistent"])

    def test_proof_does_not_claim_indirect_alias_completeness(self):
        result = audit(self.witnesses)
        self.assertFalse(result["complete_original_1_10_ne_image_scanned"])
        self.assertFalse(result["computed_address_aliases_ruled_out"])
        self.assertFalse(result["interprocedural_memcpy_or_rep_stos_ruled_out"])
        self.assertFalse(result["full_runtime_writer_graph_closed"])

    def test_encoded_widths_exact_and_nonoverlapping(self):
        for x in self.witnesses:
            self.assertEqual(instruction_width(x), x.width)
        for x in self.witnesses:
            if x.absolute_ds_address < CLOCK and x.absolute_ds_address >= 0x46AF:
                self.assertEqual(x.width, 1)
                self.assertFalse(x.overlaps(CLOCK))

    def test_word_writer_at_b1_would_overlap_clock(self):
        injected = DirectWitness(
            "1.10", 3, 0x9000, 0x46B1, 2,
            bytes.fromhex("C7 06 B1 46 01 00"),
            "synthetic_overlapping_word", "SYNTHETIC")
        self.assertTrue(injected.overlaps(CLOCK))
        report = audit(self.witnesses + [injected],
                       strict_original_manifest=False)
        self.assertEqual(
            report["direct_neighbor_write_overlaps_clock"][0]["site"], "3:9000")
        self.assertFalse(report["direct_witness_manifest_consistent"])
        with self.assertRaisesRegex(ValueError, "census diverged"):
            audit(self.witnesses + [injected])

    def test_dword_writer_at_af_would_overlap_clock(self):
        injected = DirectWitness(
            "1.10", 3, 0x9001, 0x46AF, 4,
            bytes.fromhex("66 A3 AF 46"), "synthetic_dword", "SYNTHETIC")
        self.assertEqual(instruction_width(injected), 4)
        self.assertTrue(injected.overlaps(CLOCK))
        with self.assertRaisesRegex(ValueError, "census diverged"):
            audit(self.witnesses + [injected])

    def test_dword_writer_at_b0_would_overlap_clock(self):
        injected = DirectWitness(
            "1.10", 3, 0x9002, 0x46B0, 4,
            bytes.fromhex("66 C7 06 B0 46 00 00 00 00"),
            "synthetic_dword", "SYNTHETIC")
        self.assertEqual(instruction_width(injected), 4)
        self.assertEqual(injected.last_byte, 0x46B3)
        self.assertTrue(injected.overlaps(CLOCK))

    def test_byte_writer_at_b1_does_not_overlap_clock(self):
        injected = DirectWitness(
            "1.10", 3, 0x9003, 0x46B1, 1,
            bytes.fromhex("C6 06 B1 46 01"), "synthetic_byte", "SYNTHETIC")
        self.assertFalse(injected.overlaps(CLOCK))

    def test_absolute_latch_writer_exactly_one(self):
        a = [w for w in self.witnesses if w.overlaps(LATCH)]
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].source, "3:0ECA")
        self.assertEqual(a[0].raw_opcode, bytes.fromhex("A2 A2 00"))

    def test_unknown_encoding_does_not_silently_infer_width(self):
        altered = replace(self.witnesses[0],
                          raw_opcode=bytes.fromhex("90 90 90"))
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            audit([altered], strict_original_manifest=False)

    def test_mismatched_width_rejected(self):
        altered = replace(self.witnesses[0], width=2)
        with self.assertRaisesRegex(ValueError, "Recorded instruction width"):
            audit([altered] + self.witnesses[1:],
                  strict_original_manifest=False)

    def test_duplicate_witness_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit(self.witnesses + [self.witnesses[0]])

    def test_empty_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "Empty"):
            audit([])


if __name__ == "__main__":
    unittest.main()
