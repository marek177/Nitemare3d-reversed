"""Synthetic-only 16-bit CFG disassembler checks. No original DOS2 opcode bytes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_v072_dos2_gap_cfg_probe as cfg


def fixture(instruction_bytes: bytes, base=0x100, extra=128):
    b = bytearray(base + len(instruction_bytes) + extra)
    b[base:base+len(instruction_bytes)] = instruction_bytes
    return bytes(b)


class CFGTests(unittest.TestCase):
    def test_conditional_takes_both_paths(self):
        # JZ +4; MOV AX,1234h; RET; MOV AX,5678h; RET.
        img=fixture(bytes.fromhex("74 04 B8 34 12 C3 B8 78 56 C3"))
        r=cfg.probe_image(img,0x100,0x109,((0x106,0x109),))
        self.assertEqual(r["direct_cfg_decoded_gap_bytes"],4)
        self.assertEqual(r["not_reached_by_direct_cfg_gap_bytes"],0)
        self.assertEqual(r["decode_errors_or_overlaps"],[])
        self.assertFalse(r["branches_proved_executed"] if "branches_proved_executed" in r else False)

    def test_unconditional_skip_not_called_dead_code(self):
        # JMP +4; bytes below are never reached from this local direct entry.
        img=fixture(bytes.fromhex("EB 04 B8 34 12 C3 B8 78 56 C3"))
        r=cfg.probe_image(img,0x100,0x109,((0x102,0x105),))
        self.assertEqual(r["not_reached_by_direct_cfg_gap_bytes"],4)
        self.assertIn("NOT dead-code proof",r["warning"])
        self.assertEqual(len(r["instructions_touching_gap"]),0)

    def test_indirect_jump_flagged_unresolved(self):
        img=fixture(bytes.fromhex("FF E0 C3"))
        r=cfg.probe_image(img,0x100,0x102,((0x102,0x102),))
        self.assertEqual(len(r["indirect_edges_unresolved"]),1)
        self.assertEqual(r["not_reached_by_direct_cfg_gap_bytes"],1)

    def test_instruction_crosses_end(self):
        img=fixture(bytes.fromhex("B8 34 12"))
        r=cfg.probe_image(img,0x100,0x101,((0x100,0x101),))
        self.assertTrue(any(p["error"]=="instruction_crosses_function_boundary"
                            for p in r["decode_errors_or_overlaps"]))

    def test_out_of_range_rejected(self):
        img=fixture(bytes.fromhex("C3"))
        for a,b in ((-1,0x100),(0x101,0x100),(0x100,len(img))):
            with self.assertRaises(ValueError):cfg.probe_image(img,a,b,())

    def test_load_image_over_64kb_normalizes_near_ip(self):
        img=fixture(bytes.fromhex("74 04 B8 34 12 C3 B8 78 56 C3"),base=0x1021e)
        r=cfg.probe_image(img,0x1021e,0x10227,((0x10224,0x10227),))
        self.assertEqual(r["direct_cfg_decoded_gap_bytes"],4)
        self.assertEqual(r["decode_errors_or_overlaps"],[])

    def test_original_exe_sha_is_mandatory(self):
        with self.assertRaises(ValueError):
            cfg.audit_executable(bytes(116606))

    def test_no_runtime_or_full_parity_claim(self):
        img=fixture(bytes.fromhex("EB 04 B8 34 12 C3 B8 78 56 C3"))
        r=cfg.probe_image(img,0x100,0x109,((0x102,0x105),))
        self.assertEqual(r["evidence_level"],"STATIC_DIRECT_EDGE_CFG_HEURISTIC")
        self.assertEqual(r["status"],"PARTIAL_REQUIRES_MANUAL_ASM_AND_ORIGINAL_RUNTIME")


if __name__=="__main__":
    unittest.main()
