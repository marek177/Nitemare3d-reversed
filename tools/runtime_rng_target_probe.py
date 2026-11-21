"""Bounded original-game probe; preserve operation handles and every RPC."""
from pathlib import Path
import json,base64,struct,time,sys
import runtime_probe as rp
R=rp.root;O=rp.out;spec=json.loads((O/'run_config.json').read_text());pid=int(Path(spec['pid_file']).read_text());c=json.loads((R/'work/runtime/palette_control.json').read_text());P={'session_id':c['session_id']};base=c['loadbase'];DS=base+0x2771
ctl=Path(spec['control_file']);st=json.loads(ctl.read_text()) if ctl.exists() else {'phase':'search','operation_id':None,'pending':None,'observations':0}
sites={r['site'] for r in json.loads((R/'outputs/rng_targets_20261031/RNG_target_conditions.json').read_text())['records']}
def rpc(method,args=None):
    r=rp.rpc(method,args);assert rp.last_server_pid==pid,'Wrong live pipe server'
    if 'error' in r:raise RuntimeError(json.dumps(r['error']))
    return r
def save():
    t=ctl.with_suffix('.new');t.write_text(json.dumps(st,indent=2));t.replace(ctl)
def mem(s,o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{s:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
def regs():return rpc('state.get_registers',P)['result']
def capture(r):
    assert int(r['segments']['ds'],16)==DS
    sp=int(r['general']['esp'],16)&65535;bp=int(r['general']['ebp'],16)&65535;ss=int(r['segments']['ss'],16)
    reads={'state':mem(DS,0x24b8,4),'clock':mem(DS,0x81e,4),'counter':mem(DS,0x4540,4),'flags':mem(DS,0x3f50,2),'mode':mem(DS,0x3cd4,4),'omnificent':mem(DS,0x4153,1),'player_tiles':mem(DS,0x415e,4),'N':mem(DS,0x41af,1),'stack':mem(ss,sp,32),'frame':mem(ss,bp,32)}
    return {'registers':r,'reads':reads,'state':int.from_bytes(data(reads['state']),'little'),'clock':int.from_bytes(data(reads['clock']),'little')}
def bp(seg,off):return rpc('breakpoints.create',{**P,'kind':'execution','address':{'space':'segmented','segment':f'0x{seg:04X}','offset':f'0x{off:08X}'},'once':True})
deadline=time.monotonic()+float(sys.argv[1] if len(sys.argv)>1 else 25)
while time.monotonic()<deadline:
    status=rpc('session.status',P)['result']
    if status['state']=='stopped':
        r=regs();cs=int(r['segments']['cs'],16);ip=int(r['instruction_pointer'],16);pc=f'{cs-base:04X}:{ip:04X}'
        if not st['pending'] and pc in spec.get('stop_at_pcs',[]):
            record={'pc':pc,'snapshot':capture(r),'scope':'Boundary sentinel, not a target hit. Preserve before starting another native level/domain.'};(O/'rng_search_sentinel.json').write_text(json.dumps(record,indent=2));st['phase']='sentinel';st['operation_id']=None;save();break
        if st['pending'] and (cs,ip)==(st['pending']['cs'],st['pending']['return_ip']):
            before=st['pending']['before'];after=capture(r);expected=(before['state']*214013+2531011)&0xffffffff
            events=rpc('trace.read',{**P,'cursor':None,'limit':500});rpc('trace.stop',P)
            valid=after['state']==expected and (int(r['general']['eax'],16)&65535)==((expected>>16)&32767) and (int(r['general']['esp'],16)&65535)==st['pending']['SP']
            record={'site':st['pending']['site'],'before':before,'after':after,'expected_state':expected,'LCG_AX_and_wrapper_stack_verified':valid,'trace':events,'scope':spec.get('scope','Original naturally reached CALL under documented input/file-availability scenario; no executable, actor, coordinates or RNG writes by test; not stock whole-game/every-IRQ/global-domain coverage')}
            path=O/f'target_observation_{st["observations"]:04d}.json';path.write_text(json.dumps(record,indent=2));st['observations']+=1;st['pending']=None;st['phase']='observed' if valid else 'attention';save();assert valid,'First divergence preserved';break
        if pc in sites:
            code=mem(cs,ip,5);assert data(code)==bytes.fromhex('9aa001')+struct.pack('<H',base+0xfba),'Runtime FAR target must include actual MZ loadbase relocation'
            before=capture(r);frame=data(before['reads']['frame']);si=int(r['general']['esi'],16)&65535;es=int(r['segments']['es'],16)
            if pc=='0201:0468':before['record']=mem(DS,si,32);before['descriptor']=mem(DS,int(r['general']['edi'],16)&65535,16)
            elif pc=='0AEA:03D6':before['record']=mem(es,si,32);before['descriptor']=mem(DS,int(r['general']['edi'],16)&65535,16)
            elif pc.startswith('04C7:'):
                off,seg=struct.unpack_from('<HH',frame,6);before['record']=mem(seg,off,32);before['record_address']=f'{seg:04X}:{off:04X}'
                if pc=='04C7:0C37':
                    index=struct.unpack_from('<H',data(before['record']),8)[0];before['referenced_object']=mem(base+0x21fd,(6+28*index)&65535,28)
            elif pc.startswith('083D:') and pc not in ('083D:1698','083D:16A7'):
                off,seg=struct.unpack_from('<HH',frame,10);before['descriptor']=mem(seg,off,48)
            trace=rpc('trace.start',{**P,'detail':'long','instruction_count':100})
            ret=bp(cs,ip+5);st['pending']={'site':pc,'cs':cs,'return_ip':ip+5,'SP':int(r['general']['esp'],16)&65535,'before':before,'code':code,'return_breakpoint':ret};save()
        st['operation_id']=rpc('execution.continue',P)['result']['operation_id'];save()
    elif status['state']!='running':raise RuntimeError('Unexpected state; preserve same session: '+json.dumps(status))
    assert st['operation_id'],'Running operation not owned; preserve'
    result=rpc('execution.wait',{**P,'operation_id':st['operation_id'],'timeout_ms':5000})['result']
    if result.get('state')=='stopped':st['operation_id']=None;save();continue
    # Keep one live continuation through observation timeouts. Periodic debugger
    # pauses distort clock context and incur expensive console transitions.
    if not st['pending'] and time.monotonic()>=deadline:
        pause=rpc('execution.pause',P);pause_op=pause.get('result',{}).get('operation_id')
        if pause_op:rpc('execution.wait',{**P,'operation_id':pause_op,'timeout_ms':1000})
        status=rpc('session.status',P)['result']
        if status['state']=='stopped':st['operation_id']=None;save()
save();print(json.dumps({'phase':st['phase'],'observations':st['observations'],'operation_id':st['operation_id'],'pending_return':bool(st['pending'])}))
