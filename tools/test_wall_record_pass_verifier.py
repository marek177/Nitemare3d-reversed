import json,base64,hashlib,shutil,tempfile
from pathlib import Path
from verify_wall_record_passes import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';EXE='C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe';MAP=R/'work/runtime/game_rng_level5_n_20261106/MAP.1';out=[]
for case in ('direction_argument','global_count','buffer_suffix'):
 with tempfile.TemporaryDirectory(prefix='wall_pass_negative_',dir=R/'work') as name:
  T=Path(name)
  for p in D.glob('rpc_*.json'):shutil.copy2(p,T/p.name)
  v=json.loads((D/'wall_record_pass_observation.json').read_text());records={r['response']['id']:(p,r) for p in T.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
  def alter(x,index,value):
   b=bytearray(base64.b64decode(x['result']['data_base64']));b[index]=value;x['result']['data_base64']=base64.b64encode(b).decode();x['result']['sha256']=hashlib.sha256(b).hexdigest();p,r=records[x['id']];r['response']=x;p.write_text(json.dumps(r))
  if case=='direction_argument':alter(v['passes'][0]['frame'],4,1);v['passes'][0]['direction']=1
  elif case=='global_count':
   for key in ('after_store','after_return'):
    x=v[key]['count'];b=base64.b64decode(x['result']['data_base64']);alter(x,0,b[0]^1)
  else:
   x=v['passes'][0]['after']['buffer'];b=base64.b64decode(x['result']['data_base64']);alter(x,27999,b[-1]^1)
  (T/'wall_record_pass_observation.json').write_text(json.dumps(v));rejected=False
  try:verify(T,EXE,MAP)
  except AssertionError:rejected=True
  assert rejected,case;out.append({'case':case,'rejected':True,'raw_RPC_and_memory_hashes_updated_consistently':True})
(R/'outputs/wall_passes_20261106/negative_validation.json').write_text(json.dumps({'status':'THREE_SEMANTIC_TAMPER_CASES_REJECTED','cases':out},indent=2));print(json.dumps(out))
