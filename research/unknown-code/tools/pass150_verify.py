import zipfile, hashlib, json, re, struct
from pathlib import Path
ARCHIVE=Path('/mnt/data/files/N3D_FUNCTIONS_PASS100_NATIVE_OBJECT_EFFECTS_AND_RECORD_LOOKUP.zip')
OUT=Path('/mnt/data')
FIELDS=[0x2550+i*2 for i in range(15)]
result={'pass':150,'scope':'static original normalized DOS 1.8/2.0; no runtime','builds':{},'direct_references':{},'limitations':[]}
with zipfile.ZipFile(ARCHIVE) as z:
  for ver in ('DOS_1.8','DOS_2.0'):
    root=f'pass019/analysis/{ver}/'
    img=z.read(root+'normalized_image.bin')
    intro=z.read(root+'functions/0000_0000.asm').decode()
    m=re.search(r'^0000:0004\s+b8([0-9a-f]{4})\s+mov ax, 0x([0-9a-f]+)',intro,re.M|re.I)
    assert m and int.from_bytes(bytes.fromhex(m[1]),'little')==int(m[2],16)
    seg=int(m[2],16); base=seg*16+0x2550
    block=img[base:base+30]
    assert len(block)==30
    result['builds'][ver]={'sha256':hashlib.sha256(img).hexdigest(),'normalized_image_length':len(img),'segment_from_0000_0004':hex(seg),'linear_2550':hex(base),'linear_end_exclusive':hex(base+30),'initial_words':{f'{a:04X}':struct.unpack_from('<H',img,seg*16+a)[0] for a in FIELDS},'all_30_bytes_zero':block==b'\x00'*30,'initial_asm_verified':img[4:7]==bytes.fromhex('b8'+m[1])}
    refs=[]
    for name in z.namelist():
      if not (name.startswith(root+'functions/') and name.endswith('.asm')):continue
      for l in z.read(name).decode(errors='replace').splitlines():
        mm=re.match(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+([0-9a-f]+)\s+(.*)$',l)
        if not mm:continue
        s,o,h,op=mm.groups()
        addrs=[a for a in FIELDS if f'[0x{a:04x}]' in op.lower()]
        if not addrs:continue
        raw=int(s,16)*16+int(o,16)
        refs.append({'address':s+':'+o,'raw':hex(raw),'instruction':op,'fields':[f'{a:04X}' for a in addrs],'matches_image':img[raw:raw+len(h)//2]==bytes.fromhex(h)})
    result['direct_references'][ver]={'count':len(refs),'verified':sum(x['matches_image'] for x in refs),'all_match':all(x['matches_image'] for x in refs),'by_field':{f'{a:04X}':sum(f'{a:04X}' in r['fields'] for r in refs) for a in FIELDS},'references':refs}
result['limitations']=['The DS segment comes from a specific function whose DS initialization is visible; it is not a proof that every instruction uses that DS at runtime.','Zero bytes in a normalized/static image do not prove real runtime zeros after initialization or MZ relocation.','Direct references in candidate function dumps are not a complete provenance audit; unrecognized code, indirect writes, relocations, and bulk copy may modify the block.','Original DOS executables have not been executed or traced in this pass; no Win16 comparison performed.']
(OUT/'N3D_PASS150_evidence.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
with (OUT/'N3D_PASS150_segment_block_initialization.md').open('w',encoding='utf-8') as f:
 f.write('# Nitemare 3D — PASS150: segment-pointer block, static initialization audit\n\n')
 f.write('Source: PASS100 archive, normalized original DOS 1.8 and 2.0 images; **static-only analysis**.\n\n')
 f.write('## Newly verified finding\n\n')
 f.write('The analyzed `0000:0000` routine loads `DS=0x21F9` in DOS 1.8 and `DS=0x21FD` in DOS 2.0. In the normalized images, the complete 30-byte DS interval `0x2550..0x256D` consists of zero bytes in both builds. This describes *static-image contents*, not the post-initialization runtime memory.\n\n')
 f.write('| Build | DS in function | Image address of DS:2550 | All 30 bytes zero | SHA-256 |\n|---|---|---|---|---|\n')
 for ver,b in result['builds'].items():f.write(f'| {ver} | `{b["segment_from_0000_0004"]}` | `{b["linear_2550"]}` | {b["all_30_bytes_zero"]} | `{b["sha256"]}` |\n')
 f.write('\n## Direct-reference census in candidate ASM dumps\n\n')
 f.write('| Offset in DS | DOS 1.8 | DOS 2.0 |\n|---|---:|---:|\n')
 for a in FIELDS:
  s=f'{a:04X}'
  f.write(f'| `{s}` | {result["direct_references"]["DOS_1.8"]["by_field"][s]} | {result["direct_references"]["DOS_2.0"]["by_field"][s]} |\n')
 f.write('\nThis scan counts only explicit *absolute* memory operands `[...]` and does not establish absence of writes through pointer aliases or table-copy routines. The JSON contains each instruction, source address and exact-byte match against its normalized image.\n\n')
 f.write('## Interpretation and P0 follow-up\n\n')
 f.write('The segment variables are not usable as initialized pointers in the normalized static images. Their runtime values must be established by initialization, relocation or another write path. The next proof should capture DS, these 15 WORD values, and the last writer for each word before `0000:0212` and before `0277:1176` (LOAD). Reconstruct any indirect initialization and check Win16 separately. Avoid claiming that absence of an explicit store in 548 ASM candidates proves absence of a writer.\n\n')
 f.write('## Limits\n\n')
 for x in result['limitations']:f.write('- '+x+'\n')
print(json.dumps({'builds':result['builds'],'counts':{v:{'count':x['count'],'verified':x['verified']} for v,x in result['direct_references'].items()}},indent=2))