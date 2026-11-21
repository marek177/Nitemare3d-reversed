import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());B=c['loadbase'];DS=B+0x2771;CS=B+0xd29;P={'session_id':c['session_id']};pid=int(Path(json.loads((O/'run_config.json').read_text())['pid_file']).read_text());ctl=O/'native_load_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'cache','operation_id':None,'probes':[],'gates':[],'started':False}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==pid and 'result' in x;return x
def save():ctl.write_text(json.dumps(st,indent=2))
def read(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
def reg():return rpc('state.get_registers',P)['result']
def pc(r):return int(r['segments']['cs'],16)-B,int(r['instruction_pointer'],16)
def step():
 q=rpc('execution.step',{**P,'mode':'into'});st['step_operation']=q['result'].get('operation_id');save()
 if st['step_operation']:rpc('execution.wait',{**P,'operation_id':st['step_operation'],'timeout_ms':1000})
 assert rpc('session.status',P)['result']['state']=='stopped';return reg()
deadline=time.monotonic()+45
while time.monotonic()<deadline and st['phase'] not in ('header','attention'):
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];x=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if x.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg();where=pc(r)
 if st['phase']=='cache' and where==(0xd29,0x28be):
  di=int(r['general']['edi'],16)&65535;es=int(r['segments']['es'],16);st['cache_before']={'registers':r,'source':read(DS,0x4144,16),'destination':read(es,di,16),'code':read(CS,0x28be,3)};st['cache_pointer']=[es,di];st['phase']='cache_done';save()
 elif st['phase']=='cache_done' and where==(0xd29,0x28c1):
  es,di=st['cache_pointer'];st['cache_after']={'registers':r,'destination':read(es,di,16)};assert data(st['cache_before']['source'])==data(st['cache_after']['destination']);st['phase']='clear';save()
 elif st['phase']=='clear' and where==(0xd29,0x28c9):
  st['clear_before']={'registers':r,'config':read(DS,0x4144,16),'code':read(CS,0x28c9,3)};assert data(st['clear_before']['config'])[15]==1;ar=step();st['clear_after']={'registers':ar,'config':read(DS,0x4144,16)};expected=bytearray(data(st['clear_before']['config']));expected[15]=0;assert data(st['clear_after']['config'])==expected;st['phase']='selector';save()
 elif st['phase']=='selector' and where==(0xd29,0x2696):
  sp=int(r['general']['esp'],16)&65535;st['selector_entry']={'registers':r,'stack':read(DS,sp,8),'code':read(CS,0x2696,75)};assert struct.unpack_from('<HH',data(st['selector_entry']['stack']))==(0x26e6,CS);st['phase']='scan';save()
 elif st['phase']=='scan' and where==(0xd29,0x26b7):
  bp=int(r['general']['ebp'],16)&65535;sp=int(r['general']['esp'],16)&65535;args=read(DS,sp,4);ptr,mode=struct.unpack('<HH',data(args));assert ptr==bp-16 and mode==4;st['pending_probe']={'before_registers':r,'arguments':args,'filename':read(DS,ptr,16),'code':read(CS,0x26b7,5)};save()
 elif st['phase']=='scan' and where==(0xd29,0x26bc):
  p=st['pending_probe'];p['after_registers']=r;p['returned_AX']=int(r['general']['eax'],16)&65535;st['probes'].append(p);st['pending_probe']=None;save()
 elif st['phase']=='scan' and where==(0xd29,0x26c5):st['pending_gate']={'before_registers':r,'argument':read(DS,int(r['general']['esp'],16)&65535,2),'code':read(CS,0x26c5,5)};save()
 elif st['phase']=='scan' and where==(0xd29,0x26ca):
  p=st['pending_gate'];p['after_registers']=r;p['DX_AX']=[int(r['general'][x],16)&65535 for x in ('edx','eax')];st['gates'].append(p);st['pending_gate']=None;save()
 elif st['phase']=='scan' and where==(0xd29,0x26e6):
  st['selector_return']=r;st['selected_episode']=int(r['general']['eax'],16)&65535
  if st['selected_episode']!=3:st['phase']='attention';save();break
  st['phase']='arguments';save()
 elif st['phase']=='arguments' and where==(0xd29,0x26f4):
  sp=int(r['general']['esp'],16)&65535;st['loader_arguments']={'registers':r,'stack':read(DS,sp,16),'code':read(CS,0x26f3,4)};assert struct.unpack_from('<3H',data(st['loader_arguments']['stack']))==(CS,0,3);st['phase']='store';save()
 elif st['phase']=='store' and where==(0xd29,0x97d):
  bp=int(r['general']['ebp'],16)&65535;st['store_before']={'registers':r,'frame':read(DS,bp,12),'globals':read(DS,0x626a,4),'code':read(CS,0x97d,3)};assert struct.unpack_from('<HH',data(st['store_before']['frame']),6)==(0,3);ar=step();st['store_after']={'registers':ar,'globals':read(DS,0x626a,4)};assert int.from_bytes(data(st['store_after']['globals'])[2:],'little')==0;st['phase']='await_header';save()
 elif st['phase']=='await_header' and where==(0x6b0,0x2e0):
  st['header']={'registers':r,**{k:read(DS,o,n) for k,o,n in [('episode_level',0x626a,4),('filename',0x629c,16),('RNG',0x24b8,4),('counter',0x4540,4),('header_words',0x455c,6),('map_header',0xd30c,514)]}};arm=json.loads((O/'native_load_arm.json').read_text());listing=rpc('breakpoints.list',P);st['bp_cleanup_before']=listing
  for x in listing['result']['breakpoints']:
   if x['breakpoint_id'] in arm['owned_bps']:rpc('breakpoints.delete',{**P,'breakpoint_id':x['breakpoint_id']})
  st['bp_cleanup_after']=rpc('breakpoints.list',P);st['phase']='header';st['operation_id']=None;save();(O/'native_episode3_observation.json').write_text(json.dumps(st,indent=2));break
 elif st['phase']=='cache' and not st['started']:st['started']=True;save()
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected native P stop '+str(where)+' '+st['phase'])
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id'],'selected_episode':st.get('selected_episode'),'probes':len(st['probes'])}))
