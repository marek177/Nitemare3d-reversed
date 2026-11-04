from pathlib import Path
import csv,json,hashlib,zipfile
R=Path(__file__).resolve().parents[2];O=R/'PASS002';B=O/'BATCH_01_10'
summary=json.loads((O/'REPORTS/BATCH10_SUMMARY.json').read_text());metrics=json.loads((O/'REPORTS/PASS002_metrics.json').read_text());rows=list(csv.DictReader((R/'MASTER_DATABASE/FUNCTION_MASTER.csv').open()));byid={x['function_id']:x for x in rows};audited={'DOS_2_0_0201_000A','DOS_2_0_0201_001A','WIN_1_10_0001_53CA','WIN_1_10_0003_0D9E','WIN_1_10_0003_0DA4'}
for row in summary:
 fid=row['function_id'];old=byid.get(fid,{})
 if not old:
  old={k:''for k in rows[0]};old.update(function_id=fid,binary_sha256=byid['DOS_2_0_0201_000A']['binary_sha256'],segment=fid.split('_')[-2],entry=fid.split('_')[-1],boundaries_verified=False,cfg_complete=False,algorithm_verified=False,runtime_verified=False)
 old.update(instruction_count=row['instruction_count'],unique_decoded_bytes=row['decoded_instruction_bytes'],return_count=len(row['local_returns']),unresolved_count=row['local_unresolved_jumps'],overlap_count=len(row['overlap_detected']),status='LOCAL_SEMANTICS_EMULATION_VERIFIED'if fid in audited else'STATIC_LOCAL_ANALYSIS_PARTIAL',local_graph_source='PASS002/CFG/'+fid+'.json',independent_decoder_agreement=True,complete_behavior_verified=False)
 byid[fid]=old
for fid,row in byid.items():row['isolated_emulation_evidence']=fid in audited;row.setdefault('local_graph_source','CFG/FUNCTION_CFG.json');row.setdefault('independent_decoder_agreement',False);row.setdefault('complete_behavior_verified',False)
fields=list(dict.fromkeys(k for x in byid.values()for k in x))
with (R/'MASTER_DATABASE/CUMULATIVE_FUNCTION_MASTER_PASS002.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows(byid[k]for k in sorted(byid))
inst=[]
for p in sorted(B.glob('*_INSTRUCTIONS.csv')):inst.extend(csv.DictReader(p.open()))
assert len(inst)==470
with (R/'MASTER_DATABASE/FUNCTION_INSTRUCTION_DATABASE_PASS002.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,list(inst[0]));w.writeheader();w.writerows(inst)
metrics['cumulative_reference_candidate_ids']=len(byid);metrics['cumulative_platform_candidate_ids']={'DOS':sum(k.startswith('DOS')for k in byid),'WIN16':sum(k.startswith('WIN')for k in byid)};metrics['whole_program_complete_boundary_functions']=0;metrics['cross_version_full_semantic_equivalence_functions']=0
(O/'REPORTS/PASS002_metrics.json').write_text(json.dumps(metrics,indent=2))
# Combined export is convenient for code-hosted review; separate authoritative dossiers remain intact.
combined='\n\n---\n\n'.join(p.read_text()for p in sorted(B.glob('[0-9][0-9]_*.md')));(O/'REPORTS/FUNCTIONS_01_10_COMBINED.md').write_text(combined)
# Check all named function dossiers and graph coverage before checkpointing.
for row in summary:
 fid=row['function_id'];p=B/(f'{row["number"]:02d}_{fid}.md');assert p.exists();assert sum(x.startswith('## ')for x in p.read_text().splitlines())>=25
 assert (O/'CFG'/(fid+'.json')).exists()
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in R.rglob('*')if p.is_file()and p.name!='CHECKSUMS.json'};(R/'CHECKSUMS.json').write_text(json.dumps(manifest,indent=2));assert all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in manifest.items())
name='N3D_FUNCTION_RESEARCH_PASS002_FUNCTIONS_01_10_20261104.zip'
with zipfile.ZipFile(R.parent/name,'w',zipfile.ZIP_DEFLATED,6)as z:
 for root in [R,R.parent/'inputs']:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(R.parent))
with zipfile.ZipFile(R.parent/name)as z:assert z.testzip()is None
print(json.dumps({'zip':name,'size':(R.parent/name).stat().st_size,'dossiers':10,'instruction_rows':len(inst),'reference_candidate_union':len(byid),'by_platform':metrics['cumulative_platform_candidate_ids'],'archive_crc':'PASS','source_checksums':'PASS'},indent=2))
