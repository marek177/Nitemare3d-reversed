"""python audit_replay_pass1_file_info.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert b[0x2980c:0x2981a]==b'_C_FILE_INFO=\0' and not any(b[0x2981a:0x2981e])
save('data_fields',[dict(name=n,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])) for n,a,e,t in [('crt_file_info_prefix',0x2980c,0x2981a,'NUL_ASCII_environment_prefix_13_payload_bytes'),('crt_saved_interrupt0_vector',0x2981a,0x2981e,'mutable_FAR16_pointer_initial_zero_ES_BX_save_LDS_DX_restore')]])
contexts=[]
for r in old:
    if r['cs']==0x11ee and any(a<=r['ip']<e for a,e in [(0x122,0x131),(0x17f,0x1b3),(0x27f,0x28b),(0x4ef,0x519),(0x3352,0x339b)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('instruction_contexts',contexts)
prefix=[];todo=[0x194];decoded={}
while todo:
    ip=todo.pop()
    if ip==0x1b3 or ip in decoded:continue
    assert 0x194<=ip<0x1b3;i=Decoder(16,b[0x11ee0+ip:0x12093],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control!=FlowControl.UNCONDITIONAL_BRANCH:todo.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();prefix.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('decode_prefix',prefix);cases=[]
samples=[('one_byte',bytes([65+(v>>4),65+(v&15),0])) for v in range(256)]
samples.append(('all_byte_values',b''.join(bytes([65+(v>>4),65+(v&15)]) for v in range(256))+b'\0'))
samples += [('noncanonical',x) for x in (b'\0',b'@\0',b'A\0',b'A@\0',b'QA\0',b'AZ\0',b'ZA\0',b'zz\0')]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;dg=load+0x2771
    for kind,encoded in samples:
        expected=[];p=0
        while encoded[p]>=65:
            hi=(encoded[p]-65)<<4;p+=1
            if encoded[p]<65:break
            lo=encoded[p]-65;p+=1;expected.append((hi|lo)&255)
        u.mem_write(0x61000,encoded);u.mem_write(dg*16+0x212a,bytes([0xa5])*(len(expected)+2))
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,dg),(UC_X86_REG_ES,0x6000),(UC_X86_REG_SS,dg),(UC_X86_REG_SP,0xff00),(UC_X86_REG_DI,0x1000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.emu_start(cs*16+0x194,cs*16+0x1b3,count=10000)
        assert bytes(u.mem_read(dg*16+0x212a,len(expected)+2))==bytes(expected)+b'\xa5\xa5' and u.reg_read(UC_X86_REG_DS)==dg and u.reg_read(UC_X86_REG_ES)==dg and u.reg_read(UC_X86_REG_SP)==0xff00
        cases.append(dict(load=load,kind=kind,encoded_hex=encoded.hex(),decoded_hex=bytes(expected).hex(),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=18,fields=2,cases=len(cases),failures=0,prefix_instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in prefix),prefix_instructions=len(prefix),scope='original environment decode interior prefix; supplied encoded suffix, DF0; no actual environment scan/vector installation, encoder static only',full_inherited_file_info_closed=False,real_interrupt_restore_closed=False,output_bounds_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
