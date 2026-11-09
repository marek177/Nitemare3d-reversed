import json,shutil,tempfile,base64
from pathlib import Path
from verify_n_mode2_runtime import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';MAP=R/'work/runtime/game_rng_level5_n_20261106/MAP.1';O=R/'outputs/level_fixture_20261106';results=[]
with tempfile.TemporaryDirectory(prefix='mode2_verify_',dir=R/'work') as t:
 T=Path(t);assert T.resolve().is_relative_to((R/'work').resolve());shutil.copytree(D,T,dirs_exist_ok=True);assert verify(T,MAP)['timer']==14
 def wrongmode(v):
  a=bytearray(base64.b64decode(v['before']['actor']['result']['data_base64']));a[10]=0;v['before']['actor']['result']['data_base64']=base64.b64encode(a).decode()
 cases=[('wrong_level_fixture','level_fixture_ctor_observation.json',lambda x:x['level_argument_fixture'].update(selected_level_index=3)),('wrong_timer','mode2_consumer_observation.json',lambda x:x.update(timer_expected=15)),('wrong_mode','mode2_consumer_observation.json',wrongmode)]
 for name,file,mutate in cases:
  original=(T/file).read_text();v=json.loads(original);mutate(v);(T/file).write_text(json.dumps(v))
  try:verify(T,MAP)
  except AssertionError:results.append({'case':name,'rejected':True})
  else:raise RuntimeError('Accepted altered proof '+name)
  (T/file).write_text(original)
(O/'verifier_negative_validation.json').write_text(json.dumps({'positive_original_accepted':True,'negative_cases':results,'scope':'Proof integrity tests only; not additional original path coverage'},indent=2),encoding='utf-8');print(json.dumps(results))
