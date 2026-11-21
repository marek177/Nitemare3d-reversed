import json
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};bp=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x11ee:04X}",'offset':'0x00000893'},'once':True});assert rp.last_server_pid==21868;op=rp.rpc('execution.continue',P)['result']['operation_id'];w=rp.rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':10000});v={'breakpoint':bp,'operation_id':op,'wait':w}
if w['result'].get('state')=='stopped':v['registers']=rp.rpc('state.get_registers',P)
(rp.out/'EOF_seek.json').write_text(json.dumps(v,indent=2))
