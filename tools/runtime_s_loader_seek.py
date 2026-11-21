import json,time
import runtime_probe as rp
P={'session_id':'ses-1'};c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());path=rp.out/'newgame_loader_seek_control.json';v=json.loads(path.read_text()) if path.exists() else {'operation_id':None}
def rpc(m,a):
 r=rp.rpc(m,a);assert rp.last_server_pid==21868 and 'result' in r;return r
if v['operation_id'] is None:v['operation_id']=rpc('execution.continue',P)['result']['operation_id'];path.write_text(json.dumps(v,indent=2))
for _ in range(5):
 v['wait']=rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':5000});path.write_text(json.dumps(v,indent=2))
 if v['wait']['result'].get('state')=='stopped':
  v['registers']=rpc('state.get_registers',P);a=v['registers']['result'];v['stack']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ss'],'offset':a['general']['esp']},'length':16});v['operation_id']=None;path.write_text(json.dumps(v,indent=2));break
print(json.dumps({'pending_operation':v['operation_id'],'state':v['wait']['result']}))
