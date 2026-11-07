"""Observe an original state7 actor gate without mutating the game."""
import json,base64,struct,time,sys
import runtime_probe as rp
R=rp.root;O=rp.out;c=json.loads((R/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};base=c['loadbase'];CS=base+0x4c7;DS=base+0x2771;pid=int((R/'work/runtime/bsf_s_pid.txt').read_text());case=sys.argv[1] if len(sys.argv)>1 else 'baseline';assert case in ('baseline','flag0');ctl=R/'work/runtime'/('rng_s_slot26_gate_control.json' if case=='baseline' else 'rng_s_native_gate_flag0_control.json');st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'setup','operation_id':None,'events':[],'case':case}
def rpc(m,p):
    r=rp.rpc(m,p);assert rp.last_server_pid==pid and 'result' in r;return r
def save():ctl.write_text(json.dumps(st,indent=2))
def regs():return rpc('state.get_registers',P)['result']
def mem(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def raw(x):return base64.b64decode(x['result']['data_base64'])
def bp(off):return rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{CS:04X}','offset':f'0x{off:08X}'},'once':True})
def step():
    r=rpc('execution.step',{**P,'mode':'into'});op=r.get('result',{}).get('operation_id')
    if op:rpc('execution.wait',{**P,'operation_id':op,'timeout_ms':1000})
    assert rpc('session.status',P)['result']['state']=='stopped';return regs()
def snap(r):
    bpv=int(r['general']['ebp'],16)&65535;frame=mem(int(r['segments']['ss'],16),bpv,20);v=raw(frame);off,seg=struct.unpack_from('<HH',v,6);objoff,objseg=struct.unpack_from('<HH',v,10)
    return {'registers':r,'frame':frame,'actor_address':f'{seg:04X}:{off:04X}','actor':mem(seg,off,26),'object_address':f'{objseg:04X}:{objoff:04X}','object':mem(objseg,objoff,28),'global_4153':mem(DS,0x4153,1),'RNG':mem(DS,0x24b8,4),'counter':mem(DS,0x4540,4)}
def finish(reason):
    st['phase']='complete';st['result']=reason;st['operation_id']=None;save();(O/('state7_slot26_gate_observation.json' if case=='baseline' else 'state7_RNG_gate_flag0.json')).write_text(json.dumps(st,indent=2))
deadline=time.monotonic()+25
while time.monotonic()<deadline and st['phase']!='complete':
    status=rpc('session.status',P)['result']
    if status['state']=='running':
        assert st['operation_id'];w=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
        if w.get('state')=='stopped':st['operation_id']=None;save()
        continue
    assert status['state']=='stopped';r=regs();cs=int(r['segments']['cs'],16);ip=int(r['instruction_pointer'],16)
    if st['phase']=='setup':st['breakpoint']=bp(0xf60);st['phase']='global_gate';save()
    elif st['phase']=='global_gate' and (cs,ip)==(CS,0xf60):
        s=snap(r)
        if int(s['actor_address'].split(':')[1],16)!=10482:
            st['breakpoint']=bp(0xf60);st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save();continue
        assert raw(s['actor'])[11]==7;assert raw(mem(CS,0xf60,5))==bytes.fromhex('803e534100');st['events'].append({'gate':'global_4153','before':s})
        a=step();b=step();st['events'][-1]['after_cmp']=a;st['events'][-1]['after_JNE']=b
        if int(b['instruction_pointer'],16)==0x12b0:finish('RNG initializer skipped: DS4153 nonzero; original JNE taken');break
        assert int(b['instruction_pointer'],16)==0xf69;st['breakpoint']=bp(0xf7b);st['phase']='helper_gate';save()
    elif st['phase']=='helper_gate' and (cs,ip)==(CS,0xf7b):
        s=snap(r);st['events'].append({'gate':'helper_AL','before':s});a=step();b=step();st['events'][-1]['after_OR']=a;st['events'][-1]['after_JE']=b
        if int(b['instruction_pointer'],16)==0x12b0:finish('RNG initializer skipped: helper AL zero; original OR/JE taken');break
        assert int(b['instruction_pointer'],16)==0xf81
        seq=[step(),step(),step(),step()];st['events'][-1]['mode_guard_steps']=seq
        if int(seq[-1]['instruction_pointer'],16)==0xffc:finish('RNG initializer skipped: actor mode+0A differs from3; original JNE taken');break
        assert int(seq[-1]['instruction_pointer'],16)==0xf8e;finish('All three gates passed; stopped before original initializer call, target runtime probe should capture next draw');break
    elif st['phase']!='setup':
        st['unexpected_stop']={'registers':r,'phase':st['phase']};save();raise RuntimeError('Unexpected stop; preserve original session and inspect')
    st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
save();print(json.dumps({'phase':st['phase'],'operation_id':st['operation_id'],'result':st.get('result')}))
