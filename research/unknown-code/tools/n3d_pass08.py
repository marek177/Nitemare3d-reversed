from pathlib import Path
import csv,hashlib,json,re,shutil,subprocess,zipfile
root=Path('/mnt/data'); src=root/'N3D_FUNCTION_RESEARCH_PASS07'; dst=root/'N3D_FUNCTION_RESEARCH_PASS08'
shutil.copytree(src,dst,dirs_exist_ok=True)
md=dst/'MASTER_DATABASE'; rep=dst/'REPORTS'
versions=['WIN_1_8','WIN_1_10']
codepaths={v:src/'REFERENCES'/v/'NE_SEG_02.bin' for v in versions}
# Retrieve other originals from pass01 inventory ZIP; use exported 1.10 segment images locally.
for v in versions: assert codepaths[v].exists()
# Create a direct-reference inventory for DS:0A96, 0A94 across all available reference code segments.
refs=[]; details=[]; summary=[]
for v in versions:
 b=codepaths[v].read_bytes()
 for off in range(len(b)-3):
  for addr in (0x0a94,0x0a96):
   if b[off:off+2]!=bytes([addr&255,addr>>8]):continue
   pre=b[max(0,off-3):off]; post=b[off+2:off+5]
   # A possible disp16 operand is not guaranteed to be an actual instruction; retain uncertainty.
   refs.append(dict(version=v,segment=2,disp_offset=f'{off:04X}',address=f'DS:{addr:04X}',prefix_hex=pre.hex(' '),post_hex=post.hex(' '),classification='BYTE_PATTERN_ONLY_NOT_PROVEN_INSTRUCTION'))
 # precise target function 73D4 (entry 73D9 also possible), up to RETF
 for start,end,label in [(0x73d4,0x73fe,'pointer_append_73D4'),(0x3c38,0x3c7f,'shared_fatal_3C38')]:
  cmd=['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(codepaths[v])]
  output=subprocess.check_output(cmd,text=True)
  (rep/f'PASS08_{v}_{label}.asm.txt').write_text(output)
  for line in output.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)',line)
   if m:details.append(dict(version=v,region=label,address=f'0002:{int(m[1],16):04X}',raw=m[2].strip(),instruction=m[3].strip()))
 summary.append(dict(version=v,sha256_segment2=hashlib.sha256(b).hexdigest(),pointer_operand=f'{int.from_bytes(b[0x73de:0x73e0],"little"):04X}',end_limit=f'{int.from_bytes(b[0x73e2:0x73e4],"little"):04X}',append_code_hex=b[0x73d4:0x73fe].hex(),shared_code_hex=b[0x3c38:0x3c7f].hex(),reference_pattern_count=sum(r['version']==v for r in refs)))
def csvout(path,records):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
csvout(md/'PASS08_SEG2_DIRECT_ADDRESS_PATTERNS.csv',refs)
csvout(md/'PASS08_TARGETED_INSTRUCTIONS.csv',details)
csvout(md/'PASS08_VERSION_COMPARISON.csv',summary)
# Scan all segment images available for WIN110, not just segment 2.
allrefs=[]
for f in sorted((src/'REFERENCES'/'WIN_1_10').glob('NE_SEG_*.bin')):
 b=f.read_bytes(); seg=int(f.stem[-2:]);
 for target in (0x0a94,0x0a96,0x4688):
  x=target.to_bytes(2,'little');pos=0
  while True:
   pos=b.find(x,pos)
   if pos<0:break
   allrefs.append(dict(segment=seg,offset=f'{pos:04X}',pattern=f'{target:04X}',prior_bytes=b[max(pos-4,0):pos].hex(' '),following_bytes=b[pos+2:pos+6].hex(' '),certainty='RAW_MATCH_ONLY'))
   pos+=1
csvout(md/'PASS08_ALL_SEGMENT_PATTERN_AUDIT.csv',allrefs)
# Data segment extraction from pass07 reference file: report exact bytes at pointer and around limit
b=(src/'REFERENCES'/'WIN_1_10'/'NE_SEG_10.bin').read_bytes()
evidence={'source':'WIN_1_10 original file-backed NE segment 10','data_length':len(b),'initial_ds_0a94':b[0xa94:0xa96].hex(),'initial_ds_0a96':b[0xa96:0xa98].hex(),'limit_4688_byte_window':b[0x4680:0x4690].hex(' '),'limit_4688_inside_data':0x4688<len(b),'zero_at_4688':b[0x4688:0x4698]==bytes(16),'segment2_target_sha256':summary[1]['sha256_segment2']}
(md/'PASS08_DATA_SEGMENT_EVIDENCE.json').write_text(json.dumps(evidence,indent=2))
report=f'''# PASS 08 — DS:0A96 provenance / Win16 shared control-flow audit

## Verified byte evidence
- Reference Windows 1.10 segment 10 length: **{len(b)}**; on-disk `DS:0A94` = **{evidence['initial_ds_0a94']}**, `DS:0A96` = **{evidence['initial_ds_0a96']}**. The `0A94` value is zero, but `0A96` is **0846** (little-endian `4608h`), an on-disk initial cursor. Runtime code may still mutate it.
- Win1.10 `0002:73DC` reads `DS:0A96`, `73E0` compares `BX` to `4688h`, `73E6` adds four to `DS:0A96` conditionally, then writes two 16-bit words to `DS:[BX+2]` and `DS:[BX]`. The writes therefore operate at the **old value of BX**, before the pointer's increment. At `BX=4688h`, no append occurs.
- `73F6 JCXZ 73FA` and `73F8 XOR AX,AX` distinguish a nonzero input `AX` from zero (after `MOV CX,AX` at 73D9). This needs all incoming-call paths to establish return semantics. `73D9` has no standalone BP prologue; starting there requires a caller-established BP frame, whereas `73D4` builds one.
- The segment 10 bytes at offset `4688h` are all zero in a 16-byte window, not evidence of a used runtime array.
- `3C38` sets `DS=SS`, `AX=3`, then falls into `3C3D`. `73C5` sets `AX=0014h` and jumps **directly** to `3C3D` without the DS overwrite. Both entry contexts must remain separate. `3C71/3C7A` are unresolved loader-fixed FAR calls unless mapped with source fixup records.

## Explicit limitations
- The byte scans in `PASS08_*PATTERN*.csv` are **candidate byte positions only**; they are not certified instruction boundaries or definite accesses. To resolve complete producer/writer graph, every candidate must be cross-checked against reachability, prefixes, segment overrides, aliasing and indirect stores.
- In WIN1.6/1.8/1.10 the on-disk initial cursor and the limit differ by exactly `0080h`, suggesting **32 four-byte entries**. The initializer/limit relationship is statically demonstrated, but no runtime maximum occupancy or aliasing guarantee follows. Older WIN1.0/1.3 have `DS:0A96=7241h`, exceeding the compared bound; identical interpretation is NOT justified for those builds.
- Code at `73C5` is a tail-transfer into a shared block, **not a proven stand-alone returning function**.
- PASS08 includes no executed DOS game or Windows runtime emulator comparison; statically certified-complete functions remain zero.

## Hypotheses to falsify
1. `DS:0A96` appears to be an insertion cursor for 4-byte `(word,word)` records, initialized in the file-backed segment to 4608h (WIN1.10), 4604h (WIN1.8), 45FAh (WIN1.6); track every writer and determine if an alternative initialization occurs.
2. The `4688h` constant is an apparent exclusive insertion high-water mark, exactly 32 entries past the on-disk initial cursor. Prove all possible initialization paths and absence of pointer corruption before claiming a runtime capacity guarantee.
3. The shared error path may use different DS preconditions depending on predecessor; simulate the two distinct entries, including FAR call stack effects and return paths.

## Next required evidence
Cross-version full-data-segment layout differences, reachable writers to `DS:0A96` across all 1/2/3/4/7/10 segments, loader-resolved fixups for `3C71` and `3C7A`, and independently compiled or emulated path tests.
'''
(rep/'PASS08_DS_POINTER_AND_SHARED_FATAL.md').write_text(report)
with (rep/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS08: original WIN110 DS:0A94/0A96 file bytes both zero; 73D4 pair append writes at old cursor before +=4; 73D9 is alternate entry without prologue; source-safe byte-pattern scans completed, not proven code xrefs; certified functions=0.\n')

# Cross-version on-disk pointer-to-limit audit; older builds may use a different data layout.
import struct
z=zipfile.ZipFile(root/'files'/'dosbox-n3d(20261103-105917).zip')
names={'WIN_1_0':'nite3/windows/NITE3W -10.EXE','WIN_1_3':'nite3/windows/NITE3W - 13.EXE','WIN_1_6':'nite3/windows/NITE3W - 16.EXE','WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
rows=[]
for ver,fn in names.items():
 binary=z.read(fn);ne=struct.unpack_from('<I',binary,0x3c)[0];shift=struct.unpack_from('<H',binary,ne+0x32)[0];table=struct.unpack_from('<H',binary,ne+0x22)[0];autodata=struct.unpack_from('<H',binary,ne+0x0e)[0]
 sector,length,*_=struct.unpack_from('<HHHH',binary,ne+table+8*(autodata-1));ds=binary[sector<<shift:(sector<<shift)+(length or 65536)]
 cursor=struct.unpack_from('<H',ds,0xa96)[0]
 # Prior pass has verified 73e0 limit immediates in all five releases.
 limits={'WIN_1_0':0x45c2,'WIN_1_3':0x45c2,'WIN_1_6':0x467a,'WIN_1_8':0x4684,'WIN_1_10':0x4688}
 limit=limits[ver];delta=limit-cursor
 rows.append(dict(version=ver,initial_cursor=f'{cursor:04X}',limit=f'{limit:04X}',delta=delta,entries_if_4_byte_stride=(delta//4 if delta>=0 and delta%4==0 else ''),interpretation=('CONSISTENT_32_ENTRY_WINDOW' if delta==128 else 'NOT_PROVEN_SAME_LAYOUT')))
csvout(md/'PASS08_CROSS_VERSION_CURSOR_CAPACITY.csv',rows)
with (rep/'PASS08_DS_POINTER_AND_SHARED_FATAL.md').open('a') as f:
 f.write('\n## Cross-version capacity-window audit (on-disk values)\n')
 for r in rows:f.write(f"- {r['version']}: DS:0A96={r['initial_cursor']}h; limit={r['limit']}h; delta={r['delta']} bytes; classification={r['interpretation']}\n")
 f.write('WIN1.0 and WIN1.3 use a value 7241h at the same DS offset and do not fit this pointer/limit model; the older data layout must be recovered independently.\n')

shutil.make_archive(str(root/'N3D_FUNCTION_RESEARCH_PASS08_20261103'),'zip',root,dst.name)
with zipfile.ZipFile(root/'N3D_FUNCTION_RESEARCH_PASS08_20261103.zip') as z: assert z.testzip() is None
print(json.dumps({'summary':summary,'all_seg_matches':len(allrefs),'file_evidence':evidence,'output':str(root/'N3D_FUNCTION_RESEARCH_PASS08_20261103.zip')},indent=2))