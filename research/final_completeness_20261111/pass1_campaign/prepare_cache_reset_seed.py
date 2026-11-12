"""OUTPUTS: retain all conventional RAM after the already verified sprite prefix.
This capture supplies replay inputs,not an extra natural reset execution.
"""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'runtime_watch_object_cache_draw.py').read_text(encoding='utf-8');needle="   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre";assert s.count(needle)==1
s=s.replace(needle,"   capture('cache_reset_RAM_seed',0,0,0xa0000)\n"+needle)
s=s.replace("'object_cache_draw_calls.json'","'cache_reset_seed_calls.json'").replace('object_cache_draw_runtime=True,object_cache_draw_calls=len(branch_returns)','cache_reset_seed_capture=True,seed_calls=len(branch_returns)')
s=s.replace('runtime_tests=1 if success else 0','runtime_tests=0')
s=s.replace('original0768:04D8 whole cache call then native0156:05DE first sprite draw with four65536B VGA planes; one draw,not full gameplay/global parity','data-only conventionalRAM seed after same original04D8/0156:05DE prefix; no native reset invocation,no added native scenario')
(r/'runtime_watch_cache_reset_seed.py').write_text(s,encoding='utf-8')
