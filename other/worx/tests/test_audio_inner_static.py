"""Pinned machine-code evidence for WORX v0.13 (original EXE optional)."""
from __future__ import annotations
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_audio_inner_v013 import audit, BODY_SPANS, ANCHORS

class AudioInnerMachineEvidence(unittest.TestCase):
    def test_pinned_static_manifest(self):
        saved=json.loads((ROOT/'data/worx21_audio_inner_static_v013.json').read_text())
        self.assertEqual(saved['api_handler_count_unchanged'],41)
        self.assertEqual(len(saved['machine_slices']),len(BODY_SPANS))
        self.assertEqual(len(saved['machine_anchors']),len(ANCHORS))
        self.assertEqual(saved['machine_slices']['dma_49bc']['bytes'],0x4A12-0x49BC)
        self.assertEqual(saved['machine_anchors']['dma_signed_1000_threshold_49e4']['machine_bytes'],
                         '81 f9 00 10 7e 03')
        self.assertEqual(saved['machine_anchors']['midi_loop_fallthrough_44b1']['machine_bytes'],'e2 f6 51')
        self.assertIn('44B3',saved['transitive_open']['4476_to_44B3'])

    @unittest.skipUnless(os.getenv('WORX_N3D_V20_EXE'),'Original proprietary EXE optional, not redistributed')
    def test_against_original_machine_image(self):
        expected=json.loads((ROOT/'data/worx21_audio_inner_static_v013.json').read_text())
        self.assertEqual(audit(Path(os.environ['WORX_N3D_V20_EXE'])),expected)

if __name__=='__main__':unittest.main()
