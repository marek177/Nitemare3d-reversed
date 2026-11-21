"""Static map candidates, conditional on canonical constructor and start decoding."""
import json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]; G=R/'work/runtime/game_rng_targets_i_20261031'; O=R/'outputs/mode3_start_20261106';O.mkdir(exist_ok=True)
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();H=lambda b:hashlib.sha256(b).hexdigest(); assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:]
cfg=json.loads((R/'outputs/evidence/function_cfg/nite3d20_083D_117A.json').read_text()); matched=0
for i in cfg['instructions']:
 b=bytes.fromhex(i['bytes']);assert im[0x83d*16+i['offset']:0x83d*16+i['offset']+len(b)]==b;matched+=1
table=struct.unpack_from('<26H',im,0x83d*16+0x11b8);assert table[18-8]==table[19-8]==0x11f6
assert im[0x83d*16+0x11fe:0x83d*16+0x1203]==bytes.fromhex('26c6440a03')
sources=[]; rows=[]; near=[]
for ep in (1,2,3):
 b=(G/f'MAP.{ep}').read_bytes();count=struct.unpack_from('<H',b)[0];assert len(b)==514+count*8192;wc=b[2:258];ot=b[258:514];sources.append({'file':f'MAP.{ep}','sha256':H(b),'levels':count})
 for level in range(count):
  m=b[514+level*8192:514+(level+1)*8192];starts=[{'tile':[i%64,i//64],'object_id':m[2*i+1]} for i in range(4096) if 1<=m[2*i+1]<=4]; candidates=[]
  for i in range(4096):
   w,ob=m[2*i:2*i+2];typ=ot[ob]
   if typ not in (18,19):continue
   assert 0xb4<=ob<=0xbb
   direction=2*(ob&3); mode=2 if wc[w] in (0x42,0x46) else 1 if wc[w]==0x43 else 3
   r={'tile':[i%64,i//64],'type':typ,'object_id':ob,'direction_from_asset_encoding':direction,'wall_id':w,'wall_class':wc[w],'mode_after_canonical_constructor':mode,'start_gates':[]}
   for start in starts:
    dx=start['tile'][0]-i%64;dy=start['tile'][1]-i//64;axis=abs(dx)<=8 and abs(dy)<=8;cone=sum(1<<d for d in {(direction-1)&7,direction,(direction+1)&7});mask=(0x66 if abs(dx)>=abs(dy) else 0x99)&(0x3c if dy>=0 else 0xc3)&(0x0f if dx>=0 else 0xf0); facing=bool(cone&mask)
    gate={'start':start,'delta':[dx,dy],'axis8':axis,'direction_mask_nonzero':facing,'nonzero_delta':bool(dx or dy),'pre_ray_candidate':mode==3 and axis and facing and bool(dx or dy)};r['start_gates'].append(gate)
    if gate['pre_ray_candidate']:near.append({'episode':ep,'display_level':level+1,**r,'selected_start_gate':gate})
   candidates.append(r)
  rows.append({'episode':ep,'display_level':level+1,'starts':starts,'candidates':candidates})
v={'status':'VERIFIED_STATIC_CONDITIONAL_CANDIDATES','source_sha256':H(raw),'constructor_instructions_byte_matched':matched,'type18_19_dispatch_target':'083D:11F6','mode3_writer':'083D:11FE','sources':sources,'maps':rows,'pre_ray_candidates':near,'scope':'Static original asset census and conditional axis/direction model. Start IDs1..4 and asset direction mapping are assumptions transferred from prior joins, not newly traced constructor inputs. No ray/wall/door acceptance, actual dispatcher state, native level access, RNG target hit or runtime reachability is claimed.'}
(O/'mode3_start_candidates.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({'maps':len(rows),'candidates':sum(len(x['candidates']) for x in rows),'pre_ray':[{k:x[k] for k in ('episode','display_level','tile','direction_from_asset_encoding','selected_start_gate')} for x in near]}))
