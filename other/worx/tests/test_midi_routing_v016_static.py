"""Original machine-byte pinning for RE-MAX v0.16; no private EXE in repo."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools'/'audit_midi_routing_v016.py'
EVIDENCE=ROOT/'data'/'worx21_midi_routing_v016.json'
spec=importlib.util.spec_from_file_location('worx_route_v016',SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MidiRouteStaticV016(unittest.TestCase):
    def test_saved_manifest_consistent_with_machine_pins(self):
        doc=json.loads(EVIDENCE.read_text(encoding='utf-8'))
        self.assertEqual(doc['v19_sha256_image'],module.BUILDS['v19']['image_sha256'])
        self.assertEqual(doc['v20_sha256_image'],module.BUILDS['v20']['image_sha256'])
        self.assertEqual(doc['v19_to_v20_ip_shift'],4)
        self.assertEqual(doc['original_mpu_poll_limit'],65535)
        self.assertEqual(len(doc['machine_spans']),2)
        self.assertEqual(len(doc['opcode_anchors']),32)
        self.assertEqual(len(doc['local_branches']),17)
        self.assertEqual(len(doc['near_calls']),6)
        self.assertEqual(sum(len(e['relocated_low_operand_ips']) for e in doc['machine_spans']),18)
        for e in doc['machine_spans']:
            first,last,sha=module.SPANS[e['id']]
            self.assertEqual((e['ip_start'],e['ip_end_exclusive'],e['length'],e['sha256']),
                             (f'{first:04X}',f'{last:04X}',last-first,sha))
            self.assertEqual(e['relocated_low_operand_ips'],
                             [f'{ip:04X}' for ip in module.SHIFTS[e['id']]])
        self.assertEqual({e['name'] for e in doc['opcode_anchors']},set(module.ANCHORS))
        self.assertEqual({e['name'] for e in doc['local_branches']},set(module.BRANCHES))
        self.assertEqual({e['name'] for e in doc['near_calls']},set(module.CALLS))

    def test_originals_and_negative_mutation_when_supplied(self):
        v19=os.getenv('WORX_N3D_V19_EXE')
        v20=os.getenv('WORX_N3D_V20_EXE')
        if not(v19 and v20):self.skipTest('private original EXEs not provided')
        expected=module.verify(Path(v19),Path(v20))
        saved=json.loads(EVIDENCE.read_text(encoding='utf-8'))
        self.assertEqual(expected,saved)
        raw=bytearray(Path(v20).read_bytes())
        raw[module.MZ_HEADER+module.BUILDS['v20']['cs_base']+0x5909]^=1
        with tempfile.TemporaryDirectory() as tmp:
            corrupted=Path(tmp)/'bad.exe';corrupted.write_bytes(raw)
            with self.assertRaises(ValueError):module.verify(Path(v19),corrupted)

if __name__=='__main__':unittest.main()
