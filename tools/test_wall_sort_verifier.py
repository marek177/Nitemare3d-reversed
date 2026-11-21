import json,base64,hashlib,shutil,tempfile
from pathlib import Path
from verify_wall_sort import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';EXE='C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe';out=[]
for case in ('indirect_target','comparator_result','pointer_permutation'):
 with tempfile.TemporaryDirectory(prefix='wall_sort_negative_',dir=R/'work') as name:
  T=Path(name)
  for p in D.glob('rpc_*.json'):shutil.copy2(p,T/p.name)
  v=json.loads((D/'wall_sort_observation.json').read_text());records={r['response']['id']:(p,r) for p in T.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
  def memory(x,b):
   x['result']['data_base64']=base64.b64encode(b).decode();x['result']['sha256']=hashlib.sha256(b).hexdigest();p,r=records[x['id']];r['response']=x;p.write_text(json.dumps(r))
  if case=='indirect_target':
   x=v['callbacks'][0]['operand'];b=bytearray(base64.b64decode(x['result']['data_base64']));b[0]^=1;memory(x,b)
  elif case=='pointer_permutation':
   x=v['sorts'][0]['after']['groups'];b=bytearray(base64.b64decode(x['result']['data_base64']));b[8:10]=b[10:12];memory(x,b)
  else:
   ar=v['callbacks'][0]['after_registers'];found=[(p,r) for p,r in records.values() if r['request']['method']=='state.get_registers' and r['response'].get('result')==ar];assert found;ar['general']['eax']=f"0x{int(ar['general']['eax'],16)^1:08X}"
   for p,r in found:r['response']['result']=ar;p.write_text(json.dumps(r))
  (T/'wall_sort_observation.json').write_text(json.dumps(v));rejected=False
  try:verify(T,EXE)
  except AssertionError:rejected=True
  assert rejected,case;out.append({'case':case,'rejected':True,'corresponding_raw_RPC_updated':True})
(R/'outputs/wall_sort_20261106/negative_validation.json').write_text(json.dumps({'status':'THREE_SEMANTIC_TAMPER_CASES_REJECTED','cases':out},indent=2));print(json.dumps(out))
