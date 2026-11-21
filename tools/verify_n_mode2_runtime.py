"""Verify explicit loader-input fixture, native constructor and target09F6 case."""
import json,base64,hashlib,struct,argparse
from pathlib import Path
def verify(folder,map1):
 D=Path(folder);rows=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];raw={x['response']['id']:x for x in rows};assert len(raw)==len(rows);identity=json.loads((D/'startup_identity.json').read_text());pid=identity['server_pid'];B=identity['loadbase'];DS=B+0x2771
 l=json.loads((D/'level_fixture_ctor_observation.json').read_text());ready=json.loads((D/'level_fixture_ready.json').read_text());t=json.loads((D/'target_observation_0000.json').read_text());c=json.loads((D/'mode2_consumer_observation.json').read_text());e=json.loads((D/'mode2_exit_observation.json').read_text());h=json.loads((D/'DEMO_header_runtime.json').read_text());initial=json.loads((D/'level5_initial.json').read_text())
 def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
 def check(x):
  if isinstance(x,dict):
   if 'jsonrpc' in x and 'id' in x:
    r=raw[x['id']];assert r['response']==x and r['server_pid']==pid
    if r['request']['method']=='memory.read' and 'result' in x:
     b=data(x);assert len(b)==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(b).hexdigest()==x['result']['sha256']
   for y in x.values():check(y)
  elif isinstance(x,list):
   for y in x:check(y)
 def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==pid and x['response'].get('result')==r for x in rows)
 def pc(r):return int(r['segments']['cs'],16)-B,int(r['instruction_pointer'],16)
 def addr(x,s,o,n):
  q=raw[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
 def trace(chunks,cap,start,end):
  ev=[z for x in chunks for z in x['result']['events']];assert len(ev)<cap and chunks[-1]['result'].get('next_cursor') is None and [z['sequence'] for z in ev]==list(range(1,len(ev)+1));pcs=[(int(z['address']['segment'],16)-B,int(z['address']['offset'],16)) for z in ev];assert pcs[0]==start and pcs[-1]==end;return len(ev)
 for x in (identity,l,ready,t,c,e,h,initial):check(x)
 assert pc(l['clear_before']['registers'])==(0xd29,0x28c9) and data(l['clear_before']['code'])==bytes.fromhex('a25341');cl=bytearray(data(l['clear_before']['config']));assert cl[15]==1;cl[15]=0;assert data(l['clear_after']['config'])==cl and pc(l['clear_after']['registers'])==(0xd29,0x28cc)
 manifest={x['name'].upper():x for x in json.loads((D/'input_manifest.json').read_text())};assert manifest['N3D.EXE']['sha256']=='a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485'
 f=l['level_argument_fixture'];r=f['registers'];reg(r);assert pc(r)==(0xd29,0x26f4);sp=int(r['general']['esp'],16)&65535;ss=int(r['segments']['ss'],16);addr(f['stack_before'],ss,sp,16);addr(f['stack_after'],ss,sp,16);before=data(f['stack_before']);assert struct.unpack_from('<HHH',before)==(B+0xd29,10,1);a=bytearray(before);a[2:4]=b'\4\0';assert data(f['stack_after'])==a and f['selected_level_index']==4 and f['episode_unchanged']==1
 q=raw[f['write']['id']]['request'];assert q['method']=='memory.write' and int(q['params']['address']['segment'],16)==ss and int(q['params']['address']['offset'],16)==sp+2 and base64.b64decode(q['params']['data_base64'])==b'\4\0'
 writes=[x for x in rows if x['request']['method']=='memory.write'];outside=[x for x in writes if int(x['request']['params']['address']['segment'],16)!=0x40];assert len(outside)==1 and outside[0]['response']==f['write']
 for x in writes:
  if x not in outside:assert len(base64.b64decode(x['request']['params']['data_base64']))==2
 assert pc(l['level_store_before']['registers'])==(0xd29,0x97d) and int(l['level_store_before']['registers']['general']['eax'],16)&65535==4 and data(l['level_store_before']['code'])==bytes.fromhex('a36c62');a=bytearray(data(l['level_store_before']['globals']));a[2:4]=b'\4\0';assert data(l['level_store_after']['globals'])==a and pc(l['level_store_after']['registers'])==(0xd29,0x980)
 s=l['selected_entry'];reg(s['registers']);assert pc(s['registers'])==(0x83d,0x117a);entrysp=int(s['registers']['general']['esp'],16)&65535;addr(s['stack'],DS,entrysp,12);retip,retcs,ao,aseg,oo,oseg=struct.unpack('<6H',data(s['stack']));assert s['actor_address']==[aseg,ao];addr(s['object'],oseg,oo,28);to,ts=struct.unpack_from('<HH',data(s['object']),12);addr(s['tile'],ts,to,2);assert ts==B+0x21fd and (to-0x373e)%2==0;assert data(s['wall_class'])[0] in(0x42,0x46)
 disk=Path(map1).read_bytes();assert hashlib.sha256(disk).hexdigest()==manifest['MAP.1']['sha256']==s['MAP1_sha256'];assert data(s['header'])==disk[:514] and struct.unpack('<HH',data(s['episode_level']))==(1,4);tile=data(s['tile'])[0];assert disk[514+8192*4+to-0x373e]==tile and disk[2+tile]==data(s['wall_class'])[0]
 assert pc(l['ctor_store_before']['registers'])==(0x83d,0x1262) and data(l['ctor_store_before']['code'])==bytes.fromhex('26c6440a02');a=bytearray(data(l['ctor_store_before']['actor']));assert a[10]==0;a[10]=2;assert data(l['ctor_store_after']['actor'])==a and pc(l['ctor_store_after']['registers'])==(0x83d,0x1267);assert pc(l['ctor_return'])==(0x4c7,0x1700) and (retip,retcs)==(0x1700,B+0x4c7) and int(l['ctor_return']['general']['esp'],16)&65535==(entrysp+4)&65535
 assert pc(ready['header_registers'])==(0x6b0,0x2e0);assert h['filename'].upper()=='DEMO.1' and h['file_sha256']==manifest['DEMO.1']['sha256'] and h['timing_words']==[15,7,30] and h['first_record']==[0x48e0,2,8] and h['RNG_state']==1
 assert data(h['reads']['timing'])==struct.pack('<3H',15,7,30) and data(h['reads']['first_record'])==struct.pack('<HHI',0x48e0,2,8) and data(h['reads']['RNG'])==b'\1\0\0\0' and data(h['reads']['mode'])==struct.pack('<HH',1,4)
 actorblob=data(initial['reads']['actors']);assert len(actorblob)==26*len(initial['rows'])
 for x in initial['rows']:
  ab=actorblob[26*x['slot']:26*(x['slot']+1)];ob=data(x['object_read']);assert x['actor_offset']==0x264e+26*x['slot'] and x['mode']==ab[10] and x['state']==ab[11] and x['type']==ob[6] and x['object_xy']==list(struct.unpack_from('<hh',ob,16))
 mode2=[x for x in initial['rows'] if x['mode']==2];assert len(mode2)==13
 for x in mode2:
  px,py=[z>>6 for z in x['object_xy']];wall=disk[514+8192*4+2*(64*py+px)];assert disk[2+wall] in(0x42,0x46)
 assert t['site']=='04C7:09F6' and t['LCG_AX_and_wrapper_stack_verified'] and 'loader-argument fixture' in t['scope'];br=t['before']['registers'];ar=t['after']['registers'];reg(br);reg(ar);assert pc(br)==(0x4c7,0x9f6) and pc(ar)==(0x4c7,0x9fb);state=int.from_bytes(data(t['before']['reads']['state']),'little');expected=(state*214013+2531011)&0xffffffff;assert int.from_bytes(data(t['after']['reads']['state']),'little')==expected and int(ar['general']['eax'],16)&65535==(expected>>16)&32767 and br['general']['esp']==ar['general']['esp']
 calls=[x['response'] for x in rows if x['request']['method']=='memory.read' and int(x['request']['params']['address']['segment'],16)==B+0x4c7 and int(x['request']['params']['address']['offset'],16)==0x9f6 and x['request']['params']['length']==5];assert any(data(x)==b'\x9a\xa0\x01'+struct.pack('<H',B+0xfba) for x in calls)
 assert c['phase']==e['phase']=='verified' and c['before']['registers']==ar;frame=data(c['frame']);ao2,as2,oo2,os2=struct.unpack_from('<HHHH',frame,6);assert [c['actor_seg'],c['actor_off']]==[as2,ao2];a=bytearray(data(c['before']['actor']));assert a==data(t['before']['record'])[:26] and (a[10],a[11])==(2,5);timer=((expected>>16)&32767)%8+8;struct.pack_into('<H',a,6,timer);assert timer==14==c['timer_expected'] and data(c['after']['actor'])==a and pc(c['after']['registers'])==(0x4c7,0xb0a)
 assert e['before']['registers']==c['after']['registers'] and data(e['after_ES']['actor'])==a and data(e['writer_code'])==bytes.fromhex('26c6440b06');a[11]=6;assert data(e['after_state_store']['actor'])==a and pc(e['after_state_store']['registers'])==(0x4c7,0xb12)
 before_ret=e['steps'][-1]['registers'];retsp=int(before_ret['general']['esp'],16)&65535;assert pc(before_ret)==(0x4c7,0xb4a);assert struct.unpack('<HH',data(e['return_frame']))==struct.unpack_from('<HH',frame,2)==(0xea4,B+0x4c7);assert pc(e['after_return']['registers'])==(0x4c7,0xea4) and int(e['after_return']['registers']['general']['esp'],16)&65535==(retsp+4)&65535 and data(e['after_return']['actor'])[11]==6
 windows=[trace([l['ctor_trace']],1000,(0x83d,0x117a),(0x83d,0x1262)),trace([t['trace']],100,(0x4c7,0x9f6),(0x4c7,0x9fb)),trace([c['trace']],1000,(0x4c7,0x9fb),(0x4c7,0xb0a)),trace(e['trace_chunks'],10000,(0x4c7,0xb12),(0x4c7,0xb47))]
 return {'evidence_status':'VERIFIED_RUNTIME','scenario':'Explicit one-word native-loader argument fixture10->4; native UI level selection not proved','server_pid':pid,'loadbase':f'{B:04X}','episode':1,'level_index':4,'non_BIOS_API_writes':1,'write_role':'2-byte loader stack input only','actor_or_position_or_RNG_API_writes':0,'constructor_tile':s['tile_coordinates'],'constructor_type':data(s['object'])[6],'constructor_mode_change':[0,2],'mode2_actors_at_header':len(mode2),'target_site':'04C7:09F6','counter':int.from_bytes(data(t['before']['reads']['counter']),'little'),'mode_at_call':2,'state_at_call':5,'RNG_before':state,'RNG_after':expected,'returned_AX':(expected>>16)&32767,'timer':timer,'later_state_change':[5,6],'caller_return':'04C7:0EA4','trace_window_events':windows,'remaining_from_prior11':9,'scope':'Original constructor/AI/consumer execution under fixture; no pristine UI selection, full0938 entry/dispatch-state, global writers/IRQ or remake parity closure'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('runtime_directory');p.add_argument('MAP1');a=p.parse_args();print(json.dumps(verify(a.runtime_directory,a.MAP1),indent=2))
