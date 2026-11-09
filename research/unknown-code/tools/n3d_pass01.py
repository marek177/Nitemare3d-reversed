import zipfile,hashlib,struct,csv,json,pathlib,subprocess,re,collections
ROOT=pathlib.Path('/mnt/data/N3D_FUNCTION_RESEARCH'); ZIP='/mnt/data/files/dosbox-n3d(20261103-105917).zip'
DIRS=['REFERENCES/DOS_2_0','REFERENCES/WIN_1_10','VERSIONS/DOS','VERSIONS/WIN16','FUNCTIONS/DOS','FUNCTIONS/WIN16','ASM_DIFF','CFG','CALLGRAPH','PSEUDOCODE','ALGORITHMS','RUNTIME_EVIDENCE','REPORTS','MASTER_DATABASE']
for d in DIRS:(ROOT/d).mkdir(parents=True,exist_ok=True)
U16=lambda b,i:struct.unpack_from('<H',b,i)[0]
U32=lambda b,i:struct.unpack_from('<I',b,i)[0]
z=zipfile.ZipFile(ZIP)
version_map={'N3D-10.exe':('DOS','1.0'),'N3D-11.exe':('DOS','1.1'),'N3D-12.exe':('DOS','1.2'),'N3D-E-17.EXE':('DOS','1.7'),'N3D-E-18.EXE':('DOS','1.8'),'N3D-E-19.EXE':('DOS','1.9'),'N3D-E-20.EXE':('DOS','2.0'),'NITE3W -10.EXE':('WIN16','1.0'),'NITE3W - 13.EXE':('WIN16','1.3'),'NITE3W - 16.EXE':('WIN16','1.6'),'NITE3W - 18.EXE':('WIN16','1.8'),'nite3w - 110.exe':('WIN16','1.10')}
rows=[]; entries=[]; relevant={}
for filename in z.namelist():
 short=filename.split('/')[-1]
 if short not in version_map:continue
 platform,version=version_map[short]; b=z.read(filename); relevant[(platform,version)]=b
 row={'platform':platform,'version':version,'source_archive':pathlib.Path(ZIP).name,'archive_member':filename,'byte_length':len(b),'sha256':hashlib.sha256(b).hexdigest(),'format':'','mz_header_bytes':U16(b,8)*16,'mz_relocation_count':U16(b,6),'mz_relocation_table_offset':U16(b,0x18),'mz_cs':f'{U16(b,0x16):04X}','mz_ip':f'{U16(b,0x14):04X}','mz_load_offset':'','ne_header_offset':'','ne_segment_count':'','ne_entry_cs':'','ne_entry_ip':'','ne_entry_physical_offset':'','segment_table_offset':'','ne_alignment_shift':'','unresolved_notes':''}
 if platform=='DOS':
  hdr=U16(b,8)*16;cs=U16(b,0x16);ip=U16(b,0x14);phys=hdr+cs*16+ip
  row.update(format='MZ',mz_load_offset=hdr,ne_entry_physical_offset=phys,unresolved_notes='Entry is loader/startup candidate; no assertion that unpacked program functions are visible')
  blob=b[phys:phys+96]; entry_label=f'{cs:04X}:{ip:04X}'
 else:
  ne=U32(b,0x3c); segcount=U16(b,ne+0x1c);stab=U16(b,ne+0x22);align=U16(b,ne+0x32);cs=U16(b,ne+0x16);ip=U16(b,ne+0x14)
  segment_index=cs;off=ne+stab+8*(segment_index-1)
  physical=(U16(b,off)<<align)+ip if 1<=segment_index<=segcount else -1
  row.update(format='NE',ne_header_offset=ne,ne_segment_count=segcount,ne_entry_cs=f'{cs:04X}',ne_entry_ip=f'{ip:04X}',ne_entry_physical_offset=physical,segment_table_offset=ne+stab,ne_alignment_shift=align,unresolved_notes='NE segment relocation records and exported entry table require independent decoding')
  blob=b[physical:physical+96] if physical>=0 else b'';entry_label=f'NE_SEG_{cs:04X}:{ip:04X}'
 row['entry_bytes_sha256']=hashlib.sha256(blob).hexdigest()
 rows.append(row)
 out=(ROOT/'REFERENCES'/('DOS_2_0' if platform=='DOS' else 'WIN_1_10')/'entrypoint.bin') if (platform,version) in [('DOS','2.0'),('WIN16','1.10')] else None
 if out:out.write_bytes(blob)
 # Decode exactly a 96-byte window starting at the EXE entry. This is *not* a function boundary.
 if blob:
  tmp=ROOT/'REPORTS'/f'entry_{platform}_{version.replace(".","_")}.bin';tmp.write_bytes(blob)
  p=subprocess.run(['objdump','-D','-b','binary','-m','i8086','-M','intel',str(tmp)],capture_output=True,text=True)
  asm=p.stdout if p.returncode==0 else p.stderr
  (ROOT/'REPORTS'/f'entry_{platform}_{version.replace(".","_")}.asm.txt').write_text(f'ENTRY {entry_label} mapped EXE physical {row["ne_entry_physical_offset"]}\n96 bytes ONLY; not a verified function.\n\n'+asm)
  entries.append({'platform':platform,'version':version,'entry':entry_label,'physical':row['ne_entry_physical_offset'],'first_32_bytes':blob[:32].hex(' '),'first_96_bytes_sha256':row['entry_bytes_sha256']})
with (ROOT/'MASTER_DATABASE'/'ORIGINAL_EXE_INVENTORY.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(ROOT/'MASTER_DATABASE'/'ENTRYPOINT_CANDIDATES.json').write_text(json.dumps(entries,indent=2))
for name,head in {'FUNCTION_MASTER.csv':['function_id','platform','reference_version','entry','status','evidence'], 'FUNCTION_INSTRUCTION_DATABASE.csv':['function_id','version','address','bytes','asm','confidence'], 'FUNCTION_BOUNDARIES.csv':['function_id','entry','exit','status'], 'FUNCTION_CROSS_VERSION_MATRIX.csv':['function_id','version','match_status','evidence'], 'INSTRUCTION_LEVEL_DIFF.csv':['function_id','old_version','new_version','old_address','new_address','old_bytes','new_bytes','classification'], 'UNKNOWN_FUNCTIONS.csv':['version','address','reason'], 'UNRESOLVED_BRANCHES.csv':['version','source','target_expression','reason']}.items():
 with (ROOT/'MASTER_DATABASE'/name).open('w',newline='') as f:csv.writer(f).writerow(head)
for name in ['FUNCTION_CFG.json','FUNCTION_CALLGRAPH.json','FUNCTION_DATAFLOW.json']:(ROOT/'MASTER_DATABASE'/name).write_text(json.dumps({'schema_version':1,'status':'not_analyzed','functions':[]},indent=2))
(ROOT/'REPORTS'/'FUNCTION_SEMANTIC_DIFF.md').write_text('# Semantic diff\n\nNot yet established: segment relocation / executable runtime reconstruction and function-level matching needed.\n')
(ROOT/'PSEUDOCODE'/'FUNCTION_PSEUDOCODE.md').write_text('# Function pseudocode\n\nNo complete function has been established by this pass. Entry-point disassembly is in REPORTS.\n')
# raw equal across candidate source versions is valid but not a function match
pairs=[]
for platform in ['DOS','WIN16']:
 v=[r for r in rows if r['platform']==platform]
 for a in v:
  for c in v:
   if a['version']<c['version']:
    aa=relevant[(platform,a['version'])];bb=relevant[(platform,c['version'])]
    pairs.append({'platform':platform,'a':a['version'],'b':c['version'],'exact_exe_equal':aa==bb,'sha_a':a['sha256'],'sha_b':c['sha256']})
(ROOT/'MASTER_DATABASE'/'RAW_BINARY_EQUALITY.json').write_text(json.dumps(pairs,indent=2))
report=['# Nitemare 3D — PASS 01 / Original EXE intake','',f'Source: `{pathlib.Path(ZIP).name}` (archive members read directly).',f'Located **{len(rows)}** named reference EXEs: {sum(x["platform"]=="DOS" for x in rows)} DOS, {sum(x["platform"]=="WIN16" for x in rows)} Windows. DOS 1.5 not found by filename in this archive.','', '## Reference binaries','']
for platform,version in [('DOS','2.0'),('WIN16','1.10')]:
 r=next(x for x in rows if (x['platform'],x['version'])==(platform,version))
 report+= [f'### {platform} {version}',f'- SHA-256: `{r["sha256"]}`',f'- Length: {r["byte_length"]} bytes; format {r["format"]}; entry EXE file offset {r["ne_entry_physical_offset"]}.',f'- Initial disassembly: `REPORTS/entry_{platform}_{version.replace(".","_")}.asm.txt` (96-byte window; **not** a validated function).','']
report+=['## Exact whole-file duplicate evidence','']
for p in pairs:
 if p['exact_exe_equal']:report.append(f'- {p["platform"]} {p["a"]} = {p["b"]}: identical SHA-256 and bytes.')
report+=['','## Verification status','- 0 function boundaries independently verified in this pass.','- 0 CFGs marked complete; 0 behaviorally validated functions.','- All function-level match and changed-instruction counts remain **undetermined**, not zero.','- DOS MZ entry points with zero MZ relocations may represent packed startup loaders; do not infer game function limits from the outer MZ image.','- Next: decode NE segment fixups/entry table and establish entry + call targets; investigate whether DOS code is packed and identify loaded execution image.','']
(ROOT/'REPORTS'/'PASS01_EVIDENCE.md').write_text('\n'.join(report))
(ROOT/'REPORTS'/'ALL_VERSIONS_PROGRESS.md').write_text('\n'.join(['# All versions — PASS 01','', '| Platform | Version | EXE verified by SHA-256 | Verified function bounds | Complete CFG | Runtime verified functions |','|---|---|---|---|---|---|']+[f'| {r["platform"]} | {r["version"]} | Yes | undetermined | undetermined | undetermined |' for r in rows]+['','Denominators for function counts not yet established.']))
print(json.dumps({'inventory':rows,'exact_duplicates':[p for p in pairs if p['exact_exe_equal']]},indent=2))