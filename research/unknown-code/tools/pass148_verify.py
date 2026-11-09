import re,hashlib,json,pathlib
ROOT=pathlib.Path('/mnt/data/pass148_src')
image=(ROOT/'dos20.bin').read_bytes()
results=[]
for f in sorted(ROOT.glob('*.asm')):
    count=bad=bytes_checked=0
    failures=[]
    for line in f.read_text().splitlines():
        m=re.match(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+([0-9a-f]+)\s+',line)
        if not m:continue
        segment,offset=int(m.group(1),16),int(m.group(2),16)
        raw=bytes.fromhex(m.group(3))
        at=16*segment+offset
        same=image[at:at+len(raw)]==raw
        count+=1;bytes_checked+=len(raw)
        if not same:bad+=1;failures.append(f'{segment:04X}:{offset:04X}')
    results.append(dict(function=f.stem,instructions=count,bytes=bytes_checked,mismatches=bad,failures=failures))
out={'pass':148,'image_sha256':hashlib.sha256(image).hexdigest(),'image_bytes':len(image),'verified':results,'total_instructions':sum(x['instructions'] for x in results),'total_bytes':sum(x['bytes'] for x in results),'total_mismatches':sum(x['mismatches'] for x in results),'findings':{'selection_load':'0D29:2204 on selected entry: skip init iff BP+6 nonzero and both IDs match globals 626C/626A; otherwise call 095A','cached_load':'0D29:2496 direct 1176 when DS:3CC4>=0 and decision != 1Bh; if DS:3CC4<0 calls 2204 with argument 1','conditional_load':'0D29:252E direct 1176 only when DS:3CD4==3, BP+8>=0, parsed ID matches 626C/626A; no local 095A','preservation':'0277:1176 saves and restores first eight bytes per 18-byte record; global proof of link validity requires separate runtime or alias analysis'}}
pathlib.Path('/mnt/data/N3D_PASS148_evidence.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
for x in results:print(x)
print('Totals:',out['total_instructions'],out['total_bytes'],out['total_mismatches'],out['image_sha256'])