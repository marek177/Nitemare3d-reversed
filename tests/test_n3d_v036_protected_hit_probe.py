"""Synthetic tests for the DOS 1.0/1.7/1.9/2.0 static hit-order probe.

Never bundles or executes original game code; real original inputs are only
supplied by an owner to the separate fingerprint-gated command-line tool.
"""
import importlib.util
import struct
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v036_protected_hit_probe.py"
spec = importlib.util.spec_from_file_location("n3d_v036_protected_hit_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


def synthetic_image(build):
    rule = probe.BUILDS[build]
    length = max(at + len(bytes.fromhex(code))
                 for at, code in rule["windows"].values())
    length = max(length, rule["exit"] + 4)
    image = bytearray(length + 8)
    for at, code in rule["windows"].values():
        part = bytes.fromhex(code)
        image[at:at+len(part)] = part
    image[rule["exit"]:rule["exit"]+4] = bytes.fromhex("5e 5f c9 cb")
    return image


def fake_mz(image):
    hdr = bytearray(64)
    hdr[:2] = b"MZ"
    struct.pack_into("<H", hdr, 8, 4)
    return bytes(hdr) + bytes(image)


class ProtectedHitStaticTests(unittest.TestCase):
    def test_four_distinct_fingerprinted_builds(self):
        self.assertEqual(len(probe.BUILDS), 4)
        self.assertEqual([probe.BUILDS[n]["size"]
                          for n in ("dos10", "dos17", "dos19", "dos20")],
                         [154448, 170848, 171296, 171360])
        self.assertEqual(len({p["sha256"] for p in probe.BUILDS.values()}), 4)

    def test_synthetic_original_gate_and_call_order(self):
        for build in probe.BUILDS:
            with self.subTest(build=build):
                report = probe.audit_static_image(synthetic_image(build), build)
                self.assertTrue(report["ok"])
                self.assertTrue(all(report["machine_code_windows"].values()))
                self.assertTrue(report["epilogue_retf_matches"])
                self.assertEqual(report["shield_exit_target"], report["expected_exit"])
                self.assertEqual(report["dead_state_exit_target"], report["expected_exit"])
                self.assertEqual(report["damage_producer_call_target"],
                                 report["expected_damage_producer_target"])
                self.assertEqual(report["producer_precedes_protection"],
                                 build == "dos20")

    def test_guard_check_target_cannot_be_changed(self):
        image = synthetic_image("dos19")
        cmp_site = probe.BUILDS["dos19"]["shield"]
        image[cmp_site+6] ^= 1
        report = probe.audit_static_image(image, "dos19")
        self.assertFalse(report["ok"])
        self.assertNotEqual(report["shield_exit_target"], report["expected_exit"])

    def test_dead_state_check_target_cannot_be_changed(self):
        image = synthetic_image("dos20")
        cmp_site = probe.BUILDS["dos20"]["dead"]
        image[cmp_site+6] ^= 1
        report = probe.audit_static_image(image, "dos20")
        self.assertFalse(report["ok"])
        self.assertNotEqual(report["dead_state_exit_target"], report["expected_exit"])

    def test_damage_far_call_target_mutation_detected(self):
        image = synthetic_image("dos10")
        site = probe.BUILDS["dos10"]["call"]
        image[site+1] ^= 1
        report = probe.audit_static_image(image, "dos10")
        self.assertFalse(report["ok"])
        self.assertNotEqual(report["damage_producer_call_target"],
                            report["expected_damage_producer_target"])

    def test_v20_nonzero_damage_timer_opcode_checked(self):
        image = synthetic_image("dos20")
        image[0x6A93+4] = 0x04  # timer would become 4 instead of 3
        report = probe.audit_static_image(image, "dos20")
        self.assertFalse(report["ok"])
        self.assertFalse(report["machine_code_windows"]["hit_indicator_set_three"])

    def test_v20_damage_zero_branch_check(self):
        image = synthetic_image("dos20")
        self.assertTrue(probe.audit_static_image(image, "dos20")
                        ["v20_zero_damage_skips_flash"])
        image[0x6A92] ^= 1
        result = probe.audit_static_image(image, "dos20")
        self.assertFalse(result["ok"])
        self.assertFalse(result["v20_zero_damage_skips_flash"])

    def test_frame_counter_display_codes_not_swapped(self):
        image = synthetic_image("dos20")
        report = probe.audit_static_image(image, "dos20")
        self.assertTrue(report["ok"])
        image[0xA24C] = 0x03  # would draw clear in the nonnegative branch
        report = probe.audit_static_image(image, "dos20")
        self.assertFalse(report["ok"])
        self.assertFalse(
            report["machine_code_windows"]["indicator_hit_draw_code_four"])

    def test_epilogue_retf_is_required(self):
        image = synthetic_image("dos17")
        image[probe.BUILDS["dos17"]["exit"]+3] = 0x90
        self.assertFalse(probe.audit_static_image(image, "dos17")["ok"])

    def test_fake_file_fails_sha_gate_even_with_matching_windows(self):
        for build in probe.BUILDS:
            with self.subTest(build=build):
                raw = fake_mz(synthetic_image(build))
                result = probe.verify_original(raw, build)
                self.assertFalse(result["ok"])
                self.assertFalse(result["fingerprint_matches"])
                self.assertEqual(result["verdict"], "wrong_original_build")
                self.assertFalse(result["original_runtime_executed"])
                self.assertNotIn("machine_code_windows", result)

    def test_bad_mz_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MZ"):
            probe.unpacked_image(b"bad")
        damaged = bytearray(fake_mz(synthetic_image("dos20")))
        struct.pack_into("<H", damaged, 8, 0xFFFF)
        with self.assertRaisesRegex(ValueError, "header"):
            probe.unpacked_image(damaged)

    def test_unknown_build_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            probe.verify_original(b"MZ", "dos12")


if __name__ == "__main__":
    unittest.main()
