import json,base64,hashlib,zipfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_episode3_p_20261107';O=R/'outputs/bsf_transform_20261107';H=lambda b:hashlib.sha256(b).hexdigest();ctl=json.loads((R/'work/runtime/rng_p_target_control.json').read_text());assert ctl['observations']==0 and ctl['pending'] is None and ctl['operation_id'] is None
c=json.loads((D/'current_context.json').read_text());assert c['status']['result']['state']=='stopped';s=json.loads((D/'p_boundary_end.json').read_text());counter=int.from_bytes(base64.b64decode(s['reads']['world_counter']['result']['data_base64']),'little');raw={}
for p in D.glob('rpc_*.json'):
 x=json.loads(p.read_text());assert x['server_pid']==50760;raw[x['response']['id']]=x
for x in [*s['reads'].values(),*[r['object_read'] for r in s['rows']],c['status'],c['registers'],c['breakpoints']]:
 assert raw[x['id']]['response']==x
 if 'data_base64' in x['result']:assert H(base64.b64decode(x['result']['data_base64']))==x['result']['sha256']
sentinel=json.loads((D/'rng_search_sentinel.json').read_text());assert sentinel['pc']=='0D29:26F4' and ctl['phase']=='sentinel'
import struct
q=sentinel['snapshot']['reads']['stack'];assert raw[q['id']]['response']==q;frame=struct.unpack_from('<3H',base64.b64decode(q['result']['data_base64']));assert frame==(0x154b,0,3)
summary={'status':'VERIFIED_ENDPOINT_WITH_BOUNDED_NO_CAPTURE_SEARCH','requested_seconds':240,'completed_full_budget':False,'counter_before':590,'counter_after':counter,'new_target_hits':0,'RNG_words':c['words']['RNG'],'phase':ctl['phase'],'type27_31_endpoint_rows':[{k:r[k] for k in ('slot','type','state','mode','direction','tile_delta_to_player','within_helper_axis8')} for r in s['rows'] if r['type'] in range(27,32)],'scope':'Endpoint predicates, not every intermediate activation/IRQ/write or universal reachability closure.'};(O/'runtime_validation.json').write_text(json.dumps(summary,indent=2))
report=f'''# BSF header transform and continued RNG search — 2026-11-07

Previous goal turn was progress: bounded selector contracts andP continuation were published inb5c20355845a4da31542cecdf906325a3b330cb7. This turn revalidates the same live originalPID50760 and continues its existing episode3/index0 domain. The next requested240-second interval stops EARLY at the next-loader sentinel0D29:26F4, counter{counter}, after starting at590; no additional target is captured and the full240-second budget is not completed. The cause of this reload is not established. The process remains stopped with no pending return/operation. Endpoint RNG words are{c['words']['RNG']}. Actual actor/distance rows are retained; no all-intervening-state or universal reachability claim follows.

0FBA:01B2 is a bounded in-place byte transform plus checksum. It accepts FAR buffer and16-bit count. For each byte it first XORs the pre-transform byte into a local accumulator, then XORs the buffer withSS:[2045+(index mod52)]. SI wraps16 bits. AL returns the accumulator. A nonzero count leavesDS=SS; count0 preserves incomingDS. AH is not generally zero: for nonzero count it retains the high byte of floor((count-1)/52); count0 retains initialAH. SI/DI/BP and IF/DF are preserved in tested domains. Arbitrary stack/code aliases and IRQ effects remain open. If input overlaps its key, reads see the evolving memory; a fixed immutable-key formula cannot be assumed in that domain.

The supplied52-byte key from the pinned original image transforms the supplied54-byte NITE3D.BSF header exactly into the nativeP endpointbufferDS3638..366D. ChecksumAL is0 and decoded byte3 is1, matching theDS363B selector1 gate. No broader entitlement/feature name is assigned. Selector2 points at the following data atDS363C. Original caller083D:29CA pushes length36h and theDS3638 FAR buffer at2A2F..2A35, testsAL at2A3D, and conditionally takes its errorcallee path. Native file-read/transform entry/exit and errorcallee execution are not newly captured; this is an original-code computation joined to already verified native endpoint data, not a complete writer-provenance ledger.

An independent sequential-memory oracle checks716 isolated original-instruction CPU cases. These cover all256 single-byte inputs; lengths0/2/51/52/53/54/103/104/105/255/256/65535; SI wrap; three buffer/key aliases; the supplied header; and432 singlebit ciphertext mutations. Each mutation returns the expected nonzero checksum and changes exactly the corresponding decoded bit. Tests additionally check actual output bytes, exact memory-write counts/allowed addresses, FAR stack/return and register/segment fixtures. They are syntheticCPU evidence, not native runtime coverage or a complete alias-domain proof. Two records have29/89 byte-matched instruction memberships while retainingUNKNOWN whole boundaries.

The new immutable checkpoint descends fromc47cbb41a2c6835c2a62939ebbbe458f52e272638c80104084858a903f0bb0ae. Original binaries/assets and full raw traces stay local. FullDOS/Win16/IRQ/timing/render/remake/function-boundary goal remainsACTIVE. Nine RNG sites and successful04C7:0C37 remainopen. The next direct provenance test is a fresh original startup capture of0FBA:01B2 with its incoming54 bytes, key segment, native write trace and actual return2A3A; the current preservedP session should not be restarted merely to manufacture it.
'''
(O/'transform_report.md').write_text(report,encoding='utf-8')
for n in ['verify_bsf_transform_cpu.py','update_bsf_records.py','package_bsf_transform.py']:shutil.copy2(R/'work'/n,O/n)
files={f'runtime/{p.relative_to(D).as_posix()}':p.read_bytes() for p in D.rglob('*') if p.is_file()}
for p in O.iterdir():
 if p.is_file() and p.name!='checkpoint_validation.json':files[p.name]=p.read_bytes()
for n in ['rng_p_revalidate2.log','rng_p_search240b.log','rng_p_boundary_actors.log','rng_p_boundary_context.log']:files['logs/'+n]=(R/'work/runtime'/n).read_bytes()
files['control/rng_p_target_control.json']=(R/'work/runtime/rng_p_target_control.json').read_bytes()
for n in ['runtime_trace_index.json','function_callgraph.json']:files['canonical/'+n]=(R/'outputs/evidence'/n).read_bytes()
manifest={n:{'sha256':H(b),'bytes':len(b)} for n,b in files.items()};files['manifest.json']=json.dumps({'parent_checkpoint_sha256':'c47cbb41a2c6835c2a62939ebbbe458f52e272638c80104084858a903f0bb0ae','files':manifest},indent=2).encode();z=R/'outputs/Nitemare3D_BSF_transform_checkpoint_20261107.zip';assert not z.exists()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for n,b in files.items():a.writestr(n,b)
with zipfile.ZipFile(z) as a:
 assert a.testzip() is None and set(a.namelist())==set(files)
 for n,b in files.items():assert a.read(n)==b
v={'status':'VERIFIED_CRC_EXACT_SET_ALL_HASHES','archive':str(z),'sha256':H(z.read_bytes()),'manifest_files':len(manifest)};(O/'checkpoint_validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
