import json
from pathlib import Path
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};path=rp.out/'checksum_loop_control.json';v=json.loads(path.read_text()) if path.exists() else {'operation_id':None}
def rpc(m,a):
 r=rp.rpc(m,a);assert rp.last_server_pid==3136 and 'result' in r;return r
if v['operation_id'] is None:
 assert rpc('session.status',P)['result']['state']=='stopped';v['breakpoint']=rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x83d:04X}",'offset':'0x000029A6'},'once':True});v['operation_id']=rpc('execution.continue',P)['result']['operation_id'];path.write_text(json.dumps(v,indent=2))
v['wait']=rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000});path.write_text(json.dumps(v,indent=2))
if v['wait']['result'].get('state')=='stopped':
 v['registers']=rpc('state.get_registers',P);a=v['registers']['result'];v['locals']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ss'],'offset':f"0x{(int(a['general']['ebp'],16)-16)&65535:08X}"},'length':32});v['stream']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ds'],'offset':a['general']['esi']},'length':24});v['operation_id']=None;path.write_text(json.dumps(v,indent=2))
print(json.dumps({'operation_id':v['operation_id'],'state':v['wait']['result']}))
