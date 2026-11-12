"""python audit_replay_pass1_crt_error_output.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('crt_error_callback_dispatch',0x29e,0x2c0),('crt_error_output',0x545,0x57b)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end,(name,hex(ip),hex(start),hex(end));i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
save('data_fields',[dict(name='crt_error_callback',start=0x29862,end_exclusive=0x29866,length=4,type='mutable_FAR16_pointer_initial_zero_segment_zero_disables',status='PARTIAL',range_sha256=sha(b[0x29862:0x29866]))]);assert not any(b[0x29862:0x29866])
records={};p=0x29c86
while True:
    key=struct.unpack_from('<H',b,p)[0];p+=2
    if key==65535:break
    end=b.index(0,p);records[key]=b[p:end];p=end+1
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    callback=0x60000+0x100;intercept=cs*16+0x6000;u.mem_write(callback,b'\xcb');u.mem_write(intercept,b'\xc3')
    def code(uc,a,size,data):
        if a==callback:state['trace'].append('callback')
        if a==intercept:state['trace'].append('intercept')
    def interrupt(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x40
        count=uc.reg_read(UC_X86_REG_CX);raw=bytes(uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_DX),count));assert uc.reg_read(UC_X86_REG_BX)==2
        state['trace'].append('write:'+raw.hex());state['writes'].append(raw)
        uc.reg_write(UC_X86_REG_AX,5 if state['io_error'] else count);flags=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(flags|1) if state['io_error'] else (flags&~1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt)
    def run(entry,arg,segment,offset,interceptor,io_error):
        u.mem_write(ds*16+0x2152,struct.pack('<HH',offset,segment));u.mem_write(ds*16+0x2534,struct.pack('<HH',0xd6d6 if interceptor else 0,0x6000));state.clear();state.update(trace=[],writes=[],io_error=io_error)
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x4444),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_DI,0x9876),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x7000,cs,arg));u.emu_start(cs*16+entry,cs*16+0x7000,count=5000)
        keys=[0xfc,0xff] if entry==0x29e else [arg] if arg in records else [];expected=[]
        for index,k in enumerate(keys):
            if index==1 and segment:expected.append('callback')
            if interceptor:expected.append('intercept')
            expected.append('write:'+records[k].hex())
        assert state['trace']==expected and state['writes']==[records[k] for k in keys]
        assert u.reg_read(UC_X86_REG_SP)==(0xff04 if entry==0x29e else 0xff06) and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DI)==0x9876 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,entry=entry,arg=arg,callback_segment=segment,callback_offset=offset,interceptor=interceptor,io_error=io_error,trace=';'.join(expected),passed=True))
    for segment,offset,interceptor,io_error in itertools.product((0,0x6000),(0,0x100,65535),(0,1),(0,1)):
        if segment and offset!=0x100:continue
        run(0x29e,0,segment,offset,interceptor,io_error)
    for arg,interceptor,io_error in itertools.product(list(records)+[4,0x100],(0,1),(0,1)):run(0x545,arg,0,0,interceptor,io_error)
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=4,cases=len(cases),failures=0,scope='original dispatcher, printer and existing native lookup; DOS AH40 modeled, callback/interceptor RET stubs; DF=0 only',dos_io_verified=False,callback_body_closed=False,natural_abort_flow_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))


