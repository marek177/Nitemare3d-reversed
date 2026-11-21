"""Capture one native canonical wall-trait invocation without game writes."""
import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;B=0x823;DS=B+0x2771;CS=B+0xf7;P={'session_id':'ses-1'};ctl=O/'native_trait_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'await_entry','operation_id':None,'started':False}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==23808 and 'result' in x;return x
def save():ctl.write_text(json.dumps(st,indent=2))
def read(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
def reg():return rpc('state.get_registers',P)['result']
def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
def capture(r):return {'registers':r,'output':read(DS,0xd00c,256),'header':read(DS,0xd30e,256),'episode_level':read(DS,0x626a,4)}
deadline=time.monotonic()+45
while time.monotonic()<deadline and st['phase']!='complete':
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];q=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if q.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg()
 if st['phase']=='await_entry' and pc(r)==(CS,0x1b6):
  assert int(r['segments']['ds'],16)==int(r['segments']['ss'],16)==DS;sp=int(r['general']['esp'],16)&65535;st['before']=capture(r);st['entry_stack']=read(DS,sp-8,16);st['initial_local']=read(DS,sp-3,1);st['code']=read(CS,0x1b6,153);st['caller_code']=read(B+0x277,0xb8a,5);assert struct.unpack_from('<HH',data(st['entry_stack']),8)==(0xb8f,B+0x277);assert data(st['caller_code'])==bytes.fromhex('9ab601')+struct.pack('<H',CS)
  st['ret_breakpoint']=rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{CS:04X}','offset':'0x0000024E'},'once':True});rpc('trace.start',{**P,'detail':'long','instruction_count':10000});st['phase']='await_ret';save()
 elif st['phase']=='await_ret' and pc(r)==(CS,0x24e):
  st['before_return']=capture(r);st['trace_chunks']=[];cursor=None
  for _ in range(22):
   x=rpc('trace.read',{**P,'cursor':cursor,'limit':500});st['trace_chunks'].append(x);cursor=x['result'].get('next_cursor')
   if cursor is None:break
  assert cursor is None;rpc('trace.stop',P);st['phase']='step_return';save()
  q=rpc('execution.step',{**P,'mode':'into'});st['return_operation']=q['result'].get('operation_id');save()
  if st['return_operation']:rpc('execution.wait',{**P,'operation_id':st['return_operation'],'timeout_ms':1000})
  assert rpc('session.status',P)['result']['state']=='stopped';ar=reg();st['after_return']=capture(ar);sp=int(st['before']['registers']['general']['esp'],16)&65535;assert pc(ar)==(B+0x277,0xb8f) and int(ar['general']['esp'],16)&65535==(sp+4)&65535;st['phase']='complete';st['operation_id']=None;save();(O/'native_wall_trait_observation.json').write_text(json.dumps(st,indent=2));break
 elif st['phase']=='await_entry' and not st['started']:st['started']=True;save()
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected native trait stop; preserve '+str(pc(r)))
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id']}))
