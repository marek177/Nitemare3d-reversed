import json,base64,hashlib,struct,argparse,collections
from pathlib import Path
def verify(folder,exe):
 D=Path(folder);v=json.loads((D/'wall_sort_observation.json').read_text());raw=Path(exe).read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';B=0x823;DS=B+0x2771;CS=B+0xfd9;SORT=B+0x11ee;im=bytearray(raw[int.from_bytes(raw[8:10],'little')*16:]);nr=struct.unpack_from('<H',raw,6)[0];rs=struct.unpack_from('<H',raw,24)[0]
 for j in range(nr):
  o,s=struct.unpack_from('<HH',raw,rs+4*j);p=16*s+o;struct.pack_into('<H',im,p,(struct.unpack_from('<H',im,p)[0]+B)&65535)
 rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
 def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
 def check(x):
  if isinstance(x,dict):
   if 'jsonrpc' in x and 'id' in x:
    r=rpc[x['id']];assert r['response']==x and r['server_pid']==23808
    if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and H(data(x))==x['result']['sha256']
   for y in x.values():check(y)
  elif isinstance(x,list):
   for y in x:check(y)
 def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==23808 and x['response'].get('result')==r for x in rpc.values())
 def addr(x,s,o,n):
  q=rpc[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
 def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
 def model(a,b):
  axis=12 if struct.unpack_from('<h',a,12)[0]==struct.unpack_from('<h',a,16)[0] else 14;x=struct.unpack_from('<h',a,axis)[0];y=struct.unpack_from('<h',b,axis)[0];return(x>y)-(x<y)
 check(v);assert v['phase']=='complete' and v['operation_id'] is None and v['pending_sort'] is None and v['pending_callback'] is None;b=v['before'];buf=data(b['buffer']);n=int.from_bytes(data(b['count']),'little');assert n==960;snaps=[b,v['grouped'],v['before_return'],v['after_return']]+[p[k] for p in v['sorts'] for k in ('before','after')]
 for x in snaps:
  r=x['registers'];reg(r)
  for k,o,length in [('groups',0x57fa,2672),('buffer',0x62ac,28000),('count',0x626e,2),('descriptors',0x4310,512)]:addr(x[k],DS,o,length);assert x[k]['result']['state_revision']==r['state_revision']
  for k in ('buffer','count','descriptors'):assert data(x[k])==data(b[k])
 for k,s,o,length in [('code',0xfd9,0x5e,267),('caller_code',0x277,0xb99,5),('comparator_code',0xfd9,0x16,72),('sort_code',0x11ee,0x3090,312)]:addr(v[k],B+s,o,length);assert data(v[k])==im[s*16+o:s*16+o+length]
 entry=b['registers'];sp=int(entry['general']['esp'],16)&65535;assert pc(entry)==(CS,0x5e);addr(v['entry_stack'],DS,sp,8);assert struct.unpack_from('<HH',data(v['entry_stack']))==(0xb9e,B+0x277)
 groups=data(v['grouped']['groups']);counts=list(struct.unpack_from('<4H',groups));bases=(0x5802,0x5a9c,0x5d36,0x5fd0);expected=[[0x62ac+28*i for i in range(n) if buf[28*i+7]==direction] for direction in range(4)];assert counts==[len(x) for x in expected] and all(x<=333 for x in counts);assert pc(v['grouped']['registers'])==(CS,0x10a)
 def pointers(g,i):return list(struct.unpack_from('<'+'H'*counts[i],g,bases[i]-0x57fa))
 for i in range(4):assert pointers(groups,i)==expected[i]
 assert len(v['sorts'])==4;previous=groups;sort_summary=[]
 for i,p in enumerate(v['sorts']):
  br=p['before']['registers'];ar=p['after']['registers'];s=int(br['general']['esp'],16)&65535;addr(p['frame'],DS,s,14);ip,cs,base,count,size,cmpip,cmpcs=struct.unpack('<7H',data(p['frame']));ret=(0x11e,0x135,0x14c,0x163)[i];assert(ip,cs,base,count,size,cmpip,cmpcs)==(ret,CS,bases[i],counts[i],2,0x16,CS);assert pc(br)==(SORT,0x3090) and pc(ar)==(CS,ret) and int(ar['general']['esp'],16)&65535==(s+4)&65535
  before=data(p['before']['groups']);after=data(p['after']['groups']);assert before==previous;start=base-0x57fa;end=start+2*count;assert before[:start]==after[:start] and before[end:]==after[end:];result=pointers(after,i);assert collections.Counter(result)==collections.Counter(expected[i])
  records=[buf[x-0x62ac:x-0x62ac+28] for x in result];assert all(model(records[j+1],records[j])>=0 for j in range(len(records)-1));sort_summary.append({'direction':i,'count':count,'permutation_checked':True,'adjacent_signed_comparator_order_checked':True,'changed_pointer_positions':sum(x!=y for x,y in zip(pointers(before,i),result))});previous=after
 callback_summary=[]
 for p in v['callbacks']:
  br=p['before_registers'];er=p['entry_registers'];ar=p['after_registers'];reg(br);reg(er);reg(ar);off=int(p['site'].split(':')[1],16);length=3 if off==0x30ad else 4;ss=int(br['segments']['ss'],16);s=int(br['general']['esp'],16)&65535;operand=(int(br['general']['ebp'],16)&65535)+12 if off==0x30ad else(int(br['general']['edi'],16)&65535)+18
  assert off in(0x30ad,0x312f,0x314d) and pc(br)==(SORT,off);addr(p['operand'],ss,operand,4);assert struct.unpack('<HH',data(p['operand']))==(0x16,CS);addr(p['code'],SORT,off,length);assert data(p['code'])==bytes.fromhex('ff5e0c' if length==3 else '36ff5d12');addr(p['args'],ss,s,4);a,bptr=struct.unpack('<HH',data(p['args']))
  records=[]
  for x,o,y in zip(p['element_pointers'],(a,bptr),p['records']):addr(x,DS,o,2);ptr=int.from_bytes(data(x),'little');addr(y,DS,ptr,28);records.append(data(y))
  assert pc(er)==(CS,0x16) and int(er['general']['esp'],16)&65535==(s-4)&65535;addr(p['entry_frame'],ss,(s-4)&65535,8);assert struct.unpack('<4H',data(p['entry_frame']))==(off+length,SORT,a,bptr);expected_ax=model(*records)&65535;assert pc(ar)==(SORT,off+length) and int(ar['general']['esp'],16)&65535==s and int(ar['general']['eax'],16)&65535==expected_ax
  for k in ('esi','edi','ebp'):assert ar['general'][k]==br['general'][k]
  ev=[e for x in p['trace_chunks'] for e in x['result']['events']];assert len(ev)<1000 and p['trace_chunks'][-1]['result'].get('next_cursor') is None and [e['sequence'] for e in ev]==list(range(1,len(ev)+1));assert (int(ev[0]['address']['segment'],16),int(ev[0]['address']['offset'],16))==(SORT,off) and (int(ev[-1]['address']['segment'],16),int(ev[-1]['address']['offset'],16))==(SORT,off+length);callback_summary.append({'site':p['site'],'executed_target':'0FD9:0016','AX':expected_ax,'trace_events':len(ev),'actual_FAR_return':f'11EE:{off+length:04X}'})
 assert {x['site'] for x in callback_summary}=={'11EE:30AD','11EE:312F','11EE:314D'};a=v['after_return'];assert pc(v['before_return']['registers'])==(CS,0x168) and pc(a['registers'])==(B+0x277,0xb9e) and int(a['registers']['general']['esp'],16)&65535==(sp+4)&65535;assert data(a['groups'])==previous
 for k in ('esi','edi','ebp'):assert a['registers']['general'][k]==entry['general'][k]
 return {'status':'VERIFIED_RUNTIME_RAW_RPC_CORRELATED','function':'0FD9:005E','sort_function':'11EE:3090','counts':counts,'sorts':sort_summary,'callbacks':callback_summary,'buffer_and_descriptors_unchanged':True,'native_FAR_return':'0277:0B9E','scope':'One native grouping/four-sort case and one actual comparator execution per sampled indirect site. No whole indirect target domain, all comparator invocations, sort stability, error/capacity/alias/IRQ or full initialization/RNG/remake closure.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('runtime_directory');p.add_argument('unpacked_exe');a=p.parse_args();print(json.dumps(verify(a.runtime_directory,a.unpacked_exe),indent=2))
