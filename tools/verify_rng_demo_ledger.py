"""Read-only original RNG/DEMO ledger verification using raw reads and inverse LCG."""
from pathlib import Path
import argparse,base64,hashlib,json,struct
SOURCE='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3'
DEMO='25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840'
def check(condition,message):
    if not condition:raise ValueError(message)
def decoded(response):
    r=response['result'];b=base64.b64decode(r['data_base64'],validate=True)
    check(len(b)==r['byte_count'],'Read length mismatch')
    check(hashlib.sha256(b).hexdigest()==r['sha256'],'Read SHA mismatch')
    return b
def snapshot(s,rpc_map=None,register_results=None):
    r=s['registers'];reads=s['reads'];values={k:decoded(v) for k,v in reads.items()}
    if rpc_map is not None:
        for v in reads.values():check(v['id'] in rpc_map and rpc_map[v['id']]['response']==v,'Missing/mismatched original RPC response')
        check(json.dumps(r,sort_keys=True) in register_results,'Missing original CPU register result')
    for v in reads.values():check(v['result']['state_revision']==r['state_revision'],'Mixed snapshot revisions')
    check(s['state']==struct.unpack('<I',values['state'])[0],'Derived state mismatch')
    check(s['RTC']==struct.unpack('<I',values['RTC'])[0],'Derived RTC mismatch')
    check(s['counter']==struct.unpack_from('<I',values['world'])[0],'Derived counter mismatch')
    check(tuple(s['pending_record'])==struct.unpack('<HHI',values['input']),'Derived pending record mismatch')
    check(s['flags']==struct.unpack('<H',values['flags'])[0],'Derived input flags mismatch')
    check(tuple(s['mode'])==struct.unpack('<HH',values['mode']),'Derived mode mismatch')
    return values
def verify(events,demo,binary,require_eof=False,rpc_map=None):
    check(hashlib.sha256(binary).hexdigest()==SOURCE,'Original executable identity mismatch')
    check(hashlib.sha256(demo).hexdigest()==DEMO,'DEMO identity mismatch')
    check(events and [e['event_index'] for e in events]==list(range(len(events))),'Noncontiguous event sequence')
    register_results=None
    if rpc_map is not None:
        register_results={json.dumps(x['response']['result'],sort_keys=True) for x in rpc_map.values() if x['request']['method']=='state.get_registers' and 'result' in x['response']}
    baseline=events[0];check(baseline['kind']=='baseline','Missing baseline');values=snapshot(baseline['snapshot'],rpc_map,register_results);state=baseline['snapshot']['state'];check(state==1,'Baseline seed is not1')
    records=list(struct.iter_unpack('<HHI',demo[6:]));check(tuple(baseline['snapshot']['pending_record'])==records[0],'Initial prefetch mismatch');check(struct.unpack_from('<3H',values['world'],28)==struct.unpack('<3H',demo[:6]),'Timing header mismatch')
    inverse=pow(214013,-1,1<<32);pending=[];rng=seed=reads=eof=0;h=struct.unpack_from('<H',binary,8)[0]*16
    for e in events[1:]:
        kind=e['kind'];s=e.get('snapshot')
        if s is not None:snapshot(s,rpc_map,register_results)
        if kind in ('rng_entry','seed_entry'):
            check(s['state']==state,'Unexplained entry-state change');b=decoded(e['stack']);ip,cs=struct.unpack_from('<HH',b);frame=e['frame'];check(frame['return_cs']==cs and frame['return_ip']==ip,'Return frame metadata mismatch');check(frame['SP']==(int(s['registers']['general']['esp'],16)&65535),'Entry SP metadata mismatch')
            if e['wrapper_outer_caller']:
                core_base=int(s['registers']['segments']['cs'],16)-0x11ee;oi,os=struct.unpack_from('<HH',b,4);check(e['wrapper_outer_caller']==f'{os-core_base:04X}:{oi:04X}','Outer caller metadata mismatch');at=h+(os-core_base)*16+oi-5;check(binary[at:at+5]==bytes.fromhex('9aa001ba0f'),'Encoded wrapper call target mismatch')
            pending.append(e)
        elif kind in ('rng_return','seed_return'):
            check(bool(pending),'Return without entry');entry=pending.pop();check(entry['call_id']==e['call_id'] and e['validated'],'Mismatched or invalid return');frame=entry['frame'];regs=s['registers'];check(int(regs['segments']['cs'],16)==frame['return_cs'] and int(regs['instruction_pointer'],16)==frame['return_ip'],'CPU did not reach saved return')
            check((int(regs['general']['esp'],16)&65535)==((frame['SP']+4)&65535),'Return SP mismatch')
            actual=s['state'];ax=int(regs['general']['eax'],16)&65535;check(ax==e['returned_AX'],'Returned AX metadata mismatch')
            if kind=='rng_return':
                check(((actual-2531011)*inverse)&0xffffffff==entry['snapshot']['state'],'Inverse LCG transition mismatch');check(ax==(actual>>16)&32767,'RNG output mismatch');rng+=1
            else:check(actual==struct.unpack_from('<H',decoded(entry['stack']),4)[0],'Seed parameter mismatch');seed+=1
            state=actual
        elif kind=='DEMO_post_read':
            check(not pending and s['state']==state,'Input-read state-chain mismatch');check(reads<len(records),'Extra application beyond supplied record count');expected=records[reads];check(e['applied_record_index']==reads and tuple(e['applied_file_record'])==expected,'Input record index/data mismatch')
            check(e['actual_key_SI']==(int(s['registers']['general']['esi'],16)&65535)==expected[0] and s['flags']==expected[1],'Applied key/flags mismatch');check(s['counter']>=expected[2],'Input applied before its counter')
            count=int(s['registers']['general']['eax'],16)&65535;check(count==e['read_return_AX'] and e['validated'],'Read return metadata mismatch')
            if count==8:check(reads+1<len(records) and tuple(s['pending_record'])==records[reads+1],'Prefetch order mismatch')
            elif count==0:check(reads==len(records)-1,'Premature EOF');eof+=1
            else:raise ValueError('Unexpected read result')
            reads+=1
        elif kind=='DEMO_close_entry':pass
        else:raise ValueError('Unvalidated event kind: '+kind)
    complete=eof==1 and reads==len(records) and not pending
    check(not require_eof or complete,'First EOF not proved')
    return {'events':len(events),'RNG_returns':rng,'seed_returns':seed,'input_records':reads,'pending_calls':len(pending),'first_EOF_verified':complete,'final_completed_state':state,'raw_RPC_correlation_checked':rpc_map is not None,'scope':'RNG core returns and DEMO post-read events; RTC context only, not every IRQ instruction or global alias closure'}
def load_rpc(folder):
    rows={}
    for p in Path(folder).glob('rpc_*.json'):
        v=json.loads(p.read_text());rows[v['response']['id']]=v
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ledger');p.add_argument('DEMO1');p.add_argument('unpacked_exe');p.add_argument('--require-eof',action='store_true');a=p.parse_args()
    try:
        path=Path(a.ledger);events=[json.loads(x) for x in path.read_text().splitlines()];print(json.dumps(verify(events,Path(a.DEMO1).read_bytes(),Path(a.unpacked_exe).read_bytes(),a.require_eof,load_rpc(path.parent)),indent=2))
    except (ValueError,OSError,KeyError,IndexError) as e:p.exit(2,str(e)+'\n')
