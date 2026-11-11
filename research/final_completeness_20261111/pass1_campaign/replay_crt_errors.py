"""Controlled original-instruction replay, not DOSBox-X or natural runtime.
Usage: python replay_crt_errors.py IMAGE UNICORN_DIR OUT
"""
import hashlib,json,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b)
table=b[0x29870:0x29884]
cases=[]
for major in (2,3):
    inputs=list(range(256))+[(ah<<8)|al for ah in range(1,256) for al in (0,255)]
    for ax in inputs:
        al,ah=ax&255,ax>>8
        if ah: expected=ah if ah<128 else ah-256
        else:
            idx=5 if major>=3 and al in (32,33) else min(al,19)
            expected=table[idx] if table[idx]<128 else table[idx]-256
        for reg,value in [(UC_X86_REG_CS,0x11ee),(UC_X86_REG_DS,0x2771),(UC_X86_REG_SS,0x3000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_AX,ax),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
        u.mem_write(0x3ff00,(0x4000).to_bytes(2,'little'));u.mem_write(0x29831,bytes([major]));u.mem_write(0x29828,b'\x55\xaa');u.mem_write(0x29836,b'\x00\x7e')
        u.emu_start(0x124aa,0x15ee0,count=40)
        actual=int.from_bytes(u.mem_read(0x29828,2),'little',signed=True)
        native=bytes(u.mem_read(0x29836,2))
        assert actual==expected and native==bytes([al,0x7e]) and u.reg_read(UC_X86_REG_SP)==0xff02,(major,ax,actual,expected)
        cases.append(dict(major=major,input_ax=ax,expected_error=expected,actual_error=actual,native_error_low=al,native_error_high_preserved=True))
out.mkdir(parents=True,exist_ok=True)
(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(cases=len(cases),failures=0,scope='all AL for AH=0 and all nonzero AH at AL 0/255; major 2/3; seeded default DS; no DOS interrupts',original_runtime_tests=0,deep_verified=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
