"""Synthetic DEMO framing tests; intentionally no engine-semantic claims."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_demo_layout_probe as probe  # noqa: E402


def demo(header: tuple[int, int, int], records: list[tuple[bytes, int]]) -> bytes:
    return struct.pack("<3H", *header) + b"".join(
        inputs + struct.pack("<I", tick) for inputs, tick in records
    )


class DemoProbeTests(unittest.TestCase):
    def test_both_interpretations_preserve_exact_bytes(self) -> None:
        raw = demo((10, 5, 20), [
            (bytes([0x20, 0x02, 0x00, 0x00]), 12),
            (bytes([0x00, 0x80, 0x00, 0x00]), 17),
        ])
        header, rows = probe.parse_demo(raw)
        self.assertEqual(header, (10, 5, 20))
        self.assertEqual(rows[0].win16_event, 0x20)
        self.assertEqual(rows[0].win16_mask, 0x0002)
        self.assertEqual(rows[0].two_word_a, 0x0220)
        self.assertEqual(rows[0].two_word_b, 0)
        self.assertTrue(probe.report(header, rows)["ticks_monotonic"])
        self.assertEqual(probe.report(header, rows)["win16_nonzero_pad_count"], 0)

    def test_dos_header_and_nonzero_pad_remain_observations(self) -> None:
        raw = demo((15, 7, 30), [
            (bytes([0x01, 0x02, 0x03, 0x04]), 19),
            (bytes([0x05, 0x06, 0x07, 0x00]), 10),
        ])
        header, rows = probe.parse_demo(raw)
        summary = probe.report(header, rows, 1)
        self.assertEqual(summary["header_words"], [15, 7, 30])
        self.assertEqual(summary["record_count"], 2)
        self.assertFalse(summary["ticks_monotonic"])
        self.assertEqual(summary["win16_nonzero_pad_count"], 1)
        self.assertEqual(len(summary["first_records"]), 1)

    def test_invalid_length_rejected(self) -> None:
        with self.assertRaisesRegex(probe.DemoError, "Invalid size"):
            probe.parse_demo(b"\x00" * 13)

    def test_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "DEMO.1"
            path.write_bytes(demo((15, 7, 30), [(bytes(4), 8)]))
            output = StringIO()
            with redirect_stdout(output):
                status = probe.main([str(path), "--head", "1", "--json"])
            self.assertEqual(status, 0)
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["first_tick"], 8)
            self.assertEqual(summary["two_word_a_unique"], 1)


if __name__ == "__main__":
    unittest.main()
