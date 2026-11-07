import json
import runtime_probe as rp
p=rp.out/'newgame_load_return_control.json';v=json.loads(p.read_text());P={'session_id':'ses-1'}
if v['operation_id']:
 v['wait']=rp.rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000});assert rp.last_server_pid==21868
 if v['wait']['result'].get('state')=='stopped':v['registers']=rp.rpc('state.get_registers',P);v['operation_id']=None
 p.write_text(json.dumps(v,indent=2))
print(json.dumps({'pending_operation':v['operation_id'],'state':v['wait']['result']}))
