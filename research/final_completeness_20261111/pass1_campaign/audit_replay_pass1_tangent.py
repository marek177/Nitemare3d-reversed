"""python audit_replay_pass1_tangent.py IMAGE DECODER_DIR UNICORN_DIR OUT"""
import csv,hashlib,json,math,struct,sys
from pathlib import Path
image,decoder,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
T=list(struct.unpack_from('<91h',b,0x29064));assert T[0]==0 and T[45]==1024 and T[89]==T[90]==32767
errors=[max(abs(T[i]-1024*math.tan(math.radians(i))) for i in range(89))];assert errors[0]<1.000001
fields=[dict(name='saturated_tangent_magnitude',start=0x29064,end_exclusive=0x2911a,length=182,type='signed_WORD[91]_scale_1024_saturated_quarter_wave',status='PARTIAL',range_sha256=sha(b[0x29064:0x2911a]))]
entries=[dict(table='tangent_magnitude',angle=i,image_offset=0x29064+2*i,value=T[i]) for i in range(91)]
for p,h in {0xd05a:'8b845419',0xd068:'bebc1a',0xd080:'8b84ec17',0xd086:'be241c',0xd091:'f7d8'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);allrows=[]
for name,a,e in [('tangent_magnitude',0xd04a,0xd096)]:
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
    for name,start in [('tangent_magnitude',0xd04a)]:
        for angle in range(360):
            expected=T[angle] if angle<90 else T[180-angle] if angle<180 else -T[angle-180] if angle<270 else -T[360-angle]
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5ff00,b''.join(v.to_bytes(2,'little') for v in [0x4000,cs,angle]))
            u.emu_start(load*16+start,cs*16+0x4000,count=100)
            actual=u.reg_read(UC_X86_REG_AX);actual=actual if actual<32768 else actual-65536;assert actual==expected,(name,angle,actual,expected)
            for r,v in [(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DS,load+0x2771)]:assert u.reg_read(r)==v
            cases.append(dict(function=name,load_segment=load,angle=angle,expected=expected,actual=actual,abi_checks_passed=True))
    assert bytes(u.mem_read(load*16+0x29064,182))==b[0x29064:0x2911a]
for name,rows in [('data_fields',fields),('entries',entries),('instructions',allrows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(image_sha256=sha(b),typed_bytes=182,functions=1,instructions=len(allrows),instruction_bytes=76,cases=len(cases),failures=0,max_deviation_from_scaled_tan_angles_0_to_88=errors,scope='seeded original instructions; angles 0..359, two load bases; no natural reachability proof',original_runtime_tests=0,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
