"""python audit_replay_pass1_trig.py IMAGE DECODER_DIR UNICORN_DIR OUT"""
import csv,hashlib,json,math,struct,sys
from pathlib import Path
image,decoder,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
S=list(struct.unpack_from('<91h',b,0x28ef8));C=list(struct.unpack_from('<91h',b,0x28fae));assert S[0]==C[90]==0 and S[90]==C[0]==1024
errors=[max(abs(v[i]-1024*f(math.radians(i))) for i in range(91)) for v,f in [(S,math.sin),(C,math.cos)]];assert max(errors)<1.000001
fields=[dict(name=name,start=a,end_exclusive=a+182,length=182,type='signed_WORD[91]_scale_1024_quarter_wave',status='PARTIAL',range_sha256=sha(b[a:a+182])) for name,a in [('sin_quarter_wave',0x28ef8),('cos_quarter_wave',0x28fae)]]
entries=[dict(table=name,angle=i,image_offset=a+2*i,value=v[i]) for name,a,v in [('sin',0x28ef8,S),('cos',0x28fae,C)] for i in range(91)]
for p,h in {0xcfc2:'8b84e817',0xcfd0:'be5019',0xcfe8:'8b848016',0xcfee:'beb81a',0xd00e:'8b849e18',0xd01c:'be061a',0xd036:'8b843617',0xd03c:'be6e1b'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);allrows=[]
for name,a,e in [('sin',0xcfb2,0xcffe),('cos',0xcffe,0xd04a)]:
    rows=[];p=a
    for ins in Decoder(16,b[a:e],ip=a-0xc7d0):
        assert not ins.is_invalid;rows.append(dict(function=name,image_offset=p,cs=0xc7d,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
    assert p==e
    with (out/(name+'_instructions.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    allrows+=rows
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xc7d
    for name,start in [('sin',0xcfb2),('cos',0xcffe)]:
        for angle in range(360):
            if name=='sin':expected=S[angle] if angle<90 else S[180-angle] if angle<180 else -S[angle-180] if angle<270 else -S[360-angle]
            else:expected=C[angle] if angle<90 else -C[180-angle] if angle<180 else -C[angle-180] if angle<270 else C[360-angle]
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5ff00,b''.join(v.to_bytes(2,'little') for v in [0x4000,cs,angle]))
            u.emu_start(load*16+start,cs*16+0x4000,count=100)
            actual=u.reg_read(UC_X86_REG_AX);actual=actual if actual<32768 else actual-65536;assert actual==expected,(name,angle,actual,expected)
            for r,v in [(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DS,load+0x2771)]:assert u.reg_read(r)==v
            cases.append(dict(function=name,load_segment=load,angle=angle,expected=expected,actual=actual,abi_checks_passed=True))
    assert bytes(u.mem_read(load*16+0x28ef8,364))==b[0x28ef8:0x29064]
for name,rows in [('data_fields',fields),('entries',entries),('instructions',allrows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(image_sha256=sha(b),typed_bytes=364,functions=2,instructions=len(allrows),instruction_bytes=152,cases=len(cases),failures=0,max_deviation_from_real_scaled_sin_cos=errors,scope='seeded original instructions; angles 0..359, two load bases; no natural reachability proof',original_runtime_tests=0,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
