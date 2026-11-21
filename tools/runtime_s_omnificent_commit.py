import sys,json
sys.path.insert(0,'work');import runtime_probe as rp
P={'session_id':'ses-1'};v=json.loads((rp.out/'omnificent_commit_pending.json').read_text());a=v['registers']['result'];assert int(a['instruction_pointer'],16)==0x215d and int(a['general']['eax'],16)&255==0;v['code']=rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['cs'],'offset':'0x0000215D'},'length':4});v['step']=rp.rpc('execution.step',{**P,'mode':'into'});op=v['step']['result'].get('operation_id')
if op:v['wait']=rp.rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':1000})
v['after_registers']=rp.rpc('state.get_registers',P);v['after_flag']=rp.rpc('memory.read',{**P,'address':{'space':'segmented','segment':a['segments']['ss'],'offset':'0x00004153'},'length':1});(rp.out/'omnificent_native_commit.json').write_text(json.dumps(v,indent=2))
