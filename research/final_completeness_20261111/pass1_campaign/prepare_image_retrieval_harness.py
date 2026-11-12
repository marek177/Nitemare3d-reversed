"""Derive a frozen original0402/XMS readback harness from retained startup navigation."""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'runtime_watch_image_record.py').read_text(encoding='utf-8')
a=s.index("  if stage=='image_record_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='image_retrieval_entry':
   prefix='image_retrieval_00_';pre=reg
   def capture(name,seg,off,n):
    raw=dump(seg,off,n,prefix+name+'.bin');capture_files.append(work/(prefix+name+'.bin'));return raw
   frame=capture('frame_before',pre['SS'],pre['SP'],6);retip,retcs,record=struct.unpack('<3H',frame)
   rec=capture('record_before',pre['DS'],record,10)
   pointers=capture('slot_pointers',pre['DS'],0x34cc,40)
   capture('stats_before',pre['DS'],0xe006,8);capture('tick_before',pre['DS'],0x4540,4)
   for i in range(10):
    off,seg=struct.unpack_from('<HH',pointers,4*i);capture('slot_%02d_before'%i,seg,off,6)
   capture('request_segment',pre['DS'],0x2560,2)
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC BP %04X:000007FE'%(load+0x768));request('EXEC RUN')
   movereg=wait_for(load+0x768,0x7fe,30)
   selector=struct.unpack('<H',(work/(prefix+'request_segment.bin')).read_bytes())[0]
   move=capture('xms_request',selector,0x200,16);length,sourcehandle,sourceoffset,desthandle,dest=struct.unpack('<IHIHI',move)
   assert length==8192 and sourcehandle!=0 and desthandle==0
   capture('destination_before',dest>>16,dest&65535,length)
   request('EXEC BP %04X:00000815'%(load+0x768));request('EXEC RUN');managerreg=wait_for(load+0x768,0x815,30)
   capture('destination_after_manager',dest>>16,dest&65535,length)
   request('EXEC RUN');post=wait_for(retcs,retip,30)
   capture('record_after',pre['DS'],record,10);capture('stats_after',pre['DS'],0xe006,8);capture('tick_after',pre['DS'],0x4540,4)
   capture('destination_after_return',dest>>16,dest&65535,length);capture('frame_after',pre['SS'],pre['SP'],6)
   for i in range(10):
    off,seg=struct.unpack_from('<HH',pointers,4*i);capture('slot_%02d_after'%i,seg,off,6)
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,xms_move_registers=movereg,manager_return_registers=managerreg,post_registers=post,record_offset=record))
   success=True;break
'''
s=s[:a]+block+s[z:]
s=s.replace("points[(load+0x277,0x45c)]='image_record_entry';request('EXEC BP %04X:0000045C'%(load+0x277))", "points[(load+0x768,0x402)]='image_retrieval_entry';request('EXEC BP %04X:00000402'%(load+0x768))")
s=s.replace("'image_records.json'","'image_retrievals.json'").replace('image_record_runtime=True,image_records=len(branch_returns)','image_retrieval_runtime=True,image_retrievals=len(branch_returns)')
s=s.replace('original0277:045C entry/rawpixel-load/XMSmove/append/caller snapshots; no whole-memory parity claim','original0768:0402 whole call with XMS destination readback and direct manager return; no whole-memory or renderer parity claim')
(r/'runtime_watch_image_retrieval.py').write_text(s,encoding='utf-8')
