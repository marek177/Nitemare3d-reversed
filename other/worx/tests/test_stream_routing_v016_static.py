"""Pinned original MZ byte evidence for v0.16 5F3E streamer routing."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/'tools'/'audit_stream_routing_v016.py'
DATA=BASE/'data'/'worx21_stream_routing_v016.json'
spec=importlib.util.spec_from_file_location('stream_v016',SRC)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class StreamOriginal(unittest.TestCase):
    def test_manifest_machine_constants(self):
        d=json.loads(DATA.read_text(encoding='utf8'))
        self.assertEqual(d['dos_v19_unpacked_sha256'],module.BUILD['v19'][0])
        self.assertEqual(d['dos_v20_unpacked_sha256'],module.BUILD['v20'][0])
        self.assertEqual(d['span'],{'first_ip':f'{module.START:04X}',
            'end_exclusive':f'{module.END:04X}','bytes':module.END-module.START,
            'sha256':module.PIN})
        self.assertEqual(d['operand_delta_v19_ip_plus4'],[f'{i:04X}' for i in module.SHIFT])
        self.assertEqual(len(d['anchors']),17)
        self.assertEqual(len(d['edges']),13)
        self.assertEqual(len(d['calls']),4)
        self.assertEqual(d['non_operand_differences'],0)
        self.assertEqual({e['id'] for e in d['edges']},set(module.BRANCHES))
        self.assertEqual({e['id'] for e in d['calls']},set(module.CALLS))
    def test_original_private_images_and_negative_mutation(self):
        v19=os.getenv('WORX_N3D_V19_EXE');v20=os.getenv('WORX_N3D_V20_EXE')
        if not(v19 and v20):self.skipTest('original EXEs are private, optional input')
        self.assertEqual(module.verify(Path(v19),Path(v20)),json.loads(DATA.read_text(encoding='utf8')))
        corrupted=bytearray(Path(v20).read_bytes())
        corrupted[module.HEADER+module.BUILD['v20'][2]+0x5F70]^=1
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.exe';bad.write_bytes(corrupted)
            with self.assertRaises(ValueError):module.verify(Path(v19),bad)
if __name__=='__main__':unittest.main()
