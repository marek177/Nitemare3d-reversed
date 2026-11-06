"""Native direction lists, four sorts and bounded indirect comparator samples."""
import json,base64,struct,time
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;B=0x823;DS=B+0x2771;CS=B+0xfd9;SORT=B+0x11ee;P={'session_id':'ses-1'};ctl=O/'wall_sort_control.json';st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'setup','operation_id':None,'sorts':[],'callbacks':[],'owned_bps':[]}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==23808 and 'result' in x;return x
def save():ctl.write_text(json.dumps(st,indent=2))
def read(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
def reg():return rpc('state.get_registers',P)['result']
def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
def bp(s,o,once=True):
 x=rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'once':once})['result']['breakpoint_id'];st['owned_bps'].append(x);save();return x
def capture(r):return {'registers':r,'groups':read(DS,0x57fa,2672),'buffer':read(DS,0x62ac,28000),'count':read(DS,0x626e,2),'descriptors':read(DS,0x4310,512)}
def step():
 q=rpc('execution.step',{**P,'mode':'into'});st['step_operation']=q['result'].get('operation_id');save()
 if st['step_operation']:rpc('execution.wait',{**P,'operation_id':st['step_operation'],'timeout_ms':1000})
 assert rpc('session.status',P)['result']['state']=='stopped';return reg()
deadline=time.monotonic()+45
while time.monotonic()<deadline and st['phase']!='complete':
 status=rpc('session.status',P)['result']
 if status['state']=='running':
  assert st['operation_id'];x=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
  if x.get('state')=='stopped':st['operation_id']=None;save()
  continue
 assert status['state']=='stopped';r=reg();where=pc(r)
 if st['phase']=='setup':
  assert where==(B+0x277,0xb99);bp(CS,0x5e);bp(CS,0x10a);bp(SORT,0x3090,False)
  for off in (0x11e,0x135,0x14c,0x163,0x168):bp(CS,off)
  for off in (0x30ad,0x312f,0x314d):bp(SORT,off)
  st['phase']='entry';save()
 elif st['phase']=='entry' and where==(CS,0x5e):
  st['before']=capture(r);sp=int(r['general']['esp'],16)&65535;st['entry_stack']=read(DS,sp,8);st['code']=read(CS,0x5e,267);st['caller_code']=read(B+0x277,0xb99,5);st['comparator_code']=read(CS,0x16,72);st['sort_code']=read(SORT,0x3090,312);assert struct.unpack_from('<HH',data(st['entry_stack']))==(0xb9e,B+0x277);st['phase']='grouped';save()
 elif st['phase']=='grouped' and where==(CS,0x10a):st['grouped']=capture(r);st['phase']='sort_entry';save()
 elif st['phase']=='sort_entry' and where==(SORT,0x3090):
  i=len(st['sorts']);sp=int(r['general']['esp'],16)&65535;frame=read(DS,sp,14);ip,cs,base,n,size,cmpip,cmpcs=struct.unpack('<7H',data(frame));assert (ip,cs,base,size,cmpip,cmpcs)==((0x11e,0x135,0x14c,0x163)[i],CS,(0x5802,0x5a9c,0x5d36,0x5fd0)[i],2,0x16,CS);st['pending_sort']={'before':capture(r),'frame':frame,'base':base,'count':n,'direction':i,'return_ip':ip};st['phase']='sorting';save()
 elif st['phase']=='sorting' and where[0]==SORT and where[1] in (0x30ad,0x312f,0x314d):
  off=where[1];sp=int(r['general']['esp'],16)&65535;ss=int(r['segments']['ss'],16);bpreg=int(r['general']['ebp'],16)&65535;di=int(r['general']['edi'],16)&65535;operand=bpreg+0xc if off==0x30ad else di+0x12;target=read(ss,operand,4);ip,seg=struct.unpack('<HH',data(target));assert(ip,seg)==(0x16,CS);args=read(ss,sp,4);pa,pb=struct.unpack('<HH',data(args));ea=read(DS,pa,2);eb=read(DS,pb,2);ra=int.from_bytes(data(ea),'little');rb=int.from_bytes(data(eb),'little');sample={'site':f'11EE:{off:04X}','before_registers':r,'operand':target,'operand_offset':operand,'args':args,'element_pointers':[ea,eb],'records':[read(DS,ra,28),read(DS,rb,28)],'code':read(SORT,off,3 if off==0x30ad else 4),'sort_direction':st['pending_sort']['direction']};ret=off+(3 if off==0x30ad else 4);sample['return_ip']=ret;bp(SORT,ret);rpc('trace.start',{**P,'detail':'long','instruction_count':1000});ar=step();assert pc(ar)==(CS,0x16);sample['entry_registers']=ar;sample['entry_frame']=read(ss,int(ar['general']['esp'],16)&65535,8);st['pending_callback']=sample;st['phase']='callback_return';save()
 elif st['phase']=='callback_return' and where==(SORT,st['pending_callback']['return_ip']):
  p=st['pending_callback'];p['after_registers']=r;p['trace_chunks']=[];cursor=None
  for _ in range(4):
   x=rpc('trace.read',{**P,'cursor':cursor,'limit':500});p['trace_chunks'].append(x);cursor=x['result'].get('next_cursor')
   if cursor is None:break
  assert cursor is None;rpc('trace.stop',P);st['callbacks'].append(p);st['pending_callback']=None;st['phase']='sorting';save()
 elif st['phase']=='sorting' and where==(CS,st['pending_sort']['return_ip']):
  p=st['pending_sort'];p['after']=capture(r);st['sorts'].append(p);st['pending_sort']=None;st['phase']='sort_entry' if len(st['sorts'])<4 else 'return';save()
 elif st['phase']=='return' and where==(CS,0x168):
  st['before_return']=capture(r);ar=step();sp=int(st['before']['registers']['general']['esp'],16)&65535;assert pc(ar)==(B+0x277,0xb9e) and int(ar['general']['esp'],16)&65535==(sp+4)&65535;st['after_return']=capture(ar);listing=rpc('breakpoints.list',P);st['bp_cleanup_before']=listing
  for x in listing['result']['breakpoints']:
   if x['breakpoint_id'] in st['owned_bps']:rpc('breakpoints.delete',{**P,'breakpoint_id':x['breakpoint_id']})
  st['bp_cleanup_after']=rpc('breakpoints.list',P);st['phase']='complete';st['operation_id']=None;save();(O/'wall_sort_observation.json').write_text(json.dumps(st,indent=2));break
 else:st['unexpected_stop']=r;save();raise RuntimeError('Unexpected wall sort stop '+str(where)+' '+st['phase'])
 st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id'],'sorts':len(st['sorts']),'callback_sites':[x['site'] for x in st['callbacks']]}))
