#!/usr/bin/env python3
"""Synthetic-only tests of the original EXE signature validator.

Synthetic bytes are not a real DOS executable; positive reference tests exercise
parser structure, and negatives ensure opcode/target mutations fail closed.
"""
import struct
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_v069_guard_world_alias_check as audit  # noqa: E402


def fixture(build):
    c = audit.BUILDS[build]
    raw = bytearray(b"\x00" * (0x200 + 0x1C600))
    raw[:2] = b"MZ"
    struct.pack_into("<H", raw, 8, 0x20)
    b = memoryview(raw)[512:]

    def put(off, sig):
        b[off:off+len(sig)] = sig

    put(c["clear"], audit.CLEAR)
    put(c["dispatcher"], audit.HEAD)
    put(c["dispatcher"] + 0x2C, audit.SPECIAL)
    put(c["dispatcher"] + 0x215, audit.ACCEPT)
    put(c["near"] - 1, bytes.fromhex("0E E8 C3 FD"))
    for i, site in enumerate(c["far"]):
        # Any valid unrelocated FAR pair is allowed, to test decoded targets.
        segment = c["dispatcher"] >> 4
        off = c["dispatcher"] & 15
        put(site, b"\x9A" + struct.pack("<HH", off, segment))
        put(c["gates"][i], b"\xF6\x46"
            + (b"\xFD" if i == 0 else b"\xFC") + b"\x04\x74\x0C")
        put(c["readers"][i],
            b"\x8A\x87" + struct.pack("<H", c["property"]))
    put(c["world_or"], bytes.fromhex("26 80 4C 05 01"))
    put(c["state0a"], bytes.fromhex("26 C6 45 0B 0A"))
    put(c["small"] - 16,
        bytes.fromhex("66 33 C0 8E 06")
        + struct.pack("<H", c["small_es"])
        + bytes.fromhex("66 B9 10 00 00 00 BF FE 36 F3 66 AB"))
    put(c["map"] - 14,
        bytes.fromhex("33 C0 8E 06")
        + struct.pack("<H", c["map_es"])
        + bytes.fromhex("B9 00 10 BF 00 00 D1 E9 F3 AB"))
    put(c["reset"], b"\x89\x36" + struct.pack("<H", c["count"]))
    put(c["inc"], b"\xFF\x06" + struct.pack("<H", c["count"]))
    return raw


class TestV069OriginalStaticSubset(unittest.TestCase):
    def test_dos12_structural_positive_synthetic(self):
        result = audit.verify_blob(fixture("dos12"), "dos12", enforce_sha=False)
        self.assertEqual(result["direct_near_callers"], ["0B51A"])
        self.assertFalse(result["indirect_pointer_and_SAVE_LOAD_aliases_closed"])

    def test_dos20_structural_positive_synthetic(self):
        result = audit.verify_blob(fixture("dos20"), "dos20", enforce_sha=False)
        self.assertEqual(result["collision_wrapper_far_callers"], ["06446", "06458"])
        self.assertFalse(result["original_vs_remake_parity"])

    def test_original_sha_enforced_in_normal_mode(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            audit.verify_blob(fixture("dos20"), "dos20")

    def test_detect_changed_world_cleanup(self):
        data = fixture("dos20")
        data[512 + audit.BUILDS["dos20"]["clear"] + 8] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos20", enforce_sha=False)

    def test_detect_changed_far_collision_target(self):
        data = fixture("dos20")
        data[512 + audit.BUILDS["dos20"]["far"][1] + 2] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos20", enforce_sha=False)

    def test_detect_changed_collision_property_gate(self):
        data = fixture("dos20")
        data[512 + audit.BUILDS["dos20"]["gates"][0] + 3] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos20", enforce_sha=False)

    def test_detect_changed_default_class_cleanup_predicate(self):
        data = fixture("dos12")
        data[512 + audit.BUILDS["dos12"]["dispatcher"] + 0x2C + 7] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos12", enforce_sha=False)

    def test_detect_changed_bulk_stos_width(self):
        data = fixture("dos20")
        data[512 + audit.BUILDS["dos20"]["small"]] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos20", enforce_sha=False)

    def test_detect_changed_guard_count_reset(self):
        data = fixture("dos12")
        data[512 + audit.BUILDS["dos12"]["reset"]] ^= 0x1
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos12", enforce_sha=False)

    def test_detect_collision_caller_swap_that_changes_count(self):
        data = fixture("dos20")
        data[512 + audit.BUILDS["dos20"]["far"][0]] = 0x90
        with self.assertRaises(ValueError):
            audit.verify_blob(data, "dos20", enforce_sha=False)


if __name__ == "__main__":
    unittest.main()
