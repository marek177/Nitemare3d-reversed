#!/usr/bin/env python3
"""Evidence-pinned audit of Nitemare 3D DOS v2.0 WORX INT 63h.

Run only on the EXACT unpacked N3D_DOS_v2.0_IDA.EXE image; strict SHA
check is intentional. Reads real x86 jump-table bytes, NOT Ghidra text.

The 82 slots are the range 00..51 used by N3D and verified here. No
claim is made that a disassembler reached every instruction inside each
(nonzero) target or that slots beyond 0x51 are safe/defined.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_IMAGE_SHA256 = 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
EXPECTED_IMAGE_BYTES = 0x29D60
EXPECTED_HEADER_BYTES = 0x1C00
SEG_IMAGE_BASE = 0x15BF0
TABLE_CS_OFFSET = 0x2020
TABLE_IMAGE_OFFSET = SEG_IMAGE_BASE + TABLE_CS_OFFSET
ENTRY_COUNT = 0x52 # Inclusive 00h..51h; beyond this is UNASSESSED, not 'undefined'.
EXPECTED_NULL_INITIAL = {0x00, 0x27, 0x28}
DISPATCH_IMAGE = SEG_IMAGE_BASE + 0x30E6
# Actual bytes surrounding (a) AH -> offset*2 and (b) indirect near CALL cs:[si+2020].
DISPATCH_SIG_OFFSET = SEG_IMAGE_BASE + 0x30F9
DISPATCH_SIG = bytes.fromhex('50 86 e0 32 e4 d1 e0 8b f0 58 2e ff 94 20 20')
DISPATCH_EPILOGUE_OFFSET = SEG_IMAGE_BASE + 0x311A
DISPATCH_EPILOGUE = bytes.fromhex('2e ff 0e d4 3e 2e a1 e2 30 2e 8b 16 e4 30 cf')

# Statically decoded v0.11 handlers, CS-relative half-open byte spans.
# A handful include port polling: "leaf" is a historical label, not a claim
# that every operation is a hardware-independent straight line.
# The body is machine-audited byte-for-byte (the original is NOT redistributed).
# Conditional port loops in 4Fh/50h are also audited from original instructions.
LEAF_SPANS = {
    0x02: (0x485A, 0x4866, 'write BX to 2DF0; zero AH; write AX to 2010'),
    0x03: (0x308E, 0x309A, 'read16(2C47), then clear'),
    0x08: (0x45E5, 0x45ED, 'read masked CS byte 2DEA'),
    0x09: (0x309A, 0x30C1, 'BX*0x04A9 -> 32-bit counter copies 2C4B/2C4F, status reset; returns AX=04A9'),
    0x0A: (0x30C1, 0x30DB, 'restore 32-bit time counter 2C4B from 2C4F; reset 2C53'),
    0x0B: (0x30DB, 0x30E2, 'read zero-extended CS byte 2C53'),
    0x0E: (0x45DD, 0x45E5, 'read masked CS byte 2D62'),
    0x13: (0x3004, 0x3009, 'write AL to CS:2DBC'),
    0x16: (0x3009, 0x300E, 'write AL to CS:2DBD'),
    0x1C: (0x33AF, 0x33B9, 'return CS byte 2DCA bit 0'),
    0x1D: (0x3E5B, 0x3E67, 'write BL to 2C61; DS modified but ISR restores'),
    0x1F: (0x45F2, 0x45F9, 'write 1 to CS:2D62'),
    0x20: (0x372F, 0x3750, 'DSP detected: SB mixer port writes 22h,BL; else AX=FFFF'),
    0x21: (0x3771, 0x3792, 'DSP detected: SB mixer port writes 04h,BL; else AX=FFFF'),
    0x22: (0x3750, 0x3771, 'DSP detected: SB mixer port writes 26h,BL; else AX=FFFF'),
    0x24: (0x2F5F, 0x2F66, 'return AX=1234, DX=5678'),
    0x26: (0x2E76, 0x2E7D, 'write 1 to CS:2C0C'),
    0x2A: (0x41B3, 0x41CD, 'AX=(uint16(64*2012))/201A or product if divisor=0; DX remainder'),
    0x2B: (0x41CD, 0x41E7, 'AX=(uint16(64*2014))/201C or product if divisor=0; DX remainder'),
    0x2C: (0x41E7, 0x41F6, 'return CS byte[2016 + incoming AL]; internal CLC'),
    0x2D: (0x45ED, 0x45F2, 'return CS word 2C56'),
    0x30: (0x4470, 0x4476, 'return CS word 2C49 (internal CLC not propagated by IRET)'),
    0x31: (0x4CE1, 0x4CED, 'write (AL&3F) at word CS:[4BBF + 2*BX]'),
    0x32: (0x5675, 0x5679, 'return 0xFFFF'),
    0x36: (0x5664, 0x5670, 'read word CS:[4BEF + 2*AL]'),
    0x37: (0x4866, 0x486C, 'return CS word 2DF0'),
    0x3E: (0x3ED7, 0x3EDD, 'write BL to CS:3ED6'),
    0x43: (0x34BB, 0x34C1, 'write BX to CS:34B9'),
    0x44: (0x4C61, 0x4C6B, 'write 2 to word CS:[4BAF + 2*BX]'),
    0x46: (0x389A, 0x38A7, 'install DX:BX callback at CS:3896/3898'),
    0x47: (0x4C6B, 0x4C75, 'write 0 to word CS:[4BEF + 2*BX]'),
    0x4A: (0x2208, 0x2218, 'SB mixer write index 0Ah, value BL; AX low=BL, DX=base+5'),
    0x4B: (0x21DC, 0x21EC, 'SB mixer write index 0Ch, value BL; AX low=BL, DX=base+5'),
    0x4C: (0x21EC, 0x2208, 'SB mixer write index 2Eh, value (BL | BL<<4); AX low=value, DX=base+5'),
    0x4F: (0x5A3F, 0x5A6C, 'poll SB DSP write status, then OUT (base+0Ch), AL'),
    0x50: (0x5A1E, 0x5A3F, 'poll SB DSP read status, then IN (base+0Ah), AX=AL'),
    0x51: (0x3DB3, 0x3DCB, 'set 3DB1=1;2B96=AL;2B95=FF;2BC7=00'),
}

# Four additional contracts audited from v2.0 machine instructions in v0.12.
# AH19's INT21h close service, AH29's joystick port, and AH2E's PIT ports are
# provided by caller interfaces. AH2E transitive CALL 466A is also pinned.
COMPOSED_SPANS = {
    0x12: (0x3E2B, 0x3E5B, 'MIDI indexed store: (mode &20h) && AL>=B0h suppresses table write'),
    0x19: (0x335B, 0x337B, 'conditional DOS INT21/3Eh close; AX saved, DX externally observable'),
    0x29: (0x41F6, 0x4265, 'joystick button nibble, 40 writes then 800 reads of port 201h'),
    0x2E: (0x3E67, 0x3E77, 'PIT init with audited helper 466A..469E; disabled if 201E==1'),
}
HANDLER_SPANS = {**LEAF_SPANS, **COMPOSED_SPANS}

# Not present as part of handler body but necessary to validate AH=2Eh.
TRANSITIVE_HELPERS = {0x2E: (0x466A, 0x469F, 'PIT dividend FFFFh, calls ports 43h / 40h / 40h')}


def audit(exe_path: Path):
    raw = exe_path.read_bytes()
    if raw[:2] != b'MZ':
        raise ValueError('Expected unpacked 16-bit MZ executable')
    mz_paras = struct.unpack_from('<H', raw, 8)[0]
    hdr = mz_paras * 16
    if hdr != EXPECTED_HEADER_BYTES:
        raise ValueError(f'Unexpected MZ header {hdr:#x}')
    image = raw[hdr:]
    sha256 = hashlib.sha256(image).hexdigest()
    if len(image) != EXPECTED_IMAGE_BYTES or sha256 != EXPECTED_IMAGE_SHA256:
        raise ValueError(f'Not pinned Nitemare 3D DOS v2.0 image: size={len(image)}, sha256={sha256}')
    if image[DISPATCH_SIG_OFFSET:DISPATCH_SIG_OFFSET + len(DISPATCH_SIG)] != DISPATCH_SIG:
        raise ValueError('Indirect-call opcode/selector decode witness changed')
    if image[DISPATCH_EPILOGUE_OFFSET:DISPATCH_EPILOGUE_OFFSET + len(DISPATCH_EPILOGUE)] != DISPATCH_EPILOGUE:
        raise ValueError('AX/DX + IRET return witness changed')
    rows = []
    for ah in range(ENTRY_COUNT):
        image_at = TABLE_IMAGE_OFFSET + (ah * 2)
        target = struct.unpack_from('<H', image, image_at)[0]
        if target == 0:
            status = 'NULL_IN_INITIAL_IMAGE'
            absolute = None
        else:
            absolute = SEG_IMAGE_BASE + target
            if not (0 <= absolute < len(image)):
                raise ValueError(f'AH {ah:02X} target outside image: {absolute:#x}')
            status = ('LEAF_BYTE_AUDITED' if ah in LEAF_SPANS else
                      'BODY_AND_DEPS_AUDITED' if ah in COMPOSED_SPANS else 'ENTRYPOINT_ONLY')
        if ah in HANDLER_SPANS:
            begin, end, note = HANDLER_SPANS[ah]
            if target != begin or image[SEG_IMAGE_BASE+end-1] != 0xc3:
                raise ValueError(f'Leaf range/return marker does not match AH {ah:02X}')
            span = image[SEG_IMAGE_BASE+begin:SEG_IMAGE_BASE+end]
            bodyhash = hashlib.sha256(span).hexdigest()
        else:
            note, bodyhash = None, None
        rows.append({
            'ah': f'{ah:02X}', 'table_word_image_offset': f'0x{image_at:05X}',
            'target_cs_offset': f'0x{target:04X}',
            'target_image_offset': f'0x{absolute:05X}' if absolute is not None else None,
            'status': status, 'leaf_summary': note, 'leaf_body_sha256': bodyhash
        })
    nulls = {int(r['ah'], 16) for r in rows if r['status'] == 'NULL_IN_INITIAL_IMAGE'}
    if nulls != EXPECTED_NULL_INITIAL:
        raise ValueError(f'Null slot witnesses unexpectedly differ: {sorted(nulls)}')
    transitive = {}
    for ah, (begin, end, desc) in TRANSITIVE_HELPERS.items():
        if image[SEG_IMAGE_BASE + end - 1] != 0xC3:
            raise ValueError(f'Helper for {ah:02X} missing RET')
        span = image[SEG_IMAGE_BASE + begin:SEG_IMAGE_BASE + end]
        if ah == 0x2E:
            # CALL NEAR 466Ah occurs at 3E6Bh; divisor is known FFFFh.
            if image[SEG_IMAGE_BASE+0x3E6B:SEG_IMAGE_BASE+0x3E6E] != bytes.fromhex('e8 fc 07'):
                raise ValueError('AH2E transitive PIT helper call changed')
        transitive[f'{ah:02X}'] = {
            'start': f'{begin:04X}', 'end_exclusive':f'{end:04X}',
            'sha256':hashlib.sha256(span).hexdigest(), 'purpose':desc
        }
    return {
        'source_filename': exe_path.name,
        'original_image_sha256': sha256,
        'mz_header_bytes': hdr,
        'load_image_bytes': len(image),
        'table_segment': '15BF',
        'table_offset_cs': f'0x{TABLE_CS_OFFSET:04X}',
        'table_offset_image': f'0x{TABLE_IMAGE_OFFSET:05X}',
        'selector_range_audited': '00h..51h',
        'selectors_audited': len(rows),
        'nonzero_targets': len(rows)-len(nulls),
        'null_initial_targets': sorted(f'{n:02X}' for n in nulls),
        'leaf_bodies_verified': len(LEAF_SPANS),
        'composed_bodies_verified': len(COMPOSED_SPANS),
        'machine_audited_handler_contracts': len(HANDLER_SPANS),
        'nonzero_handlers_not_reconstructed': len(rows)-len(nulls)-len(HANDLER_SPANS),
        'transitive_helpers': transitive,
        'dispatcher_signature_hex': DISPATCH_SIG.hex(' '),
        'dispatch_return_epilogue_hex': DISPATCH_EPILOGUE.hex(' '),
        'table_sha256_00_to_51': hashlib.sha256(image[TABLE_IMAGE_OFFSET:TABLE_IMAGE_OFFSET+ENTRY_COUNT*2]).hexdigest(),
        'qualifiers': [
            'No INT63 bounds guard before indirect CALL is visible in original dispatcher.',
            'Null targets are INITIAL IMAGE words, not proven permanently null at runtime.',
            'Nonzero entry point does NOT imply a reconstructed inner algorithm.',
            'AH19 INT21 and AH29/AH2E ports are external side-effect boundaries.',
            'AH2E transitive helper 466A is audited; other IRQ/call graphs remain incomplete.', 
            'IRET restores caller FLAGS unless the saved interrupt frame is modified.',
            'Original full machine executable is intentionally not embedded in this output.'
        ],
        'dispatch': rows
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('exe', type=Path)
    p.add_argument('--json', metavar='FILE')
    p.add_argument('--csv', metavar='FILE')
    args = p.parse_args()
    report = audit(args.exe)
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.csv:
        with Path(args.csv).open('w', newline='', encoding='utf-8') as fh:
            writer=csv.DictWriter(fh, fieldnames=list(report['dispatch'][0]))
            writer.writeheader()
            writer.writerows(report['dispatch'])
    print(json.dumps({k:v for k,v in report.items() if k != 'dispatch'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
