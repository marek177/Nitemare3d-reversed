from pathlib import Path
import json,base64
D=Path('outputs/evidence/runtime/bsf_eof_s_20261107');v=json.loads((D/'slot26_helper_trace.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
for x in [v['trace'],v['call_code']]:assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==21868
assert base64.b64decode(v['call_code']['result']['data_base64'])==bytes.fromhex('0ee85af7');e=v['trace']['result']['events'];assert len(e)==83 and [x['sequence'] for x in e]==list(range(1,84)) and v['trace']['result']['next_cursor'] is None
pcs=[int(x['address']['offset'],16) for x in e];assert pcs[0]==0xf75 and pcs[-1]==0xf78 and 0x79e in pcs and 0x7a0 not in pcs and pcs[pcs.index(0x795)+1]==0x797;state={};gates={}
for x in e:
 state.update(x.get('register_changes',{}))
 if int(x['address']['offset'],16) in [0x716,0x71d,0x795]:gates[x['address']['offset']]={'flags':state['flags']}
assert int(v['after']['registers']['general']['eax'],16)&255==0
O=Path('outputs/slot26_native_gate_s_20261107');(O/'helper_validation.json').write_text(json.dumps({'status':'VERIFIED_NATIVE_FACING_REJECTION','trace_events':83,'axis_checks_passed':True,'rejected_at':'04C7:0795','next_executed_PC':'04C7:0797','gridwalk_entered':False,'returned_AL':0,'native_FAR_return':'04C7:0F78','scope':'One slot26/type10 invocation; no general unreachability or successful RNG target claim.'},indent=2));print('PASS native facing rejection')
