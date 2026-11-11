"""python replay_runtime_message_lookup.py IMAGE UNICORN_DIR RECORDS_CSV OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,dep,records,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
expected={int(r['code']):int(r['text_start'])-0x27710 for r in csv.DictReader(records.open())};assert len(expected)==7
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee
    for code in [0,1,2,3,9,252,255,4,8,254,65535]:
        for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
        u.mem_write(0x5ff00,b''.join(v.to_bytes(2,'little') for v in [0x4000,cs,code]))
        u.emu_start(load*16+0x123fa,cs*16+0x4000,count=2000)
        wanted=0x264e if code==65535 else expected.get(code,0);actual=u.reg_read(UC_X86_REG_AX);assert actual==wanted
        for r,v in [(UC_X86_REG_SP,0xff06),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_ES,load+0x2771)]:assert u.reg_read(r)==v
        cases.append(dict(load_segment=load,query=code,expected_near_offset=wanted,actual_near_offset=actual,abi_checks_passed=True))
out.mkdir(parents=True,exist_ok=True);(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(cases=len(cases),failures=0,scope='seeded original instruction lookup; DF=0; no DOS output or natural reachability test',original_runtime_tests=0,deep_verified=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
