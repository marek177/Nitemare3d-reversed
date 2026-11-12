"""python audit_palette_writer_fields.py IMAGE RUNTIME WORK INVENTORY OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,runtime,work,inventory,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['palette_reset_writer_verified'];out.mkdir(exist_ok=True)
for x in proof['files']:assert sha(Path(x['path']).read_bytes())==x['sha256']
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
stops=json.loads((runtime/'input_stops.json').read_text());ports=[];effects=[]
for x in stops:
 q=x['registers'];p=x['prefix']
 if x['stage'].startswith('palette_out_'):ports.append(dict(stage=x['stage'],runtime_cs=q['CS'],ip=q['IP'],DX_port=q['DX'],AL_value=q['AX']&255,effect_state_hex=(work/(p+'palette_effect_state.bin')).read_bytes().hex(),scope='native original OUT instruction breakpoint, debugger did not write DAC ports'))
 if x['stage'] in ('palette_effect_entry','palette_effect_exit'):
  count,phase=struct.unpack('<HB',(work/(p+'palette_effect_state.bin')).read_bytes());frame=(work/(p+'palette_stack.bin')).read_bytes();retip,retcs,arg=struct.unpack_from('<HHH',frame);effects.append(dict(stage=x['stage'],countdown=count,phase=phase,caller_return_cs=retcs,caller_return_ip=retip,argument_WORD=arg,argument_low_BYTE=arg&255))
save('native_port_trace',ports);save('native_effect_states',effects)
fields=[]
for name,ds_off,length,typ in [('palette_countdown',0x3634,2,'WORD post-decrement countdown, expires when prior value is zero'),('palette_phase',0x3636,1,'BYTE zero/nonzero phase, assigned0/1'),('palette_scene_index',0xd2f7,1,'BYTE DAC index used with fixed235, native current227')]:fields.append(dict(name=name,canonical_ds=0x2771,ds_offset=ds_off,image_equivalent_start=0x27710+ds_off,length=length,type=typ,status='PARTIAL',outside_file_image=True,adds_to_PASS320=False))
save('runtime_scalar_fields',fields)
b=image.read_bytes();context=[]
for x in json.loads(inventory.read_text()):
 if x['cs']==0x83d and 0xea0<=x['ip']<0xeb1:
  raw=bytes.fromhex(x['bytes']);assert b[x['image_offset']:x['image_offset']+len(raw)]==raw;context.append(x)
assert len(context)==5 and sum(len(bytes.fromhex(x['bytes'])) for x in context)==17;save('followup_EA0_audio_wrapper_context',context)
s=dict(native_OUT_instructions=len(ports),native_effect_state_points=len(effects),runtime_scalar_fields=3,runtime_scalar_bytes_outside_file=4,new_file_data_bytes=0,new_deep_verified_bytes=0,scope='native reset caller writes fixed235 and scene227 black; first palette tick only decrements80to79; EA0 context pushes id66 and DWORD20000 to0C2B:03D6, no audible-output or full downstream audio closure',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,runtime/'independent_verification.json',inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
