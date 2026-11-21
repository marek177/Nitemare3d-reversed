"""Read-only verifier for bounded original DOSBox actor gate observations."""
from pathlib import Path
import json,base64,hashlib,sys
def verify(directory):
    D=Path(directory);records=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];by_id={r['response']['id']:r for r in records};assert len(by_id)==len(records)
    def dec(response):return base64.b64decode(response['result']['data_base64'])
    def correlated(x):
        if isinstance(x,dict):
            if 'jsonrpc' in x and 'id' in x:
                r=by_id[x['id']];assert r['response']==x and r['server_pid']==41260
                if r['request']['method']=='memory.read' and 'result' in x:
                    raw=dec(x);assert len(raw)==r['request']['params']['length']==x['result']['byte_count'];assert hashlib.sha256(raw).hexdigest()==x['result']['sha256']
            for v in x.values():correlated(v)
        elif isinstance(x,list):
            for v in x:correlated(v)
    def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==41260 and x['response'].get('result')==r for x in records)
    def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
    baseline=json.loads((D/'state7_RNG_gate_observation.json').read_text());fixture=json.loads((D/'state7_RNG_gate_flag0.json').read_text());restoration=json.loads((D/'global_4153_fixture.json').read_text());context=json.loads((D/'current_context.json').read_text())
    for x in [baseline,fixture,restoration,context]:correlated(x)
    a=baseline['events'][0];b,c=fixture['events'];CS=0x823+0x4c7
    for e in [a,b,c]:
        s=e['before'];reg(s['registers']);assert dec(s['actor'])[11]==7;assert int.from_bytes(dec(s['counter']),'little')==13;assert int.from_bytes(dec(s['RNG']),'little')==1
        frame=dec(s['frame']);off=int.from_bytes(frame[6:8],'little');seg=int.from_bytes(frame[8:10],'little');assert s['actor_address']==f'{seg:04X}:{off:04X}'
        for name,expected in [('actor',(seg,off)),('global_4153',(0x2f94,0x4153)),('RNG',(0x2f94,0x24b8)),('counter',(0x2f94,0x4540))]:
            addr=by_id[s[name]['id']]['request']['params']['address'];assert (int(addr['segment'],16),int(addr['offset'],16))==expected
    assert pc(a['before']['registers'])==(CS,0xf60) and dec(a['before']['global_4153'])==b'\x01'
    assert not int(a['after_cmp']['flags'],16)&0x40 and pc(a['after_JNE'])==(CS,0x12b0)
    assert pc(b['before']['registers'])==(CS,0xf60) and dec(b['before']['global_4153'])==b'\x00'
    assert int(b['after_cmp']['flags'],16)&0x40 and pc(b['after_JNE'])==(CS,0xf69)
    assert pc(c['before']['registers'])==(CS,0xf7b) and int(c['before']['registers']['general']['eax'],16)&255==0
    assert int(c['after_OR']['flags'],16)&0x40 and pc(c['after_JE'])==(CS,0x12b0)
    for e in [a,b,c]:
        for k,v in e.items():
            if k.startswith('after_') and isinstance(v,dict):reg(v)
    assert b['before']['actor_address']==c['before']['actor_address']
    assert a['before']['actor_address']!=b['before']['actor_address']
    assert dec(restoration['original'])==dec(restoration['restore']['after'])==b'\x01'
    global_writes=[];bios_writes=0
    for r in records:
        if r['request']['method']!='memory.write':continue
        p=r['request']['params'];s=int(p['address']['segment'],16);o=int(p['address']['offset'],16);data=base64.b64decode(p['data_base64'])
        if s==0x40:bios_writes+=1
        else:assert (s,o,len(data))==(0x2f94,0x4153,1);global_writes.append(data.hex())
    assert sorted(global_writes)==['00','01']
    assert context['status']['result']['state']=='stopped' and pc(context['registers']['result'])==(CS,0x12b0)
    assert context['words']['RNG']==[1,0] and context['words']['world'][:2]==[13,0]
    expected={'0201:0468','04C7:09F6','04C7:0C37','083D:0490','083D:049C','083D:04AC','083D:1698','083D:16A7','083D:18F2','083D:1B3C','0AEA:03D6'}
    live=context['breakpoints']['result']['breakpoints'];assert len(live)==11
    assert {f'{int(x["address"]["segment"],16)-0x823:04X}:{int(x["address"]["offset"],16):04X}' for x in live}==expected
    assert all(x['enabled'] and not x['once'] for x in live)
    result={'status':'VERIFIED_BOUNDED_ORIGINAL_RUNTIME_GATES','natural_case':{'actor':a['before']['actor_address'],'global_4153':1,'JNE_target':'04C7:12B0'},'controlled_case':{'actor':b['before']['actor_address'],'global_4153':0,'first_JNE_fallthrough':'04C7:0F69','helper_AL':0,'JE_target':'04C7:12B0'},'paired_same_actor_A_B':False,'global_byte_restored':True,'global_data_writes':global_writes,'BIOS_queue_write_calls':bios_writes,'RNG_state_writes_by_test':0,'target_RNG_invocations_observed':0,'render_counter':13,'raw_RPC_correlated':True,'final_revision':context['registers']['result']['state_revision'],'final_logical_PC':'04C7:12B0','all_11_target_conditions_runtime_closed':False}
    return result
if __name__=='__main__':print(json.dumps(verify(sys.argv[1]),indent=2))
