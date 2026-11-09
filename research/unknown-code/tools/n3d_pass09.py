from pathlib import Path
import struct,csv,json,zipfile,shutil,hashlib,subprocess,re
root=Path('/mnt/data');old=root/'N3D_FUNCTION_RESEARCH_PASS08';dst=root/'N3D_FUNCTION_RESEARCH_PASS09'
shutil.copytree(old,dst,dirs_exist_ok=True)
md=dst/'MASTER_DATABASE';reports=dst/'REPORTS'; reports.mkdir(exist_ok=True)
z=zipfile.ZipFile(root/'files'/'dosbox-n3d(20261103-105917).zip')
versions={'WIN_1_0':'nite3/windows/NITE3W -10.EXE','WIN_1_3':'nite3/windows/NITE3W - 13.EXE','WIN_1_6':'nite3/windows/NITE3W - 16.EXE','WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
fixups=list(csv.DictReader(open(md/'NE_FIXUP_EXPANDED_SITES.csv')))
def csvout(name,rows,cols):
 with (md/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
segments={}; meta=[]
for ver,path in versions.items():
 blob=z.read(path);ne=struct.unpack_from('<I',blob,0x3c)[0]; shift=struct.unpack_from('<H',blob,ne+0x32)[0];segt=struct.unpack_from('<H',blob,ne+0x22)[0];count=struct.unpack_from('<H',blob,ne+0x1c)[0];auto=struct.unpack_from('<H',blob,ne+0x0e)[0]
 for num in range(1,count+1):
  sector,length,flags,minalloc=struct.unpack_from('<HHHH',blob,ne+segt+(num-1)*8)
  seg=blob[sector<<shift:(sector<<shift)+(length or 65536)] if sector else b''
  segments[ver,num]=seg
  meta.append(dict(version=ver,segment=num,autodata=auto,stored_bytes=len(seg),flags=f'{flags:04X}',sha256=hashlib.sha256(seg).hexdigest() if seg else ''))
csvout('PASS09_SEGMENT_INVENTORY.csv',meta,list(meta[0]))
# Locate direct 16-bit addressing variants *as byte candidates* without false claims about aligned instructions.
patterns={'MOV_BX_DIRECT_A96':bytes.fromhex('8b 1e 96 0a'),'ADD_WORD_A96_4':bytes.fromhex('83 06 96 0a 04'),'MOV_AX_DIRECT_A96':bytes.fromhex('a1 96 0a'),'MOV_DIRECT_A96_AX':bytes.fromhex('a3 96 0a'),'MOV_DIRECT_A96_IMM':bytes.fromhex('c7 06 96 0a')}
for op in [0x89,0x8b,0x01,0x03,0x29,0x2b,0x39,0x3b,0xff,0x8f,0x87]:
 for modrm in range(256):
  if (modrm&0xc7)==0x06: patterns[f'GEN_{op:02X}_{modrm:02X}']=bytes([op,modrm,0x96,0x0a])
refs=[]
for (ver,seg),b in segments.items():
 if not b:continue
 for name,pat in patterns.items():
  pos=0
  while 1:
   at=b.find(pat,pos)
   if at<0:break
   refs.append(dict(version=ver,segment=seg,offset=f'{at:04X}',pattern=name,bytes=b[at:at+min(8,len(b)-at)].hex(' '),certainty='BYTE_PATTERN_CANDIDATE'))
   pos=at+1
csvout('PASS09_DIRECT_A96_BYTE_CANDIDATES.csv',refs,['version','segment','offset','pattern','bytes','certainty'])
# Evidence for actual decoded instructions in disassembly rooted at documented 73D4 location for 1.8 and 1.10.
aligned=[]
for ver in ('WIN_1_8','WIN_1_10'):
 b=segments[ver,2]
 p=dst/'REFERENCES'/ver/'NE_SEG_02.bin'
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 for lo,hi,label in ((0x73d4,0x73fe,'APPEND'),(0x3c38,0x3c80,'FATAL_SHARED'),(0x3c80,0x3cd5,'LOOKUP')):
  out=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={lo}',f'--stop-address={hi}',str(p)],text=True)
  (reports/f'PASS09_{ver}_{label}.asm.txt').write_text(out)
  for line in out.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)',line)
   if not m:continue
   instr=m[3].strip();raw=m[2].strip();addr=int(m[1],16)
   aligned.append(dict(version=ver,segment=2,region=label,address=f'{addr:04X}',bytes=raw,mnemonic=instr,certainty='LINEAR_FROM_KNOWN_REGION_NOT_FULL_CFG'))
csvout('PASS09_TARGETED_ASM.csv',aligned,list(aligned[0]))
# Resolve actual NE relocation records for original opcode 9A operand at 3C72 / 3C7B.
far=[]
for ver in versions:
 b=segments[ver,2]
 for opaddr in (0x3c71,0x3c7a):
  if opaddr>=len(b):continue
  valid=b[opaddr]==0x9a
  matching=[r for r in fixups if r['version']==ver and r['segment']=='2' and int(r['source_offset'],16)==opaddr+1]
  far.append(dict(version=ver,opcode_address=f'0002:{opaddr:04X}',opcode=f'{b[opaddr]:02X}',is_far_call_opcode=valid,operand=b[opaddr+1:opaddr+5].hex(' '),relocation_targets=';'.join(r['target'] for r in matching),reloc_record_count=len(matching),evidence='ORIGINAL_EXE_OPCODE_AND_NE_FIXUP' if valid and matching else 'NOT_VERIFIED'))
csvout('PASS09_RESOLVED_FAR_IMPORTS.csv',far,list(far[0]))
# Contextual audit of on-disk DS offsets and comparisons; do not conflate runtime image with file-backed initialization.
data=[]
for ver in versions:
 ds=segments[ver,10];code=segments[ver,2]
 v=struct.unpack_from('<H',ds,0xa96)[0] if len(ds)>0xa98 else None
 # only the targeted win1.8/1.10 code offsets confirmed, others inferred from pass08 report independently
 limit={'WIN_1_0':0x45c2,'WIN_1_3':0x45c2,'WIN_1_6':0x467a,'WIN_1_8':0x4684,'WIN_1_10':0x4688}[ver]
 data.append(dict(version=ver,autodata_segment=10,ds_a96_disk=f'{v:04X}' if v is not None else '',ds_a96_bytes=ds[0xa96:0xa98].hex(' '),candidate_bound=f'{limit:04X}',raw_delta=limit-v if v is not None else None,a96_window=ds[0xa90:0xaa0].hex(' '),bound_window=ds[limit-8:limit+8].hex(' ') if len(ds)>limit+8 else '',status='32_RECORD_WINDOW_HYPOTHESIS' if limit-v==128 else 'OLDER_DATA_LAYOUT_UNRESOLVED'))
csvout('PASS09_DS_INIT_AUDIT.csv',data,list(data[0]))
# Direct call-site screening for 73D4 and 73D9 in segment2 across versions using near CALL displacements.
callrows=[]
for ver in versions:
 b=segments[ver,2]
 for i in range(len(b)-2):
  if b[i]!=0xe8:continue
  displacement=struct.unpack_from('<h',b,i+1)[0];tgt=(i+3+displacement)&0xffff
  if tgt not in (0x73d4,0x73d9,0x73c5):continue
  callrows.append(dict(version=ver,site=f'{i:04X}',target=f'{tgt:04X}',bytes=b[i:i+3].hex(' '),confidence='RAW_E8_PATTERN_NEEDS_CFG_ALIGNMENT'))
csvout('PASS09_NEAR_CALL_TARGET_CANDIDATES.csv',callrows,['version','site','target','bytes','confidence'])
# Summary and uncertainty
summary={'pass':'09','originals_checked':len(versions),'raw_direct_A96_candidates':len(refs),'windows_110_patterns':[r for r in refs if r['version']=='WIN_1_10'],'far_calls':far,'data':data,'near_call_candidates':callrows,'certified_complete_functions':0}
(md/'PASS09_SUMMARY.json').write_text(json.dumps(summary,indent=2))
win=[r for r in far if r['version']=='WIN_1_10']
report=f'''# PASS 09 — targeted provenance of DS:0A96 and NE imports

## Original-byte evidence
- Windows 1.10 auto-data segment 10 stores `DS:[0A96] = 4608h`, with the candidate `4688h` bound yielding 128 bytes, i.e. 32 four-byte records. This is **an on-disk initializer**, not a claim about every runtime state.
- Windows 1.8 stores `4604h` with bound `4684h`; Windows 1.6 stores `45FAh` with bound `467Ah`. Both also have the 128-byte window.
- Windows 1.0/1.3 store `7241h` at offset `0A96h`; these builds cannot be assigned the later pointer model without recovering their separate layout and live DS context.
- The **only exact direct opcode patterns** found in the WIN1.10 file-backed segments targeting `0A96h` (from the targeted pattern vocabulary) are listed in PASS09_DIRECT_A96_BYTE_CANDIDATES.csv. An exhaustive search of *all* indirect writers requires complete reachability, alias analysis, and xrefs; this pass does not prove their absence.

## External calls in shared fatal handler
- At WIN1.10 `0002:3C71`, the original opcode is `9A` (FAR CALL), its operand starts at `0002:3C72`, and NE chained relocation targets **{win[0]['relocation_targets']}**.
- At WIN1.10 `0002:3C7A`, the original opcode is `9A`, its operand starts at `0002:3C7B`, and relocation targets **{win[1]['relocation_targets']}**.
- These names are module+ordinal references only. Resolving ordinal 137 to a stable named API requires reliable version-specific import documentation; runtime effects remain untested.
- 73C5 -> 3C3D is a branch into shared fatal handling; 3C38 sets DS=SS first while 73C5 does not. This impacts the precondition of subsequent `3C80` lookups.

## Boundary and verification policy
- `PASS09_NEAR_CALL_TARGET_CANDIDATES.csv` contains raw `E8` patterns that could transfer to `73D4`, `73D9`, or `73C5`; they are **not validated** by a CFG-rooted decode.
- `PASS09_TARGETED_ASM.csv` is linear disassembly bounded by previously identified code regions, not a substitute for all-entry CFG reconstruction.
- The long-term goal to enumerate all indirect calls and all writes cannot be certified by linear scans alone.
- Certified, fully analyzed functions: **0**. No runtime test was performed.

## Next technical block
  1. Validate caller sites against reachable instruction boundaries and track stack state/DS per caller.
  2. Recover earlier Windows runtime's equivalent append routine by control-flow/byte signature matching rather than assuming the same segment offset.
  3. Confirm data source of `DS:0A96` after Win16 loader relocation and any poststartup reinitialization.
  4. Expand shared handler 3C3D into independent, path-sensitive per-entry function/region reports.
'''
(reports/'PASS09_DS_A96_WRITERS_AND_FAR_IMPORTS.md').write_text(report)
with (reports/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS09: mapped WIN110 NE FAR operands 3C72->KERNEL ordinal 137, 3C7B->KERNEL ordinal 1; direct DS:A96 byte-pattern inventory across 5 Windows versions; original on-disk pointer evidence retained; complete certified functions 0.\n')
archive=shutil.make_archive(str(root/'N3D_FUNCTION_RESEARCH_PASS09_20261103'),'zip',root,dst.name)
with zipfile.ZipFile(archive) as a:assert a.testzip() is None
print(json.dumps({'zip':archive,'size':Path(archive).stat().st_size,'direct_A96_total':len(refs),'WIN110_direct':[r for r in refs if r['version']=='WIN_1_10'],'WIN110_far':win,'call_candidates_WIN110':[r for r in callrows if r['version']=='WIN_1_10'],'num_files':len(list(dst.rglob('*')))},indent=2))