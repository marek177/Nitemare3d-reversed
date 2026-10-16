#!/usr/bin/env python3
"""WORX 2.1 v0.12 original-machine static evidence for INT08 and edge cases.

Pinned to the *unpacked* N3D DOS 2.0 image; no live DOS/ISA evidence and
NO claim that 4476/40E7 or the old BIOS interrupt body has been rebuilt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_dispatch_binary import EXPECTED_IMAGE_SHA256, EXPECTED_HEADER_BYTES, SEG_IMAGE_BASE

ANCHORS = {
    'original_reentrancy_counter': (0x3ED4, 'ff ff'),
    'audio_stack_save': (0x40E7, 'fa 2e 89 26 dd 3e 2e 8c 16 df 3e'),
    'audio_private_stack_load': (0x40F2, '2e 8b 26 e1 3e 2e 8e 16 e3 3e fb'),
    'audio_tick_quantum': (0x4108, '2e a1 49 2c'),
    'audio_low_sub': (0x410C, '2e 29 06 4b 2c'),
    'audio_high_borrow': (0x4111, '2e 83 1e 4d 2c 00'),
    'audio_negative_compare': (0x4117, '2e 83 3e 4d 2c 00 7d 06'),
    'audio_negative_latch': (0x411F, '2e c6 06 53 2c 01'),
    'audio_pcm_gate': (0x4125, '2e f6 06 bc 2d 20 74 03'),
    'audio_pcm_call': (0x412D, 'e8 2d 14'),
    'audio_midi_gate': (0x4130, '2e 80 3e d6 3e 00 74 03'),
    'audio_midi_call': (0x4138, 'e8 b7 1c'),
    'audio_restore_stack': (0x4144, 'fa 2e 8b 26 dd 3e 2e 8e 16 df 3e c3'),
    'init_stack_below_40e5': (0x2EBC, 'b8 e5 40 2d 04 00 2e a3 e1 3e'),
    'init_pit_0952': (0x2F03, 'b8 52 09 e8 61 17'),
    'init_tick_0952': (0x2F09, '2e c7 06 49 2c 52 09'),
    'timer_irq_entry_and_music_mask': (0x4150, 'fc fa 2e f6 06 bc 2d 16'),
    'timer_music_call': (0x4163, 'e8 10 03'),
    'timer_tick_increment': (0x416F, '2e ff 06 b4 2d'),
    'timer_unsigned_period_branch': (0x4179, '2e 3b 06 b6 2d 58 72 0e'),
    'timer_reset_on_old_irq': (0x4181, '2e c7 06 b4 2d 00 00'),
    'timer_old_irq_chain': (0x4188, '9c 2e ff 1e 0a 00 cf'),
    'timer_reentrancy_increment': (0x418F, '2e ff 06 d4 3e'),
    'timer_pic_eoi': (0x4195, 'b0 20 e6 20'),
    'timer_gate_zero': (0x419A, '2e 83 3e d4 3e 00'),
    'timer_skipped_count': (0x41A2, '2e ff 06 e5 40'),
    'timer_audio_service': (0x41AA, 'e8 3a ff'),
    'timer_reentrancy_decrement': (0x41AD, '2e ff 0e d4 3e'),
    'timer_iret': (0x41B2, 'cf'),
    'midi_scheduler_end_of_loop': (0x44B1, 'e2 f6'),
    'midi_scheduler_fallthrough_helper': (0x44B3, '51 2e 8b 1e c0 2d'),
    'mixer_word_clear_drop_odd': (0x5577, 'd1 e9 b8 80 80 f3 ab'),
    'dsp_frequency_div_u16': (0x5C70, 'ba 0f 00 b8 40 42 f7 f3'),
    'AH52_points_to_counter_writer': (0x2358, '2e ff 06 c4 20'),
}


def audit(path: Path) -> dict:
    b=path.read_bytes()
    if b[:2]!=b'MZ' or (struct.unpack_from('<H',b,8)[0]*16)!=EXPECTED_HEADER_BYTES:
        raise ValueError('wrong MZ header')
    image=b[EXPECTED_HEADER_BYTES:]
    if hashlib.sha256(image).hexdigest()!=EXPECTED_IMAGE_SHA256:
        raise ValueError('wrong ORIGINAL N3D DOS 2.0 image identity')
    evidence={}
    for k,(offset,hexbytes) in ANCHORS.items():
        expected=bytes.fromhex(hexbytes)
        actual=image[SEG_IMAGE_BASE+offset: SEG_IMAGE_BASE+offset+len(expected)]
        if actual!=expected:
            raise ValueError(f'{k} changed at CS:{offset:04X}: {actual.hex(" ")}')
        evidence[k]={"cs_offset":f"{offset:04X}","original_machine_bytes":hexbytes}
    gate=image[SEG_IMAGE_BASE+0x4150:SEG_IMAGE_BASE+0x41B3]
    gate_sha=hashlib.sha256(gate).hexdigest()
    audio_sha=hashlib.sha256(image[SEG_IMAGE_BASE+0x40E7:SEG_IMAGE_BASE+0x4150]).hexdigest()
    # AH=52h index is immediately past 00h..51h, points to mutable CS:20C4.
    # The 20C4 counter is initially zero, and its writer is also witnessed.
    beyond=0x2020+0x52*2
    if beyond!=0x20C4 or struct.unpack_from('<H',image,SEG_IMAGE_BASE+beyond)[0]!=0:
        raise ValueError('AH52 alias assumption fails')
    if image[SEG_IMAGE_BASE+0x40E7]!=0xFA:
        raise ValueError('40E7 private-stack audio service entry changed')
    return {
        'scope':'N3D DOS v2.0 embedded WORX Toolkit 2.1',
        'image_sha256':EXPECTED_IMAGE_SHA256,
        'int08_gate_cs_span':'4150..41B2 inclusive',
        'int08_gate_body_sha256':gate_sha,
        'int08_private_stack_audio_span':'40E7..414F inclusive',
        'int08_private_stack_audio_body_sha256':audio_sha,
        'int08_audio_tick_quantum_word':'CS:2C49',
        'int08_audio_expired_latch_byte':'CS:2C53 after SIGNED high-word test',
        'int08_audio_callbacks_in_order':['CS:555D if (CS:[2DBC] & 20h)',
                                          'CS:5DF2 if CS:[3ED6] != 0'],
        'initial_reentrancy_counter_3ED4':65535,
        'pit_init_divisor':0x0952,
        'pit_divided_counter':0xFFFF//0x0952,
        'AH52_slot_alias':'CS:20C4 mutable counter, NOT stable handler table entry',
        'AH2F_loop_edge':'44B1 LOOP 44A9 falls through to 44B3 helper body at terminal CX=0',
        'AH4E_odd_length_clear':'5577 SHR CX,1; 557C REP STOSW, no odd byte handled by this instruction pair',
        'AH3F_overflow':'BX 1..15: (000F:4240h)/BX exceeds 16-bit quotient; x86 DIV fault',
        'machine_anchors':evidence,
        'limits':['Only branch and direct byte witnesses; indirect calls and aliases beyond listed not closed',
                  'No original runtime IRQ ordering or bit-exact PCM produced',
                  'Old IRQ08 vector and 4476 parser remain callbacks; 40E7 shell excludes CPU SS/SP, IF, nesting and full 555D/5DF2 bodies']
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('exe',type=Path)
    p.add_argument('--json',type=Path)
    args=p.parse_args()
    result=audit(args.exe)
    if args.json:args.json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='machine_anchors'},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
