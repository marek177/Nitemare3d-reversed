import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;D=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());B=c['loadbase'];P={'session_id':c['session_id']};pid=int((R/'work/runtime/bsf_q_pid.txt').read_text());path=D/'bsf_native_control.json';s=json.loads(path.read_text()) if path.exists() else {'phase':'arm','operation_id':None}
def rpc(m,p):
 r=rp.rpc(m,p);assert rp.last_server_pid==pid and 'result' in r;return r
def save():path.write_text(json.dumps(s,indent=2))
def read(seg,off,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{seg:04X}','offset':f'0x{off:08X}'},'length':n})
def bp(seg,off):return rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{seg:04X}','offset':f'0x{off:08X}'},'once':True})
def data(x):return base64.b64decode(x['result']['data_base64'])
if s['phase']=='arm':s['entry_bp']=bp(B+0xfba,0x1b2);s['phase']='seek';save()
deadline=time.monotonic()+45
while time.monotonic()<deadline and s['phase'] not in ('complete','attention'):
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert s['operation_id'];w=rpc('execution.wait',{**P,'operation_id':s['operation_id'],'timeout_ms':5000})['result']
  if w.get('state')=='stopped':s['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=rpc('state.get_registers',P);a=r['result'];where=(int(a['segments']['cs'],16)-B,int(a['instruction_pointer'],16))
 if s['phase']=='seek' and where==(0xfba,0x1b2):
  ss=int(a['segments']['ss'],16);sp=int(a['general']['esp'],16)&65535;frame=read(ss,sp,10);ip,cs,off,seg,n=struct.unpack('<5H',data(frame));s['before']={'registers':r,'stack':frame,'buffer':read(seg,off,n),'key':read(ss,0x2045,52),'code':read(B+0xfba,0x1b2,62),'caller_code':read(cs,ip-5,5)};assert (ip,cs,n)==(0x2a3a,B+0x83d,54);s['args']=[off,seg,n];s['return_bp']=bp(cs,ip);s['trace_start']=rpc('trace.start',{**P,'detail':'long','instruction_count':3000});s['phase']='return';save()
 elif s['phase']=='return' and where==(0x83d,0x2a3a):
  off,seg,n=s['args'];ss=int(a['segments']['ss'],16);s['after']={'registers':r,'buffer':read(seg,off,n),'key':read(ss,0x2045,52)};s['trace']=rpc('trace.read',{**P,'cursor':None,'limit':10000});s['trace_stop']=rpc('trace.stop',P);s['breakpoints']=rpc('breakpoints.list',P);s['phase']='complete';s['operation_id']=None;save();(D/'bsf_native_observation.json').write_text(json.dumps(s,indent=2));break
 elif s['phase']=='seek' and not s.get('started'):s['started']=True;save()
 else:s['unexpected_stop']=r;s['phase']='attention';save();break
 s['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':s['phase'],'operation_id':s['operation_id'],'args':s.get('args')}))
