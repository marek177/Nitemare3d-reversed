import json,base64,hashlib,shutil,tempfile,time
from pathlib import Path
from verify_o_level_fixture import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level1_o_20261107';G=R/'work/runtime/game_rng_level1_o_20261107';out=[]
for case in ('loader_argument','cached_option','header_seed'):
 with tempfile.TemporaryDirectory(prefix='level1_fixture_negative_',dir=R/'work') as name:
  T=Path(name);cutoff=time.time()-1
  for p in D.glob('rpc_*.json'):
   if p.stat().st_mtime<cutoff:shutil.copy2(p,T/p.name)
  for n in ('startup_identity.json','input_manifest.json','menu_input_fixture.json'):shutil.copy2(D/n,T/n)
  v=json.loads((D/'level1_fixture_observation.json').read_text());records={r['response']['id']:(p,r) for p in T.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
  x,index,value=(v['argument_fixture']['stack_after'],2,1) if case=='loader_argument' else (v['native_cache_after']['destination'],8,0) if case=='cached_option' else (v['header']['RNG'],0,2)
  b=bytearray(base64.b64decode(x['result']['data_base64']));b[index]=value;x['result']['data_base64']=base64.b64encode(b).decode();x['result']['sha256']=hashlib.sha256(b).hexdigest();p,r=records[x['id']];r['response']=x;p.write_text(json.dumps(r));(T/'level1_fixture_observation.json').write_text(json.dumps(v));rejected=False
  try:verify(T,G/'MAP.1',G/'DEMO.1')
  except AssertionError:rejected=True
  assert rejected,case;out.append({'case':case,'rejected':True,'corresponding_raw_RPC_and_hash_updated':True})
(R/'outputs/target_maps_20261107/negative_validation.json').write_text(json.dumps({'status':'THREE_SEMANTIC_TAMPER_CASES_REJECTED','cases':out},indent=2));print(json.dumps(out))
