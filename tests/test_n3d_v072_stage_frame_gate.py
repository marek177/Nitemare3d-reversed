"""Synthetic-only renderer stage-gate regressions; no original Nitemare3D assets."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_v071_frame_parity_gate as old
import n3d_v072_stage_frame_gate as gate


class StageFrameGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.original = root / "original"
        self.candidate = root / "candidate"
        self.create_capture(self.original, "original-dos2")
        self.create_capture(self.candidate, "candidate")

    def create_capture(self, root, role):
        root.mkdir()
        p = root / "stages" / "35_span_build_end"
        p.mkdir(parents=True)
        vec = bytearray(28000)
        vec[0] = 5
        vec[5] = 1
        vec[7] = 0
        owner = bytearray(642)
        for x in range(8, 312):
            off = 2 + 2*x
            owner[off:off+2] = (0x62AC).to_bytes(2, "little")
        spans = bytearray(910)
        spans[0:2] = (1).to_bytes(2, "little")
        spans[10:12] = (0x62AC).to_bytes(2, "little")
        spans[12:14] = (8).to_bytes(2, "little")
        spans[16:18] = (311).to_bytes(2, "little")
        files = {
            "vec.bin": bytes(vec),
            "owner.bin": bytes(owner),
            "spans.bin": bytes(spans),
            "frame.idx": bytes(64000),
            "dac.bin": bytes(768),
        }
        for name, buf in files.items():
            location = p / name if name in ("vec.bin", "owner.bin", "spans.bin") else root / name
            location.write_bytes(buf)
        manifest = {
            "format": "n3d-dos20-stage-frame-v072",
            "role": role,
            "reference_exe_sha256": old.ORIGINAL_DOS2_UNPACKED_SHA,
            "data_manifest_sha256": "a"*64,
            "episode": 1,
            "level": 1,
            "game_tick": 42,
            "player_x": 1440,
            "player_y": 3620,
            "angle_units": 80,
            "world_state_sha256": "b"*64,
            "render_checkpoint": "post-present",
            "palette_phase": "gameplay",
            "vec_count": 1,
            "stage_checkpoint": "post_span",
            "frame_checkpoint": "post_present",
            "capture_sha256": {n: gate.digest(buf) for n,buf in files.items()},
        }
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def change(self, root, filename, offset, value, resign=True):
        parts = gate.FILE_SHAPES[filename][0]
        path = root.joinpath(*parts)
        content = bytearray(path.read_bytes())
        content[offset] = value
        path.write_bytes(content)
        if resign:
            manifest_file = root / "manifest.json"
            manifest = json.loads(manifest_file.read_text())
            manifest["capture_sha256"][filename] = gate.digest(content)
            manifest_file.write_text(json.dumps(manifest))
        return content

    def manifest(self, root, field, value):
        p = root / "manifest.json"
        data = json.loads(p.read_text())
        data[field] = value
        p.write_text(json.dumps(data))

    def test_all_identical_stage_buffers_pass_as_pair_only(self):
        result = gate.analyze(self.original, self.candidate)
        self.assertTrue(result["zero_diff_at_supplied_checkpoints"])
        self.assertEqual(result["first_divergent_stage"], "PASS")
        self.assertFalse(result["whole_game_pixel_parity_proven"])
        self.assertFalse(result["original_recording_authenticated"])
        self.assertEqual(result["stage_results"]["FRAME_MISMATCH"]["compared_bytes_original"],64000)
        self.assertEqual(result["stage_results"]["OWNER_MISMATCH"]["compared_bytes_original"],610)

    def test_first_divergence_vec(self):
        self.change(self.candidate,"vec.bin",0,9)
        result = gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"VEC_MISMATCH")
        self.assertEqual(result["stage_results"]["VEC_MISMATCH"]["first_field"],"wall_id")

    def test_first_divergence_owner(self):
        owner=self.change(self.candidate,"owner.bin",2+18*2,0)
        # Mutated one active column to unowned; make count consistent.
        self.change(self.candidate,"owner.bin",0,1)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"OWNER_MISMATCH")
        self.assertEqual(result["stage_results"]["OWNER_MISMATCH"]["first_screen_x"],18)

    def test_first_divergence_span(self):
        self.change(self.candidate,"spans.bin",12,9)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"SPAN_MISMATCH")
        self.assertEqual(result["stage_results"]["SPAN_MISMATCH"]["first_field"],"x_start")

    def test_first_divergence_frame(self):
        self.change(self.candidate,"frame.idx",4*320+18,12)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"FRAME_MISMATCH")
        point=result["stage_results"]["FRAME_MISMATCH"]["first_pixel"]
        self.assertEqual((point["x"],point["y"]),(18,4))
        self.assertTrue(point["in_3d_viewport"])

    def test_first_divergence_dac(self):
        self.change(self.candidate,"dac.bin",4,3)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"DAC_MISMATCH")
        self.assertEqual(result["stage_results"]["DAC_MISMATCH"]["first_palette_index"],1)
        self.assertEqual(result["stage_results"]["DAC_MISMATCH"]["first_channel"],"G")

    def test_unsynchronized_game_tick_does_not_issue_verdict(self):
        self.manifest(self.candidate,"game_tick",43)
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_wrong_episode_or_world_state_rejected(self):
        self.manifest(self.candidate,"world_state_sha256","f"*64)
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)
        self.manifest(self.candidate,"world_state_sha256","b"*64)
        self.manifest(self.candidate,"episode",2)
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_modified_file_without_matching_digest_rejected(self):
        self.change(self.candidate,"frame.idx",1,3,resign=False)
        with self.assertRaisesRegex(old.Incomparable,"SHA-256"):
            gate.analyze(self.original,self.candidate)

    def test_wrong_file_size_rejected(self):
        f=self.candidate/"frame.idx"
        f.write_bytes(bytes(63999))
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_invalid_dac_component_rejected(self):
        self.change(self.candidate,"dac.bin",7,64)
        with self.assertRaisesRegex(old.Incomparable,"6-bit"):gate.analyze(self.original,self.candidate)

    def test_owner_pointer_outside_pool_rejected(self):
        self.change(self.candidate,"owner.bin",2+18*2,0xFF)
        with self.assertRaisesRegex(old.Incomparable,"invalid active VEC"):
            gate.analyze(self.original,self.candidate)

    def test_owner_count_must_be_consistent(self):
        self.change(self.candidate,"owner.bin",2+18*2,0)
        with self.assertRaisesRegex(old.Incomparable,"remaining count"):
            gate.analyze(self.original,self.candidate)

    def test_span_count_overflow_rejected(self):
        self.change(self.candidate,"spans.bin",0,51)
        with self.assertRaisesRegex(old.Incomparable,"maximum of 50"):
            gate.analyze(self.original,self.candidate)

    def test_invalid_role_rejected(self):
        self.manifest(self.candidate,"role","original-dos2")
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_wrong_stage_checkpoint_rejected(self):
        self.manifest(self.candidate,"stage_checkpoint","pre_span")
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_tail_unused_vec_ignored_only_after_hash_validated(self):
        self.change(self.candidate,"vec.bin",20000,7)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"PASS")

    def test_outside_viewport_owner_ignored_only_after_hash_validated(self):
        self.change(self.candidate,"owner.bin",2+2*2,7)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"PASS")

    def test_uninitialized_span_tail_ignored_only_after_hash_validated(self):
        self.change(self.candidate,"spans.bin",900,7)
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["first_divergent_stage"],"PASS")

    def test_vec_count_mismatch_rejected(self):
        self.manifest(self.candidate,"vec_count",2)
        with self.assertRaises(old.Incomparable):gate.analyze(self.original,self.candidate)

    def test_manifest_sha_not_proof_of_genuine_source(self):
        result=gate.analyze(self.original,self.candidate)
        self.assertEqual(result["evidence"],"SUPPLIED_CAPTURE_BYTE_COMPARISON_ONLY")
        self.assertFalse(result["gameplay_state_authenticated"])


if __name__ == "__main__":
    unittest.main()
