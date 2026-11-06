import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());B=c['loadbase'];DS=B+0x2771;P={'session_id':c['session_id']};spec=json.loads((O/'run_config.json').read_text());pid=int(Path(spec['pid_file']).read_text());ctl=O/'level1_fixture_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'clear','operation_id':None}
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
while time.monotonic()<deadline and st['phase']!='header':
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];x=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if x.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg();where=pc(r)
 if st['phase']=='cache_restore' and where==(0xd29,0x28ae):
  before=read(DS,0x4144,16);expected=bytearray(data(before));assert expected[8]==0;write=rpc('memory.write',{**P,'address':{'space':'segmented','segment':f'0x{DS:04X}','offset':'0x0000414C'},'data_base64':'AQ=='});after=read(DS,0x4144,16);expected[8]=1;assert data(after)==expected;st['menu_option_restore']={'registers':r,'before':before,'write':write,'after':after};st['phase']='cache_copy';save()
 elif st['phase']=='cache_copy' and where==(0xd29,0x28be):
  di=int(r['general']['edi'],16)&65535;es=int(r['segments']['es'],16);assert int(r['general']['ecx'],16)==4;st['native_cache_before']={'registers':r,'source':read(DS,0x4144,16),'destination':read(es,di,16),'code':read(B+0xd29,0x28be,3)};st['cache_destination']=[es,di];st['phase']='cache_done';save()
 elif st['phase']=='cache_done' and where==(0xd29,0x28c1):
  es,di=st['cache_destination'];st['native_cache_after']={'registers':r,'destination':read(es,di,16)};assert data(st['native_cache_after']['destination'])==data(st['native_cache_before']['source']) and data(st['native_cache_before']['source'])[8]==1;st['phase']='clear';save()
 elif st['phase']=='clear' and where==(0xd29,0x28c9):
  st['clear_before']={'registers':r,'config':read(DS,0x4144,16),'code':read(B+0xd29,0x28c9,3)};assert data(st['clear_before']['config'])[15]==1 and data(st['clear_before']['code'])==bytes.fromhex('a25341');ar=step();st['clear_after']={'registers':ar,'config':read(DS,0x4144,16)};expected=bytearray(data(st['clear_before']['config']));expected[15]=0;assert data(st['clear_after']['config'])==expected;st['phase']='argument';save()
 elif st['phase']=='argument' and where==(0xd29,0x26f4):
  sp=int(r['general']['esp'],16)&65535;ss=int(r['segments']['ss'],16);before=read(ss,sp,16);assert struct.unpack_from('<3H',data(before))==(B+0xd29,10,1);code=read(B+0xd29,0x26f3,4);assert data(code)==bytes.fromhex('0ee863e2');write=rpc('memory.write',{**P,'address':{'space':'segmented','segment':f'0x{ss:04X}','offset':f'0x{sp+2:08X}'},'data_base64':'AAA='});after=read(ss,sp,16);expected=bytearray(data(before));expected[2:4]=b'\0\0';assert data(after)==expected;st['argument_fixture']={'registers':r,'code':code,'stack_before':before,'write':write,'stack_after':after,'scope':'One2-byte input10-to0; episode1 and explicitPUSHCS frame unchanged. Not nativeUI level selection.'};st['phase']='store';save()
 elif st['phase']=='store' and where==(0xd29,0x97d):
  bp=int(r['general']['ebp'],16)&65535;frame=read(DS,bp,12);assert struct.unpack_from('<HH',data(frame),6)==(0,1) and int(r['general']['eax'],16)&65535==0;st['store_before']={'registers':r,'frame':frame,'globals':read(DS,0x626a,4),'code':read(B+0xd29,0x97d,3)};assert data(st['store_before']['code'])==bytes.fromhex('a36c62');ar=step();st['store_after']={'registers':ar,'globals':read(DS,0x626a,4)};expected=bytearray(data(st['store_before']['globals']));expected[2:4]=bytes(2);assert data(st['store_after']['globals'])==expected;st['phase']='await_header';save()
 elif st['phase']=='await_header' and where==(0x6b0,0x2e0):
  st['header']={'registers':r,**{k:read(DS,o,n) for k,o,n in [('episode_level',0x626a,4),('filename',0x629c,16),('RNG',0x24b8,4),('counter',0x4540,4),('header_words',0x455c,6),('map_header',0xd30c,514)]}};st['phase']='header';st['operation_id']=None;save();(O/'level1_fixture_observation.json').write_text(json.dumps(st,indent=2));break
 elif st['phase'] in ('clear','cache_restore') and not st.get('started'):st['started']=True;save()
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected level1 stop '+str(where)+' '+st['phase'])
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id']}))
