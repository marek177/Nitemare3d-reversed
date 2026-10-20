"""Synthetic-only stage-order tests; no commercial original assets."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import n3d_v080_midrender_checkpoint as m

class PhaseTests(unittest.TestCase):
    def test_observed_first_column_phase(self):
        self.assertEqual(m.rewind_one_phase(0x014B800F,-178403),0x014E38F2)
        self.assertEqual(m.rewind_one_phase(0x014B800F,-178403)>>16,334)
        self.assertEqual(0x014B800F>>16,331)
    def test_uint32_wrap(self):
        self.assertEqual(m.rewind_one_phase(0,-1),1)
        self.assertEqual(m.rewind_one_phase(0,1),0xffffffff)
        self.assertEqual(m.rewind_one_phase(0xffffffff,-1),0)
    def test_invalid_range(self):
        for p,s in ((-1,0),(1<<32,0),(0,1<<31),(0,-(1<<31)-1)):
            with self.assertRaises(ValueError):m.rewind_one_phase(p,s)
    def test_unrecognized_binary_rejected(self):
        with self.assertRaisesRegex(ValueError,"capture"):
            m.normalize(bytes(65536),bytes(116606))
    def test_authentic_binary_is_not_distributed(self):
        self.assertEqual(len(m.EXPECTED_DS),64)
        self.assertEqual(len(m.EXPECTED_EXE),64)
        self.assertFalse(hasattr(m,"ORIGINAL_IMAGE"))
        self.assertFalse(hasattr(m,"ORIGINAL_PALETTE"))

if __name__=="__main__":
    unittest.main()
