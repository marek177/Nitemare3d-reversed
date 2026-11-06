"""Plan coordinate fixtures using original helper bytes; no movement proof."""
import json,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=(R/'work/verify_mode3_start_rays.py').read_text();marker="for c in json.loads((O/'mode3_start_candidates.json').read_text())['pre_ray_candidates']:";assert src.count(marker)==1
# Reuse the verified read-only harness setup and exact original CPU frame.
prefix,body=src.split(marker);loop,tail=body.split("v={'status':",1);ns={'__file__':str(R/'work/verify_mode3_start_rays.py')};exec(compile(prefix,'ray_harness_setup','exec'),ns)
O=R/'outputs/mode3_movement_20261106';O.mkdir(exist_ok=True);seeds=json.loads((R/'outputs/mode3_start_20261106/mode3_start_candidates.json').read_text())['pre_ray_candidates'];tests=[]
for c in seeds:
 for py in range(28,37):
  for px in range(23,32):
   t=copy.deepcopy(c);t['selected_start_gate']['start']['tile']=[px,py];tests.append(t)
ns['tests']=tests;exec(compile('for c in tests:'+loop,'ray_coordinate_matrix','exec'),ns);results=ns['results'];assert len(results)==324
accepted=[r for r in results if r.get('AL')==1];accepted.sort(key=lambda r:(abs(r['start'][0]-27)+abs(r['start'][1]-32),r['tile'],r['start']))
map1=ns['map1'];traits=ns['traits']
for r in accepted:
 px,py=r['start'];wall=map1[514+5*8192+2*(py*64+px)];r['target_wall_traits']=traits[wall];r['target_wall_solid_bit4']=bool(traits[wall]&4);r['Manhattan_from_start']=abs(px-27)+abs(py-32)
v={'status':'SYNTHETIC_COORDINATE_MATRIX_ONLY','source_harness_sha256':hashlib.sha256((R/'work/verify_mode3_start_rays.py').read_bytes()).hexdigest(),'cases':len(results),'accepted':len(accepted),'door_lookup_stops':sum(bool(r.get('door_lookup_unmodeled')) for r in results),'nearest_accepted':accepted[:24],'scope':'Original helper/grid and level6 cells with episode1 level10 trait-table fixture, candidate directions unchanged. Player coordinates are synthetic inputs, not game memory writes or native movement. Destination cell, path traversal/collision, mutable actors, native state7 and successfulC37 remain unproved. Endpoint-before-block testing can accept a solid destination; solid flags are reported explicitly.'}
(O/'nearby_ray_matrix.json').write_text(json.dumps(v,indent=2),encoding='utf-8');(O/'nearby_ray_cases_local.json').write_text(json.dumps(results,indent=2));print(json.dumps({'cases':v['cases'],'accepted':v['accepted'],'door_stops':v['door_lookup_stops'],'nearest':v['nearest_accepted'][:4]}))

