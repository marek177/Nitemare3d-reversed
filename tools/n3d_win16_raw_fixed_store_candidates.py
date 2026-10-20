#!/usr/bin/env python3
"""Conservative byte-pattern census of candidate absolute DS writes.

Scans *all file-backed code NE segments* for selected x86-16 absolute
memory-write patterns whose address/operand width overlaps a target
DGROUP byte. Raw matches can be immediates, data islands or otherwise
not CFG-decodable: they are ALWAYS CANDIDATES, NEVER proved calls/stores.

The complete opcode space and computed SI/DI/BX/BP/ES aliases remain
outside scope. Can run after exact SHA-pinned game EXE identification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


# prefix before absolute 16-bit operand, operand width in bytes.
PATTERNS: tuple[tuple[bytes, int, str], ...] = (
    (b"\xA2", 1, "MOV_moffs8_AL"),
    (b"\xA3", 2, "MOV_moffs16_AX"),
    (b"\x66\xA3", 4, "MOV_moffs32_EAX"),
    (b"\x88\x06", 1, "MOV_abs8_reg8"),
    (b"\x89\x06", 2, "MOV_abs16_reg16"),
    (b"\x66\x89\x06", 4, "MOV_abs32_reg32"),
    (b"\xC6\x06", 1, "MOV_abs8_imm8"),
    (b"\xC7\x06", 2, "MOV_abs16_imm16"),
    (b"\x66\xC7\x06", 4, "MOV_abs32_imm32"),
    (b"\xFE\x06", 1, "INC_abs8"),
    (b"\xFE\x0E", 1, "DEC_abs8"),
    (b"\xFF\x06", 2, "INC_abs16"),
    (b"\xFF\x0E", 2, "DEC_abs16"),
    (b"\x66\xFF\x06", 4, "INC_abs32"),
    (b"\x66\xFF\x0E", 4, "DEC_abs32"),
    (b"\x86\x06", 1, "XCHG_abs8_reg8"),
    (b"\x87\x06", 2, "XCHG_abs16_reg16"),
    (b"\x66\x87\x06", 4, "XCHG_abs32_reg32"),
    (b"\x8F\x06", 2, "POP_abs16"),
    (b"\x66\x8F\x06", 4, "POP_abs32"),
)

GROUP_IMM_WRITES: tuple[tuple[int, int], ...] = (
    (0x80, 1), (0x81, 2), (0x83, 2),
)


def overlapping_sources(target: int, width: int) -> range:
    return range(max(0, target - width + 1), target + 1)


def scan_bytes(buf: bytes, *, segment: int, target: int) -> list[dict]:
    """Forensic raw-byte scan: do not infer actual instruction boundaries."""
    hits = []
    seen = set()

    def record(offset: int, start: int, width: int, name: str,
               length: int) -> None:
        if not (start <= target < start + width):
            return
        key = (offset, name, start)
        if key in seen:
            return
        seen.add(key)
        prefix = buf[max(0, offset - 5):offset].hex(" ")
        inst = buf[offset:offset+length].hex(" ")
        hits.append({
            "source": f"{segment}:{offset:04X}",
            "suggested_instruction": name,
            "ds_absolute_start": f"{start:04X}",
            "bytes_written_if_executed": width,
            "prefix_context": prefix,
            "matched_opcode_and_address": inst,
            "evidence": "RAW_PATTERN_ONLY_NOT_CFG_CONFIRMED",
        })

    for opcode, width, name in PATTERNS:
        for address in overlapping_sources(target, width):
            needle = opcode + address.to_bytes(2, "little")
            index = buf.find(needle)
            while index >= 0:
                record(index, address, width, name, len(needle))
                index = buf.find(needle, index + 1)

    # Group1 operations with direct memory address (modrm mod=00 rm=110).
    # reg=7 is CMP and writes nothing; reg=0..6 are arithmetic/logical RMW.
    for opcode, width in GROUP_IMM_WRITES:
        for reg in range(7):
            modrm = (reg << 3) | 6
            for address in overlapping_sources(target, width):
                head = bytes((opcode, modrm)) + address.to_bytes(2,"little")
                index = buf.find(head)
                while index >= 0:
                    record(index,address,width,
                           f"GRP1_RMW_{opcode:02X}_reg{reg}",len(head))
                    index = buf.find(head,index+1)

    # Operand-size prefix can produce a wider DWORD memory operation; even
    # though a 16-bit pattern is also found one byte later, record it as a
    # separately flagged 32-bit candidate rather than silently coalescing.
    for opcode in (0x81,0x83):
        width = 4
        for reg in range(7):
            modrm = (reg << 3) | 6
            for address in overlapping_sources(target, width):
                head = bytes((0x66,opcode,modrm)) + address.to_bytes(2,"little")
                index=buf.find(head)
                while index >=0:
                    record(index,address,width,
                           f"GRP1_DWORD_RMW_{opcode:02X}_reg{reg}",len(head))
                    index=buf.find(head,index+1)

    return sorted(hits,key=lambda row: (int(row["source"].split(":")[0]),
                                        int(row["source"].split(":")[1],16),
                                        row["suggested_instruction"]))


def audit_image(image: Any, target: int = 0x46B2) -> dict:
    code_segments = []
    matches = []
    for s in image.segments:
        if not s.file_offset or s.flags & 0x0001:
            continue
        code_segments.append(s.number)
        matches.extend(scan_bytes(image.bytes_at(s.number,0,s.length),
                                  segment=s.number,target=target))
    return {
        "target": f"DS:{target:04X}",
        "source_kind": "RAW_NE_CODE_BYTES_FROM_EXE",
        "file_backed_code_segments_scanned": code_segments,
        "candidate_count": len(matches),
        "raw_fixed_address_store_candidates": matches,
        "all_candidates_are_instruction_boundary_validated": False,
        "register_based_or_alias_writes_excluded": False,
        "source_scope": [
            "Selected x86-16 direct-moffs / modrm-absolute write encodings",
            "Group1 arithmetic/logical direct-absolute RMW patterns",
            "Not complete x86 ISA and not a CFG proof",
            "Raw patterns may occur inside tables, constants or false instruction starts",
        ]
    }


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input",type=Path,help="exact original NITE3W.EXE or ZIP")
    ap.add_argument("--version",default="1.8",choices=["1.0","1.3","1.6","1.8","1.10"])
    ap.add_argument("--address",type=lambda value:int(value,0),default=0x46B2)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    from n3d_win16_timer_binary_proof import find_pinned_original
    from ne_renderer_audit import NeImage
    import tempfile
    import hashlib
    src,data,p=find_pinned_original(args.input,args.version)
    with tempfile.TemporaryDirectory(prefix="n3d-raw-overlap-") as tmp:
        path=Path(tmp,"verified_n3d.exe")
        path.write_bytes(data)
        report=audit_image(NeImage(path),args.address)
    report["source"]=src
    report["whole_exe_sha256"]=hashlib.sha256(data).hexdigest()
    report["win16_version"]=p.version
    data=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.write_text(data,encoding="utf-8")
        print(f"Wrote {args.output} ({report['candidate_count']} raw candidates)")
    else:
        print(data)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
