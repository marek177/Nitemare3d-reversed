"""Synthetic-only DOS2 22CA texture-U trace tests. No game executable or assets."""
import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import n3d_v077_dos20_u_witness as witness
from n3d_v073_dos2_gap_trace_witness import HEAD, COMMON, CPU

CALLS=(0x26A6,0x26AB,0x26B0,0x26C9,0x22D6,0x26CC,0x26CF)

def fixture(nframes=1,broken=None):
    img=bytearray(0x10500)
    for ip,sz in witness.SIZE.items():
        img[ip:ip+sz]=bytes([0x90])*sz
    img[0x26A6:0x26AB]=bytes.fromhex("9a0c077d0c")
    stream=io.BytesIO()
    stream.write(HEAD.pack(b"N3DTRC01",1,0))
    seq=0
    for frame in range(nframes):
        for x in range(8,312):
            u=(x+frame)&127
            if x==101:u=(u-1)&127
            for off in CALLS:
                seq+=1
                code=bytes(img[off:off+witness.SIZE[off]])
                if off==0x26A6: code=bytes.fromhex("9a0c07a114")
                if broken=="opcode" and x==101 and off==0x26CF:code=b"\xcc"
                code=(code+bytes(16))[:16]
                ax={
                    0x26A6:frame%4,0x26AB:7,0x26B0:7,0x26C9:128,
                    0x22D6:128,0x26CC:u,0x26CF:u,
                }[off]
                if broken=="return" and x==101 and off==0x26CF:ax=(u+1)&127
                if broken=="width" and x==101 and off==0x26C9:ax=17
                si={0x26B0:7,0x26C9:x+frame,0x22D6:0x62AC}.get(off,0)
                cx=x if off==0x22D6 else 0
                cs=(witness.BASE_LINEAR+off)//16
                ip=(witness.BASE_LINEAR+off)%16
                row=CPU.pack(cs,0,0,0,0,0,ip,cs*16+ip,0,
                             ax,0,cx,0,si,x,0,0,code,16,0,0,0)
                stream.write(COMMON.pack(b"I",1,96,seq,seq))
                stream.write(row)
    return bytes(img),stream.getvalue()


class UWitnessTests(unittest.TestCase):
    def check(self,nframes=1,broken=None):
        image,data=fixture(nframes,broken)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"synthetic.zip"
            with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("evidence/session-test/trace-000000.n3dt",data)
            with zipfile.ZipFile(p) as z:
                return witness.extract_session(z,"session-test",image)

    def test_all_304_stated_columns(self):
        frames,stats=self.check()
        self.assertEqual(len(frames),1)
        self.assertEqual([r["x"] for r in frames[0]],list(range(8,312)))
        self.assertEqual(stats["original_u_calls"],304)
        self.assertEqual(stats["callsite_counts"]["u_final"],304)
        self.assertEqual([r["x"] for r in frames[0] if r["edge_corrected"]],[101])
        self.assertEqual(frames[0][93]["u"],(101-1)&127)

    def test_two_frames_split_by_reset_to_x8(self):
        frames,stats=self.check(2)
        self.assertEqual([len(x) for x in frames],[304,304])
        self.assertEqual(stats["original_u_calls"],608)
        self.assertNotEqual(bytes(r["u"] for r in frames[0]),
                            bytes(r["u"] for r in frames[1]))

    def test_relocated_far_call_checked(self):
        image,blob=fixture()
        self.assertEqual(image[0x26A6:0x26AB].hex(),"9a0c077d0c")
        self.assertIn(bytes.fromhex("9a0c07a114"),blob)

    def test_wrong_return_fails(self):
        with self.assertRaisesRegex(ValueError,"return U mismatch"):
            self.check(broken="return")

    def test_wrong_opcode_fails(self):
        with self.assertRaisesRegex(ValueError,"opcode mismatch"):
            self.check(broken="opcode")

    def test_wrong_width_fails(self):
        with self.assertRaisesRegex(ValueError,"Unsupported"):
            self.check(broken="width")

    def test_wrong_source_exe_fails_sha(self):
        import n3d_v071_dos20_opcode_gap_audit as pinned
        with self.assertRaises(ValueError):
            pinned.verify_original_exe(bytes(pinned.EXE_SIZE))

    def test_original_u_numeric_pair_first_difference(self):
        import n3d_v077_original_u_diff as compare
        original=bytearray(304)
        original[101-8]=127
        candidate=bytearray(original)
        candidate[101-8]=0
        result=compare.compare(bytes(original),bytes(candidate))
        self.assertEqual(result["different_U_columns"],1)
        self.assertEqual(result["first_wrong_screen_x"],101)
        self.assertEqual(result["original_vs_remake_framebuffer"],"NOT_TESTED")
        self.assertTrue(compare.compare(bytes(original),bytes(original))["numeric_U_equal"])

    def test_u_numeric_diff_rejects_truncated_buffer(self):
        import n3d_v077_original_u_diff as compare
        with self.assertRaisesRegex(ValueError,"304 bytes"):
            compare.compare(bytes(303),bytes(304))

    def test_event_register_fields_are_prestate(self):
        image,blob=fixture()
        with io.BytesIO(blob) as stream:
            row=next(iterate_cpu_bridge(stream))
        self.assertEqual(row["ax"],0)
        self.assertEqual(row["di"],8)

def iterate_cpu_bridge(stream):
    from n3d_v073_dos2_gap_trace_witness import iterate_cpu
    return iterate_cpu(stream)


if __name__=="__main__":
    unittest.main()
