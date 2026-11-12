"""python audit_replay_pass1_near_heap_flags.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
todo=[0x2270];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x2270<=ip<0x22c1;i=Decoder(16,b[0x11ee0+ip:0x141a1],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('near_heap_resize_or_accept',rows);save('cfg_edges',edges)
a=0x297f4;assert b[a:a+2]==b'\x05\0';save('data_fields',[dict(name='near_heap_control_flags_BYTE',start=a,end_exclusive=a+1,length=1,type='mutable_BYTE_initial_05_bits_0_and_2_consumed_adjacent_zero_untyped',status='PARTIAL',range_sha256=sha(b[a:a+1]))])
context=[]
for r in old:
    if r['cs']==0x11ee and (0x21e4<=r['ip']<0x21ef or 0x3cd3<=r['ip']<0x3ce7):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();context.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('root_and_flag_context',context);state={};cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee;psp=load+0x1000
    def intr(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x4a
        state['calls'].append((uc.reg_read(UC_X86_REG_ES),uc.reg_read(UC_X86_REG_BX)));uc.reg_write(UC_X86_REG_AX,8 if state['failure'] else 0x1234);f=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(f|1) if state['failure'] else (f&~1))
    u.hook_add(UC_HOOK_INTR,intr)
    for flags,desired,current,limit,failure,incoming_cf in itertools.product((0,1,4,5,255,0xff00,0xff05,65535),(0,1,15,16,17,0x1000,0x8000,65535),(0,1,0x1000,65535),(0,1,0xfff,65535),(0,1),(0,1)):
        fast=bool(flags&4) and ((desired-1)&65535)>((current-1)&65535) and limit>=((desired-1)&65535)
        paragraphs=desired>>4 or 0x1000;expect_calls=[] if fast else [(psp,(paragraphs+ds-psp)&65535)] if flags&4 else [(ds,paragraphs)]
        cf=0 if fast else failure;ax=desired if not cf else 8;dx=(desired-1)&65535 if fast or (not cf and flags&4) else desired;newlimit=dx if not fast and not cf and flags&4 else limit
        u.mem_write(ds*16+0x20e0,struct.pack('<HHHH',limit,ds,flags,current));u.mem_write(ds*16+0x211e,struct.pack('<H',psp));state.clear();state.update(calls=[],failure=failure)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_AX,desired),(UC_X86_REG_BX,0x20e2),(UC_X86_REG_CX,0xcafe),(UC_X86_REG_DI,0xbeef),(UC_X86_REG_EFLAGS,2|incoming_cf)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<H',0x6000));u.emu_start(cs*16+0x2270,cs*16+0x6000,count=150)
        assert state['calls']==expect_calls and u.reg_read(UC_X86_REG_AX)==ax and u.reg_read(UC_X86_REG_DX)==dx and u.reg_read(UC_X86_REG_EFLAGS)&1==cf,(flags,desired,current,limit,failure,state,ax,dx,cf)
        assert bytes(u.mem_read(ds*16+0x20e0,8))==struct.pack('<HHHH',newlimit,ds,flags,current)
        assert u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_BX)==0x20e2 and u.reg_read(UC_X86_REG_CX)==0xcafe and u.reg_read(UC_X86_REG_DI)==0xbeef and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,flags=flags,desired=desired,current=current,limit=limit,dos_failure=failure,incoming_cf=incoming_cf,fast_path=fast,resize_calls=len(expect_calls),final_cf=cf,new_limit=newlimit,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=1,fields=1,functions=[dict(name='near_heap_resize_or_accept',start=0x14150,end_exclusive=0x141a1,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,scope='native size accept/resize helper with root20E2; INT21/AH4A modeled preserving DX, no real DOS memory operation; bit0 branch static only',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
