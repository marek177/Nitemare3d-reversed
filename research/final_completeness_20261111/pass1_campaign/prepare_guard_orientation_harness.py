"""python prepare_guard_orientation_harness.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_door_interaction.py').read_text(encoding='utf-8')
s=s.replace('door_interaction_entry','guard_orientation_entry').replace("'interaction_00_'","'orientation_00_'")
s=s.replace("10,prefix+'frame_before.bin'","14,prefix+'frame_before.bin'").replace("retip,retcs,door,doorseg,command=struct.unpack('<5H',frame)","retip,retcs,guard,gseg,actor,aseg,force=struct.unpack('<7H',frame)")
s=s.replace("('frame',pre['SS'],pre['SP'],10)","('frame',pre['SS'],pre['SP'],14)")
s=s.replace('door_offset=door,door_segment=doorseg,command_word=command','guard_offset=guard,guard_segment=gseg,actor_offset=actor,actor_segment=aseg,force_word=force')
s=s.replace("   if stage=='map_load_return':\n    points[(load,0x598)]='guard_orientation_entry';request('EXEC BP %04X:00000598'%load)","   if stage=='game_start_entry':\n    points[(load+0x4c7,0x12a)]='guard_orientation_entry';request('EXEC BP %04X:0000012A'%(load+0x4c7))")
s=s.replace("'interaction_calls.json'","'orientation_calls.json'").replace('door_interaction_runtime=True,interaction_calls=len(branch_returns)','guard_orientation_runtime=True,orientation_calls=len(branch_returns)')
s=s.replace('original0000:0598 whole entry-to-return interaction','original04C7:012A whole entry-to-return orientation/frame update')
(r/'runtime_watch_guard_orientation.py').write_text(s,encoding='utf-8')
