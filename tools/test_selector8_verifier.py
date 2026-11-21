import json,shutil,tempfile
from pathlib import Path
from verify_selector8_runtime import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_targets_m_20261106';MAP=R/'work/runtime/game_rng_targets_m_20261106/MAP.2';O=R/'outputs/selector8_20261106';results=[]
with tempfile.TemporaryDirectory(prefix='selector8_verify_',dir=R/'work') as t:
 T=Path(t);assert T.resolve().is_relative_to((R/'work').resolve());shutil.copytree(D,T,dirs_exist_ok=True);assert verify(T,MAP)['health_after']==96
 cases=[('wrong_consumer_result','selector8_consumer_observation.json',lambda x:x.update(result_AX=3)),('wrong_wall_class','selector8_consumer_observation.json',lambda x:x['map_class_provenance'].update(wall_class_from_loaded_header=66)),('wrong_health_read','selector8_health_observation.json',lambda x:x['after_health']['health']['result'].update(data_base64='YQ=='))]
 for name,file,mutate in cases:
  original=(T/file).read_text();v=json.loads(original);mutate(v);(T/file).write_text(json.dumps(v))
  try:verify(T,MAP)
  except AssertionError:results.append({'case':name,'rejected':True})
  else:raise RuntimeError('Accepted altered proof: '+name)
  (T/file).write_text(original)
(O/'verifier_negative_validation.json').write_text(json.dumps({'positive_original_accepted':True,'negative_cases':results,'scope':'Proof-verifier integrity only; no additional game coverage'},indent=2),encoding='utf-8');print(json.dumps(results))
