"""Synthetic differential trace tests: no original game files are required."""

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "n3d_trace_compare.py"
spec = importlib.util.spec_from_file_location("n3d_trace_compare", SCRIPT)
import sys
sys.path.insert(0, str(SCRIPT.parent))
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def rng_rows(callers=(0x2478, 0x2478, 0x525E, 0x58A7), seed=1):
    rows = []
    state = seed
    for caller in callers:
        after = (state * 214013 + 2531011) & 0xFFFFFFFF
        rows.append({"caller": caller, "before": state, "after": after,
                     "result": (after >> 16) & 0x7FFF})
        state = after
    return rows


def fast_rows(invocation=7, tick=8):
    direct = compare.audit_fast.__globals__["FAST_DIRECT"]
    values = direct if tick % 8 == 0 else direct[:-1]
    return [{"invocation": invocation, "caller": 0xC150, "target": t}
            for t in values]


def save_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_envelope(path, csv_path, rows, build="dos-v2.0", trace_type="rng",
                   begin="demo_seed_1", end="first_input"):
    data = {
        "schema": compare.TRACE_SCHEMA,
        "build": build,
        "trace_type": trace_type,
        "row_count": len(rows),
        "csv_sha256": compare.file_hash(csv_path)["sha256"],
        "begin": begin,
        "end": end,
        "closed": True,
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


class DifferentialTraceTests(unittest.TestCase):
    def test_identical_seeded_rng_unsealed(self):
        reference = rng_rows()
        report = compare.compare_captures("rng", reference, reference)
        self.assertTrue(report["ok"])
        self.assertEqual(report["verdict"], "trace_match_unsealed")
        self.assertFalse(report["provenance"]["evidence_gate"])
        self.assertFalse(report["original_runtime_verified"])

    def test_caller_mismatch_even_when_same_rng_states(self):
        reference = rng_rows()
        candidate = rng_rows((0x2478, 0x525E, 0x525E, 0x58A7))
        report = compare.compare_captures("rng", reference, candidate)
        self.assertFalse(report["ok"])
        self.assertEqual(report["verdict"], "first_divergence")
        self.assertEqual(report["first_difference"]["index"], 1)
        self.assertEqual(report["reference_validation"]["final_state"],
                         report["candidate_validation"]["final_state"])

    def test_real_missing_rng_draw(self):
        reference = rng_rows()
        candidate = rng_rows((0x2478, 0x525E, 0x58A7))
        report = compare.compare_captures("rng", reference, candidate)
        self.assertFalse(report["ok"])
        self.assertEqual(report["first_difference"]["index"], 1)
        self.assertTrue(report["candidate_validation"]["ok"])
        self.assertEqual(report["first_difference"]["classification"],
                         "ordinary_divergence")

    def test_skipped_capture_record_detected_and_fails_continuity(self):
        reference = rng_rows()
        candidate = reference[:1] + reference[2:]
        report = compare.compare_captures("rng", reference, candidate)
        self.assertFalse(report["ok"])
        self.assertEqual(report["verdict"], "invalid_candidate_trace")
        self.assertEqual(report["first_difference"]["classification"],
                         "candidate_record_maybe_missing")
        self.assertEqual(report["candidate_validation"]["error"],
                         "RNG state discontinuity")

    def test_extra_capture_record_clue_is_not_proof(self):
        reference = rng_rows()
        extra = dict(reference[1])
        candidate = reference[:1] + [extra] + reference[1:]
        report = compare.compare_captures("rng", reference, candidate)
        self.assertFalse(report["ok"])
        self.assertEqual(report["first_difference"]["classification"],
                         "candidate_record_maybe_extra")
        self.assertEqual(report["verdict"], "invalid_candidate_trace")

    def test_fast_nested_order_is_compared_not_flattened(self):
        reference = fast_rows()
        reference.insert(2, {"invocation": 7, "caller": 0x5F26, "target": 0x1111})
        candidate = [dict(x) for x in reference]
        candidate[2]["target"] = 0x2222
        r = compare.compare_captures("fast", reference, candidate,
                                     invocation=7, tick_at_gate=8)
        self.assertFalse(r["ok"])
        self.assertTrue(r["reference_validation"]["ok"])
        self.assertTrue(r["candidate_validation"]["ok"])
        self.assertEqual(r["first_difference"]["index"], 2)

    def test_fast_gated_last_call(self):
        reference = fast_rows(tick=7)
        r = compare.compare_captures("fast", reference, reference,
                                     invocation=7, tick_at_gate=7)
        self.assertTrue(r["ok"])
        missing = compare.compare_captures("fast", reference, reference,
                                           invocation=7, tick_at_gate=8)
        self.assertFalse(missing["ok"])
        self.assertEqual(missing["verdict"], "invalid_reference_trace")

    def test_empty_rng_is_not_evidence(self):
        r = compare.compare_captures("rng", [], [])
        self.assertFalse(r["ok"])
        self.assertEqual(r["verdict"], "invalid_reference_trace")

    def test_reject_unsupported_version_in_envelope(self):
        rows = rng_rows()
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            csvfile = folder / "ref.csv"
            manifest = folder / "ref.json"
            save_csv(csvfile, rows)
            write_envelope(manifest, csvfile, rows, build="win16-v1.10")
            with self.assertRaisesRegex(ValueError, "dos-v2.0"):
                compare.validate_envelope(manifest, csvfile, "rng", len(rows), "reference")

    def test_manifests_digest_rowcount_and_closed_state(self):
        rows = rng_rows()
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            csvfile = folder / "trace.csv"
            manifest = folder / "trace.json"
            save_csv(csvfile, rows)
            obj = write_envelope(manifest, csvfile, rows)
            self.assertTrue(compare.validate_envelope(
                manifest, csvfile, "rng", len(rows), "reference")["integrity_attested"])
            obj["closed"] = False
            manifest.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not declared closed"):
                compare.validate_envelope(manifest, csvfile, "rng", len(rows), "reference")
            obj["closed"] = True
            obj["row_count"] -= 1
            manifest.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "row_count"):
                compare.validate_envelope(manifest, csvfile, "rng", len(rows), "reference")
            obj["row_count"] += 1
            manifest.write_text(json.dumps(obj), encoding="utf-8")
            csvfile.write_text(csvfile.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                compare.validate_envelope(manifest, csvfile, "rng", len(rows), "reference")

    def test_reference_fingerprint_rejects_wrong_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "not-canonical.bin"
            path.write_bytes(b"MZ" + bytes(300))
            self.assertFalse(compare.verify_reference_image(path)["match"])

    def test_evidence_gate_with_synthetic_override(self):
        rows = rng_rows()
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            ref_file, cand_file = folder / "ref.csv", folder / "cand.csv"
            ref_meta, cand_meta = folder / "ref.json", folder / "cand.json"
            image = folder / "image.bin"
            image.write_bytes(b"synthetic-not-the-original")
            for csvfile in (ref_file, cand_file):
                save_csv(csvfile, rows)
            write_envelope(ref_meta, ref_file, rows)
            write_envelope(cand_meta, cand_file, rows, build="reconstruction")
            args = dict(reference_csv=ref_file, candidate_csv=cand_file,
                        reference_envelope=ref_meta, candidate_envelope=cand_meta,
                        reference_image=image, require_provenance=True)
            mismatch = compare.compare_captures("rng", rows, rows, **args)
            self.assertFalse(mismatch["ok"])
            self.assertEqual(mismatch["verdict"], "provenance_rejected")
            with mock.patch.object(compare, "DOS20_UNPACKED_SHA256",
                                   compare.file_hash(image)["sha256"]):
                with mock.patch.object(compare, "DOS20_UNPACKED_BYTES", image.stat().st_size):
                    accepted = compare.compare_captures("rng", rows, rows, **args)
            self.assertTrue(accepted["ok"])
            self.assertTrue(accepted["provenance"]["evidence_gate"])
            # Even a self-consistent fake source cannot prove runtime execution.
            self.assertFalse(accepted["original_runtime_verified"])

    def test_boundary_mismatch_is_error(self):
        rows = rng_rows()
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            rf, cf = folder / "r.csv", folder / "c.csv"
            rm, cm = folder / "r.json", folder / "c.json"
            save_csv(rf, rows)
            save_csv(cf, rows)
            write_envelope(rm, rf, rows)
            write_envelope(cm, cf, rows, build="reconstruction", end="different_end")
            report = compare.compare_captures(
                "rng", rows, rows, reference_csv=rf, candidate_csv=cf,
                reference_envelope=rm, candidate_envelope=cm)
            self.assertFalse(report["ok"])
            self.assertEqual(report["verdict"], "provenance_rejected")
            self.assertIn("capture boundaries differ", report["provenance_errors"])


if __name__ == "__main__":
    unittest.main()
