import json
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());B=c['loadbase'];P={'session_id':c['session_id']};pid=int(Path(json.loads((O/'run_config.json').read_text())['pid_file']).read_text());proof=[]
for row in json.loads((R/'outputs/wall_sort_20261106/remaining_RNG_targets.json').read_text())['records']:
 s,o=[int(x,16) for x in row['site'].split(':')];x=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{B+s:04X}','offset':f'0x{o:08X}'},'once':False});assert rp.last_server_pid==pid and 'result' in x;proof.append({'site':row['site'],'response':x})
for s,o in [(0xd29,0x28c9),(0xd29,0x26f4),(0xd29,0x97d),(0x6b0,0x2e0)]:
 x=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{B+s:04X}','offset':f'0x{o:08X}'},'once':True});assert rp.last_server_pid==pid and 'result' in x
(O/'target_breakpoints.json').write_text(json.dumps(proof,indent=2))
