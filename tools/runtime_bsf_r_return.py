import json
from pathlib import Path
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};path=rp.out/'checksum_return_control.json';v=json.loads(path.read_text()) if path.exists() else {'operation_id':None}
def rpc(m,a):
 r=rp.rpc(m,a);assert rp.last_server_pid==3136 and 'result' in r;return r
if v['operation_id'] is None and 'after' not in v:
 v['before']=rpc('state.get_registers',P);assert int(v['before']['result']['instruction_pointer'],16)==0x29a6;v['breakpoint']=rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x83d:04X}",'offset':'0x00002A5D'},'once':True});v['trace_start']=rpc('trace.start',{**P,'detail':'long','instruction_count':2000});v['operation_id']=rpc('execution.continue',P)['result']['operation_id'];path.write_text(json.dumps(v,indent=2))
if v['operation_id']:
 v['wait']=rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000});path.write_text(json.dumps(v,indent=2))
 if v['wait']['result'].get('state')=='stopped':
  v['after']=rpc('state.get_registers',P);v['trace']=rpc('trace.read',{**P,'cursor':None,'limit':10000});v['trace_stop']=rpc('trace.stop',P);v['operation_id']=None;path.write_text(json.dumps(v,indent=2))
print(json.dumps({'pending_operation':v['operation_id'],'pc':v.get('after',{}).get('result',{}).get('instruction_pointer')}))
