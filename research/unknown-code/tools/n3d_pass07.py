from pathlib import Path
import zipfile, struct, hashlib, csv, json, shutil
root=Path('/mnt/data'); src=root/'N3D_FUNCTION_RESEARCH_PASS06'; dest=root/'N3D_FUNCTION_RESEARCH_PASS07'
shutil.copytree(src,dest,dirs_exist_ok=True)
z=zipfile.ZipFile(root/'files'/'dosbox-n3d(20261103-105917).zip')
files={'WIN_1_0':'nite3/windows/NITE3W -10.EXE','WIN_1_3':'nite3/windows/NITE3W - 13.EXE','WIN_1_6':'nite3/windows/NITE3W - 16.EXE','WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
u16=lambda b,p:struct.unpack_from('<H',b,p)[0]
summary=[];entries=[];codes=[];sdata={}
for v,fn in files.items():
 b=z.read(fn);ne=struct.unpack_from('<I',b,0x3c)[0];shift=u16(b,ne+0x32);segtab=u16(b,ne+0x22);autodata=u16(b,ne+0x0e)
 def seg(n):
  sector,size,flags,alloc=struct.unpack_from('<HHHH',b,ne+segtab+8*(n-1));return b[(sector<<shift):(sector<<shift)+(size or 65536)] if sector else b''
 ds=seg(autodata);code=seg(2);sdata[v]=ds
 anchor=ds.find(b'R6000\r\n');base=anchor-2
 assert anchor>0 and u16(ds,base)==0
 mov=code[0x3c91:0x3c94];cmp=code[0x73e0:0x73e4]
 assert mov[0]==0xbe and cmp[:2]==b'\x81\xfb'
 base_operand=u16(mov,1); limit=u16(cmp,2)
 assert base_operand==base,(v,hex(base_operand),hex(base))
 pos=base; termination=None
 for i in range(100):
  keyoff=pos;key=u16(ds,pos);pos+=2
  if key==0xffff: termination=keyoff;break
  end=ds.find(b'\0',pos)
  assert end!=-1
  raw=ds[pos:end];entries.append(dict(version=v,index=i,key=f'{key:04X}',key_offset=f'{keyoff:04X}',text_offset=f'{pos:04X}',text_utf8=raw.decode('latin1'),text_hex=raw.hex(),length=len(raw)))
  pos=end+1
 assert termination is not None
 summary.append(dict(version=v,sha256=hashlib.sha256(b).hexdigest(),autodata_segment=autodata,table_start=f'{base:04X}',asm_table_operand=f'{base_operand:04X}',table_terminator=f'{termination:04X}',table_entries=i,table_bytes=pos-base,bound_limit=f'{limit:04X}',bound_delta_from_18=limit-0x4684,table_delta_from_18=base-0x223e,segment10_length=len(ds),segment2_code=f'{code[0x3c80:0x3cb7].hex()}'))
 codes.append(dict(version=v,position='0002:3C91',bytes=mov.hex(' '),asm=f'MOV SI,{base_operand:04X}h',data_target=f'DS:{base_operand:04X}',data_target_resolved=f'NE_AUTO_DATA_SEGMENT_{autodata}'))
 codes.append(dict(version=v,position='0002:73E0',bytes=cmp.hex(' '),asm=f'CMP BX,{limit:04X}h',data_target=f'DS:{limit:04X}',data_target_resolved=f'NE_AUTO_DATA_SEGMENT_{autodata} (bounds constant)'))
# Check actual underlying table equivalence by removing positional bytes
reference=[(r['key'],r['text_hex']) for r in entries if r['version']=='WIN_1_10']
for v in files:
 assert [(r['key'],r['text_hex']) for r in entries if r['version']==v]==reference, f'changed runtime message table {v}'
# Relocation provenance: list original source site records near shared path calls
fix=[]
with (src/'MASTER_DATABASE'/'NE_FIXUP_EXPANDED_SITES.csv').open(newline='') as f:
 rows=list(csv.DictReader(f))
for r in rows:
 if r.get('version')=='WIN_1_10' and str(r.get('segment'))=='2':
  try: off=int(r.get('site_offset',''),16)
  except ValueError: continue
  if 0x3c3d<=off<=0x3c80:fix.append(r)
def writecsv(path,records):
 if not records:return
 keys=list(dict.fromkeys(k for r in records for k in r))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(records)
md=dest/'MASTER_DATABASE';writecsv(md/'PASS07_RUNTIME_TABLE_ENTRIES.csv',entries);writecsv(md/'PASS07_CROSS_VERSION_DATA_BOUNDS.csv',summary);writecsv(md/'PASS07_ASM_CONSTANT_SITES.csv',codes);writecsv(md/'PASS07_SHARED_PATH_FIXUPS.csv',fix)
(dest/'ALGORITHMS'/'PASS07_RUNTIME_LOOKUP_TABLE.json').write_text(json.dumps({'autodata_segment':10,'record_count':len(reference),'semantics':'16-bit key then zero-terminated byte string; terminated by FFFFh','records':[{'key':k,'message_hex':txt} for k,txt in reference]},indent=2))
notes=[]
for x in summary:
 notes.append(f"| {x['version']} | {x['autodata_segment']} | `{x['table_start']}` | `{x['table_terminator']}` | {x['table_entries']} | `{x['bound_limit']}` |")
shared='\n'.join(' | '.join(f'{k}={val}' for k,val in r.items()) for r in fix[:12])
report=f'''# PASS 07 — Win16 DS base, runtime-error lookup and cross-version shifts

## Provenance
Source: `dosbox-n3d(20261103-105917).zip`, five original NE binaries. SHA-256 per version in `PASS07_CROSS_VERSION_DATA_BOUNDS.csv`. Analysis directly reads NE header at `MZ[0x3C]`, auto-data segment index at NE+0x0E, segment table and data bytes; does not assume CS=DS. The script aborts if opcode, table anchor, or parsed results mismatch. No runtime or emulator run was performed.

## Result A: reconstructed DS mapping and table semantics
Every tested Windows NE file has automatic data segment index **10**. This is the loader's automatic data segment, but every actual caller's DS state is not yet fully path-proven. The bytes at data-segment index 10 have the runtime-message lookup table which is actually referenced by `0002:3C91 MOV SI,...`, and consumed at `0002:3C94 LODSW`. Its first entry is key `0000h`, followed by ASCII `R6000\\r\\n- stack overflow\\r\\n` and NUL. The list is terminated with key `FFFFh`.

| Version | NE auto-data segment | Table start offset | Terminator offset | Entries | Pointer-bound constant |
|---|---:|---|---|---:|---|
{chr(10).join(notes)}

**All five versions have 12 identical ordered (WORD key, byte string) pairs**, verified bytewise including the raw error-message bytes, rather than inferred from matching mnemonics. All variants have an FFFFh terminator. Thus the Win1.8 → Win1.10 `MOV SI,223Eh` → `MOV SI,2242h` change is a data-offset relocation, **not evidence of changed lookup behavior**. That claim is limited to this table and the analyzed `LODSW` path, not the full program.

## Result B: boundary constant and hypothesis
The direct `0002:73E0 CMP BX,imm16` values are `45C2h, 45C2h, 467Ah, 4684h, 4688h` in chronological version order. Version 1.8 → 1.10 shifts by four, matching table offset's +4; earlier 1.6 → 1.8 changes only the boundary by +10, not the table. This disproves the stronger assumption that these constants must always move together or that one four-byte insertion uniquely explains both. The helper at `73D9` contains a four-byte stride update to `DS:[0A96]`. Do **not** call `4688h` a concrete array end until the buffer's initialization and writer graph are recovered. Notably `DS:4688h` is within the file-backed auto-data segment but comprises zero-initialized bytes in the original EXE, so static content alone cannot identify runtime writes.

## Result C: shared fatal/error path and call-sites
`0002:73C5` jumps to `0002:3C3D`, a shared transfer path; `0002:3C3D` has constructed far calls (`PUSH CS; CALL near`), an error message lookup, and external FAR calls at 3C71 and 3C7A. These are relocated NE operands; raw `FFFF:0000` cannot be interpreted directly as a target. All raw fixup evidence near this range is in `PASS07_SHARED_PATH_FIXUPS.csv` (if any record matches the exact segment/offset fields). Full per-path stack balance and terminal behavior remain unverified.

## Corrected bounded pseudocode (structural, not original Ghidra)
```c
// DS must address the segment-10 auto-data image and DF must be zero.
// This expresses the normal well-formed-table path, not all wrap cases.
uint16_t lookup_runtime_message(uint16_t wanted) {{
  uint16_t cursor = TABLE_BASE;   // per-version literal in report
  for (;;) {{
    uint16_t key = read16(DS, cursor); cursor += 2;   // 0002:3C94
    if (key == wanted) return cursor;                // 0002:3C95..3C97
    if (key == 0xffff) return 0;                     // 0002:3C99..3C9B, 3CA9
    cursor = scan_zero_terminated(DS, cursor);       // 0002:3C9D..3CA7
  }}
}}
```

## Confidence and remaining tasks
- **Verified**: NE auto-data segment index, source bytes of data segment, exact table locations, table identity across all 5 releases, embedded immediates, key/string structure, 12+terminator per version.
- **Supported but conditional**: function's lookup semantics assuming documented CPU string-instruction preconditions and a valid loader-set DS.
- **Unknown**: path-specific DS and DF state of every caller, malformed table handling, complete stack convention in mixed far/near transfer, external fixup targets, array/buffer behind `DS:[0A96]`, DOS equivalent.
- **Runtime verified functions**: 0. **Statically complete certified functions**: 0.
'''
(dest/'REPORTS'/'PASS07_DS_RUNTIME_TABLE_FIVE_VERSION.md').write_text(report)
with (dest/'REPORTS'/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS07: NE auto-data segment 10 verified for all five Win16 binaries; runtime error lookup table 12 identical records + FFFF terminator across versions; per-version base and 73E0 bound immediate inventoried. Static only; 0 certified functions.\n')
shutil.make_archive(str(root/'N3D_FUNCTION_RESEARCH_PASS07_20261103'),'zip',root,dest.name)
print(json.dumps({'versions':summary,'records':len(entries),'matching_fixups':len(fix),'package':str(root/'N3D_FUNCTION_RESEARCH_PASS07_20261103.zip')},indent=2))