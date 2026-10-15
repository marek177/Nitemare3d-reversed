"""Synthetic tests for v0.37 scheduler opcode and branch verifier.

Original DOS game code is NOT included; SHA gate must reject these fixtures.
"""

import importlib.util
import struct
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v037_scheduler_gate_probe.py"
spec = importlib.util.spec_from_file_location("n3d_v037_scheduler_gate_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


def synthetic_image():
    last_window = max(site + len(bytes.fromhex(code))
                      for site, code in probe.WINDOWS.values())
    last_branch = max(site + 2 for site, _opcode, _target
                      in probe.SHORT_BRANCHES.values())
    last_call = max(site + (3 if mode == "near" else 5)
                    for site, mode, _target in probe.DIRECT_CALLS.values())
    image = bytearray(max(last_window, last_branch, last_call) + 8)
    for site, data in probe.WINDOWS.values():
        raw = bytes.fromhex(data)
        image[site:site+len(raw)] = raw
    for site, opcode, target in probe.SHORT_BRANCHES.values():
        offset = target - site - 2
        assert -128 <= offset <= 127
        image[site] = opcode
        struct.pack_into("<b", image, site+1, offset)
    for site, mode, target in probe.DIRECT_CALLS.values():
        if mode == "near":
            offset = target - site - 3
            assert -32768 <= offset <= 32767
            image[site] = 0xE8
            struct.pack_into("<h", image, site+1, offset)
        else:
            # Both FAR calls are already covered by the exact original
            # opcode window at C246. The normalized target has many valid
            # segment:offset representations: never rewrite its originally
            # encoded bytes using an arbitrary equivalent segment base.
            assert image[site] == 0x9A
            off, seg = struct.unpack_from("<HH", image, site+1)
            assert (seg << 4) + off == target
    return image


def fake_mz(image):
    header = bytearray(64)
    header[:2] = b"MZ"
    struct.pack_into("<H", header, 8, 4)
    return bytes(header) + bytes(image)


class SchedulerGateStaticTests(unittest.TestCase):
    def test_all_original_opcode_windows_and_edges_are_present(self):
        image = synthetic_image()
        result = probe.audit_original_image(image)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["verified_opcode_windows"]), 25)
        self.assertEqual(len(result["verified_short_branches"]), 13)
        self.assertEqual(len(result["verified_direct_calls"]), 13)
        self.assertTrue(all(result["verified_opcode_windows"].values()))
        self.assertTrue(all(result["verified_short_branches"].values()))
        self.assertTrue(all(result["verified_direct_calls"].values()))
        self.assertTrue(result["audited_short_branches_forward_only"])

    def test_quantized_counter_change_opcode_mutation_is_rejected(self):
        image = synthetic_image()
        image[0xBEE6] = 0xFE  # INC DWORD DS:16F6 opcode mutated
        result = probe.audit_original_image(image)
        self.assertFalse(result["ok"])
        self.assertFalse(result["verified_opcode_windows"]
                         ["slow_cache_and_counter_write"])

    def test_frame_counter_change_mutation_is_rejected(self):
        image = synthetic_image()
        image[0xBF28] = 0xFE  # INC DWORD becomes a different instruction
        self.assertFalse(probe.audit_original_image(image)["ok"])

    def test_slow_threshold_counter_plus_one_mutation(self):
        image = synthetic_image()
        image[0xC1F5] = 0x48  # DEC instead of INC
        report = probe.audit_original_image(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["slow_threshold_set_to_counter_plus_one"])

    def test_frame_threshold_counter_plus_one_mutation(self):
        image = synthetic_image()
        image[0xC279] = 0x48
        report = probe.audit_original_image(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["frame_threshold_set_to_counter_plus_one"])

    def test_demo_fast_uses_slow_not_frame_counter(self):
        image = synthetic_image()
        result = probe.audit_original_image(image)
        self.assertTrue(result["demo_fast_receives_slow_counter"])
        image[0xC22B] = 0x76  # source DS:3672 changed to DS:3676
        self.assertFalse(probe.audit_original_image(image)
                         ["demo_fast_receives_slow_counter"])

    def test_demo_odd_gate_wrong_jump_rejected(self):
        image = synthetic_image()
        image[0xC226] = 0x75  # skip on odd instead of even
        result = probe.audit_original_image(image)
        self.assertFalse(result["ok"])
        self.assertFalse(result["verified_short_branches"]
                         ["demo_even_generation_skip_fast"])

    def test_direct_call_cannot_be_silently_remapped(self):
        image = synthetic_image()
        site, mode, target = probe.DIRECT_CALLS["demo_fast_C150"]
        self.assertEqual(probe.decode_call(image, site, mode), target)
        image[site+1] ^= 1
        result = probe.audit_original_image(image)
        self.assertFalse(result["ok"])
        self.assertFalse(result["verified_direct_calls"]["demo_fast_C150"])

    def test_far_panel_and_projectile_calls(self):
        image = synthetic_image()
        for key in ("secret_panel_0AEA", "projectiles_8230"):
            site, mode, target = probe.DIRECT_CALLS[key]
            self.assertEqual(mode, "far")
            self.assertEqual(probe.decode_call(image, site, mode), target)

    def test_500_unsigned_fallback_guard_not_swapped(self):
        image = synthetic_image()
        self.assertTrue(probe.audit_original_image(image)
                        ["legacy_recovery_uses_unsigned_500_limit"])
        image[0xC295] = 0x77  # JA would invert <=500 branch
        result = probe.audit_original_image(image)
        self.assertFalse(result["ok"])
        self.assertFalse(result["verified_short_branches"]
                         ["unsigned_500_lag_no_recovery"])

    def test_missing_branch_rejected(self):
        image = synthetic_image()
        image[0xC1D8] = 0x90
        report = probe.audit_original_image(image)
        self.assertFalse(report["ok"])
        self.assertFalse(report["verified_short_branches"]["slow_high_overdue"])

    def test_original_identity_gate_rejects_synthetic_mz(self):
        fake = fake_mz(synthetic_image())
        report = probe.verify_original(fake)
        self.assertFalse(report["fingerprint_valid"])
        self.assertFalse(report["ok"])
        self.assertFalse(report["original_game_executed"])
        self.assertEqual(report["verdict"], "original_build_fingerprint_mismatch")
        self.assertNotIn("verified_opcode_windows", report)

    def test_reject_invalid_mz_header(self):
        with self.assertRaisesRegex(ValueError, "MZ"):
            probe.mz_load_image(b"nonsense")
        f = bytearray(fake_mz(synthetic_image()))
        struct.pack_into("<H", f, 8, 0xFFFF)
        with self.assertRaisesRegex(ValueError, "header"):
            probe.mz_load_image(f)


if __name__ == "__main__":
    unittest.main()
