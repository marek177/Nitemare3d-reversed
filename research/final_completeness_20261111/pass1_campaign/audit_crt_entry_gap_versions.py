"""python audit_crt_entry_gap_versions.py VERSION_MANIFEST CANONICAL_IMAGE UNPACK_PROOF OUT"""
import csv,json,hashlib,struct,sys
from pathlib import Path
manifest,image,proof,out=map(Path,sys.argv[1:]);sha=lambda x:hashlib.sha256(x).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
canonical=json.loads(proof.read_text());source=Path(canonical['source']).read_bytes();assert sha(source)==canonical['source_sha256'] and canonical['image_sha256']==sha(b)
needle=bytes.fromhex('b430cd213c02730533c00650cb');rows=[]
for r in csv.DictReader(manifest.open(encoding='utf-8-sig')):
    p=Path(r['path']);v=p.read_bytes();assert sha(v)==r['image_sha256'];u=p.parent/'unpack.json';meta=json.loads(u.read_text());entry=meta['original_cs']*16+meta['original_ip'];assert v[entry:entry+len(needle)]==needle
    assert v.find(needle)==entry and v.find(needle,entry+1)<0
    gap_start=entry-17;assert v[gap_start:entry]==b'\0'*17 and v[gap_start-1]==0xcb
    reconstructed=p.parent/'reconstructed.exe';exe=reconstructed.read_bytes();header=struct.unpack_from('<H',exe,8)[0]*16;ip,cs=struct.unpack_from('<HH',exe,0x14);assert (cs,ip)==(meta['original_cs'],meta['original_ip']);assert exe[header:]==v
    if r['label']=='20':assert v==b and entry==canonical['output_entry_cs']*16+canonical['output_entry_ip'] and gap_start==0x11ee7
    rows.append(dict(label=r['label'],image_path=str(p),image_sha256=sha(v),unpack_metadata_sha256=sha(u.read_bytes()),reconstructed_exe_sha256=sha(exe),entry_cs=cs,entry_ip=ip,entry_image=entry,gap_start=gap_start,gap_end_exclusive=entry,gap_length=17,gap_sha256=sha(v[gap_start:entry]),previous_byte_image=gap_start-1,previous_byte_hex='cb',entry_signature_sha256=sha(v[entry:entry+len(needle)]),classification='CLASSIFIED ONLY_zero_gap_candidate_not_proven_padding',scope='version metadata/reconstructed EXE crosscheck, not independently rerun original unpack for every version'))
out.mkdir(parents=True,exist_ok=True)
with (out/'versions.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(canonical_source_sha256=sha(source),canonical_image_sha256=sha(b),version_manifest_sha256=sha(manifest.read_bytes()),versions=len(rows),unique_image_sha256=len({r['image_sha256'] for r in rows}),zero_gap_length_each=17,canonical_gap_start=0x11ee7,canonical_gap_end_exclusive=0x11ef8,status_changes=0,runtime_tests=0,new_deep_verified_bytes=0,scope='exact CRT entry signature and 17B zero gap across eight DOS labels; references/writers and complete padding semantics not closed')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
