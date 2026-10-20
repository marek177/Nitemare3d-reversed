#!/usr/bin/env python3
"""Lossless DOSBox-X N3D VGA page + DAC -> 320x400 source-cache check.

This checks one captured ORIGINAL framebuffer and RGB cache, NOT remake parity.
A000/A400 are page-select semantics of the observed original DOS v2.0 path.
"""
import argparse
import hashlib
import json
from pathlib import Path

W, H = 320, 200
VRAM_BYTES = 2_097_152


def decode(vram: bytes, page: int) -> bytes:
    if len(vram) != VRAM_BYTES or page not in (0, 1):
        raise ValueError('Expected 2MiB interleaved DOSBox-X VGA VRAM and page 0/1')
    start = 0x10000 * page
    # Each row is 80 aperture bytes interleaved over 4 VGA planes.
    return vram[start:start + W * H]


def to_rgb_cache(indexed: bytes, dac: bytes) -> bytes:
    if len(indexed) != W * H or len(dac) != 768 or max(dac) > 63:
        raise ValueError('Expected 64000 indexed pixels and 768 6-bit DAC bytes')
    rgb = bytes(((c << 2) | (c >> 4)) for c in dac)
    result = bytearray()
    for y in range(H):
        row = bytearray()
        for i in indexed[y * W:(y + 1) * W]:
            row.extend(rgb[3 * i:3 * i + 3])
        result.extend(row)
        result.extend(row)
    return bytes(result)


def compare(vram: bytes, dac: bytes, ppm: bytes, page: int) -> dict:
    indexed = decode(vram, page)
    actual = to_rgb_cache(indexed, dac)
    header = b'P6\n320 400\n255\n'
    if not ppm.startswith(header) or len(ppm) != len(header) + len(actual):
        raise ValueError('Expected a 320x400 P6 RGB24 cache PPM')
    source = ppm[len(header):]
    mismatched = sum(a != b for a, b in zip(actual, source))
    return {'proof_level': 'ORIGINAL_CACHE_CONSISTENCY_ONLY',
            'page': page,
            'indexed_sha256': hashlib.sha256(indexed).hexdigest(),
            'dac_sha256': hashlib.sha256(dac).hexdigest(),
            'rgb24_sha256': hashlib.sha256(source).hexdigest(),
            'compared_rgb_pixels': 320 * 400,
            'compared_rgb_components': len(source),
            'mismatched_rgb_components': mismatched,
            'matches': mismatched == 0,
            'warning': 'A zero diff here is not original-vs-remake renderer parity.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vram', type=Path, required=True)
    parser.add_argument('--dac', type=Path, required=True)
    parser.add_argument('--cache-ppm', type=Path, required=True)
    parser.add_argument('--page', type=int, required=True, choices=(0, 1))
    parser.add_argument('--json-out', type=Path)
    args = parser.parse_args()
    try:
        report = compare(args.vram.read_bytes(), args.dac.read_bytes(),
                         args.cache_ppm.read_bytes(), args.page)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['matches'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
