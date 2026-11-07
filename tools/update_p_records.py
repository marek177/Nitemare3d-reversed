import json,shutil,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'outputs/evidence';O=R/'outputs/episode3_p_20261107';O.mkdir(exist_ok=True)
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];proof=[]
for fid in ('0D29:2696','0D29:26E2','0D29:274C','0D29:095A'):
 name='nite3d20_'+fid.replace(':','_')+'.json';p=E/'function_records'/name;v=json.loads(p.read_text());cfg=json.loads((E/'function_cfg'/name).read_text());parts=[]
 for i in sorted(cfg['instructions'],key=lambda x:x['offset']):
  b=bytes.fromhex(i['bytes']);assert im[int(fid[:4],16)*16+i['offset']:int(fid[:4],16)*16+i['offset']+len(b)]==b;parts.append(struct.pack('<HH',i['offset'],len(b))+b)
 v['P_native_episode3_case']={'status':'VERIFIED_RUNTIME_BOUNDED','source':'episode3_p_20261107/episode3_report.md','selection':'Native2696 probes map.1/map.2/map.3; AXFFFF/FFFF/0; conditional gateDX:AX nonzero; returns3 at26E6','loader_frame':['runtimeCS',0,3],'header':'episode3/index0 at06B0:02E0','config':'Native16-byte cache contains option8=1 despite inputfile0; native28C9 clearsOmnificent1-to0. Origin of option8 transition not localized.','scope':'No loader/actor/position/RNG/code API write. File/config input variant and BIOS queue fixtures. Whole boundaries/domains/IRQ/remake parity remainUNKNOWN.'}
 p.write_text(json.dumps(v,indent=2),encoding='utf-8');shutil.copy2(p,O/name);proof.append({'function':fid,'instructions_byte_matched':len(parts),'membership_sha256':hashlib.sha256(b''.join(parts)).hexdigest(),'boundary_status':v['boundary']['boundary_status']})
(O/'record_validation.json').write_text(json.dumps(proof,indent=2))
for filename in ('runtime_trace_index.json','function_callgraph.json'):
 p=E/filename;v=json.loads(p.read_text());v['P_native_episode3_20261107']={'status':'VERIFIED_RUNTIME_BOUNDED','run':'rng_episode3_p_20261107','report':'episode3_p_20261107/episode3_report.md','episode':3,'level_index':0,'whole_domain_or_global_callgraph_complete':False};p.write_text(json.dumps(v,indent=2),encoding='utf-8')
