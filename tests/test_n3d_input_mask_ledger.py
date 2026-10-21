import io
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from n3d_input_mask_ledger import read_rows,audit
def rows(body):
    return read_rows(io.StringIO("phase,expected_mask,observed_mask,stable\n"+body))
class InputLedgerTests(unittest.TestCase):
    def test_all_eight(self):
        masks=(0,0x80,0x100,0x180,0x200,0x280,0x300,0x380)
        s="".join(f"p{n},0x{n:04X},0x{n:04X},1\n" for n in masks)
        result=audit(rows(s))
        self.assertEqual(result["samples"],8)
        self.assertTrue(result["all_eight_masks_observed"])
        self.assertFalse(result["original_vs_remake_parity"])
        self.assertFalse(result["tick_atomic"])
    def test_transition_boundary(self):
        r=audit(rows("a,0x80,0,0\na,0x80,0x80,1\n"))
        self.assertEqual(r["transition_mismatches"],1)
        self.assertEqual(r["stable_mismatches"],0)
    def test_real_stable_failure(self):
        self.assertEqual(audit(rows("a,0x80,0,1\n"))["stable_mismatches"],1)
    def test_bad_masks(self):
        for value in ("0x400","0x382","-1","fish"):
            with self.subTest(value=value),self.assertRaises(ValueError):
                rows(f"a,{value},0,1\n")
    def test_bad_stable(self):
        with self.assertRaises(ValueError):rows("a,0,0,maybe\n")
    def test_empty_phase(self):
        with self.assertRaises(ValueError):rows(",0,0,1\n")
    def test_short_row(self):
        with self.assertRaises(ValueError):rows("a,0,0\n")
    def test_long_row(self):
        with self.assertRaises(ValueError):rows("a,0,0,1,junk\n")
    def test_empty(self):
        with self.assertRaises(ValueError):rows("")
    def test_not_all_masks(self):
        self.assertFalse(audit(rows("a,0,0,1\nb,0x380,0,0\n"))["all_eight_masks_observed"])
    def test_reordered_columns(self):
        r=read_rows(io.StringIO("stable,observed_mask,phase,expected_mask\n1,0x80,a,0x80\n"))
        self.assertEqual(audit(r)["matching_samples"],1)
    def test_duplicate_header_rejected(self):
        with self.assertRaises(ValueError):
            read_rows(io.StringIO("phase,expected_mask,observed_mask,stable,stable\n"))
if __name__=="__main__":unittest.main()
