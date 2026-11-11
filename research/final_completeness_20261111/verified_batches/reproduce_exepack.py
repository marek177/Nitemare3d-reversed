"""Reproduce DOS2.0 EXEPACK transform; integrity evidence, not semantic coverage.

Run: python reproduce_exepack.py EXE REFERENCE_BIN OUTPUT_DIRECTORY
Offsets in emitted CSVs are zero-based, ends exclusive. No game code executes.
"""
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def word(data, offset):
    require(0 <= offset <= len(data)-2, 'word outside input')
    return struct.unpack_from('<H', data, offset)[0]

def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    exe_path, reference_path, out_path = map(Path, sys.argv[1:])
    exe, reference = exe_path.read_bytes(), reference_path.read_bytes()
    require(digest(exe) == '552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301', 'unexpected EXE')
    require(exe[:2] == b'MZ', 'missing MZ signature')
    header_size = word(exe, 8)*16
    declared_size = (word(exe, 4)-1)*512 + (word(exe, 2) or 512)
    require(declared_size == len(exe), 'MZ declared length mismatch')
    packed = exe[header_size:declared_size]
    stub = word(exe, 22)*16
    require(stub+16 <= len(packed), 'stub outside image')
    ip, cs, reserved, packed_size, sp, ss, output_paragraphs, signature = struct.unpack_from('<8H', packed, stub)
    require(signature == 0x4252, 'missing EXEPACK RB signature')
    output = bytearray(output_paragraphs*16)
    source, destination = stub-1, len(output)-1
    trimmed = 0
    while source >= 0 and trimmed < 16 and packed[source] == 255:
        source -= 1
        trimmed += 1
    command_end = source+1
    blocks = []
    while True:
        require(source >= 2, 'truncated command')
        end = source+1
        opcode, count = packed[source], word(packed, source-2)
        source -= 3
        require(opcode & 0xfe in (0xb0, 0xb2), 'invalid EXEPACK command')
        require(count > 0 and destination-count+1 >= 0, 'invalid output bounds')
        start, stop = destination-count+1, destination+1
        if opcode & 0xfe == 0xb0:
            require(source >= 0, 'missing fill byte')
            output[start:stop] = bytes([packed[source]])*count
            source -= 1
        else:
            require(source-count+1 >= 0, 'literal input underflow')
            output[start:stop] = packed[source-count+1:source+1]
            source -= count
        blocks.append(dict(opcode=opcode, count=count, packed_start=source+1,
                           packed_end_exclusive=end, image_start=start,
                           image_end_exclusive=stop))
        destination -= count
        if opcode & 1:
            break
    require(source == destination, 'literal prefix source/output mismatch')
    output[:destination+1] = packed[:source+1]
    # Re-encode with the recovered commands, preserving the literal prefix.
    encoded = bytearray(output[:destination+1])
    for block in reversed(blocks):
        chunk = output[block['image_start']:block['image_end_exclusive']]
        encoded.extend(chunk[:1] if block['opcode'] & 0xfe == 0xb0 else chunk)
        encoded.extend(struct.pack('<HB', block['count'], block['opcode']))
    require(encoded == packed[:command_end], 'compressed stream roundtrip mismatch')
    # This build-specific table offset is explicitly recorded, not a generic EXEPACK parser.
    cursor = stub+0x132
    relocations = []
    for group in range(16):
        count = word(packed, cursor)
        cursor += 2
        for _ in range(count):
            offset = word(packed, cursor)
            cursor += 2
            address = group*65536+offset
            relocations.append(dict(image_offset=address, segment=group*0x1000,
                                    offset=offset, original_word=word(output, address)))
    require(cursor == len(packed), 'relocation table does not exactly end at EOF')
    require(len({r['image_offset'] for r in relocations}) == len(relocations), 'duplicate relocation words')
    require(output == reference, 'reproduced bytes differ from reference')
    require(len(output) == 171360, 'unexpected output size')
    require(digest(output) == 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297', 'unexpected output identity')
    result = dict(source=str(exe_path), source_sha256=digest(exe), source_bytes=len(exe),
                  reference=str(reference_path), image_sha256=digest(output), image_bytes=len(output),
                  mz_header_bytes=header_size, compressed_stub_image_offset=stub,
                  output_entry_cs=cs, output_entry_ip=ip, output_ss=ss, output_sp=sp,
                  signature=signature, reserved_parameter=reserved, packed_size_parameter=packed_size,
                  command_count=len(blocks), literal_prefix_bytes=destination+1,
                  trimmed_ff_bytes=trimmed, relocation_count=len(relocations),
                  relocation_table_offset_from_stub=0x132, roundtrip_exact=True,
                  reference_mismatches=0, pass320_ledger_verified=False,
                  semantic_promotions=0, runtime_tests=0)
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path/'reproduced_image.bin').write_bytes(output)
    (out_path/'unpack_proof.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    write_csv(out_path/'unpack_blocks.csv', blocks)
    write_csv(out_path/'relocations.csv', relocations)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
