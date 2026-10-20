#!/usr/bin/env python3
"""Synthetic raw-byte candidate scanner tests. Never claims CFG reachability."""
from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from n3d_win16_raw_fixed_store_candidates import (
    scan_bytes, audit_image, overlapping_sources
)


class FakeNEImage:
    def __init__(self, code: bytes):
        self.raw = {
            3: code,
            7: bytes.fromhex("a2 b2 46 c7 06 b1 46 00 00")
        }
        self.segments = [
            SimpleNamespace(number=3,file_offset=0x1000,flags=0x1D50,
                            length=len(code)),
            SimpleNamespace(number=7,file_offset=0x2000,flags=0x0D51,
                            length=len(self.raw[7])),
        ]

    def bytes_at(self, seg, begin, end):
        return self.raw[seg][begin:end]


def fixture():
    b=bytearray(b"\x90"*0x500)
    # A2 true byte writer to clock
    b[0x100:0x103] = bytes.fromhex("A2 B2 46")
    # WORD writes starting at B1 would also touch clock B2
    b[0x120:0x126] = bytes.fromhex("C7 06 B1 46 01 00")
    # DWORD writes starting at AF would span AF/B0/B1/B2
    b[0x140:0x144] = bytes.fromhex("66 A3 AF 46")
    # A BYTE write at B1 does NOT touch clock B2
    b[0x160:0x165] = bytes.fromhex("C6 06 B1 46 01")
    # CMP reads the clock byte but must not be called a writer
    b[0x180:0x185] = bytes.fromhex("80 3E B2 46 00")
    # Group1 ADD [B2], imm8 writes clock
    b[0x1A0:0x1A5] = bytes.fromhex("80 06 B2 46 01")
    # DWORD group1 RMW at B0 can overlap clock
    b[0x1C0:0x1C9] = bytes.fromhex("66 81 06 B0 46 00 00 00 00")
    # A directly stored latch byte at A2
    b[0x200:0x203] = bytes.fromhex("A2 A2 00")
    return bytes(b)


class RawClockScanTests(unittest.TestCase):

    def test_raw_sites_include_byte_word_and_dword_candidates(self):
        found=scan_bytes(fixture(),segment=3,target=0x46B2)
        matched={v['source'] for v in found}
        self.assertTrue({'3:0100','3:0120','3:0140','3:01A0','3:01C0'} <= matched)
        for hit in found:
            self.assertEqual(hit['evidence'],'RAW_PATTERN_ONLY_NOT_CFG_CONFIRMED')

    def test_neighbor_byte_not_clock_writing(self):
        found=scan_bytes(fixture(),segment=3,target=0x46B2)
        matched={v['source'] for v in found}
        self.assertNotIn('3:0160',matched)
        self.assertNotIn('3:0180',matched)

    def test_latch_direct_moffs8_candidate(self):
        found=scan_bytes(fixture(),segment=3,target=0x00A2)
        self.assertIn('3:0200',{v['source'] for v in found})

    def test_data_segments_ignored(self):
        img=FakeNEImage(fixture())
        result=audit_image(img,0x46B2)
        self.assertEqual(result['file_backed_code_segments_scanned'],[3])
        self.assertFalse(result['all_candidates_are_instruction_boundary_validated'])
        self.assertFalse(result['register_based_or_alias_writes_excluded'])

    def test_width_boundaries_include_all_four_possible_dword_starts(self):
        self.assertEqual(list(overlapping_sources(0x46B2,4)),
                         [0x46AF,0x46B0,0x46B1,0x46B2])
        self.assertEqual(list(overlapping_sources(0x00A2,2)),[0x00A1,0x00A2])


if __name__=="__main__":
    unittest.main()
