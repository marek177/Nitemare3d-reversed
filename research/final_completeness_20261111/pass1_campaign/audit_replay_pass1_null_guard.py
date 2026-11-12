"""python audit_replay_pass1_null_guard.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,sys,struct,functools,operator
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x2ea];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x2ea<=ip<0x30e;i=Decoder(16,b[0x11ee0+ip:0x121ee],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('crt_null_assignment_guard',rows)
original=b[0x27710:0x27752];assert len(original)==66 and functools.reduce(operator.xor,original)==0x55
save('data_fields',[dict(name='crt_null_assignment_integrity_domain',start=0x27710,end_exclusive=0x27752,length=66,type='BYTE_array_66_XOR_integrity_domain_expected_55',status='PARTIAL',range_sha256=sha(original))])
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    u.mem_write(ds*16+0x2152,bytes(4));u.mem_write(ds*16+0x2534,bytes(2))
    def interrupt(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x40 and uc.reg_read(UC_X86_REG_BX)==2
        count=uc.reg_read(UC_X86_REG_CX);state['writes'].append(bytes(uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_DX),count)));uc.reg_write(UC_X86_REG_AX,count);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
    u.hook_add(UC_HOOK_INTR,interrupt)
    samples=[]
    if load==0:
        for pos in range(66):
            for value in range(256):
                data=bytearray(original);data[pos]=value;samples.append(('single_byte',pos,value,bytes(data)))
    else:
        for pos in range(66):
            for bit in range(8):
                data=bytearray(original);data[pos]^=1<<bit;samples.append(('single_bit',pos,bit,bytes(data)))
    for a,c in [(0,1),(0,65)]:
        data=bytearray(original);data[a]^=0x80;data[c]^=0x80;samples.append(('xor_cancel',a,c,bytes(data)))
    for kind,pos,value,data in samples:
        u.mem_write(ds*16,data);state['writes']=[];checksum=functools.reduce(operator.xor,data);dirty=checksum!=0x55
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+0x2ea,cs*16+0x6000,count=10000)
        expected=[b'\r\n',b'run-time error ',b'R6001\r\n- null pointer assignment\r\n'] if dirty else []
        assert state['writes']==expected and u.reg_read(UC_X86_REG_AX)==(1 if dirty else data[-1])
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        cases.append(dict(load=load,kind=kind,position=pos,value=value,xor=checksum,diagnostic=dirty,result_ax=u.reg_read(UC_X86_REG_AX),writes=len(state['writes']),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='crt_null_assignment_guard',start=0x121ca,end_exclusive=0x121ee,instruction_bytes=36,instructions=len(rows))],typed_bytes=66,cases=len(cases),failures=0,scope='original checksum guard, callback dispatcher, error printer and lookup executed; only DOS AH40 modeled; optional callbacks disabled; seeded domain bytes',natural_null_write_reproduced=False,error_termination_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
