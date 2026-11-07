import json,base64,hashlib,struct
from pathlib import Path
D=Path('outputs/evidence/runtime/bsf_native_q_20261107');v=json.loads((D/'bsf_native_observation.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x:
   assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==58896
   if 'data_base64' in x.get('result',{}):
    a=x['result'];b=base64.b64decode(a['data_base64']);assert len(b)==a['byte_count'] and hashlib.sha256(b).hexdigest()==a['sha256']
  for z in x.values():check(z)
 elif isinstance(x,list):
  for z in x:check(z)
check(v);b=v['before'];a=v['after'];data=lambda x:base64.b64decode(x['result']['data_base64']);src=data(b['buffer']);key=data(b['key']);want=bytes(x^key[i%52] for i,x in enumerate(src));assert data(a['buffer'])==want and data(a['key'])==key
r=b['registers']['result'];t=a['registers']['result'];sp=int(r['general']['esp'],16)&65535;assert int(t['general']['esp'],16)&65535==sp+4 and int(t['general']['eax'],16)&65535==0
for k in ['esi','edi','ebp']:assert r['general'][k]==t['general'][k]
ev=v['trace']['result']['events'];assert len(ev)==719 and [x['sequence'] for x in ev]==list(range(1,720)) and v['trace']['result']['next_cursor'] is None
state={};reads=[];stores=[]
for e in ev:
 state.update(e.get('register_changes',{}));o=int(e['address']['offset'],16)
 if int(e['address']['segment'],16)==int(r['segments']['cs'],16):
  if o==0x1cb:reads.append(int(state['eax'],16)&255)
  if o==0x1de:
   i=int(state['edi'],16)&65535;assert int(state['esi'],16)&65535==0x3638+i and int(state['eax'],16)&255==key[i%52];stores.append(i)
assert bytes(reads)==src and stores==list(range(54))
branch=json.loads((D/'bsf_checksum_branch.json').read_text());check(branch);assert branch['complete'] and int(branch['steps'][-1]['after']['result']['instruction_pointer'],16)==0x2a4f
O=Path('outputs/bsf_native_q_20261107');O.mkdir(exist_ok=True);out={'status':'VERIFIED_RAW_RPC_NATIVE_TRANSFORM_AND_CHECKSUM_BRANCH','pid':58896,'trace_events':719,'ordered_byte_stores':54,'input_bytes_match_supplied_header':src==Path('work/runtime/game_bsf_native_q_20261107/NITE3D.BSF').read_bytes()[:54],'output_sha256':hashlib.sha256(want).hexdigest(),'decoded_gate_byte':want[3],'native_return':'083D:2A3A','native_checksum_branch':'2A3A ->2A3D ->2A3F ->2A4F','scope':'One native startup invocation; whole boundaries/IRQ/general aliases and file-read provenance remain open.'};(O/'validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
