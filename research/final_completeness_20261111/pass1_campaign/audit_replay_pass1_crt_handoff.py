"""python audit_replay_pass1_crt_handoff.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
spec=[('crt_exec_active_word',0x29859,2,'mutable_WORD_initial_zero_set1_before_exec_clear0_after', [0x354e,0x3593]),('crt_exec_mode_byte',0x2985b,1,'BYTE_initial_zero_compared_to2',[0x34f5,0x3581]),('crt_termination_ch_flag',0x29861,1,'mutable_BYTE_initial_zero_written_CH_consumed_in_stdio_cleanup',[0x20c,0x826]),('crt_startup_saved_return',0x2986c,4,'mutable_FAR16_pointer_initial_zero_POP_IP_CS_then_far_JMP',[0x30e,0x312,0x498]),('crt_hook_magic',0x29c44,2,'WORD_initial_zero_gate_equal_D6D6',[0x109,0x564]),('crt_near_io_hook',0x29c46,2,'mutable_NEAR16_pointer_initial_00E4_default_RET',[0x56c,0x1e3f,0x1f1c,0x350e]),('crt_near_error_hook',0x29c48,2,'mutable_NEAR16_pointer_initial_00E4_default_RET',[0x113])]
fields=[];anchors=[]
for n,a,size,t,ips in spec:
    if a in (0x29c46,0x29c48):assert b[a:a+2]==b'\xe4\0'
    else:assert not any(b[a:a+size])
    fields.append(dict(name=n,start=a,end_exclusive=a+size,length=size,type=t,status='PARTIAL',range_sha256=sha(b[a:a+size])));anchors.extend(ips)
assert sum(f['length'] for f in fields)==14 and b[0x11fc4]==0xc3
contexts=[]
for r in old:
    if r['cs']==0x11ee and any(ip-4<=r['ip']<=ip+8 for ip in anchors):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
for ip,expected in [(0x30e,'8f065c21'),(0x312,'8f065e21'),(0x498,'ff2e5c21'),(0xe4,'c3')]:assert lookup[(0x11ee,ip)]['bytes']==expected
save('data_fields',fields);save('instruction_contexts',contexts);cases=[];rel=list(csv.DictReader((image.parent/'relocations.csv').open()))
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def code(uc,a,size,data):
        if a==cs*16+0xe4:state['hooks']+=1
    def intr(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x40 and uc.reg_read(UC_X86_REG_BX)==2
        count=uc.reg_read(UC_X86_REG_CX);state['writes'].append(bytes(uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_DX),count)));uc.reg_write(UC_X86_REG_AX,count);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
    def regs(ss):
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
    for offset,segment in itertools.product((0,1,65534,65535),(0x1000,0x6000,0x9000)):
        state.clear();state.update(hooks=0,writes=[]);regs(ds);u.mem_write(ds*16+0xff00,struct.pack('<HH',offset,segment));u.emu_start(cs*16+0x30e,cs*16+0x316,count=10)
        assert bytes(u.mem_read(ds*16+0x215c,4))==struct.pack('<HH',offset,segment) and u.reg_read(UC_X86_REG_SP)==0xff04
        u.emu_start(cs*16+0x498,segment*16+offset,count=10);assert u.reg_read(UC_X86_REG_CS)==segment and u.reg_read(UC_X86_REG_IP)==offset and u.reg_read(UC_X86_REG_SP)==0xff04
        cases.append(dict(load=load,kind='staged_handoff',value=str((offset,segment)),hooks=0,passed=True))
    for magic,key in itertools.product((0,0xd6d6),(0,1,0xfc,0xff,4)):
        state.clear();state.update(hooks=0,writes=[]);u.mem_write(ds*16+0x2534,struct.pack('<HH',magic,0xe4));regs(0x5000);u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,key));u.emu_start(cs*16+0x545,cs*16+0x6000,count=10000)
        assert state['hooks']==int(magic==0xd6d6 and key!=4) and len(state['writes'])==int(key!=4) and u.reg_read(UC_X86_REG_SP)==0xff06
        cases.append(dict(load=load,kind='native_default_near_hook',value=str((magic,key)),hooks=state['hooks'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=14,fields=len(fields),cases=len(cases),failures=0,scope='staged original two POP prefix then original far-JMP; middle startup omitted; native default RET hook via original error printer/lookup, DOS AH40 modeled; other scalar writers static',whole_startup_closed=False,exec_OS_path_closed=False,natural_hook_writers_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
