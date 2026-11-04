import pathlib,json,csv,struct,re,hashlib,collections,zipfile,shutil,platform
from capstone import *
from unicorn import *
from unicorn.x86_const import *
R=pathlib.Path(__file__).resolve().parents[1];md=Cs(CS_ARCH_X86,CS_MODE_16)
rows=[];diff=[];tests=[]
for p in sorted((R/'VERSIONS/DOS').glob('*.loaded.bin')):
 hits=list(re.finditer(b'\xbb..\xc6\x07\x01\x83\xc3\x12\x81\xfb..\x72\xf4\xcb',p.read_bytes(),re.S))
 for m in hits:
  start,end=struct.unpack_from('<H',m[0],1)[0],struct.unpack_from('<H',m[0],11)[0];assert end-start==1800
  row={'file':p.name,'image_offset':hex(m.start()),'start_DS_offset':hex(start),'limit_DS_offset':hex(end),'stride':18,'writes':100,'bytes':m[0].hex(),'classification':'IDENTICAL_BYTES'if start==0x50f2 else'MODIFIED_INSTRUCTIONS','algorithm_status':'same_strided_write_algorithm_modulo_DS_base_offsets'};rows.append(row)
  for i,ri in zip(md.disasm(m[0],m.start()%16),md.disasm(bytes.fromhex('bbf250c6070183c31281fbfa5772f4cb'),10)):
   if i.bytes!=ri.bytes:diff.append({'function_id':'DOS_2_0_0201_000A','version_a':p.name,'version_b':'DOS_2_0','address_a':hex(m.start()+i.address-m.start()%16),'address_b':f'0201:{ri.address:04X}','old_bytes':i.bytes.hex(),'new_bytes':ri.bytes.hex(),'old_asm':i.mnemonic+' '+i.op_str,'new_asm':ri.mnemonic+' '+ri.op_str,'status':'operand_address_changed; behavioral_effect_depends_on_DS_layout'})
  for case in range(8):
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,m[0]);u.mem_write(0x40000,bytes([case*31])*65536);u.reg_write(UC_X86_REG_DS,0x4000);u.reg_write(UC_X86_REG_CS,0x1000);u.reg_write(UC_X86_REG_SS,0x7000);u.reg_write(UC_X86_REG_SP,0x8000);u.mem_write(0x78000,struct.pack('<HH',0x100,0x2000));u.emu_start(0x10000,0x20100,count=1000)
   expected=bytearray([case*31]*65536)
   for k in range(100):expected[start+18*k]=1
   assert bytes(u.mem_read(0x40000,65536))==expected and u.reg_read(UC_X86_REG_BX)==end
  tests.append({'file':p.name,'cases':8,'status':'PASS'})
(R/'ASM_DIFF/DOS_stride_cross_version.json').write_text(json.dumps(rows,indent=2));(R/'RUNTIME_EVIDENCE/cross_version_stride_tests.json').write_text(json.dumps(tests,indent=2))
with (R/'ASM_DIFF/INSTRUCTION_LEVEL_DIFF.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(diff[0]));w.writeheader();w.writerows(diff)
# Remove dossiers from superseded traversal; do not retain false segment-zero seeds.
master=list(csv.DictReader((R/'MASTER_DATABASE/FUNCTION_MASTER.csv').open()));ids={x['function_id']for x in master}
for p in (R/'FUNCTIONS').rglob('*'):
 if p.is_file()and p.stem not in ids:p.unlink()
# Supplemental evidence deliberately does not elevate candidates to exhaustive completion.
dos='''# DOS_2_0_0201_000A — audited strided initialization

Binary SHA-256: 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301.
Address is load-module relative segment:offset. Snapshot offset 0x201A. Runtime physical address at load segment 0x1000: 0x1201A. Disk offset is NOT obtained by adding the MZ header to this unpacked-image address.

Confirmed static body: 16 bytes, six instructions, one far return, no calls. Entry has a direct call reference in the generated callgraph. Exact alternative entry points, aliases, record meaning and full caller-context proof remain open.

| Address | Bytes | Operation | Local effect |
|---|---|---|---|
|0201:000A|bbf250|MOV BX,50F2|BX := 0x50F2; flags unchanged|
|0201:000D|c60701|MOV byte DS:[BX],1|write one byte; flags unchanged|
|0201:0010|83c312|ADD BX,18|16-bit addition; CF/PF/AF/ZF/SF/OF updated|
|0201:0013|81fbfa57|CMP BX,57FA|unsigned comparison; arithmetic flags updated|
|0201:0017|72f4|JB 000D|branch when CF=1; flags unchanged|
|0201:0019|cb|RETF|pop IP then CS; SP += 4 modulo 65536|

CFG blocks: B0 000A→B1; B1 000D–0017→B1 when unsigned BX<0x57FA, else B2; B2 0019→far caller. No unresolved local branch in this body. Stack has only the far return pair; no local frame or arguments accessed.

Precondition: executable body, mapped DS and valid far-return stack; arbitrary overlapping code/stack/data invalidates the simple model. DS origin remains unknown. CPU executes 16-bit real-mode addresses in the DOS experiment. No wrap occurs in this loop: BX advances from 0x50F2 to 0x57FA. Loop invariant at iteration k: BX=0x50F2+18*k and bytes for indices below k equal 1. Exactly 100 stores target 0x50F2..0x57E8 at stride 18. Final BX=0x57FA. Other general registers and segment registers preserved, excluding CS:IP return; SP advances four. Final arithmetic flags CF=0, PF=1, AF=0, ZF=1, SF=0, OF=0. Other modeled flags preserved. No RNG, API, timing or other globals accessed by this body.

Corrected instruction-faithful pseudocode:
```c
BX = 0x50F2;                           // 000A
 do {
    store8(DS, BX, 1);                 // 000D
    BX = (uint16_t)(BX + 18);          // 0010
    FLAGS = cmp16_flags(BX, 0x57FA);   // 0013
 } while (FLAGS.CF);                   // 0017
 far_return();                        // 0019
```
Behavioral reconstruction (memory effect only; machine state above must also be preserved):
```c
for (unsigned k=0; k<100; ++k)         // 0010–0017
    ds_bytes[0x50F2 + 18*k] = 1;      // 000D
```
RAW Ghidra/IDA decompilation unavailable. Do not label this hand reconstruction raw decompiler output.

Cross-version evidence: all nine supplied unpacked DOS snapshots contain exactly one matching instruction template, with start/limit offsets changing together and always 1800 bytes apart. These are candidate correspondences by exact opcode/CFG pattern; full data-structure identity is not proved. See DOS_stride_cross_version.json and INSTRUCTION_LEVEL_DIFF.csv. Earlier versions are MODIFIED_INSTRUCTIONS (two address immediates); same local algorithm under an explicit DS-offset mapping, not proven same gameplay behavior. A differentiating test watches the old/new DS offsets and establishes record-base correspondence from callers.

Validation: 128 randomized isolated CPU cases verify all 64 KiB of DS, preserved registers, FLAGS and return stack. Additional eight cases per nine supplied snapshots pass. These are Unicorn experiments, not original DOSBox gameplay. Full boundary/alias/caller proof, record semantics and actual gameplay runtime remain UNKNOWN. Status: LOCAL_SEMANTICS_EMULATION_VERIFIED; exhaustive completion false.
'''
win='''# WIN_1_10_0001_53CA — audited export ordinal 1

Binary hash and original bytes are in the master database. NE segment 1 file base 0x4C0, export offset 0x53CA, disk offset 0x588A. No real-mode CS=1 assertion: 1 is an NE segment index; the Windows loader assigns a selector.

Confirmed body: 14 bytes, nine instructions, single basic block, one RETF, no calls. Export table establishes an entry. Other entry aliases and external callers remain unknown.

|Offset|ASM|Effect|
|---|---|---|
|53CA|MOV AX,SS|Read SS into AX|
|53CC|PUSH BP|SP-=2; save BP|
|53CD|MOV BP,SP|Frame base|
|53CF|PUSH DS|SP-=2; save DS|
|53D0|MOV DS,AX|Temporarily set DS=SS|
|53D2|MOV AX,0x0250|Set AX=592|
|53D5|POP DS|Restore DS; SP+=2|
|53D6|LEAVE|SP=BP; restore BP; SP+=2|
|53D7|RETF|Pop IP:CS; SP+=4|

For a valid non-aliasing mapped stack, this body returns AX=0x0250, preserves BX/CX/DX/SI/DI/BP/DS/ES and modeled FLAGS, and consumes only the four-byte far return pair. Stack memory below entry SP is overwritten by saved BP/DS even though SP is restored before return. No input parameters are read. No data memory access other than stack; no loops, RNG or timing. Protected-mode descriptor faults/privilege checks are not tested by real-mode Unicorn.

Corrected pseudocode, retaining intermediate operations:
```c
AX=SS; push16(BP); BP=SP;              // 53CA–53CD
push16(DS); DS=AX;                    // 53CF–53D0
AX=0x0250;                           // 53D2
DS=pop16(); SP=BP; BP=pop16();        // 53D5–53D6
far_return();                        // 53D7
```
Behavioral pseudocode: `return_far_u16(0x0250);` (53CA–53D7), with preserved registers/stack writes as specified above. RAW Ghidra/IDA unavailable. The value's application meaning is UNKNOWN; do not infer a version API solely from constant 0x250.

All eight supplied game NE files export identical 14 bytes at ordinal 1. Earlier labeled builds use 0001:53B6; reference and its aliases use 0001:53CA. Classification IDENTICAL_BYTES; location shift recorded independently. See audited_function_cross_version.json. No added/removed instructions or local CFG changes. Identity of whole binaries differs from equality of this export.

Validation: 128 randomized isolated Unicorn cases pass AX, preserved registers, low FLAGS, DS memory and far-return checks. This does not test the Win16 loader or original Windows execution. Exact caller semantics, alternate entries and protected-mode runtime remain unknown. Status LOCAL_SEMANTICS_EMULATION_VERIFIED; exhaustive completion false.
'''
(R/'FUNCTIONS/DOS/DOS_2_0_0201_000A_AUDIT.md').write_text(dos);(R/'FUNCTIONS/WIN16/WIN_1_10_0001_53CA_AUDIT.md').write_text(win)
for fid,platform in [('DOS_2_0_0201_000A','DOS'),('WIN_1_10_0001_53CA','WIN16')]:
 with (R/'FUNCTIONS'/platform/(fid+'.md')).open('a') as f:f.write('\n## Audited supplement\n\nSee '+fid+'_AUDIT.md for verified local semantics, hand pseudocode, CFG and isolated-emulation evidence. Exhaustive completion remains false.\n')
# Verify inventory duplicates by digest; preserve filename claim versus proven identity.
inv=json.loads((R/'MASTER_DATABASE/BINARY_INVENTORY.json').read_text());groups=collections.defaultdict(list)
for x in inv:groups[x['sha256']].append(x['path'])
(R/'MASTER_DATABASE/DUPLICATE_BINARIES.json').write_text(json.dumps({k:v for k,v in groups.items()if len(v)>1},indent=2))
metrics=json.loads((R/'MASTER_DATABASE/METRICS.json').read_text());table='| File (filename claim) | Candidate functions |\n|---|---:|\n'+'\n'.join('|'+x['file']+'|'+str(x['candidate_functions'])+'|'for x in metrics)
report='''# Nitemare 3D — evidence baseline PASS001, 2026-11-04

This is a fresh, reproducible baseline from dosbox-n3d(20261103-105917).zip. It does not replace or claim to merge prior PASS reports not inspected in this session.

## Results

- Inventoried 20 EXEs (including two map editors); SHA-256 for every file.
- Captured nine packed DOS loader handoffs at load segment 0x1000, retaining raw input hashes and full 512 KiB post-unpack snapshots. Five hundred twelve KiB is the capture window, not the executable's proven image extent. Snapshots retain load-base relocation values and stale loader memory, so their hash is not a canonical executable hash.
- DOS reference N3D-UNFU.exe and N3D-E-20.EXE are byte-identical. Despite its name, UNFU contains the packed loader; direct disk-offset disassembly would analyze the wrong image.
- Parsed all nine NE files, preserving code/data segments, exports, relocation source chains and import ordinal records separately from DOS. Unallocated NE segments have no disk-backed bytes; the reported zero length encodes 64 KiB but is not a disk span.
- Found 238 DOS 2.0 and 968 Win 1.10 function candidates by recursive traversal from entry/call/export/relocated immediate far-control seeds. These are not proven totals. Indirect callbacks, PUSH CS/CALL/RETF conventions, tail calls, shared blocks and overlaps require further recovery.
- Generated 1,206 individual candidate dossiers and ASM listings, 55,507 per-function instruction rows (shared instructions may occur in several dossiers), 9,886 reference-to-file byte-signature comparisons, CFG instruction graphs, local decoder register metadata and unresolved-edge records.
- Audited DOS 0201:000A (100 byte writes at stride 18) and Win NE export ordinal 1 (returns AX=0x0250) individually. 256 randomized CPU cases plus 72 cross-version loop cases passed, 328 total. No original gameplay/runtime parity claim.
- The DOS loop differs across filename-labeled builds only in two DS address immediates within the matching 16-byte template; 100 records remain constant. Full record identity remains unknown. Win ordinal 1 body is identical across all eight supplied game NE files.

## Version identity caveats

DOS 1.5 is absent by filename. Version strings have not yet been validated against release provenance. N3D-E-18.EXE and N3D-E-19.EXE have identical whole-file SHA-256; these cannot establish independent 1.8-versus-1.9 behavior differences. NITE3W.EXE duplicates NITE3W - 16.EXE; nite3w1.exe and nite3w2.exe duplicate the labeled 1.10 reference. Packed N3d.exe reaches INT 21h during the generic unpack probe and was not analyzed as a recovered image.

## Completion accounting

All 1,206 candidates remain CANDIDATE_STATIC_PARTIAL. Confirmed exhaustive functions: 0; full boundary/alias proof: 0; verified complete program CFGs: 0; original gameplay runtime-verified functions: 0. Two bodies have local semantics and isolated-emulation evidence. No percentages or invented total function counts. Unmatched signatures remain UNKNOWN_MATCH, never automatically ADDED or REMOVED. Exact-byte signatures concatenate decoded reachable bytes and do not prove whole-function layout or semantic equivalence.

'''+table+'''

## Reproduction

Python 3 with capstone==5.0.7 and unicorn==2.1.4. Extract package preserving inputs/ beside N3D_FUNCTION_RESEARCH/. From that parent directory run:

```
python N3D_FUNCTION_RESEARCH/TOOLS/unpack_probe.py
python N3D_FUNCTION_RESEARCH/TOOLS/research.py
python N3D_FUNCTION_RESEARCH/TOOLS/verify_functions.py
python N3D_FUNCTION_RESEARCH/TOOLS/finalize_pass.py
```

The original EXEs are supplied in inputs/. Loader emulation has an instruction budget, no gameplay service emulation. No Ghidra/IDA raw output is available: hand pseudocode is labeled accordingly. EFLAGS metadata in the automated database is a decoder bitmask, not a complete instruction semantics proof. FUNCTION_DATAFLOW.json is explicitly a placeholder for full interinstruction dataflow.

## Next unresolved work

Resolve indirect calls and callback tables; verify stack-sensitive PUSH CS/near CALL/RETF paths; recover tail/shared blocks; prove each candidate boundary; establish DS provenance for the 100-record initializer; validate Win16 selector/fixup behavior in the loader; import genuine Ghidra/IDA raw decompilation; validate per-version release identities. Compare neighboring versions and classify normalized assembly only after relocation-aware correspondence is proved. Gameplay tests remain required for behavioral parity.
'''
(R/'REPORTS/PASS001_EVIDENCE_BASELINE.md').write_text(report);(R/'README.md').write_text(report)
(R/'PSEUDOCODE/FUNCTION_PSEUDOCODE.md').write_text(dos+'\n\n'+win)
(R/'ASM_DIFF/FUNCTION_SEMANTIC_DIFF.md').write_text('''# Verified local differences

See DOS_stride_cross_version.json and INSTRUCTION_LEVEL_DIFF.csv: two DS address immediates change; stride=18 and count=100 stay constant. Same local algorithm under explicit offset mapping, unverified structure identity/game behavior. Win export ordinal 1 has identical bytes in all eight supplied NE game files; only location shifts. No full-program semantic-equivalence claim.
''')
# Keep original reference binaries and a hash manifest for checkpoint validation.
shutil.copy2(R.parent/'inputs/nite3/dos/N3D-UNFU.exe',R/'REFERENCES/DOS_2_0/N3D-UNFU.exe');shutil.copy2(R.parent/'inputs/nite3/windows/nite3w - 110.exe',R/'REFERENCES/WIN_1_10/nite3w110.exe')
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in R.rglob('*')if p.is_file()and p.name!='CHECKSUMS.json'};(R/'CHECKSUMS.json').write_text(json.dumps(manifest,indent=2))
print('audited loop versions',len(rows),'instruction changes',len(diff),'total CPU cases',256+sum(x['cases']for x in tests));print('files',len(manifest))
