#!/usr/bin/env python3
"""Synthetic positive and mutation-negative checks of the D02-D CSV verifier.

These tests do not replay the original Nitemare 3D executable or raw .n3dt trace.
"""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import verify_d02d_rng229 as v  # noqa: E402


def make_rows():
    rows = []
    state = 1
    contexts = v.expected_context()
    for i, site_token in enumerate(v.EXPECTED_CALLSITE_ORDER):
        ordinal = i + 1
        before = state
        state = (state * 214013 + 2531011) & 0xFFFFFFFF
        sched, demo, key, mask = contexts[i]
        rows.append({
            "ordinal": ordinal,
            "callsite": v.SITE_CODES[int(site_token, 16)],
            "state_before": f"0x{before:08X}",
            "state_after_lcg": f"0x{state:08X}",
            "return_lcg": (state >> 16) & 0x7FFF,
            "original_store_observed": True,
            "original_return_observed": True,
            "original_instruction_complete": True,
            "scheduler_depth": 1,
            "scheduler_entries_before": sched,
            "last_demo_record_ordinal": demo,
            "last_demo_key": f"0x{key:04X}",
            "last_demo_mask": f"0x{mask:04X}",
            "call_event": ordinal * 53,
        })
    assert len(rows) == 229
    return rows


def run_fixture(rows):
    with tempfile.TemporaryDirectory(prefix="n3d-d02d-") as folder:
        path = Path(folder) / "private_export.csv"
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return v.verify(path)


class TestD02dVerifier(unittest.TestCase):
    def test_positive_synthetic_reference(self):
        result = run_fixture(make_rows())
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["derived_rows_checked"], 229)
        self.assertEqual(result["final_rng_state"], "0xD0643564")
        self.assertTrue(result["full_callsite_order_matched"])
        self.assertFalse(result["original_raw_trace_replayed"])
        self.assertFalse(result["original_vs_port_parity"])

    def test_reject_reordered_calls_even_when_counts_unchanged(self):
        rows = make_rows()
        # This mutation previously escaped count-based checks and the death-only window.
        rows[0]["callsite"], rows[39]["callsite"] = (
            rows[39]["callsite"], rows[0]["callsite"]
        )
        with self.assertRaisesRegex(ValueError, "caller ordering"):
            run_fixture(rows)

    def test_reject_scheduler_context_change(self):
        rows = make_rows()
        rows[0]["scheduler_entries_before"] = 58  # 57→58, still monotonic
        with self.assertRaisesRegex(ValueError, "scheduler/DEMO context"):
            run_fixture(rows)

    def test_reject_demo_mask_change(self):
        rows = make_rows()
        rows[0]["last_demo_mask"] = "0x0001"
        with self.assertRaisesRegex(ValueError, "scheduler/DEMO context"):
            run_fixture(rows)

    def test_reject_rng_ax_change(self):
        rows = make_rows()
        rows[50]["return_lcg"] += 1
        with self.assertRaisesRegex(ValueError, "wrong AX"):
            run_fixture(rows)

    def test_reject_rng_state_change(self):
        rows = make_rows()
        rows[50]["state_after_lcg"] = "0x00000000"
        with self.assertRaisesRegex(ValueError, "wrong LCG state"):
            run_fixture(rows)

    def test_reject_incomplete_original_record(self):
        rows = make_rows()
        rows[50]["original_instruction_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete record"):
            run_fixture(rows)

    def test_reject_event_swap(self):
        rows = make_rows()
        rows[55]["call_event"], rows[56]["call_event"] = (
            rows[56]["call_event"], rows[55]["call_event"]
        )
        with self.assertRaisesRegex(ValueError, "event ordering"):
            run_fixture(rows)

    def test_reject_missing_row(self):
        rows = make_rows()
        rows.pop(50)
        with self.assertRaisesRegex(ValueError, "expected 229 draws"):
            run_fixture(rows)


if __name__ == "__main__":
    unittest.main()
