"""python prepare_guard_facing_integration.py OUTPUTS; extend shared-world movement replay."""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'audit_replay_guard_with_validator.py').read_text(encoding='utf-8')
s=s.replace("if name!='collision':u.mem_write(addr,b'\\xcb')","if name not in ('collision','motion'):u.mem_write(addr,b'\\xcb')")
needle=" calls+=['motion','lookup'];"
replacement=" expected_guard[0x11]=(4 if sy>0 else 0 if sy<0 else expected_guard[0x11]) if sx==0 else (3 if sy>0 else 1 if sy<0 else 2) if sx>0 else (5 if sy>0 else 7 if sy<0 else 6)\n calls+=['motion','lookup'];"
assert needle in s;s=s.replace(needle,replacement)
s=s.replace('integrated original0422 plus original0254 validator, no collision stub; six other callees mocked','integrated original0422 plus original0254 validator and original00B0 facing setter; five other callees mocked')
(r/'audit_replay_guard_with_facing.py').write_text(s,encoding='utf-8')
