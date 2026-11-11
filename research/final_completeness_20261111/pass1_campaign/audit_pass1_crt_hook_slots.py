"""python audit_pass1_crt_hook_slots.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields=[];refs=[];fmt=Formatter(FormatterSyntax.INTEL)
for offset in [0x2346,0x234a,0x234e,0x2352,0x235a,0x235e]:
    a=0x27710+offset;target,initial=struct.unpack_from('<HH',b,a);assert rel[a+2]==initial and initial==0x11ee and target==0x2c0
    selected=[r for r in old if r['mnemonic']=='lcall' and ('[0x%x]'%offset) in r['operands']]
    assert selected
    for r in selected:
        p=r['image_offset'];code=bytes.fromhex(r['bytes']);assert p==r['cs']*16+r['ip'] and b[p:p+len(code)]==code
        ins=Decoder(16,code,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(code)
        assert ins.memory_displacement==offset and ins.memory_base==Register.NONE and ins.memory_index==Register.NONE and ins.memory_segment==Register.DS
        refs.append(dict(global_image=a,global_ds_offset=offset,image_offset=p,cs=r['cs'],ip=r['ip'],bytes=code.hex(),instruction=fmt.format(ins),scope='indirect FAR CALL through direct DS slot; caller DS inherited'))
    fields.append(dict(name='crt_hook_'+hex(offset)[2:],start=a,end_exclusive=a+4,length=4,type='FAR16_code_pointer',initial_segment=initial,direct_consumers=len(selected),status='PARTIAL',range_sha256=sha(b[a:a+4])))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('hook_consumers',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),fields=len(fields),typed_bytes=24,direct_consumers=len(refs),status_promoted_bytes=12,all_writers_closed=False,caller_ds_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
