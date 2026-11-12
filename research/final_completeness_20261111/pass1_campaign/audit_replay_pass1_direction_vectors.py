"""python audit_replay_pass1_direction_vectors.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);old=json.loads(inventory.read_text())
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
fields=[]
for name,a in [('guard_direction_component_a',0x2823e),('guard_direction_component_b',0x28246)]:
    fields.append(dict(name=name,start=a,end_exclusive=a+8,length=8,type='BYTE_array_8_nominal_slots_shift_left_3_to_record26',status='PARTIAL',range_sha256=sha(b[a:a+8])))
save('data_fields',fields);rows=[];contexts=[]
for r in old:
    if (r['cs']==0x4c7 and (0x1660<=r['ip']<0x1692 or 0x16e4<=r['ip']<0x16f5)) or (r['cs']==0xaea and 0xa60<=r['ip']<0xa94):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid
        row=dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i));contexts.append(row)
        if r['cs']==0x4c7 and r['ip']<0x1692:rows.append(row)
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows)==50
save('guard_direction_components',rows);save('caller_contexts',contexts);cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x4c7
    selectors=range(65536) if load==0 else list(range(12))+[0x7fff,0x8000,0xfff8,0xffff]
    for selector in selectors:
        seed=bytes(range(26));expected=bytearray(seed);expected[0x11]=(selector&3)*2
        expected[0x13]=(u.mem_read(ds*16+((selector+0xb2e)&65535),1)[0]<<3)&255
        expected[0x14]=(u.mem_read(ds*16+((selector+0xb36)&65535),1)[0]<<3)&255
        u.mem_write(0x60100,seed)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_DI,0x8765),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHHHH',0x6000,cs,0x100,0x6000,selector));u.emu_start(cs*16+0x1660,cs*16+0x6000,count=100)
        assert bytes(u.mem_read(0x60100,26))==bytes(expected)
        assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_ES)==0x6000 and u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DI)==0x8765
        cases.append(dict(load=load,selector=selector,result_11=expected[0x11],result_13=expected[0x13],result_14=expected[0x14],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=16,fields=2,functions=[dict(name='guard_direction_components',start=0x62d0,end_exclusive=0x6302,instruction_bytes=50,instructions=len(rows))],cases=len(cases),failures=0,scope='native leaf all 65536 selectors at load0 and 16 at load1000; caller domain unproven; outside nominal 8 slots reads seeded DGROUP bytes not natural runtime',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
