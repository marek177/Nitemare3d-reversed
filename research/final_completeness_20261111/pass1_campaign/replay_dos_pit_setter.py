"""Controlled original-instruction replay; synthetic state and recorded OUT only.
Usage: python replay_dos_pit_setter.py IMAGE UNICORN_DIRECTORY OUT_DIR
"""
import hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;cases=[]
for gate,value in [(0,1),(0,0x952),(0,0xffff),(1,0),(0,0),(2,0x952)]:
    uc=Uc(UC_ARCH_X86,UC_MODE_16);uc.mem_map(0,0x100000);uc.mem_write(0,b)
    initial={UC_X86_REG_AX:value,UC_X86_REG_BX:0x1234,UC_X86_REG_CX:0x2345,UC_X86_REG_DX:0x3456,UC_X86_REG_SI:0x4567,UC_X86_REG_DI:0x5678,UC_X86_REG_BP:0x6789,UC_X86_REG_DS:0x2222,UC_X86_REG_ES:0x3333}
    for reg,v in initial.items():uc.reg_write(reg,v)
    uc.reg_write(UC_X86_REG_CS,0x15bf);uc.reg_write(UC_X86_REG_SS,0x7000);uc.reg_write(UC_X86_REG_SP,0x8000)
    uc.mem_write(0x78000,struct.pack('<H',0x6000));uc.mem_write(base+0x201e,struct.pack('<H',gate));uc.mem_write(base+0x2db4,bytes.fromhex('feca feca'))
    ports=[];interrupts=[];visited=[];returned=[]
    def code(u,address,size,user):
        visited.append(address)
        if address==base+0x6000:returned.append(True);u.emu_stop()
    def intr(u,n,user):interrupts.append(n);u.emu_stop()
    def port(u,p,size,v,user):ports.append(dict(port=p,size=size,value=v))
    uc.hook_add(UC_HOOK_CODE,code);uc.hook_add(UC_HOOK_INTR,intr);uc.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT)
    uc.emu_start(base+0x466a,base+0x6001,count=1000)
    words=struct.unpack('<HH',bytes(uc.mem_read(base+0x2db4,4)));preserved=all(uc.reg_read(r)==v for r,v in initial.items())
    if gate==1:
        assert returned and not interrupts and not ports and words==(0xcafe,0xcafe) and preserved
    elif value==0:
        assert interrupts==[0] and not returned and not ports and words==(0xcafe,0xcafe)
    else:
        assert returned and not interrupts and words==(65535//value,)*2 and preserved
        assert ports==[dict(port=0x43,size=1,value=0x34),dict(port=0x40,size=1,value=value&255),dict(port=0x40,size=1,value=value>>8)]
    if returned:assert uc.reg_read(UC_X86_REG_SP)==0x8002
    cases.append(dict(gate=gate,input_ax=value,returned=bool(returned),interrupts=interrupts,port_writes=ports,ratio_words=list(words),input_registers_preserved=preserved,instruction_starts=visited,scope='controlled Unicorn execution; synthetic inputs; no DOS or hardware execution'))
out.mkdir(parents=True,exist_ok=True)
r=dict(image_sha256=h,unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob("*.dll")],unique_executed_helper_instruction_starts=len({a for c in cases for a in c["instruction_starts"] if base+0x466a<=a<base+0x469f}),cases=cases,controlled_replay_cases=len(cases),runtime_tests=0,natural_reachability_proven=False,new_deep_verified_bytes=0)
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(controlled_replay_cases=len(cases),assertions_passed=True,runtime_tests=0),indent=2))
