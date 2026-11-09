"""Read-only verification of four original record passes and their buffers."""
import json,base64,hashlib,struct,argparse
from pathlib import Path
def verify(folder,exe,map1):
 D=Path(folder);v=json.loads((D/'wall_record_pass_observation.json').read_text());raw=Path(exe).read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=bytearray(raw[int.from_bytes(raw[8:10],'little')*16:]);B=0x823;DS=B+0x2771;CS=B+0xfd9;rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
 relocation_count=struct.unpack_from('<H',raw,6)[0];relocation_start=struct.unpack_from('<H',raw,24)[0]
 for j in range(relocation_count):
  off,seg=struct.unpack_from('<HH',raw,relocation_start+4*j);pos=16*seg+off;word=struct.unpack_from('<H',im,pos)[0];struct.pack_into('<H',im,pos,(word+B)&65535)
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
 check(v);assert v['phase']=='complete' and v['operation_id'] is None and v['pending'] is None;before=v['before'];snaps=[before,v['before_store'],v['after_store'],v['after_return']]+[x[k] for x in v['passes'] for k in ('before','after')]
 for c in snaps:
  r=c['registers'];reg(r)
  for k,s,o,n in [('buffer',DS,0x62ac,28000),('count',DS,0x626e,2),('traits',DS,0xd00c,512),('header',DS,0xd30c,514),('map',B+0x21fd,0x373e,8192),('episode_level',DS,0x626a,4)]:addr(c[k],s,o,n);assert c[k]['result']['state_revision']==r['state_revision']
  for k in ('traits','header','map','episode_level'):assert data(c[k])==data(before[k])
 disk=Path(map1).read_bytes();assert H(disk)=='0f36888ef9df05004c77f920d810780e2023853b7ab6575dc6d910a871ae59f0';ep,level=struct.unpack('<HH',data(before['episode_level']));assert ep==1 and data(before['header'])==disk[:514] and data(before['map'])==disk[514+8192*level:514+8192*(level+1)]
 assert pc(before['registers'])==(CS,0xe1c);sp=int(before['registers']['general']['esp'],16)&65535;addr(v['entry_stack'],DS,sp,8);assert struct.unpack_from('<HH',data(v['entry_stack']))==(0xb99,B+0x277)
 for key,s,o,n in [('code',CS,0xe1c,80),('child_code',CS,0xb02,794),('caller_code',B+0x277,0xb94,5)]:addr(v[key],s,o,n)
 assert data(v['code'])==im[0xfd9*16+0xe1c:0xfd9*16+0xe6c] and data(v['child_code'])==im[0xfd9*16+0xb02:0xfd9*16+0xe1c] and data(v['caller_code'])==bytes.fromhex('9a1c0e')+struct.pack('<H',CS)
 cumulative=0;counts=[];previous=data(before['buffer']);ranges=[]
 assert len(v['passes'])==4
 for i,p in enumerate(v['passes']):
  b=p['before'];a=p['after'];br=b['registers'];ar=a['registers'];childsp=int(br['general']['esp'],16)&65535;addr(p['frame'],DS,childsp,12);ip,cs,direction,pointer,prior,savedsi=struct.unpack('<6H',data(p['frame']));ret=(0xe28,0xe3b,0xe4e,0xe61)[i]
  assert pc(br)==(CS,0xb02) and pc(ar)==(CS,ret) and (ip,cs,direction,pointer,prior)==(ret,CS,i,0x62ac+28*cumulative,cumulative) and p['direction']==i and p['pointer']==pointer and p['cumulative_before']==prior
  assert int(ar['general']['esp'],16)&65535==(childsp+4)&65535;assert childsp==sp-12 and savedsi==int(before['registers']['general']['esi'],16)&65535
  n=int(ar['general']['eax'],16)&65535;assert n==p['returned_count'] and cumulative+n<=1000;start=28*cumulative;end=28*(cumulative+n);bb=data(b['buffer']);ab=data(a['buffer']);assert bb==previous and ab[:start]==bb[:start] and ab[end:]==bb[end:]
  records=[ab[j:j+28] for j in range(start,end,28)];assert all(x[7]==i and x[8:12]==bytes(4) for x in records);ranges.append({'direction':i,'start_index':cumulative,'count':n,'end_index_exclusive':cumulative+n,'changed_bytes':sum(x!=y for x,y in zip(bb,ab))});counts.append(n);cumulative+=n;previous=ab
 bs=v['before_store'];ast=v['after_store'];ar=v['after_return'];assert pc(bs['registers'])==(CS,0xe66) and int(bs['registers']['general']['esi'],16)&65535==cumulative;addr(v['store_code'],CS,0xe66,4);assert data(v['store_code'])==bytes.fromhex('89366e62');assert pc(ast['registers'])==(CS,0xe6a) and int.from_bytes(data(ast['count']),'little')==cumulative and data(bs['buffer'])==data(ast['buffer'])==data(ar['buffer'])==previous
 reg(v['after_pop_si']);assert pc(v['after_pop_si'])==(CS,0xe6b) and pc(ar['registers'])==(B+0x277,0xb99);assert int(ar['registers']['general']['esp'],16)&65535==(sp+4)&65535 and int.from_bytes(data(ar['count']),'little')==cumulative
 for k in ('esi','edi','ebp'):assert ar['registers']['general'][k]==before['registers']['general'][k]
 for k in ('ds','ss'):assert ar['registers']['segments'][k]==before['registers']['segments'][k]
 return {'status':'VERIFIED_RUNTIME_RAW_RPC_CORRELATED','function':'0FD9:0E1C','child':'0FD9:0B02','server_pid':23808,'episode':ep,'level_index':level,'counts':counts,'total':cumulative,'record_stride':28,'buffer_bytes':28000,'passes':ranges,'all_record_direction_bytes_and_zero_dword8_verified':True,'unchanged_input_map_header_traits':True,'FAR_return':'0277:0B99','previous_global_count':int.from_bytes(data(before['count']),'little'),'scope':'One native four-pass call under prior documented N menu/input history. Entry/return/argument and endpoint-memory proof; no full inner instruction/write/IRQ trace, universal map/capacity/error/alias domain, descriptor-pointer ownership or new RNG/C37/remake claim.'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('runtime_directory');p.add_argument('unpacked_exe');p.add_argument('MAP1');a=p.parse_args();print(json.dumps(verify(a.runtime_directory,a.unpacked_exe,a.MAP1),indent=2))
