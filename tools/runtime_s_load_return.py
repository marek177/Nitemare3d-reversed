import json
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':'ses-1'};p=rp.out/'newgame_load_return_control.json';v={'breakpoint':rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0xd29:04X}",'offset':'0x0000281A'},'once':True})};assert rp.last_server_pid==21868;v['operation_id']=rp.rpc('execution.continue',P)['result']['operation_id'];p.write_text(json.dumps(v,indent=2));v['wait']=rp.rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000})
if v['wait']['result'].get('state')=='stopped':v['registers']=rp.rpc('state.get_registers',P);v['operation_id']=None
p.write_text(json.dumps(v,indent=2));print(json.dumps({'pending_operation':v['operation_id'],'state':v['wait']['result']}))
