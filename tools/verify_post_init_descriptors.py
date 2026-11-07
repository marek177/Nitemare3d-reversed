import json,base64,hashlib,struct,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';O=R/'outputs/wall_sort_20261106';v=json.loads((D/'near_rng_descriptor_post_init.json').read_text());obs=json.loads((D/'wall_record_pass_observation.json').read_text());rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x and 'id' in x:
   r=rpc[x['id']];assert r['response']==x and r['server_pid']==23808
   if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
  for a in x.values():check(a)
 elif isinstance(x,list):
  for a in x:check(a)
def addr(x,o,n):
 q=rpc[x['id']]['request']['params'];assert int(q['address']['segment'],16)==0x2f94 and int(q['address']['offset'],16)==o and q['length']==n
check(v);assert v['status_response']['result']['state']=='stopped';r=v['registers']['result'];assert (int(r['segments']['cs'],16),int(r['instruction_pointer'],16))==(0xed3,0x2e0);addr(v['count'],0x626e,2);n=int.from_bytes(data(v['count']),'little');assert n==960;addr(v['buffer'],0x62ac,n*28);b=data(v['buffer']);changed_from_pass=sum(x!=y for x,y in zip(b,data(obs['after_return']['buffer'])[:n*28]));assert changed_from_pass==v['buffer_bytes_changed_since_pass']
for x in [v['buffer'],v['count']]+[d['read'] for d in v['descriptors'].values()]:assert x['result']['state_revision']==r['state_revision']
indices={b[28*i+4] for i in range(n)};assert set(v['descriptors'])=={str(i) for i in indices};groups=collections.Counter();candidates=[]
for i in indices:
 d=v['descriptors'][str(i)];addr(d['read'],0x4310+8*i,8);assert d['words']==list(struct.unpack('<4H',data(d['read'])))
 if d['words'][2]:addr(d['timing_table'],d['words'][2],16)
 else:assert d['timing_table'] is None
for i in range(n):
 rec=b[28*i:28*i+28];d=v['descriptors'][str(rec[4])]['words'];excluded=rec[6] in(7,0x2d,0x2f);groups[(rec[6],rec[4],d[2]!=0,d[1]!=0,excluded)]+=1
 if not excluded and d[1] and d[2]:candidates.append(i)
expected=[{'class6':k[0],'descriptor_index4':k[1],'timing_table_nonzero':k[2],'caller_speed_nonzero':k[3],'local_class_excluded':k[4],'count':count} for k,count in sorted(groups.items())];assert v['group_counts']==expected and v['candidate_indices']==candidates
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];proof=[]
for fid in ('0201_04F0','0201_040E'):
 c=json.loads((R/'outputs/evidence/function_cfg'/f'nite3d20_{fid}.json').read_text());s=int(fid[:4],16)
 for x in c['instructions']:
  code=bytes.fromhex(x['bytes']);assert im[s*16+x['offset']:s*16+x['offset']+len(code)]==code
 proof.append({'candidate_function':fid.replace('_',':'),'byte_matched_instruction_memberships':len(c['instructions']),'whole_boundary':'UNKNOWN'})
summary={'status':'VERIFIED_RUNTIME_ENDPOINT_WITH_STATIC_FORMULA_JOIN','records':n,'unique_descriptor_indices':len(indices),'nonzero_timing_table_descriptors':sum(d['words'][2]!=0 for d in v['descriptors'].values()),'records_with_nonzero_caller_speed':sum(g['count'] for g in expected if g['caller_speed_nonzero']),'local_class_speed_table_candidates':len(candidates),'candidate_indices':candidates,'buffer_bytes_changed_since_pass':changed_from_pass,'static_formula_memberships':proof,'scope':'First Demo-header snapshot at06B0:02E0 after parent return; formulaDS4310+8*recordByte4 comes from static caller. This does not prove actual caller pointer/visibility/list domain, future descriptor persistence, runtime threshold decisions or successful0201:0468. Future deferred-load/frame mutations remainopen.'};(O/'post_init_descriptor_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
