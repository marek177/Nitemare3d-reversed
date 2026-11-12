"""python audit_replay_pass1_crt_null_text.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert b[0x29a33:0x29a3b]==b'(null)\x06\0'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);functions=[]
out.mkdir(parents=True,exist_ok=True)
for name,a,e in [('crt_fetch_word',0x1a53,0x1a5b),('crt_fetch_dword',0x1a5b,0x1a67),('crt_fetch_string_pointer',0x1a67,0x1a84),('string_branch',0x17dd,0x180b)]:
    rows=[]
    for i in Decoder(16,b[0x11ee0+a:0x11ee0+e],ip=a):
        assert not i.is_invalid;raw=b[0x11ee0+i.ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,i.ip)]['bytes']==raw.hex()
        rows.append(dict(cs=0x11ee,ip=i.ip,image_offset=0x11ee0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    if name!='string_branch':functions.append(dict(name=name,start=0x11ee0+a,end_exclusive=0x11ee0+e,instruction_bytes=e-a,instructions=len(rows)))
fields=[]
for name,a,e,t in [('crt_counted_null_text',0x29a33,0x29a39,'ASCII_counted_text_6_not_NUL_terminated'),('crt_counted_null_length',0x29a39,0x29a3b,'WORD_text_length_initial_6')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    variants=[('near_null',False,0,0),('near_nonnull',False,ds,0x9000),('far_null',True,0,0),('far_zero_segment',True,0,0x9000),('far_zero_offset',True,ds,0),('far_other_segment',True,0x7000,0x100)]
    for name,far,seg,off in variants:
        null=seg==0 and off==0
        for limit in (0,1,3,6,65535):
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_BP,0xff00),(UC_X86_REG_SP,0xfe00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5ff0a,struct.pack('<H',0x8000));u.mem_write(0x5fefc,struct.pack('<H',0x20 if far else 0));u.mem_write(0x5fef4,struct.pack('<H',limit))
            u.mem_write(ds*16+0x8000,struct.pack('<HH',off,seg))
            if not null:u.mem_write(seg*16+off,b'ABCDE\0')
            u.emu_start(cs*16+0x17dd,cs*16+0x19c8,count=200)
            length=6 if null else min(5,limit);expected_seg=ds if null else seg;expected_off=0x2323 if null else off
            assert (u.reg_read(UC_X86_REG_ES),u.reg_read(UC_X86_REG_DI),u.reg_read(UC_X86_REG_CX))==(expected_seg,expected_off,length)
            assert struct.unpack('<H',u.mem_read(0x5ff0a,2))[0]==0x8000+(4 if far else 2) and u.reg_read(UC_X86_REG_SP)==0xfe00
            cases.append(dict(load_segment=load,variant=name,far_mode=far,input_segment=seg,input_offset=off,limit=limit,is_null=null,result_segment=expected_seg,result_offset=expected_off,result_length=length,passed=True))
for name,rows in [('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=8,cases=len(cases),failures=0,scope='original string branch and argument-fetch helpers; DF=0; stop at 19C8 before output/padding; no mocked callees',full_formatter_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
