"""Derive native whole door-interaction capture from frozen sparse harness."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_validator_branches.py').read_text(encoding='utf-8')
start=s.index("  if stage in ('validator_allow_branch','validator_block_branch'):")
end=s.index('  if stage:\n',start)
block='''  if stage=='door_interaction_entry':
   prefix='interaction_00_';pre=reg
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));ext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   frame=dump(pre['SS'],pre['SP'],10,prefix+'frame_before.bin');capture_files.append(work/(prefix+'frame_before.bin'));retip,retcs,door,doorseg,command=struct.unpack('<5H',frame)
   captures=[('world',load+0x21fd,0,0x573e),('dgroup',pre['DS'],0,0xe030),('frame',pre['SS'],pre['SP'],10)]
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_before.bin');capture_files.append(work/(prefix+name+'_before.bin'))
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC RUN');post=wait_for(retcs,retip,30)
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));postext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_after.bin');capture_files.append(work/(prefix+name+'_after.bin'))
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,post_registers=post,post_extra=postext,door_offset=door,door_segment=doorseg,command_word=command))
   success=True;break
'''
s=s[:start]+block+s[end:]
old="    for ip,label in [(0x27e,'validator_block_branch'),(0x41c,'validator_allow_branch')]:\n     points[(load+0x4c7,ip)]=label;request('EXEC BP %04X:%08X'%(load+0x4c7,ip))"
assert old in s;s=s.replace(old,"    points[(load,0x598)]='door_interaction_entry';request('EXEC BP %04X:00000598'%load)")
s=s.replace('validator_branch_runtime=True,branch_returns=len(branch_returns),observed_AL_results=sorted(results)','door_interaction_runtime=True,interaction_calls=len(branch_returns)')
s=s.replace("'branch_returns.json'","'interaction_calls.json'")
s=s.replace('original0254 allowed/blocked return branches, not whole entry-to-return snapshots','original0000:0598 whole entry-to-return interaction; whole world and DGROUP before/after')
(r/'runtime_watch_door_interaction.py').write_text(s,encoding='utf-8')
