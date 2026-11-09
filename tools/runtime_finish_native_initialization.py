import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;B=0x823;DS=B+0x2771;P={'session_id':'ses-1'};ctl=O/'finish_init_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'setup','operation_id':None}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==23808 and 'result' in x;return x
def save():ctl.write_text(json.dumps(st,indent=2))
def reg():return rpc('state.get_registers',P)['result']
def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
def read(o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{DS:04X}','offset':f'0x{o:08X}'},'length':n})
def capture(r):return {'registers':r,**{k:read(o,n) for k,o,n in [('buffer',0x62ac,28000),('count',0x626e,2),('descriptors',0x4310,512),('episode_level',0x626a,4),('filename',0x629c,16),('RNG',0x24b8,4),('counter',0x4540,4),('header_words',0x455c,6)]}}
deadline=time.monotonic()+45
while time.monotonic()<deadline and st['phase']!='complete':
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];x=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if x.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg();where=pc(r)
 if st['phase']=='setup':
  assert where==(B+0x277,0xb9e);st['before_remaining']=capture(r)
  for s,o in [(0x277,0xbc0),(0x6b0,0x2e0)]:rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{B+s:04X}','offset':f'0x{o:08X}'},'once':True})
  st['phase']='parent_return';save()
 elif st['phase']=='parent_return' and where==(B+0x277,0xbc0):
  st['before_parent_return']=capture(r);sp=int(r['general']['esp'],16)&65535;st['parent_return_frame']=read(sp,4);assert struct.unpack('<HH',base64.b64decode(st['parent_return_frame']['result']['data_base64']))==(0x9c4,B+0xd29);q=rpc('execution.step',{**P,'mode':'into'});st['step_operation']=q['result'].get('operation_id');save()
  if st['step_operation']:rpc('execution.wait',{**P,'operation_id':st['step_operation'],'timeout_ms':1000})
  assert rpc('session.status',P)['result']['state']=='stopped';ar=reg();assert pc(ar)==(B+0xd29,0x9c4) and int(ar['general']['esp'],16)&65535==(sp+4)&65535;st['after_parent_return']=capture(ar);st['phase']='header';save()
 elif st['phase']=='header' and where==(B+0x6b0,0x2e0):st['header']=capture(r);st['phase']='complete';st['operation_id']=None;save();(O/'finished_init_observation.json').write_text(json.dumps(st,indent=2));break
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected initialization stop '+str(where)+' '+st['phase'])
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id']}))
