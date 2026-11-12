"""python prepare_classification_harness.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_door_interaction.py').read_text(encoding='utf-8');start=s.index("  if stage=='door_interaction_entry':");end=s.index('  if stage:\n',start)
block='''  if stage in ('tile_flags_entry','occupancy_flags_entry'):
   prefix='producer_%02d_'%len(branch_returns);pre=reg
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));ext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   captures=[('dgroup',pre['DS'],0,0xe030),('frame',pre['SS'],pre['SP']-8,12)]
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_before.bin');capture_files.append(work/(prefix+name+'_before.bin'))
   frame=(work/(prefix+'frame_before.bin')).read_bytes();retip,retcs=struct.unpack_from('<HH',frame,8)
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC RUN');post=wait_for(retcs,retip,30)
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));postext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_after.bin');capture_files.append(work/(prefix+name+'_after.bin'))
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,post_registers=post,post_extra=postext))
   for targetcs,targetip in [(retcs,retip),(pre['CS'],pre['IP'])]:
    for line in request('EXEC BPLIST'):
     m=re.match(r'^([0-9a-fA-F]+)\\. BP ([0-9a-fA-F]+):([0-9a-fA-F]+)',line)
     if m and (int(m[2],16),int(m[3],16))==(targetcs,targetip):request('EXEC BPDEL '+m[1]);break
    else:raise AssertionError('producer breakpoint missing')
   if len(branch_returns)==2:success=True;break
   request('EXEC RUN');continue
'''
s=s[:start]+block+s[end:]
old="   if stage=='map_load_return':\n    points[(load,0x598)]='door_interaction_entry';request('EXEC BP %04X:00000598'%load)"
assert old in s;s=s.replace(old,"   if stage=='game_start_entry':\n    for ip,label in [(0x1b6,'tile_flags_entry'),(0x250,'occupancy_flags_entry')]:\n     points[(load+0xf7,ip)]=label;request('EXEC BP %04X:%08X'%(load+0xf7,ip))")
s=s.replace("'interaction_calls.json'","'producer_calls.json'").replace('door_interaction_runtime=True,interaction_calls=len(branch_returns)','classification_producer_runtime=True,producer_calls=len(branch_returns)')
s=s.replace('original0000:0598 whole entry-to-return interaction; whole world and DGROUP before/after','original00F7:01B6/0250 whole entry-to-return table producers; whole DGROUP before/after')
(r/'runtime_watch_classification_producers.py').write_text(s,encoding='utf-8')
