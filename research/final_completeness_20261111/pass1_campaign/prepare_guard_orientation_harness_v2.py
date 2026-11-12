"""python prepare_guard_orientation_harness_v2.py OUTPUTS; capture indirect near-DS frame bank."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_guard_orientation.py').read_text(encoding='utf-8')
needle="   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC RUN');post=wait_for(retcs,retip,30)"
insert="""   world_before=(work/(prefix+'world_before.bin')).read_bytes();dgroup_before=(work/(prefix+'dgroup_before.bin')).read_bytes();actor_class=world_before[actor+4];descriptor=struct.unpack_from('<H',dgroup_before,0x3d22+8*actor_class)[0];assert descriptor+0x34<=65536
   dump(pre['DS'],descriptor,0x34,prefix+'descriptor_before.bin');capture_files.append(work/(prefix+'descriptor_before.bin'));captures.append(('descriptor',pre['DS'],descriptor,0x34))
"""
assert needle in s;s=s.replace(needle,insert+needle)
s=s.replace('force_word=force))','force_word=force,descriptor_offset=descriptor))')
(r/'runtime_watch_guard_orientation_v2.py').write_text(s,encoding='utf-8')
