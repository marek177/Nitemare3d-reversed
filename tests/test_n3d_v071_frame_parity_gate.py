"""Synthetic indexed-frame / DAC parity regressions without original assets."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import n3d_v071_frame_parity_gate as gate

def manifest(role):
    return dict(role=role,reference_exe_sha256=gate.ORIGINAL_DOS2_UNPACKED_SHA,
        data_manifest_sha256="a"*64,world_state_sha256="b"*64,
        episode=1,level=1,game_tick=42,player_x=1440,player_y=3620,
        angle_units=80,render_checkpoint="post-ui",palette_phase="gameplay")

class PairTests(unittest.TestCase):
    def test_equal_buffers(self):
        o=manifest("original-dos2"); c=manifest("candidate")
        x=gate.compare_pair(bytes(64000),bytes(64000),bytes(768),bytes(768),o,c)
        self.assertTrue(x["pair_matches"])
        self.assertEqual(x["compared_indexed_pixels"],64000)

    def test_pixel_and_dac_mismatch(self):
        o=manifest("original-dos2"); c=manifest("candidate")
        f=bytearray(64000);f[1298]=12
        d=bytearray(768);d[4]=3
        x=gate.compare_pair(bytes(64000),bytes(f),bytes(768),bytes(d),o,c)
        self.assertEqual(x["different_indexed_pixels"],1)
        self.assertEqual(x["first_indexed_mismatch"]["x"],18)
        self.assertEqual(x["first_indexed_mismatch"]["y"],4)
        self.assertEqual(x["different_dac_components"],1)

    def test_reject_unsynced_and_invalid(self):
        o=manifest("original-dos2");c=manifest("candidate")
        c["game_tick"]=43
        with self.assertRaises(gate.Incomparable):
            gate.compare_pair(bytes(64000),bytes(64000),bytes(768),bytes(768),o,c)
        c["game_tick"]=42
        with self.assertRaises(gate.Incomparable):
            gate.compare_pair(bytes(64000),bytes(63999),bytes(768),bytes(768),o,c)
        with self.assertRaises(gate.Incomparable):
            gate.compare_pair(bytes(64000),bytes(64000),bytes(768),bytes([64])*768,o,c)

if __name__=="__main__": unittest.main()
