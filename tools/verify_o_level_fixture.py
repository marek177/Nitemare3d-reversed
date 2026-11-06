import json,base64,struct,hashlib,argparse
from pathlib import Path
def verify(folder,map1,demo1):
 D=Path(folder);v=json.loads((D/'level1_fixture_observation.json').read_text());ui=json.loads((D/'menu_input_fixture.json').read_text());identity=json.loads((D/'startup_identity.json').read_text());B=identity['loadbase'];pid=identity['server_pid'];DS=B+0x2771;rows=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];raw={r['response']['id']:r for r in rows};assert len(raw)==len(rows)
 def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
 def check(x):
  if isinstance(x,dict):
   if 'jsonrpc' in x and 'id' in x:
    r=raw[x['id']];assert r['response']==x and r['server_pid']==pid
    if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
   for y in x.values():check(y)
  elif isinstance(x,list):
   for y in x:check(y)
 def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==pid and x['response'].get('result')==r for x in rows)
 def addr(x,s,o,n):
  q=raw[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
 def pc(r):return int(r['segments']['cs'],16)-B,int(r['instruction_pointer'],16)
 check(v);check(ui);assert v['phase']=='header' and v['operation_id'] is None
 for x in (ui['before'],ui['after']):addr(x,DS,0x4144,16)
 before=data(ui['before']);expected=bytearray(before);assert before[8]==1;expected[8]=0;assert data(ui['after'])==expected
 restore=v['menu_option_restore'];reg(restore['registers']);assert pc(restore['registers'])==(0xd29,0x28ae);assert data(restore['before'])==expected and data(restore['after'])==before
 cb=v['native_cache_before'];ca=v['native_cache_after'];reg(cb['registers']);reg(ca['registers']);assert pc(cb['registers'])==(0xd29,0x28be) and pc(ca['registers'])==(0xd29,0x28c1);r=cb['registers'];di=int(r['general']['edi'],16)&65535;ss=int(r['segments']['ss'],16);assert int(r['segments']['es'],16)==ss==DS and di==(int(r['general']['ebp'],16)-24)&65535 and int(r['general']['esi'],16)&65535==0x4144 and int(r['general']['ecx'],16)==4 and int(r['flags'],16)&0x400==0
 addr(cb['source'],DS,0x4144,16);addr(cb['destination'],ss,di,16);addr(ca['destination'],ss,di,16);assert data(cb['source'])==data(ca['destination'])==before and int(ca['registers']['general']['ecx'],16)==0 and int(ca['registers']['general']['edi'],16)&65535==(di+16)&65535 and int(ca['registers']['general']['esi'],16)&65535==0x4154;assert data(cb['code'])==bytes.fromhex('f366a5')
 cl=v['clear_before'];cr=v['clear_after'];reg(cl['registers']);reg(cr['registers']);assert pc(cl['registers'])==(0xd29,0x28c9) and pc(cr['registers'])==(0xd29,0x28cc) and data(cl['code'])==bytes.fromhex('a25341');a=bytearray(data(cl['config']));assert a[15]==1;a[15]=0;assert data(cr['config'])==a
 f=v['argument_fixture'];reg(f['registers']);assert pc(f['registers'])==(0xd29,0x26f4);sp=int(f['registers']['general']['esp'],16)&65535;ss=int(f['registers']['segments']['ss'],16);addr(f['stack_before'],ss,sp,16);addr(f['stack_after'],ss,sp,16);a=bytearray(data(f['stack_before']));assert struct.unpack_from('<3H',a)==(B+0xd29,10,1);a[2:4]=bytes(2);assert data(f['stack_after'])==a and data(f['code'])==bytes.fromhex('0ee863e2')
 sb=v['store_before'];sa=v['store_after'];reg(sb['registers']);reg(sa['registers']);assert pc(sb['registers'])==(0xd29,0x97d) and pc(sa['registers'])==(0xd29,0x980) and data(sb['code'])==bytes.fromhex('a36c62') and struct.unpack_from('<HH',data(sb['frame']),6)==(0,1) and int(sb['registers']['general']['eax'],16)&65535==0;a=bytearray(data(sb['globals']));a[2:4]=bytes(2);assert data(sa['globals'])==a
 allowed={ui['write']['id'],restore['write']['id'],f['write']['id']};seen=set();bios=0
 for r in rows:
  if r['request']['method']!='memory.write':continue
  p=r['request']['params'];seg=int(p['address']['segment'],16);o=int(p['address']['offset'],16);b=base64.b64decode(p['data_base64']);assert 'result' in r['response']
  if seg==0x40:assert len(b)==2 and (o==0x1c or 0x1e<=o<0x100 and o%2==0);bios+=1
  else:
   assert r['response']['id'] in allowed;seen.add(r['response']['id'])
   if r['response']['id']==f['write']['id']:assert (seg,o,b)==(ss,sp+2,bytes(2))
   else:assert seg==DS and o==0x414c and b==(b'\0' if r['response']['id']==ui['write']['id'] else b'\1')
 assert seen==allowed
 h=v['header'];reg(h['registers']);assert pc(h['registers'])==(0x6b0,0x2e0)
 for k,o,n in [('episode_level',0x626a,4),('filename',0x629c,16),('RNG',0x24b8,4),('counter',0x4540,4),('header_words',0x455c,6),('map_header',0xd30c,514)]:addr(h[k],DS,o,n);assert h[k]['result']['state_revision']==h['registers']['state_revision']
 manifest=json.loads((D/'input_manifest.json').read_text());game=Path(map1).parent
 for item in manifest:
  asset=(game/item['name']).read_bytes();assert len(asset)==item['bytes'] and hashlib.sha256(asset).hexdigest()==item['sha256']
 assert before==(game/'CONFIG.SAV').read_bytes()
 m=Path(map1).read_bytes();d=Path(demo1).read_bytes();assert hashlib.sha256(m).hexdigest()=='0f36888ef9df05004c77f920d810780e2023853b7ab6575dc6d910a871ae59f0';assert data(h['map_header'])==m[:514] and struct.unpack('<HH',data(h['episode_level']))==(1,0) and data(h['filename']).split(b'\0')[0]==b'demo.1' and data(h['header_words'])==d[:6] and int.from_bytes(data(h['RNG']),'little')==1 and int.from_bytes(data(h['counter']),'little')==2
 return {'status':'VERIFIED_RUNTIME_RAW_RPC_CORRELATED','server_pid':pid,'loadbase':f'{B:04X}','episode':1,'level_index':0,'temporary_input_flag_restored_before_native_cache':True,'native_config_cache_all16_bytes_verified':True,'non_BIOS_write_count':3,'BIOS_write_count':bios,'loader_argument':[10,0],'level_store_changed_value':data(sb['globals'])[2:4]!=bytes(2),'native_Omnificent_clear':True,'RNG_seed':1,'counter':2,'scope':'Independent original O under temporary menu-option disable/restore and loader-input fixture. No native UI level choice or physical keyboard/IRQ9 parity; no actor/position/RNG/executable patch. Not target invocation or global closure.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('MAP1');p.add_argument('DEMO1');a=p.parse_args();print(json.dumps(verify(a.runtime,a.MAP1,a.DEMO1),indent=2))
