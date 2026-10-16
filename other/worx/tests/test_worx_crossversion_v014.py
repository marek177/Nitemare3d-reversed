"""Pinned cross-version selected WORX code spans; original binaries are optional."""
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'tools'/'compare_worx_versions_v014.py'
MANIFEST=ROOT/'data'/'worx21_crossversion_v19_v20_v014.json'
spec=importlib.util.spec_from_file_location('compare_worx_versions_v014',P)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CrossVersion(unittest.TestCase):
    def test_pinned_operand_shift_summary(self):
        data=json.loads(MANIFEST.read_text())
        self.assertEqual(data['functions_compared'],6)
        self.assertEqual(data['changed_operand_bytes'],41)
        self.assertEqual(data['image_delta'],-60)
        self.assertEqual(data['old_effective_ip_delta'],4)
        self.assertEqual(len(data['far_call_proofs']),2)
        self.assertEqual(data['far_call_proofs'][0]['v19_call_bytes'], '9a 81 2e bb 15')
        self.assertEqual(data['far_call_proofs'][0]['v20_call_bytes'], '9a 7d 2e bf 15')
        self.assertEqual(data['version19_image_sha256'],module.IMAGES['v19']['sha'])
        self.assertEqual(data['version20_image_sha256'],module.IMAGES['v20']['sha'])
        for item in data['functions']:
            lo,hi,_=module.SPAN_AND_V19_SHA[item['name']]
            expected=module.EXPECTED_V19_SHIFTED_OFFSETS[item['name']]
            self.assertEqual(item['byte_count'],hi-lo)
            self.assertEqual(item['changed_ips'],[f'{x:04X}' for x in expected])
            self.assertEqual(item['same_bytes'],hi-lo-len(expected))

    def test_originals_when_present(self):
        p19=os.environ.get('WORX_N3D_V19_EXE')
        p20=os.environ.get('WORX_N3D_V20_EXE')
        if not(p19 and p20):
            self.skipTest('original v1.9 and v2.0 proprietary EXEs not bundled')
        result=module.compare(Path(p19),Path(p20))
        self.assertEqual(result['changed_operand_bytes'],41)
        self.assertEqual(result['functions_compared'],6)

if __name__=='__main__':unittest.main()
