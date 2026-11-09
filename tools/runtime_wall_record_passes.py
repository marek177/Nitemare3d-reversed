"""Native four-direction record passes, argument frames, buffers and FAR exit."""
import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;B=0x823;CS=B+0xfd9;DS=B+0x2771;P={'session_id':'ses-1'};ctl=O/'wall_record_pass_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'setup','operation_id':None,'passes':[]}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==23808 and 'result' in x;return x
def save():ctl.write_text(json.dumps(st,indent=2))
def read(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
def reg():return rpc('state.get_registers',P)['result']
def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
def bp(s,o,once=True):return rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'once':once})['result']['breakpoint_id']
def capture(r):return {'registers':r,'buffer':read(DS,0x62ac,28000),'count':read(DS,0x626e,2),'traits':read(DS,0xd00c,512),'header':read(DS,0xd30c,514),'map':read(B+0x21fd,0x373e,8192),'episode_level':read(DS,0x626a,4)}
def step():
 q=rpc('execution.step',{**P,'mode':'into'});st['step_operation']=q['result'].get('operation_id');save()
 if st['step_operation']:rpc('execution.wait',{**P,'operation_id':st['step_operation'],'timeout_ms':1000})
 assert rpc('session.status',P)['result']['state']=='stopped';return reg()
deadline=time.monotonic()+45
while time.monotonic()<deadline and st['phase']!='complete':
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];q=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if q.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg()
 if st['phase']=='setup':
  assert pc(r)==(B+0x277,0xb94);st['parent_before_call']=r;bp(CS,0xe1c);st['child_entry_bp']=bp(CS,0xb02,False)
  for o in (0xe28,0xe3b,0xe4e,0xe61,0xe66):bp(CS,o)
  st['phase']='entry';save()
 elif st['phase']=='entry' and pc(r)==(CS,0xe1c):
  sp=int(r['general']['esp'],16)&65535;st['before']=capture(r);st['entry_stack']=read(DS,sp,8);st['code']=read(CS,0xe1c,80);st['child_code']=read(CS,0xb02,794);st['caller_code']=read(B+0x277,0xb94,5);assert struct.unpack_from('<HH',data(st['entry_stack']))==(0xb99,B+0x277);st['phase']='child_entry';save()
 elif st['phase']=='child_entry' and pc(r)==(CS,0xb02):
  sp=int(r['general']['esp'],16)&65535;frame=read(DS,sp,12);ip,cs,direction,pointer,cumulative,savedsi=struct.unpack('<6H',data(frame));i=len(st['passes']);assert (ip,cs,direction)==((0xe28,0xe3b,0xe4e,0xe61)[i],CS,i);assert cumulative==(sum(x['returned_count'] for x in st['passes'])) and pointer==(0x62ac+28*cumulative)&65535;st['pending']={'before':capture(r),'frame':frame,'direction':direction,'pointer':pointer,'cumulative_before':cumulative,'return_ip':ip};st['phase']='child_exit';save()
 elif st['phase']=='child_exit' and pc(r)==(CS,st['pending']['return_ip']):
  p=st['pending'];n=int(r['general']['eax'],16)&65535;assert n+p['cumulative_before']<=1000;sp0=int(p['before']['registers']['general']['esp'],16)&65535;assert int(r['general']['esp'],16)&65535==(sp0+4)&65535;p['after']=capture(r);p['returned_count']=n;st['passes'].append(p);st['pending']=None;st['phase']='child_entry' if len(st['passes'])<4 else 'store';save()
 elif st['phase']=='store' and pc(r)==(CS,0xe66):
  total=sum(x['returned_count'] for x in st['passes']);assert int(r['general']['esi'],16)&65535==total;st['before_store']=capture(r);st['store_code']=read(CS,0xe66,4);assert data(st['store_code'])==bytes.fromhex('89366e62');ar=step();assert pc(ar)==(CS,0xe6a);st['after_store']=capture(ar);assert int.from_bytes(data(st['after_store']['count']),'little')==total;st['after_pop_si']=step();assert pc(st['after_pop_si'])==(CS,0xe6b);ar=step();entrysp=int(st['before']['registers']['general']['esp'],16)&65535;assert pc(ar)==(B+0x277,0xb99) and int(ar['general']['esp'],16)&65535==(entrysp+4)&65535;st['after_return']=capture(ar);rpc('breakpoints.delete',{**P,'breakpoint_id':st['child_entry_bp']});st['phase']='complete';st['operation_id']=None;save();(O/'wall_record_pass_observation.json').write_text(json.dumps(st,indent=2));break
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected wall pass stop '+str(pc(r)))
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id'],'counts':[x['returned_count'] for x in st['passes']]}))
