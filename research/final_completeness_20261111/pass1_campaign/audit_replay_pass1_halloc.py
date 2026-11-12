"""python audit_replay_pass1_halloc.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x2a16];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x2a16<=ip<0x2aea;i=Decoder(16,b[0x11ee0+ip:0x149ca],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('crt_zeroed_far_allocate',rows);assert not any(b[0x29b7a:0x29b7e]);save('data_fields',[dict(name='crt_zeroed_allocation_retry_callback',start=0x29b7a,end_exclusive=0x29b7e,length=4,type='mutable_FAR16_pointer_initial_zero_retry_callback',status='PARTIAL',range_sha256=sha(b[0x29b7a:0x29b7e]))])
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;state={};callback=0x70000;u.mem_write(callback,b'\xcb')
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def code(uc,a,size,data):
        if a!=callback:return
        sp=uc.reg_read(UC_X86_REG_SP);args=struct.unpack('<HHH',uc.mem_read(0x50000+sp+4,6));assert args==(state['size'],state['count']&65535,state['count']>>16)
        state['callbacks']+=1;assert state['returns'];uc.reg_write(UC_X86_REG_AX,state['returns'].pop(0))
    def interrupt(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48;state['os_calls']+=1;flags=uc.reg_read(UC_X86_REG_EFLAGS)
        if state['success']:
            assert uc.reg_read(UC_X86_REG_BX)==state['paragraphs'];uc.reg_write(UC_X86_REG_AX,0x6000);uc.reg_write(UC_X86_REG_EFLAGS,flags&~1)
        else:uc.reg_write(UC_X86_REG_AX,8);uc.reg_write(UC_X86_REG_EFLAGS,flags|1)
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt)
    def run(count,size,policy,success=False):
        returns=[] if policy=='null' else [0] if policy=='zero' else [1,0] if policy=='retry1' else [65535,0]
        u.mem_write(ds*16+0x246a,struct.pack('<HH',0,0 if policy=='null' else 0x7000));u.mem_write(ds*16+0x20f6,bytes(4));product=(count*size)&0xffffffff;paragraphs=(product+15)//16
        if success:u.mem_write(0x60000,bytes([0xa5])*(paragraphs*16+2))
        state.clear();state.update(count=count,size=size,returns=list(returns),callbacks=0,os_calls=0,success=success,paragraphs=paragraphs)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,0x402)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHIH',0x6000,cs,count,size));u.emu_start(cs*16+0x2a16,cs*16+0x6000,count=200000)
        result=u.reg_read(UC_X86_REG_DX)*65536+u.reg_read(UC_X86_REG_AX)
        if success:
            assert result==0x60000000 and state['os_calls']==1 and state['callbacks']==0 and bytes(u.mem_read(0x60000,paragraphs*16+2))==bytes(paragraphs*16)+b'\xa5\xa5'
            assert struct.unpack('<H',u.mem_read(ds*16+0x20f6,2))[0]==0x6000+paragraphs-1
        else:assert result==0 and state['callbacks']==len(returns) and not state['returns']
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        cases.append(dict(load=load,count=count,size=size,policy=policy,success=success,os_calls=state['os_calls'],callbacks=state['callbacks'],result=result,passed=True))
    for count,size,policy in itertools.product((0,1,15,16,4096,65535,65536,65537,0xffffffff),(0,1,2,3,16,256,65535),('null','zero','retry1','retryFFFF')):run(count,size,policy)
    for count,size in itertools.product((1,2,15,16,17,255),(1,2,3,16)):run(count,size,'null',True)
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='crt_zeroed_far_allocate',start=0x148f6,end_exclusive=0x149ca,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],typed_bytes=4,cases=len(cases),failures=0,scope='original complete control/zero-fill body; DOS AH48 modeled; retry callback RETF/hook; success limited to products below 65536; larger requests failure paths only',large_success_domain_closed=False,real_DOS_allocation_closed=False,retry_callback_body_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
