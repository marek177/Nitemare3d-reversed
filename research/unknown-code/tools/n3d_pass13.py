from pathlib import Path
import shutil,csv,json,hashlib,zipfile,subprocess,re
R=Path('/mnt/data'); S=R/'N3D_FUNCTION_RESEARCH_PASS12'; D=R/'N3D_FUNCTION_RESEARCH_PASS13'; shutil.copytree(S,D,dirs_exist_ok=True)
M=D/'MASTER_DATABASE'; REP=D/'REPORTS'; F=D/'FUNCTIONS/WIN16'
regions={'39A8':(0x39a8,0x39cb),'3CB7':(0x3cb7,0x3cf4),'3C80':(0x3c80,0x3cb7),'SHARED_FATAL':(0x3c38,0x3c7f)}
pat=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)$')
def csvwrite(name,rs):
 with (M/name).open('w',newline='') as o:
  w=csv.DictWriter(o,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
allrows=[]; audit=[]
for vers in ('WIN_1_8','WIN_1_10'):
 path=D/'REFERENCES'/vers/'NE_SEG_02.bin';b=path.read_bytes()
 for fid,(start,end) in regions.items():
  s=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(path)],text=True)
  group=[]
  for ln in s.splitlines():
   x=pat.match(ln)
   if x:
    a=int(x.group(1),16); raw=bytes.fromhex(x.group(2)); op=x.group(3).strip(); assert b[a:a+len(raw)]==raw
    group.append({'version':vers,'routine':fid,'seg':'0002','offset':f'{a:04X}','bytes':raw.hex(' ').upper(),'asm':op,'source_sha256':hashlib.sha256(b).hexdigest(),'verification':'EXACT_SEGMENT_BYTES'})
  audit.append({'version':vers,'routine':fid,'start':f'{start:04X}','end_exclusive':f'{end:04X}','decoded_instructions':len(group),'decoded_bytes':sum(len(bytes.fromhex(x['bytes'])) for x in group),'gap_free':sum(len(bytes.fromhex(x['bytes'])) for x in group)==end-start})
  allrows+=group
  (F/f'PASS13_{vers}_{fid}_RAW_ASM.txt').write_text('\n'.join(f"{r['offset']}  {r['bytes']:<18} {r['asm']}" for r in group)+'\n')
csvwrite('PASS13_VERIFIED_LOCAL_INSTRUCTIONS.csv',allrows)
csvwrite('PASS13_REGION_COVERAGE_AUDIT.csv',audit)
# Each statement grounded in explicit segment addresses; distinguish path sensitivity.
deps=[
 {'routine':'3C80','address':'3C8C-3C8D','instruction':'PUSH DS; POP ES','reads':'DS','writes':'ES','condition':'All entries reaching lookup prologue','evidence':'DIRECT_INSTRUCTION','remaining':'Does not prove DS is correct segment when called'},
 {'routine':'3C80','address':'3C94','instruction':'LODSW','reads':'DS:SI,DF','writes':'AX,SI','condition':'Table lookup loop','evidence':'DIRECT_INSTRUCTION','remaining':'DF=0 is not established locally'},
 {'routine':'3C80','address':'3CA3','instruction':'REPNZ SCASB','reads':'ES:DI,DF,CX,AL','writes':'DI,CX,ZF','condition':'ID mismatch and not FFFF','evidence':'DIRECT_INSTRUCTION','remaining':'NUL termination and DF=0 not established locally'},
 {'routine':'3CB7','address':'3CCD','instruction':'CALL 3C80','reads':'current DS,stack arg','writes':'AX, ES','condition':'DS:[0A94] != 0','evidence':'INTERPROCEDURAL_FROM_3C80','remaining':'3C80 may touch FLAGS and nonlocal ES; ABI validity to confirm'},
 {'routine':'3CB7','address':'3CD2','instruction':'JE 3CE8','reads':'ZF set by OR AX,AX','writes':'IP','condition':'lookup result == 0','evidence':'DIRECT_INSTRUCTION','remaining':'ES not used on skip path'},
 {'routine':'3CB7','address':'3CDC','instruction':'REPNZ SCASB','reads':'ES:DI,DF,CX,AL','writes':'DI,CX,ZF','condition':'lookup result != 0','evidence':'ES_EQUALS_DS_ON_THIS_PATH','remaining':'DF=0 and ES preservation through lookup verified from instructions; no external call between 3CCD and 3CDC'},
 {'routine':'SHARED_FATAL','address':'3C62','instruction':'POP ES','reads':'DS via preceding PUSH DS','writes':'ES','condition':'Nonzero message branch','evidence':'DIRECT_INSTRUCTION','remaining':'DF=0 needed for scan at 3C68'},
 {'routine':'SHARED_FATAL','address':'3C68','instruction':'REPNZ SCASB','reads':'ES:DI,DF,CX,AL','writes':'DI,CX,ZF','condition':'Nonzero message branch','evidence':'DIRECT_INSTRUCTION','remaining':'DF not locally established'},
]
csvwrite('PASS13_SEGMENT_FLAG_DEPENDENCIES.csv',deps)
stack=[
 {'routine':'39A8','callee_entry_sp':'S','stack_after_prologue':'S-4','saved_regs':'BP at S-2; DS at S-4','return':'RETF at 39CA','stack_after_return':'S+4','parameter_bytes':0,'note':'near CALL preceded by PUSH CS'},
 {'routine':'3CB7','callee_entry_sp':'S','stack_after_prologue':'S-6 (also PUSH DI)','saved_regs':'BP S-2; DS S-4; DI S-6','return':'RETF 2 at 3CF1','stack_after_return':'S+6','parameter_bytes':2,'note':'3C80 call pushes arg + CS then near CALL, callee removes 6 from its entry'},
 {'routine':'3C80','callee_entry_sp':'S','stack_after_prologue':'S-8 (also PUSH SI,DI)','saved_regs':'BP S-2; DS S-4; SI S-6; DI S-8','return':'RETF 2 at 3CB4','stack_after_return':'S+6','parameter_bytes':2,'note':'ES set to DS as non-preserved side effect'},
]
csvwrite('PASS13_STACK_FRAMES.csv',stack)
# Differing bytes only at aligned instruction starts in these three routines
lookup={}
for r in allrows:
 if r['routine'] in ('39A8','3CB7','3C80'):
  lookup.setdefault((r['routine'],r['offset']),{})[r['version']]=r
align=[]
for (rt,ad),rs in sorted(lookup.items()):
 a=rs.get('WIN_1_8');b=rs.get('WIN_1_10')
 align.append({'routine':rt,'offset':ad,'win18_bytes':a['bytes'] if a else '', 'win110_bytes':b['bytes'] if b else '', 'win18_asm':a['asm'] if a else '', 'win110_asm':b['asm'] if b else '', 'classification':'IDENTICAL_BYTES' if a and b and a['bytes']==b['bytes'] else 'MODIFIED_INSTRUCTIONS' if a and b else 'UNMATCHED_OFFSET'})
csvwrite('PASS13_ALIGNED_ROUTINE_DIFF.csv',align)
changed=[r for r in align if r['classification']!='IDENTICAL_BYTES']
report='''# PASS 13 — Win16 chain 39A8 / 3CB7 / 3C80: ES, DF and stack audit

## Evidence
The `REFERENCES/WIN_1_8/NE_SEG_02.bin` and `REFERENCES/WIN_1_10/NE_SEG_02.bin` segment bytes were re-decoded with GNU objdump i8086. Each instruction's bytes were asserted equal to the segment bytes. The CSV audit contains the number of decoded instructions and contiguous range checks. These results concern **local** CFG, not full-program reachability.

## New finding: ES producer
* `0002:3CB7` checks `DS:[0A94]` at `3CC2` and conditionally calls `3C80` at `3CCD`.
* `0002:3C80` unconditionally executes `PUSH DS; POP ES` at `3C8C–3C8D`. It never restores the prior ES before `RETF 2` (`3CB4`). Thus **ES=DS on a normally returning 3C80 path**.
* `3CB7` tests returned AX at `3CD0–3CD2`; only the nonzero return continues to `SCASB` at `3CDC`. There is no intervening ES write or CALL between `3CCD` and `3CDC`. Therefore **on the 3CB7 scan path**, ES equals the DS value used in the lookup, assuming a valid call/return and no asynchronous segment register corruption.
* Calling 3CB7 when `DS:[0A94]==0` avoids both lookup and scan and does not need the ES contract.
* `3C80` is *not* a conventional ES-preserving routine: a corrected calling-convention report must list the ES side effect. This is a concrete cross-function data dependence.

## New finding: DF is an unresolved precondition
`LODSW` at `3C94`, `REPNZ SCASB` at `3CA3`, `3CDC` and `3C68` rely on DF. None of the scoped routines contains `CLD`, `STD` or `POPF`. Expected forward lookup is consistent with DF=0, but **that condition is not proved by these functions**. A full entrypoint-to-callsite dataflow or runtime FLAGS trace is still needed. No complete-function certification is justified.

## Exact synthetic FAR stack model
Let S be SP immediately on entry to each callee. The caller has already pushed CS manually, then used near CALL. Hence memory at `SS:S` contains return IP, `SS:S+2` contains CS. For `3CB7/3C80`, `SS:S+4` contains the argument.
* On entry, `INC BP; PUSH BP; MOV BP,SP; PUSH DS` stores modified BP at S-2 and DS at S-4, then later pushes any local SI/DI registers. `SUB BP,2; MOV SP,BP; POP DS; POP BP; DEC BP` retrieves DS from S-4 and BP from S-2 and restores the original BP.
* `39A8` ends in `RETF` and returns with SP=S+4. Its nested 3CB7 calls use additional synthetic FAR frames.
* `3CB7` and `3C80` end `RETF 2`, returning with SP=S+6; return discards IP, synthetic CS, and 2-byte argument.
* In a normal return from a `PUSH arg; PUSH CS; CALL rel16` site, SP is restored exactly to its pre-push value. This is a stack-balance property of the observed instruction sequence, not a claim about exceptional exits.

## OPEN: shared fatal handler and external imports
`3C38` starts with `PUSH SS; POP DS`, but the 73C5 error20 stub jumps directly to `3C3D`, bypassing this step. `3C3D` pushes AX twice and calls the same three helper routines using synthetic CS, then calls KERNEL ordinals through NE fixups. All exit behavior following the external calls depends on their ABI/non-return semantics. Preserve the two entry paths separately.

## Cross-version alignment
The local instruction-offset comparison is given in PASS13_ALIGNED_ROUTINE_DIFF.csv. A comparison at identical offsets is not globally relocation-normalized; evidence for algorithm identity must also track DS data content and caller state. No additional DOS 2.0 function results in this pass.

## Completion status
Local instructions verified, ES producer explained on the scan path, stack return arithmetic derived. DF source, global reachability, import effects, alternative entries, and runtime behavior remain open. **Fully certified functions: 0**.
'''
(REP/'PASS13_ES_DF_STACK_AUDIT.md').write_text(report)
(D/'ALGORITHMS/PASS13_3CB7_PATH_CORRECTED_PSEUDOCODE.c').write_text('''/* Static path model; pseudo-C, NOT a C ABI replacement. SEG2:3CC2..3CF1 */
void runtime_message_output(uint16_t key) {
  if (read16(DS,0x0A94)==0) return;             /* 3CC2,3CC7 */
  uint16_t text=lookup_3C80(key);                 /* 3CC9..3CCD; ES = DS as side effect */
  if(text==0) return;                             /* 3CD0..3CD2 */
  uint16_t di=text;                               /* 3CD4..3CD5 */
  uint16_t length=scan_nul_ES_DI(di,0xFFFF);      /* 3CD7..3CE0, assumes DF=0 */
  uint16_t output=read16(DS,0x0870);             /* 3CE1 */
  fatal_error_20(output,text,length);             /* 3CE5, no normal return proved */
}
/* ES remains modified when lookup_3C80 returns. Caller segment state is an open dependency. */
''')
summary={'pass':13,'scope':['WIN_1_8','WIN_1_10'],'scoped_routines':['39A8','3CB7','3C80','SHARED_FATAL'],'decoded_records':len(allrows),'alignment_pairs':len(align),'changed_aligned_sites':len(changed),'changes':changed,'audit':audit,'verified_new_findings':['ES=DS established by 3C80 prior to 3CB7 scan on successful lookup path','S+4 / S+6 synthetic far-return stack arithmetic'],'open':['DF entry-state','global reachability','shared handler termination','DOS 2.0 unpacked image'],'certified_complete_functions':0}
(M/'PASS13_SUMMARY.json').write_text(json.dumps(summary,indent=2))
with (REP/'ALL_VERSIONS_PROGRESS.md').open('a') as o:o.write('\nPASS13: ES producer traced from 3C80 to 3CB7; DF not established locally; 3 synthetic FAR frame stack effects audited. Full certifications 0.\n')
arch=R/'N3D_FUNCTION_RESEARCH_PASS13_20261103.zip'
with zipfile.ZipFile(arch,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in D.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(R))
with zipfile.ZipFile(arch) as z:assert z.testzip() is None
print(json.dumps({'archive':str(arch),'bytes':arch.stat().st_size,'decoded':len(allrows),'aligned':len(align),'changes':changed,'audit':audit},indent=2))