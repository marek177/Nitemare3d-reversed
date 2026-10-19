#!/usr/bin/env python3
"""Hash-pinned Win16 NE timer disassembly and relocation evidence extractor.

Reads original Nitemare 3-D EXE bytes from a local EXE or ZIP (including nested
ZIPs) without distributing them. It is a static audit, not runtime emulation.

Requires Capstone, already used by tools/ne_renderer_audit.py.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import zipfile

from capstone import CS_ARCH_X86, CS_MODE_16, Cs
from ne_renderer_audit import NeImage

MAX_EXE_BYTES = 8 * 1024 * 1024
MAX_NESTED_ZIP_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True)
class Profile:
    version: str
    sha256: str
    raw_size: int
    seg3_file_offset: int
    seg3_length: int
    timer_init: int
    read_time: int
    imports: tuple[tuple[int, str, int], ...]


PROFILES = (
    Profile("1.0", "6476e259a3a763e2985f22ea6655929e5b313f63ca4bcb976f98b6d50b72140c",
            229008, 90016, 61378, 0xD43E, 0xD498,
            ((0xD457, "MMSYSTEM", 604), (0xD47D, "MMSYSTEM", 605),
             (0xD490, "MMSYSTEM", 606), (0xD49F, "MMSYSTEM", 607),
             (0xD4A6, "USER", 13))),
    Profile("1.3", "926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156",
            229136, 90016, 61340, 0xD44A, 0xD4A4,
            ((0xD463, "MMSYSTEM", 604), (0xD489, "MMSYSTEM", 605),
             (0xD49C, "MMSYSTEM", 606), (0xD4AB, "MMSYSTEM", 607),
             (0xD4B2, "USER", 13))),
    Profile("1.6", "5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418",
            230128, 90016, 61409, 0xD5BE, 0xD618,
            ((0xD5D7, "MMSYSTEM", 604), (0xD5FD, "MMSYSTEM", 605),
             (0xD610, "MMSYSTEM", 606), (0xD61F, "MMSYSTEM", 607),
             (0xD626, "USER", 13))),
    Profile("1.8", "144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22",
            230224, 90016, 61301, 0xD5BE, 0xD618,
            ((0xD5D7, "MMSYSTEM", 604), (0xD5FD, "MMSYSTEM", 605),
             (0xD610, "MMSYSTEM", 606), (0xD61F, "MMSYSTEM", 607),
             (0xD626, "USER", 13))),
    Profile("1.10", "12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481",
            230400, 90048, 61372, 0xD66C, 0xD6C6,
            ((0xD685, "MMSYSTEM", 604), (0xD6AB, "MMSYSTEM", 605),
             (0xD6BE, "MMSYSTEM", 606), (0xD6CD, "MMSYSTEM", 607),
             (0xD6D4, "USER", 13))),
)
HASH_TO_PROFILE = {p.sha256: p for p in PROFILES}


def iter_zip_exes(data: bytes, description: str, depth: int = 0):
    """Only read bounded EXE members and at most two nested ZIP levels."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for entry in sorted(archive.infolist(), key=lambda item: item.filename):
            if entry.is_dir() or entry.flag_bits & 1:
                continue
            name = entry.filename.replace("\\", "/")
            suffix = name.lower()
            if suffix.endswith(".exe") and entry.file_size <= MAX_EXE_BYTES:
                member = archive.read(entry)
                # Win16 shareware distributions sometimes place NITE3W.EXE
                # inside a ZIP self-extracting .EXE (N3WUNR.EXE).
                # Parse its appended ZIP directory; never execute the wrapper.
                if depth < 2 and zipfile.is_zipfile(io.BytesIO(member)):
                    yield from iter_zip_exes(
                        member, description + "::" + name, depth + 1)
                yield description + "::" + name, member
            elif (suffix.endswith(".zip") and depth < 2 and
                  entry.file_size <= MAX_NESTED_ZIP_BYTES):
                nested = archive.read(entry)
                if zipfile.is_zipfile(io.BytesIO(nested)):
                    yield from iter_zip_exes(
                        nested, description + "::" + name, depth + 1)


def find_pinned_original(path: Path, only_version: str | None = None):
    if path.suffix.lower() == ".zip":
        candidates = iter_zip_exes(path.read_bytes(), path.name)
    else:
        data = path.read_bytes()
        if len(data) > MAX_EXE_BYTES:
            raise ValueError("Input EXE is unexpectedly large; supply the original NE EXE or its ZIP")
        candidates = [(path.name, data)]
    seen = 0
    for name, data in candidates:
        seen += 1
        sha = hashlib.sha256(data).hexdigest()
        profile = HASH_TO_PROFILE.get(sha)
        if profile and (only_version is None or only_version == profile.version):
            if len(data) != profile.raw_size:
                raise ValueError("Original SHA matched but byte length differed")
            return name, data, profile
    raise ValueError(
        f"No hash-pinned Win16 Nitemare EXE found among {seen} candidate(s). "
        "Only original Windows 1.0, 1.3, 1.6, 1.8, 1.10 hashes are accepted. "
        "An installer, DOS executable, or an unverified patch is not equivalent."
    )


def import_at(image: NeImage, ip: int, module: str, ordinal: int):
    """Require FAR call opcode and a matching NE imported-ordinal relocation."""
    instruction = image.bytes_at(3, ip, ip + 5)
    fixups = [r for r in image.relocations
              if r.segment == 3 and ip + 1 <= r.source_offset <= ip + 4]
    wanted = f"import {module} ordinal {ordinal}".lower()
    matching = [r for r in fixups if r.target.lower() == wanted]
    return {
        "caller": f"3:{ip:04X}",
        "opcode_far_call_9a": instruction[0] == 0x9A,
        "target_expected": f"{module}.{ordinal}",
        "relocation_matches": [
            {"source": f"3:{r.source_offset:04X}", "type": r.source_type,
             "flags": r.flags, "target": r.target} for r in matching
        ],
        "verified": instruction[0] == 0x9A and bool(matching),
    }


def candidate_near_calls(image: NeImage, segment: int, destination: int):
    """Raw E8 scan only: matches may be immediate data, never claim a CFG closure."""
    entry = image.segment(segment)
    if not entry.file_offset:
        return []
    raw = image.bytes_at(segment, 0, entry.length)
    candidates = []
    for ip in range(len(raw) - 2):
        if raw[ip] != 0xE8:
            continue
        displacement = struct.unpack_from("<h", raw, ip + 1)[0]
        target = (ip + 3 + displacement) & 0xFFFF
        if target == destination:
            candidates.append(f"{segment}:{ip:04X}")
    return candidates


def internal_far_relocations(image: NeImage, segment: int, destination: int):
    """Fixup-backed references; only some source locations may be CALL instructions."""
    target = f"internal {segment}:{destination:04X}".lower()
    return [
        {"source": f"{r.segment}:{r.source_offset:04X}",
         "type": r.source_type, "target": r.target,
         "flags": r.flags}
        for r in image.relocations if r.target.lower() == target
    ]


def disassemble_region(image: NeImage, segment: int, start: int, end: int):
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    lookup = image.relocation_map(segment)
    lines = []
    for insn in decoder.disasm(image.bytes_at(segment, start, end), start):
        fixes = [lookup[offset].target
                 for offset in range(insn.address, insn.address + insn.size)
                 if offset in lookup]
        lines.append({
            "address": f"{segment}:{insn.address:04X}",
            "file_offset": f"0x{image.file_offset(segment, insn.address):X}",
            "bytes": bytes(insn.bytes).hex(" "),
            "mnemonic": insn.mnemonic,
            "operands": insn.op_str,
            "relocations": fixes,
        })
    return lines


def verify_win18_timer_call_and_stack(image: NeImage) -> dict:
    """Exact, build-specific facts from SHA-pinned Win16 1.8 instructions.

    The noninitialized local is a *source-level risk fact*, not permission
    to read undefined C++ stack memory in the reconstructed engine.
    """
    expected_bytes = {
        0x0EE6: "6a 00",         # immediate arg 0 -> initialize
        0x0EE8: "9a be d5",      # FAR CALL 3:D5BE (segment word NE-fixed)
        0x0EED: "83 c4 02",      # caller pops int arg
        0x0F22: "6a 01",         # immediate arg 1 -> cleanup
        0x0F24: "9a be d5",      # FAR CALL 3:D5BE
        0x0F29: "83 c4 02",
        0xD5BE: "c8 06 00 00",   # ENTER 6,0; local 6 bytes uninitialized
        0xD5D0: "8d 46 fa",      # pointer to [BP-6] caps struct
        0xD5D5: "6a 04",         # 4-byte TIMECAPS output
        0xD5E3: "a2 b2 46",      # flag DS:46B2 from timeGetDevCaps status
        0xD5E6: "8b 76 fa",      # SI <- wPeriodMin at [BP-6]
        0xD5FC: "56",            # begin with pushed SI
        0xD5FD: "9a",            # far MMSYSTEM 605
        0xD60D: "ff 76 fe",      # end with pushed [BP-2]
        0xD610: "9a",            # far MMSYSTEM 606
    }
    for ip, hex_bytes in expected_bytes.items():
        expected = bytes.fromhex(hex_bytes)
        actual = image.bytes_at(3, ip, ip + len(expected))
        if actual != expected:
            raise ValueError(
                f"Win16 v1.8 timer instruction changed at 3:{ip:04X}: "
                f"{actual.hex()} vs {expected.hex()}"
            )
    fixups = internal_far_relocations(image, 3, 0xD5BE)
    callsite_by_fixup_source = {x["source"] for x in fixups}
    if callsite_by_fixup_source != {"3:0EEB", "3:0F27"}:
        raise ValueError(
            "Win16 v1.8 timer initializer FAR caller relocation census changed"
        )
    imports = [
        import_at(image, 0xD5D7, "MMSYSTEM", 604),
        import_at(image, 0xD5FD, "MMSYSTEM", 605),
        import_at(image, 0xD610, "MMSYSTEM", 606),
    ]
    if not all(x["verified"] for x in imports):
        raise ValueError("v1.8 timer imports not independently fixup-backed")
    # Complete linear instruction body D5BE..D617, including early returns.
    instructions = disassemble_region(image, 3, 0xD5BE, 0xD618)
    use_of_uninitialized = [
        row for row in instructions
        if "[bp - 2]" in row["operands"]
    ]
    if len(use_of_uninitialized) != 1 or (
            use_of_uninitialized[0]["mnemonic"] != "push" or
            use_of_uninitialized[0]["address"] != "3:D60D"):
        raise ValueError("v1.8 BP-2 cleanup read assumption no longer unique")
    return {
        "proof": "SHA_PINNED_ORIGINAL_BYTE_STATIC",
        "build": "1.8",
        "init_far_call": "3:0EE8",
        "init_immediate_argument": 0,
        "cleanup_far_call": "3:0F24",
        "cleanup_immediate_argument": 1,
        "imported_timer_api_calls_verified": 3,
        "timer_local_allocation_bytes": 6,
        "time_get_dev_caps_buffer": "[BP-6]",
        "time_get_dev_caps_output_bytes": 4,
        "time_begin_period_argument": "SI = max(wPeriodMin, 10)",
        "time_end_period_argument": "WORD PTR [BP-2]",
        "time_end_period_local_initialized_by_function": False,
        "observed_bp_minus_2_references": use_of_uninitialized,
        "verified_timer_fixup_caller_sources": sorted(callsite_by_fixup_source),
        "limits": [
            "No dynamic timing measurement",
            "The original stack-residue value is not statically a fixed constant",
            "Do not reproduce a host-language uninitialized read in portable C++",
            "Only version 1.8 is byte-verified by this bounded claim"
        ],
    }


def inspect(image: NeImage, profile: Profile):
    seg3 = image.segment(3)
    if (seg3.file_offset, seg3.length) != (
            profile.seg3_file_offset, profile.seg3_length):
        raise ValueError("NE segment-3 layout differs from pinned original evidence")
    calls = [import_at(image, ip, module, ordinal)
             for ip, module, ordinal in profile.imports]
    if not all(c["verified"] for c in calls):
        raise ValueError(
            "A pinned import relocation/callsite did not match. "
            "Do not infer the timeEndPeriod argument from unverified bytes."
        )
    end = profile.read_time + 0x1B
    lines = disassemble_region(image, 3, profile.timer_init, end)
    cleanup_ip = next(ip for ip, _, ordinal in profile.imports if ordinal == 606)
    near_cleanup = [row for row in lines
                    if cleanup_ip - 24 <= int(row["address"].split(":")[1], 16)
                    <= cleanup_ip + 5]
    win18_proof = (
        verify_win18_timer_call_and_stack(image)
        if profile.version == "1.8" else None
    )
    return {
        "win18_timer_stack_proof": win18_proof,
        "build": profile.version,
        "source_sha256": profile.sha256,
        "source_size": profile.raw_size,
        "logical_segment": 3,
        "segment_3_file_offset": seg3.file_offset,
        "segment_3_length": seg3.length,
        "timer_init": f"3:{profile.timer_init:04X}",
        "read_time": f"3:{profile.read_time:04X}",
        "verified_import_anchors": calls,
        "cleanup_call_context": near_cleanup,
        "timer_function_disassembly": lines,
        "candidate_near_E8_xrefs_to_timer_init": candidate_near_calls(
            image, 3, profile.timer_init),
        "fixup_backed_internal_references_to_timer_init":
            internal_far_relocations(image, 3, profile.timer_init),
        "limits": [
            "E8 byte scan includes non-instruction candidates until instruction boundaries/CFG are proved",
            "Indirect writable FAR pointers require additional dataflow/reachability proof",
            "The exact timeEndPeriod argument must be read from the preceding instructions",
            "No original EXE is included in the generated JSON",
            "No runtime or timing parity is implied",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="Original Win16 EXE or ZIP of Win16 EXEs")
    ap.add_argument("--version", choices=[p.version for p in PROFILES],
                    help="Select a specific verified build")
    ap.add_argument("--output", type=Path, help="Optional local JSON report output")
    args = ap.parse_args(argv)
    try:
        source, original, profile = find_pinned_original(args.input, args.version)
        with tempfile.TemporaryDirectory(prefix="n3d-ne-static-") as tmp:
            copied = Path(tmp, "verified_nite3w.exe")
            copied.write_bytes(original)
            image = NeImage(copied)
            report = inspect(image, profile)
        report["source_label"] = source
        result = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Static audit written to {args.output}")
        else:
            print(result)
        return 0
    except (ValueError, OSError, zipfile.BadZipFile, struct.error) as exc:
        print(f"Cannot validate Win16 binary: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
