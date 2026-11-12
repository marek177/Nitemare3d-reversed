"""python audit_replay_pass1_crt_segment_mask.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for i in Decoder(16,b[0x13ce3:0x13cf4],ip=0x1e03):
    raw=b[0x11ee0+i.ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,i.ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=i.ip,image_offset=0x11ee0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert i.next_ip==0x1e14;save('crt_mask_transform',rows)
fields=[dict(name=n,start=a,end_exclusive=a+2,length=2,type=t,status='PARTIAL',range_sha256=sha(b[a:a+2])) for n,a,t in [('crt_io_flag_mask',0x2982a,'WORD_initial_zero_complement_AND_CX_bit80_transform'),('crt_psp_context_segment',0x2982e,'mutable_WORD_segment_initial_zero_used_for_environment_and_command_tail')]]
assert b[0x2982a:0x2982c]==b[0x2982e:0x29830]==bytes(2);save('data_fields',fields)
contexts=[]
for r in old:
    if r['cs']==0x11ee and any(a<=r['ip']<e for a,e in [(0x13b,0x17d),(0x31c,0x32a),(0x349,0x360),(0x49c,0x4b0),(0x2296,0x22ac),(0x1db0,0x1e14)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('instruction_contexts',contexts);cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    samples=[(m,0x80) for m in range(65536)] if load==0 else []
    samples += [(m,c) for m in (0,1,0x7f,0x80,0xff,0x7fff,0x8000,0xffff) for c in (0,1,0x7f,0x80,0xff,0x8000,0xffff)]
    if load==0:samples=[(m,c) for m,c in samples if c!=0x80]+[(m,0x80) for m in range(65536)]
    for mask,incoming in samples:
        u.mem_write(ds*16+0x211a,struct.pack('<H',mask))
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_CX,incoming),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<H',0x6000));u.emu_start(cs*16+0x1e03,cs*16+0x6000,count=100)
        expected=(~mask)&incoming&65535;result=0 if expected&0x80 else 1
        assert u.reg_read(UC_X86_REG_AX)==expected and u.reg_read(UC_X86_REG_CX)==result and u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,mask=mask,input_cx=incoming,output_ax=expected,output_cx=result,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='crt_mask_transform',start=0x13ce3,end_exclusive=0x13cf4,instruction_bytes=17,instructions=len(rows))],typed_bytes=4,cases=len(cases),failures=0,scope='original complete NEAR bitmask helper; seeded DS word and CX; PSP-context consumers static only, no DOS startup or memory calls',mask_writer_domain_closed=False,original_PSP_initialization_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
