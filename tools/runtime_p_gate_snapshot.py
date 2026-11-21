import json
from pathlib import Path
import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};B=c['loadbase'];s=rp.rpc('session.status',P);assert rp.last_server_pid==50760 and s['result']['state']=='stopped'
def read(seg,off,n):return rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{seg:04X}','offset':f'0x{off:08X}'},'length':n})
v={'status_before':s,'gate_code':read(B+0x83d,0x29ca,0x2ad7-0x29ca),'header_buffer':read(B+0x2771,0x3638,54),'status_after':rp.rpc('session.status',P)};assert v['status_after']['result']['state_revision']==s['result']['state_revision'];(rp.out/'gate_endpoint_snapshot.json').write_text(json.dumps(v,indent=2))
