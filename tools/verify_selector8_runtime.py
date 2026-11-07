"""Raw-RPC verification of target0490, its selector8 consumer and nonfatal health path."""
import json,base64,hashlib,struct,argparse
from pathlib import Path
from verify_omnificent_runtime import verify as verify_origin
def verify(folder,map2):
 D=Path(folder);origin=verify_origin(D);pid=origin['pid'];B=int(origin['loadbase'],16);DS=B+0x2771;S=B+0x83d;P=B+0x637;raw={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]};t=json.loads((D/'target_observation_0000.json').read_text());c=json.loads((D/'selector8_consumer_observation.json').read_text());h=json.loads((D/'selector8_health_observation.json').read_text())
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
 def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==pid and x['response'].get('result')==r for x in raw.values())
 def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
 def addr(x,s,o,n):
  q=raw[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
 def trace(chunks,cap,start,end):
  events=[e for x in chunks for e in x['result']['events']];assert len(events)<cap and chunks[-1]['result'].get('next_cursor') is None and [e['sequence'] for e in events]==list(range(1,len(events)+1));assert (int(events[0]['address']['segment'],16),int(events[0]['address']['offset'],16))==start and (int(events[-1]['address']['segment'],16),int(events[-1]['address']['offset'],16))==end;return len(events)
 for x in (t,c,h):check(x)
 assert t['site']=='083D:0490' and t['LCG_AX_and_wrapper_stack_verified'];assert pc(t['before']['registers'])==(S,0x490) and pc(t['after']['registers'])==(S,0x495)
 assert c['phase']==h['phase']=='verified' and c['before']['registers']==t['after']['registers'];before=c['before'];reg(before['registers']);reg(c['after']['registers']);bp=int(before['registers']['general']['ebp'],16)&65535;addr(before['frame'],DS,bp,16);frame=data(before['frame']);ret_ip,ret_cs=struct.unpack_from('<HH',frame,2);assert (ret_ip,ret_cs)==(0x719,P)
 ao,aseg,oo,oseg=struct.unpack_from('<HHHH',frame,6);addr(before['actor'],aseg,ao,26);addr(before['object'],oseg,oo,28);obj=data(before['object']);assert obj[6]==8 and obj==data(t['before']['descriptor'])[:28]
 addr(c['selector_table'],S,0x45e,46);assert struct.unpack_from('<H',data(c['selector_table']))[0]==0x490
 addr(before['difficulty'],DS,0x4180,2);difficulty=struct.unpack('<H',data(before['difficulty']))[0];rngAX=int(t['after']['registers']['general']['eax'],16)&65535;expected=rngAX&7
 if difficulty==2:expected=(expected*2)&65535
 elif difficulty==0:expected>>=1
 assert c['result_AX']==expected==4 and int(c['after']['registers']['general']['eax'],16)&65535==expected and pc(c['after']['registers'])==(P,0x719)
 for field,s,o,n in [('actor',aseg,ao,26),('object',oseg,oo,28),('RNG',DS,0x24b8,4)]:addr(c['after'][field],s,o,n);assert data(c['after'][field])==data(before[field])
 addr(c['callee_stack'],DS,bp-6,22);stack=data(c['callee_stack']);ar=c['after']['registers'];assert int(ar['general']['esi'],16)&65535==struct.unpack_from('<H',stack)[0] and int(ar['general']['edi'],16)&65535==struct.unpack_from('<H',stack,2)[0] and int(ar['general']['ebp'],16)&65535==struct.unpack_from('<H',frame)[0] and int(ar['general']['esp'],16)&65535==(bp+6)&65535
 assert h['before']['registers']==ar
 for key in ['before','before_flash','after_flash','before_health','after_health','before_epilogue','after_return']:
  x=h[key];reg(x['registers'])
  for name,o,n in [('globals',0x417a,32),('health',0x4189,1),('flash',0x417a,2),('mode',0x3cd4,2),('invincibility',0x4151,1),('RNG',0x24b8,4)]:addr(x[name],DS,o,n);assert x[name]['result']['state_revision']==x['registers']['state_revision']
  assert data(x['globals'])[15:16]==data(x['health']) and data(x['globals'])[:2]==data(x['flash'])
 assert data(h['before']['health'])==b'\x64' and data(h['before']['mode'])==b'\1\0' and data(h['before']['invincibility'])==b'\0'
 assert pc(h['before_flash']['registers'])==(P,0x723);addr(h['flash_code'],P,0x723,6);assert data(h['flash_code'])==bytes.fromhex('c7067a410300');a=bytearray(data(h['before_flash']['globals']));a[:2]=b'\3\0';assert data(h['after_flash']['globals'])==a and pc(h['after_flash']['registers'])==(P,0x729)
 assert pc(h['before_health']['registers'])==(P,0x77d) and int(h['before_health']['registers']['general']['eax'],16)&255==4;addr(h['health_code'],P,0x77d,4);assert data(h['health_code'])==bytes.fromhex('28068941');a=bytearray(data(h['before_health']['globals']));a[15]=96;assert data(h['after_health']['globals'])==a and pc(h['after_health']['registers'])==(P,0x781)
 assert pc(h['before_epilogue']['registers'])==(P,0x78b)
 for x,off in zip(h['steps'],(0x78c,0x78d,0x78e)):reg(x['registers']);assert pc(x['registers'])==(P,off)
 sp=int(h['steps'][-1]['registers']['general']['esp'],16)&65535;addr(h['return_frame'],DS,sp,4);ip,cs=struct.unpack('<HH',data(h['return_frame']));assert (ip,cs)==struct.unpack_from('<HH',data(h['parent_frame']),2)==(0xedf,B+0x4c7);assert pc(h['after_return']['registers'])==(cs,ip) and int(h['after_return']['registers']['general']['esp'],16)&65535==(sp+4)&65535 and data(h['after_return']['health'])==b'\x60'
 provenance=c['map_class_provenance'];disk=Path(map2).read_bytes();assert hashlib.sha256(disk).hexdigest()==provenance['MAP2_sha256']=='9d08edc848a2f887f8e970ab0e4ec1c2b21e31b73b77d6b4d13c946b063a97c9';addr(provenance['header'],DS,0xd30c,514);header=data(provenance['header']);assert header==disk[:514];to,ts=struct.unpack_from('<HH',obj,12);addr(provenance['object_tile'],ts,to,2);assert ts==B+0x21fd and 0<=to-0x373e<8192 and (to-0x373e)%2==0;tile=data(provenance['object_tile']);assert provenance['current_wall_id']==tile[0] and provenance['wall_class_from_loaded_header']==header[2+tile[0]]
 counts=[trace([t['trace']],100,(S,0x490),(S,0x495)),trace(c['trace_chunks'],1000,(S,0x495),(P,0x719)),trace([h['gate_trace']],1000,(P,0x729),(P,0x77d))]
 return {'evidence_status':'VERIFIED_RUNTIME','target_site':'083D:0490','previously_unobserved_target_hit':True,'server_pid':pid,'loadbase':f'{B:04X}','counter':int.from_bytes(data(t['before']['reads']['counter']),'little'),'selector':8,'RNG_before':t['before']['state'],'RNG_after':t['after']['state'],'RNG_AX':rngAX,'difficulty':difficulty,'consumer_result_AX':expected,'consumer_return':'0637:0719','health_before':100,'health_after':96,'health_writer':'0637:077D','flash_writer':'0637:0723','caller_return':'04C7:0EDF','trace_window_events':counts,'loaded_MAP2_header_verified':True,'map_origin_even_wall_byte_verified':True,'remaining_from_original11_targets':10,'scope':'One natural selector8/nonfatal damage case. Other selectors, fatal/invincible/mode2, native constructor and global IRQ/RNG/remake parity remain open.'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('runtime_directory');p.add_argument('MAP2');a=p.parse_args();print(json.dumps(verify(a.runtime_directory,a.MAP2),indent=2))
