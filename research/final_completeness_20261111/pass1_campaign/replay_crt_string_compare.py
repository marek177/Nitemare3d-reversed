"""python replay_crt_string_compare.py IMAGE UNICORN_DIR OUT"""
import hashlib,json,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
def folded(s):return bytes(v+32 if 65<=v<=90 else v for v in s.split(b'\0')[0])
pairs=[(b'',b''),(b'A',b'a'),(b'Z',b'z'),(b'abc',b'ab'),(b'ab',b'abc'),(b'A',b'B'),(b'b',b'A'),(b'@',b'`'),(b'[',b'{'),(b'333',b'333'),(b'01532',b'01533'),(b'080993',b'080993'),(b'372535',b'372534'),(b'\xff',b'\x80'),(b'\x80',b'\xff'),(b'a\0ignored',b'A\0tail')]
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee
    for first,second in pairs:
        x,y=folded(first),folded(second);expected=(x>y)-(x<y)
        u.mem_write(0x60033,first+b'\0');u.mem_write(0x61053,second+b'\0')
        u.mem_write(0x5ff00,b''.join(v.to_bytes(2,'little') for v in [0x4000,cs,0x33,0x6000,0x53,0x6100]))
        for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
        u.emu_start(load*16+0x15b48,cs*16+0x4000,count=1000)
        actual=u.reg_read(UC_X86_REG_AX);actual=actual if actual<32768 else actual-65536
        assert actual==expected
        for r,v in [(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678)]:assert u.reg_read(r)==v
        assert bytes(u.mem_read(0x60033,len(first)+1))==first+b'\0' and bytes(u.mem_read(0x61053,len(second)+1))==second+b'\0'
        cases.append(dict(load_segment=load,first_hex=first.hex(),second_hex=second.hex(),expected=expected,actual=actual,abi_checks_passed=True))
out.mkdir(parents=True,exist_ok=True);(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(cases=len(cases),failures=0,requires_df_zero=True,scope='seeded original instructions; DF=0; no natural reachability proof',original_runtime_tests=0,deep_verified=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
