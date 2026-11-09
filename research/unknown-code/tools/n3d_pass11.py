from pathlib import Path
import csv,json,zipfile,shutil,hashlib,struct,subprocess,re
R=Path('/mnt/data'); prior=R/'N3D_FUNCTION_RESEARCH_PASS10'; dst=R/'N3D_FUNCTION_RESEARCH_PASS11';shutil.copytree(prior,dst,dirs_exist_ok=True)
M=dst/'MASTER_DATABASE'; P=dst/'REPORTS'; M.mkdir(exist_ok=True);P.mkdir(exist_ok=True)
files={'WIN_1_0':'nite3/windows/NITE3W -10.EXE','WIN_1_3':'nite3/windows/NITE3W - 13.EXE','WIN_1_6':'nite3/windows/NITE3W - 16.EXE','WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
with zipfile.ZipFile(R/'files/dosbox-n3d(20261103-105917).zip') as z:
 segments={}
 for version,path in files.items():
  b=z.read(path); ne=struct.unpack_from('<I',b,0x3c)[0];shift=struct.unpack_from('<H',b,ne+0x32)[0];tab=struct.unpack_from('<H',b,ne+0x22)[0]; so,sz,_,_=struct.unpack_from('<HHHH',b,ne+tab+8);segments[version]=b[so<<shift:(so<<shift)+(sz or 65536)]

def disasm(b,start,stop):
 q=R/'_pass11_segment.bin';q.write_bytes(b)
 out=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={stop}',str(q)],text=True)
 outrows=[]
 for line in out.splitlines():
  mat=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)$',line)
  if mat:outrows.append({'address':int(mat[1],16),'bytes':mat[2].strip(),'asm':mat[3].strip()})
 return outrows

def writecsv(n,rs,fields=None):
 fields=fields or list(rs[0]);
 with (M/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
# Verify the actual per-site opcode/target at precisely established local boundaries.
callers=[0x3ce5,0x57e2,0x587e,0x59ee,0x5a62]
callrows=[]
for v,b in segments.items():
 for site in callers:
  rel=struct.unpack_from('<h',b,site+1)[0];target=(site+3+rel)&0xffff
  callrows.append({'version':v,'callsite':f'0002:{site:04X}','raw_bytes':b[site:site+3].hex(' '),'opcode_E8':b[site]==0xe8,'target':f'0002:{target:04X}','local_boundary_from_PASS10':True,'global_reachability_proven':False})
assert all(r['opcode_E8'] and r['target']=='0002:73C5' for r in callrows)
writecsv('PASS11_ERROR20_CALLSITE_CROSSVERSION.csv',callrows)
# Explicit micro-CFG for common error routine, with distinct error-20 tail entry and error-3 entry.
cfg=[('73C5','73C8','fallthrough','AX=0014h'),('73C8','3C3D','tail_jump','no local RET'),('3C38','3C3D','fallthrough','DS=SS; AX=3'),('3C3D','3C40','fallthrough','push AX twice, push CS'),('3C40','39A8','near_call','manual return/stack proof pending'),('3C43','3CB7','near_call','manual return/stack proof pending'),('3C47','3C80','near_call','lookup return in AX'),('3C4F','3C6E','conditional_je','lookup AX==0'),('3C4F','3C51','conditional_not_taken','lookup AX!=0'),('3C59','3C5E','conditional_jne','first byte not M'),('3C59','3C5B','conditional_not_taken','first byte M'),('3C68','3C6A','fallthrough','REPNZ SCAS'),('3C71','KERNEL!#137','import_far_call','NE fixup'),('3C7A','KERNEL!#1','import_far_call','NE fixup')]
writecsv('PASS11_ERROR20_MICROCFG.csv',[dict(source=s,target=t,edge_type=k,evidence_note=n) for s,t,k,n in cfg]); (M/'PASS11_ERROR20_MICROCFG.json').write_text(json.dumps([dict(source=s,target=t,type=k,note=n) for s,t,k,n in cfg],indent=2))
# Path and stack notes: arithmetic applies only to explicitly known pushes/pops; not assume callee cleanup.
stack=[('caller CALL 73C5',-2,'return IP pushed for NEAR CALL'),('73C5 MOV AX,0014h',0,'error id'),('73C8 JMP 3C3D',0,'transfer to common routine, return IP not consumed here'),('3C3D PUSH AX',-2,'error id push'),('3C3E PUSH AX',-2,'second error id push'),('3C3F PUSH CS',-2,'segment word push'),('3C40 CALL 39A8',-2,'NEAR return IP push; callee effect unknown'),('3C43 PUSH CS',-2,'later state unknown because callee effect unresolved'),('3C44 CALL 3CB7',-2,'callee effect unknown'),('3C47 PUSH CS',-2,'callee effect unresolved'),('3C48 CALL 3C80',-2,'callee effect unknown'),('3C6E PUSH BX',-2,'post-call stack absolute unknown'),('3C6F PUSH DS',-2,'segment parameter'),('3C70 PUSH AX',-2,'string or null parameter'),('3C71 CALL FAR KERNEL!#137',-4,'CPU pushes CS:IP; API convention unknown'),('3C79 PUSH AX',-2,'255 exit status'),('3C7A CALL FAR KERNEL!#1',-4,'CPU pushes CS:IP; semantic non-return not proven purely from binary')]
writecsv('PASS11_ERROR20_STACK_TRANSFER.csv',[{'step':i+1,'instruction':ins,'local_push_delta_bytes':d,'interpretation':n,'absolute_sp':'UNKNOWN_AFTER_UNRESOLVED_CALLEE'} for i,(ins,d,n) in enumerate(stack)])
# Show raw identical site bytes and common path across all 5 variants; scoped window, not whole function.
regions={'ERROR20_STUB':(0x73c5,0x73cb),'SHARED_ERROR':(0x3c38,0x3c7f)}
rr=[]
for label,(a,b) in regions.items():
 ref=segments['WIN_1_10'][a:b]
 for v,dat in segments.items():
  block=dat[a:b];rr.append({'region':label,'version':v,'range':f'0002:{a:04X}-{b-1:04X}','identical_to_win110':block==ref,'different_bytes':sum(x!=y for x,y in zip(block,ref)),'sha256':hashlib.sha256(block).hexdigest()})
writecsv('PASS11_SHARED_ERROR_CROSSVERSION_BYTES.csv',rr)
for v in ('WIN_1_8','WIN_1_10'):
 for label,(a,b) in regions.items():
  listing=disasm(segments[v],a,b)
  (P/f'PASS11_{v}_{label}.asm.txt').write_text('\n'.join(f"{x['address']:04X} {x['bytes']:<20} {x['asm']}" for x in listing)+'\n')
# A non-return inference is conditional on Windows KERNEL API semantics; still capture direct binary facts.
report='''# PASS 11 — ERROR20 path and stack evidence (Windows 1.10)

## Targeted evidence
Source: archived Win16 1.10 original `nite3w - 110.exe`, NE segment 2. Independent byte extraction performed in this pass. `0002:73C5` contains `B8 14 00 E9 72 C8` (`MOV AX,0014h; JMP 3C3Dh`). Every one of five near-call sites targets this address in all five examined Windows versions.

## Shared handler, precise path
* `0002:3C38` is an alternate entry: `PUSH SS; POP DS; MOV AX,0003h`; it merges at `3C3D`. The error-20 path via `73C5` does **not** execute this `DS=SS` prelude. Thus the data-segment context must be tracked per ingress.
* `3C3D/3C3E`: two consecutive `PUSH AX`; `3C3F`: `PUSH CS`; `3C40`: near-call to `39A8`. `3C43`: `PUSH CS`, call `3CB7`; `3C47`: `PUSH CS`, call `3C80`. DO NOT assume these are conventional C calls or that the stack can be summed across these callees without checking their `RET/RETF` semantics.
* `3C4D OR AX,AX; 3C4F JE 3C6E` branches on lookup return; nonzero path adjusts a pointer, scans for carriage return, and writes NUL at `[DI-1]`.
* `3C71` is `CALL FAR` relocated to `KERNEL!#137` and `3C7A` to `KERNEL!#1` in all five versions; unresolved platform ABI and side effects prevent full static completion of the path.

## Critical stack observation
A caller executing `CALL NEAR 73C5` pushes its return IP. The `73C8 JMP 3C3D` does not pop that IP. Since the common handler proceeds toward KERNEL calls, the caller's ordinary successor should **not** be considered reachable through a proven normal return unless a return path through the OS calls is shown. This is a conditional non-return inference, **not** runtime verification.

## Coverage and limitations
A total of 25 local E8 site/target pairs was rechecked against original EXE bytes; the same byte sites do not establish program-wide CFG reachability. The new micro-CFG is a *partial graph* with unresolved callee effects. No runtime checks, no authenticated GitHub write, no complete function certification.

## P0 for PASS 12
Decode and trace `0002:39A8`, `0002:3CB7`, `0002:3C80` with explicit calling conventions, stack delta and segment origins; then discover how their output is used at `3C4D`. Identify the KERNEL ordinals using version-correct Win16 documentation, and verify termination behavior separately.
'''
(P/'PASS11_ERROR20_STACK_CALLGRAPH_ANALYSIS.md').write_text(report)
summary={'pass':11,'crossversion_near_sites_verified':len(callrows),'windows_versions':list(segments),'microcfg_edges':len(cfg),'stack_transfer_steps':len(stack),'full_function_certifications':0,'open':['global callsite reachability','callee RET/RETF stack cleanup','DS provenance for error20 ingress','KERNEL API runtime behavior','DOS 2.0 loader unpacking']}
(M/'PASS11_SUMMARY.json').write_text(json.dumps(summary,indent=2))
with (P/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS11: 25 near-call operands revalidated across five Win16 binaries; partial error20 tail CFG and stack transfer audit; 0 fully certified functions.\n')
(R/'_pass11_segment.bin').unlink(missing_ok=True)
archive=R/'N3D_FUNCTION_RESEARCH_PASS11_20261103.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(dst.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(R))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'size':archive.stat().st_size,'summary':summary,'region_differences':rr},indent=2))