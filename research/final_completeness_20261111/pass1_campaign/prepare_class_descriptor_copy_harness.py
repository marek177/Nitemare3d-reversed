"""python prepare_class_descriptor_copy_harness.py OUTPUTS
Capture original90BYTE header copy for actor-class8, no injected game data.
"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_guard_orientation_v2.py').read_text(encoding='utf-8');a=s.index("  if stage=='guard_orientation_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='class_copy_entry':
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));ext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   probe=dump(reg['SS'],ext['BP']-0x18,0x18,'class_probe_%02d.bin'%len(branch_returns));slot=struct.unpack_from('<H',probe,0x16)[0]
   if slot!=0x3d22+8*8:request('EXEC RUN');continue
   prefix='class_copy_00_';pre=reg;ds=pre['DS'];source=(ext['BP']-0x74)&65535
   group=dump(ds,0,0xe030,prefix+'dgroup_before.bin');capture_files.append(work/(prefix+'dgroup_before.bin'));destination=struct.unpack_from('<H',group,slot)[0];assert destination+90<=65536
   captures=[('world',load+0x21fd,0,0x573e),('source_header',pre['SS'],source,90),('destination',ds,destination,90),('locals',pre['SS'],ext['BP']-0x18,0x18)]
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_before.bin');capture_files.append(work/(prefix+name+'_before.bin'))
   request('EXEC BP %04X:000009D7'%(load+0x277));request('EXEC RUN');post=wait_for(load+0x277,0x9d7,30)
   response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));postext=dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   captures.append(('dgroup',ds,0,0xe030))
   for name,seg,off,length in captures:
    dump(seg,off,length,prefix+name+'_after.bin');capture_files.append(work/(prefix+name+'_after.bin'))
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,post_registers=post,post_extra=postext,slot_offset=slot,source_offset=source,destination_offset=destination))
   success=True;break
'''
s=s[:a]+block+s[z:]
s=s.replace("points[(load+0x4c7,0x12a)]='guard_orientation_entry';request('EXEC BP %04X:0000012A'%(load+0x4c7))","points[(load+0x277,0x9c1)]='class_copy_entry';request('EXEC BP %04X:000009C1'%(load+0x277))")
s=s.replace("'orientation_calls.json'","'class_copies.json'").replace('guard_orientation_runtime=True,orientation_calls=len(branch_returns)','class_descriptor_copy_runtime=True,class_copies=len(branch_returns)')
s=s.replace('original04C7:012A whole entry-to-return orientation/frame update','original0277:09C1..09D7 class8 descriptor copy block, not whole map-loader function')
(r/'runtime_watch_class_descriptor_copy.py').write_text(s,encoding='utf-8')
