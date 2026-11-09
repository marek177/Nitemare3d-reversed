from pathlib import Path
import json,base64
D=Path('outputs/evidence/runtime/bsf_eof_s_20261107');v=json.loads((D/'state7_slot26_gate_observation.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
for e in v['events']:
 b=e['before']
 for k in ['frame','actor','object','global_4153','RNG','counter']:assert raw[b[k]['id']]['response']==b[k] and raw[b[k]['id']]['server_pid']==21868
 assert b['actor_address']=='2A20:28F2' and base64.b64decode(b['object']['result']['data_base64'])[6]==10 and base64.b64decode(b['global_4153']['result']['data_base64'])==b'\0'
e=v['events'][-1];assert int(e['before']['registers']['general']['eax'],16)&255==0 and int(e['after_JE']['instruction_pointer'],16)==0x12b0
O=Path('outputs/slot26_native_gate_s_20261107');O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'VERIFIED_RAW_RPC_TARGET_ACTOR_GATE','actor':'2A20:28F2','slot':26,'type':10,'DS4153':0,'helper_return_AL':0,'branch_target':'04C7:12B0','static_call':'04C7:0F75 ->04C7:06D2 viaPUSHCS/NEARCALL','scope':'Return/branch observed; exact rejection cause inside helper not yet traced. No RNG target hit.'},indent=2));print('PASS targeted actor gate')
