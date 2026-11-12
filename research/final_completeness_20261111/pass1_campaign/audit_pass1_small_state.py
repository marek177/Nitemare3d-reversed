"""python audit_pass1_small_state.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
spec=[(0x1ac,2,'cached_handle_WORD','0277:008D tests zero; 00A1 writes AX; 00BC/00CE pass handle'),(0x244,1,'one_time_init_BYTE','0277:018E tests; 0199 clears DL'),(0x678,1,'one_time_gate_BYTE','0277:176A tests; 1771 clears'),(0xad2,2,'episode_cache_key_WORD','04C7:0B7D compares episode; 0B83 stores; following class 41/42 lookup'),(0xc9c,2,'cyclic_selector_WORD','0768:04E2 indexes FAR pointer table; 04FB increments; 04FF signed bound; 0505 resets'),(0x1507,1,'toggle_BYTE','083D:1504 tests; 152E XOR 1'),(0x16f0,1,'lifecycle_latch_BYTE','0BCC:0084/00EC tests; 00E5 sets; 011B clears'),(0x17e6,1,'sound_priority_BYTE_unsigned','0C2B:040B/0426 unsigned compare; 0436 writes incoming priority AL'),(0x20de,2,'startup_NEAR_code_pointer','11EE:00EE assigns 01EB; 011C indirect near CALL; initial 01F2'),(0x2122,2,'startup_mode_WORD_low_BYTE_consumed','11EE:0316 loads WORD; AL compared with 2; high-byte role unresolved'),(0x2178,2,'CRT_counter_WORD','11EE:0B0B increments; higher-level purpose unresolved'),(0x2532,2,'optional_initializer_NEAR_pointer','11EE:00B3 loads CX; JCXZ skips; 00B9 CALL CX')]
rows=[];refs=[];old=json.loads(inventory.read_text())
for off,n,typ,note in spec:
    a=0x27710+off;matched=[]
    for r in old:
        raw=bytes.fromhex(r['bytes']);i=Decoder(16,raw,ip=r['ip']).decode()
        if not any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)):continue
        if i.memory_base!=Register.NONE or i.memory_index!=Register.NONE or i.memory_segment!=Register.DS:continue
        if i.memory_displacement!=off:continue
        assert b[r['image_offset']:r['image_offset']+len(raw)]==raw and i.len==len(raw) and not i.is_invalid
        matched.append(dict(field_offset=off,cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),memory_size=i.memory_size))
    assert matched,(off,typ)
    refs.extend(matched);rows.append(dict(name=typ.lower()+'_'+hex(off),start=a,end_exclusive=a+n,length=n,type=typ,status='PARTIAL',initial_hex=b[a:a+n].hex(),range_sha256=sha(b[a:a+n]),evidence=note,reference_count=len(matched)))
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('data_fields',rows);save('direct_references',refs)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=sum(r['length'] for r in rows),fields=len(rows),validated_direct_references=len(refs),runtime_tests=0,new_deep_verified_bytes=0,scope='direct absolute DS operands checked against canonical bytes; DS runtime provenance and complete functions remain open')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
