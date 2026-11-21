import json
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());B=c['loadbase'];P={'session_id':c['session_id']};pid=int(Path(json.loads((O/'run_config.json').read_text())['pid_file']).read_text());owned=[];targets=[]
for row in json.loads((R/'outputs/target_maps_20261107/remaining_RNG_targets.json').read_text())['records']:
 s,o=[int(x,16) for x in row['site'].split(':')];r=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{B+s:04X}','offset':f'0x{o:08X}'},'once':False});assert rp.last_server_pid==pid and 'result' in r;targets.append({'site':row['site'],'response':r})
for s,o,once in [(0xd29,0x28be,True),(0xd29,0x28c1,True),(0xd29,0x28c9,True),(0xd29,0x2696,True),(0xd29,0x26b7,False),(0xd29,0x26bc,False),(0xd29,0x26c5,False),(0xd29,0x26ca,False),(0xd29,0x26e6,True),(0xd29,0x26f4,True),(0xd29,0x97d,True),(0x6b0,0x2e0,True)]:
 r=rp.rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{B+s:04X}','offset':f'0x{o:08X}'},'once':once});assert rp.last_server_pid==pid and 'result' in r;owned.append(r['result']['breakpoint_id'])
(O/'native_load_arm.json').write_text(json.dumps({'owned_bps':owned,'target_bps':targets},indent=2))
