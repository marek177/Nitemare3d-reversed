"""Synthetic N3DTRC01 CPU witness tests. Never include commercial opcode bytes."""
import io
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import n3d_v073_dos2_gap_trace_witness as w


LOAD_SEG = 0x0824


def make_image():
    image=bytearray(0x11000)
    image[0xCAB8]=0x90
    image[0xCBF2:0xCBF6]=bytes.fromhex("0F 84 E0 02")
    image[0xCBF6]=0x90
    image[0xCED6]=0x90
    image[0xCD9C:0xCDA4]=bytes([0x90])*8
    image[0x1021E]=0x90
    image[0x10408:0x1040C]=bytes([0x90])*4
    image[0xFEFA]=0x90
    return bytes(image)


def cpu_event(image, offset, event_num, code=None, code_valid=16, load_seg=LOAD_SEG,
              protected=0, code32=0):
    cs = (load_seg + offset//16) & 0xFFFF
    ip = offset % 16
    if code is None:
        code=(image[offset:offset+16]+bytes(16))[:16]
    code=(code+bytes(16))[:16]
    body=w.CPU.pack(cs,0,0,0,0,0,ip,cs*16+ip,0,
                    0,0,0,0,0,0,0,0,code,code_valid,code32,protected,0)
    assert len(body)==76
    return w.COMMON.pack(b"I",1,96,event_num,event_num)+body


def make_trace(image, offsets, modify=None):
    raw=w.HEAD.pack(w.MAGIC,1,0)
    for j,offset in enumerate(offsets,1):
        kw=modify(j,offset) if modify else {}
        raw+=cpu_event(image,offset,j,**kw)
        if j==1:
            raw+=w.COMMON.pack(b"F",1,20,j*10,j) # unrelated record
    return io.BytesIO(raw)


class WitnessTests(unittest.TestCase):
    def test_sizes_and_header(self):
        self.assertEqual((w.HEAD.size,w.COMMON.size,w.CPU.size),(16,20,76))
        rows=list(w.iterate_cpu(make_trace(make_image(),[0xCAB8,0xCD9D])))
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[1]["code_valid"],16)

    def test_lookahead_is_not_execution(self):
        image=make_image()
        data=w.witness_one(make_trace(image,[0xCD9C]),image,LOAD_SEG)
        section=data["routines"]["CAB8_projection"]
        self.assertGreater(section["lookahead_matching_gap_bytes"],0)
        self.assertEqual(section["executed_decoded_gap_bytes"],0)
        self.assertFalse(section["gap_runtime_proven_complete"])

    def test_execution_at_gap(self):
        image=make_image()
        data=w.witness_one(make_trace(image,[0xCD9D]),image,LOAD_SEG)
        section=data["routines"]["CAB8_projection"]
        self.assertEqual(section["executed_decoded_gap_bytes"],1)
        self.assertEqual(section["executed_gap_instruction_starts"],["0x0CD9D"])

    def test_second_routine_gap(self):
        image=make_image()
        data=w.witness_one(make_trace(image,[0x10408]),image,LOAD_SEG)
        section=data["routines"]["1021E_visibility"]
        self.assertEqual(section["executed_decoded_gap_bytes"],1)
        self.assertEqual(section["static_gap_bytes"],16)

    def test_corrupted_instruction_not_accepted(self):
        image=make_image()
        def altered(j,off):
            return {"code":bytes([0xCC])+image[off+1:off+16]}
        result=w.witness_one(make_trace(image,[0xCD9D],altered),image,LOAD_SEG)
        p=result["routines"]["CAB8_projection"]
        self.assertEqual(p["validated_instruction_events"],0)
        self.assertEqual(p["executed_decoded_gap_bytes"],0)
        self.assertEqual(p["mismatch_events_first_or_executed_byte"],1)

    def test_truncated_cpu_window_not_executed(self):
        image=make_image()
        def short(j,off):return {"code_valid":1}
        result=w.witness_one(make_trace(image,[0xCBF2],short),image,LOAD_SEG)
        self.assertEqual(result["routines"]["CAB8_projection"]["insufficient_window_events"],1)

    def test_branch_to_early_return(self):
        image=make_image()
        result=w.witness_one(make_trace(image,[0xCBF2,0xCED6]),image,LOAD_SEG)
        self.assertEqual(result["routines"]["CAB8_projection"]
                         ["observed_branch_targets_from_CBF2"]["0x0CED6"],1)

    def test_branch_fallthrough(self):
        image=make_image()
        result=w.witness_one(make_trace(image,[0xCBF2,0xCBF6]),image,LOAD_SEG)
        self.assertEqual(result["routines"]["CAB8_projection"]
                         ["observed_branch_targets_from_CBF2"]["0x0CBF6"],1)

    def test_incorrect_base_no_fake_witness(self):
        image=make_image()
        result=w.witness_one(make_trace(image,[0xCD9D]),image,0x0000)
        self.assertEqual(result["routines"]["CAB8_projection"]["instruction_events"],0)

    def test_reject_incorrect_header(self):
        data=make_trace(make_image(),[0xCAB8]).getvalue()
        with self.assertRaises(ValueError):
            list(w.iterate_cpu(io.BytesIO(b"INVALID!"+data[8:])))
        with self.assertRaises(ValueError):
            list(w.iterate_cpu(io.BytesIO(data[:-1])))

    def test_reject_invalid_load_segment(self):
        with self.assertRaises(ValueError):
            w.witness_one(make_trace(make_image(),[0xCAB8]),make_image(),-1)

    def test_authenticated_original_guard(self):
        with self.assertRaises(ValueError):
            w.original.verify_original_exe(bytes(w.original.EXE_SIZE))

    def test_window_not_runtime_assertion(self):
        image=make_image()
        report=w.witness_one(make_trace(image,[0xCAB8]),image,LOAD_SEG)
        self.assertEqual(report["original_vs_remake_pixel_parity"],"NOT_TESTED")
        self.assertFalse(report["routines"]["CAB8_projection"]["semantic_equivalence_proven"])


if __name__=="__main__":
    unittest.main()
