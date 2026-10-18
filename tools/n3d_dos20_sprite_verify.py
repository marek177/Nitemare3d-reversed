#!/usr/bin/env python3
"""Verify the exact DOS image used by the sprite contract. No game execution."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

IMAGE_SHA256 = '552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301'
BODY_SHA256 = '9c6317d465f0e2c2c4c3a9919738c2d05e7da778b8f992f363ebefb210166937'
# Image-relative instruction anchors (MZ header is excluded).
ANCHORS = {
    0x1B84: '2b4f0ef7d941',       # bottom-top+1
    0x1B9A: '66f7f1',             # unsigned DIV ECX
    0x1BC0: '39470e7e06',         # signed bottom clipping
    0x1BCE: '39470c7d34',         # signed top clipping
    0x1C8C: '268a47052410',       # actor flags, bit 10
    0x1CA1: 'bb5000f6e3',         # MUL BL, row pitch 80
    0x1CC0: 'b011d2c0',           # repeated VGA mask
    0x1CDA: '3b46ea7722',         # unsigned JA, equal is visible
    0x1CEE: '8a043c1f7403268805', # transparent sample skip
    0x1CF7: '83c75003da13f5',     # pitch / ADD / ADC
}

def verify(data):
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA256:
        raise ValueError('Unsupported image SHA-256; no contract verified')
    if data[:2] != b'MZ':
        raise ValueError('Not an MZ image')
    header_bytes = struct.unpack_from('<H', data, 8)[0] * 16
    image = data[header_bytes:]
    if hashlib.sha256(image[0x1B3E:0x1D3D]).hexdigest() != BODY_SHA256:
        raise ValueError('Sprite function bytes differ')
    for offset, expected in ANCHORS.items():
        raw = bytes.fromhex(expected)
        if image[offset:offset+len(raw)] != raw:
            raise ValueError(f'Instruction mismatch at {offset:04X}')
    return {'image_sha256': IMAGE_SHA256, 'mz_header_bytes': header_bytes,
            'function': '1000:1B3E..1D3C', 'body_sha256': BODY_SHA256,
            'verified_anchors': len(ANCHORS), 'pixel_parity': 'unproven'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.exe.read_bytes()), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
