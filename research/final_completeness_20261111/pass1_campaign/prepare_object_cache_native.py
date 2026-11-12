"""OUTPUTS: original0768:04D8 cyclic object cache capture, no game patches."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_calendar.py').read_text(encoding='utf-8');a=s.index("  if stage=='calendar_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='object_cache_entry':
   prefix='object_cache_00_';pre=reg
   def capture(name,seg,off,n):
    raw=dump(seg,off,n,prefix+name+'.bin');capture_files.append(work/(prefix+name+'.bin'));return raw
   def extra_regs():
    response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));return dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   ext=extra_regs();frame=capture('frame_before',pre['SS'],pre['SP'],6);retip,retcs,record=struct.unpack('<3H',frame)
   rec=capture('record_before',pre['DS'],record,10);area=rec[0]*rec[1];tag=struct.unpack_from('<I',rec,2)[0];assert area>0 and (tag==0 or tag>=0x80000000)
   state=capture('state_before',pre['DS'],0x3504,2);count=struct.unpack('<H',state)[0];index=struct.unpack('<H',capture('index_before',pre['DS'],0xc9c,2))[0];assert 0<=index<count<=128
   table_seg=struct.unpack('<H',capture('table_segment',pre['DS'],0x2560,2))[0];table=capture('pointer_table_before',table_seg,0,512);off,seg=struct.unpack_from('<HH',table,4*index)
   owner=struct.unpack('<H',capture('slot_owner_before',seg,off,2))[0]
   if owner:capture('old_record_before',pre['DS'],owner,10)
   capture('DGROUP_before',pre['DS'],0,0xe030);capture('stats_before',pre['DS'],0xe012,4)
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC BP %04X:000007FE'%(load+0x768));request('EXEC RUN');movereg=wait_for(load+0x768,0x7fe,30)
   move=capture('xms_request',table_seg,0x200,16);length,sourcehandle,sourceoffset,desthandle,dest=struct.unpack('<IHIHI',move);assert length==((area+1023)//1024)*1024 and sourcehandle!=0 and desthandle==0
   capture('destination_before',dest>>16,dest&65535,length);request('EXEC BP %04X:00000815'%(load+0x768));request('EXEC RUN');managerreg=wait_for(load+0x768,0x815,30);capture('destination_after_manager',dest>>16,dest&65535,length)
   request('EXEC RUN');post=wait_for(retcs,retip,30);postext=extra_regs();capture('record_after',pre['DS'],record,10);capture('slot_owner_after',seg,off,2)
   if owner:capture('old_record_after',pre['DS'],owner,10)
   capture('destination_after_return',dest>>16,dest&65535,length);capture('DGROUP_after',pre['DS'],0,0xe030);capture('pointer_table_after',table_seg,0,512);capture('stats_after',pre['DS'],0xe012,4);capture('index_after',pre['DS'],0xc9c,2);capture('frame_after',pre['SS'],pre['SP'],6)
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,xms_move_registers=movereg,manager_return_registers=managerreg,post_registers=post,post_extra=postext,record_offset=record,area=area,tag_hex='%08X'%tag,slot_index=index,slot_count=count,old_owner=owner))
   success=True;break
'''
s=s[:a]+block+s[z:];s=s.replace("points[(load+0x11ee,0x2dc0)]='calendar_entry'","points[(load+0x768,0x4d8)]='object_cache_entry'")
s=s.replace("'calendar_calls.json'","'object_cache_calls.json'").replace('calendar_runtime=True,calendar_calls=len(branch_returns)','object_cache_runtime=True,object_cache_calls=len(branch_returns)')
s=s.replace('original11EE:2DC0 whole calendar conversion with native arguments/timezone-ready/fullDGROUP snapshots; no renderer or global calendar parity claim','original0768:04D8 whole object cache call,fullDGROUP/pointertable/index/slotowner/XMS readback; no full renderer or global parity claim')
(r/'runtime_watch_object_cache.py').write_text(s,encoding='utf-8')
