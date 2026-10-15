"""Synthetic DOS animation call-graph tests; no original binaries included."""

import importlib.util
import struct
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_v034_animation_probe.py"
spec = importlib.util.spec_from_file_location("n3d_v034_animation_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


def synthetic_image():
    last_edge = max(at + (5 if encoding == "far" else 3)
                    for at, encoding, _target in probe.CALL_EDGES.values())
    last_witness = max(at + len(bytes.fromhex(code))
                       for at, code in probe.WITNESSES.values())
    image = bytearray(max(last_edge, last_witness) + 16)

    # The small fixtures describe our model, not recovered original bytes.
    for at, code in probe.WITNESSES.values():
        blob = bytes.fromhex(code)
        image[at:at+len(blob)] = blob
    for at, encoding, target in probe.CALL_EDGES.values():
        if encoding == "near":
            displacement = target - (at + 3)
            assert -32768 <= displacement <= 32767
            image[at] = 0xE8
            struct.pack_into("<h", image, at+1, displacement)
        else:
            image[at] = 0x9A
            struct.pack_into("<HH", image, at+1, target & 15, target >> 4)
    return image


def mz_with_image(image):
    header = bytearray(64)
    header[:2] = b"MZ"
    struct.pack_into("<H", header, 8, 4)
    return bytes(header) + bytes(image)


class ObjectAnimationStaticProbeTests(unittest.TestCase):
    def test_all_direct_edges_and_witnesses_synthetic(self):
        proof = probe.check_static_image(synthetic_image())
        self.assertTrue(proof["ok"])
        self.assertEqual(len(proof["direct_call_edges"]), 16)
        self.assertEqual(len(proof["opcode_witnesses"]), 18)
        self.assertTrue(all(proof["opcode_witnesses"].values()))

    def test_edge_sites_are_unique(self):
        sites = [site for site, _encoding, _target
                 in probe.CALL_EDGES.values()]
        self.assertEqual(len(set(sites)), len(sites))

    def test_real_original_rejects_synthetic_file_before_offset_checks(self):
        result = probe.verify_original_executable(
            mz_with_image(synthetic_image()))
        self.assertFalse(result["ok"])
        self.assertFalse(result["fingerprint_matches"])
        self.assertEqual(result["verdict"], "incorrect_original_executable")
        self.assertNotIn("opcode_witnesses", result)
        self.assertFalse(result["original_game_executed"])

    def test_near_call_uses_signed_displacement(self):
        image = synthetic_image()
        site, encoding, expected = probe.CALL_EDGES["span_render_to_animation"]
        self.assertEqual(encoding, "near")
        self.assertLess(expected, site)
        self.assertEqual(probe.decode_direct_call(image, site, encoding),
                         expected)

    def test_far_call_normalizes_segment_times_16(self):
        image = synthetic_image()
        site, encoding, expected = probe.CALL_EDGES["renderer_project_sorted_objects"]
        self.assertEqual(encoding, "far")
        self.assertEqual(probe.decode_direct_call(image, site, encoding),
                         expected)

    def test_near_call_target_change_fails(self):
        image = synthetic_image()
        at = probe.CALL_EDGES["span_render_to_animation"][0]
        image[at + 1] ^= 1
        proof = probe.check_static_image(image)
        self.assertFalse(proof["ok"])
        self.assertFalse(proof["direct_call_edges"]["span_render_to_animation"]["ok"])

    def test_far_call_target_change_fails(self):
        image = synthetic_image()
        at = probe.CALL_EDGES["projectiles_also_to_projection"][0]
        image[at + 3] ^= 1
        proof = probe.check_static_image(image)
        self.assertFalse(proof["ok"])
        self.assertFalse(proof["direct_call_edges"]["projectiles_also_to_projection"]["ok"])

    def test_opcode_substitution_fails_closed(self):
        image = synthetic_image()
        at = probe.CALL_EDGES["outer_frame_to_renderer"][0]
        image[at] = 0x90  # NOP, not a CALL
        proof = probe.check_static_image(image)
        self.assertFalse(proof["ok"])
        self.assertIsNone(proof["direct_call_edges"]["outer_frame_to_renderer"]["observed_target"])

    def test_frame_increment_witness_change_fails(self):
        image = synthetic_image()
        at = probe.WITNESSES["span_frame_increment"][0]
        image[at + 1] ^= 1
        proof = probe.check_static_image(image)
        self.assertFalse(proof["ok"])
        self.assertFalse(proof["opcode_witnesses"]["span_frame_increment"])

    def test_due_guard_witness_change_fails(self):
        image = synthetic_image()
        at = probe.WITNESSES["regular_projected_deadline_guard"][0]
        image[at + 5] ^= 1
        self.assertFalse(probe.check_static_image(image)["ok"])

    def test_truncated_instruction_fails(self):
        image = bytearray(10)
        self.assertIsNone(probe.decode_direct_call(image, 9, "far"))
        self.assertFalse(probe.check_static_image(image)["ok"])

    def test_invalid_or_short_mz_rejected(self):
        with self.assertRaisesRegex(ValueError, "MZ"):
            probe.unpacked_mz_image(b"NOT_MZ")
        with self.assertRaisesRegex(ValueError, "header size"):
            raw = bytearray(mz_with_image(synthetic_image()))
            struct.pack_into("<H", raw, 8, 0xFFFF)
            probe.unpacked_mz_image(raw)

    def test_static_trace_cannot_claim_runtime(self):
        report = probe.verify_original_executable(
            mz_with_image(synthetic_image()))
        self.assertFalse(report["runtime_animation_order_verified"])
        self.assertFalse(report["complete_object_scheduler_identified"])
        self.assertEqual(probe.CALL_EDGES["fast_to_noop_hook"][2], 0xC51A)


if __name__ == "__main__":
    unittest.main()
