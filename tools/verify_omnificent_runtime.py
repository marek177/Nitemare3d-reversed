"""Read-only proof checker; no live debugger or source-game writes."""
import json,base64,hashlib,struct,sys
from pathlib import Path
def verify(directory,require_c37=False):
    D=Path(directory);raw=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];byid={r['response']['id']:r for r in raw};assert len(raw)==len(byid);pids={r['server_pid'] for r in raw};assert len(pids)==1;pid=next(iter(pids))
    def data(r):return base64.b64decode(r['result']['data_base64'])
    def check(x):
        if isinstance(x,dict):
            if 'jsonrpc' in x and 'id' in x:
                r=byid[x['id']];assert r['response']==x and r['server_pid']==pid
                if r['request']['method']=='memory.read' and 'result' in x:
                    b=data(x);assert len(b)==r['request']['params']['length']==x['result']['byte_count'];assert hashlib.sha256(b).hexdigest()==x['result']['sha256']
            for v in x.values():check(v)
        elif isinstance(x,list):
            for v in x:check(v)
    def reg(r):assert any(v['request']['method']=='state.get_registers' and v['response'].get('result')==r for v in raw)
    def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
    manifest={x['name'].upper():x for x in json.loads((D/'input_manifest.json').read_text())};origin=json.loads((D/'config_origin_runtime.json').read_text());native=json.loads((D/'native_demo_4153_clear.json').read_text());header=json.loads((D/'DEMO_header_runtime.json').read_text())
    for v in [origin,native,header]:check(v)
    before=origin['before'];after=origin['after'];base=pc(before['registers'])[0]-0x277;DS=base+0x2771
    assert pc(before['registers'])==(base+0x277,0xce5) and pc(after['registers'])==(base+0x277,0xcea);reg(before['registers']);reg(after['registers'])
    assert data(before['buffer'])[15]==0 and data(after['buffer'])[15]==1 and hashlib.sha256(data(after['buffer'])).hexdigest()==manifest['CONFIG.SAV']['sha256']
    assert data(before['filename']).lower()==b'config.sav\0';assert struct.unpack_from('<HHH',data(before['stack']))[1:]==(0x4144,16)
    assert data(before['code'])==bytes.fromhex('9a141e')+struct.pack('<H',base+0x11ee);assert int(after['registers']['general']['eax'],16)&65535==16
    assert (int(after['registers']['general']['esp'],16)&65535)==(int(before['registers']['general']['esp'],16)&65535)
    b=native['before'];a=native['after'];reg(b['registers']);reg(a['registers']);assert pc(b['registers'])==(base+0xd29,0x28c9) and pc(a['registers'])==(base+0xd29,0x28cc)
    assert data(b['code'])==bytes.fromhex('a25341') and int(b['registers']['general']['eax'],16)&255==0
    expected=bytearray(data(b['config']));assert expected[15]==1;expected[15]=0;assert data(a['config'])==expected
    assert not int(b['registers']['flags'],16)&0x400;assert hashlib.sha256(data(b['cached_config'])).hexdigest()==manifest['CONFIG.SAV']['sha256']
    assert header['filename'].upper()=='DEMO.2' and header['file_sha256']==manifest['DEMO.2']['sha256']=='deb7fe959b6b1c9f0f7f4a793a40e0ef75873b436c715bd9f74d4ef965ac304d'
    assert header['timing_words']==[10,5,20] and header['first_record']==[0x48e0,2,26] and header['RNG_state']==1 and header['mode_words']==[1,4]
    assert data(header['reads']['timing'])==struct.pack('<HHH',10,5,20) and data(header['reads']['first_record'])==struct.pack('<HHI',0x48e0,2,26)
    writes=[r for r in raw if r['request']['method']=='memory.write']
    for r in writes:
        p=r['request']['params'];assert int(p['address']['segment'],16)==0x40 and len(base64.b64decode(p['data_base64']))==2
    observations=[]
    for path in sorted(D.glob('target_observation_*.json')):
        v=json.loads(path.read_text());check(v);b=v['before'];a=v['after'];reg(b['registers']);reg(a['registers']);s,o=(int(q,16) for q in v['site'].split(':'))
        assert pc(b['registers'])==(base+s,o) and pc(a['registers'])==(base+s,o+5)
        state=int.from_bytes(data(b['reads']['state']),'little');expected=(state*214013+2531011)&0xffffffff;assert int.from_bytes(data(a['reads']['state']),'little')==expected==v['expected_state']
        assert (int(a['registers']['general']['eax'],16)&65535)==(expected>>16)&32767
        assert (int(a['registers']['general']['esp'],16)&65535)==(int(b['registers']['general']['esp'],16)&65535)
        assert data(v['before']['reads']['omnificent'])==b'\0'
        observations.append({'site':v['site'],'before_state':state,'after_state':expected,'AX':(expected>>16)&32767,'counter':int.from_bytes(data(b['reads']['counter']),'little') if 'counter' in b['reads'] else None})
        if v['site']=='04C7:0C37':
            actor=data(b['record']);obj=data(b['referenced_object']);assert (actor[10],actor[11])==(3,7) and obj[6] in (18,19)
            f=data(b['reads']['frame']);assert struct.unpack_from('<HH',f,2)==(0xf94,base+0x4c7)
            if 'player_tiles' in b['reads']:
                px,py=struct.unpack('<hh',data(b['reads']['player_tiles']));ox,oy=struct.unpack_from('<hh',obj,16);assert abs(px-(ox>>6))<=8 and abs(py-(oy>>6))<=8
    if require_c37:assert any(x['site']=='04C7:0C37' for x in observations)
    result={'status':'VERIFIED_BOUNDED_NATIVE_CONFIG_AND_DEMO','pid':pid,'loadbase':f'{base:04X}','config_file_offset15_load_0_to1_verified':True,'native_demo_clear_1_to0_verified':True,'original_cached_config_matches_file':True,'DEMO2_header_verified':True,'debugger_gameplay_memory_writes':0,'BIOS_queue_write_calls':len(writes),'RNG_observations':observations,'full_rng_domain_or_tick_parity':False}
    return result
if __name__=='__main__':print(json.dumps(verify(sys.argv[1],'--require-c37' in sys.argv[2:]),indent=2))
