#!/usr/bin/env python3
"""Synthetic NE fixtures for the hash-pinned Win16 timer proof extractor."""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ne_renderer_audit import NeImage
from n3d_win16_timer_binary_proof import (
    Profile, PROFILES, candidate_near_calls, disassemble_region,
    find_pinned_original, import_at, inspect, internal_far_relocations,
    iter_zip_exes,
)


def synthetic_ne_bytes() -> bytes:
    # Header at 0x80, NE segment 3 at 0x300, alignment 16 bytes.
    # No original game content is stored in the fixture.
    data = bytearray(0x500)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    ne = 0x80
    data[ne:ne+2] = b"NE"
    struct.pack_into("<H", data, ne+0x1C, 3)      # segment count
    struct.pack_into("<H", data, ne+0x1E, 1)      # module count
    struct.pack_into("<H", data, ne+0x22, 0x40)   # segment table
    struct.pack_into("<H", data, ne+0x28, 0x5C)   # module refs
    struct.pack_into("<H", data, ne+0x2A, 0x5E)   # import names
    struct.pack_into("<H", data, ne+0x32, 4)      # alignment shift
    struct.pack_into("<HHHH", data, ne+0x40+2*8,
                     0x30, 0x80, 0x0100, 0x80)   # NE segment 3
    struct.pack_into("<H", data, ne+0x5C, 0)
    data[ne+0x5E:ne+0x5E+9] = b"\x08MMSYSTEM"
    base = 0x300
    # synthetic FAR CALL, word relocated to MMSYSTEM ordinal 606
    data[base+0x10:base+0x15] = b"\x9A\xFF\xFF\x00\x00"
    # synthetic NEAR CALL from 3:0030 to 3:0010
    data[base+0x30:base+0x33] = b"\xE8\xDD\xFF"
    # ADDITIVE imported ordinal fixup (source_offset = opcode+1)
    struct.pack_into("<H", data, base+0x80, 1)
    struct.pack_into("<BBHHH", data, base+0x82, 3, 5, 0x11, 1, 606)
    return bytes(data)


class TimerBinaryProofTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name, "synthetic.exe")
        self.data = synthetic_ne_bytes()
        self.file.write_bytes(self.data)
        self.image = NeImage(self.file)

    def test_ne_segment_alignment_and_import_fixup(self):
        seg = self.image.segment(3)
        self.assertEqual((seg.file_offset, seg.length), (0x300, 0x80))
        self.assertEqual(seg.flags & 0x0100, 0x0100)
        call = import_at(self.image, 0x10, "MMSYSTEM", 606)
        self.assertTrue(call["opcode_far_call_9a"])
        self.assertTrue(call["verified"])
        self.assertEqual(call["relocation_matches"][0]["source"], "3:0011")
        self.assertFalse(import_at(self.image, 0x10, "MMSYSTEM", 605)["verified"])

    def test_near_candidate_is_not_claimed_reachable(self):
        self.assertEqual(candidate_near_calls(self.image, 3, 0x10), ["3:0030"])
        self.assertEqual(candidate_near_calls(self.image, 3, 0x11), [])
        self.assertEqual(internal_far_relocations(self.image, 3, 0x10), [])

    def test_disassembly_and_relocation_annotation(self):
        lines = disassemble_region(self.image, 3, 0x10, 0x15)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["address"], "3:0010")
        self.assertEqual(lines[0]["mnemonic"], "lcall")
        self.assertEqual(lines[0]["relocations"], ["import MMSYSTEM ordinal 606"])

    def test_original_hash_guard(self):
        with self.assertRaisesRegex(ValueError, "No hash-pinned"):
            find_pinned_original(self.file)

    def test_pinned_profiles_have_expected_unique_hashes(self):
        self.assertEqual(len(PROFILES), 5)
        self.assertEqual(len({p.sha256 for p in PROFILES}), 5)
        for p in PROFILES:
            self.assertEqual(len(p.sha256), 64)
            self.assertEqual(len(p.imports), 5)
            self.assertEqual([ordinal for _, _, ordinal in p.imports],
                             [604, 605, 606, 607, 13])
            self.assertEqual(p.read_time - p.timer_init, 0x5A)
            self.assertGreater(p.seg3_length, p.read_time + 5)

    def test_synthetic_zip_and_nested_zip(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("foo/SYNTHETIC.EXE", self.data)
        items = list(iter_zip_exes(buffer.getvalue(), "outer.zip"))
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0][0].endswith("foo/SYNTHETIC.EXE"))
        self.assertEqual(items[0][1], self.data)

        wrapper = io.BytesIO()
        with zipfile.ZipFile(wrapper, "w") as z:
            z.writestr("deep.zip", buffer.getvalue())
        nested = list(iter_zip_exes(wrapper.getvalue(), "wrapper.zip"))
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0][1], self.data)

    def test_synthetic_report_without_bypassing_sha_guard(self):
        # inspect() is unit-tested with a fake profile on synthetic bytes.
        # Public CLI still requires a real sha-pinned original build.
        profile = Profile(
            version="SYNTHETIC",
            sha256=hashlib.sha256(self.data).hexdigest(),
            raw_size=len(self.data),
            seg3_file_offset=0x300,
            seg3_length=0x80,
            timer_init=0x10,
            read_time=0x15,
            imports=((0x10, "MMSYSTEM", 606),),
        )
        report = inspect(self.image, profile)
        self.assertEqual(report["timer_init"], "3:0010")
        self.assertEqual(report["candidate_near_E8_xrefs_to_timer_init"],
                         ["3:0030"])
        self.assertEqual(len(report["verified_import_anchors"]), 1)


if __name__ == "__main__":
    unittest.main()
