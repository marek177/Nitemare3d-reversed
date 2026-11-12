"""python prepare_image_record_harness.py OUTPUTS
Original045C entry -> raw03CA return -> XMS move -> append return -> actual caller.
"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_guard_orientation_v2.py').read_text(encoding='utf-8');a=s.index("  if stage=='guard_orientation_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='image_record_entry':
   prefix='image_record_00_';pre=reg
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));ext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   frame=dump(pre['SS'],pre['SP'],14,prefix+'frame_before.bin');capture_files.append(work/(prefix+'frame_before.bin'));retip,retcs,handle,record,code,index,wall=struct.unpack('<7H',frame)
   def stage_capture(label):
    for name,seg,off,length in [('record',pre['DS'],record,10),('stats',pre['DS'],0xe00c,0x12),('cache_state',pre['DS'],0x3506,6),('flag',pre['DS'],0x3cce,1)]:
     dump(seg,off,length,prefix+label+'_'+name+'.bin');capture_files.append(work/(prefix+label+'_'+name+'.bin'))
   stage_capture('entry');request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC BP %04X:00000474'%(load+0x277));request('EXEC RUN');rawreg=wait_for(load+0x277,0x474,30);stage_capture('raw_loaded')
   rec=(work/(prefix+'raw_loaded_record.bin')).read_bytes();size=rec[0]*rec[1];off,seg=struct.unpack_from('<HH',rec,6);assert size>0
   dump(seg,off,size,prefix+'pixels_raw.bin');capture_files.append(work/(prefix+'pixels_raw.bin'))
   request('EXEC BP %04X:000007FE'%(load+0x768));request('EXEC BP %04X:000003E4'%(load+0x768));request('EXEC RUN');movereg=wait_for(load+0x768,0x7fe,30);stage_capture('xms_move')
   selector=dump(pre['DS'],0x2560,2,prefix+'request_segment.bin');capture_files.append(work/(prefix+'request_segment.bin'));requestseg=struct.unpack('<H',selector)[0];move=dump(requestseg,0x200,16,prefix+'xms_request.bin');capture_files.append(work/(prefix+'xms_request.bin'));length=struct.unpack_from('<I',move)[0];src=struct.unpack_from('<I',move,6)[0];assert length<=65536
   dump(src>>16,src&65535,length,prefix+'xms_source.bin');capture_files.append(work/(prefix+'xms_source.bin'))
   request('EXEC RUN');appendreg=wait_for(load+0x768,0x3e4,30);stage_capture('append_return');request('EXEC RUN');post=wait_for(retcs,retip,30);stage_capture('caller_return')
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));postext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   dump(pre['SS'],pre['SP'],14,prefix+'frame_after.bin');capture_files.append(work/(prefix+'frame_after.bin'))
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,raw_loaded_registers=rawreg,xms_move_registers=movereg,append_return_registers=appendreg,post_registers=post,post_extra=postext,handle=handle,record_offset=record,code_WORD=code,image_index=index,wall_WORD=wall,logical_pixel_bytes=size))
   success=True;break
'''
s=s[:a]+block+s[z:]
s=s.replace("points[(load+0x4c7,0x12a)]='guard_orientation_entry';request('EXEC BP %04X:0000012A'%(load+0x4c7))","points[(load+0x277,0x45c)]='image_record_entry';request('EXEC BP %04X:0000045C'%(load+0x277))")
s=s.replace("'orientation_calls.json'","'image_records.json'").replace('guard_orientation_runtime=True,orientation_calls=len(branch_returns)','image_record_runtime=True,image_records=len(branch_returns)')
s=s.replace('original04C7:012A whole entry-to-return orientation/frame update; whole world and DGROUP before/after','original0277:045C entry/rawpixel-load/XMSmove/append/caller snapshots; no whole-memory parity claim')
(r/'runtime_watch_image_record.py').write_text(s,encoding='utf-8')
