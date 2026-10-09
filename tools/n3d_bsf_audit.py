#!/usr/bin/env python3
"""Read-only Nitemare-3D BSF decoder / integrity audit.

Scope: the documented 54-byte NITE3D.BSF header and three separately XORed
resources. This is an independently written verifier, not an EXE patcher,
license modifier, or replacement for original-runtime tracing.

Source/evidence: docs/BSF_PROTECTION_RE_v5.md (this repository) and
https://github.com/vs-sr-dev/pc-nitemare3d-doc/blob/main/docs/08-branding-and-the-bsf.md
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import struct
import sys

KEY = b"Copyright 1992, David P Gray, Gray Design Associates"
HEADER_BYTES = 54
CHUNK_COUNT = 3

if len(KEY) != 52:
    raise RuntimeError("BSF XOR key length is not 52")


class BSFError(ValueError):
    """Malformed archive or failed read-only integrity check."""


def xor_bytes(data: bytes, seed: int = 0) -> int:
    accumulator = seed & 0xFF
    for value in data:
        accumulator ^= value
    return accumulator


def transform(data: bytes) -> bytes:
    """XOR a *single* buffer; every header/chunk call starts at key index zero."""
    return bytes(value ^ KEY[i % len(KEY)] for i, value in enumerate(data))


@dataclass(frozen=True)
class Chunk:
    index: int
    offset: int
    size: int
    ciphertext_xor: int


@dataclass(frozen=True)
class Archive:
    raw: bytes
    distributor: str
    registration_flag: int
    expected_dos_exe_xor: int
    expected_map1_xor: int
    chunks: tuple[Chunk, ...]
    contiguous: bool

    @property
    def registered(self) -> bool:
        return self.registration_flag != 0

    def decoded_chunk(self, index: int) -> bytes:
        if not 0 <= index < len(self.chunks):
            raise BSFError(f"Chunk index out of range: {index}")
        c = self.chunks[index]
        return transform(self.raw[c.offset:c.offset + c.size])

    def summary(self) -> dict:
        return {
            "file_bytes": len(self.raw),
            "header_ciphertext_xor": "0x00 (valid)",
            "distributor": self.distributor,
            "registered": self.registered,
            "registration_flag": self.registration_flag,
            "expected_dos_exe_xor": f"0x{self.expected_dos_exe_xor:02X}",
            "expected_map1_xor": f"0x{self.expected_map1_xor:02X}",
            "chunks": [
                {"index": c.index, "offset": c.offset, "size": c.size,
                 "ciphertext_xor": f"0x{c.ciphertext_xor:02X}"}
                for c in self.chunks
            ],
            "chunks_cover_file_without_gaps": self.contiguous,
        }


def parse_bsf(raw: bytes) -> Archive:
    if len(raw) < HEADER_BYTES:
        raise BSFError(f"Truncated BSF header: {len(raw)} < {HEADER_BYTES}")

    encoded_header = raw[:HEADER_BYTES]
    header_xor = xor_bytes(encoded_header)
    if header_xor:
        raise BSFError(f"Invalid ciphertext header XOR: 0x{header_xor:02X}; expected 0x00")
    header = transform(encoded_header)

    offsets = struct.unpack_from("<3I", header, 36)
    sizes = struct.unpack_from("<3H", header, 48)
    spans: list[tuple[int, int]] = []
    chunks: list[Chunk] = []
    for index, (offset, size) in enumerate(zip(offsets, sizes)):
        end = offset + size
        if offset < HEADER_BYTES or end > len(raw):
            raise BSFError(
                f"Chunk {index} outside BSF: offset={offset}, size={size}, file={len(raw)}"
            )
        spans.append((offset, end))
        chunks.append(Chunk(index, offset, size, xor_bytes(raw[offset:end])))

    ordered = sorted(spans)
    for previous, following in zip(ordered, ordered[1:]):
        if following[0] < previous[1]:
            raise BSFError(f"Overlapping BSF chunks: {previous} and {following}")

    cursor = HEADER_BYTES
    for begin, end in ordered:
        if begin != cursor:
            break
        cursor = end
    contiguous = cursor == len(raw) and (
        all(begin == HEADER_BYTES + sum(sizes[j] for j in range(i))
            for i, (begin, _) in enumerate(spans))
    )

    distributor = header[4:36].split(b"\x00", 1)[0].decode("cp437", errors="replace")
    return Archive(
        raw=raw,
        distributor=distributor,
        registration_flag=header[3],
        expected_dos_exe_xor=header[1],
        expected_map1_xor=header[2],
        chunks=tuple(chunks),
        contiguous=contiguous,
    )


def checksum_file(path: Path) -> int:
    """Weak original file-integrity XOR, initially seeded to 0x7B."""
    value = 0x7B
    with path.open("rb") as stream:
        while True:
            buffer = stream.read(65536)
            if not buffer:
                break
            value = xor_bytes(buffer, value)
    return value


def verify_installation(
    archive: Archive, platform: str, *, exe: Path | None, map1: Path | None
) -> list[str]:
    """Check the build-specific policy; never edit or generate game files."""
    if platform not in {"dos", "win16"}:
        raise BSFError(f"Unknown platform: {platform!r}")
    result: list[str] = []

    if platform == "dos":
        if exe is None:
            raise BSFError("DOS verification requires N3D.EXE")
        actual = checksum_file(exe)
        if actual != archive.expected_dos_exe_xor:
            raise BSFError(
                f"{exe.name}: expected XOR 0x{archive.expected_dos_exe_xor:02X}, "
                f"found 0x{actual:02X}"
            )
        result.append(f"{exe.name}: DOS executable XOR 0x{actual:02X} OK")
    else:
        result.append("Win16: BSF EXE checksum is not enforced by original loader")

    if archive.registered:
        result.append("MAP.1: registered build; checksum check skipped")
    else:
        if map1 is None:
            raise BSFError("Shareware verification requires MAP.1")
        actual = checksum_file(map1)
        if actual != archive.expected_map1_xor:
            raise BSFError(
                f"{map1.name}: expected XOR 0x{archive.expected_map1_xor:02X}, "
                f"found 0x{actual:02X}"
            )
        result.append(f"{map1.name}: shareware MAP.1 XOR 0x{actual:02X} OK")
    return result


def manual_image_ids(text: str) -> list[int]:
    """For %oN% markup, the original IMG image ID is N + 256."""
    return sorted({int(number) + 256 for number in re.findall(r"%o(\d+)%", text)})


def source_path(value: Path) -> Path:
    if value.is_dir():
        for filename in ("NITE3D.BSF", "nite3d.bsf"):
            candidate = value / filename
            if candidate.is_file():
                return candidate
        raise BSFError(f"No NITE3D.BSF in {value}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    info = commands.add_parser("info", help="Show decoded header and chunk table")
    info.add_argument("source", type=Path, help="BSF file or its installation folder")
    info.add_argument("--json", action="store_true", help="Machine-readable summary")

    verify = commands.add_parser("verify", help="Check original DOS/Win16 integrity policy")
    verify.add_argument("source", type=Path)
    verify.add_argument("--platform", required=True, choices=("dos", "win16"))
    verify.add_argument("--exe", type=Path, help="DOS N3D.EXE (defaults to sibling file)")
    verify.add_argument("--map1", type=Path, help="MAP.1 (defaults to sibling file)")

    extract = commands.add_parser("text", help="Print locally decoded CP437 resource")
    extract.add_argument("source", type=Path)
    extract.add_argument("index", type=int, choices=range(CHUNK_COUNT))
    extract.add_argument("--image-ids", action="store_true",
                         help="Print referenced IMG image IDs rather than resource text")

    args = parser.parse_args(argv)
    try:
        path = source_path(args.source)
        archive = parse_bsf(path.read_bytes())
        if args.command == "info":
            if args.json:
                print(json.dumps(archive.summary(), indent=2, ensure_ascii=False))
            else:
                for key, value in archive.summary().items():
                    print(f"{key}: {value}")
        elif args.command == "verify":
            if args.platform == "win16" and args.exe is not None:
                raise BSFError("--exe is only meaningful for --platform dos")
            base = path.parent
            exe = (args.exe or base / "N3D.EXE") if args.platform == "dos" else None
            map1 = args.map1 or base / "MAP.1"
            for line in verify_installation(archive, args.platform, exe=exe, map1=map1):
                print(line)
        else:
            text = archive.decoded_chunk(args.index).decode("cp437")
            if args.image_ids:
                if args.index != 1:
                    raise BSFError("Image markup analysis applies to manual chunk 1")
                print(" ".join(str(number) for number in manual_image_ids(text)))
            else:
                sys.stdout.write(text)
                if not text.endswith("\n"):
                    sys.stdout.write("\n")
        return 0
    except (OSError, BSFError) as error:
        print(f"BSF audit error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
