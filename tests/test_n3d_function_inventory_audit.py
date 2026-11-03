import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'tools'/'n3d_function_inventory_audit.py'
spec = importlib.util.spec_from_file_location('audit', SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

class InventoryTests(unittest.TestCase):
    def audit_text(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sample.csv'
            p.write_text(text, encoding='utf-8')
            return audit_module.audit(p)

    def test_statuses_are_not_merged(self):
        r = self.audit_text('version,entry,status,evidence\nDOS2,1234:0000,confirmed,trace1\nDOS2,1234:0010,candidate,\nWIN110,2:3994,unresolved,\n')
        self.assertEqual(r['versions']['DOS2']['confirmed'], 1)
        self.assertEqual(r['versions']['DOS2']['candidate'], 1)
        self.assertEqual(r['versions']['WIN110']['unresolved'], 1)
        self.assertFalse(r['errors'])

    def test_duplicates_and_empty_evidence(self):
        r = self.audit_text('version,entry,status,evidence\nDOS2,abcd:0000,confirmed,\nDOS2,abcd:0000,candidate,\nDOS2,ABCD:0000,candidate,\n')
        self.assertEqual(len(r['errors']), 2)

    def test_missing_columns(self):
        with self.assertRaises(ValueError):
            self.audit_text('version,entry\nDOS2,1234:0000\n')

if __name__ == '__main__':
    unittest.main()
