"""Synthetic metadata regression checks for the v0.79 addendum."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from n3d_v079_addendum_audit import audit  # noqa: E402

class AddendumAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "research/v079_20261120_evidence.json").read_text())

    def test_checked_inventory(self):
        self.assertEqual(audit(self.doc, ROOT)["status"], "METADATA_ONLY_PASS")

    def test_anti_parity_guard(self):
        bad = copy.deepcopy(self.doc)
        bad["global_original_vs_remake_parity"] = True
        with self.assertRaises(ValueError):
            audit(bad, ROOT)

    def test_noncode_sum(self):
        bad = copy.deepcopy(self.doc)
        next(r for r in bad["items"] if r["id"] == "NONCODE_20261119")["metrics"]["unknown_bytes"] += 1
        with self.assertRaises(ValueError):
            audit(bad, ROOT)

    def test_duplicate_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["items"].append(copy.deepcopy(bad["items"][0]))
        with self.assertRaises(ValueError):
            audit(bad, ROOT)

if __name__ == "__main__":
    unittest.main()
