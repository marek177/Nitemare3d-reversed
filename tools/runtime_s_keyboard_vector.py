import sys,json
sys.path.insert(0,'work');import runtime_probe as rp
c=json.loads((rp.root/'work/runtime/palette_control.json').read_text());P={'session_id':'ses-1'};s=rp.rpc('session.status',P);assert rp.last_server_pid==21868 and s['result']['state']=='stopped';v={'status':s,'loadbase':c['loadbase']}
for name,seg,off,n in [('vector09',0,0x24,4),('prior_handler',c['loadbase']+0x2771,0x3f52,4),('installed_flag',c['loadbase']+0x2771,0xb3e,1),('install_code',c['loadbase']+0x6b0,0x134,88)]:v[name]=rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{seg:04X}','offset':f'0x{off:08X}'},'length':n})
(rp.out/'keyboard_vector_endpoint.json').write_text(json.dumps(v,indent=2))
