from pathlib import Path
import json,base64,struct,hashlib
D=Path('outputs/evidence/runtime/bsf_file_r_20261107');a=json.loads((D/'file_checksum_entry.json').read_text());b=json.loads((D/'checksum_loop_control.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
for x in [a['stack'],a['registers'],b['registers'],b['locals'],b['stream']]:
 assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==3136
 if 'data_base64' in x['result']:
  y=x['result'];z=base64.b64decode(y['data_base64']);assert len(z)==y['byte_count'] and hashlib.sha256(z).hexdigest()==y['sha256']
f=struct.unpack('<8H',base64.b64decode(a['stack']['result']['data_base64']));loc=base64.b64decode(b['locals']['result']['data_base64']);stream=base64.b64decode(b['stream']['result']['data_base64']);assert f[:6]==(0x2a5d,0x1060,0x1663,0,0,0x36);assert loc[7]==0x36 and stream[6]&0x10 and int(b['registers']['result']['instruction_pointer'],16)==0x29a6
O=Path('outputs/bsf_file_r_20261107');O.mkdir(exist_ok=True);v={'status':'VERIFIED_RAW_RPC_ENTRY_AND_CHECKSUM_ENDPOINT','pid':3136,'function':'083D:28EE','count':0,'expected_checksum':54,'actual_checksum':54,'stream_flag10_set':True,'endpoint':'083D:29A6','scope':'No final-read/EOF call-count or stale-buffer proof; no actual final FAR return captured yet.'};(O/'validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
