"""python audit_replay_direction_index.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
for i in Decoder(16,b[0xc838:0xc869],ip=0x68):
    assert not i.is_invalid;raw=b[0xc7d0+i.ip:0xc7d0+i.next_ip];assert lookup[(0xc7d,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0xc7d,ip=i.ip,image_offset=0xc7d0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x96
refs=[r for r in old if '0x4158' in r['operands']]
for r in refs:
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw) and i.memory_displacement==0x4158
writers=[r for r in refs if r['operands'].startswith('word ptr [0x4158],')];assert len(writers)==1 and writers[0]['cs']==0xc7d and writers[0]['ip']==0x96
out.mkdir(parents=True,exist_ok=True);cases=0;valid=[];normal_valid=[]
with (out/'cases.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['load_segment','input_signed','normalized_signed','index_signed','normalized_0_359','index_0_7'])
    for load,values in [(0,range(-32768,32768)),(0x1000,[-32768,-405,-404,-361,-360,-1,0,359,360,719,720,32767])]:
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xc7d;ds=load+0x2771
        for value in values:
            expected=value+360 if value<0 else value
            if expected>=360:expected-=360
            q=abs(expected)//45*(-1 if expected<0 else 1)
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5ff00,struct.pack('<HHH',0x4000,cs,value&65535));u.emu_start(cs*16+0x68,cs*16+0x99,count=100)
            actual,index=struct.unpack('<hh',u.mem_read(ds*16+0x4156,4));assert (actual,index)==(expected,q),(load,value,actual,index,expected,q)
            assert u.reg_read(UC_X86_REG_SP)==0xfefa and u.reg_read(UC_X86_REG_BP)==0xfefe and u.reg_read(UC_X86_REG_DS)==ds
            nvalid=0<=actual<360;ivalid=0<=index<8;w.writerow([load,value,actual,index,nvalid,ivalid]);cases+=1
            if load==0:
                if nvalid:normal_valid.append(value)
                if ivalid:valid.append(value)
assert normal_valid==list(range(-360,720)) and valid==list(range(-404,720))
for name,rows in [('instructions',instructions),('inventory_direct_refs',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),scope='seeded prefix only; stop before 0099; no trig callee or natural callers',prefix_start=0xc838,prefix_end_exclusive=0xc869,prefix_bytes=49,prefix_instructions=len(instructions),cases=cases,exhaustive_load_zero_inputs=65536,second_load_boundary_cases=12,failures=0,normalization_valid_input_interval_inclusive=[-360,719],index_valid_input_interval_inclusive=[-404,719],inventory_direct_refs=len(refs),inventory_direct_word_writers=len(writers),global_alias_writer_inventory_closed=False,original_runtime_tests=0,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
