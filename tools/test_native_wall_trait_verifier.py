"""Reject coherent but false memory evidence, beyond raw-RPC mismatch guards."""
import json,base64,hashlib,shutil,tempfile
from pathlib import Path
from verify_native_wall_trait import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';EXE='C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe';out=[]
for kind,case in ((k,c) for k in ('wall','object') for c in ('initial_bit7','output_byte','caller_frame')):
 with tempfile.TemporaryDirectory(prefix='native_trait_negative_',dir=R/'work') as name:
  T=Path(name)
  for p in D.glob('rpc_*.json'):shutil.copy2(p,T/p.name)
  v=json.loads((D/f'native_{kind}_trait_observation.json').read_text());records={r['response']['id']:(p,r) for p in T.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
  def alter(x,index,value):
   b=bytearray(base64.b64decode(x['result']['data_base64']));b[index]=value;x['result']['data_base64']=base64.b64encode(b).decode();x['result']['sha256']=hashlib.sha256(b).hexdigest();p,r=records[x['id']];r['response']=x;p.write_text(json.dumps(r))
  if case=='initial_bit7':alter(v['initial_local'],0,128);alter(v['entry_stack'],5,128)
  elif case=='output_byte':
   for key in ('before_return','after_return'):
    x=v[key]['output'];b=base64.b64decode(x['result']['data_base64']);alter(x,0,b[0]^1)
  else:
   x=v['entry_stack'];b=base64.b64decode(x['result']['data_base64']);alter(x,8,b[8]^1)
  (T/f'native_{kind}_trait_observation.json').write_text(json.dumps(v));rejected=False
  try:verify(T,EXE,kind)
  except AssertionError:rejected=True
  assert rejected,case;out.append({'kind':kind,'case':case,'rejected':True,'raw_RPC_and_memory_hashes_updated_consistently':True})
O=R/'outputs/native_trait_20261106';O.mkdir(exist_ok=True);(O/'negative_validation.json').write_text(json.dumps({'status':'SIX_SEMANTIC_TAMPER_CASES_REJECTED','cases':out},indent=2));print(json.dumps(out))
