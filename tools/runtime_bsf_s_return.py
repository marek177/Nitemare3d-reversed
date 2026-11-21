import json,base64,struct
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};path=rp.out/'EOF_return_control.json';assert not path.exists()
def rpc(m,a):
 r=rp.rpc(m,a);assert rp.last_server_pid==21868 and 'result' in r;return r
r=rpc('state.get_registers',P);a=r['result'];assert int(a['instruction_pointer'],16)==0x893;ss=a['segments']['ss'];bp=int(a['general']['ebp'],16)&65535
stack=rpc('memory.read',{**P,'address':{'space':'segmented','segment':ss,'offset':f'0x{bp:08X}'},'length':12});f=struct.unpack('<6H',base64.b64decode(stack['result']['data_base64']));outerbp=f[0]
outer=rpc('memory.read',{**P,'address':{'space':'segmented','segment':ss,'offset':f'0x{outerbp:08X}'},'length':16});g=struct.unpack('<8H',base64.b64decode(outer['result']['data_base64']));dest=g[3]
before=rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ds'],'offset':f'0x{dest:08X}'},'length':1});v={'before_registers':r,'inner_frame':stack,'outer_frame':outer,'destination_before':before,'destination':dest};v['breakpoint']=rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f"0x{c['loadbase']+0x83d:04X}",'offset':'0x000029A0'},'once':True});v['trace_start']=rpc('trace.start',{**P,'detail':'long','instruction_count':2000});v['operation_id']=rpc('execution.continue',P)['result']['operation_id'];path.write_text(json.dumps(v,indent=2));v['wait']=rpc('execution.wait',{**P,'operation_id':v['operation_id'],'timeout_ms':10000});path.write_text(json.dumps(v,indent=2))
if v['wait']['result'].get('state')=='stopped':
 v['after_registers']=rpc('state.get_registers',P);v['destination_after']=rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ds'],'offset':f'0x{dest:08X}'},'length':1});v['trace']=rpc('trace.read',{**P,'cursor':None,'limit':10000});v['trace_stop']=rpc('trace.stop',P);v['operation_id']=None;path.write_text(json.dumps(v,indent=2))
print(json.dumps({'inner_frame':f,'outer_frame':g,'destination':dest,'pending_operation':v['operation_id']}))
