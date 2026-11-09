from pathlib import Path
import shutil,zipfile,csv,json,subprocess,re,hashlib
root=Path('/mnt/data'); src=root/'N3D_FUNCTION_RESEARCH_PASS05'; dst=root/'N3D_FUNCTION_RESEARCH_PASS06'
shutil.copytree(src,dst,dirs_exist_ok=True)
db=dst/'MASTER_DATABASE'; rpt=dst/'REPORTS';fn=dst/'FUNCTIONS'/'WIN16'
segs={v:(src/'REFERENCES'/v/'NE_SEG_02.bin').read_bytes() for v in ['WIN_1_8','WIN_1_10']}
rx=re.compile(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2} )+)\s+([^\s]+)(?:\s+(.*))?$',re.I)
def decode(v,a,end):
 p=src/'REFERENCES'/v/'NE_SEG_02.bin'
 s=subprocess.run(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={a}',f'--stop-address={end}',str(p)],capture_output=True,text=True,check=True).stdout
 rows=[]
 for line in s.splitlines():
  m=rx.match(line)
  if m: rows.append(dict(address=int(m[1],16),bytes=' '.join(m[2].split()),mnemonic=m[3],operands=(m[4] or '').strip()))
 return rows
regions=[('lookup',0x3c80,0x3cb7),('consumer',0x3cb7,0x3cf4),('bridge',0x73c5,0x73cb),('shared_target',0x3c3d,0x3c7f),('other_entry',0x3c38,0x3c3d),('pointer_bound_helper',0x73d9,0x73fe)]
inst=[];diff=[];reports=[]
for name,a,b in regions:
 x={v:decode(v,a,b) for v in segs}
 for v in segs:
  for i in x[v]:inst.append(dict(version=v,region=name,segment=2,**i))
 first={r['address']:r for r in x['WIN_1_8']};second={r['address']:r for r in x['WIN_1_10']}
 for addr in sorted(set(first)|set(second)):
  p=first.get(addr);q=second.get(addr)
  st='IDENTICAL_BYTES' if p and q and p['bytes']==q['bytes'] else 'MODIFIED_AT_SAME_OFFSET' if p and q else 'ONLY_ONE_SIDE'
  diff.append(dict(region=name,segment=2,address=f'{addr:04X}',classification=st,win18_bytes=p['bytes'] if p else '',win110_bytes=q['bytes'] if q else '',win18_asm=(p['mnemonic']+' '+p['operands']) if p else '',win110_asm=(q['mnemonic']+' '+q['operands']) if q else ''))
 reports.append(dict(region=name,start=f'{a:04X}',end_exclusive=f'{b:04X}',win18_instructions=len(x['WIN_1_8']),win110_instructions=len(x['WIN_1_10']),modified=sum(y['classification']!='IDENTICAL_BYTES' for y in diff if y['region']==name)))
 for v in segs:
  asm='\n'.join(f"{i['address']:04X}  {i['bytes']:<22} {i['mnemonic']:<8} {i['operands']}" for i in x[v]); (fn/f'PASS06_{v}_{name}.asm.txt').write_text(asm+'\n')
def csvout(path,items,fields):
 with open(path,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(items)
csvout(db/'PASS06_INSTRUCTION_EVIDENCE.csv',inst,['version','region','segment','address','bytes','mnemonic','operands'])
csvout(db/'PASS06_EXACT_OFFSET_DIFF.csv',diff,['region','segment','address','classification','win18_bytes','win110_bytes','win18_asm','win110_asm'])
csvout(db/'PASS06_REGIONS.csv',reports,['region','start','end_exclusive','win18_instructions','win110_instructions','modified'])
# CFG edges directly evidenced by opcodes
edges=[('0002:3C80','0002:3C94','initial_loop'),('0002:3C97','0002:3CA9','JE_match'),('0002:3C9B','0002:3CA9','JE_terminator'),('0002:3CA7','0002:3C94','JMP_next'),('0002:3CB7','0002:3C80','FAR_call_push_CS_near_call'),('0002:3CB7','0002:73C5','NEAR_call'),('0002:73C5','0002:3C3D','JMP_tail_to_shared'),('0002:3C38','0002:3C3D','fallthrough'),('0002:3C3D','0002:39A8','FAR_call_push_CS_near_call'),('0002:3C3D','0002:3CB7','FAR_call_push_CS_near_call'),('0002:3C3D','0002:3C80','FAR_call_push_CS_near_call')]
(dst/'CFG'/'PASS06_FOCUSED_CALLGRAPH.json').write_text(json.dumps([dict(source=a,target=b,type=c) for a,b,c in edges],indent=2))
report='''# PASS 06 — Windows 1.8 / 1.10: symbol lookup and shared error path

## Scope and evidence
- The two 16-bit segment-2 images are the original unrelocated NE segment bytes copied from PASS05.
- Decoder is GNU objdump in i8086 mode. Full instruction data and two-version offset comparison are in `MASTER_DATABASE/PASS06_INSTRUCTION_EVIDENCE.csv` and `PASS06_EXACT_OFFSET_DIFF.csv`.
- All interpretations below are static. Runtime behavior is NOT verified. No full function is certified.

## Finding 1: `0002:3C80` is a table lookup over a WORD key followed by a zero-terminated string (high-confidence static reconstruction)

At `3C91`, `MOV SI,2242h` (Win 1.10); at `3C94` `LODSW` reads from **DS:SI**, not CS:SI. Win1.8 loads `223Eh`. `DS` is copied to `ES` at `3C8C..3C8D`. Comparing the bytes at CS:223E and CS:2242 would therefore be UNSOUND until the caller's DS is proven.

Instruction mapping:
- 3C8E: key from [BP+6] into DX.
- 3C91: table base offset (DS relative).
- 3C94: LODSW obtains current key and advances SI by two (assuming direction flag clear).
- 3C95..3C97: equality test; on match returns offset to string following WORD.
- 3C99..3C9B: `INC AX; XCHG SI,AX; JE` tests original WORD == FFFFh (the XCHG does not modify flags); then return zero after 3CA9 XCHG.
- 3C9D..3CA3: `XCHG DI,AX; XOR AX,AX; MOV CX,FFFFh; REPNZ SCASB` scans next zero terminator in ES.
- 3CA5..3CA7: SI=DI, jump back to next WORD entry.
- 3CA9..3CB4: AX=string offset or zero; restore saved registers, FAR return and pop 2 argument bytes.

**Conditions / unresolved:** DF must be zero for forward LODSW and SCASB; available in-segment table and max scan length are not yet proved. SCASB failure at 65535 bytes, segment wrap, and malformed tables remain to be checked. Segment identity, table contents, and callers other than known ones are unresolved.

### Corrected pseudocode (not raw Ghidra output)
```c
// DS and ES point to the same runtime data segment; DF=0 precondition.
uint16_t lookup_message(uint16_t key) {
    uint16_t si = TABLE_OFFSET; // 0x223E in Win1.8, 0x2242 in Win1.10
    for (;;) {
        uint16_t entry_key = read16(DS, si); si += 2;     // 3C94
        if (entry_key == key) return si;                 // 3C95-3C97, 3CA9
        if (entry_key == 0xFFFF) return 0;               // 3C99-3C9B, 3CA9
        // SCASB searches for a NUL in ES; loaded ES = DS at 3C8C-3C8D.
        si = scan_past_nul(ES, si);                       // 3C9D-3CA7
    }
}
```

The pseudocode assumes the normal no-wrap bounded-string interpretation. Exact 16-bit wrap and REP bounds are preserved in the ASM evidence and not yet specified in the higher-level reconstruction.

## Finding 2: `0002:3CB7` uses the lookup and may invoke a shared error path
- `3CC2..3CC7`: if `DS:0A94 == 0`, skip the lookup/action.
- `3CC9..3CCD`: push key and CS; near call `3C80` behaves as a constructed FAR call, consistent with `RETF 2` of callee.
- `3CD0..3CD2`: if AX = 0, skip action.
- `3CD4..3CE0`: uses ES:DI to scan a zero-terminated string and derives length in CX.
- `3CE1..3CE5`: BX = DS:0870; calls `73C5`.
- `73C5..73CA`: sets AX=0014h and jumps to `3C3D` (does not RET).
- `3C3D..`: shared code calls `39A8`, `3CB7`, and `3C80`, then includes relocatable FAR external calls; a full path-sensitive treatment is pending.

**Critical subtlety:** `73C5` is a jump thunk into shared cleanup/error flow, not a separate locally returning function. It changes the callgraph and means the analysis cannot conclude that `3CB7` simply returns after the call. The `3C38` predecessor executes PUSH SS / POP DS and sets AX=3; the jump from `73C5` reaches `3C3D` without running that predecessor. Therefore the DS state on each entry must be analyzed separately.

## Finding 3: cross-version change in another shared helper
- `0002:73E0` (both versions): `CMP BX, 4684h` (Win1.8) vs `CMP BX, 4688h` (Win1.10); exact change +4 bytes in an apparent pointer limit.
- `0002:3C91`: DS-table offset +4 bytes (`223E` -> `2242`).
- These correlated +4 shifts suggest a possible data-layout change, but are NOT proof of an added table element or semantic equivalence. DS segment data, relocation references and runtime values must be checked.

## Outstanding blockers
1. Establish DS/ES and runtime data segment mapping from callers and NE loader.
2. Locate and reconstruct the lookup table in the **correct** data segment (not code segment 2).
3. Analyze the target 3C3D through the external call fixups and exit paths.
4. Analyze all predecessors of 73C5 / 3C3D and stack balance, including the constructed FAR calls.
5. Check Win1.0, 1.3, 1.6 for equivalent functions by CFG/semantics, not only same offsets.
6. DOS2 remains packed/unmapped; no DOS cross-platform function claim.

**Verification status: static, partial; runtime not performed; certified complete functions = 0.**
'''
(rpt/'PASS06_SYMBOL_LOOKUP_SHARED_ERROR.md').write_text(report)
(dst/'ALGORITHMS'/'PASS06_lookup_message_corrected.c').write_text('''/* Static reconstruction, NOT yet runtime verified. See PASS06 report for assumptions. */\n#include <stdint.h>\nuint16_t lookup_message(uint16_t key, uint16_t base, const uint8_t *data) {\n  uint16_t si=base;\n  for (;;) {\n    uint16_t word=(uint16_t)(data[si] | (data[(uint16_t)(si+1)] << 8)); si=(uint16_t)(si+2);\n    if (word==key) return si;\n    if (word==0xffff) return 0;\n    /* NOTE: unbounded search is only an approximation; the real SCASB has CX=FFFFh. */\n    while (data[si] != 0) si=(uint16_t)(si+1);\n    si=(uint16_t)(si+1);\n  }\n}\n''')
with open(rpt/'ALL_VERSIONS_PROGRESS.md','a') as f:f.write('\nPASS06: Win 1.8/1.10 DS-relative lookup 3C80 and shared tail 73C5 -> 3C3D traced; additionally CMP BX bound +4 at 73E0. Static partial only; 0 certified functions.\n')
shutil.make_archive(str(root/'N3D_FUNCTION_RESEARCH_PASS06_20261103'),'zip',root,dst.name)
print(json.dumps({'regions':reports,'modified':[d for d in diff if d['classification']!='IDENTICAL_BYTES'],'package':str(root/'N3D_FUNCTION_RESEARCH_PASS06_20261103.zip')},indent=2))