import json,tempfile,shutil,base64,hashlib,sys
from pathlib import Path
from verify_p_native_selection import verify
d=Path(sys.argv[1]);assert verify(d)['episode']==3
for field in ('loader_arguments','cache_after'):
 with tempfile.TemporaryDirectory() as tmp:
  t=Path(tmp)
  for p in d.glob('rpc_*.json'):shutil.copy2(p,t/p.name)
  s=json.loads((d/'native_episode3_observation.json').read_text());x=s[field]['stack' if field=='loader_arguments' else 'destination'];b=bytearray(base64.b64decode(x['result']['data_base64']));b[4 if field=='loader_arguments' else 8]^=1;x['result']['data_base64']=base64.b64encode(b).decode();x['result']['sha256']=hashlib.sha256(b).hexdigest()
  for p in t.glob('rpc_*.json'):
   r=json.loads(p.read_text())
   if r['response']['id']==x['id']:r['response']=x;p.write_text(json.dumps(r));break
  (t/'native_episode3_observation.json').write_text(json.dumps(s))
  try:verify(t)
  except AssertionError:pass
  else:raise AssertionError('Coherent mutation accepted: '+field)
print(json.dumps({'status':'PASS','coherent_proof_and_raw_RPC_mutations_rejected':2}))
