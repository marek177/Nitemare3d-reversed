import json,base64
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());DS=c['loadbase']+0x2771;P={'session_id':c['session_id']};pid=int(Path(json.loads((O/'run_config.json').read_text())['pid_file']).read_text())
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==pid and 'result' in x;return x
def read():return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{DS:04X}','offset':'0x00004144'},'length':16})
assert rpc('session.status',P)['result']['state']=='stopped';before=read();b=base64.b64decode(before['result']['data_base64']);assert b[8]==1;write=rpc('memory.write',{**P,'address':{'space':'segmented','segment':f'0x{DS:04X}','offset':'0x0000414C'},'data_base64':'AA=='});after=read();expected=bytearray(b);expected[8]=0;assert base64.b64decode(after['result']['data_base64'])==expected
for o in (0x28ae,0x28be,0x28c1):rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{c["loadbase"]+0xd29:04X}','offset':f'0x{o:08X}'},'once':True})
(O/'menu_input_fixture.json').write_text(json.dumps({'before':before,'write':write,'after':after,'scope':'Temporary input-option byte8 disable for menu; restore1 at28AE before nativeDemo cache. No causal mouse-driver diagnosis claimed.'},indent=2));p=O/'level1_fixture_control.json';st=json.loads(p.read_text());st['prior_wait_operation']=st['operation_id'];st['operation_id']=None;st['phase']='cache_restore';st['started']=False;p.write_text(json.dumps(st,indent=2))
