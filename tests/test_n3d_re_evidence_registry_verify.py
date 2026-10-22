"""Mutation/acceptance tests for the evidence metadata (not original N3D)."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from n3d_re_evidence_registry_verify import validate_registry  # noqa: E402

REGISTRY = json.loads(
    (ROOT / "docs/RE_EVIDENCE_REGISTRY_20261022.json").read_text(
        encoding="utf-8"
    )
)


class EvidenceAtlasTests(unittest.TestCase):
    def check_rejected(self, replacement):
        with self.assertRaises(ValueError):
            validate_registry(replacement, ROOT)

    def test_checked_in_registry(self):
        info = validate_registry(copy.deepcopy(REGISTRY), ROOT)
        self.assertGreaterEqual(info["observations"], 20)
        self.assertGreaterEqual(info["source_documents"], 100)
        self.assertFalse(info["original_vs_remake_parity_proven"])

    def test_bad_schema(self):
        v = copy.deepcopy(REGISTRY); v["schema"] = "v999"
        self.check_rejected(v)

    def test_bad_commit_sha(self):
        v = copy.deepcopy(REGISTRY); v["source_commit_sha"] = "abcdef"
        self.check_rejected(v)

    def test_bad_original_exe_sha(self):
        v = copy.deepcopy(REGISTRY)
        v["original_reference_exe"]["sha256"] = "not-sha"
        self.check_rejected(v)

    def test_global_parity_promotion(self):
        v = copy.deepcopy(REGISTRY)
        v["full_original_vs_remake_parity_proven"] = True
        self.check_rejected(v)

    def test_fabricated_original_rerun(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["verified_against_original_in_this_update"] = True
        self.check_rejected(v)

    def test_local_parity_promotion(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["original_vs_remake_parity_proven"] = True
        self.check_rejected(v)

    def test_duplicate_id(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][1]["id"] = v["observations"][0]["id"]
        self.check_rejected(v)

    def test_wrong_grade(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["grade"] = "100-percent-complete"
        self.check_rejected(v)

    def test_source_missing(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["sources"] = [
            "docs/NEVER_EXISTS_PRIVATE_ORIGINAL.EXE"
        ]
        self.check_rejected(v)

    def test_parent_traversal(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["sources"] = ["docs/../README.md"]
        self.check_rejected(v)

    def test_unlisted_existing_source(self):
        v = copy.deepcopy(REGISTRY)
        v["source_document_inventory"].remove(
            v["observations"][0]["sources"][0]
        )
        self.check_rejected(v)

    def test_duplicate_inventory_path(self):
        v = copy.deepcopy(REGISTRY)
        v["source_document_inventory"].append(
            v["source_document_inventory"][0]
        )
        self.check_rejected(v)

    def test_missing_document_on_disk(self):
        v = copy.deepcopy(REGISTRY)
        v["source_document_inventory"].append("docs/NONEXISTENT.md")
        v["source_document_inventory"].sort()
        self.check_rejected(v)

    def test_no_original_files_committed(self):
        v = copy.deepcopy(REGISTRY)
        v["original_files_committed"] = True
        self.check_rejected(v)

    def test_empty_claim(self):
        v = copy.deepcopy(REGISTRY)
        v["observations"][0]["statement"] = "maybe"
        self.check_rejected(v)


if __name__ == "__main__":
    unittest.main()
