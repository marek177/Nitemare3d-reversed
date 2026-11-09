"""Read-only raw-RPC verifier of one native wall-trait builder invocation."""
import json,base64,hashlib,struct,argparse,collections
from pathlib import Path
def verify(folder,exe,kind='wall'):
 ENTRY,RET,STORE,HEADER,OUTPUT,CALLSITE,RETURN,CALLHEX={'wall':(0x1b6,0x24e,0x23f,0xd30e,0xd00c,0xb8a,0xb8f,'9ab601'),'object':(0x250,0x2f1,0x2e2,0xd40e,0xd10c,0xb8f,0xb94,'9a5002')}[kind]
 D=Path(folder);v=json.loads((D/f'native_{kind}_trait_observation.json').read_text());raw=Path(exe).read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]};B=0x823;CS=B+0xf7;DS=B+0x2771
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
 check(v);assert v['phase']=='complete' and v['operation_id'] is None;b=v['before'];r=v['before_return'];a=v['after_return']
 for c in (b,r,a):
  reg(c['registers']);addr(c['header'],DS,HEADER,256);addr(c['output'],DS,OUTPUT,256);addr(c['episode_level'],DS,0x626a,4)
  for k in ('header','output','episode_level'):assert c[k]['result']['state_revision']==c['registers']['state_revision']
 br=b['registers'];ar=a['registers'];sp=int(br['general']['esp'],16)&65535;assert pc(br)==(CS,ENTRY) and pc(r['registers'])==(CS,RET) and pc(ar)==(B+0x277,RETURN);assert int(br['segments']['ds'],16)==int(br['segments']['ss'],16)==DS
 addr(v['initial_local'],DS,sp-3,1);addr(v['entry_stack'],DS,sp-8,16);initial=data(v['initial_local'])[0];assert data(v['entry_stack'])[5]==initial and struct.unpack_from('<HH',data(v['entry_stack']),8)==(RETURN,B+0x277)
 addr(v['code'],CS,ENTRY,RET-ENTRY+1);assert data(v['code'])==im[0xf7*16+ENTRY:0xf7*16+RET+1];addr(v['caller_code'],B+0x277,CALLSITE,5);assert data(v['caller_code'])==bytes.fromhex(CALLHEX)+struct.pack('<H',CS)
 def model(c):
  if kind=='wall':return(initial&128)|(3 if 1<=c<=0x40 else 0)|(4 if 1<=c<=0x30 else 0)|(8 if 0x31<=c<=0x40 else 0)|(16 if c in(0x2e,0x2f) else 0)|(64 if c in(0x47,0x48) else 0)
  return(initial&128)|(1 if 6<=c<=0x3d else 0)|(2 if 8<=c<=0x2d else 0)|(4 if 0x2f<=c<=0x3d else 0)|(8 if 8<=c<=0x25 else 0)|(32 if c==0x2a else 0)|(64 if c==4 else 0)
 header=data(b['header']);expected=bytes(map(model,header));assert data(r['header'])==data(a['header'])==header and data(r['output'])==data(a['output'])==expected
 for name in ('ebx','ecx','edi','esi','ebp'):assert ar['general'][name]==br['general'][name]
 for name in ('ds','es','ss','fs','gs'):assert ar['segments'][name]==br['segments'][name]
 assert int(ar['general']['esp'],16)&65535==(sp+4)&65535 and int(ar['general']['eax'],16)==(int(br['general']['eax'],16)&0xffffff00)|expected[-1] and int(ar['general']['edx'],16)&65535==header[-1]
 assert int(ar['flags'],16)&0x8d5==0x44 and int(ar['flags'],16)&0x400==int(br['flags'],16)&0x400
 windows=[x['chunks'] for x in v.get('full_trace_windows',[])]+[v['trace_chunks']];events=[];counts=[]
 for wi,chunks in enumerate(windows):
  ev=[e for x in chunks for e in x['result']['events']];assert len(ev)<=10000 and chunks[-1]['result'].get('next_cursor') is None and [e['sequence'] for e in ev]==list(range(1,len(ev)+1));counts.append(len(ev));events.extend({**e,'_window_index':wi} for e in ev)
 assert counts[-1]<10000 and all(n==10000 for n in counts[:-1]);assert (int(events[0]['address']['segment'],16),int(events[0]['address']['offset'],16))==(CS,ENTRY) and (int(events[-1]['address']['segment'],16),int(events[-1]['address']['offset'],16))==(CS,RET)
 if len(windows)>1:
  reg(v['resumed_window_start']);assert v['resumed_window_start']==v['full_trace_windows'][-1]['pause_registers'];first=windows[-1][0]['result']['events'][0];assert (int(first['address']['segment'],16),int(first['address']['offset'],16))==pc(v['resumed_window_start'])
 state={};writes=[]
 for e in events:
  state.update(e.get('register_changes',{}))
  if int(e['address']['segment'],16)==CS and int(e['address']['offset'],16)==STORE:
   i=int(state['esi'],16)&65535;value=int(state['eax'],16)&255;assert i<256 and value==expected[i];writes.append({'index':i,'value':value,'sequence':e['sequence']})
 assert [w['index'] for w in writes]==list(range(256));assert im[0xf7*16+STORE:0xf7*16+STORE+4]==bytes.fromhex('8884')+struct.pack('<H',OUTPUT)
 foreign=collections.Counter(f"{int(e['address']['segment'],16)-B:04X}" for e in events if int(e['address']['segment'],16)!=CS)
 runs=[];current=[]
 for e in events:
  if int(e['address']['segment'],16)==CS:
   if current:runs.append(current);current=[]
  else:current.append(e)
 assert not current
 interleavings=[{'window':x[0]['_window_index'],'first_sequence':x[0]['sequence'],'last_sequence':x[-1]['sequence'],'event_count':len(x),'entry_loadbase_normalized':f"{int(x[0]['address']['segment'],16)-B:04X}:{int(x[0]['address']['offset'],16):04X}",'last_instruction':x[-1]['instruction']} for x in runs]
 return {'status':'VERIFIED_RUNTIME_RAW_RPC_CORRELATED','function':f'00F7:{ENTRY:04X}','server_pid':23808,'loadbase':'0823','initial_local_byte':initial,'output_bit7':initial&128,'trace_window_event_counts':counts,'loadbase_normalized_segment_event_counts':dict(foreign),'interleaved_runs':interleavings,'ordered_store_sites_checked':len(writes),'all256_output_bytes_match':True,'header_unchanged':True,'output_bytes_changed_from_entry':sum(x!=y for x,y in zip(data(b['output']),expected)),'native_FAR_return':f'0277:{RETURN:04X}','stack_delta':4,'defined_FLAGS_and_DF_checked':True,'scope':'One native invocation after Escape/Enter BIOS queue fixtures and original Demo reload, including interleaved execution in other segments. Capacity windows remain separately identified; stop instructions are not presumed executed. RETF is separately stepped. This verifies initialbit7=0 in this case, not all native stack provenance, boundaries, aliases, interrupt entry/side-effect closure, bit7 consumers, C37 or remake parity.'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('runtime_directory');p.add_argument('unpacked_exe');p.add_argument('--kind',choices=['wall','object'],default='wall');a=p.parse_args();print(json.dumps(verify(a.runtime_directory,a.unpacked_exe,a.kind),indent=2))

