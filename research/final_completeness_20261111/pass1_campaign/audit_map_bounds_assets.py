"""OUTPUTS GAME_DIR: exact shipped MAP bounds/start/border evidence; finite asset facts,not movement invariants."""
import csv,hashlib,json,struct,sys
from pathlib import Path
root,game=map(Path,sys.argv[1:]);out=root/'map_bounds_assets';out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();manifest=list(csv.DictReader((root/'map_level_loader_replay/assets.csv').open()));truth=list(csv.DictReader((root/'classification_producers_replay/value_flag_truth_table.csv').open()));flags={int(x['input_BYTE']):int(x['output_low7']) for x in truth if x['function']=='tile_flags_generate'};levels=[];border=[];spawns=[];files=[]
for m in manifest:
 ep=int(m['episode']);p=game/('MAP.%d'%ep);b=p.read_bytes();assert sha(b)==m['sha256'] and len(b)==int(m['length']);n=struct.unpack_from('<H',b)[0];assert n==int(m['levels']) and len(b)==514+8192*n;terrain=b[2:258];objects=b[258:514]
 for level in range(n):
  a=514+8192*level;grid=b[a:a+8192];starts=[];holes=[]
  for y in range(64):
   for x in range(64):
    k=2*(y*64+x);t,o=grid[k:k+2];kind=terrain[t];f=flags[kind]
    if objects[o]==2:
     rec=dict(episode=ep,level_zero_based=level,x=x,y=y,fineX_center=32+64*x,fineY_center=32+64*y,object_BYTE=o,object_kind=2,file_object_byte=a+k+1);starts.append(rec);spawns.append(rec)
    if x in (0,63) or y in (0,63):
     rec=dict(episode=ep,level_zero_based=level,x=x,y=y,file_terrain_byte=a+k,terrain_BYTE=t,terrain_kind=kind,terrain_flags_low7=f,immediate_ray_block=bool(f&2 and f&4),door_query_required=bool(f&2 and not(f&4) and f&8));border.append(rec)
     if not rec['immediate_ray_block']:holes.append(rec)
  levels.append(dict(episode=ep,level_zero_based=level,payload_start=a,payload_end_exclusive=a+8192,payload_sha256=sha(grid),spawn_count=len(starts),spawn_interior=all(1<=x['x']<=62 and 1<=x['y']<=62 for x in starts),border_cells=252,border_not_immediate_ray_block=len(holes),terrain_kind44_types=json.dumps([i for i,k in enumerate(terrain) if k==68])))
 files.append(dict(path=str(p.resolve()),sha256=sha(b)))
def save(n,r):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
save('levels',levels);save('border_cells',border);save('spawn_cells',spawns);non=[x for x in border if not x['immediate_ray_block']];save('border_exceptions',non);summary=dict(levels=len(levels),border_cells=len(border),spawn_cells=len(spawns),all_one_spawn=all(x['spawn_count']==1 for x in levels),all_spawn_interior=all(x['spawn_interior'] for x in levels),border_immediate_block=sum(x['immediate_ray_block'] for x in border),border_exceptions=len(non),exception_kind_BYTE_pairs=sorted(set((x['terrain_kind'],x['terrain_BYTE']) for x in non)),runtime_tests=0,new_deep_verified_bytes=0,scope='Exact original asset/header/payload facts using prior verified low7classification truth table; inheritedbit80 irrelevantto2/4/8. No fullmovement,bounds-preservation,leveltransition,mutableworld/SAVELOAD or naturalOOBproof.',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (root/'map_level_loader_replay/assets.csv',root/'classification_producers_replay/value_flag_truth_table.csv',Path(__file__))]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
