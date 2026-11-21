from pathlib import Path
import json
D=Path('outputs/evidence/runtime/bsf_file_r_20261107');v=json.loads((D/'checksum_return_control.json').read_text());print('pc',v['after']['result']['instruction_pointer']);e=v['trace']['result']['events'];print('events',len(e));print([(x['address']['offset'],x['instruction']) for x in e[:5]]);print([(x['address']['offset'],x['instruction']) for x in e[-3:]])
raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
for x in [v['before'],v['after'],v['trace']]:assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==3136
assert int(v['after']['result']['instruction_pointer'],16)==0x2a5d and any(x['instruction']=='retf' and int(x['address']['offset'],16)==0x29c8 for x in e)
a=int(v['before']['result']['general']['ebp'],16)&65535;b=int(v['after']['result']['general']['esp'],16)&65535;assert b==a+6
O=Path('outputs/bsf_file_r_20261107');p=O/'validation.json';s=json.loads(p.read_text());s['actual_FAR_return']='083D:2A5D';s['return_trace_events']=len(e);s['return_frame_checked']=True;s['scope']='One native checksum invocation and actual return; last-read/EOF count and stale-buffer semantics remain open.';p.write_text(json.dumps(s,indent=2))
