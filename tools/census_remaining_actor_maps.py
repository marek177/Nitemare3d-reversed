import json,struct,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];G=R/'work/runtime/game_rng_targets_i_20261031';O=R/'outputs/target_maps_20261107';O.mkdir(exist_ok=True);sources=[];rows=[]
for ep in (1,2,3):
 b=(G/f'MAP.{ep}').read_bytes();count=struct.unpack_from('<H',b)[0];assert len(b)==514+8192*count;sources.append({'file':f'MAP.{ep}','sha256':hashlib.sha256(b).hexdigest(),'levels':count});types=b[258:514]
 for level in range(count):
  m=b[514+8192*level:514+8192*(level+1)];starts=[[i%64,i//64] for i in range(4096) if 1<=m[2*i+1]<=4];hist=collections.Counter(types[m[2*i+1]] for i in range(4096) if 8<=types[m[2*i+1]]<=33);candidates=[]
  for i in range(4096):
   typ=types[m[2*i+1]]
   if typ not in (9,10,17,18,19,20,27,28,29,30,31):continue
   x,y=i%64,i//64;distance=min((max(abs(x-px),abs(y-py)) for px,py in starts),default=None);candidates.append({'tile':[x,y],'type':typ,'object_id':m[2*i+1],'wall_id':m[2*i],'wall_class':b[2+m[2*i]],'nearest_start_axis_distance':distance})
  rows.append({'episode':ep,'level_index':level,'display_level':level+1,'starts':starts,'actor_type_histogram':dict(hist),'candidates':sorted(candidates,key=lambda c:(c['nearest_start_axis_distance'] if c['nearest_start_axis_distance'] is not None else 999,c['type'],c['tile']))})
ranked=[{'episode':r['episode'],'display_level':r['display_level'],'near':[c for c in r['candidates'] if c['type'] in (9,10)][:3]} for r in rows if any(c['type'] in (9,10) for c in r['candidates'])];ranked.sort(key=lambda r:min(c['nearest_start_axis_distance'] for c in r['near'] if c['nearest_start_axis_distance'] is not None))
v={'status':'VERIFIED_STATIC_ASSET_CENSUS','sources':sources,'maps':rows,'scope':'Original header object-type/spawn-cell candidates. No native construction, mode/state, facing/ray, path/collision, hit or target invocation proof.'};(O/'remaining_actor_map_census.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({'maps':len(rows),'selector9_10_maps':ranked[:8]}))

