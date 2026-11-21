import json,shutil,tempfile
from pathlib import Path
from verify_a36_runtime import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_targets_m_20261106';results=[]
with tempfile.TemporaryDirectory(prefix='a36_verify_',dir=R/'work') as t:
 T=Path(t)
 for p in D.glob('rpc_*.json'):shutil.copy2(p,T/p.name)
 names=['startup_identity.json','next_rng_call_observation.json','A36_consumer_observation.json','A36_exit_observation.json'];original={n:(D/n).read_text() for n in names}
 for n,s in original.items():(T/n).write_text(s)
 assert verify(T)['timer']==14
 cases=[('wrong_returned_AX','next_rng_call_observation.json',lambda v:v.update(returned_AX=0)),('wrong_actor_address','A36_consumer_observation.json',lambda v:v.update(actor_off=v['actor_off']+1)),('wrong_timer','A36_consumer_observation.json',lambda v:v.update(expected_timer=15))]
 for name,n,mutate in cases:
  v=json.loads(original[n]);mutate(v);(T/n).write_text(json.dumps(v))
  try:verify(T)
  except AssertionError:results.append({'case':name,'rejected':True})
  else:raise RuntimeError('Tampered proof accepted: '+name)
  (T/n).write_text(original[n])
v={'positive_original_accepted':True,'negative_cases':results,'scope':'Verifier integrity checks only; no new game execution or expanded path coverage'}
O=R/'outputs/a36_20261106';O.mkdir(exist_ok=True);(O/'verifier_negative_validation.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
