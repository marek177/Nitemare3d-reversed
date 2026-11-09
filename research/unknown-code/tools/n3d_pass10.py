from pathlib import Path
import zipfile,shutil,csv,json,struct,subprocess,re,hashlib
root=Path('/mnt/data'); src=root/'N3D_FUNCTION_RESEARCH_PASS09'; dst=root/'N3D_FUNCTION_RESEARCH_PASS10';shutil.copytree(src,dst,dirs_exist_ok=True)
md=dst/'MASTER_DATABASE';reports=dst/'REPORTS'; reports.mkdir(exist_ok=True)
arch=zipfile.ZipFile(root/'files/dosbox-n3d(20261103-105917).zip')
vers={'WIN_1_0':'nite3/windows/NITE3W -10.EXE','WIN_1_3':'nite3/windows/NITE3W - 13.EXE','WIN_1_6':'nite3/windows/NITE3W - 16.EXE','WIN_1_8':'nite3/windows/NITE3W - 18.EXE','WIN_1_10':'nite3/windows/nite3w - 110.exe'}
def seg2(v):
 b=arch.read(vers[v]); ne=struct.unpack_from('<I',b,0x3c)[0]; shift=struct.unpack_from('<H',b,ne+0x32)[0]; s=struct.unpack_from('<H',b,ne+0x22)[0];off,length,*_=struct.unpack_from('<HHHH',b,ne+s+8)
 return b[off<<shift:(off<<shift)+(length or 65536)]
segments={v:seg2(v) for v in vers}
# Root each instruction stream at an independently visible control-flow branch target instead of arbitrary sliding windows.
regions={
 'ERROR_CALLER':(0x3ccd,0x3cf4,0x3ce5),
 'READ_FILE_CALLER':(0x57d6,0x5801,0x57e2),
 'READ_CHAR_CALLER':(0x5876,0x589a,0x587e),
 'WRITE_FILE_CALLER':(0x59dd,0x5a17,0x59ee),
 'WRITE_CHAR_CALLER':(0x5a4e,0x5a85,0x5a62),
 'ERROR_STUB':(0x73c5,0x73cb,0x73c5),
 'ERROR_COMMON':(0x3c3d,0x3c80,0x3c3d)
}
# objdump on specified start decodes sequential instruction boundaries; this is not a global CFG proof.
def decode(b,start,end):
 p=root/'_n3d_pass10_seg.bin';p.write_bytes(b)
 output=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(p)],text=True)
 parsed=[]
 for l in output.splitlines():
  match=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)$',l)
  if match:parsed.append((int(match[1],16),match[2].strip(),match[3].strip()))
 return parsed
rows=[];blockrows=[];diff=[]
for v,b in segments.items():
 for name,(start,end,site) in regions.items():
  listing=decode(b,start,end)
  boundary=next((x for x in listing if x[0]==site),None)
  displacement=struct.unpack_from('<h',b,site+1)[0] if b[site]==0xe8 else None
  target=(site+3+displacement)&0xffff if displacement is not None else None
  rows.append(dict(version=v,region=name,start=f'{start:04X}',end=f'{end:04X}',site=f'{site:04X}',bytes=b[site:site+3].hex(' '),decoded_boundary=bool(boundary),decoded_instruction=boundary[2] if boundary else '',target=f'{target:04X}' if target is not None else '',target_is_73c5=target==0x73c5,confidence='LOCALLY_ALIGNED_FROM_SELECTED_START_NOT_GLOBAL_REACHABILITY'))
  if v=='WIN_1_10':
   for addr,by,asm in listing:blockrows.append(dict(region=name,address=f'0002:{addr:04X}',bytes=by,asm=asm))
for name,(start,end,site) in regions.items():
 b1=segments['WIN_1_8'];b2=segments['WIN_1_10']
 diff.append(dict(region=name,start=f'{start:04X}',end=f'{end:04X}',bytes_identical=b1[start:end]==b2[start:end],sha256_win18=hashlib.sha256(b1[start:end]).hexdigest(),sha256_win110=hashlib.sha256(b2[start:end]).hexdigest(),different_byte_positions=sum(x!=y for x,y in zip(b1[start:end],b2[start:end]))))
# Control-flow conditions immediately preceding each call and successor paths are manually readable in the stored per-region ASM files.
def csvwrite(name,rr):
 with (md/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
csvwrite('PASS10_CALLSITE_ALIGNMENT.csv',rows)
csvwrite('PASS10_WIN110_TARGETED_ASM.csv',blockrows)
csvwrite('PASS10_WIN18_WIN110_REGION_DIFF.csv',diff)
for name,(lo,hi,_) in regions.items():
 for v in ('WIN_1_8','WIN_1_10'):
  lines=decode(segments[v],lo,hi)
  (reports/f'PASS10_{v}_{name}.asm.txt').write_text('\n'.join(f'{a:04X} {bs:<20} {ins}' for a,bs,ins in lines)+'\n')
summary={'pass':10,'regions':len(regions),'versions':list(vers),'call_sites_verified_locally':sum(r['decoded_boundary'] and r['target_is_73c5'] for r in rows if r['region'] not in ('ERROR_STUB','ERROR_COMMON')),'win110_sites':[r for r in rows if r['version']=='WIN_1_10' and r['region'] not in ('ERROR_STUB','ERROR_COMMON')],'diff':diff,'certified_functions':0,'scope_limitation':'Locally rooted decode; no complete program-wide CFG, no exhaustive xrefs.'}
(md/'PASS10_SUMMARY.json').write_text(json.dumps(summary,indent=2))
(reports/'PASS10_ERROR20_CALLER_VALIDATION.md').write_text('''# PASS 10 — validation of five error-code-20 call sites

## Grounded observations from original Win16 segment 2 bytes

All five site opcodes are `E8 rel16` and their destination is `0002:73C5` in the five examined binaries. Local disassembly rooted at surrounding instruction boundaries identifies each E8 as an aligned instruction. This is stronger evidence than the previous raw-byte pattern scan, but these caller roots have **not** been independently proven to be globally reachable.

| Call | Local predecessor | Local successor |
|---|---|---|
| `3CE5` | `3CE1 MOV BX,[0870]` | `3CE8 POP DI` |
| `57E2` | `57E0 JB 57E7` | `57E5 JMP 57FB` |
| `587E` | `587C JB 5883` | `5881 JMP 5897` |
| `59EE` | `59EC JB 59F3` | `59F1 JMP 5A07` |
| `5A62` | `5A60 JB 5A67` | `5A65 JMP 5A7B` |

At `73C5`: `MOV AX,0014h; JMP 3C3Dh`. It does not preserve a local return path. The common handler beginning at `3C3D` pushes AX, invokes `39A8`, `3CB7`, and `3C80`, and proceeds toward error handling and termination. Each caller's return address may remain on the stack when entering this handler: calling convention and side effects must be traced before treating any following instruction as reachable on that error branch.

### Important precision
- The E8 byte pattern is shared across Windows 1.0, 1.3, 1.6, 1.8 and 1.10 at these same offsets. That is not a statement about globally identical surrounding functions.
- The 5 callers appear in runtime library I/O or reporting logic. **Not proven** to represent Nitemare3D gameplay routines.
- The common error handler is a shared tail target and cannot be packaged as an independent ordinary returning callee without more analysis.
- `73CB` contains byte 00 before a likely alternate prologue at `73CC`; do not decode `73CB` blindly as an instruction boundary.
- Full DS and SS live-state and dynamic OS error behavior remain unresolved.
- Fully certified functions: **zero**. No runtime tests performed in PASS10.

Next: start CFG from independently confirmed export/relocation entrypoints; prove each caller-root's provenance, trace 3C3D termination, validate old-version data layouts by semantic signature rather than absolute offsets.
''')
with (reports/'ALL_VERSIONS_PROGRESS.md').open('a') as f:f.write('\nPASS10: local alignment of five error-code-20 near-call sites across five Win16 binaries; region diff Windows 1.8 versus 1.10; common fatal tail; certified complete functions 0.\n')
archive=shutil.make_archive(str(root/'N3D_FUNCTION_RESEARCH_PASS10_20261103'),'zip',root,dst.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(root/'_n3d_pass10_seg.bin').unlink(missing_ok=True)
print(json.dumps({'zip':archive,'size':Path(archive).stat().st_size,'summary':summary},indent=2))