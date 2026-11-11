"""python audit_replay_angle_lookup.py IMAGE DECODER_DIR UNICORN_DIR OUT"""
import bisect,csv,hashlib,json,struct,sys
from pathlib import Path
image,decoder,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
T=list(struct.unpack_from('<91h',b,0x29064));assert T==sorted(T) and T[-2:]==[32767,32767]
for p,h in {0xd09f:'660fbf4606',0xd0a4:'66c1e00a',0xd0c3:'66f7f9',0xd0e1:'c746fe5419',0xd0f7:'83ff5b',0xd0fa:'7ced',0xd108:'81c7b400',0xd112:'b86801'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];p=0xd096;fmt=Formatter(FormatterSyntax.INTEL)
for ins in Decoder(16,b[p:0xd12b],ip=p-0xc7d0):
    assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0xc7d,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
assert p==0xd12b
values=[-32768,-32767,-1024,-100,-33,-32,-31,-1,0,1,31,32,33,100,1024,32766,32767]
pairs={(n,d) for n in values for d in values}
for v in T:
    for n in {v,-v}:
        for d in [-1024,1024]:pairs.add((n,d))
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xc7d
    for n,d in sorted(pairs):
        ratio=None if d==0 else abs(n*1024)//abs(d)
        index=90 if d==0 else bisect.bisect_left(T,ratio)
        expected=index+180 if n<0 and d>=0 else 360-index if n<0 else 180-index if d>0 else index
        for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
        u.mem_write(0x5ff00,b''.join((v&65535).to_bytes(2,'little') for v in [0x4000,cs,n,d]))
        u.emu_start(load*16+0xd096,cs*16+0x4000,count=2000)
        actual=u.reg_read(UC_X86_REG_AX);assert actual==expected,(n,d,actual,expected,index)
        for r,v in [(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_DS,load+0x2771)]:assert u.reg_read(r)==v
        cases.append(dict(load_segment=load,numerator=n,denominator=d,absolute_ratio=ratio,lookup_index=index,expected_angle=expected,actual_angle=actual,abi_checks_passed=True))
    assert bytes(u.mem_read(load*16+0x29064,182))==b[0x29064:0x2911a]
out.mkdir(parents=True,exist_ok=True)
with (out/'instructions.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(image_sha256=sha(b),function_start=0xd096,function_end_exclusive=0xd12b,instruction_bytes=149,instructions=len(rows),cases=len(cases),failures=0,unique_input_pairs=len(pairs),index_91_cases=sum(r['lookup_index']==91 for r in cases),zero_vector_result=90,scope='seeded original instructions, selected grid and all table thresholds; no natural caller proof',original_runtime_tests=0,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
