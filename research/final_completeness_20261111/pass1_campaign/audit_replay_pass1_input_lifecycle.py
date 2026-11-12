"""python audit_replay_pass1_input_lifecycle.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('input_irq9_lifecycle',0x134,0x18c),('input_aux_lifecycle',0x18c,0x1d0)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x6b00+ip:0x6b00+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0x6b00+ip:0x6b00+i.next_ip];assert lookup[(0x6b0,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x6b0,ip=ip,image_offset=0x6b00+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0x6b00+start,end_exclusive=0x6b00+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[dict(name=n,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])) for n,a,e,t in [('input_irq9_active',0x2824e,0x2824f,'mutable_BYTE_initial_zero'),('input_aux_initialized',0x2824f,0x28250,'mutable_BYTE_initial_zero'),('input_last_key_word',0x28250,0x28252,'mutable_WORD_initial_zero_compared_and_written_SI')]]
assert not any(b[0x2824e:0x28252]);save('data_fields',fields)
context=[]
for r in old:
    if r['cs']==0x6b0 and 0x330<=r['ip']<0x386:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);context.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('key_history_context',context);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x6b0;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x158c2:'get_vector',load*16+0x158d4:'set_vector',load*16+0x831e:'aux_init',load*16+0x8338:'aux_close'}
    for a in targets:u.mem_write(a,b'\xcb')
    def hook(uc,a,size,data):
        if a not in targets:return
        n=targets[a];sp=uc.reg_read(UC_X86_REG_SP)
        if n=='get_vector':
            assert struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0]==9;state['trace'].append(n);uc.reg_write(UC_X86_REG_AX,0x2222);uc.reg_write(UC_X86_REG_DX,0x1111)
        elif n=='set_vector':state['trace'].append((n,)+struct.unpack('<3H',uc.mem_read(0x50000+sp+4,6)))
        else:
            state['trace'].append(n)
            if n=='aux_init':uc.reg_write(UC_X86_REG_AX,state['probe'])
    u.hook_add(UC_HOOK_CODE,hook)
    for entry in (0x134,0x18c):
        for flag,mode,probe in itertools.product(range(256),(0,1,2,65535),(1,) if entry==0x134 else (0,1,65535)):
            u.mem_write(ds*16+0xb3e,bytes([flag,flag]));u.mem_write(ds*16+0x414c,b'\xa5');u.mem_write(ds*16+0x3f52,struct.pack('<HH',0x4444,0x3333));state.clear();state.update(trace=[],probe=probe)
            expected=[];newflag=flag;present=0xa5;saved=(0x4444,0x3333)
            if entry==0x134:
                if mode==0 and flag==0:expected=['get_vector',('set_vector',9,0,load+0x6b0)];newflag=1;saved=(0x2222,0x1111)
                elif mode==1 and flag:expected=[('set_vector',9,0x4444,0x3333)];newflag=0
            else:
                if mode==0:
                    if flag==0:expected=['aux_init'];present=int(probe!=0)
                    newflag=1
                elif mode==1:expected=['aux_close'] if flag else [];present=0;newflag=0
            for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
            u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,mode));u.emu_start(cs*16+entry,cs*16+0x6000,count=500)
            off=0xb3e if entry==0x134 else 0xb3f
            assert bytes(u.mem_read(ds*16+off,1))==bytes([newflag]) and bytes(u.mem_read(ds*16+0x414c,1))==bytes([present]) and struct.unpack('<HH',u.mem_read(ds*16+0x3f52,4))==saved and state['trace']==expected,(entry,flag,mode,probe,state['trace'],expected)
            assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
            cases.append(dict(load=load,entry=entry,old_flag=flag,mode=mode,probe=probe,new_flag=newflag,present=present,trace=str(expected),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=4,cases=len(cases),failures=0,scope='original two lifecycle control bodies; get/set vector and aux init/close mocked; key WORD consumer static only; no real interrupt installation or device',original_isr_closed=False,natural_input_lifecycle_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
