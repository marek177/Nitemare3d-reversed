"""Synthetic-only tests for renderer static-vs-runtime coverage accounting."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_v071_dos20_opcode_gap_audit as audit

class GapTests(unittest.TestCase):
    def test_span_lengths(self):
        self.assertEqual([end-start+1 for start,end,_ in audit.ROUTINES.values()], [1060,324,672])
        self.assertEqual(sum(end-start+1 for group in audit.RUNTIME_HOLES.values() for start,end in group),67)

    def test_coverage(self):
        image = bytes(0x200+0x104BE)
        report = audit.audit_bytes(image)
        self.assertEqual(report["routine_bytes"],2056)
        self.assertEqual(report["runtime_missing_bytes"],67)
        self.assertEqual(report["evidence"],"STATIC_BYTES_ONLY")
        self.assertEqual(report["original_vs_port_indexed_framebuffer_parity"],"NOT_TESTED")
        self.assertEqual([len(part["holes"]) for part in report["routines"].values()],[1,0,4])

    def test_mutated_hole(self):
        image=bytearray(0x200+0x104BE)
        image[0x200+0xCD9D]=99
        report=audit.audit_bytes(bytes(image))
        self.assertFalse(report["routines"]["CAB8_projection"]["holes"][0]["all_zero"])
        self.assertTrue(report["routines"]["1021E_visibility"]["holes"][0]["all_zero"])

    def test_boundaries(self):
        image=bytes(0x200+0x104BE)
        with self.assertRaises(ValueError):
            audit.image_bytes(image,-1,1)
        with self.assertRaises(ValueError):
            audit.image_bytes(image,0x104BE,0x104BE)
        with self.assertRaises(ValueError):
            audit.audit_bytes(image[:-1])

    def test_version_guard(self):
        with self.assertRaises(ValueError):
            audit.verify_original_exe(bytes(116606))
        with self.assertRaises(ValueError):
            audit.header_size(bytes(32))

if __name__ == "__main__":
    unittest.main()
