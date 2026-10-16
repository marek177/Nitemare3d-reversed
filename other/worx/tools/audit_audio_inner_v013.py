#!/usr/bin/env python3
"""WORX 2.1 embedded in Nitemare DOS 2.0: byte-pinned 0.13 audio RE.

Targets ORIGINAL expanded MZ image (178,528 bytes), not N3D-UNFU or other
WORX build. This audit proves executable bytes and explicitly witnessed
edges; it does NOT certify full transitive closure, IRQ/ISA timing or audio.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

# Do not derive expected signatures from the same candidate file in the audit:
EXPECTED_IMAGE_SHA256='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
EXPECTED_MZ_HEADER_BYTES=0x1C00
EXPECTED_IMAGE_SIZE=0x29D60
CS_IMAGE_BASE=0x15BF0
# Low CS=15BF segment, addressing original image bytes at +0x15BF0.
BODY_SPANS={
  'timer_midi_outer_4476':(0x4476,0x44B3,'aecabeb8b171c0d276e1d7e79559119337c292504ef124b21840f63ee2c940a7'),
  'midi_track_44b3_REMAINS_OPEN':(0x44B3,0x45DD,'9dcda1b828209b6608e23b1ca619f2a833c46bf7ef351c45168bc8dc6b4c8742'),
  'tempo_ff51_455d':(0x455D,0x458C,'66a97d8ea13617f5d1b1aeecbec13a803d969b6764af54f23a146a5c59ac8b10'),
  'vlq_45f9':(0x45F9,0x4630,'569c78b7d219c20f857c4edd780a2ac7a011ee80ea49058e1c4dc4c74838f51c'),
  'dma_49bc':(0x49BC,0x4A12,'9ef7734e568166359064c544b8734120b0a76487307067026c75764e00bce77e'),
  'pit_helper_466a':(0x466A,0x469F,'6b9d5028a52646356b8982a1b86cb3e47b9b48bda087495180989c558850cefd'),
  'pcm_555d_REMAINS_OPEN':(0x555D,0x5664,'6211c2ac65b829358c8dbe149cd2f554f885cb37718e6d9827e4bc0e19a541d1'),
  'pcm_sample_arithmetic_5625':(0x5625,0x563F,'2cd59a7ac6c3bceb30ba2b41e2a2dfd229fb9f3b7119daa377be87918f3ca459'),
  'music_gate_5df2':(0x5DF2,0x5E19,'1581cc2456e97b2464f178fa16ec3a09f83f5a4ed0d73ff84285579c1444dc34'),
  'stream_fill_prefix_5f17':(0x5F17,0x5F3E,'65eb4513aaee75e8cbba22d10088b8e0df7821cb7c8a0d7750e88943ee0a12a8'),
}
# Anchors specifically rule out accidental mistaken control flow / widths.
ANCHORS={
 'midi_enabled_guard_4478':(0x4478,'2e 80 3e 62 2d 00 75 01 c3'),
 'midi_counter_increment_4481':(0x4481,'2e ff 06 54 2c'),
 'midi_unsigned_threshold_448a':(0x448A,'2e 3b 06 5a 2c 72 0c'),
 'midi_count_to_cx_44a4':(0x44A4,'2e 8b 0e 58 2c'),
 'midi_call_44a9':(0x44A9,'e8 07 00'),
 'midi_loop_fallthrough_44b1':(0x44B1,'e2 f6 51'),
 'midi_vlq_initial_registers_45fb':(0x45FB,'33 c0 33 d2'),
 'midi_vlq_recur_460f':(0x460F,'d1 e0 d1 d2 d1 e0 d1 d2'),
 'midi_vlq_stop_460a':(0x460A,'80 ff 80 72 1e'),
 'midi_vlq_call_4528':(0x4528,'e8 ce 00'),
 'dma_reset_49bf':(0x49BF,'32 c0 e6 0c'),
 'dma_second_sample_49c3':(0x49C3,'e4 02 e4 02 fb 86 e0 32 c0 8b c8'),
 'dma_below_base_49ce':(0x49CE,'2e a1 df 2d 3b c8 73 03'),
 'dma_0400_threshold_49db':(0x49DB,'81 f9 00 04 73 03'),
 'dma_signed_1000_threshold_49e4':(0x49E4,'81 f9 00 10 7e 03'),
 'dma_signed_ring_49fc':(0x49FC,'3b ca 7d 0a'),
 'dma_final_length_4a0a':(0x4A0A,'2b ca 2e 89 0e db 48 c3'),
 'pcm_gate_555f':(0x555F,'e8 5a f4 83 f9 00 75 01 c3'),
 'pcm_length_save_5572':(0x5572,'2e 89 0e 8b 47'),
 'pcm_word_clear_5577':(0x5577,'d1 e9 b8 80 80 f3 ab'),
 'pcm_eight_slots_5658':(0x5658,'83 c3 02 83 fb 10 73 03'),
 'pcm_signed_multiply_add_5625':(0x5625,'8a 04 32 e4 d1 e8 1f 2d 40 00 2e 8b 97 bf 4b d1 e2 d1 e2 f7 ea 26 00 25'),
 'music_active_5df2':(0x5DF2,'2e 80 3e ea 2d 01 74 01 c3'),
 'music_mode_5dfd':(0x5DFD,'2e 80 3e e3 48 02 74 0b'),
 'music_second_mode_5e05':(0x5E05,'2e 80 3e e3 48 0c 74 03'),
 'music_dma_and_stream_5e10':(0x5E10,'e8 a9 eb e3 03 e8 ff 00 c3'),
 'stream_prefix_active_5f19':(0x5F19,'2e c6 06 ea 2d 01'),
 'stream_prefix_count_5f1f':(0x5F1F,'2e 8b 0e db 48 e3 18'),
 'stream_prefix_fill_5f30':(0x5F30,'b0 00 2e 80 3e e4 48 00 75 02 b0 80 f3 aa'),
 'tempo_skip_meta_length_455d':(0x455D,'47 53 52 26 8a 15 47 32 f6'),
 'tempo_divide_by_2c5a_456e':(0x456E,'2e 8b 1e 5a 2c f7 f3'),
 'tempo_high_product_4575':(0x4575,'bb 73 1e f7 e3 8b c2 bb 0a 00 f7 e3'),
 'tempo_pit_call_4581':(0x4581,'e8 e6 00 2e a3 49 2c'),
 'pit_466a_mode_gate':(0x466A,'2e 83 3e 1e 20 01 75 01 c3'),
 'pit_466a_div':(0x467D,'8b d8 33 d2 b8 ff ff f7 f3'),
 'pit_466a_out':(0x4690,'b0 34 e6 43 58 e6 40 8a c4 e6 40'),
}

TRANSITIVE_OPEN={
  '4476_to_44B3':'44B3..45DC includes output 3A4D, vlq 45F9, start music 4265, CMF 4389, PIT 466A',
  '555D_to_49BC':'DMA helper implemented at register/PortIO boundary; ISA timing remains external',
  '555D_to_5863':'XMS/EMS sample refill & far callback CS:[21C8] not closed',
  '555D_to_5502':'playlist activation & voice-routing nested into 56F0/5792/4C75 not closed',
  '5DF2_to_5F17':'file/resource audio streaming incl 312E, DOS/device-dependent paths not closed',
}

def audit(exe:Path)->dict:
    raw=exe.read_bytes()
    if len(raw)<EXPECTED_MZ_HEADER_BYTES or raw[:2]!=b'MZ' or struct.unpack_from('<H',raw,8)[0]*16!=EXPECTED_MZ_HEADER_BYTES:
        raise ValueError('Input must be the ORIGINAL unpacked v2.0 MZ image')
    image=raw[EXPECTED_MZ_HEADER_BYTES:]
    img_sha=hashlib.sha256(image).hexdigest()
    if len(image)!=EXPECTED_IMAGE_SIZE or img_sha!=EXPECTED_IMAGE_SHA256:
        raise ValueError('Original Nitemare DOS v2.0 image SHA or size mismatch')
    slices={}
    for name,(start,end,expectedhash) in BODY_SPANS.items():
        b=image[CS_IMAGE_BASE+start:CS_IMAGE_BASE+end]
        actual=hashlib.sha256(b).hexdigest()
        if actual!=expectedhash:
            raise ValueError(f'Machine-body drift at {name}: {actual}')
        slices[name]={'cs_start':f'{start:04X}','cs_end_exclusive':f'{end:04X}',
                     'bytes':len(b),'sha256':actual}
    anchors={}
    for name,(offset,hex_text) in ANCHORS.items():
        want=bytes.fromhex(hex_text)
        got=image[CS_IMAGE_BASE+offset:CS_IMAGE_BASE+offset+len(want)]
        if got!=want:raise ValueError(f'Opcode witness failed {name}: {got.hex(" ")}')
        anchors[name]={'cs_offset':f'{offset:04X}','machine_bytes':hex_text}
    return {'origin':'unpacked N3D DOS v2.0 embedded WORX 2.1',
            'image_sha256':EXPECTED_IMAGE_SHA256,
            'machine_slices':slices,'machine_anchors':anchors,
            'closure':{
                '49BC':'transitive-independent register, state, ports on injected I/O; CPU IF/timing open',
                '45F9':'machine-body algorithm modeled except real-mode memory mapping & infinite input',
                '4476':'outer loop and call sequence only; 44B3 handler still open',
                '5DF2':'branch and direct call order only; 5F17 streaming still open',
                '555D':'pre-clear prefix and per-sample primitive only; mixer loop and callees open',
                '5F17':'buffer-fill prefix only; stream file/payload processing open',
                '455D':'FF51 tempo arithmetic / direct PIT subroutine modeled; enclosing 44B3 remains open'},
            'transitive_open':TRANSITIVE_OPEN,
            'api_handler_count_unchanged':41}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('exe',type=Path)
    p.add_argument('--json',type=Path)
    args=p.parse_args()
    r=audit(args.exe)
    if args.json:
        args.json.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'origin':r['origin'],'image_sha256':r['image_sha256'],
                     'slices':len(r['machine_slices']),'anchors':len(r['machine_anchors']),
                     'api_handler_count_unchanged':41,'transitive_open':r['transitive_open']},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
