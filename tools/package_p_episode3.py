import json,base64,hashlib,zipfile,shutil
from pathlib import Path
from verify_p_native_selection import verify
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_episode3_p_20261107';O=R/'outputs/episode3_p_20261107';O.mkdir(exist_ok=True);H=lambda b:hashlib.sha256(b).hexdigest()
validation=verify(D);(O/'selection_validation.json').write_text(json.dumps(validation,indent=2))
ctl=json.loads((R/'work/runtime/rng_p_target_control.json').read_text());assert ctl['observations']==0 and ctl['pending'] is None and ctl['operation_id'] is None
c=json.loads((D/'current_context.json').read_text());assert c['status']['result']['state']=='stopped';assert len(c['breakpoints']['result']['breakpoints'])==10
raw={}
for p in D.glob('rpc_*.json'):
 x=json.loads(p.read_text());raw[x['response']['id']]=x
snap=[]
for name in ('p_initial','p_after180','p_after300'):
 s=json.loads((D/(name+'.json')).read_text())
 for x in [*s['reads'].values(),*[r['object_read'] for r in s['rows']]]:
  assert raw[x['id']]['response']==x;b=base64.b64decode(x['result']['data_base64']);assert H(b)==x['result']['sha256']
 assert len(s['rows'])==28 and s['type_histogram']=={'26':18,'28':6,'27':3,'29':1}
 selected=[{k:r[k] for k in ('slot','type','state','mode','direction','tile_delta_to_player','within_helper_axis8')} for r in s['rows'] if r['type'] in range(27,32)]
 assert all(not r['within_helper_axis8'] for r in selected)
 snap.append({'name':name,'counter':int.from_bytes(base64.b64decode(s['reads']['world_counter']['result']['data_base64']),'little'),'type_histogram':s['type_histogram'],'selected':selected})
assert [x['counter'] for x in snap]==[2,218,345] and c['words']['RNG']==[1,0]
summary={'status':'VERIFIED_BOUNDED_NO_TARGET_CAPTURE','requested_completed_intervals_seconds':[180,120],'target_observations':0,'snapshots':snap,'final_RNG_state':1,'all_initial_actors_mode0':True,'remaining_targets':9,'next_load_sentinel_armed':True,'scope':'Endpoint actor data; no all-intervening-state/writer/IRQ ledger or constructor-domain closure. Distance predicate modeled from prior helper analysis, not native helper return captures.'}
(O/'search_validation.json').write_text(json.dumps(summary,indent=2))
for name in ('scenario.json','input_manifest.json','startup_identity.json'):shutil.copy2(D/name,O/name)
shutil.copy2(R/'work/runtime/rng_p_negative_validation.json',O/'negative_validation.json')
remaining=json.loads((R/'outputs/target_maps_20261107/remaining_RNG_targets.json').read_text());remaining['P_case']={'episode':3,'level_index':0,'target_hits':0,'counter_end':345,'RNG_state':1,'native_selection_proved':True,'scope':'No universal unreachability claim.'};(O/'remaining_RNG_targets.json').write_text(json.dumps(remaining,indent=2))
report='''# Native episode3 selection and bounded RNG test — P, 2026-11-07

Independent original DOS20 run P PID50760, loadbase0822, uses the same pinned packed executable and emulator as O. The supplied24 present game files are hash-revalidated. Only MAP.1/MAP.2 availability and input CONFIG byte8 (1 to0) differ from the source directory. These are explicit input variants. Fourteen API memory writes are all two-byte BIOS queue/tail fixtures; no loader, actor, coordinates, RNG or executable API write is present. Physical keyboard/IRQ9 parity is not claimed.

The visually inspected paused page projection shows Demo selected. Native0D29:28BE copies16 configuration bytes exactly. Its source byte8 is1 despite the inputfile0; the intervening writer has not been localized. Native28C9 clears DS4153/Omnificent1 to0. This corroborates its Demo clear behavior; no new full writer-domain closure is claimed. Cached configuration and file configuration must not be conflated.

Native2696 is entered with its26E6 FAR-compatible return frame. At26B7, three original near filename pointers and mode4 arguments name map.1/map.2/map.3. Returns at26BC areFFFF/FFFF/0. The conditional083D:29CA(1) call returns nonzero DX:AX (2F93:363B); its broader semantic meaning remains unknown. Native26E6 returnsAX3. At26F4 the unmodified PUSH-CS frame contains runtimeCS,level0,episode3. The loader's097D store and06B0:02E0 header confirm episode3/index0. This is native selection from file availability, unlike O's explicit loader argument fixture. Error/scan/all episode domains remain open.

The independent verifier correlates saved responses with rawRPC IDs/serverPID, byte lengths/hashes, arguments, cache and native header. It checks every API memory write lies in the BIOS queue and revalidates the input manifest. Two coherent proof-plus-rawRPC mutations (episode argument and cached option) are rejected. Four existing function records are byte-matched to the pinned unpacked image, retaining their boundary status and whole-domain UNKNOWN limits.

Initial endpoint data contains28 actors:18 type26,6 type28,3 type27,1 type29; allmode0. This supplies the type27..31 candidate family for083D:18F2, but does not prove execution of its constructor or attack callback. Two completed requested wall-time intervals,180 and120 seconds, advance the original counter2 to218 to345 with zero new target captures. At each captured endpoint all10 type27..31 actors are outside the helper axis8 predicate and remainstate7. These are endpoint predicate observations, not traced native helper return values or all-intervening-state proofs. Final RNG state remains1. No universal target unreachability or entire-map coverage is inferred.

The process is preserved stopped with nine remaining RNG target breakpoints and one next-loader sentinel0D29:26F4; no RNG return or operation is pending. All nine target sites remain open. For04C7:0C37 the established required path remains state7,Omnificent0,accepted native helper0F75 and mode3. This map's initialmode0 actors do not supply that condition. Prior Cemetery explodable-door/path hypotheses remain unverified; no successful nativeC37 hit is claimed. Complete DOS/Win16, IRQ, alias/writer, function boundary and original-versus-remake parity work remains ACTIVE. Raw traces, supplied assets and page images stay local; public artifacts contain derived evidence and reproducibility sources.
'''
(O/'episode3_report.md').write_text(report,encoding='utf-8')
resume={'pid':50760,'endpoint':r'\\.\pipe\dosbox-agent-codex-episode3-p-20261107','loadbase':'0822','control':ctl,'counter':345,'context_pc':{'cs':c['registers']['result']['segments']['cs'],'ip':c['registers']['result']['instruction_pointer']},'goal_status':'ACTIVE','scope':'Preserve P and earlier N/O sessions; sentinel prevents silently mixing another native load.'};(O/'resume.json').write_text(json.dumps(resume,indent=2))
sources=['prepare_rng_p.py','arm_p_native_load.py','runtime_p_native_load.py','verify_p_native_selection.py','test_p_selection_verifier.py','update_p_records.py','package_p_episode3.py','runtime_rng_target_probe.py','runtime_probe.py','runtime_actor_eligibility_snapshot.py','runtime_rng_target_context.py']
for name in sources:shutil.copy2(R/'work'/name,O/name)
files={f'runtime/{p.relative_to(D).as_posix()}':p.read_bytes() for p in D.rglob('*') if p.is_file()}
for p in O.iterdir():
 if p.is_file() and p.name!='checkpoint_validation.json':files[p.name]=p.read_bytes()
for p in (R/'work/runtime').glob('rng_p*.log'):files['logs/'+p.name]=p.read_bytes()
for n in ('runtime_trace_index.json','function_callgraph.json'):files['canonical/'+n]=(R/'outputs/evidence'/n).read_bytes()
manifest={n:{'sha256':H(b),'bytes':len(b)} for n,b in files.items()};files['manifest.json']=json.dumps({'parent_checkpoint_sha256':'cd9fa907fcc821e5c740778baed2b8151191476b8b5ad1f2d5aee36913e17e34','files':manifest},indent=2).encode();z=R/'outputs/Nitemare3D_episode3_P_checkpoint_20261107.zip';assert not z.exists()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for n,b in files.items():a.writestr(n,b)
with zipfile.ZipFile(z) as a:
 assert a.testzip() is None and set(a.namelist())==set(files)
 for n,b in files.items():assert a.read(n)==b
v={'status':'VERIFIED_CRC_EXACT_SET_ALL_HASHES','archive':str(z),'sha256':H(z.read_bytes()),'manifest_files':len(manifest)};(O/'checkpoint_validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
