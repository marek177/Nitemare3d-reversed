#!/usr/bin/env python3
"""Nitemare 3D DOS2 D02-E: bounded static/data audit of 3000-vs-7000 timing drift.

Inputs: user-owned original N3D-UNFU.exe (MZ with 512-byte header), and
D02-D *derived* evidence JSON (not original raw CPU trace). The script never
modifies the inputs and never claims to have captured fresh runtime evidence.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

EXPECTED_EXE_SHA = '552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301'
EXPECTED_ORIGINAL_PACKED_SHA = 'a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485'
EXPECTED_DEMO_SHA = '25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840'

# Exact offsets refer to the image after the 512-byte DOS MZ header.
# Ordered key witnesses are fixed data: they do NOT imply exhaustiveness of
# all indirect calls, all alias writers or all runtime code branches.
WITNESSES = {
    0x5F74: bytes.fromhex('C8 02 00 00 57 56'),   # damage-handler entry
    0x5F88: bytes.fromhex('9A C0 01 3D 08'),      # CALL FAR 083D:01C0 = image 8590
    0x5F95: bytes.fromhex('8E 46 08 26 8A 44 10'), # read actor HP at +0x10
    0x5F9C: bytes.fromhex('3B 46 FE'),            # compare HP against damage
    0x5F9F: bytes.fromhex('0F 8F A5 00'),         # signed HP>damage jump 6048
    0x5FA3: bytes.fromhex('26 88 64 10'),         # zero actor HP (AH=0)
    0x5FAD: bytes.fromhex('9A E4 1B 3D 08'),      # CALL FAR 083D:1BE4 = image 9FB4
    0x6A2F: bytes.fromhex('9A 04 13 C7 04'),      # hit-scan caller of image 5F74
    0x8125: bytes.fromhex('9A 04 13 C7 04'),      # projectile caller of image 5F74
    0x8590: bytes.fromhex('C8 04 00 00 57 56'),   # damage producer entry
    0x85AD: bytes.fromhex('9A A0 01 BA 0F'),      # shared RNG
    0x85B2: bytes.fromhex('B9 19 00 99 F7 F9'),   # 25; CWD; IDIV CX
    0x9FB4: bytes.fromhex('55 8B EC 57 56'),      # resource selector entry
    0x9FE3: bytes.fromhex('9A A0 01 BA 0F'),      # shared RNG
    0x9FE8: bytes.fromhex('B9 07 00 99 F7 F9'),   # 7; CWD; IDIV CX
    0xA00C: bytes.fromhex('38 6F 4B'),            # selected table byte comparison
    0xA00F: bytes.fromhex('74 D2'),               # retry to 9FE3
    0xBEB4: bytes.fromhex('C8 04 00 00 66 8B 46 06'),
    0xBEF4: bytes.fromhex('C8 04 00 00 66 0F BF 06 C2 3C'),
    0xC1A8: bytes.fromhex('C8 08 00 00 0E E8 C4 FC'),
}


def load_image(exe: Path) -> bytes:
    raw = exe.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_EXE_SHA:
        raise ValueError(f'wrong original DOS v2.0 EXE SHA256: {actual}')
    if raw[:2] != b'MZ':
        raise ValueError('not a DOS MZ executable')
    hdr = int.from_bytes(raw[8:10], 'little') * 16
    if hdr != 512:
        raise ValueError(f'unexpected MZ header: {hdr}')
    image = raw[hdr:]
    for addr, window in WITNESSES.items():
        actual_bytes = image[addr:addr + len(window)]
        if actual_bytes != window:
            raise AssertionError(f'original static witness at 0x{addr:04X} mismatched: {actual_bytes.hex()}')
    return image


def far_call_targets(img: bytes, dest: int) -> list[int]:
    """Literal 9A opcode-pattern matches to this linear MZ image target.

    Segments/offsets are original, before relocation. This is NOT an exhaustive
    decoded instruction inventory, and cannot rule out dynamic indirect CALLs.
    """
    result = []
    for idx in range(len(img) - 4):
        if img[idx] == 0x9A:
            off = int.from_bytes(img[idx + 1:idx + 3], 'little')
            seg = int.from_bytes(img[idx + 3:idx + 5], 'little')
            if seg * 16 + off == dest:
                result.append(idx)
    return result


def row_context_diffs(old: list[dict], new: list[dict], key: str) -> list[int]:
    return [i for i, (o, n) in enumerate(zip(old, new), 1) if o[key] != n[key]]


def group_extra_calls(rows: list[dict]) -> list[dict]:
    """Group 85AD + immediately following 9FE3 RNG cycles, NOT call-stack proof."""
    result = []
    i = 0
    while i < len(rows):
        if rows[i]['callsite'] != '0x85AD':
            raise AssertionError(f'expected damage RNG at extra call #{rows[i]["ordinal"]}')
        start = int(rows[i]['ordinal'])
        visit = int(rows[i]['scheduler_entries_before'])
        demo = int(rows[i]['last_demo_record_ordinal'])
        i += 1
        draws = []
        while i < len(rows) and rows[i]['callsite'] == '0x9FE3':
            draws.append(int(rows[i]['ordinal']))
            if int(rows[i]['scheduler_entries_before']) != visit:
                raise AssertionError('observed packet crosses scheduler-entry count')
            if int(rows[i]['last_demo_record_ordinal']) != demo:
                raise AssertionError('observed packet crosses DEMO record')
            i += 1
        if not draws:
            raise AssertionError('missing expected RNG resource selection')
        result.append({'first_rng_ordinal':start,
                       'last_rng_ordinal':draws[-1],
                       'damage_rng_callsite':'0x85AD',
                       'resource_rng_callsite':'0x9FE3',
                       'resource_rng_draws':len(draws),
                       'resource_rng_retries_inferred_from_consecutive_trace':len(draws)-1,
                       'total_rng_draws':1+len(draws),
                       'scheduler_entries_before':visit,
                       'last_demo_record_ordinal':demo})
    return result


def audit(img: bytes, evidence: dict) -> dict:
    if evidence.get('source_original_exe_sha256') != EXPECTED_ORIGINAL_PACKED_SHA:
        raise ValueError('D02-D evidence references another original packed executable')
    if evidence.get('source_demo_sha256') != EXPECTED_DEMO_SHA:
        raise ValueError('D02-D evidence references another DEMO.1 asset')
    runs = evidence['runs']
    if len(runs) != 7:
        raise ValueError('unexpected D02-D run matrix')
    old = runs[6]['rng_rows'] # documented fixed-3000 sample, 229 draws
    new = runs[5]['rng_rows'] # documented fixed-7000 sample, 220 draws
    if (len(old), len(new)) != (229, 220):
        raise AssertionError('unexpected 229/220 original evidence')
    for run_idx in (5,6):
        run = runs[run_idx]
        if run['complete_original_rng_outcomes'] != run['rng_entries']:
            raise AssertionError('a missing original RNG return/store would invalidate closure')
        if run['scheduler_max_depth'] != 1 or run['scheduler_unmatched_returns'] != 0:
            raise AssertionError('unexpected scheduler evidence')
    for ordinal, (o, n) in enumerate(zip(old,new), 1):
        for k in ('callsite','state_before','state_after_lcg','return_lcg'):
            if o[k] != n[k]:
                raise AssertionError(f'RNG stream differs at #{ordinal}, field={k}')
        if not o['original_instruction_complete'] or not n['original_instruction_complete']:
            raise AssertionError('RNG transition not original-instruction complete')
    schedule_differences = row_context_diffs(old,new,'scheduler_entries_before')
    demo_differences = row_context_diffs(old,new,'last_demo_record_ordinal')
    if schedule_differences[0] != 211 or demo_differences[0] != 219:
        raise AssertionError('first context divergence unexpected')
    extra = old[len(new):]
    grouped = group_extra_calls(extra)
    if [g['total_rng_draws'] for g in grouped] != [5,4]:
        raise AssertionError('extra nine RNG calls do not match expected two grouped cycles')
    links = {
        '5F74_handler_callers': far_call_targets(img,0x5f74),
        '8590_damage_producer_callers': far_call_targets(img,0x8590),
        '9FB4_resource_selector_callers': far_call_targets(img,0x9fb4),
    }
    if links != {
        '5F74_handler_callers':[0x6a2f,0x8125],
        '8590_damage_producer_callers':[0x5f88],
        '9FB4_resource_selector_callers':[0x5fad],
    }:
        raise AssertionError(f'direct far-call graph unexpectedly changed: {links}')
    return {
        'schema':'n3d-d02e-bounded-static-timing-audit-v1',
        'build': 'DOS 2.0 N3D-UNFU',
        'original_exe_sha256':EXPECTED_EXE_SHA,
        'raw_original_runtime_recaptured_in_this_audit':False,
        'source':'D02-D derived original-runtime evidence + fresh original EXE opcode audit',
        'reference_fixed_cycles_3000':{'rng_draws':len(old),'demo_records':runs[6]['original_demo_unique_applied_records']},
        'candidate_fixed_cycles_7000':{'rng_draws':len(new),'demo_records':runs[5]['original_demo_unique_applied_records']},
        'common_exact_rng_prefix':len(new),
        'first_scheduler_visit_context_divergence':{
            'rng_ordinal':schedule_differences[0],
            'callsite':old[schedule_differences[0]-1]['callsite'],
            'reference_scheduler_entries':old[schedule_differences[0]-1]['scheduler_entries_before'],
            'candidate_scheduler_entries':new[schedule_differences[0]-1]['scheduler_entries_before'],
            'same_demo_record':old[schedule_differences[0]-1]['last_demo_record_ordinal'],
        },
        'first_demo_record_context_divergence':{
            'rng_ordinal':demo_differences[0],
            'reference_demo_record':old[demo_differences[0]-1]['last_demo_record_ordinal'],
            'candidate_demo_record':new[demo_differences[0]-1]['last_demo_record_ordinal'],
        },
        'remaining_reference_only_rng_groups':grouped,
        'remaining_reference_only_callsites':dict(collections.Counter(r['callsite'] for r in extra)),
        'verified_original_opcode_windows': len(WITNESSES),
        'literal_direct_far_call_graph':{k:[f'0x{a:04X}' for a in v] for k,v in links.items()},
        'local_lethal_damage_branch':{
            'damage_producer_call':'0x5F88 -> 0x8590 (RNG at 0x85AD)',
            'hitpoints_read':'0x5F98 ES:[SI+0x10]',
            'compare':'0x5F9C HP versus computed damage',
            'nonlethal_exit':'0x5F9F JG 0x6048',
            'lethal_path':'0x5FA3 HP=0 -> 0x5FAD selector 0x9FB4 (RNG at 0x9FE3)',
            'direct_callers_of_handler':['0x6A2F hitscan','0x8125 projectile'],
        },
        'claim_boundary':(
            'The reference-only nine RNG draws form two damage/selector patterns '
            'consistent with two executions of the local lethal-hit path. '
            'The exact runtime caller/actor and the specific BEB4/BEF4/C1A8 clock '
            'branch responsible for the A/B timing difference are NOT proven; '
            'absence before EOF does not establish a game logic omission.'
        ),
        'closure':{'D02E_static_causal_path':'VERIFIED ORIGINAL STATIC',
                   'D02E_A_B_first_context_divergence':'VERIFIED DERIVED RUNTIME EVIDENCE',
                   'D02E_exact_clock_gate':'OPEN',
                   'D02E_original_vs_clean_room':'OPEN'},
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe',required=True,type=Path)
    p.add_argument('--evidence',required=True,type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=audit(load_image(args.exe), json.loads(args.evidence.read_text()))
    txt=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(txt,encoding='utf-8')
    else:print(txt,end='')

if __name__=='__main__': main()
