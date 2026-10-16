"""Reproducible original-image evidence contracts without shipping copyrighted EXE.

Optionally set WORX_N3D_V20_EXE to the exact unpacked original. No claim
that a cached JSON row proves an instruction branch in a different binary.
"""
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_dispatch_binary import audit, LEAF_SPANS, COMPOSED_SPANS, ENTRY_COUNT, EXPECTED_IMAGE_SHA256

class DispatchOriginalStaticEvidence(unittest.TestCase):
    def test_manifest_has_consistent_leaf_coverage(self):
        p=ROOT/'data/n3d_v20_int63_dispatch.json'
        report=json.loads(p.read_text(encoding='utf-8'))
        self.assertEqual(report['original_image_sha256'], EXPECTED_IMAGE_SHA256)
        self.assertEqual(report['selectors_audited'], ENTRY_COUNT)
        self.assertEqual(report['nonzero_targets'], 79)
        self.assertEqual(report['null_initial_targets'], ['00','27','28'])
        self.assertEqual(report['table_sha256_00_to_51'],
                         '38aeeb4ae7790a72808a6855f3ce9691f777f15975260abc0901efd5e70ebf5d')
        self.assertEqual(report['leaf_bodies_verified'], len(LEAF_SPANS))
        self.assertEqual(len(LEAF_SPANS),37)
        self.assertEqual(report['composed_bodies_verified'],4)
        self.assertEqual(len(COMPOSED_SPANS),4)
        self.assertEqual(report['machine_audited_handler_contracts'],41)
        self.assertEqual(report['nonzero_handlers_not_reconstructed'],38)
        self.assertIn('2E',report['transitive_helpers'])
        self.assertEqual(len(report['transitive_helpers']['2E']['sha256']),64)
        rows=report['dispatch']
        self.assertEqual(len(rows),82)
        for i,row in enumerate(rows):
            ah=f'{i:02X}'
            self.assertEqual(row['ah'],ah)
            self.assertEqual(int(row['table_word_image_offset'],16),0x17C10+i*2)
            if i in LEAF_SPANS:
                self.assertEqual(row['status'],'LEAF_BYTE_AUDITED')
                self.assertEqual(row['target_cs_offset'],f'0x{LEAF_SPANS[i][0]:04X}')
                self.assertEqual(len(row['leaf_body_sha256']),64)
            elif i in COMPOSED_SPANS:
                self.assertEqual(row['status'],'BODY_AND_DEPS_AUDITED')
                self.assertEqual(row['target_cs_offset'],f'0x{COMPOSED_SPANS[i][0]:04X}')
                self.assertEqual(len(row['leaf_body_sha256']),64)
            else:
                self.assertIsNone(row['leaf_body_sha256'])

    @unittest.skipUnless(os.environ.get('WORX_N3D_V20_EXE'),
                         'Optional pinned proprietary binary not supplied; manifest test still runs')
    def test_recompute_against_original_machine_bytes(self):
        original=Path(os.environ['WORX_N3D_V20_EXE'])
        actual=audit(original)
        saved=json.loads((ROOT/'data/n3d_v20_int63_dispatch.json').read_text())
        saved.pop('source_filename',None)
        actual.pop('source_filename',None)
        self.assertEqual(actual,saved)

if __name__=='__main__':
    unittest.main()
