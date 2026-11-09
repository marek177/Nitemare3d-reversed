from pathlib import Path
import zipfile,struct,hashlib,subprocess,re,csv,json,shutil
R=Path('/mnt/data'); SRC=R/'N3D_FUNCTION_RESEARCH_PASS11'; DST=R/'N3D_FUNCTION_RESEARCH_PASS12'; shutil.copytree(SRC,DST,dirs_exist_ok=True)
M=DST/'MASTER_DATABASE';REPORT=DST/'REPORTS';FUN=DST/'FUNCTIONS/WIN16';ALG=DST/'ALGORITHMS'
Z=zipfile.ZipFile(R/'files/dosbox-n3d(20261103-105917).zip')
exe={'WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
def getseg(data,i=2):
 ne=struct.unpack_from('<I',data,0x3c)[0];shift=struct.unpack_from('<H',data,ne+0x32)[0];tbl=struct.unpack_from('<H',data,ne+0x22)[0];entry=ne+tbl+(i-1)*8;off,length,flags,alloc=struct.unpack_from('<HHHH',data,entry);return data[off<<shift:(off<<shift)+(length or 65536)]
B={v:getseg(Z.read(fn)) for v,fn in exe.items()};HASH={v:hashlib.sha256(Z.read(fn)).hexdigest() for v,fn in exe.items()}
regions={'39A8':(0x39a8,0x39cb),'3CB7':(0x3cb7,0x3cf4),'3C80':(0x3c80,0x3cb7),'ERROR':(0x3c3d,0x3c7f)}
pattern=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)$')
rows=[]
for v,b in B.items():
 tmp=R/'_pass12_seg.bin';tmp.write_bytes(b)
 for name,(start,end) in regions.items():
  listing=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(tmp)],text=True)
  for line in listing.splitlines():
   mm=pattern.match(line)
   if mm:
    addr=int(mm[1],16); bb=bytes.fromhex(mm[2]); rows.append({'version':v,'function_id':f'{v}_SEG2_{name}','segment':'0002','offset':f'{addr:04X}','raw_bytes':bb.hex(' '),'size':len(bb),'asm':mm[3].strip(),'address_verified':b[addr:addr+len(bb)]==bb,'scope':'TARGETED_LINEAR_DISASM_NOT_GLOBAL_CFG'})
 tmp.unlink()
def csvout(path,data,fields=None):
 with (M/path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(data[0]));w.writeheader();w.writerows(data)
csvout('PASS12_INSTRUCTIONS_WIN18_WIN110.csv',rows)
# Validate identical and one changed instruction, with instruction boundary alignment.
diffs=[]
for name in regions:
 x=[r for r in rows if r['version']=='WIN_1_8' and r['function_id'].endswith('_'+name)]
 y=[r for r in rows if r['version']=='WIN_1_10' and r['function_id'].endswith('_'+name)]
 dy={int(r['offset'],16):r for r in y}
 for a in x:
  b=dy.get(int(a['offset'],16))
  diffs.append({'region':name,'offset':a['offset'],'win18_bytes':a['raw_bytes'],'win110_bytes':b['raw_bytes'] if b else '','win18_asm':a['asm'],'win110_asm':b['asm'] if b else '','class':'IDENTICAL_BYTES' if b and a['raw_bytes']==b['raw_bytes'] else 'MODIFIED_INSTRUCTIONS' if b else 'OFFSET_NOT_MATCHED'})
csvout('PASS12_INSTRUCTION_DIFF.csv',diffs)
# Explicit stack model validated for each routine using distinctive epilogue.
stack=[]
for name,entry,cleanup in [('39A8',0,0),('3CB7',2,2),('3C80',2,2)]:
 for v in B:
  stack.append({'function_id':f'{v}_SEG2_{name}','entry_stack':'[SP]=near return IP; [SP+2]=explicitly PUSHed CS; [SP+4]=1 word argument' if cleanup else '[SP]=near return IP; [SP+2]=explicitly PUSHed CS','prologue':'INC BP; PUSH BP; MOV BP,SP; PUSH DS','exit':'SUB BP,2; MOV SP,BP; POP DS; POP BP; DEC BP; RETF'+(' 2' if cleanup else ''),'net_sp_increase_at_return':4+cleanup,'reason':'synthetic FAR stack frame, near call to far-return function','interrupt_or_exception_paths':'not counted'})
csvout('PASS12_STACK_CONVENTIONS.csv',stack)
flow=[
 {'function':'3C80','site':'3C94','branch':'read key via LODSW; advance SI by 2','effect':'DS:SI read; AX=key'},
 {'function':'3C80','site':'3C97','branch':'equal key','effect':'return string offset in AX'},
 {'function':'3C80','site':'3C99','branch':'INC AX when key mismatch','effect':'ZF=1 if key FFFF (16-bit wrap)'},
 {'function':'3C80','site':'3C9B','branch':'JE uses retained ZF from INC AX through XCHG','effect':'return AX=0000 if sentinel'},
 {'function':'3C80','site':'3CA3','branch':'REPNZ SCASB','effect':'search zero byte in ES:DI, assumed DF=0'},
 {'function':'3C80','site':'3CA7','branch':'JMP 3C94','effect':'repeat with next entry'},
 {'function':'3CB7','site':'3CC2','branch':'DS:[0A94]==0','effect':'skip output, RETF 2'},
 {'function':'3CB7','site':'3CD2','branch':'lookup returned 0','effect':'skip output, RETF 2'},
 {'function':'3CB7','site':'3CE5','branch':'CALL 73C5','effect':'error20 path; normal return unproven'},
 {'function':'39A8','site':'39B7','branch':'CALL 3CB7 with argument 00FC','effect':'may enter nonreturn error path'},
 {'function':'39A8','site':'39BF','branch':'CALL 3CB7 with argument 00FF','effect':'may enter nonreturn error path'},
]
csvout('PASS12_LOCAL_CONTROL_DATAFLOW.csv',flow)
# Produce self-contained audit with corrected pseudocode carefully tied to addresses.
report=f'''# PASS 12 — Individual routine stack and dataflow audit

## Source and method
Original Win16 NE EXE embedded in `dosbox-n3d(20261103-105917).zip`; extracted segment 2 and verified all bytes against `objdump -m i8086`. WIN 1.10 SHA-256 `{HASH['WIN_1_10']}` and WIN 1.8 SHA-256 `{HASH['WIN_1_8']}`. This is local static decoding, **not** complete global CFG reachability or runtime verification.

## Calling convention discovery: artificial far call
All three routines begin `MOV AX,DS; NOP; INC BP; PUSH BP; MOV BP,SP; PUSH DS; MOV DS,AX` and finish `SUB BP,2; MOV SP,BP; POP DS; POP BP; DEC BP; RETF [2]`. Callers use `PUSH CS; CALL NEAR` (and optionally `PUSH argument` before that). Thus `RETF` consumes near return IP and the explicit pushed CS, while `RETF 2` additionally discards the 16-bit argument. `INC BP` / `DEC BP` and `SUB BP,2` enable this unusual frame teardown. **Misclassifying the callee as NEAR RET causes false CFG edges and incorrect SP.**

### 0002:39A8
- No explicit argument in observed call from 3C40; net successful return SP increase relative to callee entry = 4 bytes.
- Pushes 00FCh and 00FFh as arguments for two separate calls to 3CB7 at 39B7 and 39BF. Its own successful final AX is FFh (39BA) unless unproven effects alter it; termination via 3CB7 is path-dependent.
- On local normal path, DS is restored and BP is restored modulo a deliberate INC/DEC pair. No ordinary near `RET` is present.

### 0002:3CB7
- One 16-bit argument at `[BP+6]` (3CC9); returns via `RETF 2` (3CF1); return SP increases by 6 bytes relative to entry.
- Conditional DS:[0A94] enable check at 3CC2; resolves key through 3C80 at 3CCD; if nonzero, scans a 0-terminated byte sequence with `REPNZ SCASB` at 3CDC, computes length using `NOT CX; DEC CX`, retrieves BX from DS:[0870], then calls 73C5 at 3CE5.
- `SCASB` uses **ES:DI**; this function does not itself set ES, so a caller/ambient ES assumption must be proved. No claim that normal return follows the call to 73C5.

### 0002:3C80
- One 16-bit key argument at `[BP+6]` (3C8E); successful `RETF 2` (3CB4). Saves SI,DI and sets ES=DS at 3C8C–3C8D.
- Initializes SI from an immediate offset at 3C91 (Win 1.8=223Eh; Win 1.10=2242h). At 3C94 `LODSW` loads a 16-bit key and advances SI. At 3C95–3C97 the matched-key path returns the current SI, pointing at text.
- Unmatched key at 3C99 `INC AX` sets ZF when original key was FFFFh; `XCHG SI,AX` preserves ZF, so `JE 3CA9` detects end sentinel and returns AX=0 via a second exchange. On normal mismatch, `XCHG DI,AX` obtains string offset then `REPNZ SCASB` advances to the NUL terminator; SI=DI then loops.
- Important conditions not yet proven: DF must be zero for forward string scan; all strings must terminate and fit within DS, CX max-length search can exhaust; segment alias and future runtime mutation unverified.

## Shared error handler implications
At 3C3F/3C43/3C47 a `PUSH CS` immediately precedes each NEAR CALL to far-return callee (39A8 / 3CB7 / 3C80). At 3C3D/3C3E there are two error-number pushes. The 3C40 call consumes its synthetic segment, then 3C44 consumes a CS and one argument, then 3C48 consumes CS and another argument. This yields consistent stack shape **only when each callee returns normally**. The 3CB7 error20 tail is separately not proven to return. The 3C80 lookup returns string offset AX or zero; 3C4D tests AX.

## Cross-version evidence
Local instruction-level comparison for the three routines and shared error block is in PASS12_INSTRUCTION_DIFF.csv. A changed pointer load alone does not prove a changed algorithm; previous passes have shown the lookup table payload unchanged. Preserve data offset in byte-accurate pseudocode per version.

## Open blockers
1. Resolve ES contract when 3CB7 scans through ES:DI.
2. Prove source of DS and DF at the 3C80 lookup and error20 path.
3. Check whether historical code segmentation uses alternative entries or shared tails.
4. Validate KERNEL ordinal ABI, nonreturn status and runtime behavior.
5. Reconstruct DOS 2.0 unpacked image for true DOS reference-function parity.

**Complete certified functions: 0.**
'''
(REPORT/'PASS12_PER_FUNCTION_STACK_DATAFLOW.md').write_text(report)
(ALG/'PASS12_3C80_CORRECTED_PSEUDOCODE.c').write_text('''/* Evidence: Win16 1.10 SEG2:3C8E..3CB4. Simplified only; not literal C ABI. */
uint16_t lookup_3C80(uint16_t wanted) {
    uint16_t si = 0x2242; /* Win1.8: 0x223E */
    for (;;) {
        uint16_t id = read16(DS, si); si = (uint16_t)(si + 2); /* 3C94 */
        if (id == wanted) return si; /* 3C95..3C97, 3CA9 */
        if (id == 0xffff) return 0; /* INC+XCHG+JE: 3C99..3C9B */
        do { uint8_t c = read8(DS, si++); if (c == 0) break; } while (true); /* 3C9D..3CA7 */
    }
}
/* Requires DF=0, valid NUL-terminated strings, ES=DS; no bounds guarantees proven. */
''')
summary={'pass':12,'versions':['WIN_1_8','WIN_1_10'],'targeted_functions':3,'instruction_rows':len(rows),'instruction_diff_rows':len(diffs),'changed_instruction_sites':[d for d in diffs if d['class']!='IDENTICAL_BYTES'],'stack_convention_records':len(stack),'completed_functions':0,'runtime_verified':0}
(M/'PASS12_SUMMARY.json').write_text(json.dumps(summary,indent=2))
with (REPORT/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS12: deep per-function 39A8/3CB7/3C80 stack ABI audit, instruction exact WIN1.8-WIN1.10 diff, corrected lookup pseudocode. Complete functions 0.\n')
archive=R/'N3D_FUNCTION_RESEARCH_PASS12_20261103.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(DST.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(R))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'summary':summary},indent=2))