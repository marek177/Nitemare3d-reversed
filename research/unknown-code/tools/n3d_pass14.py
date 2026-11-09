from pathlib import Path
import shutil,csv,json,subprocess,re,zipfile,hashlib
ROOT=Path('/mnt/data'); SRC=ROOT/'N3D_FUNCTION_RESEARCH_PASS13'; DST=ROOT/'N3D_FUNCTION_RESEARCH_PASS14'; shutil.copytree(SRC,DST,dirs_exist_ok=True)
DB=DST/'MASTER_DATABASE'; REPORT=DST/'REPORTS'; OUT=DST/'CFG';
def writecsv(fname,rows,fields):
 with (DB/fname).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
regex=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)$',re.I)
records=[]; counts=[]; snippets=[]
versions=['WIN_1_0','WIN_1_3','WIN_1_6','WIN_1_8','WIN_1_10']
for ver in versions:
 for seg in (1,2,3,4,7):
  p=DST/'REFERENCES'/ver/f'NE_SEG_{seg:02d}.bin'
  if not p.exists():continue
  data=p.read_bytes(); raw=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',str(p)],text=True)
  linear=[]
  for line in raw.splitlines():
   m=regex.match(line)
   if not m:continue
   adr=int(m[1],16); enc=bytes.fromhex(m[2]); ins=m[3].strip().lower()
   if enc==b'\xfc' or enc==b'\xfd' or enc==b'\x9d' or enc==b'\x9c' or enc==b'\xcf' or enc==b'\x9a':
    kind={b'\xfc':'CLD',b'\xfd':'STD',b'\x9d':'POPF',b'\x9c':'PUSHF',b'\xcf':'IRET',b'\x9a':'FAR_CALL'}[enc]
    records.append(dict(version=ver,segment=seg,offset=f'{adr:04X}',bytes=enc.hex(),mnemonic=kind,classification='LINEAR_DISASSEMBLY_CANDIDATE_NOT_REACHABILITY_PROVEN',source_seg_sha256=hashlib.sha256(data).hexdigest()))
   linear.append((adr,enc,ins))
  counts.append(dict(version=ver,segment=seg,segment_bytes=len(data),cld_candidates=sum(r['version']==ver and r['segment']==seg and r['mnemonic']=='CLD' for r in records),std_candidates=sum(r['version']==ver and r['segment']==seg and r['mnemonic']=='STD' for r in records),popf_candidates=sum(r['version']==ver and r['segment']==seg and r['mnemonic']=='POPF' for r in records)))
writecsv('PASS14_DIRECTION_FLAG_LINEAR_CANDIDATES.csv',records,list(records[0]))
writecsv('PASS14_DF_CANDIDATE_COUNTS.csv',counts,list(counts[0]))
# Local, trusted instruction boundary verification through explicit fixed contiguous entrypoint regions
seg2=(DST/'REFERENCES/WIN_1_10/NE_SEG_02.bin').read_bytes()
def disassemble(start,end):
 p=DST/'REFERENCES/WIN_1_10/NE_SEG_02.bin'
 raw=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(p)],text=True)
 result=[]
 for line in raw.splitlines():
  m=regex.match(line)
  if m:
   off=int(m[1],16); enc=bytes.fromhex(m[2]);ins=m[3].strip()
   assert seg2[off:off+len(enc)]==enc
   result.append((off,enc,ins))
 return result
windows={'LOOKUP_3C80':(0x3c80,0x3cb7),'MESSAGE_3CB7':(0x3cb7,0x3cf4),'FATAL_3C38':(0x3c38,0x3c7f),'STARTUP_3718':(0x3718,0x3790)}
local=[]
for name,(a,b) in windows.items():
 for off,enc,ins in disassemble(a,b):
  if enc in (b'\xfc',b'\xfd',b'\x9d',b'\xcf'):
   local.append(dict(region=name,address=f'0002:{off:04X}',mnemonic=ins,bytes=enc.hex()))
writecsv('PASS14_VERIFIED_LOCAL_DF_MODIFIERS.csv',local,['region','address','mnemonic','bytes'])
# Static proof of locally visible paths: no direct DF operations for exact 3 routines, but far-called functions can modify flags
# Targeted exact instruction tables annotated for 3C80 and 3CB7.
traces=[]
for name in ('LOOKUP_3C80','MESSAGE_3CB7','FATAL_3C38'):
 a,b=windows[name]
 for off,enc,ins in disassemble(a,b):
  flag='DF_CONSUMER' if any(x in ins.lower() for x in ('lods','scas','movs','stos','cmps')) else 'POTENTIAL_EXTERNAL_FLAGS_SIDE_EFFECT' if ins.lower().startswith(('call','int ')) else 'NO_DIRECT_DF_WRITE'
  traces.append(dict(region=name,address=f'0002:{off:04X}',bytes=enc.hex(' '),instruction=ins,df_note=flag))
writecsv('PASS14_LOCAL_DF_INSTRUCTION_AUDIT.csv',traces,list(traces[0]))
# fatal chain instruction-level stack accounting, conditional external KERNEL calls
stack=[]
for off,enc,ins in disassemble(0x3c3d,0x3c7f):
 mnemonic=ins.split()[0].lower();delta='unknown'
 if mnemonic=='push':delta='-2'
 elif mnemonic=='pop':delta='+2'
 elif mnemonic=='call':delta='-2 if near; -4 if far, callee stack cleanup unknown'
 elif mnemonic in ('jmp','je','jne'):delta='0'
 elif mnemonic=='retf':delta='+4 plus optional immediate'
 elif mnemonic=='retn':delta='+2 plus optional immediate'
 elif mnemonic in ('repnz','repne','repe','rep'):delta='0'
 else:delta='0 (excluding implicit unknown instruction effects)'
 stack.append(dict(address=f'0002:{off:04X}',instruction=ins,bytes=enc.hex(' '),stack_effect=delta,notes='external call: calling convention and nonreturn unverified' if mnemonic=='call' and enc[:1]==b'\x9a' else ''))
writecsv('PASS14_FATAL_STACK_AND_EXITS.csv',stack,list(stack[0]))
# Focused 16bit effects, four consumed DF instructions; relation to locally set DF
summary={'pass':14,'versions_requested':versions,'versions_actually_scanned':sorted(set(r['version'] for r in counts)),'coverage_by_version':{v: sorted(r['segment'] for r in counts if r['version']==v) for v in versions},'seg2_locally_checked':list(windows),'linear_candidate_total':len(records),'linear_cld_candidates':sum(r['mnemonic']=='CLD' for r in records),'linear_std_candidates':sum(r['mnemonic']=='STD' for r in records),'local_df_modifier_count':len(local),'scope_notice':'Linear disassembly is not a reachable code proof; segment tables and relocation data may mix code and data. Absence in a local routine does not rule out DF set by caller or imported code.','certified_complete_functions':0}
(DB/'PASS14_SUMMARY.json').write_text(json.dumps(summary,indent=2))
(REPORT/'PASS14_DF_PRODUCER_CALLCHAIN.md').write_text('''# PASS 14 — Win16 Direction Flag provenance and fatal-exit audit

## What was actually computed

Requested Windows 1.0, 1.3, 1.6, 1.8 and 1.10, but only the locally saved segment files were available: **Windows 1.10 segments 1, 2, 3, 4, 7 and Windows 1.8 segment 2**. Windows 1.0, 1.3 and 1.6 were NOT scanned in PASS 14. Re-disassembled these existing original NE segment images using `objdump -D -b binary -m i8086 -M intel`. Wrote all **linear decoding candidates** for CLD (`FC`), STD (`FD`), POPF (`9D`), PUSHF (`9C`), and IRET (`CF`), with segment SHA-256. These are candidate instruction boundaries, **not** a proof of reachable code. Some are data bytes accidentally decoded as code. Exact instruction analysis of `0002:3C80`, `3CB7` and `3C38` is separately audited.

## Finding 1: four DF-dependent consumers, no local DF producer

The reference Windows 1.10 routines contain: `0002:3C94 LODSW`, `3CA3 REPNE SCASB`, `3CDC REPNE SCASB`, `3C68 REPNE SCASB`. The three scoped routines contain no local `CLD`, `STD`, `POPF`, or `IRET`. Thus they depend on incoming DF state on those execution paths. It is **not proved** that DF=0 for every caller. Finding a `CLD` elsewhere (or its absence from one region) cannot close that proof without path-sensitive callgraph and external import flags-clobber modeling.

## Finding 2: direct normal-path ES provenance

The lookup routine `0002:3C80` executes `PUSH DS; POP ES` at `3C8C–3C8D`. The `0002:3CB7` caller invokes it at `3CCD` and scans `ES:DI` at `3CDC` on the non-null return path. Thus ES=DS *at the lookup's assignment point* and ES is not visibly overwritten by subsequent local instructions before the scan. However, verifying correct DS values requires upstream path analysis.

## Finding 3: fatal handler cannot be certified as terminating

The shared handler at `3C3D` executes helper calls to `39A8`, `3CB7`, `3C80`, then calls `KERNEL` ordinal 137 at `3C71`, and `KERNEL` ordinal 1 at `3C7A` (import identities from earlier relocation work). The code appears to prepare error-message output and exit, but the exact ABI, DF preservation, stack cleanup, and nonreturn behavior of the imported routines have **not** been runtime verified. Therefore do not mark this handler as `noreturn` without external semantics evidence.

## Important caveat — alternative entry path

`0002:3C38` uses `PUSH SS; POP DS`, whereas `73C5` uses a direct jump to `3C3D`, skipping that DS rewrite. Their preconditions differ. Both converge at `3C3D`; stack inference must keep that split.

## Next P0

Derive DF guarantees from reachable instructions starting at NE entrypoints, inspect initial CPU flags and all calls across segment boundaries, and establish imported Win16 KERNEL functions' flags and exit behavior from dependable ABI documentation or runtime tracing. Continue reference DOS 2.0 executable-image reconstruction; no DOS function was newly certified in this pass.

**Completed function certificates: 0.**
''')
with (REPORT/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS14: linear CLD/STD/POPF/PUSHF/IRET candidates across available Win16 1.10 and partial 1.8 segments; independent exact local audit of three DF-consuming routines; external KERNEL stack/termination remains unresolved. Certified 0.\n')
zip_path=ROOT/'N3D_FUNCTION_RESEARCH_PASS14_20261104.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in DST.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(zip_path) as z: assert z.testzip() is None
print(json.dumps({'archive':str(zip_path),'size_bytes':zip_path.stat().st_size,'file_count':len(list(DST.rglob('*'))),'summary':summary,'counts':counts},indent=2))