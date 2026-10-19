#!/usr/bin/env python3
"""Read-only D02 shared RNG evidence verifier from original N3DTRC01 sparse traces."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/mnt/data')
from n3d_d01_runtime_verify import iter_records, decode_cpu
SITES={0x2478,0x525E,0x5582,0x5666,0x56A6,0x573F,0x58A7,0x85AD,0x8860,0x886C,0x887C,0x9A68,0x9A77,0x9C98,0x9CC2,0x9D6E,0x9F0C,0x9F36,0x9FE3,0xA047,0xA12B,0xB276}

def analyze(session):
    calls=[]; entries=[]; written={}; returns=[]; seed=0; checkpoint=[]
    for kind,event,seq,pay in iter_records(session):
        if kind!=b'I':continue
        c=decode_cpu(pay); pos=c['image']
        if pos==0xF9AC:seed+=1
        if pos in (0xF9B1,0x6DDA,0x6DE4,0x6DF6,0x9806):checkpoint.append({'event':event,'offset':f'0x{pos:X}'})
        if pos in SITES and c['code'].startswith(bytes.fromhex('9aa001')):calls.append({'event':event,'offset':f'0x{pos:04X}'})
        if pos==0xFD40:entries.append(event)
        if pos==0x150F3:
            written[event]=c['regs']['eax']&0xffff | ((c['regs']['edx']&0xffff)<<16)
        if pos==0x150FC:returns.append({'event':event,'value':c['regs']['eax']&0xffff})
    assert seed==1,seed
    assert len(calls)==len(entries)==len(returns)==len(written),(len(calls),len(entries),len(returns),len(written))
    state=1; out=[]
    for i,(call,entry,(store_evt,store),ret) in enumerate(zip(calls,entries,written.items(),returns),1):
        expected=(state*214013+2531011)&0xffffffff
        expected_result=(expected>>16)&0x7fff
        assert call['event']<entry<store_evt<ret['event'],f'order mismatch at {i}'
        assert store==expected,(i,hex(store),hex(expected))
        assert (ret['value'] & 0x7fff)==expected_result,(i,ret['value'],expected_result)
        out.append({'n':i,'callsite':call['offset'],'state_before':f'0x{state:08X}','state_after':f'0x{store:08X}','result':expected_result,'call_event':call['event']})
        state=store
    summary={}
    for line in (Path(session)/'summary.txt').read_text().splitlines():
        if '=' in line:k,v=line.split('=',1);summary[k]=v
    assert summary['reason']=='D02_RNG_TARGET_REACHED'
    assert int(summary['d02_rng_entries'])==len(out)
    return {'session':str(session),'recorded_rng':len(out),'cpu_callbacks':int(summary['d01_cpu_callbacks']),'saved_instructions':int(summary['instructions']),'rng':out,'checkpoints':checkpoint}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('sessions',nargs='+',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    runs=[analyze(s) for s in args.sessions]
    n=min(x['recorded_rng'] for x in runs)
    a=[(x['callsite'],x['state_after'],x['result']) for x in runs[0]['rng'][:n]]
    assert all(a==[(x['callsite'],x['state_after'],x['result']) for x in run['rng'][:n]] for run in runs[1:])
    report={'schema':'n3d-d02-original-runtime-first-chain-v1','independent_runs':len(runs),'common_prefix_length':n,'common_prefix_reproduced':True,'runs':runs,'note':'Original DOS2 shared-wrapper events; this is not exhaustive indirect/CRT-rand census or original-vs-cleanroom parity. Dense tails can overlap and target count may overshoot.'}
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'runs':[(x['recorded_rng'],x['cpu_callbacks']) for x in runs], 'prefix':n,'chain':runs[-1]['rng']},indent=2))
if __name__=='__main__':main()
