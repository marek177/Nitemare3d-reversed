"""Synthetic fixtures; neither execution of the original nor remake parity."""
import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import n3d_gameplay_diff as d

class GameDiffTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.ref,self.rm=self.make('ref','original')
        self.cand,self.cm=self.make('cand','remake')
    def make(self,name,kind,edit=None):
        path=self.root/(name+'.csv')
        rows=[dict(sample=i,tick=i,x=1440+i*5,y=3616-i*10,direction=i*5,
                   input_mask='0x0080',hp=100,ammo=50-i,weapon=1,object_count=3,
                   guard_count=2,projectile_count=0,render_count=i) for i in range(3)]
        if edit: edit(rows)
        with path.open('w',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=d.FIELDS)
            w.writeheader()
            w.writerows(rows)
        meta=self.root/(name+'.json')
        meta.write_text(json.dumps(dict(schema='n3d.gameplay-state.v1',
             kind=kind,build=kind,capture_id='E1M1',begin='start',end='end',
             closed=True,row_count=len(rows),csv_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
        return path,meta
    def report(self):
        return d.run(self.ref,self.cand,self.rm,self.cm)
    def test_match_is_not_parity_proof(self):
        r=self.report()
        self.assertTrue(r['comparison']['equal'])
        self.assertTrue(r['boundaries_verified'])
        self.assertFalse(r['parity_proven'])
        self.assertFalse(r['original_runtime_verified'])
    def test_first_difference(self):
        self.cand,self.cm=self.make('cand','remake',lambda r:r[1].update(x=999))
        r=self.report()['comparison']
        self.assertEqual(r['sample'],1)
        self.assertEqual(r['fields']['x']['candidate'],999)
    def test_tick_alignment(self):
        self.cand,self.cm=self.make('cand','remake',lambda r:r[2].update(tick=8))
        self.assertEqual(self.report()['comparison']['classification'],'tick_alignment')
    def test_missing_sample(self):
        self.cand,self.cm=self.make('cand','remake',lambda r:r[1].update(sample=3))
        with self.assertRaisesRegex(d.TraceError,'noncontiguous'): self.report()
    def test_bad_mask(self):
        self.cand,self.cm=self.make('cand','remake',lambda r:r[1].update(input_mask='0x10000'))
        with self.assertRaisesRegex(d.TraceError,'uint16'): self.report()
    def test_bad_direction(self):
        self.cand,self.cm=self.make('cand','remake',lambda r:r[1].update(direction=360))
        with self.assertRaisesRegex(d.TraceError,'direction'): self.report()
    def test_tampered_digest(self):
        self.cand.write_bytes(self.cand.read_bytes()+b'\n')
        with self.assertRaisesRegex(d.TraceError,'SHA256'): self.report()
    def test_wrong_boundary(self):
        m=json.loads(self.cm.read_text())
        m['end']='different'
        self.cm.write_text(json.dumps(m))
        self.assertFalse(self.report()['boundaries_verified'])
    def test_wrong_manifest_kind(self):
        m=json.loads(self.cm.read_text())
        m['kind']='original'
        self.cm.write_text(json.dumps(m))
        with self.assertRaisesRegex(d.TraceError,'kind'): self.report()
    def test_duplicate_header(self):
        self.cand.write_text('sample,sample\n0,0\n')
        with self.assertRaisesRegex(d.TraceError,'duplicated'): d.read(self.cand)
    def test_unattested_cli_is_failure(self):
        self.assertEqual(d.main([str(self.ref),str(self.cand),'--output',str(self.root/'out')]),1)
    def test_attested_cli_success(self):
        self.assertEqual(d.main([str(self.ref),str(self.cand),
            '--original-manifest',str(self.rm),'--remake-manifest',str(self.cm),
            '--output',str(self.root/'out')]),0)

if __name__=='__main__':
    unittest.main()
