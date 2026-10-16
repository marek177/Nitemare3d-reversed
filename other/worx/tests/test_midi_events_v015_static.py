"""Pinned original-byte evidence for the new v0.15 44EE/3A4D MIDI shell."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools'/'audit_midi_events_v015.py'
MANIFEST=ROOT/'data'/'worx21_midi_events_v015.json'
spec=importlib.util.spec_from_file_location('worx_midi_events_v015',SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Static(unittest.TestCase):
    def test_manifest_and_pinned_witness_counts(self):
        d=json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.assertEqual(d['original_v19_sha256'],module.BUILD['v19']['sha'])
        self.assertEqual(d['original_v20_sha256'],module.BUILD['v20']['sha'])
        self.assertEqual(d['v19_ip_minus_v20_ip'],4)
        self.assertEqual(d['status_nibble_data_length'],list(module.PARAM_COUNTS))
        self.assertEqual(len(d['v20_spans']),4)
        self.assertEqual(len(d['v20_anchors']),22)
        self.assertEqual(len(d['v20_branch_targets']),7)
        self.assertEqual(len(d['v20_near_calls']),2)
        self.assertEqual(sum(len(q['modified_operand_ips']) for q in d['crossversion_matches']),13)
        for e in d['v20_spans']:
            lo,hi,h=module.SPANS[e['id']]
            self.assertEqual((e['ip_start'],e['ip_end_exclusive'],e['length'],e['sha256']),
                             (f'{lo:04X}',f'{hi:04X}',hi-lo,h))
        for e in d['v20_anchors']:
            ip,signature=module.ANCHORS[e['id']]
            self.assertEqual((e['ip'],e['signature']),(f'{ip:04X}',signature))
        for e in d['crossversion_matches']:
            self.assertEqual(e['modified_operand_ips'],
                             [f'{ip:04X}' for ip in module.EXPECTED_SHIFTED[e['id']]])

    def test_original_bytes_with_negative_mutation_if_provided(self):
        old=os.getenv('WORX_N3D_V19_EXE')
        new=os.getenv('WORX_N3D_V20_EXE')
        if not old or not new:
            self.skipTest('private original EXE inputs must be explicitly supplied')
        checked=module.verify(Path(old),Path(new))
        self.assertEqual(checked['v20_spans'][0]['sha256'],module.SPANS['v20_channel_shell'][2])
        patched=bytearray(Path(new).read_bytes())
        patched[module.HEADER+module.BUILD['v20']['base']+0x451A]^=0x01
        with tempfile.TemporaryDirectory() as p:
            path=Path(p)/'mutated.exe';path.write_bytes(patched)
            with self.assertRaises(ValueError):module.verify(Path(old),path)

if __name__=='__main__':unittest.main()
