"""Conservative static bit2-clear cell connectivity, not movement/collision proof."""
import json,base64,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'outputs/mode3_movement_20261106';m=(R/'work/runtime/game_rng_targets_i_20261031/MAP.1').read_bytes()[514+5*8192:514+6*8192];t=base64.b64decode(json.loads((R/'outputs/evidence/runtime/rng_level5_n_20261106/wall_object_traits_capture.json').read_text())['traits']['result']['data_base64']);prev={(27,32):None};q=collections.deque(prev)
while q:
 x,y=q.popleft()
 for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
  a,b=p
  if 0<=a<64 and 0<=b<64 and p not in prev and not t[m[2*(b*64+a)]]&2:prev[p]=(x,y);q.append(p)
out=[]
for a in json.loads((O/'nearby_ray_cases_local.json').read_text()):
 p=tuple(a['start'])
 if a.get('AL')==1 and p in prev:
  path=[]
  while p is not None:path.append(p);p=prev[p]
  out.append({'actor':a['tile'],'path':path[::-1]})
out.sort(key=lambda a:len(a['path']));frontier={}
for x,y in prev:
 for a,b in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
  if 0<=a<64 and 0<=b<64 and (a,b) not in prev:
   wall=m[2*(b*64+a)];flags=t[wall]
   if flags&8 and not flags&4:frontier[(a,b)]={'tile':[a,b],'wall_id':wall,'traits':flags,'adjacent_component_tile':[x,y]}
classes=(R/'work/runtime/game_rng_targets_i_20261031/MAP.1').read_bytes()[2:258];special={}
for x,y in prev:
 for a,b in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
  if 0<=a<64 and 0<=b<64 and (a,b) not in prev:
   wall=m[2*(b*64+a)];cls=classes[wall]
   if cls in (9,10,12,0x2e,0x2f):special[(a,b)]={'tile':[a,b],'wall_id':wall,'class':cls,'traits':t[wall],'adjacent_component_tile':[x,y]}
v={'status':'STATIC_PLANNING_ONLY','connected_bit2_clear_cells':len(prev),'accepted_connected':len(out),'nearest_routes':out[:8],'conditional_door_frontier':list(frontier.values()),'special_class_frontier':list(special.values()),'scope':'Cardinal cell adjacency using captured wall-trait bit2 clear. Door cells excluded; no object collision, player radius, exact input/rotation, native movement or successfulC37 proof. Special class9/10/12/2E/2F frontier is a candidate query, not a proved operation. All routes require original-game verification.'};(O/'floor_route_plan.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
