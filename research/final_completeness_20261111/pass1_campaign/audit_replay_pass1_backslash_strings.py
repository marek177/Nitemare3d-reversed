"""python audit_replay_pass1_backslash_strings.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
functions=[]
for name,start,end in [('crt_strcat_near',0x2326,0x2365),('crt_strcpy_near',0x2366,0x2398)]:
    todo=[start];decoded={};rows=[]
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for off in (0x2174,0x2176):
    a=0x27710+off;assert b[a:a+2]==b'\\\0';fields.append(dict(name='crt_backslash_string_'+hex(off),start=a,end_exclusive=a+2,length=2,type='NUL_ASCII_backslash_near_string',status='PARTIAL',range_sha256=sha(b[a:a+2])))
save('data_fields',fields)
context=[]
for r in old:
    if r['cs']==0x11ee and 0x658<=r['ip']<0x6ae:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);context.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('caller_context',context);cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for fn,spare,dpare,length,oldlen,pattern in itertools.product((0x2326,0x2366),(0,1),(0,1),(0,1,2,3,7,8,15,16,31,64),(0,1,2,15,31),(0,1,2)):
        src=0x4000+spare;dst=0x5000+dpare;source=bytes((65 if pattern==0 else 255 if pattern==1 else (i*73)%255+1) for i in range(length))+b'\0';prefix=b'p'*oldlen
        initial=bytearray(b'\xa5'*256);initial[:oldlen+1]=prefix+b'\0';expected=initial[:];offset=oldlen if fn==0x2326 else 0;expected[offset:offset+len(source)]=source
        u.mem_write(ds*16+src,source);u.mem_write(ds*16+dst,bytes(initial));u.mem_write(ds*16+dst-1,b'\x5a')
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_DI,0x8765),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHHH',0x6000,cs,dst,src));u.emu_start(cs*16+fn,cs*16+0x6000,count=2000)
        assert bytes(u.mem_read(ds*16+dst,256))==bytes(expected) and bytes(u.mem_read(ds*16+dst-1,1))==b'\x5a'
        assert u.reg_read(UC_X86_REG_AX)==dst and u.reg_read(UC_X86_REG_ES)==ds and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DI)==0x8765
        cases.append(dict(load=load,function=fn,source_parity=spare,destination_parity=dpare,length=length,old_destination_length=oldlen,pattern=pattern,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=4,fields=2,functions=functions,cases=len(cases),failures=0,scope='native near strcpy/strcat, DF0, terminated nonoverlapping DS strings and bounded supplied buffers; caller SS/DS relation static only, no original OS I/O',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
