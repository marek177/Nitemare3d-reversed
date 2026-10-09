#!/usr/bin/env python3
"""Compare two documented Nitemare-3D DEMO record interpretations.

The eight-byte record framing is shared, but the DOS v2.0 documentation
and Win16 v1.10 executable-backed analysis assign different meanings to
the four input bytes. Both views are printed without promoting the DOS
semantics or changing existing replay behavior. Input files are read only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import struct
import sys

HEADER_SIZE = 6
RECORD_SIZE = 8


class DemoError(ValueError):
    pass


@dataclass(frozen=True)
class Record:
    index: int
    offset: int
    tick: int
    win16_event: int
    win16_mask: int
    win16_padding: int
    two_word_a: int
    two_word_b: int

    def as_dict(self) -> dict:
        return {
            "index": self.index,
            "offset": self.offset,
            "tick": self.tick,
            "win16_u8_u16_u8": {
                "event": self.win16_event,
                "mask": f"0x{self.win16_mask:04X}",
                "pad": self.win16_padding,
            },
            "two_u16_words": {
                "word_a": f"0x{self.two_word_a:04X}",
                "word_b": f"0x{self.two_word_b:04X}",
            },
        }


def parse_demo(raw: bytes) -> tuple[tuple[int, int, int], list[Record]]:
    if len(raw) < HEADER_SIZE or (len(raw) - HEADER_SIZE) % RECORD_SIZE:
        raise DemoError(
            f"Invalid size {len(raw)}: expected 6 + N*8 bytes"
        )
    header = struct.unpack_from("<3H", raw)
    rows = []
    for index, offset in enumerate(range(HEADER_SIZE, len(raw), RECORD_SIZE)):
        event = raw[offset]
        mask = struct.unpack_from("<H", raw, offset + 1)[0]
        padding = raw[offset + 3]
        a, b = struct.unpack_from("<2H", raw, offset)
        tick = struct.unpack_from("<I", raw, offset + 4)[0]
        rows.append(Record(index, offset, tick, event, mask, padding, a, b))
    return header, rows


def report(header: tuple[int, int, int], rows: list[Record], head: int = 8) -> dict:
    times = [row.tick for row in rows]
    pad_counts = Counter(row.win16_padding for row in rows)
    return {
        "header_words": list(header),
        "record_count": len(rows),
        "first_tick": times[0] if times else None,
        "last_tick": times[-1] if times else None,
        "ticks_monotonic": all(a <= b for a, b in zip(times, times[1:])),
        "win16_nonzero_pad_count": sum(count for value, count in pad_counts.items() if value),
        "win16_event_unique": len({row.win16_event for row in rows}),
        "win16_mask_unique": len({row.win16_mask for row in rows}),
        "two_word_a_unique": len({row.two_word_a for row in rows}),
        "two_word_b_unique": len({row.two_word_b for row in rows}),
        "first_records": [row.as_dict() for row in rows[:head]],
        "evidence_warning": (
            "Two byte-level interpretations only. Original DOS v2.0 "
            "control-bit semantics remain unverified until disassembly/runtime tracing."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("demo", type=Path, help="DEMO.n from your own game copy")
    ap.add_argument("--head", type=int, default=8, help="Number of records to show (default 8)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.head < 0 or args.head > 1000:
        ap.error("--head must be between 0 and 1000")
    try:
        header, rows = parse_demo(args.demo.read_bytes())
    except (OSError, DemoError) as error:
        print(f"DEMO probe error: {error}", file=sys.stderr)
        return 2
    output = report(header, rows, args.head)
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for key, value in output.items():
            if key != "first_records":
                print(f"{key}: {value}")
        for item in output["first_records"]:
            print(f"record {item['index']}: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
