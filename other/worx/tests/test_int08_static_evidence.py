"""Validate machine-code anchor witness for INT08 when pinned EXE is present."""
from __future__ import annotations
import json
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_int08_re_first import ANCHORS, audit

class Int08MachineEvidence(unittest.TestCase):
    def test_checked_static_manifest(self):
        manifest=json.loads((ROOT/'data/worx21_int08_static_evidence.json').read_text())
        self.assertEqual(manifest['initial_reentrancy_counter_3ED4'],0xFFFF)
        self.assertEqual(manifest['int08_private_stack_audio_body_sha256'],
                         '1caf9d948575f57763ddd611d7190dfb6b675965776cc66fb86ba23d2328b4cb')
        self.assertEqual(len(manifest['int08_audio_callbacks_in_order']),2)
        self.assertEqual(manifest['pit_init_divisor'],0x0952)
        self.assertEqual(manifest['pit_divided_counter'],27)
        self.assertEqual(len(manifest['machine_anchors']),len(ANCHORS))
        self.assertEqual(manifest['int08_gate_body_sha256'],
                         '575221bdfdc0622f8a816ea823014931aebb2fc79bdae319ba2d4bad6c136bf2')
        self.assertEqual(manifest['machine_anchors']['timer_music_call']['original_machine_bytes'],'e8 10 03')
        self.assertEqual(manifest['machine_anchors']['timer_iret']['original_machine_bytes'],'cf')

    @unittest.skipUnless(os.getenv('WORX_N3D_V20_EXE'),'Optional pinned original MZ EXE not present')
    def test_pinned_machine_image(self):
        expected=json.loads((ROOT/'data/worx21_int08_static_evidence.json').read_text())
        actual=audit(Path(os.environ['WORX_N3D_V20_EXE']))
        self.assertEqual(actual,expected)
