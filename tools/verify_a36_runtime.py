"""Independent raw-RPC check of bounded original A36/ACF consumer and FAR exit."""
import json,base64,hashlib,struct,sys
from pathlib import Path
def verify(folder):
 D=Path(folder);records=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];raw={x['response']['id']:x for x in records};assert len(raw)==len(records)
 f=json.loads((D/'next_rng_call_observation.json').read_text());c=json.loads((D/'A36_consumer_observation.json').read_text());e=json.loads((D/'A36_exit_observation.json').read_text());pid=json.loads((D/'startup_identity.json').read_text())['server_pid'];B=int(json.loads((D/'startup_identity.json').read_text())['registers']['result']['segments']['cs'],16);DS=B+0x2771;CS=B+0x4c7
 def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
 def correlated(x):
  if isinstance(x,dict):
   if 'jsonrpc' in x and 'id' in x:
    r=raw[x['id']];assert r['response']==x and r['server_pid']==pid
    if r['request']['method']=='memory.read' and 'result' in x:
     b=data(x);assert len(b)==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(b).hexdigest()==x['result']['sha256']
   for y in x.values():correlated(y)
  elif isinstance(x,list):
   for y in x:correlated(y)
 def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==pid and x['response'].get('result')==r for x in records)
 def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
 def addr(x,s,o,n):
  q=raw[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
 def snap(x,fields):
  r=x['registers'];reg(r)
  for key,(s,o,n) in fields.items():addr(x[key],s,o,n);assert x[key]['result']['state_revision']==r['state_revision']
 def trace(chunks,capacity,start,end):
  ev=[x for chunk in chunks for x in chunk['result']['events']];assert len(ev)<capacity and chunks[-1]['result'].get('next_cursor') is None;assert [x['sequence'] for x in ev]==list(range(1,len(ev)+1))
  pcs=[(int(x['address']['segment'],16),int(x['address']['offset'],16)) for x in ev];assert pcs[0]==start and pcs[-1]==end;return ev,pcs
 for x in (f,c,e):correlated(x)
 for k in ('before','after'):
  r=f[k]['registers'];reg(r);assert int(r['segments']['ds'],16)==DS
  for name,o,n in [('state',0x24b8,4),('clock',0x81e,4),('counter',0x4540,4),('mode',0x3cd4,4),('flags',0x3f50,2),('pending_input',0x34be,8)]:addr(f[k]['reads'][name],DS,o,n);assert f[k]['reads'][name]['result']['state_revision']==r['state_revision']
 assert f['phase']==c['phase']==e['phase']=='verified' and f['caller_site']=='04C7:0A36' and e['caller_return']=='04C7:0EA4'
 assert pc(f['before']['registers'])==(B+0xfba,0x1a0) and pc(f['after']['registers'])==(CS,0xa3b)
 addr(f['caller_code'],CS,0xa36,5);assert data(f['caller_code'])==b'\x9a\xa0\x01'+struct.pack('<H',B+0xfba)
 sp=int(f['before']['registers']['general']['esp'],16)&65535;addr(f['stack'],DS,sp,4);assert struct.unpack('<HH',data(f['stack']))==(0xa3b,CS)
 first=int.from_bytes(data(f['before']['reads']['state']),'little');second=(first*214013+2531011)&0xffffffff
 assert f['before_state']==first and f['after_state']==second and f['returned_AX']==(second>>16)&32767
 assert int.from_bytes(data(f['after']['reads']['state']),'little')==second and int(f['after']['registers']['general']['eax'],16)&65535==(second>>16)&32767;assert int(f['after']['registers']['general']['esp'],16)&65535==(sp+4)&65535
 actor_s=c['actor_seg'];actor_o=c['actor_off'];fields={'actor':(actor_s,actor_o,26),'state':(DS,0x24b8,4)}
 for key in ('before','second_before','second_after','after'):snap(c[key],fields)
 assert c['before']['registers']==f['after']['registers'];bp=int(c['before']['registers']['general']['ebp'],16)&65535;addr(c['frame'],DS,bp,16);frame=data(c['frame']);assert struct.unpack_from('<HH',frame,6)==(actor_o,actor_s);obj_o,obj_s=struct.unpack_from('<HH',frame,10);addr(c['object'],obj_s,obj_o,28);addr(c['local_y'],DS,bp-2,2);addr(c['difficulty'],DS,0x4180,2)
 assert pc(c['second_before']['registers'])==(CS,0xacf) and pc(c['second_after']['registers'])==(CS,0xad4) and pc(c['after']['registers'])==(CS,0xb0a)
 assert int.from_bytes(data(c['second_before']['state']),'little')==second;third=(second*214013+2531011)&0xffffffff;assert int.from_bytes(data(c['second_after']['state']),'little')==third;ax=int(c['second_after']['registers']['general']['eax'],16)&65535;assert ax==(third>>16)&32767;assert c['second_before']['registers']['general']['esp']==c['second_after']['registers']['general']['esp']
 addr(c['second_code'],CS,0xacf,5);assert data(c['second_code'])==data(f['caller_code']);a=bytearray(data(c['before']['actor']));assert (a[10],a[11],a[23],a[24])==(0,3,1,0);assert data(c['object'])[6]==8
 selector=((second>>16)&32767)&7;assert selector==3;dx=int(c['before']['registers']['general']['edi'],16)&65535;dx=dx-65536 if dx&32768 else dx;dy=struct.unpack('<h',data(c['local_y']))[0];a[19]=8 if dx>0 else 248 if dx<0 else 0;a[20]=8 if dy>0 else 248 if dy<0 else 0
 assert data(c['second_before']['actor'])==a==data(c['second_after']['actor']);timer=ax%8+8;difficulty=struct.unpack('<H',data(c['difficulty']))[0]
 if difficulty==2:timer>>=1
 elif difficulty==0:timer=(timer<<1)&65535
 struct.pack_into('<H',a,6,timer);assert data(c['after']['actor'])==a and timer==c['expected_timer']==14
 ef={'actor':(actor_s,actor_o,26),'RNG':(DS,0x24b8,4)}
 for key in ('before','after_ES','after_state_store','before_epilogue','after_return'):snap(e[key],ef)
 assert e['before']['registers']==c['after']['registers'] and data(e['after_ES']['actor'])==a;assert pc(e['after_ES']['registers'])==(CS,0xb0d);addr(e['writer_code'],CS,0xb0d,5);assert data(e['writer_code'])==bytes.fromhex('26c6440b06');a[11]=6;assert data(e['after_state_store']['actor'])==a and pc(e['after_state_store']['registers'])==(CS,0xb12)
 assert pc(e['before_epilogue']['registers'])==(CS,0xb47)
 for x,ip in zip(e['steps'],(0xb48,0xb49,0xb4a)):snap(x,ef);assert pc(x['registers'])==(CS,ip)
 ret_sp=int(e['steps'][-1]['registers']['general']['esp'],16)&65535;addr(e['return_frame'],DS,ret_sp,4);ip,cs=struct.unpack('<HH',data(e['return_frame']));assert (ip,cs)==struct.unpack_from('<HH',frame,2)==(0xea4,CS)
 assert pc(e['after_return']['registers'])==(cs,ip) and int(e['after_return']['registers']['general']['esp'],16)&65535==(ret_sp+4)&65535;assert data(e['after_return']['actor'])==data(e['before_epilogue']['actor']) and data(e['after_return']['actor'])[11]==6
 windows=[]
 for chunks,cap,start,end in [(f['trace_chunks'],1000,(B+0xfba,0x1a0),(CS,0xa3b)),(c['trace_chunks'],2000,(CS,0xa3b),(CS,0xb0a)),(e['trace_chunks'],10000,(CS,0xb12),(CS,0xb47))]:
  ev,pcs=trace(chunks,cap,start,end);windows.append({'events':len(ev),'capacity':cap,'sequences_contiguous':True,'last_stop_instruction_execution_not_inferred':True})
 for target in (0xb0,0x12a,0x422):assert (CS,target) in [(int(x['address']['segment'],16),int(x['address']['offset'],16)) for chunk in e['trace_chunks'] for x in chunk['result']['events']]
 writes=[x for x in records if x['request']['method']=='memory.write']
 for x in writes:assert int(x['request']['params']['address']['segment'],16)==0x40 and len(base64.b64decode(x['request']['params']['data_base64']))==2
 return {'evidence_status':'VERIFIED_RUNTIME','server_pid':pid,'loadbase':f'{B:04X}','counter':int.from_bytes(data(f['before']['reads']['counter']),'little'),'actor':f'{actor_s:04X}:{actor_o:04X}','object_type':8,'mode':0,'state_transition':[3,6],'calls':[{'site':'04C7:0A36','before':first,'after':second,'AX':(second>>16)&32767},{'site':'04C7:0ACF','before':second,'after':third,'AX':ax}],'timer':timer,'direction_bytes':list(a[19:21]),'state_writer':'04C7:0B0D','caller_return':'04C7:0EA4','trace_windows':windows,'gameplay_API_writes':0,'unobserved_target_hits':0,'scope':'One natural mode0 actor continuation, not mode2 site09F6 or mode3 site0C37, not whole0938 entry/boundaries, all nested effects, IRQ/global writer or remake parity closure'}
if __name__=='__main__':print(json.dumps(verify(sys.argv[1]),indent=2))
