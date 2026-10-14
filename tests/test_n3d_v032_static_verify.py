"""Synthetic unit checks for the read-only v0.32 original-byte verifier.

These tests are not evidence that the original game was executed.
"""
import importlib.util
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v032_static_verify.py"
spec = importlib.util.spec_from_file_location("n3d_v032_static_verify", SCRIPT)
verify = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verify
spec.loader.exec_module(verify)


def fake_dos_mz(payload=b"proof"):
    data = bytearray(0x40+len(payload))
    data[:2] = b"MZ"
    struct.pack_into("<H", data, 8, 4)  # 4 paragraphs = 64 bytes
    data[0x40:] = payload
    return bytes(data)


def fake_win16_ne(payload=b"\x90"*512):
    data = bytearray(0x200+len(payload))
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 0x40)
    data[0x40:0x42] = b"NE"
    struct.pack_into("<H", data, 0x40+0x1c, 3)
    struct.pack_into("<H", data, 0x40+0x22, 0x40)
    struct.pack_into("<H", data, 0x40+0x32, 4)
    struct.pack_into("<HH", data, 0x80+2*8, 0x20, len(payload))
    data[0x200:] = payload
    return bytes(data)


class StaticVerificationTests(unittest.TestCase):
    def test_identity_catalog_five_are_build_specific(self):
        self.assertEqual(len(verify.PROFILES), 5)
        self.assertEqual(verify.PROFILES["dos12"][0], "mz-raw")
        self.assertEqual(verify.PROFILES["win16"][0], "ne-raw")
        self.assertEqual(verify.PROFILES["dos20"][1], 171360)

    def test_extract_dos_load_image_and_reject_short_header(self):
        self.assertEqual(verify.mz_image(fake_dos_mz(b"xyz")), b"xyz")
        with self.assertRaises(ValueError):
            verify.mz_image(b"plain")

    def test_extract_ne_seg3(self):
        image = b"\xF6\x87\x94\x7e" + b"\x90"*60
        self.assertEqual(verify.ne_segment(fake_win16_ne(image), 3), image)
        with self.assertRaises(ValueError):
            verify.ne_segment(fake_dos_mz(), 3)

    def test_detect_edited_win16_opcode(self):
        image = bytearray(0x2200)
        offset, code = verify.WIN16_SEG3["push_wall_property_forbidden_bit_02"]
        image[offset:offset+len(bytes.fromhex(code))] = bytes.fromhex(code)
        self.assertTrue(verify.check_sites(image, {"push": (offset, code)})["push"])
        image[offset+4] ^= 1
        self.assertFalse(verify.check_sites(image, {"push": (offset, code)})["push"])

    def test_verified_dos_fingerprint_cannot_be_guessed_from_header(self):
        image = fake_dos_mz(b"no-original")
        r = verify.verify("dos20", image)
        self.assertFalse(r["ok"])
        self.assertFalse(r["fingerprint_valid"])
        self.assertEqual(r["opcode_witnesses"], {})
        self.assertFalse(r["original_runtime_verified"])

    def test_synthetic_profile_override_only(self):
        raw = fake_dos_mz(b"synthetic")
        with patch.dict(verify.PROFILES, {"dos20": ("mz-image", len(b"synthetic"),
                                                  verify.sha256(b"synthetic"))}):
            # v0.32 witnesses still required, not just a matching image hash.
            r = verify.verify("dos20", raw)
            self.assertTrue(r["fingerprint_valid"])
            self.assertFalse(r["ok"])
            self.assertFalse(all(r["opcode_witnesses"].values()))

    def test_read_win16_save_hp(self):
        data = bytearray(verify.SAVE_SLOT_SIZE)
        struct.pack_into("<I", data, 0, verify.SAVE_SLOT_SIZE)
        data[verify.SAVE_HP_OFFSET] = 100
        r = verify.inspect_save(data)
        self.assertEqual(r["hp_observed"], 100)
        self.assertEqual(r["hp_absolute_file_offset"], 0x206A)
        self.assertFalse(r["load_timing_verified"])
        data[verify.SAVE_HP_OFFSET] = 0
        self.assertEqual(verify.inspect_save(data)["hp_observed"], 0)

    def test_reject_non_matching_sav_slots(self):
        data = bytes(verify.SAVE_SLOT_SIZE)
        with self.assertRaisesRegex(ValueError, "bad size marker"):
            verify.inspect_save(data)
        with self.assertRaisesRegex(ValueError, "fixed-size"):
            verify.inspect_save(data[:-1])

    def test_second_save_slot_base_offset(self):
        data = bytearray(verify.SAVE_SLOT_SIZE*2)
        for i in range(2):
            struct.pack_into("<I", data, i*verify.SAVE_SLOT_SIZE, verify.SAVE_SLOT_SIZE)
        data[verify.SAVE_SLOT_SIZE+verify.SAVE_HP_OFFSET] = 47
        r = verify.inspect_save(data, 1)
        self.assertEqual(r["hp_observed"], 47)
        self.assertEqual(r["hp_absolute_file_offset"], verify.SAVE_SLOT_SIZE+0x206A)

    def test_unknown_version_does_not_reuse_wrong_offsets(self):
        data = fake_dos_mz(b"sample")
        self.assertNotEqual(verify.sha256(data), verify.PROFILES["dos12"][2])
        self.assertNotIn("push_wall_property_forbidden_bit_02", verify.DOS20_IMAGE)


if __name__ == "__main__":
    unittest.main()
