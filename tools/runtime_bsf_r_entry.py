from pathlib import Path
import json
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};pid=int((rp.root/'work/runtime/bsf_r_pid.txt').read_text());s=rp.rpc('session.status',P);assert rp.last_server_pid==pid and s['result']['state']=='stopped';bp=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x83d:04X}",'offset':'0x000028EE'},'once':True});op=rp.rpc('execution.continue',P)['result']['operation_id'];w=rp.rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':10000});v={'server_pid':pid,'operation_id':op,'wait':w,'breakpoint':bp}
if w['result'].get('state')=='stopped':
 r=rp.rpc('state.get_registers',P);v['registers']=r;a=r['result'];v['stack']=rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ss'],'offset':a['general']['esp']},'length':16})
(rp.out/'file_checksum_entry.json').write_text(json.dumps(v,indent=2))
