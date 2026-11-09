import json
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;p=O/'run_config.json';spec=json.loads(p.read_text());pid=int(Path(spec['pid_file']).read_text());c=json.loads((R/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};r=rp.rpc('session.status',P);assert rp.last_server_pid==pid and r['result']['state']=='stopped';x=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{c["loadbase"]+0xd29:04X}','offset':'0x000026F4'},'once':True});assert rp.last_server_pid==pid and 'result' in x;spec['stop_at_pcs']=['0D29:26F4'];p.write_text(json.dumps(spec,indent=2));(O/'search_boundary_arm.json').write_text(json.dumps(x,indent=2))
