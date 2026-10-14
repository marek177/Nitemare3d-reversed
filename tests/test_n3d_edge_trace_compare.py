"""No original game data: verify the edge comparator, not 1:1 gameplay."""

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_edge_trace_compare.py"
spec = importlib.util.spec_from_file_location("n3d_edge_trace_compare", SCRIPT)
edge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = edge
spec.loader.exec_module(edge)


FIXTURES = {
    "push": [
        [0, 24, 672, 672, 8, 0, 24, 0],
        [1, 24, 680, 672, 7, 0, 24, 0],
        [2, 24, 680, 672, 7, 1, 24, 25],
        [3, 24, 688, 672, 6, 0, 24, 0],
    ],
    "door": [[0, 4, 3, 1, 0, 3], [1, 4, 3, 4, 1, 3], [2, 4, 3, 3, 0, 3]],
    "projectile": [
        [0, 1, 0, 10, 10, -1, "0101010101010101", "0101010101010101"],
        [1, 1, 0, 10, 9, 3, "0101010001010101", "0101010101010101"],
    ],
    "panel": [[0, 1, 100, 50, 110, 50, 1], [1, 1, 102, 50, 110, 50, 1],
              [2, 1, 104, 50, 110, 50, 0]],
}


def write_csv(path, scenario, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(edge.FIELDS[scenario])
        writer.writerows(rows)


def write_envelope(path, csv_path, scenario, rows, *,
                   build="dos-v2.0", end="post_event"):
    data = {"schema": edge.SCHEMA, "scenario": scenario,
            "build": build, "row_count": len(rows),
            "csv_sha256": edge.sha256(csv_path), "begin": "pre_event",
            "end": end, "closed": True}
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


class EdgeTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def paths(self, scenario, reference, candidate):
        r, c = self.root / "reference.csv", self.root / "candidate.csv"
        write_csv(r, scenario, reference)
        write_csv(c, scenario, candidate)
        return r, c

    def test_all_four_scenarios_match_unsealed_only(self):
        for scenario, rows in FIXTURES.items():
            with self.subTest(scenario=scenario):
                r, c = self.paths(scenario, rows, rows)
                report = edge.compare_traces(scenario, r, c)
                self.assertTrue(report["ok"])
                self.assertEqual(report["verdict"], "trace_match_unsealed")
                self.assertFalse(report["original_runtime_verified"])
                self.assertFalse(edge.compare_traces(scenario, r, c,
                    require_boundaries=True)["ok"])

    def test_first_divergence_per_scenario(self):
        for scenario, rows in FIXTURES.items():
            with self.subTest(scenario=scenario):
                candidate = [r.copy() for r in rows]
                field = "remaining" if scenario == "push" else (
                    "timer" if scenario == "door" else (
                    "ammo_after" if scenario == "projectile" else "x0"))
                index = edge.FIELDS[scenario].index(field)
                candidate[1][index] += 1
                r, c = self.paths(scenario, rows, candidate)
                report = edge.compare_traces(scenario, r, c)
                self.assertFalse(report["ok"])
                self.assertEqual(report["first_difference"]["index"], 1)
                self.assertEqual(report["first_difference"]["field"], field)

    def test_equal_prefix_and_extra_row_do_not_match(self):
        rows = FIXTURES["door"]
        r, c = self.paths("door", rows, rows[:-1])
        report = edge.compare_traces("door", r, c)
        self.assertEqual(report["first_difference"]["kind"], "different_length")
        self.assertFalse(report["ok"])
        r, c = self.paths("door", rows[:-1], rows)
        self.assertEqual(edge.compare_traces("door", r, c)["first_difference"]["index"], 2)

    def test_reject_nonconsecutive_steps(self):
        rows = [r.copy() for r in FIXTURES["push"]]
        rows[2][0] = 4
        r, _ = self.paths("push", rows, FIXTURES["push"])
        with self.assertRaisesRegex(ValueError, "contiguous"):
            edge.read_trace(r, "push")

    def test_reject_bad_projectile_slot_byte_string(self):
        rows = [r.copy() for r in FIXTURES["projectile"]]
        rows[0][6] = "11111111"  # eight hex digits, not eight bytes
        r, _ = self.paths("projectile", rows, FIXTURES["projectile"])
        with self.assertRaisesRegex(ValueError, "eight hex bytes"):
            edge.read_trace(r, "projectile")

    def test_accept_unknown_slot_state_bytes_without_guessing(self):
        rows = [r.copy() for r in FIXTURES["projectile"]]
        rows[0][6] = "FF01020304050607"
        r, _ = self.paths("projectile", rows, rows)
        self.assertEqual(edge.read_trace(r, "projectile")[0]["slot_states_before"],
                         "ff01020304050607")

    def test_reject_invalid_boolean_and_allocated_slot(self):
        rows = [r.copy() for r in FIXTURES["projectile"]]
        rows[0][1] = 2
        r, _ = self.paths("projectile", rows, FIXTURES["projectile"])
        with self.assertRaisesRegex(ValueError, "0 or 1"):
            edge.read_trace(r, "projectile")
        rows[0][1] = 1
        rows[0][5] = 8
        r, _ = self.paths("projectile", rows, FIXTURES["projectile"])
        with self.assertRaisesRegex(ValueError, "outside"):
            edge.read_trace(r, "projectile")

    def test_header_mismatch_rejected(self):
        r, _ = self.paths("panel", FIXTURES["panel"], FIXTURES["panel"])
        r.write_text("step,wrong\n0,1\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "CSV header"):
            edge.read_trace(r, "panel")

    def test_boundary_manifests_are_declarations_not_runtime_proof(self):
        rows = FIXTURES["push"]
        r, c = self.paths("push", rows, rows)
        rm, cm = self.root / "reference.json", self.root / "candidate.json"
        write_envelope(rm, r, "push", rows)
        write_envelope(cm, c, "push", rows, build="modern-reconstruction")
        args = {"reference_envelope": rm, "candidate_envelope": cm,
                "require_boundaries": True}
        report = edge.compare_traces("push", r, c, **args)
        self.assertTrue(report["ok"])
        self.assertTrue(report["boundary_declarations_valid"])
        self.assertFalse(report["original_runtime_verified"])
        manifest = json.loads(rm.read_text(encoding="utf-8"))
        manifest["closed"] = False
        rm.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not declared closed"):
            edge.compare_traces("push", r, c, **args)

    def test_boundary_cross_capture_and_missing_envelope(self):
        rows = FIXTURES["panel"]
        r, c = self.paths("panel", rows, rows)
        rm, cm = self.root / "ref.json", self.root / "cand.json"
        write_envelope(rm, r, "panel", rows)
        write_envelope(cm, c, "panel", rows, end="different_end")
        result = edge.compare_traces("panel", r, c,
            reference_envelope=rm, candidate_envelope=cm)
        self.assertFalse(result["ok"])
        self.assertEqual(result["verdict"], "invalid_boundaries")
        result = edge.compare_traces("panel", r, c, reference_envelope=rm)
        self.assertFalse(result["ok"])

    def test_envelope_digest_and_count(self):
        rows = FIXTURES["door"]
        r, c = self.paths("door", rows, rows)
        manifest = self.root / "ref.json"
        data = write_envelope(manifest, r, "door", rows)
        data["row_count"] -= 1
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "row_count"):
            edge.validate_envelope(manifest, r, "door", len(rows))
        data["row_count"] = len(rows)
        manifest.write_text(json.dumps(data), encoding="utf-8")
        r.write_bytes(r.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            edge.validate_envelope(manifest, r, "door", len(rows))


if __name__ == "__main__":
    unittest.main()
