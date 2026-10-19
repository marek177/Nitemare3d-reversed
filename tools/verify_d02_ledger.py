#!/usr/bin/env python3
"""Validate the exported DOS2 shared-wrapper ledger, not the raw CPU trace.

Raw trace verification additionally requires the source capture and its parser.
This tool proves JSON consistency, LCG arithmetic and unchanged prefix ordering.
"""
import json
import sys
from pathlib import Path


def verify(data):
    if data.get('schema') != 'n3d-d02-original-runtime-first-chain-v1':
        raise ValueError('unsupported ledger schema')
    runs = data['runs']
    if len(runs) < 2 or data['independent_runs'] != len(runs):
        raise ValueError('need at least two recorded sessions')
    sites = {0x2478,0x525E,0x5582,0x5666,0x56A6,0x573F,0x58A7,0x85AD,
             0x8860,0x886C,0x887C,0x9A68,0x9A77,0x9C98,0x9CC2,0x9D6E,
             0x9F0C,0x9F36,0x9FE3,0xA047,0xA12B,0xB276}
    sequences = []
    for run in runs:
        state, event, sequence = 1, -1, []
        if not run['rng'] or run['recorded_rng'] != len(run['rng']):
            raise ValueError('invalid recorded count')
        for n, draw in enumerate(run['rng'], 1):
            next_state = (state * 214013 + 2531011) & 0xffffffff
            result = (next_state >> 16) & 0x7fff
            site = int(draw['callsite'], 16)
            if (draw['n'] != n or int(draw['state_before'], 16) != state or
                int(draw['state_after'], 16) != next_state or
                draw['result'] != result or site not in sites or
                draw['call_event'] <= event):
                raise ValueError(f'inconsistent draw {n}')
            sequence.append((site, next_state, result))
            state, event = next_state, draw['call_event']
        sequences.append(sequence)
    common = min(map(len, sequences))
    if (data['common_prefix_length'] != common or
        data['common_prefix_reproduced'] is not True or
        any(s[:common] != sequences[0][:common] for s in sequences[1:])):
        raise ValueError('shared prefix mismatch')
    return {'ledger_consistent': True, 'replicated_prefix': common,
            'run_lengths': list(map(len, sequences)), 'raw_trace_reverified': False,
            'full_demo_or_port_parity': False}


if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[1] / 'docs/evidence/2026-10-19/'
        'N3D_REMAX_D02_RUNTIME_CHAIN_20261019.json')
    try:
        print(json.dumps(verify(json.loads(path.read_text())), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        sys.exit(f'FAIL: {exc}')
