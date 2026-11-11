"""python audit_crt_unloaded_hooks.py IMAGE INVENTORY DECODER_DIR OUT"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rows=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL)
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
refs=[];evidence=[];decoded={};slots=list(range(0x2346,0x2362,4))
for r in rows:
    p=r['image_offset'];raw=bytes.fromhex(r['bytes'])
    assert p==16*r['cs']+r['ip'] and b[p:p+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    decoded[(r['cs'],r['ip'])]=i
    item=dict(cs=r['cs'],ip=r['ip'],image_offset=p,bytes=raw.hex(),instruction=fmt.format(i))
    if i.memory_base==Register.NONE and i.memory_index==Register.NONE and i.memory_displacement in slots and '[' in fmt.format(i):
        refs.append(dict(slot=i.memory_displacement,segment_register=i.memory_segment,**item))
    if r['cs']==0x11ee and any(a<=r['ip']<e for a,e in [(0xf4,0x122),(0x29e,0x2c6),(0x545,0x57b)]):evidence.append(item)
assert b[0x121a0:0x121a6]==bytes.fromhex('b80200e92efe')
assert decoded[(0x11ee,0x2c3)].near_branch_target==0xf4
assert b[0x124d8]==0xcb # 11EE:05F8 default FAR-return hook
slot_rows=[]
for s in slots:
    p=0x27710+s;off,seg=struct.unpack_from('<HH',b,p)
    assert (off,seg)==(0x2c0,0x11ee) and rel[p+2]==seg
    slot_rows.append(dict(ds_offset=s,start=p,end_exclusive=p+4,initial_offset=off,initial_segment=seg,relocation_image=p+2,direct_memory_refs_in_inventory=sum(r['slot']==s for r in refs),range_sha256=sha(b[p:p+4])))
assert not [r for r in refs if r['slot']==0x2356]
p=0x29c86;records=[]
while True:
    code=struct.unpack_from('<H',b,p)[0];p+=2
    if code==0xffff:break
    end=b.index(0,p);records.append(dict(code=code,text_image=p,text=b[p:end].decode('ascii')));p=end+1
assert [r['text'] for r in records if r['code']==2]==['R6002\r\n- floating-point support not loaded\r\n']
out.mkdir(parents=True,exist_ok=True)
for name,data in [('slots',slot_rows),('direct_memory_refs',refs),('instructions',evidence),('error_records',records)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),verified_instruction_starts=len(rows),initial_slots=7,stub_start=0x121a0,stub_end_exclusive=0x121a6,stub_instructions=2,error_code=2,slot_2356_direct_refs=0,absence_scope='direct unindexed memory displacements in supplied inventory only',all_writers_closed=False,indirect_refs_closed=False,runtime_tests=0,new_deep_verified_bytes=0,pass1_map_changed=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
