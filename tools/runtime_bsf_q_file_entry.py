import json
from pathlib import Path
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};assert rp.rpc('session.status',P)['result']['state']=='stopped' and rp.last_server_pid==58896
r=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x83d:04X}",'offset':'0x000028EE'},'once':True});op=rp.rpc('execution.continue',P)['result']['operation_id'];w=rp.rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':10000});v={'entry_breakpoint':r,'operation_id':op,'wait':w}
if w['result'].get('state')=='stopped':
 v['registers']=rp.rpc('state.get_registers',P);a=v['registers']['result'];v['stack']=rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ss'],'offset':a['general']['esp']},'length':16})
(rp.out/'file_checksum_entry.json').write_text(json.dumps(v,indent=2))
