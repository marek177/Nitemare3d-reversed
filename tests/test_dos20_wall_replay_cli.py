"""Executable integration tests on synthetic DS/IMG/frame files, no game assets."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

PROGRAM = os.environ.get('N3D_DOS20_WALL_REPLAY')
if '--program' in sys.argv:
    at = sys.argv.index('--program')
    PROGRAM = sys.argv[at+1]
    del sys.argv[at:at+2]


@unittest.skipUnless(PROGRAM, 'build replay executable and pass --program or N3D_DOS20_WALL_REPLAY')
class SnapshotPipeline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ds = bytearray(65536)
        self.img = bytearray(0xBC00 + 2*(10+4096))
        self.vec = 0x62AC
        self.w16(0x4D64, 1)
        for at, value in [(0x415C,1),(0x41B2,0),(0x41B4,1024),
                          (0x4162,1440),(0x4164,3620),(0x4550,160)]: self.w16(at,value)
        self.w32(0x3686,81715200)
        self.w32(0x368A,459074)
        for i in range(256): self.ds[0x4A64+3*i:0x4A64+3*i+3] = bytes([i%64,i//64,0])
        self.ds[self.vec] = 5
        self.ds[self.vec+5] = 8
        self.ds[self.vec+6] = 1
        for delta,value in [(12,1440),(14,3620),(16,1504),(18,3620),(20,0),(24,319)]:
            self.w16(self.vec+delta,value)
        for x in range(8,312): self.w16(0x4564+2*x,self.vec)
        for at,value in [(0x4D6E,self.vec),(0x4D70,8),(0x4D72,331),
                         (0x4D74,311),(0x4D76,331)]: self.w16(at,value)
        self.w32(0x4D7C,331<<16)
        struct.pack_into('<I',self.img,4*5,0xBC00)
        self.img[0x800+5*90+2]=2
        for i,color in enumerate((42,79)):
            start=0xBC00+i*(10+4096)
            self.img[start:start+2]=bytes((64,64))
            self.img[start+10:start+10+4096]=bytes([color])*4096
        self.background=bytes([171])*64000
        self.reference=self.expected(42)
        self.output=self.root/'output'

    def w16(self, at, value): struct.pack_into('<H',self.ds,at,value)
    def w32(self, at, value): struct.pack_into('<I',self.ds,at,value)
    def expected(self,color):
        result=bytearray(self.background)
        for y in range(59,101): result[y*320+8:y*320+312]=bytes([color])*304
        return bytes(result)

    def run_replay(self, reference=True, extra=()):
        for name,content in [('DS.bin',self.ds),('IMG.1',self.img),
                             ('background.idx',self.background),('reference.idx',self.reference)]:
            (self.root/name).write_bytes(content)
        inputs = {p.name:hashlib.sha256(p.read_bytes()).digest() for p in self.root.iterdir() if p.is_file()}
        args=[str(Path(PROGRAM).resolve()),'--ds',str(self.root/'DS.bin'),
              '--img',str(self.root/'IMG.1'),'--vec-count','1',
              '--background-frame',str(self.root/'background.idx'),'--output-dir',str(self.output)]
        if reference: args+=['--reference-frame',str(self.root/'reference.idx')]
        result=subprocess.run(args+list(extra),capture_output=True,text=True,timeout=30)
        for name,digest in inputs.items():
            self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).digest(),digest)
        return result

    def test_pipeline_writes_expected_pixels_and_material_ledger(self):
        p=self.run_replay()
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual((self.output/'candidate.idx').read_bytes(),self.reference)
        mask=(self.output/'generated.mask').read_bytes()
        self.assertEqual(sum(mask),304*42)
        self.assertEqual(report['generated_wall_pixels'],12768)
        self.assertEqual(report['wall_pixel_mismatches'],0)
        self.assertIsNone(report['first_wall_mismatch'])
        self.assertIsNone(report['wall_mismatch_bounds'])
        self.assertTrue(report['wall_pixels_equal'])
        self.assertFalse(report['full_frame_parity_proven'])
        self.assertFalse(report['original_recording_authenticated'])
        rows=list(csv.DictReader(io.StringIO((self.output/'columns.csv').read_text())))
        self.assertEqual(len(rows),304)
        self.assertEqual(rows[152]['screen_x'],'160')
        self.assertEqual(rows[152]['physical_u'],'0')
        self.assertEqual(rows[152]['shade_index'],'0')
        self.assertEqual((self.output/'candidate.u-valid').read_bytes(),bytes([1])*304)

    def test_animation_frame_is_used_by_actual_raster(self):
        self.ds[self.vec+3]=1
        self.reference=self.expected(79)
        p=self.run_replay()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.output/'candidate.idx').read_bytes(),self.reference)

    def test_one_generated_pixel_difference_fails_with_location(self):
        wrong=bytearray(self.reference)
        wrong[59*320+18]=43
        self.reference=bytes(wrong)
        p=self.run_replay()
        self.assertEqual(p.returncode,1,p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual(report['wall_pixel_mismatches'],1)
        self.assertEqual(report['first_wall_mismatch_pixel'],59*320+18)
        first=report['first_wall_mismatch']
        self.assertEqual((first['x'],first['y'],first['candidate_index'],first['reference_index']), (18,59,42,43))
        self.assertEqual((first['owner'],first['span_index'],first['wall_id']), (self.vec,0,5))
        rows=list(csv.DictReader(io.StringIO((self.output/'columns.csv').read_text())))
        self.assertEqual(sum(int(r['mismatch_pixels']) for r in rows),1)
        self.assertEqual(rows[10]['mismatch_pixels'],'1')
        self.assertEqual(sum(int(r['compared_pixels']) for r in rows),12768)

    def test_first_difference_is_row_major_with_inclusive_bounds(self):
        wrong=bytearray(self.reference)
        for x,y in [(8,100),(311,59),(160,80)]: wrong[y*320+x]=43
        self.reference=bytes(wrong)
        p=self.run_replay()
        self.assertEqual(p.returncode,1,p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual(report['wall_pixel_mismatches'],3)
        self.assertEqual(report['first_wall_mismatch_pixel'],59*320+311)
        self.assertEqual(report['first_wall_mismatch']['x'],311)
        self.assertEqual(report['wall_mismatch_bounds'],dict(left=8,top=59,right=311,bottom=100))

    def test_background_difference_is_not_wall_parity(self):
        wrong=bytearray(self.reference);wrong[0]=0;self.reference=bytes(wrong)
        p=self.run_replay()
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertTrue(report['wall_pixels_equal'])
        self.assertFalse(report['full_frame_parity_proven'])
        self.assertEqual((self.output/'candidate.idx').read_bytes()[0],171)

    def test_missing_reference_has_no_equality_verdict(self):
        p=self.run_replay(reference=False)
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertIsNone(report['wall_pixels_equal'])
        self.assertIsNone(report['wall_pixel_mismatches'])
        self.assertIsNone(report['first_wall_mismatch'])
        self.assertIsNone(report['wall_mismatch_bounds'])
        rows=list(csv.DictReader(io.StringIO((self.output/'columns.csv').read_text())))
        self.assertTrue(all(r['compared_pixels']=='0' and r['mismatch_pixels']=='' for r in rows))
        self.assertEqual(report['wall_pixels_compared'],0)

    def test_empty_wall_coverage_is_not_vacuous_parity(self):
        self.w32(0x4D7C,0xFFFF0000)  # signed Q4 phase -1: all columns culled
        p=self.run_replay()
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual(report['generated_wall_pixels'],0)
        self.assertEqual(report['culled_columns'],304)
        self.assertIsNone(report['wall_pixels_equal'])
        self.assertEqual((self.output/'candidate.idx').read_bytes(),self.background)
        self.assertEqual((self.output/'candidate.u-valid').read_bytes(),bytes(304))
        rows=list(csv.DictReader(io.StringIO((self.output/'columns.csv').read_text())))
        self.assertEqual(len(rows),304)
        self.assertTrue(all(r['physical_u']=='' and None not in r for r in rows))

    def patterned_replay(self, width, displacement=331):
        # Column and row coefficients differ: transposition, squashed 128-wide
        # faces, constant U, missing carry and transparent-zero errors diverge.
        self.w16(0x4162,1472)  # local=32, so center physical U=96 for width128
        self.w16(0x4D72,displacement); self.w16(0x4D76,displacement)
        self.w32(0x4D7C,displacement<<16)
        self.img=bytearray(0xBC00+10+width*64)
        struct.pack_into('<I',self.img,4*5,0xBC00)
        self.img[0x800+5*90+2]=1
        self.img[0xBC00:0xBC02]=bytes((width,64))
        for u in range(width):
            for v in range(64): self.img[0xBC00+10+u*64+v]=(17*u+3*v)&255
        bottom=(80*16+displacement)//16
        n=2*(bottom-80)+1
        step=(64<<16)//n
        first=bottom-n if bottom<155 else 4
        count=n+1 if bottom<155 else 152
        source=0 if bottom<155 else (((n-152)*64*65536)//n)//2
        expected=bytearray(self.background)
        expected_u=[]
        trunc=lambda value,denom: (abs(value)//denom)*(-1 if value<0 else 1)
        for x in range(8,312):
            projected=trunc(trunc((x-160)*459074,displacement),1024)
            u=(-(projected+32))&(width-1)
            expected_u.append(u)
            for row in range(count):
                v=(source+row*step)>>16
                expected[(first+row)*320+x]=(17*u+3*v)&255
        self.reference=bytes(expected)
        p=self.run_replay()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.output/'candidate.idx').read_bytes(),self.reference)
        self.assertEqual((self.output/'candidate.u').read_bytes(),bytes(expected_u))
        report=json.loads(p.stdout)
        self.assertEqual(report['generated_wall_pixels'],304*count)
        # Ensure the fixture really checks varying U/V and the second face.
        self.assertGreater(len(set(expected_u)),2)
        if width==128: self.assertEqual(expected_u[152],96)
        self.assertIn(0,self.reference[first*320+8:(first+count)*320])

    def test_patterned_64_wide_texture_uv_and_fixed_point_carry(self):
        self.patterned_replay(64)

    def test_patterned_128_wide_texture_preserves_second_face(self):
        self.patterned_replay(128)

    def test_patterned_clipped_wall_uses_vertical_source_offset(self):
        self.patterned_replay(128,2000)

    def reject_without_output(self, extra=()):
        p=self.run_replay(extra=extra)
        self.assertEqual(p.returncode,2,p.stdout+p.stderr)
        self.assertFalse(self.output.exists())

    def test_bad_ds_does_not_create_output(self):
        self.ds.pop();self.reject_without_output()

    def test_invalid_shade_rejected(self):
        self.w16(0x6278,8);self.reject_without_output()

    def test_wrong_cache_selector_rejected(self):
        self.ds[self.vec+4]=1;self.reject_without_output()

    def test_faulting_cedc_divisor_rejected(self):
        self.w16(0x41B4,0);self.reject_without_output()

    def test_existing_output_is_not_modified(self):
        self.output.mkdir();sentinel=self.output/'keep.txt';sentinel.write_text('keep')
        p=self.run_replay()
        self.assertEqual(p.returncode,2)
        self.assertEqual(list(self.output.iterdir()),[sentinel])
        self.assertEqual(sentinel.read_text(),'keep')

    def test_unknown_option_and_bad_page_rejected(self):
        self.reject_without_output(('--page','2'))
        self.reject_without_output(('--surprise','1'))

if __name__=='__main__': unittest.main()
