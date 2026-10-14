"""v0.33 synthetic verifier tests. They do not bundle original game bytes."""

import importlib.util
import struct
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v033_push_verify.py"
spec = importlib.util.spec_from_file_location("n3d_v033_push_verify", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


def fake_mz(image):
    header = bytearray(64)
    header[0:2] = b"MZ"
    struct.pack_into("<H", header, 8, 4)
    return bytes(header) + image


def fake_ne(segment3):
    # MZ stub at 0x00, NE header at 0x80, segment table at 0xC0,
    # segment 3 data at 0x200 (alignment 16). Purely synthetic.
    raw = bytearray(0x200+len(segment3))
    raw[:2] = b"MZ"
    struct.pack_into("<I", raw, 0x3C, 0x80)
    raw[0x80:0x82] = b"NE"
    struct.pack_into("<H", raw, 0x80+0x1C, 3)
    struct.pack_into("<H", raw, 0x80+0x22, 0x40)
    struct.pack_into("<H", raw, 0x80+0x32, 4)
    struct.pack_into("<HH", raw, 0xC0+2*8, 0x20, len(segment3))
    raw[0x200:] = segment3
    return bytes(raw)


def paired_fixture():
    dos_image = bytearray(probe.DOS_START+probe.LENGTH)
    win_seg3 = bytearray(probe.WIN_SEG3_START+probe.LENGTH)
    body = bytes([0xAA] * probe.LENGTH)
    dos_image[probe.DOS_START:] = body
    win_seg3[probe.WIN_SEG3_START:] = body
    allowed = {pos for start, n, _ in probe.OPERAND_SPANS
               for pos in range(start, start+n)}
    for relative in allowed:
        win_seg3[probe.WIN_SEG3_START+relative] = 0x55
    return dos_image, win_seg3, allowed


class PushCompareTests(unittest.TestCase):
    def test_explicit_mask_is_only_twenty_address_operand_bytes(self):
        _dos, _win, allowed = paired_fixture()
        self.assertEqual(len(allowed), 20)
        self.assertEqual(probe.LENGTH, 292)
        self.assertEqual(len(probe.OPERAND_SPANS), 9)
        self.assertEqual(probe.OPERAND_SPANS[7][1], 4)

    def test_masked_control_flow_match_without_original_data(self):
        dos, win, _allowed = paired_fixture()
        result = probe.compare_masked(dos, win)
        self.assertTrue(result["masked_control_flow_equal"])
        self.assertTrue(result["exact_original_pattern"])
        self.assertEqual(result["identical_bytes"], 272)
        self.assertEqual(result["different_bytes"], 20)
        self.assertEqual(result["unexpected_difference_offsets"], [])

    def test_opcode_change_is_not_masked(self):
        dos, win, allowed = paired_fixture()
        self.assertNotIn(0x20, allowed)
        win[probe.WIN_SEG3_START+0x20] ^= 1
        result = probe.compare_masked(dos, win)
        self.assertFalse(result["masked_control_flow_equal"])
        self.assertEqual(result["unexpected_difference_offsets"], [0x20])

    def test_missing_expected_operand_change_is_not_exact_pattern(self):
        dos, win, allowed = paired_fixture()
        original_body_byte = dos[probe.DOS_START+0x07]
        win[probe.WIN_SEG3_START+0x07] = original_body_byte
        result = probe.compare_masked(dos, win)
        self.assertTrue(result["masked_control_flow_equal"])
        self.assertFalse(result["exact_original_pattern"])
        self.assertEqual(result["different_bytes"], 19)

    def test_broken_binary_body_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            probe.compare_masked(bytearray(50), bytearray(200))

    def test_executable_load_image_parser(self):
        original = b"small-synthetic"
        self.assertEqual(probe.dos_unpacked_image(fake_mz(original)), original)
        with self.assertRaisesRegex(ValueError, "MZ"):
            probe.dos_unpacked_image(original)

    def test_win_ne_segment_parser(self):
        original = bytes(range(200))
        self.assertEqual(probe.win_ne_segment(fake_ne(original)), original)
        with self.assertRaisesRegex(ValueError, "NE"):
            probe.win_ne_segment(fake_mz(b"not-ne"))

    def test_fingerprint_fails_closed_on_synthetic_lookalike(self):
        dos, win, _allowed = paired_fixture()
        report = probe.verify_pair(fake_mz(dos), fake_ne(win))
        self.assertFalse(report["verified_static_control_flow"])
        self.assertFalse(report["dos_image_fingerprint"])
        self.assertFalse(report["win16_file_fingerprint"])
        self.assertEqual(report["verdict"], "build_fingerprint_mismatch")
        self.assertFalse(report["original_runtime_executed"])
        self.assertFalse(report["runtime_1to1_confirmed"])

    def test_witness_detection(self):
        image = bytearray(0x0F60)
        image[0x0EF5:0x0EFB] = bytes.fromhex("f6 46 f7 06 75 64")
        check = probe.byte_windows(image, {
            "blocked": probe.DOS_WITNESSES["block_on_target_object_flags06"]
        })
        self.assertTrue(check["blocked"])
        image[0x0EF8] = 0x04
        check = probe.byte_windows(image, {
            "blocked": probe.DOS_WITNESSES["block_on_target_object_flags06"]
        })
        self.assertFalse(check["blocked"])

    def test_foreign_opcode_witnesses_have_build_scoped_locations(self):
        self.assertEqual(probe.DOS_WITNESSES["fastcall_to_push_updater"][0], 0xC172)
        self.assertEqual(probe.WIN_WITNESSES["counter_decrement_after_call"][0],
                         0x231B)


if __name__ == "__main__":
    unittest.main()
