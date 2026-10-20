import importlib.util
import os
import struct
import tempfile
import unittest
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/'tools'/'n3d_d02n_producer_static_verify.py'
spec=importlib.util.spec_from_file_location('producer_audit',MODULE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ProducerStaticTests(unittest.TestCase):
    def test_near_branch(self):
        b=bytearray(32)
        b[4]=0xe8;struct.pack_into('<h',b,5,7)
        self.assertEqual(mod.target_near(b,4),14)
    def test_far_branch(self):
        b=bytearray(32)
        b[4]=0x9a
        struct.pack_into('<HH',b,5,0xE1C,0x0FD9)
        self.assertEqual(mod.target_far(b,4),0x10BAC)
    def test_invalid_call_helpers_fail_even_without_assertions(self):
        for raw,offset in [(b'',0),(b'\xe8',0),(b'\x90\0\0',0),(b'\xe8\0\0',-1)]:
            with self.assertRaises(ValueError): mod.target_near(raw,offset)
        for raw,offset in [(b'',0),(b'\x9a',0),(b'\x90\0\0\0\0',0),(b'\x9a\0\0\0\0',-1)]:
            with self.assertRaises(ValueError): mod.target_far(raw,offset)

    def test_original_fingerprint_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fake.exe'
            p.write_bytes(b'MZ'+b'\0'*1024)
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                mod.audit_file(p)
    def test_original_private_if_set(self):
        env=os.getenv('N3D_D02N_ORIGINAL_EXE')
        if not env:self.skipTest('No private DOS 2.0 original bound')
        d=mod.audit_file(Path(env))
        self.assertEqual(d['direct_call_edges'],10)
        self.assertEqual(d['opcode_windows'],59)
        self.assertEqual(d['count_literal_refs'],15)
        self.assertEqual(len(d['door_orientation_table']),16)
        self.assertEqual(d['count_literal_writer'],['0x10BF6'])
        for cls in d['door_orientation_table']:
            self.assertIn(cls['orientation'],('0/1','2/3'))

if __name__=='__main__':unittest.main()
