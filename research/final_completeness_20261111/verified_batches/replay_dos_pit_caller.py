"""Original caller+callee instruction replay with synthetic divisor/gate.
Usage: python replay_dos_pit_caller.py IMAGE UNICORN_DIR OUT_DIR
"""
import hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;cases=[]
for denominator,gate in [(4650,0),(4650,1),(11025,0),(0,0),(18,0)]:
    uc=Uc(UC_ARCH_X86,UC_MODE_16);uc.mem_map(0,0x100000);uc.mem_write(0,b)
    for reg,value in [(UC_X86_REG_CS,0x15bf),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_DS,0x2222)]:uc.reg_write(reg,value)
    uc.mem_write(base+0x34b9,struct.pack('<H',denominator));uc.mem_write(base+0x201e,struct.pack('<H',gate));uc.mem_write(base+0x2db4,bytes.fromhex('feca feca'))
    interrupts=[];ports=[];stop=[];helper_ax=[]
    def code(u,a,size,user):
        if a==base+0x466a:helper_ax.append(u.reg_read(UC_X86_REG_AX))
        if a==0x1917d:stop.append(True);u.emu_stop()
    def intr(u,n,user):interrupts.append(dict(number=n,ip=u.reg_read(UC_X86_REG_IP)));u.emu_stop()
    def port(u,p,size,v,user):ports.append(dict(port=p,size=size,value=v))
    uc.hook_add(UC_HOOK_CODE,code);uc.hook_add(UC_HOOK_INTR,intr);uc.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT)
    uc.emu_start(0x1916b,0x1917e,count=1000)
    if denominator in (0,18):assert len(interrupts)==1 and interrupts[0]['number']==0 and not helper_ax and not stop
    elif denominator==4650 and gate==0:assert helper_ax==[0] and len(interrupts)==1 and interrupts[0]['number']==0 and not stop
    elif gate==1:assert helper_ax==[0] and stop and not interrupts and not ports
    else:assert helper_ax==[108] and stop and not interrupts and ports==[dict(port=0x43,size=1,value=0x34),dict(port=0x40,size=1,value=108),dict(port=0x40,size=1,value=0)]
    cases.append(dict(denominator=denominator,gate=gate,helper_input_ax=helper_ax,interrupts=interrupts,returned_to_caller=bool(stop),ports=ports,ratio_words=list(struct.unpack('<HH',bytes(uc.mem_read(base+0x2db4,4))))))
out.mkdir(parents=True,exist_ok=True)
r=dict(image_sha256=h,unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],cases=cases,controlled_replay_cases=len(cases),runtime_tests=0,natural_reachability_proven=False,new_deep_verified_bytes=0,scope='synthetic state, original caller+callee bytes, no DOS/hardware execution')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(controlled_replay_cases=len(cases),assertions_passed=True,runtime_tests=0)))
