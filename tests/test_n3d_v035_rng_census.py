"""Synthetic tests of original-file opcode census; no original game bytes."""
import importlib.util
import struct
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v035_rng_census.py"
spec = importlib.util.spec_from_file_location("n3d_v035_rng_census", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


def fake_load_image():
    # All bytes are synthetic: use only explicitly documented witness
    # instructions and generate an independent jump table.
    length = max(probe.DIRECT_CALLS[-1] + 64,
                 max(at + len(bytes.fromhex(blob))
                     for at, blob in probe.WITNESSES.values()) + 64)
    image = bytearray(length)
    for at, blob in probe.WITNESSES.values():
        expected = bytes.fromhex(blob)
        image[at:at+len(expected)] = expected
    for at in probe.DIRECT_CALLS:
        image[at:at+5] = probe.RNG_FAR_CALL_OPCODE
    for index, target in enumerate(probe.DAMAGE_BRANCH_TARGETS):
        struct.pack_into("<H", image, probe.DAMAGE_TABLE_SITE+index*2,
                         target - probe.DAMAGE_CODE_SEGMENT_IMAGE_BASE)
    return image


def fake_mz(image):
    header = bytearray(64)
    header[:2] = b"MZ"
    struct.pack_into("<H", header, 8, 4)
    return bytes(header) + bytes(image)


class RngCensusTests(unittest.TestCase):
    def test_22_known_callers_sorted_and_include_missing_two(self):
        self.assertEqual(len(probe.DIRECT_CALLS), 22)
        self.assertEqual(tuple(sorted(set(probe.DIRECT_CALLS))),
                         probe.DIRECT_CALLS)
        self.assertIn(0x8860, probe.DIRECT_CALLS)
        self.assertIn(0x886C, probe.DIRECT_CALLS)

    def test_exact_raw_signature_scan(self):
        image = fake_load_image()
        self.assertEqual(probe.find_opcode_sites(image), probe.DIRECT_CALLS)
        self.assertEqual(len(probe.find_opcode_sites(image)), 22)

    def test_synthetic_windows_and_class_jump_table(self):
        data = probe.validate_sites(fake_load_image())
        self.assertTrue(data["ok"])
        self.assertEqual(data["observed_direct_opcode_occurrences"], 22)
        self.assertEqual(data["damage_class_08_entry"], 0x8860)
        self.assertEqual(data["damage_class_09_entry"], 0x886C)
        self.assertEqual(data["damage_class_0a_entry"], 0x886C)
        self.assertEqual(data["damage_class_11_to_14_entries"], [0x887C]*4)
        self.assertTrue(all(data["witnesses"].values()))

    def test_missing_direct_call_fails_even_with_same_other_21(self):
        image = fake_load_image()
        image[0x886C] = 0x90
        report = probe.validate_sites(image)
        self.assertFalse(report["ok"])
        self.assertEqual(report["missing_original_callsite_offsets"], [0x886C])

    def test_extra_signature_rejected_without_changing_expected_sites(self):
        image = fake_load_image()
        at = 0x11000
        if len(image) < at+5:
            image.extend(bytes(at+5-len(image)))
        image[at:at+5] = probe.RNG_FAR_CALL_OPCODE
        report = probe.validate_sites(image)
        self.assertFalse(report["ok"])
        self.assertEqual(report["unexpected_raw_signature_offsets"], [at])

    def test_class_jump_table_change_fails(self):
        image = fake_load_image()
        # Mangle the class 09 destination from 886C to 8860.
        struct.pack_into("<H", image, probe.DAMAGE_TABLE_SITE+2,
                         0x8860-probe.DAMAGE_CODE_SEGMENT_IMAGE_BASE)
        report = probe.validate_sites(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["damage_jump_table_matches"])
        self.assertEqual(report["observed_direct_opcode_occurrences"], 22)

    def test_damage_mask_change_fails_witness(self):
        image = fake_load_image()
        image[0x887C + 6] = 0x0F  # change mask but leave far CALL unchanged
        report = probe.validate_sites(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["witnesses"]["damage_rng_mask_1f"])

    def test_projected_variant_rejection_opcode_change_fails(self):
        image = fake_load_image()
        image[0xB297] = 0x75  # jne instead of je
        report = probe.validate_sites(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["witnesses"]["projected_variant_reject_empty"])

    def test_signature_in_data_cannot_override_hash_gate(self):
        fake = fake_mz(fake_load_image())
        report = probe.verify_original(fake)
        self.assertFalse(report["ok"])
        self.assertFalse(report["fingerprint_matches"])
        self.assertEqual(report["verdict"], "incorrect_original_executable")
        self.assertFalse(report["original_game_executed"])
        self.assertFalse(report["total_dynamic_rng_order_verified"])
        self.assertNotIn("witnesses", report)

    def test_class_jump_opcode_fails(self):
        image = fake_load_image()
        image[probe.DAMAGE_JMP_OPCODE] = 0x90
        with self.assertRaisesRegex(ValueError, "damage class jump"):
            probe.validate_sites(image)

    def test_mz_header_gate(self):
        image = fake_load_image()
        self.assertEqual(probe.load_image(fake_mz(image)), image)
        with self.assertRaisesRegex(ValueError, "MZ"):
            probe.load_image(b"garbage")
        invalid = bytearray(fake_mz(image))
        struct.pack_into("<H", invalid, 8, 0xFFFF)
        with self.assertRaisesRegex(ValueError, "header"):
            probe.load_image(invalid)

    def test_dead_modulo_seven_comparison_mathematically_unreachable(self):
        # The actual RNG returns only 0..32767. For signed 16-bit IDIV +7
        # the remainder is 0..6, never 7. Table-byte==0 retry still exists.
        self.assertEqual({r % 7 for r in range(32768)}, set(range(7)))
        self.assertNotIn(7, (r % 7 for r in range(32768)))
        for key in ("resource_slot1_mod7_dead_compare",
                    "resource_slot2_mod7_dead_compare"):
            self.assertIn(key, probe.WITNESSES)


if __name__ == "__main__":
    unittest.main()
