"""Optional original-binary audit and mandatory reproducible v0.14 signature checks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools'/'audit_audio_deep_v014.py'
MANIFEST=ROOT/'data'/'worx21_audio_deep_static_v014.json'
spec=importlib.util.spec_from_file_location('worx_v014_audit',SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestV014Static(unittest.TestCase):
    def test_manifest_is_pinned_to_independent_constants(self):
        data=json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.assertEqual(data['image_sha256'],mod.EXPECTED_IMAGE_SHA256)
        self.assertEqual(len(data['proofs']['slices']),6)
        self.assertEqual(len(data['proofs']['anchors']),25)
        self.assertEqual(len(data['proofs']['branch_targets']),11)
        for item in data['proofs']['slices']:
            lo,hi,expected=mod.SLICES[item['id']]
            self.assertEqual(item['start_ip'],f'{lo:04X}')
            self.assertEqual(item['end_exclusive'],f'{hi:04X}')
            self.assertEqual(item['bytes'],hi-lo)
            self.assertEqual(item['sha256'],expected)
        for item in data['proofs']['anchors']:
            ip,expected=mod.ANCHORS[item['id']]
            self.assertEqual(item['ip'],f'{ip:04X}')
            self.assertEqual(bytes.fromhex(item['bytes']),bytes.fromhex(expected))
        for item in data['proofs']['branch_targets']:
            a,_,b=mod.EDGES[item['id']]
            self.assertEqual((item['from_ip'],item['to_ip']), (f'{a:04X}',f'{b:04X}'))

    def test_original_byte_audit_if_supplied(self):
        fname=os.getenv('WORX_N3D_V20_EXE')
        if not fname:
            self.skipTest('original proprietary DOS EXE not distributed in reference package')
        path=Path(fname)
        proof=mod.audit(path)
        self.assertEqual(len(proof['proofs']['branch_targets']),11)
        self.assertEqual(len(proof['proofs']['anchors']),25)
        self.assertEqual(len(proof['proofs']['slices']),6)
        # Ensure a mutated binary cannot silently validate via regenerating hashes.
        raw=bytearray(path.read_bytes())
        raw[mod.HEADER_LENGTH+mod.CS_BASE+0x58C3] ^= 1
        with tempfile.TemporaryDirectory() as d:
            forged=Path(d)/'tampered.exe'; forged.write_bytes(raw)
            with self.assertRaises(ValueError):mod.audit(forged)

if __name__=='__main__': unittest.main()
