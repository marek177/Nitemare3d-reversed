import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_n3d_image import VENDOR, audit_file, EXPECTED_HEADER, EXPECTED_IMAGE_SIZE
from audit_wrappers import build_report
from compare_riptide_dispatch import parse_table


class AuditTests(unittest.TestCase):
    def test_wrapper_inventory_consistency(self):
        r = build_report()
        self.assertEqual(r['N3D_wrapper_count'], 75)
        self.assertEqual(r['wrapper_size_bytes'], 4843)
        self.assertEqual(r['status'], 'INVENTORY_CONSISTENT')
        self.assertIn('51', [x['referenced_command_hex'][0]
                             for x in json.loads((ROOT / 'data/n3d_v20_wrappers.json').read_text())['wrappers']
                             if x['referenced_command_hex']])

    def test_cross_game_79_dispatch_entries(self):
        sample = 'word_20950 dw 0\n' + ''.join(
            f'        dw offset sub_{i:04X}\n' for i in range(1, 79)
        ) + 'word_209EE dw 0\n'
        table = parse_table(sample)
        self.assertEqual(len(table), 79)
        self.assertEqual(table[0]['ah'], '00')
        self.assertEqual(table[-1]['ah'], '4E')
        self.assertNotIn('51', [row['ah'] for row in table])

    def test_synthetic_mz_static_structure(self):
        # This is a SYNTHETIC FIXTURE, not a DOS game runtime trace.
        fake = bytearray(EXPECTED_HEADER + EXPECTED_IMAGE_SIZE)
        fake[:2] = b'MZ'
        struct.pack_into('<H', fake, 8, EXPECTED_HEADER // 16)
        buf = EXPECTED_HEADER
        fake[buf + 0x15BFE:buf + 0x17C00] = b'\x80' * (0x17C00 - 0x15BFE)
        fake[buf + 0x187FD:buf + 0x187FD + len(VENDOR)] = VENDOR
        fake[buf + 0x11A6A:buf + 0x11A6A+5] = bytes.fromhex('9A7D2EBF15')
        fake[buf + 0x10C6C:buf + 0x10C6C+5] = bytes.fromhex('9A662FBF15')
        digest = hashlib.sha256(fake[buf:]).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / 'synthetic_not_original.exe'
            file.write_bytes(fake)
            checks = audit_file(file, expected_sha256=digest)
            self.assertEqual(checks['status'], 'STATIC_IMAGE_IDENTIFIED')
            self.assertEqual(checks['statuses']['neutral_pcm_buffer_bytes'], True)
            fake[buf + 0x15BFE] = 0x00
            file.write_bytes(fake)
            checks_bad = audit_file(file)
            self.assertEqual(checks_bad['statuses']['neutral_pcm_buffer_bytes'], False)
            self.assertIn('load_image_sha256_match', checks_bad['failed_checks'])


if __name__ == '__main__':
    unittest.main()
