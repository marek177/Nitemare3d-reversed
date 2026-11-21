"""Read-only raw-RPC validation of the bounded native visibility code reads."""
import json,base64,hashlib,struct,sys
from pathlib import Path
def verify(folder):
 D=Path(folder);v=json.loads((D/'visibility_relocation_runtime.json').read_text());raw={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]};pid=v['server_pid'];B=int(v['loadbase'],16)
 def correlated(x):
  assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==pid
 r=v['registers'];correlated(r);regs=r['result'];revision=regs['state_revision'];assert int(regs['segments']['cs'],16)==B+0xd29 and int(regs['instruction_pointer'],16)==0x440
 targets={'0AEA:0DCE':(B+0xaea,0xdce,b'\x9a'+struct.pack('<HH',0,B)),'0AEA:0DD8':(B+0xaea,0xdd8,b'\x9a'+struct.pack('<HH',0x1e0,B)),'0000:01E0':(B,0x1e0,None)}
 assert set(v['reads'])==set(targets)
 for k,(seg,off,expected) in targets.items():
  x=v['reads'][k];correlated(x);q=raw[x['id']]['request'];assert q['method']=='memory.read';a=q['params']['address'];assert (int(a['segment'],16),int(a['offset'],16))==(seg,off)
  data=base64.b64decode(x['result']['data_base64'],validate=True);assert len(data)==q['params']['length']==x['result']['byte_count'];assert x['result']['state_revision']==revision;assert hashlib.sha256(data).hexdigest()==x['result']['sha256']
  if expected is not None:assert data==expected
  else:assert len(data)==28 and hashlib.sha256(data).hexdigest()=='f1869a55b1fe9d0c6f8884bf9d8c68df98f5cff1f8480c06b8a3c93d50c75a2a'
 return {'status':'VERIFIED_NATIVE_MEMORY_READS_CORRELATED_TO_RPC','server_pid':pid,'loadbase':v['loadbase'],'revision':revision,'relocated_direct_calls':2,'predicate_bytes':28,'executed_callee_invocations_claimed':0,'successful_C37_claimed':False}
if __name__=='__main__':print(json.dumps(verify(sys.argv[1]),indent=2))
