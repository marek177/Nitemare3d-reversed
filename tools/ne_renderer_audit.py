#!/usr/bin/env python3
"""Evidence-oriented NE disassembly helper for the NITE3W renderer audit.

The tool keeps logical NE ``segment:offset`` addresses visible, converts them
to file offsets, and annotates Win16 relocation records.  It is intentionally
small: it is an audit aid, not a general NE loader or decompiler.
"""
from __future__ import annotations

import argparse
import dataclasses
import struct
from pathlib import Path
from typing import Iterable

try:
    from capstone import CS_ARCH_X86, CS_MODE_16, Cs
except ImportError as exc:  # pragma: no cover - dependency error is user-facing
    raise SystemExit("capstone is required: python -m pip install capstone") from exc


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def pstring(data: bytes, offset: int) -> str:
    size = data[offset]
    return data[offset + 1 : offset + 1 + size].decode("latin1", errors="replace")


@dataclasses.dataclass(frozen=True)
class Segment:
    number: int
    file_offset: int
    length: int
    flags: int
    minimum_allocation: int


@dataclasses.dataclass(frozen=True)
class Relocation:
    segment: int
    source_offset: int
    source_type: int
    flags: int
    target: str


class NeImage:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        if self.data[:2] != b"MZ":
            raise ValueError("not an MZ executable")
        self.ne_offset = u32(self.data, 0x3C)
        if self.data[self.ne_offset : self.ne_offset + 2] != b"NE":
            raise ValueError("MZ executable has no NE header")

        ne = self.ne_offset
        self.alignment_shift = u16(self.data, ne + 0x32)
        segment_count = u16(self.data, ne + 0x1C)
        module_count = u16(self.data, ne + 0x1E)
        segment_table = ne + u16(self.data, ne + 0x22)
        module_table = ne + u16(self.data, ne + 0x28)
        imported_names = ne + u16(self.data, ne + 0x2A)

        self.modules = [
            pstring(self.data, imported_names + u16(self.data, module_table + i * 2))
            for i in range(module_count)
        ]
        self.segments: list[Segment] = []
        for index in range(segment_count):
            sector, length, flags, minimum = struct.unpack_from(
                "<HHHH", self.data, segment_table + index * 8
            )
            self.segments.append(
                Segment(
                    index + 1,
                    sector << self.alignment_shift if sector else 0,
                    length or 0x10000,
                    flags,
                    minimum,
                )
            )
        self.relocation_records = list(self._read_relocations())
        self.relocations = list(self._expand_relocation_chains())

    def segment(self, number: int) -> Segment:
        if number < 1 or number > len(self.segments):
            raise ValueError(f"segment {number} is outside the NE segment table")
        return self.segments[number - 1]

    def file_offset(self, segment: int, offset: int) -> int:
        entry = self.segment(segment)
        if not entry.file_offset or offset < 0 or offset >= entry.length:
            raise ValueError(f"{segment}:{offset:04X} has no file-backed byte")
        return entry.file_offset + offset

    def bytes_at(self, segment: int, start: int, end: int) -> bytes:
        entry = self.segment(segment)
        if start < 0 or end < start or end > entry.length:
            raise ValueError("requested disassembly range is outside the segment")
        return self.data[entry.file_offset + start : entry.file_offset + end]

    def _read_relocations(self) -> Iterable[Relocation]:
        for segment in self.segments:
            if not segment.file_offset or not (segment.flags & 0x0100):
                continue
            cursor = segment.file_offset + segment.length
            count = u16(self.data, cursor)
            cursor += 2
            for _ in range(count):
                source_type, flags, source_offset, word1, word2 = struct.unpack_from(
                    "<BBHHH", self.data, cursor
                )
                cursor += 8
                target_type = flags & 0x03
                if target_type == 0:
                    target = f"internal {word1 & 0xFF}:{word2:04X}"
                elif target_type == 1:
                    module = self.modules[word1 - 1] if 0 < word1 <= len(self.modules) else f"module#{word1}"
                    target = f"import {module} ordinal {word2}"
                elif target_type == 2:
                    module = self.modules[word1 - 1] if 0 < word1 <= len(self.modules) else f"module#{word1}"
                    target = f"import {module} name@{word2:04X}"
                else:
                    target = f"OS fixup {word1:04X}:{word2:04X}"
                yield Relocation(segment.number, source_offset, source_type, flags, target)

    def _expand_relocation_chains(self) -> Iterable[Relocation]:
        """Expand NE non-additive fixup chains into individual source sites.

        Win16 linkers store the next source offset in the word being fixed up.
        A single internal-segment relocation can therefore represent hundreds
        of far-call segment-word sites.  The terminal link is ``0xFFFF``.
        """
        for record in self.relocation_records:
            current = record.source_offset
            seen: set[int] = set()
            segment = self.segment(record.segment)
            while current != 0xFFFF:
                if current in seen or current + 2 > segment.length:
                    raise ValueError(
                        f"invalid relocation chain in segment {record.segment} at {current:04X}"
                    )
                seen.add(current)
                target = record.target
                if record.source_type == 2 and target.startswith("internal ") and current >= 2:
                    # A segment-only fixup leaves the offset half of a far
                    # address intact immediately before the patched selector.
                    target_segment = target.split()[1].split(":", 1)[0]
                    target_offset = u16(self.data, segment.file_offset + current - 2)
                    target = f"internal {target_segment}:{target_offset:04X}"
                yield dataclasses.replace(record, source_offset=current, target=target)
                if record.flags & 0x04:  # additive fixup: no source chain
                    break
                current = u16(self.data, segment.file_offset + current)

    def relocation_map(self, segment: int) -> dict[int, Relocation]:
        return {r.source_offset: r for r in self.relocations if r.segment == segment}


def parse_number(text: str) -> int:
    return int(text, 0)


def disassemble(image: NeImage, segment: int, start: int, end: int) -> None:
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    relocations = image.relocation_map(segment)
    for insn in decoder.disasm(image.bytes_at(segment, start, end), start):
        annotations: list[str] = []
        for offset in range(insn.address, insn.address + insn.size):
            relocation = relocations.get(offset)
            if relocation:
                annotations.append(f"reloc@+{offset - insn.address}: {relocation.target}")
        file_offset = image.file_offset(segment, insn.address)
        suffix = f" ; {'; '.join(annotations)}" if annotations else ""
        print(
            f"{segment}:{insn.address:04X} file+0x{file_offset:05X}  "
            f"{insn.bytes.hex(' '):<23} {insn.mnemonic:<8} {insn.op_str}{suffix}"
        )


def print_xrefs(image: NeImage, target: str) -> None:
    normalized = target.lower()
    hits = [r for r in image.relocations if normalized in r.target.lower()]
    for relocation in hits:
        file_offset = image.file_offset(relocation.segment, relocation.source_offset)
        print(
            f"{relocation.segment}:{relocation.source_offset:04X} "
            f"file+0x{file_offset:05X} type=0x{relocation.source_type:02X} "
            f"flags=0x{relocation.flags:02X} -> {relocation.target}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    disasm = subparsers.add_parser("disasm", help="annotated 16-bit disassembly")
    disasm.add_argument("segment", type=parse_number)
    disasm.add_argument("start", type=parse_number)
    disasm.add_argument("end", type=parse_number)

    xrefs = subparsers.add_parser("xrefs", help="relocations containing target text")
    xrefs.add_argument("target")

    args = parser.parse_args()
    image = NeImage(args.exe)
    if args.command == "disasm":
        disassemble(image, args.segment, args.start, args.end)
    elif args.command == "xrefs":
        print_xrefs(image, args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
