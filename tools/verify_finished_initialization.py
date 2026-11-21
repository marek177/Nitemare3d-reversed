import json,base64,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';O=R/'outputs/wall_sort_20261106';v=json.loads((D/'finished_init_observation.json').read_text());rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]};DS=0x2f94
def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x and 'id' in x:
   r=rpc[x['id']];assert r['response']==x and r['server_pid']==23808
   if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
  for y in x.values():check(y)
 elif isinstance(x,list):
  for y in x:check(y)
def reg(r):assert any(x['request']['method']=='state.get_registers' and x['server_pid']==23808 and x['response'].get('result')==r for x in rpc.values())
def addr(x,o,n):
 q=rpc[x['id']]['request']['params'];assert int(q['address']['segment'],16)==DS and int(q['address']['offset'],16)==o and q['length']==n
def pc(r):return int(r['segments']['cs'],16),int(r['instruction_pointer'],16)
check(v);assert v['phase']=='complete' and v['operation_id'] is None
for c in [v[k] for k in ('before_remaining','before_parent_return','after_parent_return','header')]:
 r=c['registers'];reg(r)
 for k,o,n in [('buffer',0x62ac,28000),('count',0x626e,2),('descriptors',0x4310,512),('episode_level',0x626a,4),('filename',0x629c,16),('RNG',0x24b8,4),('counter',0x4540,4),('header_words',0x455c,6)]:addr(c[k],o,n);assert c[k]['result']['state_revision']==r['state_revision']
 assert int.from_bytes(data(c['count']),'little')==960
b=v['before_parent_return'];a=v['after_parent_return'];sp=int(b['registers']['general']['esp'],16)&65535;addr(v['parent_return_frame'],sp,4);assert struct.unpack('<HH',data(v['parent_return_frame']))==(0x9c4,0x154c) and pc(b['registers'])==(0xa9a,0xbc0) and pc(a['registers'])==(0x154c,0x9c4) and int(a['registers']['general']['esp'],16)&65535==(sp+4)&65535
assert any(x['request']['method']=='execution.step' and x['response'].get('result',{}).get('operation_id')==v['step_operation'] for x in rpc.values())
h=v['header'];assert pc(h['registers'])==(0xed3,0x2e0) and data(h['filename']).split(b'\0')[0]==b'demo.1' and struct.unpack('<HH',data(h['episode_level']))==(1,10) and int.from_bytes(data(h['RNG']),'little')==1 and int.from_bytes(data(h['counter']),'little')==2
disk=(R/'work/runtime/game_rng_level5_n_20261106/DEMO.1').read_bytes();assert data(h['header_words'])==disk[:6] and struct.unpack('<3H',disk[:6])==(15,7,30)
summary={'status':'VERIFIED_RUNTIME_RAW_RPC_CORRELATED','parent_return':'0277:0BC0 -> 0D29:09C4','parent_stack_delta':4,'later_checkpoint':'06B0:02E0','episode':1,'level_index':10,'Demo_file':'DEMO.1','Demo_header_words':[15,7,30],'RNG_seed':1,'counter':2,'record_count':960,'record_bytes_changed_after_sort':sum(x!=y for x,y in zip(data(v['before_remaining']['buffer']),data(h['buffer']))),'scope':'Parent return and later first Demo-header checkpoint, not witnessed parent entry/zeroing or individual execution/effects of every intervening initializer, all deferred loads/frames/IRQ/writer domains or remake parity.'};(O/'finished_initialization_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
