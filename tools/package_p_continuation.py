import json,base64,hashlib,zipfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_episode3_p_20261107';O=R/'outputs/episode3_p_continuation_20261107';H=lambda b:hashlib.sha256(b).hexdigest();ctl=json.loads((R/'work/runtime/rng_p_target_control.json').read_text());assert ctl['pending'] is None and ctl['operation_id'] is None
c=json.loads((D/'current_context.json').read_text());assert c['status']['result']['state']=='stopped'
s=json.loads((D/'p_after540.json').read_text());counter=int.from_bytes(base64.b64decode(s['reads']['world_counter']['result']['data_base64']),'little');targets=[r for r in s['rows'] if r['type'] in range(27,32)]
summary={'status':'VERIFIED_ENDPOINT_DATA_WITH_BOUNDED_SEARCH','requested_interval_seconds':240,'counter_before':345,'counter_after':counter,'phase':ctl['phase'],'new_target_observations':ctl['observations'],'RNG_words':c['words']['RNG'],'actor_types':s['type_histogram'],'type27_31_endpoint_rows':[{k:r[k] for k in ('slot','type','state','mode','direction','tile_delta_to_player','within_helper_axis8')} for r in targets],'breakpoint_count':len(c['breakpoints']['result']['breakpoints']),'scope':'Endpoint data and generic probe result; no all-intervening writes/IRQ or universal reachability closure.'}
assert ctl['observations']==0
raw={}
for p in D.glob('rpc_*.json'):
 x=json.loads(p.read_text());assert x['server_pid']==50760;raw[x['response']['id']]=x
for x in [*s['reads'].values(),*[r['object_read'] for r in s['rows']],c['status'],c['registers'],c['breakpoints']]:
 assert raw[x['id']]['response']==x
 if 'data_base64' in x['result']:assert H(base64.b64decode(x['result']['data_base64']))==x['result']['sha256']
(O/'continuation_validation.json').write_text(json.dumps(summary,indent=2))
report=f'''# P continuation and episode gate contract — 2026-11-07

Previous turn was progress: independentP natural episode3/index0 selection and two completed intervals were published inaa56ff63dc283c52fa705b29fb1a843cf99e4365. This continuation revalidates the same livePID50760/start time and debugger endpoint, then runs another requested240-second target-search interval, preserving its operation handle across wait timeouts. The original counter advances345 to{counter}. Target captures remain0; RNG endpoint words are{c['words']['RNG']}. Actual endpoint actor rows and breakpoint state are retained in continuation_validation.json. This is not universal target unreachability, full map-state coverage or an IRQ/writer ledger.

The previously unnamed083D:29CA(1) gate is now resolved locally. Original guardCMP AX,5/JA bounds six word targets inCS:[29E0], namely29F2,2A7C,2A90,2A9A,2AA8,2AB6. Selector1 at2A7C checks byteDS363B and returnsDX:AX=DS:363B if nonzero, otherwise0:0. Selector2 returnsDS:363C. The earlier nativeP26C5/26CA observation2F93:363B is therefore a nonnull pointer return, not boolean1 or a proved episode-specific entitlement.

An isolated original-instruction CPU matrix checks1028 cases: selectors1/2 over256 bytevalues and twoDS values, plus invalidselectors6/FFFF. FAR return, caller-retained argument, preserved register fixtures and bothDF values are checked. Invalidselectors skip to29EC and expose incoming uninitialized localsBP-4/BP-2; this function is not a generally safe out-of-range query. These are synthetic original-byte executions, not additional game call coverage. Selector0 contains literalrb/nite3d.bsf, a36h-byte header request intoDS3638 and further callees; file decoding, error behavior and selectors0/3/4/5 remain partial. The original input header is not silently equated with its runtime buffer.

Read-only native endpoint capture independently matches all269 loaded envelopebytes after every MZ relocation. It correlates rawRPC/PID/revisions and captures the54-byte current header buffer. This proves current code/table integrity and data, not execution of header initialization or absence of intervening writers. The canonical function record and CFG retain UNKNOWN whole boundaries with a bounded six-target switch annotation; no global indirect census row is removed or closed.

Nine RNG target sites, successful04C7:0C37, natural Cemetery interaction/path, global function ownership/alias/IRQ/timing and nativeWin16/remake parity remain open. Full GOAL stays ACTIVE. Supplied assets and full raw runtime captures remain local. The checkpoint is an immutable child ofP70860fa31161ec49f11e7ff82273290ff7c2d537f68e824fd97fcdb11072f9db.
'''
(O/'continuation_report.md').write_text(report,encoding='utf-8')
for n in ['verify_episode_gate_cpu.py','runtime_p_gate_snapshot.py','verify_p_gate_snapshot.py','package_p_continuation.py']:shutil.copy2(R/'work'/n,O/n)
files={f'runtime/{p.relative_to(D).as_posix()}':p.read_bytes() for p in D.rglob('*') if p.is_file()}
for p in O.iterdir():
 if p.is_file() and p.name!='checkpoint_validation.json':files[p.name]=p.read_bytes()
for n in ['rng_p_revalidate.log','rng_p_search240.log','rng_p_actors540.log','rng_p_context540.log','rng_p_gate_snapshot.log']:files['logs/'+n]=(R/'work/runtime'/n).read_bytes()
files['control/rng_p_target_control.json']=(R/'work/runtime/rng_p_target_control.json').read_bytes();manifest={n:{'sha256':H(b),'bytes':len(b)} for n,b in files.items()};files['manifest.json']=json.dumps({'parent_checkpoint_sha256':'70860fa31161ec49f11e7ff82273290ff7c2d537f68e824fd97fcdb11072f9db','files':manifest},indent=2).encode();z=R/'outputs/Nitemare3D_episode3_P_continuation_checkpoint_20261107.zip';assert not z.exists()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for n,b in files.items():a.writestr(n,b)
with zipfile.ZipFile(z) as a:
 assert a.testzip() is None and set(a.namelist())==set(files)
 for n,b in files.items():assert a.read(n)==b
v={'status':'VERIFIED_CRC_EXACT_SET_ALL_HASHES','archive':str(z),'sha256':H(z.read_bytes()),'manifest_files':len(manifest)};(O/'checkpoint_validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
