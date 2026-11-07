import json
from pathlib import Path
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());B=c['loadbase'];P={'session_id':c['session_id']};path=rp.out/'bsf_checksum_branch.json';assert not path.exists()
def rpc(m,p):
 r=rp.rpc(m,p);assert rp.last_server_pid==58896 and 'result' in r;return r
def reg():return rpc('state.get_registers',P)
v={'initial':reg(),'steps':[]};assert int(v['initial']['result']['segments']['cs'],16)==B+0x83d and int(v['initial']['result']['instruction_pointer'],16)==0x2a3a
v['code']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{B+0x83d:04X}','offset':'0x00002A3A'},'length':7})
for expected in (0x2a3d,0x2a3f,0x2a4f):
 x=rpc('execution.step',{**P,'mode':'into'});op=x['result'].get('operation_id');row={'operation':x};v['steps'].append(row);path.write_text(json.dumps(v,indent=2))
 if op:row['wait']=rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':1000})
 row['after']=reg();path.write_text(json.dumps(v,indent=2));assert int(row['after']['result']['instruction_pointer'],16)==expected
v['complete']=True;path.write_text(json.dumps(v,indent=2))
