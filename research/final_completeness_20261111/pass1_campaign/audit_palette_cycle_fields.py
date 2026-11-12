"""python audit_palette_cycle_fields.py IMAGE RUNTIME WORK OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,runtime,work,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['palette_cycle_verified'];out.mkdir(exist_ok=True)
for x in proof['files']:assert sha(Path(x['path']).read_bytes())==x['sha256']
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));source=Path(next(x['source'] for x in inputs if Path(x['source']).name.upper()=='MAP.1'));raw=source.read_bytes()[514:8706];endpoint=(work/'noncode_tail_final.bin').read_bytes()[0x2570e-0x1bda2:0x2770e-0x1bda2];rows=[]
for n,(a,z) in enumerate(zip(raw,endpoint)):
 if a!=z:rows.append(dict(map_byte_offset=n,image_offset=0x2570e+n,cell_index=n//2,storage_major_index=n//128,storage_minor_index=n//2%64,cell_byte=n%2,initial=a,endpoint=z,scope='raw64x64 stride2 storage indices; worldX/Y and writer not assigned'))
assert len(rows)==4 and all(x['cell_byte']==1 for x in rows);save('map_endpoint_differences',rows)
stops=json.loads((runtime/'input_stops.json').read_text());ports=[];phases=[]
for x in stops:
 p=x['prefix'];q=x['registers']
 if x['stage'].startswith('palette_out_'):ports.append(dict(stage=x['stage'],runtime_cs=q['CS'],ip=q['IP'],DX_port=q['DX'],AL_value=q['AX']&255))
 if x['stage'] in ('palette_reset_branch','palette_flash_branch','palette_dark_branch','palette_rng_return','palette_followup_return'):
  count,phase=struct.unpack('<HB',(work/(p+'palette_effect_state.bin')).read_bytes());phases.append(dict(stage=x['stage'],countdown=count,phase=phase,rng_state=int.from_bytes((work/(p+'rng_state.bin')).read_bytes(),'little'),AX=q['AX'],world_counter=int.from_bytes((work/(p+'world_counter.bin')).read_bytes(),'little')))
assert len(ports)==24 and len(phases)==5;save('native_OUT_trace',ports);save('native_phase_trace',phases)
s=dict(native_colour_calls=6,native_OUT_instructions=24,native_phase_markers=5,native_rng_seed_before=proof['native_rng_seed_before'],native_rng_seed_after=proof['native_rng_seed_after'],native_rng_AX=proof['native_rng_AX'],next_dark_countdown=proof['next_dark_countdown'],map_endpoint_differences=4,map_differences_all_cell_byte1=True,new_file_data_bytes=0,new_deep_verified_bytes=0,scope='native first full palette cycle and RNG transition; four mapBYTE1 endpoint differences observed but writer, object identity and world axes unassigned; per-tick call count and audible audio not observed',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,runtime/'independent_verification.json',source,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
