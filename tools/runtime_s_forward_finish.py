import sys,json
sys.path.insert(0,'work');import runtime_probe as rp
P={'session_id':'ses-1'};p=rp.out/'forward_fixture_finish.json';v=json.loads(p.read_text()) if p.exists() else {'operation_id':None}
def rpc(m,a):
 r=rp.rpc(m,a);assert rp.last_server_pid==21868 and 'result' in r;return r
if v['operation_id'] is None and 'after_registers' not in v:
 v['before_registers']=rpc('state.get_registers',P);v['operation_id']=rpc('execution.continue',P)['result']['operation_id'];p.write_text(json.dumps(v,indent=2))
if v['operation_id']:
 v['wait']=rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000});p.write_text(json.dumps(v,indent=2))
 if v['wait']['result'].get('state')=='stopped':
  v['after_registers']=rpc('state.get_registers',P);DS=v['after_registers']['result']['segments']['ss'];v['after_inputs']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':DS,'offset':'0x00004156'},'length':12});v['flags']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':DS,'offset':'0x00003F50'},'length':2});v['operation_id']=None;p.write_text(json.dumps(v,indent=2))
print(json.dumps({'pending_operation':v['operation_id'],'PC':v.get('after_registers',{}).get('result',{}).get('instruction_pointer')}))
